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
"""Life cycle events.

This module provides the :class:`~.IZopeLifecycleEvent` interface,
in addition to concrete classes implementing the various event interfaces.
"""
__docformat__ = 'restructuredtext'

from zope.interface.interfaces import ObjectEvent
from zope.interface import implementer, moduleProvides
from zope.event import notify

from zope.lifecycleevent.interfaces import IZopeLifecycleEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IAttributes
from zope.lifecycleevent.interfaces import ISequence


moduleProvides(IZopeLifecycleEvent)

@implementer(IObjectCreatedEvent)
class ObjectCreatedEvent(ObjectEvent):
    """An object has been created"""


def created(object):
    "See :meth:`.IZopeLifecycleEvent.created`"
    notify(ObjectCreatedEvent(object))


@implementer(IAttributes)
class Attributes(object):
    """Describes modified attributes of an interface."""

    def __init__(self, interface, *attributes):
        self.interface = interface
        self.attributes = attributes


@implementer(ISequence)
class Sequence(object):
    """Describes modified keys of an interface."""

    def __init__(self, interface, *keys):
        self.interface = interface
        self.keys = keys


@implementer(IObjectModifiedEvent)
class ObjectModifiedEvent(ObjectEvent):
    """An object has been modified"""

    def __init__(self, object, *descriptions):
        """Init with a list of modification descriptions."""
        super(ObjectModifiedEvent, self).__init__(object)
        self.descriptions = descriptions


def modified(object, *descriptions):
    "See :meth:`.IZopeLifecycleEvent.modified`"
    notify(ObjectModifiedEvent(object, *descriptions))


@implementer(IObjectCopiedEvent)
class ObjectCopiedEvent(ObjectCreatedEvent):
    """An object has been copied"""

    def __init__(self, object, original):
        super(ObjectCopiedEvent, self).__init__(object)
        self.original = original


def copied(object, original):
    "See :meth:`.IZopeLifecycleEvent.copied`"
    notify(ObjectCopiedEvent(object, original))


@implementer(IObjectMovedEvent)
class ObjectMovedEvent(ObjectEvent):
    """An object has been moved"""

    def __init__(self, object, oldParent, oldName, newParent, newName):
        ObjectEvent.__init__(self, object)
        self.oldParent = oldParent
        self.oldName = oldName
        self.newParent = newParent
        self.newName = newName


def moved(object, oldParent, oldName, newParent, newName):
    "See :meth:`.IZopeLifecycleEvent.moved`"
    notify(ObjectMovedEvent(object, oldParent, oldName, newParent, newName))


@implementer(IObjectAddedEvent)
class ObjectAddedEvent(ObjectMovedEvent):
    """An object has been added to a container.

    If ``newParent`` or ``newName`` is not provided or is ``None``,
    they will be taken from the values of ``object.__parent__`` or
    ``object.__name__``, respectively.
    """

    def __init__(self, object, newParent=None, newName=None):
        if newParent is None:
            newParent = object.__parent__
        if newName is None:
            newName = object.__name__
        ObjectMovedEvent.__init__(self, object, None, None, newParent, newName)


def added(object, newParent=None, newName=None):
    "See :meth:`.IZopeLifecycleEvent.added`"
    notify(ObjectAddedEvent(object, newParent, newName))


@implementer(IObjectRemovedEvent)
class ObjectRemovedEvent(ObjectMovedEvent):
    """An object has been removed from a container.

    If ``oldParent`` or ``oldName`` is not provided or is ``None``,
    they will be taken from the values of ``object.__parent__`` or
    ``object.__name__``, respectively.
    """

    def __init__(self, object, oldParent=None, oldName=None):
        if oldParent is None:
            oldParent = object.__parent__
        if oldName is None:
            oldName = object.__name__
        ObjectMovedEvent.__init__(self, object, oldParent, oldName, None, None)


def removed(object, oldParent=None, oldName=None):
    "See :meth:`.IZopeLifecycleEvent.removed`"
    notify(ObjectRemovedEvent(object, oldParent, oldName))



def _copy_docs():
    for func_name, func_value in IZopeLifecycleEvent.namesAndDescriptions():
        func = globals()[func_name]
        func.__doc__ = func_value.__doc__

_copy_docs()
del _copy_docs
