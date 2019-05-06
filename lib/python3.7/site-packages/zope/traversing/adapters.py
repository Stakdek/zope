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
"""
Adapters for the traversing mechanism.
"""

import six
import zope.interface

from zope.location.interfaces import ILocationInfo, LocationError
from zope.traversing.interfaces import ITraversable, ITraverser
from zope.traversing.namespace import namespaceLookup
from zope.traversing.namespace import nsParse

from zope.location.traversing import RootPhysicallyLocatable  # BBB


_marker = object()  # opaque marker that doesn't get security proxied


@zope.interface.implementer(ITraversable)
class DefaultTraversable(object):
    """
    Traverses objects via attribute and item lookup.

    Implements `~zope.traversing.interfaces.ITraversable`.
    """

    def __init__(self, subject):
        self._subject = subject

    def traverse(self, name, furtherPath):
        subject = self._subject
        __traceback_info__ = (subject, name, furtherPath)
        try:
            attr = getattr(subject, name, _marker)
        except UnicodeEncodeError:
            # If we're on Python 2, and name was a unicode string the
            # name would have been encoded using the system encoding
            # (usually ascii). Failure to encode means invalid
            # attribute name.
            attr = _marker
        if attr is not _marker:
            return attr
        if hasattr(subject, '__getitem__'):
            try:
                return subject[name]
            except (KeyError, TypeError):
                pass
        raise LocationError(subject, name)


@zope.interface.implementer(ITraverser)
class Traverser(object):
    """
    Provide traverse features.

    Implements `~zope.traversing.interfaces.ITraverser`.
    """

    # This adapter can be used for any object.

    def __init__(self, wrapper):
        self.context = wrapper

    def traverse(self, path, default=_marker, request=None):
        if not path:
            return self.context

        if isinstance(path, six.string_types):
            path = path.split('/')
            if len(path) > 1 and not path[-1]:
                # Remove trailing slash
                path.pop()
        else:
            path = list(path)

        path.reverse()
        pop = path.pop

        curr = self.context
        if not path[-1]:
            # Start at the root
            pop()
            curr = ILocationInfo(self.context).getRoot()
        try:
            while path:
                name = pop()
                curr = traversePathElement(curr, name, path, request=request)

            return curr
        except LocationError:
            if default == _marker:
                raise
            return default


def traversePathElement(obj, name, further_path, default=_marker,
                        traversable=None, request=None):
    """
    Traverse a single step *name* relative to the given object.

    This is used to implement
    :meth:`zope.traversing.interfaces.ITraversalAPI.traverseName`.

    :param str name: must be a string.  '.' and '..' are treated
        specially, as well as names starting with '@' or '+'.
        Otherwise *name* will be treated as a single path segment.
    :param list further_path: a list of names still to be traversed.
        This method is allowed to change the contents of
        *further_path*.

    :keyword ITraversable traversable: You can explicitly pass in
        an `~zope.traversing.interfaces.ITraversable` as the
        *traversable* argument.  If you do not, the given object will
        be adapted to ``ITraversable``.

    :keyword request: assed in when traversing from presentation
        code.  This allows paths like ``@@foo`` to work.

    :raises zope.location.interfaces.LocationError: if *path* cannot
        be found and '*default* was not provided.
    """
    __traceback_info__ = (obj, name)

    if name == '.':
        return obj

    if name == '..':
        return obj.__parent__

    if name and name[:1] in '@+':
        ns, nm = nsParse(name)
        if ns:
            return namespaceLookup(ns, nm, obj, request)
    else:
        nm = name

    if traversable is None:
        traversable = ITraversable(obj, None)
        if traversable is None:
            raise LocationError('No traversable adapter found', obj)

    try:
        return traversable.traverse(nm, further_path)
    except UnicodeEncodeError:
        # If we're on Python 2, and nm was a unicode string, and the traversable
        # tried to do an attribute lookup, the nm would have been encoded using the
        # system encoding (usually ascii). Failure to encode means invalid attribute
        # name.
        if default is not _marker:
            return default
        raise LocationError(obj, name)
    except LocationError:
        if default is not _marker:
            return default
        raise
