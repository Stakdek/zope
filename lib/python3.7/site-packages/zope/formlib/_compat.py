##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Compatibility between Python versions
"""
import base64
import sys

PY3 = sys.version_info[0] >= 3

if PY3:

    from io import StringIO
    unicode = str
    imap = map
    basestring = str

    def toUnicode(obj):
        return obj.decode() if isinstance(obj, bytes) else str(obj)

    def safeBase64Encode(obj):
        return base64.b64encode(
            obj.encode()).strip().replace(b'=', b'_').decode()

else:

    from StringIO import StringIO
    from itertools import imap
    unicode = unicode
    basestring = basestring

    def toUnicode(obj):
        if isinstance(obj, bytes):
            return unicode(obj, 'utf-8')
        else:
            return unicode(obj)

    def safeBase64Encode(obj):
        return base64.b64encode(toUnicode(obj)).strip().replace('=', '_')
