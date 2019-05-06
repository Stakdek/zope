#! /usr/bin/env python
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
"""Driver program to run METAL and TAL regression tests:
compares interpeted test files with expected output files in a sibling
directory.
"""

from __future__ import print_function

import glob
import os
import sys
import traceback
import difflib
import copy
import optparse

try:
    # Python 2.x
    from cStringIO import StringIO
except ImportError:
    # Python 3.x
    from io import StringIO

import zope.tal.driver
import zope.tal.tests.utils

def showdiff(a, b, out):
    print(''.join(difflib.ndiff(a, b)), file=out)

def main(argv=None, out=sys.stdout):
    parser = optparse.OptionParser('usage: %prog [options] [testfile ...]',
                                   description=__doc__)
    parser.add_option('-q', '--quiet', action='store_true',
            help="less verbose output")
    internal_options = optparse.OptionGroup(parser, 'Internal options')
    internal_options.add_option('-Q', '--very-quiet',
            action='store_true', dest='unittesting',
            help="no output on success, only diff/traceback on failure")
    internal_options.add_option('-N', '--normalize-newlines',
            action='store_true', dest='normalize_newlines',
            help="ignore differences between CRLF and LF")
    parser.add_option_group(internal_options)
    driver_options = optparse.OptionGroup(parser, 'Driver options',
            "(for debugging only; supplying these *will* cause test failures)")
    for option in zope.tal.driver.OPTIONS:
        driver_options.add_option(option)
    parser.add_option_group(driver_options)
    opts, args = parser.parse_args(argv)

    if not args:
        here = os.path.dirname(__file__)
        prefix = os.path.join(here, "tests", "input", "test*.")
        if zope.tal.tests.utils.skipxml:
            xmlargs = []
        else:
            xmlargs = glob.glob(prefix + "xml")
            xmlargs.sort()
        htmlargs = glob.glob(prefix + "html")
        htmlargs.sort()
        args = xmlargs + htmlargs
        if not args:
            sys.stderr.write("No tests found -- please supply filenames\n")
            sys.exit(1)
    errors = 0
    for arg in args:
        locopts = []
        if "metal" in arg and not opts.macro_only:
            locopts.append("-m")
        if "_sa" in arg and not opts.annotate:
            locopts.append("-a")
        if not opts.unittesting:
            print(arg, end=' ', file=out)
            sys.stdout.flush()
        if zope.tal.tests.utils.skipxml and arg.endswith(".xml"):
            print("SKIPPED (XML parser not available)", file=out)
            continue
        save = sys.stdout, sys.argv
        try:
            try:
                sys.stdout = stdout = StringIO()
                sys.argv = ["driver.py"] + locopts + [arg]
                zope.tal.driver.main(copy.copy(opts))
            finally:
                sys.stdout, sys.argv = save
        except SystemExit:
            raise
        except:
            errors = 1
            if opts.quiet:
                print(sys.exc_info()[0].__name__, file=out)
                sys.stdout.flush()
            else:
                if opts.unittesting:
                    print('', file=out)
                else:
                    print("Failed:", file=out)
                    sys.stdout.flush()
                traceback.print_exc()
            continue
        head, tail = os.path.split(arg)
        outfile = os.path.join(
            head.replace("input", "output"),
            tail)
        try:
            f = open(outfile)
        except IOError:
            expected = None
            print("(missing file %s)" % outfile, end=' ', file=out)
        else:
            expected = f.readlines()
            f.close()
        stdout.seek(0)
        if hasattr(stdout, "readlines"):
            actual = stdout.readlines()
        else:
            actual = readlines(stdout)
        if opts.normalize_newlines or "_sa" in arg or arg.endswith('.xml'):
            # EOL normalization makes the tests pass:
            # - XML files, on Windows, have \r\n line endings.  Because
            #   expat insists on byte streams on Python 3, we end up with
            #   those \r\n's going through the entire TAL engine and
            #   showing up in the actual output.  Expected output, on the
            #   other hand, has just \n's, since we read the file as text.
            # - Source annotation tests: when a developer converts all the
            #   input and output files to \r\n line endings and runs
            #   tests on Linux (because they're trying to debug Windows
            #   problems but can't be forced to use an inferior OS), we
            #   also have \r\n's going through the TAL engine and showing
            #   up both in actual and expected lists.  Except for source
            #   annotation lines added by TAL, which always use just \n.
            actual = [l.replace('\r\n', '\n') for l in actual]
            if expected is not None:
                expected = [l.replace('\r\n', '\n') for l in expected]
        if actual == expected:
            if not opts.unittesting:
                print("OK", file=out)
        else:
            if opts.unittesting:
                print('', file=out)
            else:
                print("not OK", file=out)
            errors = 1
            if not opts.quiet and expected is not None:
                showdiff(expected, actual, out)
    if errors:
        if opts.unittesting:
            return 1
        else:
            sys.exit(1)

def readlines(f):
    L = []
    while 1:
        line = f.readline()
        if not line:
            break
        L.append(line)
    return L

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
