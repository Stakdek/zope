##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Adapter:

Adapts zope.security.interfaces.IPrincipal to
zope.publisher.interfaces.logginginfo.ILoggingInfo.
"""
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.logginginfo import ILoggingInfo
from zope.security.interfaces import IPrincipal


@adapter(IPrincipal)
@implementer(ILoggingInfo)
class PrincipalLogging(object):
    """Adapts zope.security.interfaces.IPrincipal to
    zope.publisher.interfaces.logginginfo.ILoggingInfo."""

    def __init__(self, principal):
        self.principal = principal

    def getLogMessage(self):
        pid = self.principal.id
        return pid.encode('ascii', 'backslashreplace')
