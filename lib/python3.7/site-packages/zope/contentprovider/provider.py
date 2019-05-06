##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Simple base class for implementing content providers
"""
from zope.component import adapter
from zope.interface import Interface, implementer
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.contentprovider.interfaces import IContentProvider


@implementer(IContentProvider)
@adapter(Interface, IBrowserRequest, Interface)
class ContentProviderBase(BrowserView):
    """Base class for content providers"""

    def __init__(self, context, request, view):
        super(ContentProviderBase, self).__init__(context, request)
        self.__parent__ = view

    def update(self):
        pass

    def render(self, *args, **kwargs):
        raise NotImplementedError(
            '``render`` method must be implemented by subclass')
