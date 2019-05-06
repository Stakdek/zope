##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Tests of the contenttypes extension mechanism.
"""
from __future__ import print_function
import unittest

class ContentTypesTestCase(unittest.TestCase):

    def setUp(self):
        import mimetypes
        mimetypes.init()
        self._old_state = mimetypes.__dict__.copy()

    def tearDown(self):
        import mimetypes
        mimetypes.__dict__.clear()
        mimetypes.__dict__.update(self._old_state)

    def _check_types_count(self, delta):
        import mimetypes
        self.assertEqual(len(mimetypes.types_map),
                         len(self._old_state["types_map"]) + delta)

    def _getFilename(self, name):
        import os.path
        here = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(here, name)

    def test_main(self):
        import zope.contenttype
        result = []
        zope.contenttype.print = result.append
        zope.contenttype.main()
        del zope.contenttype.print
        self.assertTrue(result)

    def test_guess_content_type(self):
        from zope.contenttype import add_files
        from zope.contenttype import guess_content_type
        filename = self._getFilename('mime.types-1')
        add_files([filename])
        ctype, _encoding = guess_content_type(body=b'text file')
        self.assertEqual(ctype, "text/plain")
        ctype, _encoding = guess_content_type(body=b'\001binary')
        self.assertEqual(ctype, "application/octet-stream")
        ctype, _encoding = guess_content_type()
        self.assertEqual(ctype, "text/x-unknown-content-type")


    def test_add_one_file(self):
        from zope.contenttype import add_files
        from zope.contenttype import guess_content_type
        filename = self._getFilename('mime.types-1')
        add_files([filename])
        ctype, encoding = guess_content_type("foo.ztmt-1")
        self.assertTrue(encoding is None)
        self.assertEqual(ctype, "text/x-vnd.zope.test-mime-type-1")
        ctype, encoding = guess_content_type("foo.ztmt-1.gz")
        self.assertEqual(encoding, "gzip")
        self.assertEqual(ctype, "text/x-vnd.zope.test-mime-type-1")
        self._check_types_count(1)

    def test_add_two_files(self):
        from zope.contenttype import add_files
        from zope.contenttype import guess_content_type
        filename1 = self._getFilename('mime.types-1')
        filename2 = self._getFilename('mime.types-2')
        add_files([filename1, filename2])
        ctype, encoding = guess_content_type("foo.ztmt-1")
        self.assertTrue(encoding is None)
        self.assertEqual(ctype, "text/x-vnd.zope.test-mime-type-1")
        ctype, encoding = guess_content_type("foo.ztmt-2")
        self.assertTrue(encoding is None)
        self.assertEqual(ctype, "text/x-vnd.zope.test-mime-type-2")
        self._check_types_count(2)

    def test_text_type(self):
        HTML = b'<HtmL><body>hello world</body></html>'
        from zope.contenttype import text_type
        self.assertEqual(text_type(HTML),
                         'text/html')
        self.assertEqual(text_type(b'<?xml version="1.0"><foo/>'),
                         'text/xml')
        self.assertEqual(text_type(b'<?XML version="1.0"><foo/>'),
                         'text/xml')
        self.assertEqual(text_type(b'foo bar'),
                         'text/plain')
        self.assertEqual(text_type(b'<!DOCTYPE HTML PUBLIC '
                                   b'"-//W3C//DTD HTML 4.01 Transitional//EN" '
                                   b'"http://www.w3.org/TR/html4/loose.dtd">'),
                         'text/html')
        self.assertEqual(text_type(b'\n\n<!DOCTYPE html>\n'), 'text/html')
        # we can also parse text snippets
        self.assertEqual(text_type(b'<p>Hello</p>'), 'text/html')
        longtext = b'abc ' * 100
        self.assertEqual(text_type(b'<p>' + longtext + b'</p>'), 'text/html')
        # See https://bugs.launchpad.net/bugs/487998
        self.assertEqual(text_type(b' ' * 14 + HTML),
                         'text/html')
        self.assertEqual(text_type(b' ' * 14 + b'abc'),
                         'text/plain')
        self.assertEqual(text_type(b' ' * 14),
                         'text/plain')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
