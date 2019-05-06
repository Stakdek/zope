##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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

PY3 = sys.version_info[0] >= 3

if PY3: # pragma: no cover

    import builtins

    string_types = (str,)
    text_type = str

    # borrowed from 'six'
    def reraise(tp, value, tb=None):
        if value is None:
            value = tp
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

else: # pragma: no cover

    import __builtin__  as builtins

    text_type = unicode
    string_types = (basestring,)

    # borrowed from 'six'
    exec("""\
def reraise(tp, value, tb=None):
    raise tp, value, tb
""")
