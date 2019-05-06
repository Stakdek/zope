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
"""Float Widget tests
"""
import unittest
import doctest
from zope.formlib.tests.test_browserwidget import SimpleInputWidgetTest
from zope.formlib.interfaces import IInputWidget
from zope.formlib.widgets import FloatWidget
from zope.formlib.interfaces import ConversionError, WidgetInputError
from zope.interface.verify import verifyClass

from zope.schema import Float


class FloatWidgetTest(SimpleInputWidgetTest):
    """Documents and tests the float widget.
        
        >>> verifyClass(IInputWidget, FloatWidget)
        True
    """

    _FieldFactory = Float
    _WidgetFactory = FloatWidget

    def test_hasInput(self):
        del self._widget.request.form['field.foo']
        self.assertFalse(self._widget.hasInput())
        # widget has input, even if input is an empty string
        self._widget.request.form['field.foo'] = u''
        self.assertTrue(self._widget.hasInput())
        self._widget.request.form['field.foo'] = u'123'
        self.assertTrue(self._widget.hasInput())

    def test_getInputValue(self):
        self._widget.request.form['field.foo'] = u''
        self.assertRaises(WidgetInputError, self._widget.getInputValue)
        self._widget.request.form['field.foo'] = u'123.45'
        self.assertEqual(self._widget.getInputValue(), 123.45)
        self._widget.request.form['field.foo'] = u'abc'
        self.assertRaises(ConversionError, self._widget.getInputValue)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FloatWidgetTest),
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
