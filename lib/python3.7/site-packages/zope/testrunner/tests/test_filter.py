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
"""Unit tests for the testrunner's filtering functions
"""

import unittest

from zope.testrunner import filter


class TestFilterMakerFunction(unittest.TestCase):
    def test_no_filters(self):
        accept = filter.build_filtering_func([])
        self.assertFalse(accept('test_xx'))
        self.assertFalse(accept('test_yy'))
        self.assertFalse(accept('test_zz'))

    def test_match_all_filter(self):
        accept = filter.build_filtering_func(['.'])
        self.assertTrue(accept('test_xx'))
        self.assertTrue(accept('test_yy'))
        self.assertTrue(accept('test_zz'))

    def test_select_specific_pattern(self):
        accept = filter.build_filtering_func(['xx'])
        self.assertTrue(accept('test_xx'))
        self.assertFalse(accept('test_yy'))
        self.assertFalse(accept('test_zz'))

    def test_select_several_patterns(self):
        accept = filter.build_filtering_func(['xx', 'yy'])
        self.assertTrue(accept('test_xx'))
        self.assertTrue(accept('test_yy'))
        self.assertFalse(accept('test_zz'))

    def test_reject_one_pattern(self):
        accept = filter.build_filtering_func(['!xx'])
        self.assertFalse(accept('test_xx'))
        self.assertTrue(accept('test_yy'))
        self.assertTrue(accept('test_zz'))

    def test_reject_several_patterns(self):
        accept = filter.build_filtering_func(['!xx', '!zz'])
        self.assertFalse(accept('test_xx'))
        self.assertTrue(accept('test_yy'))
        self.assertFalse(accept('test_zz'))

    def test_accept_and_reject(self):
        accept = filter.build_filtering_func(['!xx', 'yy'])
        self.assertFalse(accept('test_xx'))
        self.assertTrue(accept('test_yy'))
        self.assertFalse(accept('test_zz'))

    def test_accept_and_reject_overlap(self):
        accept = filter.build_filtering_func(['!test_', 'yy'])
        self.assertFalse(accept('test_xx'))
        self.assertFalse(accept('test_yy'))
        self.assertFalse(accept('test_zz'))

    def test_accept_and_reject_same(self):
        accept = filter.build_filtering_func(['yy', '!yy'])
        self.assertFalse(accept('test_xx'))
        self.assertFalse(accept('test_yy'))
        self.assertFalse(accept('test_zz'))
