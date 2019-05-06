=============================
 Creating and Sending Events
=============================

As discussed in :doc:`quickstart`, most uses of
``zope.lifecycleevent`` will be satisfied with the high level API
described by
:class:`~zope.lifecycleevent.interfaces.IZopeLifecycleEvent`, but it is
possible to create and send events manually, both those defined here
and your own subclasses.

Provided Events
===============

All of the functions described in :doc:`quickstart` are very simple
wrappers that create an event object defined by this package and then
use :func:`zope.event.notify` to send it. You can do the same, as
shown below, but there is usually little reason to do so.

    >>> from zope.event import notify
    >>> from zope.lifecycleevent import ObjectCreatedEvent
    >>> from zope.lifecycleevent import ObjectCopiedEvent
    >>> from zope.lifecycleevent import ObjectModifiedEvent
    >>> from zope.lifecycleevent import ObjectMovedEvent
    >>> from zope.lifecycleevent import ObjectRemovedEvent

    >>> obj = object()
    >>> notify(ObjectCreatedEvent(obj))
    >>> notify(ObjectCopiedEvent(object(), obj))
    >>> notify(ObjectMovedEvent(obj,
    ...        None, 'oldName',
    ...        None, 'newName'))
    >>> notify(ObjectModifiedEvent(obj, "description 1", "description 2"))
    >>> notify(ObjectRemovedEvent(obj, "oldParent", "oldName"))

Subclassing Events
==================

It can sometimes be helpful to subclass one of the provided event
classes. If you then want to send a notification of that class, you
must manually construct and notify it.

One reason to create a subclass is to be able to add additional
attributes to the event object, perhaps changing the constructor
signature in the process. Another reason to create a subclass is to be
able to easily subscribe to all events that are *just* of that class.
The class :class:`zope.container.contained.ContainerModifiedEvent` is
used for this reason.


For example, in an application with distinct users, we might want to
let subscribers know which user created the object. We might also want
to be able to distinguish between objects that are created by a user
and those that are automatically created as part of system operation
or administration. The following subclass lets us do both.

    >>> class ObjectCreatedByEvent(ObjectCreatedEvent):
    ...    "A created event that tells you who created the object."
    ...    def __init__(self, object, created_by):
    ...        super(ObjectCreatedByEvent, self).__init__(object)
    ...        self.created_by = created_by

    >>> obj = object()
    >>> notify(ObjectCreatedByEvent(obj, "Black Night"))
