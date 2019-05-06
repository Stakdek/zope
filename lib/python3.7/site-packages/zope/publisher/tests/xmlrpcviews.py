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
"""XML-RPC Views test objects
"""
from zope.interface import Interface, implementer
from zope.publisher.interfaces.xmlrpc import IXMLRPCPublisher

class IC(Interface): pass

@implementer(IXMLRPCPublisher)
class V1(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

class VZMI(V1):
    pass

@implementer(IXMLRPCPublisher)
class R1(object):
    def __init__(self, request):
        self.request = request


class RZMI(R1):
    pass
