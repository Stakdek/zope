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
"""TextArea Functional Tests
"""
import unittest

from zope.interface import Interface, implementer
from zope.schema import Text
from zope.formlib import form
from zope.publisher.browser import TestRequest
from zope.formlib.tests.support import patternExists
from zope.formlib.widgets import TextAreaWidget
from zope.formlib.tests.functionalsupport import FunctionalWidgetTestCase
import zope.schema.interfaces

class ITextTest(Interface):
    s1 = Text(
        required=True,
        min_length=2,
        max_length=10)

    s2 = Text(
        required=False,
        missing_value=u'')

    s3 = Text(
        required=False)

@implementer(ITextTest)
class TextTest(object):

    def __init__(self):
        self.s1 = ''
        self.s2 = u'foo'
        self.s3 = None

class Form(form.EditForm):
    form_fields = form.fields(ITextTest)

class Test(FunctionalWidgetTestCase):
    widgets = [
        (zope.schema.interfaces.IText, TextAreaWidget),
        ]
    
    def test_display_editform(self):
        foo = TextTest()
        request = TestRequest()

        html = Form(foo, request)()
    
        # all fields should be displayed in text fields
        self.assertTrue(patternExists(
            '<textarea .* name="form.s1".*></textarea>',
            html))
        self.assertTrue(patternExists(
            '<textarea .* name="form.s2".*>foo</textarea>',
            html))
        self.assertTrue(patternExists(
            '<textarea .* name="form.s3".*></textarea>',
            html))

    def test_submit_editform(self):
        foo = TextTest()
        request = TestRequest()

        request.form['form.s1'] = u'foo'
        request.form['form.s2'] = u'bar'
        request.form['form.s3'] = u'baz'
        request.form['form.actions.apply'] = u''

        Form(foo, request)()
        
        # check new values in object
        self.assertEqual(foo.s1, u'foo')
        self.assertEqual(foo.s2, u'bar')
        self.assertEqual(foo.s3, u'baz')

    def test_invalid_type(self):
        """Tests textarea widget's handling of invalid unicode input.

        The text widget will succeed in converting any form input into
        unicode.
        """
        foo = TextTest()
        request = TestRequest()

        # submit invalid type for text
        request.form['form.s1'] = 123 # not unicode
        request.form['form.actions.apply'] = u''

        html = Form(foo, request)()

        # Note: We don't have a invalid field value
        # since we convert the value to unicode
        self.assertTrue(not 'Object is of wrong type' in html)

    def test_missing_value(self):
        foo = TextTest()
        request = TestRequest()

        # submit missing values for s2 and s3
        request.form['form.s1'] = u'foo'
        request.form['form.s2'] = ''
        request.form['form.s3'] = ''
        request.form['form.actions.apply'] = u''

        Form(foo, request)()

        # check new value in object
        self.assertEqual(foo.s1, u'foo')
        self.assertEqual(foo.s2, u'')   # default missing_value
        self.assertEqual(foo.s3, None)  # None is s3's missing_value

    def test_required_validation(self):
        foo = TextTest()
        request = TestRequest()
        
        # submit missing values for required field s1
        request.form['form.s1'] = ''
        request.form['form.s2'] = ''
        request.form['form.s3'] = ''
        request.form['form.actions.apply'] = u''

        html = Form(foo, request)()

        # confirm error msgs
        s1_index = html.find('form.s1')
        s2_index = html.find('form.s2')
        missing_index = html.find('missing')
        self.assertTrue(s1_index < missing_index < s2_index)

    def test_length_validation(self):
        foo = TextTest()
        request = TestRequest()
        
        # submit value for s1 that is too short
        request.form['form.s1'] = u'a'
        request.form['form.actions.apply'] = u''

        html = Form(foo, request)()

        self.assertTrue('Value is too short' in html)

        # submit value for s1 that is too long
        request.form['form.s1'] = u'12345678901'
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()

        self.assertTrue('Value is too long' in html)

    def test_omitted_value(self):
        foo = TextTest()
        request = TestRequest()

        # confirm default values
        self.assertEqual(foo.s1, '')
        self.assertEqual(foo.s2, u'foo')
        self.assertTrue(foo.s3 is None)

        # submit change with only s2 present -- note that required
        # field s1 is omitted, which should not cause a validation error
        request.form['form.s2'] = u'bar'
        request.form['form.actions.apply'] = u''

        Form(foo, request)()
        
        # check new values in object
        self.assertEqual(foo.s1, '')
        self.assertEqual(foo.s2, u'bar')
        self.assertTrue(foo.s3 is None)

    def test_conversion(self):
        foo = TextTest()
        request = TestRequest()

        # confirm that line terminators are converted correctly on post
        request.form['form.s2'] = u'line1\r\nline2' # CRLF per RFC 822 
        request.form['form.actions.apply'] = u''
        html = Form(foo, request)()
        
        self.assertEqual(foo.s2, u'line1\nline2')

        # confirm conversion to HTML

        request = TestRequest()
        html = Form(foo, request)()
        self.assertTrue(patternExists('line1\r\nline2', html))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite
