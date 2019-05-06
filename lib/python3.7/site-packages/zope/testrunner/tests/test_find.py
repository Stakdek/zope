##############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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
"""Unit tests for test discovery."""

import doctest
import os.path
import unittest

from zope.testrunner import find


class UniquenessOptions:
    """A basic mock of our command-line options."""

    keepbytecode = True
    at_level = 99
    test = []
    module = []
    require_unique_ids = True


class TestUniqueness(unittest.TestCase):
    """Test how the testrunner handles non-unique IDs."""

    def setUp(self):
        super(TestUniqueness, self).setUp()
        suites = [
            doctest.DocFileSuite('testrunner-ex/sampletests.rst'),
            doctest.DocFileSuite('testrunner-ex/sampletests.rst'),
            doctest.DocFileSuite('testrunner-ex/sampletestsl.rst'),
            doctest.DocFileSuite('testrunner-ex/sampletestsl.rst'),
            ]
        self.test_suites = unittest.TestSuite(suites)

    def test_tests_from_suite_records_duplicate_test_ids(self):
        # If tests_from_suite encounters a test ID which has already been
        # registered, it records them in the duplicated_test_ids set it is
        # passed.
        duplicated_test_ids = set()
        list(find.tests_from_suite(
            self.test_suites, UniquenessOptions(),
            duplicated_test_ids=duplicated_test_ids))
        self.assertNotEqual(0, len(duplicated_test_ids))

    def test_tests_from_suite_ignores_duplicate_ids_if_option_not_set(self):
        # If the require_unique_ids option is not set, tests_from_suite will
        # not record any of the IDs as duplicates.
        options = UniquenessOptions()
        options.require_unique_ids = False
        duplicated_test_ids = set()
        list(find.tests_from_suite(
            self.test_suites, options,
            duplicated_test_ids=duplicated_test_ids))
        self.assertEqual(0, len(duplicated_test_ids))

    def test_find_tests_raises_error_if_duplicates_found(self):
        # If find_tests, which calls tests_from_suite, finds a duplicate
        # test ID, it raises an error.
        self.assertRaises(
            find.DuplicateTestIDError,
            find.find_tests, UniquenessOptions(), [self.test_suites])

    def test_DuplicateTestIDError_message_contains_all_test_ids(self):
        # The error raised by find_tests when duplicates are encountered
        # contains all the duplicate test IDs it found.
        with self.assertRaises(find.DuplicateTestIDError) as e:
            find.find_tests(UniquenessOptions(), [self.test_suites])
        self.assertIn(
            os.path.join('testrunner-ex', 'sampletests.rst'), str(e.exception))
        self.assertIn(
            os.path.join('testrunner-ex', 'sampletestsl.rst'),
            str(e.exception))
