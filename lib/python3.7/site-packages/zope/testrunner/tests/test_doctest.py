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
"""Test harness for the test runner itself.
"""
from __future__ import print_function

import doctest
import gc
import os
import re
import sys
import unittest

from zope.testing import renormalizing


#separated checkers for the different platform,
#because it s...s to maintain just one
if sys.platform == 'win32':
    checker = renormalizing.RENormalizing([
        # 2.5 changed the way pdb reports exceptions
        (re.compile(r"<class 'exceptions.(\w+)Error'>:"),
         r'exceptions.\1Error:'),

        #rewrite pdb prompt to ... the current location
        #windows, py2.4 pdb seems not to put the '>' on doctest locations
        #therefore we cut it here
        (re.compile('^> doctest[^\n]+->None$', re.M), '...->None'),

        #rewrite pdb prompt to ... the current location
        (re.compile('^> [^\n]+->None$', re.M), '> ...->None'),

        (re.compile(r"<module>"), (r'?')),
        (re.compile(r"<type 'exceptions.(\w+)Error'>:"),
         r'exceptions.\1Error:'),

        # testtools content formatter is used to mime-encode
        # tracebacks when the SubunitOutputFormatter is used, and the
        # resulting text includes a size which can vary depending on
        # the path included in the traceback.
        (re.compile(r'traceback\n[A-F\d]+', re.MULTILINE),
         r'traceback\nNNN'),

        (re.compile("'[A-Za-z]:\\\\"), "'"), # hopefully, we'll make Windows happy
                                             # replaces drives with nothing

        (re.compile(r'\\\\'), '/'), # more Windows happiness
                                    # double backslashes in coverage???

        (re.compile(r'\\'), '/'), # even more Windows happiness
                                  # replaces backslashes in paths

        (re.compile(r'/r$', re.MULTILINE), '\\r'), # undo some of that

        #this is a magic to put linefeeds into the doctest
        (re.compile('##r##\n'), '\r'),

        (re.compile(r'(\d+ minutes )?\d+[.]\d\d\d seconds'), 'N.NNN seconds'),
        (re.compile(r'\d+[.]\d\d\d s'), 'N.NNN s'),
        (re.compile(r'\d+[.]\d\d\d{'), 'N.NNN{'),
        (re.compile(r'\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+'),
         'YYYY-MM-DD HH:MM:SS.mmmmmm'),
        (re.compile('( |")[^\n]+testrunner-ex'), r'\1testrunner-ex'),
        (re.compile('( |")[^\n]+testrunner.py'), r'\1testrunner.py'),
        (re.compile(r'> [^\n]*(doc|unit)test[.]py\(\d+\)'),
         r'\1test.py(NNN)'),
        (re.compile(r'[.]py\(\d+\)'), r'.py(NNN)'),
        (re.compile(r'[.]py:\d+'), r'.py:NNN'),
        (re.compile(r' line \d+,', re.IGNORECASE), r' Line NNN,'),
        (re.compile(r' line {([a-z]+)}\d+{', re.IGNORECASE), r' Line {\1}NNN{'),

        # omit traceback entries for unittest.py or doctest.py (and
        # their package variants) from output:
        (re.compile(r'^ +File "[^\n]*(doctest|unittest|case)(/__init__)?.py", [^\n]+\n[^\n]+\n',
                    re.MULTILINE),
         r''),
        (re.compile(r'^{\w+} +File "{\w+}[^\n]*(doctest|unittest|case)(/__init__)?.py{\w+}", [^\n]+\n[^\n]+\n',
                    re.MULTILINE),
         r''),
        #(re.compile('^> [^\n]+->None$', re.M), '> ...->None'),
        (re.compile('import pdb; pdb'), 'Pdb()'), # Py 2.3

        # Python 3 exceptions are from the builtins module
        (re.compile(r'builtins\.(SyntaxError|TypeError)'),
         r'exceptions.\1'),

        # Python 3.6 introduces ImportError subclasses
        (re.compile(r'ModuleNotFoundError:'), 'ImportError:'),

        # Python 3.3 has better exception messages
        (re.compile("ImportError: No module named '(?:[^']*[.])?([^'.]*)'"),
         r'ImportError: No module named \1'),

        # PyPy has different exception messages too
        (re.compile("ImportError: No module named (?:[a-zA-Z_0-9.]*[.])?([a-zA-Z_0-9]*)"),
         r'ImportError: No module named \1'),
        (re.compile("NameError: global name '([^']*)' is not defined"),
         r"NameError: name '\1' is not defined"),

        ])
