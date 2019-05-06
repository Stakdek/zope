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
"""Test Browser Widget
"""
import unittest
from zope.component.testing import PlacelessSetup
from zope.interface import Interface, implementer
from zope.publisher.browser import TestRequest
from zope.schema import Text, Int
from doctest import DocTestSuite

from zope.formlib.widget import SimpleInputWidget
from zope.formlib.interfaces import ConversionError
from zope.formlib.interfaces import WidgetInputError, MissingInputError

from zope.formlib.tests import support

class BrowserWidgetTest(PlacelessSetup,
                        support.VerifyResults,
                        unittest.TestCase):

    _FieldFactory = Text
    _WidgetFactory = None

    def setUpContent(self, desc=u'', title=u'Foo Title'):
        field = self._FieldFactory(
            __name__='foo', title=title, description=desc)
        class ITestContent(Interface):
            foo = field
        @implementer(ITestContent)
        class TestObject:
            pass
        self.content = TestObject()
        field = ITestContent['foo']
        field = field.bind(self.content)
        request = TestRequest(HTTP_ACCEPT_LANGUAGE='ru')
        request.form['field.foo'] = u'Foo Value'
        self._widget = self._WidgetFactory(field, request)

    def setUp(self):
        super(BrowserWidgetTest, self).setUp()
        self.setUpContent()


class SimpleInputWidgetTest(BrowserWidgetTest):

    _WidgetFactory = SimpleInputWidget

    def test_required(self):
        # widget required defaults to its context required
        self.assertTrue(self._widget.required)
        self.assertTrue(self._widget.context.required)
        # changing widget context required has no effect on widget required
        self._widget.context.required = False
        self.assertTrue(self._widget.required)
        self.assertTrue(not self._widget.context.required)

    def test_hasInput(self):
        self.assertTrue(self._widget.hasInput())
        del self._widget.request.form['field.foo']
        self.assertFalse(self._widget.hasInput())

    def testProperties(self):
        self.assertEqual(self._widget.tag, 'input')
        self.assertEqual(self._widget.type, 'text')
        self.assertEqual(self._widget.cssClass, '')
        self.assertEqual(self._widget.extra, '')

    def testRender(self, value=None, check_list=None):
        if value is None:
            value = 'Foo Value'
        if check_list is None:
            check_list = ('type="text"', 'id="field.foo"', 'name="field.foo"',
                          'value="Foo Value"')
        self._widget.setRenderedValue(value)
        self.verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"',) + check_list[1:]
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('type="hidden"', 'style="color: red"') + check_list[1:]
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)

    def testLabel(self):
        self.setUpContent(title=u'Foo:')
        self.assertEqual(self._widget.label, u'Foo:')

    def testHint(self):
        self.setUpContent(desc=u'Foo Description')
        self.assertEqual(self._widget.hint, u'Foo Description')


class TestWidget(SimpleInputWidget):

    def _toFieldValue(self, v):
        if v == u'barf!':
            raise ConversionError('ralph')
        return v or None

class Test(BrowserWidgetTest):

    _WidgetFactory = TestWidget

    def test_getFormValue(self):

        class W(SimpleInputWidget):
            def _toFieldValue(self, v):
                return u'X' + (v or '')

            def _toFormValue(self, v):
                return v and v[1:] or ''

        field = Text(__name__ = 'foo', title = u"Foo Title")
        request = TestRequest()

        w = W(field, request)
        self.assertEqual(w._getFormValue(), '')
        request.form['field.foo'] = 'val'
        self.assertEqual(w._getFormValue(), 'val')

        w.setRenderedValue('Xfoo')
        self.assertEqual(w._getFormValue(), 'foo')

    def test_hasValidInput(self):
        self.assertEqual(self._widget.getInputValue(), u'Foo Value')

        self._widget.request.form['field.foo'] = (1, 2)
        self.assertFalse(self._widget.hasValidInput())

        self._widget.request.form['field.foo'] = u'barf!'
        self.assertFalse(self._widget.hasValidInput())

        del self._widget.request.form['field.foo']
        self._widget.context.required = True
        self.assertFalse(self._widget.hasValidInput())

        self._widget.context.required = False
        self._widget.request.form['field.foo'] = u''
        self.assertTrue(self._widget.hasValidInput())

    def test_getInputValue(self):
        self.assertEqual(self._widget.getInputValue(), u'Foo Value')

        self._widget.request.form['field.foo'] = (1, 2)
        self.assertRaises(WidgetInputError, self._widget.getInputValue)

        self._widget.request.form['field.foo'] = u'barf!'
        self.assertRaises(ConversionError, self._widget.getInputValue)

        del self._widget.request.form['field.foo']
        self._widget.context.required = True
        self.assertRaises(MissingInputError, self._widget.getInputValue)

        self._widget.context.required = False
        self._widget.request.form['field.foo'] = u''
        self.assertEqual(self._widget.getInputValue(), None)

    def test_applyChanges(self):
        self.assertEqual(self._widget.applyChanges(self.content), True)

    def test_hasInput(self):
        self.assertTrue(self._widget.hasInput())
        del self._widget.request.form['field.foo']
        self.assertFalse(self._widget.hasInput())
        self._widget.request.form['field.foo'] = u'foo'
        self.assertTrue(self._widget.hasInput())
        # widget has input, even if input is an empty string
        self._widget.request.form['field.foo'] = u''
        self.assertTrue(self._widget.hasInput())

    def test_getFormValue_w_default(self):
        field = Text(__name__ = 'foo', title = u"Foo Title", default=u"def")
        request = TestRequest()
        widget = self._WidgetFactory(field, request)
        self.assertEqual(widget._getFormValue(), u'def')

    def test_getFormValue_preserves_errors(self):
        field = Int(__name__ = 'foo', title = u"Foo Title", default=42)
        request = TestRequest()
        widget = self._WidgetFactory(field, request)

        # Sometimes you want to set a custom error on a widget.
        widget._error = 'my error'

        # _getFormValue shouldn't replace it.
        request.form['field.foo'] = u'barf!'
        widget._getFormValue()
        self.assertEqual(widget._error, 'my error')

        # _getFormValue shouldn't clear it either
        request.form['field.foo'] = 33
        widget._getFormValue()
        self.assertEqual(widget._error, 'my error')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    suite.addTest(DocTestSuite("zope.formlib.widget", checker=support.checker))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
