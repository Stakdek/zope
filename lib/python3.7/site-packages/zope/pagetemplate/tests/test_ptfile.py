##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Tests of PageTemplateFile.
"""
import os
import tempfile
import unittest

import six
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

class AbstractPTCase(object):

    def get_pt(self, text=b'<html />'):
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(text)
        self.addCleanup(os.unlink, f.name)
        pt = PageTemplateFile(f.name)
        pt.read()
        return pt

class TypeSniffingTestCase(AbstractPTCase,
                           unittest.TestCase):

    def check_content_type(self, text, expected_type):
        pt = self.get_pt(text)
        self.assertEqual(pt.content_type, expected_type)

    def test_sniffer_xml_ascii(self):
        self.check_content_type(
            b"<?xml version='1.0' encoding='ascii'?><doc/>",
            "text/xml")
        self.check_content_type(
            b"<?xml\tversion='1.0' encoding='ascii'?><doc/>",
            "text/xml")

    def test_sniffer_xml_utf8(self):
        # w/out byte order mark
        self.check_content_type(
            b"<?xml version='1.0' encoding='utf-8'?><doc/>",
            "text/xml")
        self.check_content_type(
            b"<?xml\tversion='1.0' encoding='utf-8'?><doc/>",
            "text/xml")
        # with byte order mark
        self.check_content_type(
            b"\xef\xbb\xbf<?xml version='1.0' encoding='utf-8'?><doc/>",
            "text/xml")
        self.check_content_type(
            b"\xef\xbb\xbf<?xml\tversion='1.0' encoding='utf-8'?><doc/>",
            "text/xml")

    def test_sniffer_xml_utf16_be(self):
        # w/out byte order mark
        self.check_content_type(
            b"\0<\0?\0x\0m\0l\0 \0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'"
            b"\0 \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>"
            b"\0<\0d\0o\0c\0/\0>",
            "text/xml")
        self.check_content_type(
            b"\0<\0?\0x\0m\0l\0\t\0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'"
            b"\0 \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>"
            b"\0<\0d\0o\0c\0/\0>",
            "text/xml")
        # with byte order mark
        self.check_content_type(
            b"\xfe\xff"
            b"\0<\0?\0x\0m\0l\0 \0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'"
            b"\0 \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>"
            b"\0<\0d\0o\0c\0/\0>",
            "text/xml")
        self.check_content_type(
            b"\xfe\xff"
            b"\0<\0?\0x\0m\0l\0\t\0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'"
            b"\0 \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>"
            b"\0<\0d\0o\0c\0/\0>",
            "text/xml")

    def test_sniffer_xml_utf16_le(self):
        # w/out byte order mark
        self.check_content_type(
            b"<\0?\0x\0m\0l\0 \0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'\0"
            b" \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>\0"
            b"<\0d\0o\0c\0/\0>\n",
            "text/xml")
        self.check_content_type(
            b"<\0?\0x\0m\0l\0\t\0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'\0"
            b" \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>\0"
            b"<\0d\0o\0c\0/\0>\0",
            "text/xml")
        # with byte order mark
        self.check_content_type(
            b"\xff\xfe"
            b"<\0?\0x\0m\0l\0 \0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'\0"
            b" \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>\0"
            b"<\0d\0o\0c\0/\0>\0",
            "text/xml")
        self.check_content_type(
            b"\xff\xfe"
            b"<\0?\0x\0m\0l\0\t\0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'\0"
            b" \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>\0"
            b"<\0d\0o\0c\0/\0>\0",
            "text/xml")

    HTML_PUBLIC_ID = "-//W3C//DTD HTML 4.01 Transitional//EN"
    HTML_SYSTEM_ID = "http://www.w3.org/TR/html4/loose.dtd"

    def test_sniffer_html_ascii(self):
        self.check_content_type(
            ("<!DOCTYPE html [ SYSTEM '%s' ]><html></html>"
             % self.HTML_SYSTEM_ID).encode("utf-8"),
            "text/html")
        self.check_content_type(
            b"<html><head><title>sample document</title></head></html>",
            "text/html")

    @unittest.expectedFailure
    def test_sniffer_xml_simple(self):
        # TODO: This reflects a case that simply isn't handled by the
        # sniffer; there are many, but it gets it right more often than
        # before. This case actually returns text/html
        self.check_content_type(b"<doc><element/></doc>",
                                "text/xml")

    def test_html_default_encoding(self):
        pt = self.get_pt(
            b"<html><head><title>"
            # 'Test' in russian (utf-8)
            b"\xd0\xa2\xd0\xb5\xd1\x81\xd1\x82"
            b"</title></head></html>")
        rendered = pt()
        self.assertTrue(isinstance(rendered, six.text_type))
        self.assertEqual(rendered.strip(),
                         (u"<html><head><title>"
                          u"\u0422\u0435\u0441\u0442"
                          u"</title></head></html>"))

    def test_html_encoding_by_meta(self):
        pt = self.get_pt(
            b"<html><head><title>"
            # 'Test' in russian (windows-1251)
            b"\xd2\xe5\xf1\xf2"
            b'</title><meta http-equiv="Content-Type"'
            b' content="text/html; charset=windows-1251">'
            b"</head></html>")
        rendered = pt()
        self.assertTrue(isinstance(rendered, six.text_type))
        self.assertEqual(rendered.strip(),
                         (u"<html><head><title>"
                          u"\u0422\u0435\u0441\u0442"
                          u"</title></head></html>"))

    def test_xhtml(self):
        pt = self.get_pt(
            b"<html><head><title>"
            # 'Test' in russian (windows-1251)
            b"\xd2\xe5\xf1\xf2"
            b'</title><meta http-equiv="Content-Type"'
            b' content="text/html; charset=windows-1251"/>'
            b"</head></html>")
        rendered = pt()
        self.assertTrue(isinstance(rendered, six.text_type))
        self.assertEqual(rendered.strip(),
                         (u"<html><head><title>"
                          u"\u0422\u0435\u0441\u0442"
                          u"</title></head></html>"))


class TestPageTemplateFile(AbstractPTCase,
                           unittest.TestCase):

    def test_no_such_file(self):
        with self.assertRaises(ValueError):
            PageTemplateFile('this file does not exist')

    def test_prefix_str(self):
        pt = PageTemplateFile(os.path.basename(__file__),
                              _prefix=os.path.dirname(__file__))
        self.assertEqual(pt.filename, __file__)


    def test_cook_no_debug(self):
        pt = self.get_pt()
        pt._v_debug = False
        pt._cook_check()
        self.assertTrue(pt._v_last_read)
        lr = pt._v_last_read
        pt._cook_check()
        self.assertEqual(lr, pt._v_last_read)


    def test_cook_mtime_fails(self):
        pt = self.get_pt()

        getmtime = os.path.getmtime
        def bad(_path):
            raise OSError()
        os.path.getmtime = bad
        try:
            pt._cook_check()
        finally:
            os.path.getmtime = getmtime

        self.assertEqual(0, pt._v_last_read)

    def test_pickle_not_allowed(self):
        import pickle
        pt = self.get_pt()

        with self.assertRaises(TypeError):
            pickle.dumps(pt)
