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
"""Debug functions

"""
from __future__ import print_function

import doctest
import io
import pdb
import sys
import threading
import traceback

try:
    import ipdb
    _ipdb_state = threading.local()
except ImportError:
    ipdb = None

import zope.testrunner.interfaces


def _use_ipdb():
    """Check whether ipdb is usable."""
    global _ipdb_ok
    if ipdb is None:
        return False
    if getattr(_ipdb_state, 'ok', None) is None:
        _ipdb_state.ok = False
        if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
            try:
                sys.stdin.fileno()
            except (AttributeError, io.UnsupportedOperation):
                pass
            else:
                _ipdb_state.ok = True
    return _ipdb_state.ok


def post_mortem(exc_info):
    err = exc_info[1]
    if isinstance(err, (doctest.UnexpectedException, doctest.DocTestFailure)):

        if isinstance(err, doctest.UnexpectedException):
            exc_info = err.exc_info

            # Print out location info if the error was in a doctest
            if exc_info[2].tb_frame.f_code.co_filename == '<string>':
                print_doctest_location(err)

        else:
            print_doctest_location(err)
            # Hm, we have a DocTestFailure exception.  We need to
            # generate our own traceback
            try:
                exec(('raise ValueError'
                      '("Expected and actual output are different")'
                      ), err.test.globs)
            except:
                exc_info = sys.exc_info()

    print(''.join(traceback.format_exception_only(exc_info[0], exc_info[1])))
    if _use_ipdb():
        ipdb.post_mortem(exc_info[2])
    else:
        pdb.post_mortem(exc_info[2])
    raise zope.testrunner.interfaces.EndRun()


def print_doctest_location(err):
    # This mimics pdb's output, which gives way cool results in emacs :)
    filename = err.test.filename
    if filename.endswith('.pyc'):
        filename = filename[:-1]
    print("> %s(%s)_()" % (filename, err.test.lineno+err.example.lineno+1))
