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
"""Command-line option parsing
"""
from __future__ import print_function

import argparse
import re
import os
import sys

import pkg_resources

from zope.testrunner.formatter import (
    ColorfulOutputFormatter,
    OutputFormatter,
    SubunitOutputFormatter,
    SubunitV2OutputFormatter,
)
from zope.testrunner.formatter import terminal_has_colors
from zope.testrunner.profiling import available_profilers

def _regex_search(s):
    return re.compile(s).search

parser = argparse.ArgumentParser(
    description="Discover and run unittest tests")


parser.add_argument("legacy_module_filter", nargs="?",
                    help="DEPRECATED: Prefer to use --module.")


parser.add_argument("legacy_test_filter", nargs="?",
                    help="DEPRECATED: Prefer to use --test.")

######################################################################
# Searching and filtering

searching = parser.add_argument_group("Searching and filtering", """\
Options in this group are used to define which tests to run.
""")

searching.add_argument(
    '--package', '--dir', '-s', action="append", dest='package',
    help="""\
Search the given package's directories for tests.  This can be
specified more than once to run tests in multiple parts of the source
tree.  For example, if refactoring interfaces, you don't want to see
the way you have broken setups for tests in other packages. You *just*
want to run the interface tests.

Packages are supplied as dotted names.  For compatibility with the old
test runner, forward and backward slashed in package names are
converted to dots.

(In the special case of packages spread over multiple directories,
only directories within the test search path are searched. See the
--path option.)

""")

searching.add_argument(
    '--module', '-m', action="append", dest='module',
    help="""\
Specify a test-module filter as a regular expression.  This is a
case-sensitive regular expression, used in search (not match) mode, to
limit which test modules are searched for tests.  The regular
expressions are checked against dotted module names.  In an extension
of Python regexp notation, a leading "!" is stripped and causes the
sense of the remaining regexp to be negated (so "!bc" matches any
string that does not match "bc", and vice versa).  The option can be
specified multiple test-module filters.  Test modules matching any of
the test filters are searched.  If no test-module filter is specified,
then all test modules are used.
""")

searching.add_argument(
    '--test', '-t', action="append", dest='test',
    help="""\
Specify a test filter as a regular expression.  This is a
case-sensitive regular expression, used in search (not match) mode, to
limit which tests are run.  In an extension of Python regexp notation,
a leading "!" is stripped and causes the sense of the remaining regexp
to be negated (so "!bc" matches any string that does not match "bc",
and vice versa).  The option can be specified multiple test filters.
Tests matching any of the test filters are included.  If no test
filter is specified, then all tests are run.
""")

searching.add_argument(
    '--unit', '-u', action="store_true", dest='unit',
    help="""\
Run only unit tests, ignoring any layer options.
""")

searching.add_argument(
    '--non-unit', '-f', action="store_true", dest='non_unit',
    help="""\
Run tests other than unit tests.
""")

searching.add_argument(
    '--layer', action="append", dest='layer',
    help="""\
Specify a test layer to run.  The option can be given multiple times
to specify more than one layer.  If not specified, all layers are run.
It is common for the running script to provide default values for this
option.  Layers are specified regular expressions, used in search
mode, for dotted names of objects that define a layer.  In an
extension of Python regexp notation, a leading "!" is stripped and
causes the sense of the remaining regexp to be negated (so "!bc"
matches any string that does not match "bc", and vice versa).  The
layer named 'zope.testrunner.layer.UnitTests' is reserved for
unit tests, however, take note of the --unit and non-unit options.
""")

searching.add_argument(
    '-a', '--at-level', type=int, dest='at_level',
    default=1,
    help="""\
Run the tests at the given level.  Any test at a level at or below
this is run, any test at a level above this is not run.  Level 0
runs all tests.
""")

searching.add_argument(
    '--all', action="store_true", dest='all',
    help="Run tests at all levels.")

searching.add_argument(
    '--list-tests', action="store_true", dest='list_tests',
    default=False,
    help="List all tests that matched your filters.  Do not run any tests.")

searching.add_argument(
    '--require-unique', action="store_true", dest='require_unique_ids',
    default=False,
    help="""\
Require that all test IDs be unique and raise an error if duplicates are
encountered.
""")


######################################################################
# Reporting

