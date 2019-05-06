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
"""Radio Widget Functional Tests
"""
import unittest

from zope.interface import Interface, implementer
from zope.schema import Bool
from zope.formlib import form
from zope.publisher.browser import TestRequest
from zope.formlib.tests.support import patternExists
from zope.formlib.widgets import BooleanRadioWidget
from zope.formlib.tests.functionalsupport import FunctionalWidgetTestCase
import zope.schema.interfaces

class IFoo(Interface):
    bar = Bool(title=u'Bar')

@implementer(IFoo)
class Foo(object):
    def __init__(self):
        self.bar = True

class Form(form.EditForm):
    form_fields = form.fields(IFoo)
    form_fields['bar'].custom_widget = BooleanRadioWidget

    
class Test(FunctionalWidgetTestCase):
    widgets = [(zope.schema.interfaces.IBool, BooleanRadioWidget)]

    def test_display_editform(self):
        foo = Foo()
        request = TestRequest()
        html = Form(foo, request)()

        # bar field should be displayed as two radio buttons
        self.assertTrue(patternExists(
            '<input .*checked="checked".*name="form.bar".*type="radio".*'
            'value="on".* />',
            html))
        self.assertTrue(patternExists(
            '<input .*name="form.bar".*type="radio".*value="off".* />',
            html))

        # a hidden element is used to note that the field is present
        self.assertTrue(patternExists(
            '<input name="form.bar-empty-marker" type="hidden" value="1".* />',
            html))


    def test_submit_editform(self):
        foo = Foo()
        request = TestRequest()
        request.form['form.bar'] = 'off'
        request.form['form.actions.apply'] = u''
        Form(foo, request)()

        self.assertEqual(foo.bar, False)

    def test_missing_value(self):
        foo = Foo()
        request = TestRequest()
        
        # temporarily make bar field not required
        IFoo['bar'].required = False

        # submit missing value for bar
        request.form['form.bar-empty-marker'] = ''
        request.form['form.actions.apply'] = u''

        Form(foo, request)()
 
        # confirm use of missing_value as new object value
        self.assertTrue(IFoo['bar'].missing_value is None)
        self.assertTrue(foo.bar is None)

        # restore bar required state
        IFoo['bar'].required = True


    def test_required_validation(self):
        foo = Foo()
        request = TestRequest()

        self.assertTrue(IFoo['bar'].required)

        # submit missing value for bar
        request.form['form.bar-empty-marker'] = ''
        request.form['form.actions.apply'] = u''

        html = Form(foo, request)()
        
        # confirm error msgs
        self.assertTrue('Required input is missing' in html)
        

    def test_invalid_allowed_value(self):
        foo = Foo()
        request = TestRequest()

        # submit a value for bar isn't allowed
        request.form['form.bar'] = 'bogus'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        self.assertTrue('Invalid value' in html)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite
