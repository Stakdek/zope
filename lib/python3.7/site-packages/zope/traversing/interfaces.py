##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Interfaces to do with traversing.
"""

from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent
from zope.interface.interfaces import ObjectEvent

# BBB: Re-import symbols to their old location.
from zope.location.interfaces import LocationError as TraversalError
from zope.location.interfaces import IRoot as IContainmentRoot
from zope.location.interfaces import ILocationInfo as IPhysicallyLocatable


_RAISE_KEYERROR = object()


class ITraversable(Interface):
    """To traverse an object, this interface must be provided"""

    def traverse(name, furtherPath):
        """Get the next item on the path

        Should return the item corresponding to 'name' or raise
        :exc:`~zope.location.interfaces.LocationError` where appropriate.

        :param str name: an ASCII string or Unicode object.
        :param list furtherPath: is a list of names still to be
            traversed.  This method is allowed to change the contents
            of furtherPath.
        """


class ITraverser(Interface):
    """Provide traverse features"""

    # XXX This is used like a utility but implemented as an adapter: The
    # traversal policy is only implemented once and repeated for all objects
    # along the path.

    def traverse(path, default=_RAISE_KEYERROR):
        """Return an object given a path.

        Path is either an immutable sequence of strings or a slash ('/')
        delimited string.

        If the first string in the path sequence is an empty string, or the
        path begins with a '/', start at the root. Otherwise the path is
        relative to the current context.

        If the object is not found, return *default* argument.

        """


class ITraversalAPI(Interface):
    """
    Common API functions to ease traversal computations.

    This is provided by :mod:`zope.traversing.api`.
    """

    def joinPath(path, *args):
        """Join the given relative paths to the given *path*.

        Returns a text (`unicode`) path.

        The path should be well-formed, and not end in a '/' unless it is
        the root path. It can be either a string (ascii only) or unicode.
        The positional arguments are relative paths to be added to the
        path as new path segments. The path may be absolute or relative.

        A segment may not start with a '/' because that would be confused
        with an absolute path. A segment may not end with a '/' because we
        do not allow '/' at the end of relative paths.  A segment may
        consist of '.' or '..' to mean "the same place", or "the parent path"
        respectively. A '.' should be removed and a '..' should cause the
        segment to the left to be removed.  ``joinPath('/', '..')`` should
        raise an exception.
        """

    def getPath(obj):
        """Returns a string representing the physical path to the object.
        """

    def getRoot(obj):
        """Returns the root of the traversal for the given object.
        """

    def traverse(object, path, default=None, request=None):
        """
        Traverse *path* relative to the given object.

        :param str path: a string with path segments separated by '/'.
        :keyword request: Passed in when traversing from
            presentation code.  This allows paths like "@@foo" to work.
        :raises zope.location.interfaces.LocationError: if *path* cannot be found

        .. note:: Calling `traverse` with a path argument taken from an
            untrusted source, such as an HTTP request form variable,
            is a bad idea.  It could allow a maliciously constructed
            request to call code unexpectedly.  Consider using
            `traverseName` instead.
        """

    def traverseName(obj, name, default=None, traversable=None,
                     request=None):
        """
        Traverse a single step *name* relative to the given object.

        *name* must be a string.  '.' and '..' are treated specially,
        as well as names starting with '@' or '+'.  Otherwise *name*
        will be treated as a single path segment.

        You can explicitly pass in an `ITraversable` as the
        *traversable* argument.  If you do not, the given object will
        be adapted to `ITraversable`.

        *request* is passed in when traversing from presentation code.
        This allows paths like "@@foo" to work.

        :raises zope.location.interfaces.LocationError: if *path* cannot
            be found and *default* was not provided.
        """

    def getName(obj):
        """
        Get the name an object was traversed via.
        """

    def getParent(obj):
        """
        Returns the container the object was traversed via.

        Returns `None` if the object is a containment root.

        :raises TypeError: if the object doesn't have enough context
            to get the parent.
        """

    def getParents(obj):
        """
        Returns a list starting with the given object's parent
        followed by each of its parents.

        :raises TypeError: if the context doesn't go all the way down
            to a containment root.
        """

    def canonicalPath(path_or_object):
        """
        Returns a canonical absolute unicode path for the path or object.

        Resolves segments that are '.' or '..'.

        :raises ValueError: if a badly formed path is given.
        """


class IPathAdapter(Interface):
    """
    Marker interface for adapters to be used in paths.

    .. seealso:: :class:`.namespace.adapter`.
    """


class IEtcNamespace(Interface):
    """
    Marker for utility registrations in the ``++etc++`` namespace.

    .. seealso:: :class:`.namespace.etc`
    """


class IBeforeTraverseEvent(IObjectEvent):
    """
    An event which gets sent on publication traverse.
    """

    request = Attribute("The current request")


@implementer(IBeforeTraverseEvent)
class BeforeTraverseEvent(ObjectEvent):
    """
    An event which gets sent on publication traverse.

    Default implementation of `IBeforeTraverseEvent`.
    """


    def __init__(self, ob, request):
        ObjectEvent.__init__(self, ob)
        self.request = request
