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
# Stock __traceback_supplement__ implementations

try:
    from html import escape
except ImportError:  # PY2
    from cgi import escape


class PathTracebackSupplement(object):
    """Implementation of ITracebackSupplement"""
    pp = None

    def __init__(self, object):
        self.object = object
        if hasattr(object, 'getPhysicalPath'):
            self.pp = '/'.join(object.getPhysicalPath())
        if hasattr(object, 'absolute_url'):
            self.source_url = '%s/manage_main' % object.absolute_url()

    def getInfo(self, as_html=0):
        if self.pp is None:
            return
        if as_html:
            return '<b>Physical Path:</b>%s' % (escape(self.pp))
        else:
            return '   - Physical Path: %s' % self.pp
