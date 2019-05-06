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
"""Checkbox Widget tests
"""
import unittest

from zope.interface import Interface, implementer
from zope.schema import Bool
from zope.formlib import form
from zope.publisher.browser import TestRequest
from zope.formlib.tests.support import patternExists
from zope.formlib.widgets import CheckBoxWidget
from zope.formlib.tests.functionalsupport import FunctionalWidgetTestCase
import zope.schema.interfaces

class IBoolTest(Interface):

    b1 = Bool(
        required=True)

    b2 = Bool(
        required=False)

@implementer(IBoolTest)
class BoolTest(object):

    def __init__(self):
        self.b1 = True
        self.b2 = False

class Form(form.EditForm):
    form_fields = form.fields(IBoolTest)
           
class Test(FunctionalWidgetTestCase):
    widgets = [(zope.schema.interfaces.IBool, CheckBoxWidget)]
    
    def test_display_editform(self):
        foo = BoolTest()
        request = TestRequest()
        html = Form(foo, request)()
        
        # b1 and b2 should be displayed in checkbox input fields
        self.assertTrue(patternExists(
            '<input .* checked="checked".* name="form.b1".* ' \
            'type="checkbox".* />',
            html))
        self.assertTrue(patternExists(
            '<input .* name="form.b2".* type="checkbox".* />',
            html))
        # confirm that b2 is *not* checked
        self.assertTrue(not patternExists(
            '<input .* checked="checked".* name="form.b2".* ' \
            'type="checkbox".* />',
            html))

    def test_submit_editform(self):
        foo = BoolTest()

        request = TestRequest()
        request.form['form.b1'] = ''
        request.form['form.b2'] = 'on'
        request.form['form.actions.apply'] = u''
                
        Form(foo, request)()

        # check new values in object
        self.assertEqual(foo.b1, False)
        self.assertEqual(foo.b2, True)

    def test_unexpected_value(self):
        foo = BoolTest()
        foo.b1 = True
        foo.b2 = True
        
        request = TestRequest()
        request.form['form.b1'] = 'true'
        request.form['form.b2'] = 'foo'
        request.form['form.actions.apply'] = u''

        Form(foo, request)()

        # values other than 'on' should be treated as False
        self.assertEqual(foo.b1, False)
        self.assertEqual(foo.b2, False)

    def test_missing_value(self):
        # Note: checkbox widget doesn't support a missing value. This
        # test confirms that one cannot set a Bool field to None.
        foo = BoolTest()
        self.assertEqual(foo.b1, True)
        
        request = TestRequest()
        request.form['form.b1'] = CheckBoxWidget._missing
        
        Form(foo, request)()

        # confirm b1 is not missing
        self.assertTrue(foo.b1 != Bool.missing_value)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite


