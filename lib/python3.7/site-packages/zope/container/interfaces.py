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
"""Container-related interfaces
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface, Invalid
from zope.interface.common.mapping import IItemMapping
from zope.interface.common.mapping import IReadMapping, IEnumerableMapping
from zope.location.interfaces import ILocation
from zope.schema import Set

from zope.lifecycleevent.interfaces import IObjectModifiedEvent

# the following imports provide backwards compatibility for consumers;
# do not remove them
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.location.interfaces import IContained
# /end backwards compatibility imports

from zope.container.i18n import ZopeMessageFactory as _

class DuplicateIDError(KeyError):
    pass

class ContainerError(Exception):
    """An error of a container with one of its components."""

class InvalidContainerType(Invalid, TypeError):
    """The type of a container is not valid."""

class InvalidItemType(Invalid, TypeError):
    """The type of an item is not valid."""

class InvalidType(Invalid, TypeError):
    """The type of an object is not valid."""



class IItemContainer(IItemMapping):
    """Minimal readable container."""


class ISimpleReadContainer(IItemContainer, IReadMapping):
    """Readable content containers."""


class IReadContainer(ISimpleReadContainer, IEnumerableMapping):
    """Readable containers that can be enumerated."""


class IWriteContainer(Interface):
    """An interface for the write aspects of a container."""

    def __setitem__(name, object):
        """Add the given `object` to the container under the given name.

        Raises a ``TypeError`` if the key is not a unicode or ascii string.

        Raises a ``ValueError`` if the key is empty, or if the key contains
        a character which is not allowed in an object name.

        Raises a ``KeyError`` if the key violates a uniqueness constraint.

        The container might choose to add a different object than the
        one passed to this method.

        If the object doesn't implement `IContained`, then one of two
        things must be done:

        1. If the object implements `ILocation`, then the `IContained`
           interface must be declared for the object.

        2. Otherwise, a `ContainedProxy` is created for the object and
           stored.

        The object's `__parent__` and `__name__` attributes are set to the
        container and the given name.

        If the old parent was ``None``, then an `IObjectAddedEvent` is
        generated, otherwise, an `IObjectMovedEvent` is generated.  An
        `IContainerModifiedEvent` is generated for the container.

        If the object replaces another object, then the old object is
        deleted before the new object is added, unless the container
        vetos the replacement by raising an exception.

        If the object's `__parent__` and `__name__` were already set to
        the container and the name, then no events are generated and
        no hooks.  This allows advanced clients to take over event
        generation.

        """

    def __delitem__(name):
        """Delete the named object from the container.

        Raises a ``KeyError`` if the object is not found.

        If the deleted object's `__parent__` and `__name__` match the
        container and given name, then an `IObjectRemovedEvent` is
        generated and the attributes are set to ``None``. If the object
        can be adapted to `IObjectMovedEvent`, then the adapter's
        `moveNotify` method is called with the event.

        Unless the object's `__parent__` and `__name__` attributes were
        initially ``None``, generate an `IContainerModifiedEvent` for the
        container.

        If the object's `__parent__` and `__name__` were already set to
        ``None``, then no events are generated.  This allows advanced
        clients to take over event generation.

        """


class IItemWriteContainer(IWriteContainer, IItemContainer):
    """A write container that also supports minimal reads."""


class IContainer(IReadContainer, IWriteContainer):
    """Readable and writable content container."""


class IContentContainer(IContainer):
    """A container that is to be used as a content type."""


class IBTreeContainer(IContainer):
    """Container that supports BTree semantics for some methods."""

    def items(key=None):
        """Return an iterator over the key-value pairs in the container.

        If ``None`` is passed as `key`, this method behaves as if no argument
        were passed; exactly as required for ``IContainer.items()``.

        If `key` is in the container, the first item provided by the iterator
        will correspond to that key.  Otherwise, the first item will be for
        the key that would come next if `key` were in the container.

        """

    def keys(key=None):
        """Return an iterator over the keys in the container.

        If ``None`` is passed as `key`, this method behaves as if no argument
        were passed; exactly as required for ``IContainer.keys()``.

        If `key` is in the container, the first key provided by the iterator
        will be that key.  Otherwise, the first key will be the one that would
        come next if `key` were in the container.

        """

    def values(key=None):
        """Return an iterator over the values in the container.

        If ``None`` is passed as `key`, this method behaves as if no argument
        were passed; exactly as required for ``IContainer.values()``.

        If `key` is in the container, the first value provided by the iterator
        will correspond to that key.  Otherwise, the first value will be for
        the key that would come next if `key` were in the container.

        """


class IOrdered(Interface):
    """Objects whose contents are maintained in order."""


    def updateOrder(order):
        """Revise the order of keys, replacing the current ordering.

        order is a list or a tuple containing the set of existing keys in
        the new order. `order` must contain ``len(keys())`` items and cannot
        contain duplicate keys.

        Raises ``TypeError`` if order is not a tuple or a list.

        Raises ``ValueError`` if order contains an invalid set of keys.
        """


class IOrderedContainer(IOrdered, IContainer):
    """Containers whose contents are maintained in order."""



class IContainerNamesContainer(IContainer):
    """Containers that always choose names for their items."""

class IReservedNames(Interface):
    """A sequence of names that are reserved for that container"""
    
    reservedNames = Set(
        title=_(u'Reserved Names'),
        description=_(u'Names that are not allowed for addable content'),
        required=True,
        )
    
class NameReserved(ValueError):
    __doc__ = _("""The name is reserved for this container""")

##############################################################################
# Adding objects

class UnaddableError(ContainerError):
    """An object cannot be added to a container."""

    def __init__(self, container, obj, message=""):
        self.container = container
        self.obj = obj
        self.message = message and ": %s" % message

    def __str__(self):
        return ("%(obj)s cannot be added "
                "to %(container)s%(message)s" % self.__dict__)


class INameChooser(Interface):

    def checkName(name, object):
        """Check whether an object name is valid.

        Raises a user error if the name is not valid.
        """

    def chooseName(name, object):
        """Choose a unique valid name for the object.

        The given name and object may be taken into account when
        choosing the name.

        chooseName is expected to always choose a valid name (that would pass
        the checkName test) and never raise an error.

        """


##############################################################################
# Modifying containers


class IContainerModifiedEvent(IObjectModifiedEvent):
    """The container has been modified.

    This event is specific to "containerness" modifications, which means
    addition, removal or reordering of sub-objects.
    """


##############################################################################
# Finding objects

class IFind(Interface):
    """
    Find support for containers.
    """

    def find(id_filters=None, object_filters=None):
        """Find object that matches all filters in all sub-objects.

        This container itself is not included.
        """


class IObjectFindFilter(Interface):

    def matches(object):
        """Return True if the object matches the filter criteria."""


class IIdFindFilter(Interface):

    def matches(id):
        """Return True if the id matches the filter criteria."""