else:
    #*nix
    checker = renormalizing.RENormalizing([
        # 2.5 changed the way pdb reports exceptions
        (re.compile(r"<class 'exceptions.(\w+)Error'>:"),
         r'exceptions.\1Error:'),

        #rewrite pdb prompt to ... the current location
        (re.compile('^> [^\n]+->None$', re.M), '> ...->None'),

        (re.compile(r"<module>"), (r'?')),
        (re.compile(r"<type 'exceptions.(\w+)Error'>:"),
         r'exceptions.\1Error:'),

        #this is a magic to put linefeeds into the doctest
        #on win it takes one step, linux is crazy about the same...
        (re.compile('##r##'), r'\r'),
        (re.compile(r'\r'), '\\\\r\n'),

        (re.compile(r'(\d+ minutes )?\d+[.]\d\d\d seconds'), 'N.NNN seconds'),
        (re.compile(r'\d+[.]\d\d\d s'), 'N.NNN s'),
        (re.compile(r'\d+[.]\d\d\d{'), 'N.NNN{'),
        (re.compile(r'\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+'),
         'YYYY-MM-DD HH:MM:SS.mmmmmm'),
        (re.compile('( |"|\')[^\'\n]+testrunner-ex'), r'\1testrunner-ex'),
        (re.compile('( |"|\')[^\'\n]+testrunner.py'), r'\1testrunner.py'),
        (re.compile(r'> [^\n]*(doc|unit)test[.]py\(\d+\)'),
         r'\1test.py(NNN)'),
        (re.compile(r'[.]py\(\d+\)'), r'.py(NNN)'),
        (re.compile(r'[.]py:\d+'), r'.py:NNN'),
        (re.compile(r' line \d+,', re.IGNORECASE), r' Line NNN,'),
        (re.compile(r' line {([a-z]+)}\d+{', re.IGNORECASE), r' Line {\1}NNN{'),

        # testtools content formatter is used to mime-encode
        # tracebacks when the SubunitOutputFormatter is used, and the
        # resulting text includes a size which can vary depending on
        # the path included in the traceback.
        (re.compile(r'traceback\n[A-F\d]+', re.MULTILINE),
         r'traceback\nNNN'),

        # omit traceback entries for unittest.py or doctest.py (and
        # their package variants) from output:
        (re.compile(r'^ +File "[^\n]*(doctest|unittest|case)(/__init__)?.py", [^\n]+\n[^\n]+\n',
                    re.MULTILINE),
         r''),
        (re.compile(r'^{\w+} +File "{\w+}[^\n]*(doctest|unittest|case)(/__init__)?.py{\w+}", [^\n]+\n[^\n]+\n',
                    re.MULTILINE),
         r''),
        (re.compile('import pdb; pdb'), 'Pdb()'), # Py 2.3

        # Python 3 exceptions are from the builtins module
        (re.compile(r'builtins\.(SyntaxError|TypeError)'),
         r'exceptions.\1'),

        # Python 3.6 introduces ImportError subclasses
        (re.compile(r'ModuleNotFoundError:'), 'ImportError:'),

        # Python 3.3 has better exception messages
        (re.compile("ImportError: No module named '(?:[^']*[.])?([^'.]*)'"),
         r'ImportError: No module named \1'),

        # PyPy has different exception messages too
        (re.compile("ImportError: No module named (?:[a-zA-Z_0-9.]*[.])?([a-zA-Z_0-9]*)"),
         r'ImportError: No module named \1'),
        (re.compile("NameError: global name '([^']*)' is not defined"),
         r"NameError: name '\1' is not defined"),

        ])