reporting = parser.add_argument_group("Reporting", """\
Reporting options control basic aspects of test-runner output
""")

reporting.add_argument(
    '--verbose', '-v', action="count", dest='verbose',
    default=0,
    help="""\
Make output more verbose.
Increment the verbosity level.
""")

reporting.add_argument(
    '--quiet', '-q', action="store_true", dest='quiet',
    help="""\
Make the output minimal, overriding any verbosity options.
""")

reporting.add_argument(
    '--progress', '-p', action="store_true", dest='progress',
    help="""\
Output progress status
""")

reporting.add_argument(
    '--no-progress', action="store_false", dest='progress',
    help="""\
Do not output progress status.  This is the default, but can be used to
counter a previous use of --progress or -p.
""")

# The actual processing will be done in the get_options function, but
# we want argparse to generate appropriate help info for us, so we add
# an option anyway.
reporting.add_argument(
    '--auto-progress', action="store_const", const=None,
    help="""\
Output progress status, but only when stdout is a terminal.
""")

reporting.add_argument(
    '--color', '-c', action="store_true", dest='color',
    help="""\
Colorize the output.
""")

reporting.add_argument(
    '--no-color', '-C', action="store_false", dest='color',
    help="""\
Do not colorize the output.  This is the default, but can be used to
counter a previous use of --color or -c.
""")

# The actual processing will be done in the get_options function, but
# we want argparse to generate appropriate help info for us, so we add
# an option anyway.
reporting.add_argument(
    '--auto-color', action="store_const", const=None,
    help="""\
Colorize the output, but only when stdout is a terminal.
""")

reporting.add_argument(
    '--subunit', action="store_true", dest='subunit',
    help="""\
Use subunit v1 output.  Will not be colorized.
""")

reporting.add_argument(
    '--subunit-v2', action="store_true", dest='subunit_v2',
    help="""\
Use subunit v2 output.  Will not be colorized.
""")

reporting.add_argument(
    '--slow-test', type=float, dest='slow_test_threshold', metavar='N',
    default=10,
    help="""\
With -c and -vvv, highlight tests that take longer than N seconds (default:
%(default)s).
""")

reporting.add_argument(
    '-1', '--hide-secondary-failures',
    action="store_true", dest='report_only_first_failure',
    help="""\
Report only the first failure in a doctest. (Examples after the
failure are still executed, in case they do any cleanup.)
""")

reporting.add_argument(
    '--show-secondary-failures',
    action="store_false", dest='report_only_first_failure',
    help="""\
Report all failures in a doctest.  This is the default, but can
be used to counter a default use of -1 or --hide-secondary-failures.
""")

reporting.add_argument(
    '--ndiff', action="store_true", dest="ndiff",
    help="""\
When there is a doctest failure, show it as a diff using the ndiff.py utility.
""")

reporting.add_argument(
    '--udiff', action="store_true", dest="udiff",
    help="""\
When there is a doctest failure, show it as a unified diff.
""")

reporting.add_argument(
    '--cdiff', action="store_true", dest="cdiff",
    help="""\
When there is a doctest failure, show it as a context diff.
""")

reporting.add_argument(
    '--ignore-new-thread',
    metavar='REGEXP',
    action="append",
    default=[],
    dest='ignore_new_threads',
    help="""\
If a thread with this name is left behind, don't report this at the end.
This is a case-sensitive regular expression, used in match mode.
This option can be used multiple times. If a thread name matches any of them,
it will be ignored.
""")


######################################################################
# Analysis

analysis = parser.add_argument_group("Analysis", """\
Analysis options provide tools for analysing test output.
""")


analysis.add_argument(
    '--stop-on-error', '--stop', '-x', action="store_true",
    dest='stop_on_error',
    help="Stop running tests after first test failure or error."
    )

analysis.add_argument(
    '--post-mortem', '--pdb', '-D', action="store_true", dest='post_mortem',
    help="Enable post-mortem debugging of test failures"
    )


analysis.add_argument(
    '--gc', '-g', action="append", dest='gc', type=int,
    help="""\
Set the garbage collector generation threshold.  This can be used
to stress memory and gc correctness.  Some crashes are only
reproducible when the threshold is set to 1 (aggressive garbage
collection).  Do "--gc 0" to disable garbage collection altogether.

The --gc option can be used up to 3 times to specify up to 3 of the 3
Python gc_threshold settings.

""")

