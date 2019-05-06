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
"""Compatibility module for xmlrpclib

This module unifies namespace for xmlrpclib, that changed its name in
python-3.x (became xmlrpc.client).

The intention is to let xmlrpclib names to be importable from zcml.
"""
import sys
PYTHON2 = sys.version_info[0] == 2
PYTHON3 = sys.version_info[0] == 3

if PYTHON2:
    def _u(s, encoding='unicode_escape'):
        return unicode(s, encoding)
    from xmlrpclib import *
    import types
    CLASS_TYPES = (type, types.ClassType)
else:
    def _u(s, encoding=None):
        if encoding is None:
            return s
        return str(s, encoding)
    CLASS_TYPES = (type,)
    from xmlrpc.client import *
