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
"""Test the AbsoluteURL view
"""
import unittest

import zope.component
from zope.component import getMultiAdapter, adapter
from zope.component.testing import PlacelessSetup
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.testing import browserView
from zope.i18n.interfaces import IUserPreferredCharsets
from zope.interface import Interface, implementer
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest
from zope.publisher.http import IHTTPRequest, HTTPCharsets
from zope.location.interfaces import ILocation
from zope.location.location import LocationProxy

from zope.traversing.testing import contained, Contained


class IRoot(Interface):
    pass


@implementer(IRoot)
class Root(Contained):
    pass


class TrivialContent(object):
    """Trivial content object, used because instances of object are rocks."""


class AdaptedContent(object):
    """A simple content object that has an ILocation adapter for it."""


class FooContent(object):
    """Class whose location will be provided by an adapter."""


@implementer(ILocation)
@adapter(FooContent)
class FooLocation(object):
    """Adapts FooAdapter to the ILocation protocol."""

    def __init__(self, context):
        self.context = context

    @property
    def __name__(self):
        return 'foo'

    @property
    def __parent__(self):
        return contained(TrivialContent(), Root(), name='bar')


class TestAbsoluteURL(PlacelessSetup, unittest.TestCase):

    assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegex',
                                getattr(unittest.TestCase, 'assertRaisesRegexp'))

    def setUp(self):
        PlacelessSetup.setUp(self)
        from zope.traversing.browser import AbsoluteURL, SiteAbsoluteURL
        browserView(None, 'absolute_url', AbsoluteURL)
        browserView(IRoot, 'absolute_url', SiteAbsoluteURL)
        browserView(None, '', AbsoluteURL, providing=IAbsoluteURL)
        browserView(IRoot, '', SiteAbsoluteURL, providing=IAbsoluteURL)
        zope.component.provideAdapter(FooLocation)
        zope.component.provideAdapter(HTTPCharsets, (IHTTPRequest,),
                                      IUserPreferredCharsets)
        # LocationProxy as set by zope.location
        # this makes a default LocationProxy for all objects that
        # don't define a more specific adapter
        zope.component.provideAdapter(LocationProxy, (Interface,),
                                      ILocation)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def test_interface(self):
        request = TestRequest()
        content = contained(TrivialContent(), Root(), name='a')
        view = getMultiAdapter((content, request), name='absolute_url')

        verifyObject(IAbsoluteURL, view)

    def testBadObject(self):
        request = TestRequest()
        view = getMultiAdapter((42, request), name='absolute_url')
        self.assertRaises(TypeError, view.__str__)
        self.assertRaises(TypeError, absoluteURL, 42, request)

    def testNoContext(self):
        request = TestRequest()
        view = getMultiAdapter((Root(), request), name='absolute_url')
        self.assertEqual(str(view), 'http://127.0.0.1')
        self.assertEqual(absoluteURL(Root(), request), 'http://127.0.0.1')

    def testBasicContext(self):
        request = TestRequest()

        content = contained(TrivialContent(), Root(), name='a')
        content = contained(TrivialContent(), content, name='b')
        content = contained(TrivialContent(), content, name='c')
        view = getMultiAdapter((content, request), name='absolute_url')
        self.assertEqual(str(view), 'http://127.0.0.1/a/b/c')
        self.assertEqual(absoluteURL(content, request),
                         'http://127.0.0.1/a/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
                         ({'name':  '', 'url': 'http://127.0.0.1'},
                          {'name': 'a', 'url': 'http://127.0.0.1/a'},
                          {'name': 'b', 'url': 'http://127.0.0.1/a/b'},
                          {'name': 'c', 'url': 'http://127.0.0.1/a/b/c'},
                         ))

    def testParentButNoLocation(self):
        request = TestRequest()

        content1 = TrivialContent()
        content1.__parent__ = Root()
        content1.__name__ = 'a'

        content2 = TrivialContent()
        content2.__parent__ = content1
        content2.__name__ = 'b'

        content3 = TrivialContent()
        content3.__parent__ = content2
        content3.__name__ = 'c'

        view = getMultiAdapter((content3, request), name='absolute_url')
        self.assertEqual(str(view), 'http://127.0.0.1/a/b/c')
        self.assertEqual(absoluteURL(content3, request),
                         'http://127.0.0.1/a/b/c')

    def testAdaptedContext(self):
        request = TestRequest()

        content = FooContent()
        view = getMultiAdapter((content, request), name='absolute_url')
        self.assertEqual(str(view), 'http://127.0.0.1/bar/foo')
        self.assertEqual(absoluteURL(content, request),
                         'http://127.0.0.1/bar/foo')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
                         ({'name':  '', 'url': 'http://127.0.0.1'},
                          {'name': 'bar', 'url': 'http://127.0.0.1/bar'},
                          {'name': 'foo', 'url': 'http://127.0.0.1/bar/foo'},
                         ))

    def testParentTrumpsAdapter(self):
        # if we have a location adapter for a content object but
        # the object also has its own __parent__, this will trump the
        # adapter
        request = TestRequest()

        content = FooContent()
        content.__parent__ = Root()
        content.__name__ = 'foo'

        view = getMultiAdapter((content, request), name='absolute_url')
        self.assertEqual(str(view), 'http://127.0.0.1/foo')
        self.assertEqual(absoluteURL(content, request),
                         'http://127.0.0.1/foo')

    def testBasicContext_unicode(self):
        #Tests so that AbsoluteURL handle unicode names as well
        request = TestRequest()
        root = Root()
        root.__name__ = u'\u0439'

        content = contained(TrivialContent(), root, name=u'\u0442')
        content = contained(TrivialContent(), content, name=u'\u0435')
        content = contained(TrivialContent(), content, name=u'\u0441')
        view = getMultiAdapter((content, request), name='absolute_url')
        self.assertEqual(str(view),
                         'http://127.0.0.1/%D0%B9/%D1%82/%D0%B5/%D1%81')
        self.assertEqual(view(),
                         'http://127.0.0.1/%D0%B9/%D1%82/%D0%B5/%D1%81')
        self.assertEqual(view.__unicode__(),
                         u'http://127.0.0.1/\u0439/\u0442/\u0435/\u0441')
        self.assertEqual(absoluteURL(content, request),
                         'http://127.0.0.1/%D0%B9/%D1%82/%D0%B5/%D1%81')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
                         ({'name':  '', 'url': 'http://127.0.0.1'},
                          {'name': u'\u0439', 'url': 'http://127.0.0.1/%D0%B9'},
                          {'name': u'\u0442',
                           'url': 'http://127.0.0.1/%D0%B9/%D1%82'},
                          {'name': u'\u0435',
                           'url': 'http://127.0.0.1/%D0%B9/%D1%82/%D0%B5'},
                          {'name': u'\u0441',
                           'url':
                           'http://127.0.0.1/%D0%B9/%D1%82/%D0%B5/%D1%81'},
                         ))

    def testRetainSkin(self):
        request = TestRequest()
        request._traversed_names = ('a', 'b')
        request._app_names = ('++skin++test', )

        content = contained(TrivialContent(), Root(), name='a')
        content = contained(TrivialContent(), content, name='b')
        content = contained(TrivialContent(), content, name='c')
        view = getMultiAdapter((content, request), name='absolute_url')
        base = 'http://127.0.0.1/++skin++test'
        self.assertEqual(str(view), base + '/a/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
                         ({'name':  '', 'url': base + ''},
                          {'name': 'a', 'url': base + '/a'},
                          {'name': 'b', 'url': base + '/a/b'},
                          {'name': 'c', 'url': base + '/a/b/c'},
                         ))

    def testVirtualHosting(self):
        request = TestRequest()

        vh_root = TrivialContent()
        content = contained(vh_root, Root(), name='a')
        request._vh_root = content
        content = contained(TrivialContent(), content, name='b')
        content = contained(TrivialContent(), content, name='c')
        view = getMultiAdapter((content, request), name='absolute_url')
        self.assertEqual(str(view), 'http://127.0.0.1/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
                         ({'name':  '', 'url': 'http://127.0.0.1'},
                          {'name': 'b', 'url': 'http://127.0.0.1/b'},
                          {'name': 'c', 'url': 'http://127.0.0.1/b/c'},
                         ))

    def testVirtualHostingWithVHElements(self):
        request = TestRequest()

        vh_root = TrivialContent()
        content = contained(vh_root, Root(), name='a')
        request._vh_root = content
        content = contained(TrivialContent(), content, name='b')
        content = contained(TrivialContent(), content, name='c')
        view = getMultiAdapter((content, request), name='absolute_url')
        self.assertEqual(str(view), 'http://127.0.0.1/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
                         ({'name':  '', 'url': 'http://127.0.0.1'},
                          {'name': 'b', 'url': 'http://127.0.0.1/b'},
                          {'name': 'c', 'url': 'http://127.0.0.1/b/c'},
                         ))

    def testVirtualHostingInFront(self):
        request = TestRequest()

        root = Root()
        request._vh_root = contained(root, root, name='')
        content = contained(root, None)
        content = contained(TrivialContent(), content, name='a')
        content = contained(TrivialContent(), content, name='b')
        content = contained(TrivialContent(), content, name='c')
        view = getMultiAdapter((content, request), name='absolute_url')
        self.assertEqual(str(view), 'http://127.0.0.1/a/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
                         ({'name':  '', 'url': 'http://127.0.0.1'},
                          {'name': 'a', 'url': 'http://127.0.0.1/a'},
                          {'name': 'b', 'url': 'http://127.0.0.1/a/b'},
                          {'name': 'c', 'url': 'http://127.0.0.1/a/b/c'},
                         ))

    def testNoContextInformation(self):
        request = TestRequest()
        view = getMultiAdapter((None, request), name='absolute_url')
        self.assertEqual(str(view), 'http://127.0.0.1')
        self.assertEqual(absoluteURL(None, request), 'http://127.0.0.1')

    def testVirtualHostingWithoutContextInformation(self):
        request = TestRequest()
        request._vh_root = contained(TrivialContent(), Root(), name='a')
        view = getMultiAdapter((None, request), name='absolute_url')
        self.assertEqual(str(view), 'http://127.0.0.1')
        self.assertEqual(absoluteURL(None, request), 'http://127.0.0.1')


    def test_breadcrumbs_no_parent(self):

        view = AbsoluteURL(self, None)
        with self.assertRaisesRegex(TypeError,
                                    "There isn't enough context"):
            view.breadcrumbs()

    def test_nameless_context(self):

        @implementer(ILocation)
        class Context(object):
            __parent__ = self
            __name__ = None

        class DummyAbsoluteURL(object):
            # Our implementation of IAbsoluteURL
            # for our parent

            def __init__(self, *args):
                pass

            called = False

            def __str__(self):
                DummyAbsoluteURL.called = True
                return ''

            def breadcrumbs(self):
                DummyAbsoluteURL.called = True
                return ()

        browserView(type(self), '', DummyAbsoluteURL, IAbsoluteURL)

        request = TestRequest()
        self.assertIsInstance(zope.component.getMultiAdapter((self, request), IAbsoluteURL),
                              DummyAbsoluteURL)
        context = Context()

        # First the view
        view = AbsoluteURL(context, request)
        with self.assertRaisesRegex(TypeError,
                                    "There isn't enough context"):
            str(view)

        self.assertTrue(DummyAbsoluteURL.called)
        DummyAbsoluteURL.called = False

        # Now the breadcrumbs
        view = AbsoluteURL(context, request)
        with self.assertRaisesRegex(TypeError,
                                    "There isn't enough context"):
            view.breadcrumbs()

        self.assertTrue(DummyAbsoluteURL.called)