# On Python 3, monkey-patch doctest with our own _SpoofOut replacement.  We
# need sys.stdout to be binary-capable so that we can pass through binary
# output from test formatters cleanly, which is in particular required for
# subunit.  We don't expect to be able to do actual binary comparisons in
# doctests, but that's OK.
# See https://github.com/zopefoundation/zope.testrunner/pull/23 for the
# background.
if sys.version_info[0] >= 3:
    import io

    class _SpoofOut(io.TextIOWrapper):
        def __init__(self):
            super(_SpoofOut, self).__init__(io.BytesIO(), encoding='utf-8')

        def write(self, s):
            super(_SpoofOut, self).write(s)
            # Always flush immediately so that getvalue() never returns
            # short results.
            self.flush()

        def getvalue(self):
            result = self.buffer.getvalue().decode('utf-8', 'replace')
            # If anything at all was written, make sure there's a trailing
            # newline.  There's no way for the expected output to indicate
            # that a trailing newline is missing.
            if result and not result.endswith("\n"):
                result += "\n"
            # We're reading bytes, so we have to do universal newlines
            # conversion by hand.
            return result.replace(os.linesep, '\n')

        def truncate(self, size=None):
            self.seek(size)
            super(_SpoofOut, self).truncate()


def setUp(test):
    test.globs['print_function'] = print_function
    test.globs['saved-sys-info'] = (
        sys.path[:],
        sys.argv[:],
        sys.modules.copy(),
    )
    if hasattr(gc, 'get_threshold'):
        test.globs['saved-gc-threshold'] = gc.get_threshold()
    if sys.version_info[0] >= 3:
        test.globs['saved-doctest-SpoofOut'] = doctest._SpoofOut
        doctest._SpoofOut = _SpoofOut
    test.globs['this_directory'] = os.path.split(__file__)[0]
    test.globs['testrunner_script'] = sys.argv[0]


def tearDown(test):
    sys.path[:], sys.argv[:] = test.globs['saved-sys-info'][:2]
    if hasattr(gc, 'get_threshold'):
        gc.set_threshold(*test.globs['saved-gc-threshold'])
    sys.modules.clear()
    sys.modules.update(test.globs['saved-sys-info'][2])
    if sys.version_info[0] >= 3:
        doctest._SpoofOut = test.globs['saved-doctest-SpoofOut']


