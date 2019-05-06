##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""'browser' namespace directive tests
"""

import os
import unittest
from io import StringIO

import zope.browserresource
import zope.publisher.defaultview
import zope.security.management

from zope import component
from zope.component import provideAdapter
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.interface import Interface, implementer
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security.proxy import ProxyFactory
from zope.testing import cleanup
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable

from zope.browserresource.directory import DirectoryResource
from zope.browserresource.file import FileResource
from zope.browserresource.i18nfile import I18nFileResource
from zope.browserresource.metaconfigure import I18nResource
from zope.browserresource.metaconfigure import resource


tests_path = os.path.join(
    os.path.dirname(zope.browserresource.__file__),
    'tests')

template = u"""<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""

class IV(Interface):
    def index():
        "A method"


@implementer(IV)
class R1(object):
    pass


class ITestLayer(IBrowserRequest):
    """Test Layer."""

class ITestSkin(ITestLayer):
    """Test Skin."""


class MyResource(object):

    def __init__(self, request):
        self.request = request


class TestZCML(cleanup.CleanUp, unittest.TestCase):

    def setUp(self):
        super(TestZCML, self).setUp()
        XMLConfig('meta.zcml', zope.browserresource)()
        provideAdapter(DefaultTraversable, (None,), ITraversable)
        self.request = TestRequest()

    def testI18nResource(self):
        self.assertEqual(component.queryAdapter(self.request, name='test'), None)

        path1 = os.path.join(tests_path, 'testfiles', 'test.pt')
        path2 = os.path.join(tests_path, 'testfiles', 'test2.pt')

        xmlconfig(StringIO(
            template
            %
            u'''
            <browser:i18n-resource name="test" defaultLanguage="fr">
              <browser:translation language="en" file="%s" />
              <browser:translation language="fr" file="%s" />
            </browser:i18n-resource>
            ''' % (path1, path2)
        ))

        v = component.getAdapter(self.request, name='test')
        self.assertEqual(
            component.queryAdapter(self.request, name='test').__class__,
            I18nFileResource)
        with open(path1, 'rb') as f:
            self.assertEqual(v._testData('en'), f.read())
        with open(path2, 'rb') as f:
            self.assertEqual(v._testData('fr'), f.read())

        # translation must be provided for the default language
        config = StringIO(
            template %
            u'''
            <browser:i18n-resource name="test" defaultLanguage="fr">
              <browser:translation language="en" file="%s" />
              <browser:translation language="lt" file="%s" />
            </browser:i18n-resource>
            ''' % (path1, path2)
        )
        self.assertRaises(ConfigurationError, xmlconfig, config)

    def testFactory(self):
        self.assertEqual(
            component.queryAdapter(self.request, name='index.html'), None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:resource
                name="index.html"
                factory="
                  zope.browserresource.tests.test_directives.MyResource"
                />
            '''
        ))

        r = component.getAdapter(self.request, name='index.html')
        self.assertEqual(r.__class__, MyResource)
        r = ProxyFactory(r)
        self.assertEqual(r.__name__, "index.html")

    def testFile(self):
        from zope.security.interfaces import ForbiddenAttribute
        path = os.path.join(tests_path, 'testfiles', 'test.pt')

        self.assertEqual(component.queryAdapter(self.request, name='test'), None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:resource
                name="index.html"
                file="%s"
                />
            ''' % path
        ))

        unwrapped_r = component.getAdapter(self.request, name='index.html')
        self.assertTrue(isinstance(unwrapped_r, FileResource))
        r = ProxyFactory(unwrapped_r)
        self.assertEqual(r.__name__, "index.html")

        # Make sure we can access available attrs and not others
        for n in ('GET', 'HEAD', 'publishTraverse', 'request', '__call__'):
            getattr(r, n)

        self.assertRaises(ForbiddenAttribute, getattr, r, '_testData')

        with open(path, 'rb') as f:
            self.assertEqual(unwrapped_r._testData(), f.read())


    def testPluggableFactory(self):

        class ImageResource(object):
            def __init__(self, image, request):
                pass

        class ImageResourceFactory(object):
            def __init__(self, path, checker, name):
                pass
            def __call__(self, request):
                return ImageResource(None, request)

        from zope.browserresource.interfaces import IResourceFactoryFactory
        component.provideUtility(ImageResourceFactory, IResourceFactoryFactory,
                                 name='gif')

        xmlconfig(StringIO(
            template %
            u'''
            <browser:resource
                name="test.gif"
                file="%s"
                />
            ''' % os.path.join(tests_path, 'testfiles', 'test.gif')
        ))

        r = component.getAdapter(self.request, name='test.gif')
        self.assertTrue(isinstance(r, ImageResource))

    def testDirectory(self):
        path = os.path.join(tests_path, 'testfiles', 'subdir')

        self.assertEqual(component.queryAdapter(self.request, name='dir'), None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:resourceDirectory
                name="dir"
                directory="%s"
                />
            ''' % path
        ))

        r = component.getAdapter(self.request, name='dir')
        self.assertTrue(isinstance(r, DirectoryResource))
        r = ProxyFactory(r)
        self.assertEqual(r.__name__, "dir")

        # Make sure we can access available attrs and not others
        for n in ('publishTraverse', 'browserDefault', 'request', '__call__',
                  'get', '__getitem__'):
            getattr(r, n)

        self.assertRaises(Exception, getattr, r, 'directory_factory')

        inexistent_dir = StringIO(
            template %
            u'''
            <browser:resourceDirectory
                name="dir"
                directory="does-not-exist"
                />
            ''')

        self.assertRaises(ConfigurationError, xmlconfig, inexistent_dir)

    def test_SkinResource(self):
        self.assertEqual(component.queryAdapter(self.request, name='test'), None)

        path = os.path.join(tests_path, 'testfiles', 'test.pt')
        xmlconfig(StringIO(
            template %
            u'''
            <browser:resource
                name="test"
                file="%s"
                layer="
                  zope.browserresource.tests.test_directives.ITestLayer"
                />
            ''' % path
        ))

        self.assertEqual(component.queryAdapter(self.request, name='test'), None)

        r = component.getAdapter(TestRequest(skin=ITestSkin), name='test')
        with open(path, 'rb') as f:
            self.assertEqual(r._testData(), f.read())


class Context(object):

    class info(object):
        file = __file__
        line = 1

    def __init__(self):
        self.actions = []

    def path(self, s):
        return s

    def action(self, **kwargs):
        self.actions.append(kwargs)

class _AbstractHandlerTest(unittest.TestCase):

    if not hasattr(unittest.TestCase, 'assertRaisesRegex'):
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp

    def setUp(self):
        self.context = Context()

    def _call(self, **kwargs):
        context = self.context
        self._callFUT(context, 'Name', **kwargs)
        return context

    def _check_raises(self, regex, **kwargs):
        with self.assertRaisesRegex(ConfigurationError, regex):
            self._call(**kwargs)

    def _check_warning_msg(self, msg, **kwargs):
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self._call(**kwargs)

        self.assertEqual(1, len(w))
        self.assertEqual(
            msg,
            str(w[0].message))


class TestResource(_AbstractHandlerTest):

    def _callFUT(self, *args, **kwargs):
        resource(*args, **kwargs)

    def test_factory_and_file_and(self):
        excludes = {
            'factory': ['file', 'image', 'template'],
            'file': ['factory', 'image', 'template'],
            'image': ['factory', 'file', 'template'],
            'template': ['factory', 'file', 'image']
        }
        for main, excluded_args in excludes.items():
            for excluded_arg in excluded_args:
                kwargs = {main: 'main', excluded_arg: 'excluded'}
                __traceback_info__ = main, excluded_arg
                self._check_raises("Must use exactly one of factory or file",
                                   **kwargs)

    def _check_warning(self, **kwargs):
        msg = ('The "template" and "image" attributes of resource directive '
               'are deprecated in favor of pluggable file resource factories '
               'based on file extensions. Use the "file" attribute instead.')
        self._check_warning_msg(msg, **kwargs)

    def test_image_warning(self):
        self._check_warning(image='image')

    def test_template_warning(self):
        self._check_warning(template='template')

class TestI18nResource(_AbstractHandlerTest):

    def _callFUT(self, *args, **kwargs):
        I18nResource(*args).translation(self.context, **kwargs)

    def test_file_and_image(self):
        self._check_raises(
            ".*more than one of file",
            file='file', image='image', language='en')

    def test_no_file_or_image(self):
        self._check_raises(
            'At least one of the file',
            file=None, image=None, language='en')

    def test_image(self):
        self._check_warning_msg(
            'The "image" attribute of i18n-resource directive is '
            'deprecated in favor of simple files. Use the "file" '
            'attribute instead.',
            image=__file__, language='en'
        )

    def test_call_no_name(self):
        I18nResource(self.context)()
        self.assertEqual(self.context.actions, [])

    def test_call_public_permission(self):
        resource = I18nResource(self.context, 'Name', permission='zope.Public')
        resource.translation(self.context, 'en', file=__file__)
        resource()
        self.assertEqual(1, len(self.context.actions))

    def test_call_require(self):
        resource = I18nResource(self.context, 'Name', permission='zope.Public')
        resource.translation(self.context, 'en', file=__file__)
        resource(require={'foo': 'bar'})
        self.assertEqual(1, len(self.context.actions))

        factory = self.context.actions[0]['args'][1]
        factory(TestRequest())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
