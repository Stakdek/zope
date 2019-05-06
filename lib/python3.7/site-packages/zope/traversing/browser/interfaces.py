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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Browser traversal interfaces
"""
from zope.interface import Interface


class IAbsoluteURL(Interface):
    """
    An absolute URL.

    These are typically registered as adapters or multi-adapters
    for objects.
    """

    def __unicode__():
        """Returns the URL as a unicode string."""

    def __str__():
        """Returns an ASCII string with all unicode characters url quoted."""

    def __repr__():
        """Get a string representation """

    def __call__():
        """Returns an ASCII string with all unicode characters url quoted."""

    def breadcrumbs():
        """Returns a tuple like ({'name':name, 'url':url}, ...)

        Name is the name to display for that segment of the breadcrumbs.
        URL is the link for that segment of the breadcrumbs.
        """


class IAbsoluteURLAPI(Interface):
    """
    The API to compute absolute URLs of objects.

    Provided by :mod:`zope.traversing.browser.absoluteurl`
    """

    def absoluteURL(ob, request):
        """
        Compute the absolute URL of an object.

        This should return an ASCII string by looking up an adapter
        from `(ob, request)` to :class:`IAbsoluteURL` and then calling it.
        """