def test_suite():
    optionflags = (doctest.ELLIPSIS |
                   doctest.NORMALIZE_WHITESPACE |
                   doctest.REPORT_NDIFF)
    suites = [
        doctest.DocFileSuite(
            'testrunner-arguments.rst',
            'testrunner-coverage.rst',
            'testrunner-debugging-layer-setup.rst',
            'testrunner-debugging-import-failure.rst',
            'testrunner-debugging-nonprintable-exc.rst',
            'testrunner-debugging.rst',
            'testrunner-edge-cases.rst',
            'testrunner-errors.rst',
            'testrunner-layers-api.rst',
            'testrunner-layers-instances.rst',
            'testrunner-layers-buff.rst',
            'testrunner-subprocess-errors.rst',
            'testrunner-layers-cantfind.rst',
            'testrunner-layers-cwd.rst',
            'testrunner-layers-ntd.rst',
            'testrunner-layers-topological-sort.rst',
            'testrunner-layers.rst',
            'testrunner-progress.rst',
            'testrunner-colors.rst',
            'testrunner-simple.rst',
            'testrunner-nestedcode.rst',
            'testrunner-test-selection.rst',
            'testrunner-verbose.rst',
            'testrunner-repeat.rst',
            'testrunner-knit.rst',
            'testrunner-shuffle.rst',
            'testrunner-eggsupport.rst',
            'testrunner-stops-when-stop-on-error.rst',
            'testrunner-new-threads.rst',
            setUp=setUp, tearDown=tearDown,
            optionflags=optionflags,
            checker=checker),
        doctest.DocTestSuite('zope.testrunner'),
        doctest.DocTestSuite('zope.testrunner.coverage',
                             optionflags=optionflags),
        doctest.DocTestSuite('zope.testrunner.options'),
        doctest.DocTestSuite('zope.testrunner.find'),
    ]

    # PyPy uses a different garbage collector
    if hasattr(gc, 'get_threshold'):
        suites.append(
            doctest.DocFileSuite(
                'testrunner-gc.rst',
                setUp=setUp, tearDown=tearDown,
                optionflags=optionflags,
                checker=checker))

    # PyPy does not support sourceless imports, apparently (tried version 1.9)
    if 'PyPy' not in sys.version and not sys.dont_write_bytecode:
        suites.append(
            doctest.DocFileSuite(
                'testrunner-wo-source.rst',
                setUp=setUp, tearDown=tearDown,
                optionflags=optionflags,
                checker=checker))

    if sys.platform == 'win32':
        suites.append(
            doctest.DocFileSuite(
                'testrunner-coverage-win32.rst',
                setUp=setUp, tearDown=tearDown,
                optionflags=optionflags,
                checker=checker))

    suites.append(
        doctest.DocFileSuite(
            'testrunner-profiling.rst',
            setUp=setUp, tearDown=tearDown,
            optionflags=optionflags,
            checker=renormalizing.RENormalizing([
                (re.compile(r'tests_profile[.]\S*[.]prof'),
                 'tests_profile.*.prof'),
            ]),
        )
    )

    suites.append(
        doctest.DocFileSuite(
            'testrunner-profiling-cprofiler.rst',
            setUp=setUp, tearDown=tearDown,
            optionflags=optionflags,
            checker=renormalizing.RENormalizing([
                (re.compile(r'tests_profile[.]\S*[.]prof'),
                 'tests_profile.*.prof'),
            ]),
        )
    )

    suites.append(
        doctest.DocFileSuite(
            'testrunner-report-skipped.rst',
            setUp=setUp, tearDown=tearDown,
            optionflags=optionflags,
            checker=checker)
    )

    if hasattr(sys, 'gettotalrefcount'):
        suites.append(
            doctest.DocFileSuite(
                'testrunner-leaks.rst',
                setUp=setUp, tearDown=tearDown,
                optionflags=optionflags,
                checker=renormalizing.RENormalizing([
                    (re.compile(r'(\d+ minutes )?\d+[.]\d\d\d seconds'), 'N.NNN seconds'),
                    (re.compile(r'sys refcount=\d+ +change=\d+'),
                     'sys refcount=NNNNNN change=NN'),
                    (re.compile(r'sum detail refcount=\d+ +'),
                     'sum detail refcount=NNNNNN '),
                    (re.compile(r'total +\d+ +\d+'),
                     'total               NNNN    NNNN'),
                    (re.compile(r"^ +(int|type) +-?\d+ +-?\d+ *\n", re.M),
                     ''),
                ]),
            )
        )
    else:
        suites.append(
            doctest.DocFileSuite(
                'testrunner-leaks-err.rst',
                setUp=setUp, tearDown=tearDown,
                optionflags=optionflags,
                checker=checker,
            )
        )

    try:
        import subunit
        subunit
    except ImportError:
        suites.append(
            doctest.DocFileSuite(
                'testrunner-subunit-err.rst',
                setUp=setUp, tearDown=tearDown,
                optionflags=optionflags,
                checker=checker))
    else:
        suites.append(
            doctest.DocFileSuite(
                'testrunner-subunit.rst',
                'testrunner-subunit-v2.rst',
                setUp=setUp, tearDown=tearDown,
                optionflags=optionflags,
                checker=checker))
        if hasattr(sys, 'gettotalrefcount'):
            suites.append(
                doctest.DocFileSuite(
                    'testrunner-subunit-leaks.rst',
                    setUp=setUp, tearDown=tearDown,
                    optionflags=optionflags,
                    checker=checker))

    suites.append(doctest.DocFileSuite(
        'testrunner-unexpected-success.rst',
        setUp=setUp, tearDown=tearDown,
        optionflags=optionflags,
        checker=checker))

    return unittest.TestSuite(suites)
