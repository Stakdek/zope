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
"""Interfaces for the XMLRPC publisher.
"""

__docformat__ = "reStructuredText"

from zope.interface import Interface

from zope.publisher.interfaces import IPublication, IView
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest


class IXMLRPCPublisher(IPublishTraverse):
    """XML-RPC Publisher"""


class IXMLRPCPublication(IPublication):
    """Object publication framework."""

    def getDefaultTraversal(request, ob):
        """Get the default published object for the request

        Allows a default view to be added to traversal.
        Returns (ob, steps_reversed).
        """

class IXMLRPCRequest(IHTTPRequest):
    """XML-RPC Request
    """

class IXMLRPCView(IView):
    """XMLRPC View"""

class IXMLRPCPremarshaller(Interface):
    """Pre-Marshaller to remove proxies for xmlrpclib"""

    def __call__(self):
        """Return the given object without proxies."""
