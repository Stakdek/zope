##############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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

import unittest

from zope.browserpage.metaconfigure import page
from zope.browserpage.metaconfigure import view
from zope.browserpage.metaconfigure import simple
from zope.browserpage.metaconfigure import _handle_menu
from zope.configuration.exceptions import ConfigurationError

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
        self._callFUT(context, 'Name', None, **kwargs)
        return context

    def _check_raises(self, regex, **kwargs):
        with self.assertRaisesRegex(ConfigurationError, regex):
            self._call(**kwargs)

class TestPage(_AbstractHandlerTest):

    def _callFUT(self, *args, **kwargs):
        page(*args, **kwargs)

    def test_no_class_no_template(self):
        self._check_raises('Must specify a class or template')

    def test_template_attribute(self):
        self._check_raises(
            'Attribute and template cannot be used together',
            template=self, attribute="attr")

    def test_template_not_exists(self):
        self._check_raises(
            "No such file",
            template=__name__)

    def test_class_missing_attribute(self):
        self._check_raises(
            "The provided class doesn't have the specified attribute",
            class_=type(self), attribute="does not exist")

    def test_class_with_browser_default(self):
        class BrowserDefault(object):
            def browserDefault(self):
                raise AssertionError("Not called")
        context = self._call(
            class_=BrowserDefault)

        action = context.actions[1]
        register = action['args']
        new_class = register[1]
        self.assertEqual(new_class.browserDefault,
                         BrowserDefault.browserDefault)

    def test_class_implements(self):
        from zope.publisher.interfaces.browser import IBrowserPublisher
        from zope import interface

        class Class(object):
            # How does this arise in the wild?
            # @implementer(IThing) doesn't do it.
            __implements__ = None

        self.assertTrue(hasattr(Class, '__implements__'))
        context = self._call(class_=Class)

        action = context.actions[1]
        register = action['args']
        new_class = register[1]
        self.assertIn(IBrowserPublisher, interface.implementedBy(new_class))

class TestViewPage(_AbstractHandlerTest):

    view = None

    def _callFUT(self, *args, **kwargs):
        self.view = view(self.context, None)
        self.view.page(self.context, 'Name', **kwargs)

    def test_no_attribute(self):
        self._check_raises(
            "Must specify either a template or an attribute name")

class TestView(_AbstractHandlerTest):

    def test_class_without_attribute(self):
        v = view(self.context, None, class_=type(self))
        v.pages.append([None, 'does not exist', None])
        self._call = v

        self._check_raises('Undefined attribute')

    def test_class_without_publish_traverse_name(self):
        class C(object):
            attr = 'the attr'

        v = view(self.context, None, class_=C)
        v.pages.append(['page_name', 'attr', None])

        v()

        action = self.context.actions[2]
        register = action['args']
        new_class = register[1]

        instance = new_class(None, None)
        self.assertEqual(C.attr,
                         instance.publishTraverse(None, 'page_name'))

        with self.assertRaises(LookupError):
            instance.publishTraverse(None, 'something else')

    def test_class_with_publish_traverse_name(self):
        class C(object):
            attr = 'the attr'

            def publishTraverse(self, *args):
                raise AssertionError("Never called")

        v = view(self.context, None, class_=C)
        v.pages.append(['page_name', 'attr', None])

        v()

        action = self.context.actions[2]
        register = action['args']
        new_class = register[1]

        instance = new_class(None, None)
        self.assertEqual(C.attr,
                         instance.publishTraverse(None, 'page_name'))

    def test_class_with_publish_traverse_other_name(self):
        class C(object):
            attr = 'the attr'

            def publishTraverse(self, *args):
                return 'default value'

        v = view(self.context, None, class_=C)
        v.pages.append(['page_name', 'attr', None])

        v()

        action = self.context.actions[2]
        register = action['args']
        new_class = register[1]

        instance = new_class(None, None)
        self.assertEqual('default value',
                         instance.publishTraverse(None, 'something else'))

    def test_template_with_attr_not_equal_name(self):
        import os
        v = view(self.context, None)
        v.page(self.context, 'page_name', attribute='foo',
               template=os.path.join(os.path.dirname(__file__), 'test.pt'))
        v()
        action = self.context.actions[2]
        register = action['args']
        new_class = register[1]

        self.assertTrue(hasattr(new_class, 'foo'))
        self.assertTrue(hasattr(new_class, 'page_name'))

class TestHandleMenu(_AbstractHandlerTest):

    def _call(self, **kwargs):
        args = {
            '_context': self.context,
            'menu': None,
            'title': None,
            'for_': None,
            'name': '',
            'permission': None
        }
        args.update(kwargs)
        return _handle_menu(**args)

    def test_one_or_the_other(self):
        self._check_raises(
            ".*they must both be specified",
            menu='menu', title='')

        self._check_raises(
            ".*they must both be specified",
            menu='', title='menu')

    def test_bad_for(self):
        self._check_raises(
            "Menus can be specified only for single-view",
            menu='menu', title='title',
            for_=(1, 2)
        )

    def test_no_directive(self):
        from zope.browserpage import metaconfigure
        import warnings
        menuItemDirective = metaconfigure.menuItemDirective
        metaconfigure.menuItemDirective = metaconfigure._fallbackMenuItemDirective
        try:
            with warnings.catch_warnings(record=True) as w:
                result = self._call(menu='menu', title='title', for_=(1,))
            self.assertEqual(result, [])
            self.assertEqual(
                'Page directive used with "menu" argument, while "zope.browsermenu" '
                'package is not installed. Doing nothing.',
                str(w[0].message))
        finally:
            metaconfigure.menuItemDirective = menuItemDirective

class TestSimple(unittest.TestCase):

    def test_publish_not_found(self):
        sview = simple(None, None)
        with self.assertRaises(LookupError):
            sview.publishTraverse(None, None)

    def test_recursive_call(self):
        sview = simple(None, None)
        sview.__page_attribute__ = '__call__'

        with self.assertRaises(AttributeError):
            sview()
