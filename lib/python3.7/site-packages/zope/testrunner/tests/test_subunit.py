##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
"""Unit tests for the testrunner's subunit integration."""


import io
import sys
import unittest

from zope.testrunner import formatter


try:
    unichr
except NameError:
    unichr = chr # Python 3


try:
    import subunit
    subunit
except ImportError:
    def test_suite():
        return unittest.TestSuite()
else:

    class TestSubunitTracebackPrintingMixin(object):

        def makeByteStringFailure(self, text, encoding):
            try:
                if sys.version_info[0] < 3:
                    # On Python 2, note that this deliberately throws a
                    # string of bytes instead of a unicode object.  This
                    # simulates errors thrown by utf8-encoded doctests.
                    bytestr = text.encode(encoding)
                    self.fail(bytestr)
                else:
                    # On Python 3, it's more accurate to just use the
                    # Unicode text directly.
                    self.fail(text)
            except self.failureException:
                return sys.exc_info()

        def test_print_failure_containing_utf8_bytestrings(self):
            exc_info = self.makeByteStringFailure(unichr(6514), 'utf8')
            self.subunit_formatter.test_failure(self, 0, exc_info)
            assert b"AssertionError: \xe1\xa5\xb2" in self.output.getvalue()
            # '\xe1\xa5\xb2'.decode('utf-8') == unichr(6514)

        def test_print_error_containing_utf8_bytestrings(self):
            exc_info = self.makeByteStringFailure(unichr(6514), 'utf8')
            self.subunit_formatter.test_error(self, 0, exc_info)
            assert b"AssertionError: \xe1\xa5\xb2" in self.output.getvalue()
            # '\xe1\xa5\xb2'.decode('utf-8') == unichr(6514)

        @unittest.skipIf(
            sys.version_info[0] >= 3,
            'Tracebacks are always Unicode on Python 3')
        def test_print_failure_containing_latin1_bytestrings(self):
            exc_info = self.makeByteStringFailure(unichr(241), 'latin1')
            self.subunit_formatter.test_failure(self, 0, exc_info)
            assert b"AssertionError: \xef\xbf\xbd" in self.output.getvalue()
            # '\xef\xbf\xbd'.decode('utf-8') = unichr(0xFFFD)

    class TestSubunitTracebackPrinting(
            TestSubunitTracebackPrintingMixin, unittest.TestCase):

        def setUp(self):
            class FormatterOptions:
                verbose = False
            options = FormatterOptions()

            self.output = io.BytesIO()
            self.subunit_formatter = formatter.SubunitOutputFormatter(
                options, stream=self.output)

    class TestSubunitV2TracebackPrinting(
            TestSubunitTracebackPrintingMixin, unittest.TestCase):

        def setUp(self):
            class FormatterOptions:
                verbose = False
            options = FormatterOptions()

            self.output = io.BytesIO()
            self.subunit_formatter = formatter.SubunitV2OutputFormatter(
                options, stream=self.output)

    def test_suite():
        return unittest.defaultTestLoader.loadTestsFromName(__name__)
