##############################################################################
#
# Copyright (c) 2001-2009 Zope Foundation and Contributors.
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
"""Simple View Class Tests
"""
import unittest

class Test_SimpleTestView(unittest.TestCase):

    def _getTargetClass(self):
        from zope.browserpage.tests.simpletestview import SimpleTestView
        return SimpleTestView

    def _makeOne(self, context, request):
        return self._getTargetClass()(context, request)

    def test_simple(self):
        from zope.publisher.browser import TestRequest
        context = DummyContext()
        request = TestRequest()
        view = self._makeOne(context, request)
        self.assertIsNotNone(view['test'])
        out = view()
        self.assertEqual(out.replace('\r\n', '\n'),
                         '<html>\n'
                         '  <body>\n'
                         '    <p>hello world</p>\n'
                         '  </body>\n</html>\n')

class Test_SimpleViewClass(unittest.TestCase):

    def _getTargetClass(self):
        from zope.browserpage.simpleviewclass import SimpleViewClass
        return SimpleViewClass

    def _makeKlass(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test___name__(self):
        klass = self._makeKlass('testsimpleviewclass.pt', name='test.html')
        view = klass(None, None)
        self.assertEqual(view.__name__, 'test.html')

    def test__used_for__(self):
        klass = self._makeKlass('testsimpleviewclass.pt',
                                name='test.html',
                                used_for=self)
        self.assertIs(klass.__used_for__, self)

    def test___getitem___(self):
        klass = self._makeKlass('testsimpleviewclass.pt', name='test.html')
        view = klass(None, None)
        self.assertTrue(view['test'] is not None)
        self.assertRaises(KeyError, view.__getitem__, 'foo')

    def test_w_base_classes(self):
        from zope.publisher.browser import TestRequest
        class BaseClass(object):
            pass

        klass = self._makeKlass('testsimpleviewclass.pt', bases=(BaseClass, ))

        self.assertTrue(issubclass(klass, BaseClass))

        ob = DummyContext()
        request = TestRequest()
        view = klass(ob, request)
        self.assertIsNotNone(view['test'])
        out = view()
        self.assertEqual(out.replace('\r\n', '\n'),
                         '<html>\n'
                         '  <body>\n'
                         '    <p>hello world</p>\n'
                         '  </body>\n</html>\n')

class Test_simple(unittest.TestCase):

    def _getTargetClass(self):
        from zope.browserpage.simpleviewclass import simple
        return simple

    def _makeOne(self, context=None, request=None):
        if context is None:
            context = DummyContext()
        if request is None:
            request = DummyRequest()
        return self._getTargetClass()(context, request)

    def test_class_conforms_to_IBrowserPublisher(self):
        from zope.interface.verify import verifyClass
        from zope.publisher.interfaces.browser import IBrowserPublisher
        verifyClass(IBrowserPublisher, self._getTargetClass())

    def test_browserDefault(self):
        request = DummyRequest()
        view = self._makeOne(request=request)
        self.assertEqual(view.browserDefault(request), (view, ()))

    def test_publishTraverse_not_index_raises_NotFound(self):
        from zope.publisher.interfaces import NotFound
        request = DummyRequest()
        view = self._makeOne(request=request)
        self.assertRaises(NotFound, view.publishTraverse, request, 'nonesuch')

    def test_publishTraverse_w_index_returns_index(self):
        request = DummyRequest()
        view = self._makeOne(request=request)
        index = view.index = DummyTemplate()
        self.assertTrue(view.publishTraverse(request, 'index.html') is index)

    def test___getitem___uses_index_macros(self):
        view = self._makeOne()
        view.index = index = DummyTemplate()
        index.macros = {}
        index.macros['aaa'] = aaa = object()
        self.assertTrue(view['aaa'] is aaa)

    def test___call___no_args_no_kw(self):
        view = self._makeOne()
        view.index = index = DummyTemplate()
        result = view()
        self.assertTrue(result is index)
        self.assertEqual(index._called_with, ((), {}))

    def test___call___w_args_no_kw(self):
        view = self._makeOne()
        view.index = index = DummyTemplate()
        result = view('abc')
        self.assertTrue(result is index)
        self.assertEqual(index._called_with, (('abc',), {}))

    def test___call___no_args_w_kw(self):
        view = self._makeOne()
        view.index = index = DummyTemplate()
        result = view(foo='bar')
        self.assertTrue(result is index)
        self.assertEqual(index._called_with, ((), {'foo': 'bar'}))

    def test___call___w_args_w_kw(self):
        view = self._makeOne()
        view.index = index = DummyTemplate()
        result = view('abc', foo='bar')
        self.assertTrue(result is index)
        self.assertEqual(index._called_with, (('abc',), {'foo': 'bar'}))


class DummyContext:
    pass

class DummyResponse:
    pass

class DummyRequest:
    debug = False
    response = DummyResponse()

class DummyTemplate:
    def __call__(self, *args, **kw):
        self._called_with = (args, kw)
        return self

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_SimpleTestView),
        unittest.makeSuite(Test_SimpleViewClass),
        unittest.makeSuite(Test_simple),
    ))
