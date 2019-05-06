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
"""DateTime Widget Functional Tests
"""
import unittest

import re
from datetime import datetime

from zope.interface import Interface, implementer
from zope.schema import Datetime, Choice
from zope.formlib import form
from zope.publisher.browser import TestRequest
from zope.formlib.widgets import DatetimeWidget, DropdownWidget, ChoiceInputWidget
from zope.formlib.tests.functionalsupport import FunctionalWidgetTestCase
import zope.schema.interfaces
from zope.datetime import parseDatetimetz, tzinfo

class IDatetimeTest(Interface):
    d1 = Datetime(
        required=True,
        min=datetime(2003, 1, 1, tzinfo=tzinfo(0)),
        max=datetime(2020, 12, 31, tzinfo=tzinfo(0)))

    d2 = Datetime(
        required=False)

    d3 = Choice(
        required=False,
        values=(
            datetime(2003, 9, 15, tzinfo=tzinfo(0)),
            datetime(2003, 10, 15, tzinfo=tzinfo(0))),
        missing_value=datetime(2000, 1, 1, tzinfo=tzinfo(0)))

@implementer(IDatetimeTest)
class DatetimeTest(object):

    def __init__(self):
        self.d1 = datetime(2003, 4, 6, tzinfo=tzinfo(0))
        self.d2 = datetime(2003, 8, 6, tzinfo=tzinfo(0))
        self.d3 = None

class Form(form.EditForm):
    form_fields = form.fields(IDatetimeTest)
    
class Test(FunctionalWidgetTestCase):

    widgets = [
        (zope.schema.interfaces.IDatetime, DatetimeWidget),
        (zope.schema.interfaces.IChoice, ChoiceInputWidget),
        ((zope.schema.interfaces.IChoice, zope.schema.interfaces.IVocabularyTokenized),
         DropdownWidget)]
    
    def getDateForField(self, field, source):
        """Returns a datetime object for the specified field in source.

        Returns None if the field value cannot be converted to date.
        """

        # look in input element first
        pattern = '<input .* name="form.%s".* value="(.*)".*>' % field
        m = re.search(pattern, source)
        if m is None:
            # look in a select element
            pattern = '<select .* name="form.%s".*>.*' \
                '<option value="(.*)" selected>*.</select>' % field
            m = re.search(pattern, source, re.DOTALL)
            if m is None:
                return None
        return parseDatetimetz(m.group(1))

    def test_display_editform(self):
        foo = DatetimeTest()
        request = TestRequest()

        html = Form(foo, request)()
        
        # confirm date values in form with actual values
        self.assertEqual(self.getDateForField('d1', html),
            foo.d1)
        self.assertEqual(self.getDateForField('d2', html),
            foo.d2)
        self.assertTrue(self.getDateForField('d3', html) is None)


    def test_submit_editform(self):
        foo = DatetimeTest()
        request = TestRequest()

        request.form['form.d1'] = u'2003-02-01 00:00:00+00:00'
        request.form['form.d2'] = u'2003-02-02 00:00:00+00:00'
        request.form['form.d3'] = u'2003-10-15 00:00:00+00:00'
        request.form['form.actions.apply'] = u''

        Form(foo, request)()

        self.assertEqual(foo.d1, datetime(2003, 2, 1, tzinfo=tzinfo(0)))
        self.assertEqual(foo.d2, datetime(2003, 2, 2, tzinfo=tzinfo(0)))
        self.assertEqual(foo.d3, datetime(2003, 10, 15, tzinfo=tzinfo(0)))

    def test_missing_value(self):
        foo = DatetimeTest()
        request = TestRequest()

        # submit missing values for d2 and d3
        request.form['form.d2'] = ''
        request.form['form.d3-empty-marker'] = ''

        request.form['form.actions.apply'] = u''
        Form(foo, request)()
        
        self.assertTrue(foo.d2 is None) # default missing_value for dates
        # 2000-1-1 is missing_value for d3
        self.assertEqual(foo.d3, datetime(2000, 1, 1, tzinfo=tzinfo(0)))

    def test_required_validation(self):
        foo = DatetimeTest()
        request = TestRequest()

        request.form['form.d1'] = ''
        request.form['form.d2'] = ''
        request.form['form.d3'] = ''

        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()
        
        # confirm error msgs

        # only Required input is missing after d1
        d1_index = html.find('form.d1')
        self.assertTrue(html.find('Required input is missing', d1_index) != -1)
        # but not after d2 or further
        d2_index = html.find('form.d2')
        self.assertTrue(html.find('Required input is missing', d2_index) == -1)
        

    def test_invalid_value(self):
        foo = DatetimeTest()
        request = TestRequest()

        # submit a value for d3 that isn't allowed
        request.form['form.d3'] = u'2003-02-01 12:00:00+00:00'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        # Invalid value message for d3
        d3_index = html.find('form.d3')
        self.assertTrue(html.find('Invalid', d3_index) != -1)

    def test_min_max_validation(self):
        foo = DatetimeTest()
        request = TestRequest()

        # submit value for d1 that is too low
        request.form['form.d1'] = u'2002-12-31 12:00:00+00:00'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()
        
        d1_index = html.find('form.d1')
        self.assertTrue(html.find('Value is too small') != -1)
        d2_index = html.find('form.d2')
        self.assertTrue(html.find('Value is too small', d2_index) == -1)

        request = TestRequest()
        # submit value for d1 that is too high
        request.form['form.d1'] = u'2021-12-01 12:00:00+00:00'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        self.assertTrue(html.find('Value is too big') != -1)
        d2_index = html.find('form.d2')
        self.assertTrue(html.find('Value is too big', d2_index) == -1)

    def test_omitted_value(self):
        foo = DatetimeTest()
        request = TestRequest()
        
        # remember default values
        d1 = foo.d1
        d2 = foo.d2
        self.assertTrue(d2 is not None)
        d3 = foo.d3

        # submit change with only d2 present -- note that required
        # field d1 is omitted, which should not cause a validation error
        request.form['form.d2'] = ''
        request.form['form.actions.apply'] = u''

        Form(foo, request)()
        
        # check new value in object
        self.assertEqual(foo.d1, d1)
        self.assertTrue(foo.d2 is None)
        self.assertEqual(foo.d3, d3)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite
