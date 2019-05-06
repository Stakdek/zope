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
"""Float Widget Functional Tests
"""
import unittest

from zope.interface import Interface, implementer
from zope.schema import Float, Choice
from zope.formlib import form
from zope.publisher.browser import TestRequest
from zope.formlib.tests.support import patternExists
from zope.formlib.widgets import (
    FloatWidget,
    DropdownWidget, ChoiceInputWidget)
from zope.formlib.tests.functionalsupport import FunctionalWidgetTestCase
import zope.schema.interfaces

class IFloatTest(Interface):

    f1 = Float(
        required=False,
        min=1.1,
        max=10.1)

    f2 = Float(
        required=False)

    f3 = Choice(
        required=True,
        values=(0.0, 1.1, 2.1, 3.1, 5.1, 7.1, 11.1),
        missing_value=0)

@implementer(IFloatTest)
class FloatTest(object):

    def __init__(self):
        self.f1 = None
        self.f2 = 1.1
        self.f3 = 2.1

class Form(form.EditForm):
    form_fields = form.fields(IFloatTest)
    
class Test(FunctionalWidgetTestCase):
    widgets = [
        (zope.schema.interfaces.IFloat, FloatWidget),
        (zope.schema.interfaces.IChoice, ChoiceInputWidget),
        ((zope.schema.interfaces.IChoice, zope.schema.interfaces.IVocabularyTokenized),
         DropdownWidget)]
    
    def test_display_editform(self):
        foo = FloatTest()
        request = TestRequest()

        # display edit view
        html = Form(foo, request)()

        # f1 and f2 should be displayed in text fields
        self.assertTrue(patternExists(
            '<input .* name="form.f1".* value="".*>', html))
        self.assertTrue(patternExists(
            '<input .* name="form.f2".* value="1.1".*>', html))

        # f3 should be in a dropdown
        self.assertTrue(patternExists(
            '<select .*name="form.f3".*>', html))
        self.assertTrue(patternExists(
            '<option selected="selected" value="2.1">2.1</option>',
            html))

    def test_submit_editform(self):
        foo = FloatTest()
        request = TestRequest()

        # submit edit view
        request.form['form.f1'] = '1.123'
        request.form['form.f2'] = '2.23456789012345'
        request.form['form.f3'] = '11.1'
        request.form['form.actions.apply'] = u''
        Form(foo, request)()
        
        # check new values in object
        self.assertEqual(foo.f1, 1.123)
        self.assertEqual(foo.f2, 2.23456789012345)
        self.assertEqual(foo.f3, 11.1)

    def test_missing_value(self):
        foo = FloatTest()
        request = TestRequest()

        # submit missing values for f2 and f3
        request.form['form.f1'] = ''
        request.form['form.f2'] = ''
        request.form['form.f3'] = '1.1'
        request.form['form.actions.apply'] = u''
        Form(foo, request)()
 
        # check new values in object
        self.assertEqual(foo.f1, None)
        self.assertEqual(foo.f2, None) # None is default missing_value
        self.assertEqual(foo.f3, 1.1)  # 0 is from f3.missing_value=0

    def test_required_validation(self):
        foo = FloatTest()
        request = TestRequest()
        
        # submit missing values for required field f1
        request.form['form.f1'] = ''
        request.form['form.f2'] = ''
        request.form['form.f3'] = ''
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        # confirm error msgs
        f3_index = html.find('form.f3')
        missing_index = html.find('missing')
        self.assertTrue(missing_index > f3_index)
        self.assertTrue(missing_index != -1)

    def test_invalid_allowed_value(self):
        foo = FloatTest()
        request = TestRequest()
        
        # submit a value for f3 that isn't allowed
        request.form['form.f3'] = '10000'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        self.assertTrue('Invalid' in html)

    def test_min_max_validation(self):
        foo = FloatTest()
        request = TestRequest()

        # submit value for f1 that is too low
        request.form['form.f1'] = '-1'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        self.assertTrue('Value is too small' in html)

        request = TestRequest()

        request.form['form.f1'] = '1000.2'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        self.assertTrue('Value is too big' in html)

    def test_omitted_value(self):
        foo = FloatTest()
        request = TestRequest()

        # confirm default values
        self.assertTrue(foo.f1 is None)
        self.assertEqual(foo.f2, 1.1)
        self.assertEqual(foo.f3, 2.1)

        # submit change with only f2 present -- note that required
        # field f1 is omitted, which should not cause a validation error
        request.form['form.f2'] = ''
        request.form['form.actions.apply'] = u''
        Form(foo, request)()

        # check new value in object
        self.assertTrue(foo.f1 is None)
        self.assertTrue(foo.f2 is None)
        self.assertEqual(foo.f3, 2.1)

    def test_conversion(self):
        foo = FloatTest()
        request = TestRequest()

        # submit value for f1 that cannot be convert to an float
        request.form['form.f1'] = 'foo'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        self.assertTrue('Invalid floating point data' in html)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

