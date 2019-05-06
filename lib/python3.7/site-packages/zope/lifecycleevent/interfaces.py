##############################################################################
#
# Copyright (c) 2002, 2003 Zope Foundation and Contributors.
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
"""Event-related interfaces
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface, Attribute
from zope.interface import interfaces


class IZopeLifecycleEvent(Interface):
    """
    High-level functions for sending events.

    These are implemented by the :mod:`zope.lifecycleevent` module.
    """

    def created(object):
        """Send an :class:`~.IObjectCreatedEvent` for ``object``."""

    def modified(object, *descriptions):
        """Send an :class:`~.IObjectModifiedEvent` for ``object``.

        ``descriptions`` is a sequence of interfaces or fields which were
        updated. The :class:`IAttributes` and :class:`ISequence` helpers
        can be used.

        """

    def copied(object, original):
        """Send an :class:`~.IObjectCopiedEvent` for ``object``.

        ``original`` is the object the copy was created from.

        """

    def moved(object, oldParent, oldName, newParent, newName):
        """Send an :class:`~.IObjectMovedEvent` for ``object``.

        ``oldParent`` is the container ``object`` was removed from.
        ``oldName`` was the name used to store ``object`` in ``oldParent``.
        ``newParent`` is the container ``object`` was added to.
        ``newName`` is the name used to store ``object`` in ``newParent``.

        Note that ``newParent`` and ``oldParent`` may be the same if the names
        are different, and vice versa.

        """

    def added(object, newParent=None, newName=None):
        """Send an :class:`~.IObjectAddedEvent` for ``object``.

        ``newParent`` is the container ``object`` was added to.
        ``newName`` is the name used to store ``object`` in the container.

        If either of these is not provided or is ``None``, they will
        be taken from the values of ``object.__parent__`` or
        ``object.__name__``, respectively.
        """

    def removed(object, oldParent=None, oldName=None):
        """Send an :class:`~.IObjectRemovedEvent` for ``object``.

        ``oldParent`` is the container ``object`` was removed from.
        ``oldName`` was the name used to store ``object`` in `oldParent`.

        If either of these is not provided or is ``None``, they will
        be taken from the values of ``object.__parent__`` or
        ``object.__name__``, respectively.
        """


class IObjectCreatedEvent(interfaces.IObjectEvent):
    """An object has been created.

    The ``object`` attribute will commonly have a value of ``None``
    for its ``__name__`` and ``__parent__`` values (if it has those attributes
    at all).
    """


class IObjectCopiedEvent(IObjectCreatedEvent):
    """An object has been copied."""

    original = Attribute("The original from which the copy was made.")


class IObjectModifiedEvent(interfaces.IObjectEvent):
    """An object has been modified"""

    descriptions = Attribute("""The supplied modification descriptions.

    These may be interfaces or implementations of :class:`IModificationDescription`
    such as :class:`~.Attributes` or :class:`~.Sequence`""")


class IModificationDescription(Interface):
    """Marker interface for descriptions of object modifications.

    Can be used as a parameter of an IObjectModifiedEvent."""


class IAttributes(IModificationDescription):
    """Describes the attributes of an interface."""

    interface = Attribute("The involved interface.")
    attributes = Attribute("A sequence of modified attributes.")


class ISequence(IModificationDescription):
    """Describes the modified keys of a sequence-like interface."""

    interface = Attribute("The involved interface.")
    keys = Attribute("A sequence of modified keys.")


##############################################################################
# Moving Objects

class IObjectMovedEvent(interfaces.IObjectEvent):
    """An object has been moved."""

    oldParent = Attribute("The old location parent for the object.")
    oldName = Attribute("The old location name for the object.")
    newParent = Attribute("The new location parent for the object.")
    newName = Attribute("The new location name for the object.")


##############################################################################
# Adding objects

class IObjectAddedEvent(IObjectMovedEvent):
    """An object has been added to a container."""


##############################################################################
# Removing objects


class IObjectRemovedEvent(IObjectMovedEvent):
    """An object has been removed from a container."""
