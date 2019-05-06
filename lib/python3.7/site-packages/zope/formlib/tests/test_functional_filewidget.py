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
"""File Widget Tests
"""
import unittest

from zope.publisher.browser import TestRequest
from zope.interface import Interface, implementer
from zope.schema import Field
from zope.schema.interfaces import IField
from zope.formlib import form, _compat
from zope.formlib._compat import StringIO
from zope.formlib.tests.support import patternExists
from zope.formlib.widgets import FileWidget
from zope.formlib.tests.functionalsupport import FunctionalWidgetTestCase

class IFileField(IField):
    """Field for representing a file that can be edited by FileWidget."""

@implementer(IFileField)
class FileField(Field):
    pass

class IFileTest(Interface):
    f1 = FileField(required=True)
    f2 = FileField(required=False)

@implementer(IFileTest)
class FileTest(object):

    def __init__(self):
        self.f1 = None
        self.f2 = 'foo'

class Form(form.EditForm):
    form_fields = form.fields(IFileTest)
    form_fields['f1'].custom_widget = FileWidget
    form_fields['f2'].custom_widget = FileWidget

class SampleTextFile(StringIO):
    def __init__(self, buf, filename=''):
        StringIO.__init__(self, buf)
        self.filename = filename

class Test(FunctionalWidgetTestCase):

    sampleText = "The quick brown fox\njumped over the lazy dog."
    sampleTextFile = SampleTextFile(sampleText)

    emptyFileName = 'empty.txt'
    emptyFile = SampleTextFile('', emptyFileName)

    def test_display_editform(self):
        foo = FileTest()
        request = TestRequest()

        # display edit view
        html = Form(foo, request)()

        # field should be displayed in a file input element
        self.assertTrue(patternExists(
            '<input .* name="form.f1".* type="file".*>', html))
        self.assertTrue(patternExists(
            '<input .* name="form.f2".* type="file".*>', html))

    def test_submit_text(self):
        foo = FileTest()
        request = TestRequest()

        self.assertTrue(foo.f1 is None)
        self.assertEqual(foo.f2, 'foo')

        # submit a sample text file
        request.form['form.f1'] = self.sampleTextFile
        request.form['form.f2'] = self.sampleTextFile
        request.form['form.f1.used'] = ''
        request.form['form.f2.used'] = ''
        request.form['form.actions.apply'] = u''

        Form(foo, request)()

        # check new values in object
        self.assertEqual(foo.f1, self.sampleText)
        self.assertEqual(foo.f2, self.sampleText)

    def test_invalid_value(self):
        foo = FileTest()
        request = TestRequest()

        # submit an invalid file value
        request.form['form.f1'] = 'not a file - same as missing input'
        request.form['form.f1.used'] = ''
        request.form['form.f2.used'] = ''
        request.form['form.actions.apply'] = u''

        html = Form(foo, request)()

        self.assertTrue('Form input is not a file object', html)

    def test_required_validation(self):
        foo = FileTest()
        request = TestRequest()

        # submit missing value for required field f1
        request.form['form.f1.used'] = ''
        request.form['form.f2.used'] = ''
        request.form['form.actions.apply'] = u''

        html = Form(foo, request)()

        # confirm error msgs
        f1_index = html.find('form.f1')
        f2_index = html.find('form.f2')
        missing_index = html.find('Required input is missing')
        self.assertTrue(missing_index > f1_index)
        self.assertTrue(html.find('Required input is missing', f2_index) == -1)

    def test_empty_file(self):
        foo = FileTest()
        request = TestRequest()

        # submit missing value for required field f1
        request.form['form.f2'] = self.emptyFile
        request.form['form.f2.used'] = ''
        request.form['form.actions.apply'] = u''
        # we don't let f1 know that it was rendered
        # or else it will complain (see test_required_validation) and the
        # change will not succeed.

        Form(foo, request)()

        # new value for f1 should be field.missing_value (i.e, None)
        self.assertTrue(foo.f1 is None)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

