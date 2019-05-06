##############################################################################
#
# Copyright (c) 2004-2013 Zope Foundation and Contributors.
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
"""Test runner
"""

import os
import sys


def run(defaults=None, args=None, script_parts=None, cwd=None, warnings=None):
    """Main runner function which can be and is being used from main programs.

    Will execute the tests and exit the process according to the test result.

    .. versionchanged:: 4.8.0
       Add the *warnings* keyword argument. See :class:`zope.testrunner.runner.Runner`

    """
    failed = run_internal(defaults, args, script_parts=script_parts, cwd=cwd,
                          warnings=warnings)
    sys.exit(int(failed))


def run_internal(defaults=None, args=None, script_parts=None, cwd=None, warnings=None):
    """Execute tests.

    Returns whether errors or failures occured during testing.

    .. versionchanged:: 4.8.0
       Add the *warnings* keyword argument. See :class:`zope.testrunner.runner.Runner`

    """
    if script_parts is None:
        script_parts = _script_parts(args)
    if cwd is None:
        cwd = os.getcwd()
    # XXX Bah. Lazy import to avoid circular/early import problems
    from zope.testrunner.runner import Runner
    runner = Runner(defaults, args, script_parts=script_parts, cwd=cwd, warnings=warnings)
    runner.run()
    return runner.failed


def _script_parts(args=None):
    script_parts = (args or sys.argv)[0:1]
    # If we are running via setup.py, then we'll have to run the
    # sub-process differently.
    if script_parts[0] == 'setup.py':
        script_parts = ['-c', 'from zope.testrunner import run; run()']
    else:
        # make sure we remember the absolute path early -- the tests might
        # do an os.chdir()
        script_parts[0] = os.path.abspath(script_parts[0])
    return script_parts


if __name__ == '__main__':
    # this used to allow people to try out the test runner with
    #   python -m zope.testrunner --test-path .
    # on Python 2.5.  This broke on 2.6, and 2.7 and newer use __main__.py
    # for that.  But there are some users out there who actually use
    #   python -e zope.testrunner.__init__ --test-path .
    # so let's keep this for BBB
    run()
