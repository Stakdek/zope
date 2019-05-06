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
"""Int Widget Functional Tests
"""
import unittest

from zope.interface import Interface, implementer
from zope.schema import Int, Choice
from zope.formlib import form
from zope.publisher.browser import TestRequest
from zope.formlib.tests.support import patternExists
from zope.formlib.widgets import (
    IntWidget,
    DropdownWidget, ChoiceInputWidget)
from zope.formlib.tests.functionalsupport import FunctionalWidgetTestCase
import zope.schema.interfaces

class IIntTest(Interface):
    i1 = Int(
        required=True,
        min=1,
        max=10)

    i2 = Int(
        required=False)

    i3 = Choice(
        required=False,
        values=(0, 1, 2, 3, 5, 7, 11),
        missing_value=0)


class IIntTest2(Interface):
    """Used to test an unusual care where missing_value is -1 and
    not in allowed_values."""

    i1 = Choice(
        required=False,
        missing_value=-1,
        values=(10, 20, 30))


@implementer(IIntTest)
class IntTest(object):

    def __init__(self):
        self.i1 = None
        self.i2 = 1
        self.i3 = 2


@implementer(IIntTest2)
class IntTest2(object):

    def __init__(self):
        self.i1 = 10

class Form(form.EditForm):
    form_fields = form.fields(IIntTest)

class Form2(form.EditForm):
    form_fields = form.fields(IIntTest2)
    
class Test(FunctionalWidgetTestCase):
    widgets = [
        (zope.schema.interfaces.IInt, IntWidget),
        (zope.schema.interfaces.IChoice, ChoiceInputWidget),
        ((zope.schema.interfaces.IChoice, zope.schema.interfaces.IVocabularyTokenized),
         DropdownWidget)]
    
    def test_display_editform(self):
        foo = IntTest()
        request = TestRequest()
        
        html = Form(foo, request)()
        
        # i1 and i2 should be displayed in text fields
        self.assertTrue(patternExists(
            '<input .* name="form.i1".* value="".*>', html))
        self.assertTrue(patternExists(
            '<input .* name="form.i2".* value="1".*>', html))
        
        # i3 should be in a dropdown
        self.assertTrue(patternExists(
            '<select .*name="form.i3".*>', html))
        self.assertTrue(patternExists(
            '<option selected="selected" value="2">2</option>',
            html))

    def test_submit_editform(self):
        foo = IntTest()
        request = TestRequest()

        request.form['form.i1'] = '1'
        request.form['form.i2'] = '2'
        request.form['form.i3'] = '3'
        request.form['form.actions.apply'] = u''
        
        Form(foo, request)()

        # check new values in object
        self.assertEqual(foo.i1, 1)
        self.assertEqual(foo.i2, 2)
        self.assertEqual(foo.i3, 3)

    def test_missing_value(self):
        foo = IntTest()
        request = TestRequest()
       
        # submit missing values for i2 and i3
        request.form['form.i1'] = '1'
        request.form['form.i2'] = ''
        request.form['form.i3-empty-marker'] = ''
        request.form['form.actions.apply'] = u''
        
        Form(foo, request)()

        # check new values in object
        self.assertEqual(foo.i1, 1)
        self.assertEqual(foo.i2, None) # None is default missing_value
        self.assertEqual(foo.i3, 0)  # 0 is from i3.missing_value=0

    def test_alternative_missing_value(self):
        """Tests the addition of an empty value at the top of the dropdown
        that, when selected, updates the field with form.missing_value.
        """
        foo = IntTest2() # note alt. class
        request = TestRequest()
        
        html = Form2(foo, request)()

        # confirm that i1 is has a blank item at top with value=""
        self.assertTrue(patternExists(
            '<select id="form.i1" name="form.i1" .*>', html))
        self.assertTrue(patternExists(
            '<option value="">.*</option>', html))
        self.assertTrue(patternExists(
            '<option selected="selected" value="10">10</option>',
            html))

        # submit form as if top item is selected
        request.form['form.i1-empty-marker'] = '1'
        request.form['form.actions.apply'] = u''
        html = Form2(foo, request)()
        
        # confirm new value is -1 -- i1.missing_value
        self.assertEqual(foo.i1, -1)

    def test_required_validation(self):
        foo = IntTest()
        request = TestRequest()
       
        # submit missing values for required field i1
        request.form['form.i1'] = ''
        request.form['form.i2'] = ''
        request.form['form.i3'] = ''
        request.form['form.actions.apply'] = u''
        
        html = Form(foo, request)()

        # confirm error msgs
        i1_index = html.find('form.i1')
        i2_index = html.find('form.i2')
        i3_index = html.find('form.i3')
        self.assertTrue(i1_index < html.find('missing') <  i2_index)
        self.assertTrue(html.find('missing', i2_index) == -1)
        self.assertTrue(html.find('missing', i3_index) == -1)

    def test_invalid_allowed_value(self):
        foo = IntTest()
        request = TestRequest()
       
        # submit a value for i3 that isn't allowed
        request.form['form.i3'] = '12'
        request.form['form.actions.apply'] = u''
        
        html = Form(foo, request)()

        i3_index = html.find('form.i3')
        invalid_index = html.find('Invalid')
        self.assertTrue(invalid_index != -1)
        self.assertTrue(invalid_index > i3_index)

    def test_min_max_validation(self):
        foo = IntTest()
        request = TestRequest()

        # submit value for i1 that is too low
        request.form['form.i1'] = '-1'
        request.form['form.actions.apply'] = u''
        
        html = Form(foo, request)()

        self.assertTrue('Value is too small' in html)
    
        # submit value for i1 that is too high
        request.form['form.i1'] = '11'
        request.form['form.actions.apply'] = u''
        
        html = Form(foo, request)()

        self.assertTrue('Value is too big' in html)

    def test_omitted_value(self):
        foo = IntTest()
        request = TestRequest()

        self.assertTrue(foo.i1 is None)
        self.assertEqual(foo.i2, 1)
        self.assertEqual(foo.i3, 2)

        # submit change with only i2 present -- note that required
        # field i1 is omitted, which should not cause a validation error
        request.form['form.i2'] = ''
        request.form['form.actions.apply'] = u''
        
        Form(foo, request)()

        # check new value in object
        self.assertTrue(foo.i1 is None)
        self.assertTrue(foo.i2 is None)
        self.assertEqual(foo.i3, 2)

    def test_conversion(self):
        foo = IntTest()
        request = TestRequest()

        request.form['form.i1'] = 'foo'
        request.form['form.actions.apply'] = u''
        
        html = Form(foo, request)()

        self.assertTrue('Invalid integer data' in html)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite
