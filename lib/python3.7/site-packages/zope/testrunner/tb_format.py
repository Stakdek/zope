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
"""Set up testing environment
"""

import sys
import traceback
import zope.exceptions.exceptionformatter
import zope.testrunner.feature


try:
    _iter_chain = traceback._iter_chain
except AttributeError:
    # Python 3.5
    def _iter_chain(exc, custom_tb=None, seen=None):
        if seen is None:
            seen = set()
        seen.add(exc)
        its = []
        context = exc.__context__
        cause = exc.__cause__
        if cause is not None and cause not in seen:
            its.append(_iter_chain(cause, False, seen))
            its.append([(traceback._cause_message, None)])
        elif (context is not None and
              not exc.__suppress_context__ and
              context not in seen):
            its.append(_iter_chain(context, None, seen))
            its.append([(traceback._context_message, None)])
        its.append([(exc, custom_tb or exc.__traceback__)])
        # itertools.chain is in an extension module and may be unavailable
        for it in its:
            for x in it:
                yield x


def format_exception(t, v, tb, limit=None, chain=None):
    if chain:
        values = _iter_chain(v, tb)
    else:
        values = [(v, tb)]
    fmt = zope.exceptions.exceptionformatter.TextExceptionFormatter(
        limit=None, with_filenames=True)
    for v, tb in values:
        if isinstance(v, str):
            return v
        return fmt.formatException(t, v, tb)


def print_exception(t, v, tb, limit=None, file=None, chain=None):
    if chain:
        values = _iter_chain(v, tb)
    else:
        values = [(v, tb)]
    if file is None:
        file = sys.stdout
    for v, tb in values:
        file.writelines(format_exception(t, v, tb, limit))


class Traceback(zope.testrunner.feature.Feature):

    active = True

    def global_setup(self):
        self.old_format = traceback.format_exception
        traceback.format_exception = format_exception

        self.old_print = traceback.print_exception
        traceback.print_exception = print_exception

    def global_teardown(self):
        traceback.format_exception = self.old_format
        traceback.print_exception = self.old_print
