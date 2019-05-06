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
"""Browser Interfaces
"""

__docformat__ = "reStructuredText"

from zope.interface import Attribute
from zope.interface import alsoProvides
from zope.browser.interfaces import IBrowserView # BBB import

from zope.publisher.interfaces import IPublication
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import ISkinType
from zope.publisher.interfaces import ISkinnable
from zope.publisher.interfaces.http import IHTTPApplicationRequest
from zope.publisher.interfaces.http import IHTTPRequest

# BBB moved to zope.publisher.interfaces since not only browser reuquest
# can use the skin pattern
from zope.publisher.interfaces import IDefaultSkin # BBB import
from zope.publisher.interfaces import ISkinChangedEvent # BBB import


class IBrowserApplicationRequest(IHTTPApplicationRequest):
    """Browser-specific requests
    """

    def __getitem__(key):
        """Return Browser request data

        Request data are retrieved from one of:

        - Environment variables

          These variables include input headers, server data, and other
          request-related data.  The variable names are as
          specified
          in the `CGI specification <https://tools.ietf.org/html/rfc3875>`_.

        - Cookies

          These are the cookie data, if present.

        - Form data

        Form data are searched before cookies, which are searched
        before environmental data.
        """

    form = Attribute(
        """Form data

        This is a read-only mapping from name to form value for the name.
        """)


class IBrowserPublication(IPublication):
    """Object publication framework.
    """

    def getDefaultTraversal(request, ob):
        """Get the default published object for the request

        Allows a default view to be added to traversal.
        Returns (ob, steps_reversed).
        """


class IBrowserRequest(IHTTPRequest, ISkinnable):
    """Browser-specific Request functionality.

    Note that the browser is special in many ways, since it exposes
    the Request object to the end-developer.
    """


class IBrowserPublisher(IPublishTraverse):
    """
    A type of `.IPublishTraverse` that also supports default objects.
    """

    def browserDefault(request):
        """Provide the default object

        The default object is expressed as a (possibly different)
        object and/or additional traversal steps.

        Returns an object and a sequence of names.  If the sequence of
        names is not empty, then a traversal step is made for each name.
        After the publisher gets to the end of the sequence, it will
        call ``browserDefault`` on the last traversed object.

        Normal usage is to return self for object and a default view name.

        The publisher calls this method at the end of each traversal path. If
        a non-empty sequence of names is returned, the publisher will traverse
        those names and call browserDefault again at the end.

        Note that if additional traversal steps are indicated (via a
        nonempty sequence of names), then the publisher will try to adjust
        the base href.
        """

class IBrowserPage(IBrowserView, IBrowserPublisher):
    """Browser page"""

    def __call__(*args, **kw):
        """Compute a response body"""


class IBrowserSkinType(ISkinType):
    """A skin is a set of layers."""


class IDefaultBrowserLayer(IBrowserRequest):
    """The default layer."""

alsoProvides(IDefaultBrowserLayer, IBrowserSkinType)
