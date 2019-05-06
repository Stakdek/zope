##############################################################################
#
# Copyright (c) 2001, 2002, 2006 Zope Foundation and Contributors.
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
"""Decimal Widget Functional Tests
"""
import unittest

import decimal
from zope.interface import Interface, implementer
from zope.schema import Decimal, Choice
from zope.formlib import form
from zope.publisher.browser import TestRequest
from zope.formlib.tests.support import patternExists
from zope.formlib.widgets import (
    DecimalWidget,
    DropdownWidget, ChoiceInputWidget)
from zope.formlib.tests.functionalsupport import FunctionalWidgetTestCase
import zope.schema.interfaces

class IDecimalTest(Interface):

    f1 = Decimal(
        required=False,
        min=decimal.Decimal("1.1"),
        max=decimal.Decimal("10.1"))

    f2 = Decimal(
        required=False)

    f3 = Choice(
        required=True,
        values=(decimal.Decimal("0.0"), decimal.Decimal("1.1"),
                decimal.Decimal("2.1"), decimal.Decimal("3.1"),
                decimal.Decimal("5.1"), decimal.Decimal("7.1"),
                decimal.Decimal("11.1")),
        missing_value=0)


@implementer(IDecimalTest)
class DecimalTest(object):

    def __init__(self):
        self.f1 = None
        self.f2 = decimal.Decimal("1.1")
        self.f3 = decimal.Decimal("2.1")


class Form(form.EditForm):
    form_fields = form.fields(IDecimalTest)

class Test(FunctionalWidgetTestCase):
    widgets = [
        (zope.schema.interfaces.IDecimal, DecimalWidget),
        (zope.schema.interfaces.IChoice, ChoiceInputWidget),
        ((zope.schema.interfaces.IChoice, zope.schema.interfaces.IVocabularyTokenized),
         DropdownWidget)]

    def test_display_editform(self):
        foo = DecimalTest()
        request = TestRequest()
        
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
        foo = DecimalTest()
        request = TestRequest()

        request.form['form.f1'] = '1.123'
        request.form['form.f2'] = '2.23456789012345'
        request.form['form.f3'] = '11.1'
        request.form['form.actions.apply'] = u''
        Form(foo, request)()

        # check new values in object
        self.assertEqual(foo.f1, decimal.Decimal("1.123"))
        self.assertEqual(foo.f2, decimal.Decimal("2.23456789012345"))
        self.assertEqual(foo.f3, decimal.Decimal("11.1"))

    def test_missing_value(self):
        foo = DecimalTest()
        request = TestRequest()

        request.form['form.f1'] = ''
        request.form['form.f2'] = ''
        request.form['form.f3'] = '1.1'
        request.form['form.actions.apply'] = u''
        Form(foo, request)()

        # check new values in object
        self.assertEqual(foo.f1, None)
        self.assertEqual(foo.f2, None) # None is default missing_value
        self.assertEqual(foo.f3, decimal.Decimal("1.1"))  # 0 is from f3.missing_value=0

    def test_required_validation(self):
        foo = DecimalTest()
        request = TestRequest()
        
        request.form['form.f1'] = ''
        request.form['form.f2'] = ''
        request.form['form.f3'] = ''
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        # confirm error msgs
        f3_index = html.find('form.f3')
        missing_index = html.find('Required input is missing')
        self.assertTrue(missing_index > f3_index)

    def test_invalid_allowed_value(self):
        foo = DecimalTest()
        request = TestRequest()

        # submit a value for f3 that isn't allowed
        request.form['form.f3'] = '10000'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        f3_index = html.find('form.f3')
        invalid_index = html.find('Invalid')
        self.assertTrue(invalid_index > f3_index)

    def test_min_max_validation(self):
        foo = DecimalTest()
        request = TestRequest()
        
        # submit value for f1 that is too low
        request.form['form.f1'] = '-1'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        f1_index = html.find('form.f1')
        f2_index = html.find('form.f2')
        too_small_index = html.find('Value is too small')
        self.assertTrue(too_small_index > f1_index)
        self.assertTrue(html.find('Value is too small', f2_index) == -1)

        # submit value for f1 that is too high
        request.form['form.f1'] = '1000.2'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        f1_index = html.find('form.f1')
        f2_index = html.find('form.f2')
        too_high_index = html.find('Value is too big')
        self.assertTrue(too_high_index > f1_index)
        self.assertTrue(html.find('Value is too small', f2_index) == -1)

    def test_omitted_value(self):
        foo = DecimalTest()
        request = TestRequest()

        # confirm default values
        self.assertTrue(foo.f1 is None)
        self.assertEqual(foo.f2, decimal.Decimal("1.1"))
        self.assertEqual(foo.f3, decimal.Decimal("2.1"))

        # submit change with only f2 present -- note that required
        # field f1 is omitted, which should not cause a validation error
        request.form['form.f2'] = ''
        request.form['form.actions.apply'] = u''
        Form(foo, request)()

        # check new value in object
        self.assertTrue(foo.f1 is None)
        self.assertTrue(foo.f2 is None)
        self.assertEqual(foo.f3, decimal.Decimal("2.1"))

    def test_conversion(self):
        foo = DecimalTest()
        request = TestRequest()

        # submit value for f1 that cannot be convert to an float
        request.form['form.f1'] = 'foo'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        f1_index = html.find('form.f1')
        f2_index = html.find('form.f2')
        invalid_index = html.find('Invalid decimal data')
        self.assertTrue(invalid_index > f1_index)
        self.assertTrue(html.find('Invalid decimal data', f2_index) == -1)
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

