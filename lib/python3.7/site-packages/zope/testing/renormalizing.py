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
import sys
import doctest


IGNORE_EXCEPTION_MODULE_IN_PYTHON2 = doctest.register_optionflag(
    'IGNORE_EXCEPTION_MODULE_IN_PYTHON2')
IGNORE_EXCEPTION_MODULE_IN_PYTHON2_HINT = """\
===============================================================
HINT:
  The optionflag IGNORE_EXCEPTION_MODULE_IN_PYTHON2 is set.
  You seem to test traceback output.
  If you are indeed, make sure to use the full dotted name of
  the exception class like Python 3 displays,
  even though you are running the tests in Python 2.
  The exception message needs to be last line (and thus not
  split over multiple lines).
==============================================================="""


class OutputChecker(doctest.OutputChecker):
    """Pattern-normalizing outout checker
    """

    def __init__(self, patterns=None):
        if patterns is None:
            patterns = []
        self.transformers = list(map(self._cook, patterns))

    def __add__(self, other):
        if not isinstance(other, RENormalizing):
            return NotImplemented
        return RENormalizing(self.transformers + other.transformers)

    def _cook(self, pattern):
        if hasattr(pattern, '__call__'):
            return pattern
        regexp, replacement = pattern
        return lambda text: regexp.sub(replacement, text)

    def check_output(self, want, got, optionflags):
        if got == want:
            return True

        for transformer in self.transformers:
            want = transformer(want)
            got = transformer(got)

        if sys.version_info[0] < 3:
            if optionflags & IGNORE_EXCEPTION_MODULE_IN_PYTHON2:
                want = strip_dottedname_from_traceback(want)

        return doctest.OutputChecker.check_output(self, want, got, optionflags)

    def output_difference(self, example, got, optionflags):

        want = example.want

        # If want is empty, use original outputter. This is useful
        # when setting up tests for the first time.  In that case, we
        # generally use the differencer to display output, which we evaluate
        # by hand.
        if not want.strip():
            return doctest.OutputChecker.output_difference(
                self, example, got, optionflags)

        # Dang, this isn't as easy to override as we might wish
        original = want

        for transformer in self.transformers:
            want = transformer(want)
            got = transformer(got)

        # temporarily hack example with normalized want:
        example.want = want

        if sys.version_info[0] < 3:
            if optionflags & IGNORE_EXCEPTION_MODULE_IN_PYTHON2:
                if maybe_a_traceback(got) is not None:
                    got += IGNORE_EXCEPTION_MODULE_IN_PYTHON2_HINT

        result = doctest.OutputChecker.output_difference(
            self, example, got, optionflags)
        example.want = original

        return result

RENormalizing = OutputChecker


def maybe_a_traceback(string):
    # We wanted to confirm more strictly we're dealing with a traceback here.
    # However, doctest will preprocess exception output. It gets rid of the
    # the stack trace and the "Traceback (most recent call last)"-part. It
    # passes only the exception message to the checker.
    if not string:
        return None

    lines = string.splitlines()
    last = lines[-1]
    words = last.split(' ')
    first = words[0]
    if not first.endswith(':'):
        return None

    return lines, last, words, first


def strip_dottedname_from_traceback(string):
    maybe = maybe_a_traceback(string)
    if maybe is None:
        return string

    lines, last, words, first = maybe
    name = first.split('.')[-1]
    words[0] = name
    last = ' '.join(words)
    lines[-1] = last
    return '\n'.join(lines)
