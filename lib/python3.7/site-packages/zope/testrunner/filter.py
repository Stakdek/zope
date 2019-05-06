##############################################################################
#
# Copyright (c) 2004-2008 Zope Foundation and Contributors.
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
"""Filter which tests to run.
"""

import re

import zope.testrunner.feature


UNITTEST_LAYER = 'zope.testrunner.layer.UnitTests'


class Filter(zope.testrunner.feature.Feature):
    """Filters and orders all tests registered until now."""

    active = True

    def global_setup(self):
        layers = self.runner.tests_by_layer_name
        options = self.runner.options

        if UNITTEST_LAYER in layers:
            # We start out assuming unit tests should run and look for reasons
            # why they shouldn't be run.
            should_run = True
            if (not options.non_unit):
                if options.layer:
                    accept = build_filtering_func(options.layer)
                    should_run = accept(UNITTEST_LAYER)
                else:
                    should_run = True
            else:
                should_run = False

            if not should_run:
                layers.pop(UNITTEST_LAYER)

        if self.runner.options.resume_layer is not None:
            for name in list(layers):
                if name != self.runner.options.resume_layer:
                    layers.pop(name)
            if not layers:
                self.runner.options.output.error_with_banner(
                    "Cannot find layer %s" % self.runner.options.resume_layer)
                self.runner.errors.append(
                    ("subprocess failed for %s" %
                         self.runner.options.resume_layer,
                     None))
        elif self.runner.options.layer:
            accept = build_filtering_func(self.runner.options.layer)
            for name in list(layers):
                if not accept(name):
                    # No pattern matched this name so we remove it
                    layers.pop(name)

        if (self.runner.options.verbose and
            not self.runner.options.resume_layer):
            if self.runner.options.all:
                msg = "Running tests at all levels"
            else:
                msg = "Running tests at level %d" % self.runner.options.at_level
            self.runner.options.output.info(msg)

    def report(self):
        if not self.runner.do_run_tests:
            return
        if self.runner.options.resume_layer:
            return
        if self.runner.options.verbose:
            self.runner.options.output.tests_with_errors(self.runner.errors)
            self.runner.options.output.tests_with_failures(self.runner.failures)


def build_filtering_func(patterns):
    """Build a filtering function from a set of patterns

    Patterns are understood as regular expressions, with the additional feature
    that, prefixed by "!", they create a "don't match" rule.

    This returns a function which returns True if a string matches the set of
    patterns, or False if it doesn't match.

    """

    selected = []
    unselected = []

    for pattern in patterns:
        if pattern.startswith('!'):
            store = unselected.append
            pattern = pattern[1:]
        else:
            store = selected.append

        store(re.compile(pattern).search)

    if not selected and unselected:
        # If there's no selection patterns but some un-selection patterns,
        # suppose we want everything (that is, everything that matches '.'),
        # minus the un-selection ones.
        selected.append(re.compile('.').search)

    def accept(value):
        return (any(search(value) for search in selected) and not
                any(search(value) for search in unselected))

    return accept
