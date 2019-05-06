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
"""File Widget tests
"""
import doctest
import unittest
from zope.interface.verify import verifyClass

from zope.formlib._compat import StringIO
from zope.formlib.interfaces import IInputWidget
from zope.formlib.widgets import FileWidget
from zope.formlib.tests.test_browserwidget import (
    SimpleInputWidgetTest)

class FileWidgetTest(SimpleInputWidgetTest):
    """Documents and tests the file widget.

        >>> verifyClass(IInputWidget, FileWidget)
        True
    """

    _WidgetFactory = FileWidget

    def setUp(self):
        super(FileWidgetTest, self).setUp()
        file = StringIO('Foo Value')
        file.filename = 'test.txt'
        self._widget.request.form['field.foo'] = file

    def testProperties(self):
        self.assertEqual(self._widget.tag, 'input')
        self.assertEqual(self._widget.type, 'file')
        self.assertEqual(self._widget.cssClass, '')
        self.assertEqual(self._widget.extra, '')
        self.assertEqual(self._widget.default, '')
        self.assertEqual(self._widget.displayWidth, 20)
        self.assertEqual(self._widget.displayMaxWidth, '')

    def test_hasInput(self): # override the usual one
        del self._widget.request.form['field.foo']
        self._widget.request.form['field.foo.used'] = ''
        self.assertTrue(self._widget.hasInput())
        del self._widget.request.form['field.foo.used']
        self.assertFalse(self._widget.hasInput())

    def testRender(self):
        value = 'Foo Value'
        self._widget.setRenderedValue(value)
        check_list = ('type="file"', 'id="field.foo"', 'name="field.foo"',
                      'size="20"')

        self.verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"',) + check_list[1:-1]
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FileWidgetTest),
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
