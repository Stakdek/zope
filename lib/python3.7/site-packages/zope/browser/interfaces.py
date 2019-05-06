##############################################################################
#
# Copyright (c) 2004-2009 Zope Foundation and Contributors.
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
"""Shared dependency less Zope3 brwoser components.
"""
__docformat__ = 'restructuredtext'

from zope.interface import Attribute
from zope.interface import Interface

class IView(Interface):
    """ Views are multi-adapters for context and request objects.
    """
    context = Attribute("The context object the view renders")
    request = Attribute("The request object driving the view")

class IBrowserView(IView):
    """ Views which are specialized for requests from a browser

    Such views are distinct from those geerated via WebDAV, FTP, XML-RPC,
    etc.
    """

class IAdding(IBrowserView):
    """ Multi-adapter interface for views which add items to containers.

    The 'context' of the view must implement :obj:`zope.container.interfaces.IContainer`.
    """

    def add(content):
        """Add content object to context.

        Add using the name in ``contentName``.

        Return the added object in the context of its container.

        If ``contentName`` is already used in container, raise
        :class:`zope.container.interfaces.DuplicateIDError`.
        """

    contentName = Attribute(
        """The content name, usually set by the Adder traverser.

        If the content name hasn't been defined yet, returns ``None``.

        Some creation views might use this to optionally display the
        name on forms.
        """
    )

    def nextURL():
        """Return the URL that the creation view should redirect to.

        This is called by the creation view after calling add.

        It is the adder's responsibility, not the creation view's to
        decide what page to display after content is added.
        """

    def nameAllowed():
        """Return whether names can be input by the user.
        """

    def addingInfo():
        """Return add menu data as a sequence of mappings.

        Each mapping contains 'action', 'title', and possibly other keys.

        The result is sorted by title.
        """

    def isSingleMenuItem():
        """Return whether there is single menu item or not."""

    def hasCustomAddView():
        "This should be called only if there is ``singleMenuItem`` else return 0"


class ITerms(Interface):
    """ Adapter providing lookups for vocabulary terms.
    """
    def getTerm(value):
        """Return an ITitledTokenizedTerm object for the given value

        LookupError is raised if the value isn't in the source.

        The return value should have the ``token`` and ``title`` attributes.
        """

    def getValue(token):
        """Return a value for a given identifier token

        LookupError is raised if there isn't a value in the source.
        """

class ISystemErrorView(Interface):
    """Error views that can classify their contexts as system errors
    """

    def isSystemError():
        """Return a boolean indicating whether the error is a system errror
        """
