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
"""
ExceptionFormatter tests.
"""

import sys
from unittest import TestCase

from zExceptions import HTTPException
from zExceptions.ExceptionFormatter import format_exception


def tb(as_html=0):
    t, v, b = sys.exc_info()
    try:
        return ''.join(format_exception(t, v, b, as_html=as_html))
    finally:
        del b


class ExceptionForTesting(HTTPException):
    pass


class TestingTracebackSupplement(object):

    source_url = '/somepath'
    line = 634
    column = 57
    warnings = ['Repent, for the end is nigh']

    def __init__(self, expression):
        self.expression = expression


class Test(TestCase):

    def testBasicNamesText(self, as_html=0):
        try:
            raise ExceptionForTesting()
        except ExceptionForTesting:
            string = tb(as_html)
            # The traceback should include the name of this function.
            self.assertIn('testBasicNamesText', string)
            # The traceback should include the name of the exception.
            self.assertIn('ExceptionForTesting', string)
        else:
            self.fail('no exception occurred')

    def testBasicNamesHTML(self):
        self.testBasicNamesText(1)

    def testSupplement(self, as_html=0):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        "You are one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            # import pdb; pdb.set_trace()
            string = tb(as_html)
            # The source URL
            self.assertIn('/somepath', string)
            # The line number
            self.assertIn('634', string)
            # The column number
            self.assertIn('57', string)
            # The expression
            self.assertIn("You are one in a million", string)
            # The warning
            self.assertIn("Repent, for the end is nigh", string)
        else:
            self.fail('no exception occurred')

    def testSupplementHTML(self):
        self.testSupplement(1)

    def testTracebackInfo(self, as_html=0):
        try:
            __traceback_info__ = "Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            string = tb(as_html)
            if as_html:
                # Be sure quoting is happening.
                self.assertIn('Adam &amp; Eve', string)
            else:
                self.assertIn('Adam & Eve', string)
        else:
            self.fail('no exception occurred')

    def testTracebackInfoHTML(self):
        self.testTracebackInfo(1)

    def testMultipleLevels(self):
        # Makes sure many levels are shown in a traceback.
        def f(n):
            """Produces a (n + 1)-level traceback."""
            __traceback_info__ = 'level%d' % n
            if n > 0:
                f(n - 1)
            else:
                raise ExceptionForTesting

        try:
            f(10)
        except ExceptionForTesting:
            string = tb()
            for n in range(11):
                self.assertIn('level%d' % n, string)
        else:
            self.fail('no exception occurred')

    def testQuoteLastLine(self):
        class C:
            pass
        try:
            raise TypeError(C())
        except Exception:
            string = tb(1)
        else:
            self.fail('no exception occurred')
        self.assertIn('&lt;', string)
        self.assertIn('&gt;', string)