analysis.add_argument(
    '--gc-option', '-G', action="append", dest='gc_option',
    choices={'DEBUG_STATS', 'DEBUG_COLLECTABLE', 'DEBUG_UNCOLLECTABLE',
             'DEBUG_INSTANCES', 'DEBUG_OBJECTS', 'DEBUG_SAVEALL',
             'DEBUG_LEAK'},
    help="""\
Set a Python gc-module debug flag.  This option can be used more than
once to set multiple flags.
""")

analysis.add_argument(
    '--repeat', '-N', action="store", type=int, dest='repeat',
    default=1,
    help="""\
Repeat the tests the given number of times.  This option is used to
make sure that tests leave their environment in the state they found
it and, with the --report-refcounts option to look for memory leaks.
""")

analysis.add_argument(
    '--report-refcounts', '-r', action="store_true", dest='report_refcounts',
    help="""\
After each run of the tests, output a report summarizing changes in
refcounts by object type.  This option that requires that Python was
built with the --with-pydebug option to configure.
""")

analysis.add_argument(
    '--coverage', action="store", dest='coverage',
    help="""\
Perform code-coverage analysis, saving trace data to the directory
with the given name.  A code coverage summary is printed to standard
out.
""")

analysis.add_argument(
    '--profile', action="store", dest='profile',
    choices=set(available_profilers),
    help="""\
Run the tests under cProfiler and display the top 50 stats, sorted
by cumulative time and number of calls.
""")
analysis.add_argument(
    '--profile-directory', action="store", dest='prof_dir', default='.',
    help="""\
Directory for temporary profiler files.  All files named tests_profile.*.prof
in this directory will be removed.  If you intend to run multiple instances
of the test runner in parallel, be sure to tell them to use different
directories, so they won't step on each other's toes.
""")

######################################################################
# Setup

setup = parser.add_argument_group("Setup", """\
Setup options are normally supplied by the testrunner script, although
they can be overridden by users.
""")

setup.add_argument(
    '--path', action="append", dest='path',
    type=os.path.abspath,
    help="""\
Specify a path to be added to Python's search path.  This option can
be used multiple times to specify multiple search paths.  The path is
usually specified by the test-runner script itself, rather than by
users of the script, although it can be overridden by users.  Only
tests found in the path will be run.

This option also specifies directories to be searched for tests.
See the search_directory.
""")

setup.add_argument(
    '--test-path', action="append", dest='test_path',
    type=os.path.abspath,
    help="""\
Specify a path to be searched for tests, but not added to the Python
search path.  This option can be used multiple times to specify
multiple search paths.  The path is usually specified by the
test-runner script itself, rather than by users of the script,
although it can be overridden by users.  Only tests found in the path
will be run.
""")

setup.add_argument(
    '--package-path', action="append", dest='package_path', nargs=2,
    help="""\
Specify a path to be searched for tests, but not added to the Python
search path.  Also specify a package for files found in this path.
This is used to deal with directories that are stitched into packages
that are not otherwise searched for tests.

This option takes 2 arguments.  The first is a path name. The second is
the package name.

This option can be used multiple times to specify
multiple search paths.  The path is usually specified by the
test-runner script itself, rather than by users of the script,
although it can be overridden by users.  Only tests found in the path
will be run.
""")

setup.add_argument(
    '--tests-pattern', action="store", dest='tests_pattern',
    default=_regex_search('^tests$'),
    type=_regex_search,
    help="""\
The test runner looks for modules containing tests.  It uses this
pattern to identify these modules.  The modules may be either packages
or python files.

If a test module is a package, it uses the value given by the
test-file-pattern to identify python files within the package
containing tests.
""")

setup.add_argument(
    '--suite-name', action="store", dest='suite_name',
    default='test_suite',
    help="""\
Specify the name of the object in each test_module that contains the
module's test suite.
""")

setup.add_argument(
    '--test-file-pattern', action="store", dest='test_file_pattern',
    default=_regex_search('^test'),
    type=_regex_search,
    help="""\
Specify a pattern for identifying python files within a tests package.
See the documentation for the --tests-pattern option.
""")

