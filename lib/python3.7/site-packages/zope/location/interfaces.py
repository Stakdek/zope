##############################################################################
#
# Copyright (c) 2003-2009 Zope Foundation and Contributors.
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
"""Location framework interfaces
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.interface import Attribute
from zope.schema import TextLine


class ILocation(Interface):
    """Objects that can be located in a hierachy.

    Given a parent and a name an object can be located within that parent. The
    locatable object's `__name__` and `__parent__` attributes store this
    information.

    Located objects form a hierarchy that can be used to build file-system-like
    structures. For example in Zope `ILocation` is used to build URLs and to
    support security machinery.

    To retrieve an object from its parent using its name, the `ISublocation`
    interface provides the `sublocations` method to iterate over all objects
    located within the parent. The object searched for can be found by reading
    each sublocation's __name__ attribute.

    """

    __parent__ = Attribute("The parent in the location hierarchy.")

    __name__ = TextLine(
        title=(u"The name within the parent"),
        description=(u"The object can be looked up from the parent's "
                     u"sublocations using this name."),
        required=False,
        default=None)

# The IContained interface was moved from zope.container to here in
# zope.container 3.8.2 to break dependency cycles.  It is not actually
# used within this package, but is depended upon by external
# consumers.

class IContained(ILocation):
    """Objects contained in containers."""

class ILocationInfo(Interface):
    """Provides supplemental information for located objects.

    Requires that the object has been given a location in a hierarchy.

    """

    def getRoot():
        """Return the root object of the hierarchy."""

    def getPath():
        """Return the physical path to the object as a string.

        Uses '/' as the path segment separator.

        """

    def getParent():
        """Returns the container the object was traversed via.

        Returns None if the object is a containment root.
        Raises TypeError if the object doesn't have enough context to get the
        parent.

        """

    def getParents():
        """Returns a list starting with the object's parent followed by
        each of its parents.

        Raises a TypeError if the object is not connected to a containment
        root.

        """

    def getName():
        """Return the last segment of the physical path."""

    def getNearestSite():
        """Return the site the object is contained in

        If the object is a site, the object itself is returned.

        """


class ISublocations(Interface):
    """Provide access to sublocations of an object.

    All objects with the same parent object are called the ``sublocations`` of
    that parent.

    """

    def sublocations():
        """Return an iterable of the object's sublocations."""


class IRoot(Interface):
    """Marker interface to designate root objects within a location hierarchy.
    """


class LocationError(KeyError, LookupError):
    """There is no object for a given location."""

# Soft dependency on zope.component.
#
# Also, these interfaces used to be defined here directly, so this provides
# backward-compatibility
try:
    from zope.component.interfaces import ISite
except ImportError: # pragma: no cover
    class ISite(Interface):
        pass