setup.add_argument(
    '--ignore_dir', action="append", dest='ignore_dir',
    default=['.git', '.svn', 'CVS', '{arch}', '.arch-ids', '_darcs'],
    help="""\
Specifies the name of a directory to ignore when looking for tests.
""")

setup.add_argument(
    '--shuffle', action="store_true", dest='shuffle',
    help="""\
Shuffles the order in which tests are ran.
""")

setup.add_argument(
    '--shuffle-seed', action="store", dest='shuffle_seed', type=int,
    help="""\
Value used to initialize the tests shuffler. Specify a value to create
repeatable random ordered tests.
""")


######################################################################
# Other

other = parser.add_argument_group("Other", "Other options")

other.add_argument(
    '--version', action="store_true", dest='showversion',
    help="Print the version of the testrunner, and exit.")

other.add_argument(
    '-j', action="store", type=int, dest='processes',
    default=1,
    help="""\
Use up to given number of parallel processes to execute tests.  May decrease
test run time substantially.  Defaults to %(default)s.
""")

other.add_argument(
    '--keepbytecode', '-k', action="store_true", dest='keepbytecode',
    help="""\
Normally, the test runner scans the test paths and the test
directories looking for and deleting pyc or pyo files without
corresponding py files.  This is to prevent spurious test failures due
to finding compiled modules where source modules have been deleted.
This scan can be time consuming.  Using this option disables this
scan.  If you know you haven't removed any modules since last running
the tests, can make the test run go much faster.
""")

other.add_argument(
    '--usecompiled', action="store_true", dest='usecompiled',
    help="""\
Normally, a package must contain an __init__.py file, and only .py files
can contain test code.  When this option is specified, compiled Python
files (.pyc and .pyo) can be used instead:  a directory containing
__init__.pyc or __init__.pyo is also considered to be a package, and if
file XYZ.py contains tests but is absent while XYZ.pyc or XYZ.pyo exists
then the compiled files will be used.  This is necessary when running
tests against a tree where the .py files have been removed after
compilation to .pyc/.pyo.  Use of this option implies --keepbytecode.
""")

other.add_argument(
    '--exit-with-status', action="store_true", dest='exitwithstatus',
    help="""DEPRECATED: The test runner will always exit with a status.\
""")


######################################################################
# Command-line processing


def merge_options(options, defaults):
    odict = options.__dict__
    for name, value in defaults.__dict__.items():
        if (value is not None) and (odict[name] is None):
            odict[name] = value

def get_options(args=None, defaults=None):
    # Because we want to inspect stdout and decide to colorize or not, we
    # replace the --auto-color option with the appropriate --color or
    # --no-color option.  That way the subprocess doesn't have to decide (which
    # it would do incorrectly anyway because stdout would be a pipe).
    def apply_auto_color(args):
        if args and '--auto-color' in args:
            if sys.stdout.isatty() and terminal_has_colors():
                colorization = '--color'
            else:
                colorization = '--no-color'

            args[:] = [arg.replace('--auto-color', colorization)
                       for arg in args]

    # The comment of apply_auto_color applies here as well
    def apply_auto_progress(args):
        if args and '--auto-progress' in args:
            if sys.stdout.isatty():
                progress = '--progress'
            else:
                progress = '--no-progress'

            args[:] = [arg.replace('--auto-progress', progress)
                       for arg in args]

    apply_auto_color(args)
    apply_auto_color(defaults)
    apply_auto_progress(args)
    apply_auto_progress(defaults)

    if defaults:
        defaults = parser.parse_args(defaults)
    else:
        defaults = None

    if args is None:
        args = sys.argv

    options = parser.parse_args(args[1:], defaults)
    options.original_testrunner_args = args

    if options.showversion:
        dist = pkg_resources.require('zope.testrunner')[0]
        print('zope.testrunner version %s' % dist.version)
        options.fail = True
        return options

    if options.subunit or options.subunit_v2:
        try:
            import subunit
            subunit
        except ImportError:
            print("""\
        Subunit is not installed. Please install Subunit
        to generate subunit output.
        """)
            options.fail = True
            return options

    if options.subunit and options.subunit_v2:
        print("""\
        You may only use one of --subunit and --subunit-v2.
        """)
        options.fail = True
        return options

    if options.subunit:
        options.output = SubunitOutputFormatter(options)
    elif options.subunit_v2:
        options.output = SubunitV2OutputFormatter(options)
    elif options.color:
        options.output = ColorfulOutputFormatter(options)
        options.output.slow_test_threshold = options.slow_test_threshold
    else:
        options.output = OutputFormatter(options)

    options.fail = False

    if options.legacy_module_filter:
        module_filter = options.legacy_module_filter
        if module_filter != '.':
            if options.module:
                options.module.append(module_filter)
            else:
                options.module = [module_filter]

        if options.legacy_test_filter:
            test_filter = options.legacy_test_filter
            if options.test:
                options.test.append(test_filter)
            else:
                options.test = [test_filter]

    options.ignore_dir = set(options.ignore_dir)
    options.test = options.test or ['.']
    options.module = options.module or ['.']

    options.path = options.path or []
    options.test_path = options.test_path or []
    options.test_path += options.path

    options.test_path = ([(path, '') for path in options.test_path]
                         +
                         [(os.path.abspath(path), package)
                          for (path, package) in options.package_path or ()
                         ])

    if options.package:
        pkgmap = dict(options.test_path)
        options.package = [normalize_package(p, pkgmap)
                           for p in options.package]

    options.prefix = [(path + os.path.sep, package)
                      for (path, package) in options.test_path]

    # Sort prefixes so that longest prefixes come first.
    # That is because only first match is evaluated which
    # can be a problem with nested source packages.
    options.prefix.sort(key=lambda p: len(p[0]), reverse=True)

    if options.all:
        options.at_level = sys.maxsize

    if options.unit and options.non_unit:
        # The test runner interprets this as "run only those tests that are
        # both unit and non-unit at the same time".  The user, however, wants
        # to run both unit and non-unit tests.  Disable the filtering so that
        # the user will get what she wants:
        options.unit = options.non_unit = False

    if options.unit:
        # XXX Argh.
        options.layer = ['zope.testrunner.layer.UnitTests']

    options.layer = options.layer and {l: 1 for l in options.layer}

    if options.usecompiled:
        options.keepbytecode = options.usecompiled

    if options.quiet:
        options.verbose = 0

    if options.report_refcounts and options.repeat < 2:
        print("""\
        You must use the --repeat (-N) option to specify a repeat
        count greater than 1 when using the --report_refcounts (-r)
        option.
        """)
        options.fail = True
        return options


    if options.report_refcounts and not hasattr(sys, "gettotalrefcount"):
        print("""\
        The Python you are running was not configured
        with --with-pydebug. This is required to use
        the --report-refcounts option.
        """)
        options.fail = True
        return options

    if options.module and options.require_unique_ids:
        # We warn if --module and --require-unique are specified at the same
        # time, though we don't exit.
        print("""\
        You specified a module along with --require-unique;
        --require-unique will not try to enforce test ID uniqueness when
        working with a specific module.
        """)

    return options

def normalize_package(package, package_map=None):
    r"""Normalize package name passed to the --package option.

        >>> normalize_package('zope.testrunner')
        'zope.testrunner'

    Converts path names into package names for compatibility with the old
    test runner.

        >>> normalize_package('zope/testrunner')
        'zope.testrunner'
        >>> normalize_package('zope/testrunner/')
        'zope.testrunner'
        >>> normalize_package('zope\\testrunner')
        'zope.testrunner'

    Can use a map of absolute pathnames to package names

        >>> a = os.path.abspath
        >>> normalize_package('src/zope/testrunner/',
        ...                   {a('src'): ''})
        'zope.testrunner'
        >>> normalize_package('src/zope_testrunner/',
        ...                   {a('src/zope_testrunner'): 'zope.testrunner'})
        'zope.testrunner'
        >>> normalize_package('src/zope_something/tests',
        ...                   {a('src/zope_something'): 'zope.something',
        ...                    a('src'): ''})
        'zope.something.tests'

    """
    package_map = {} if package_map is None else package_map
    package = package.replace('\\', '/')
    if package.endswith('/'):
        package = package[:-1]
    bits = package.split('/')
    for n in range(len(bits), 0, -1):
        pkg = package_map.get(os.path.abspath('/'.join(bits[:n])))
        if pkg is not None:
            bits = bits[n:]
            if pkg:
                bits = [pkg] + bits
            return '.'.join(bits)
    return package.replace('/', '.')
