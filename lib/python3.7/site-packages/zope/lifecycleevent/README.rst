=============
 Quick Start
=============

.. module:: zope.lifecycleevent

This document describes the various event types defined by this
package and provides some basic examples of using them to inform parts
of the system about object changes.

All events have three components: an *interface* defining the event's
structure, a default *implementation* of that interface (the *event
object*), and a high-level *convenience function* (defined by the
:class:`~.IZopeLifecycleEvent` interface) for easily sending that
event in a single function call.

.. note:: The convenience functions are simple wrappers for
   constructing an event object and sending it via
   :func:`zope.event.notify`. Here we will only discuss using these
   functions; for more information on the advanced usage of when and
   how to construct and send event objects manually, see
   :doc:`manual`.

.. note:: This document will not discuss actually *handling* these
   events (setting up *subscribers* for them). For information on
   that topic, see :doc:`handling`.

We will go through the events in approximate order of how they would
be used to follow the life-cycle of an object.

Creation
========

The first event is :class:`~.IObjectCreatedEvent`, implemented by
:class:`~.ObjectCreatedEvent`, which is used to communicate that a single object
has been created. It can be sent with the
:func:`zope.lifecycleevent.created` function.


For example:

    >>> from zope.lifecycleevent import created

    >>> obj = {}
    >>> created(obj)

Copying
=======

Copying an object is a special case of creating one. It can happen at
any time and is implemented with :class:`~.IObjectCopiedEvent`,
:class:`~.ObjectCopiedEvent`, or the API
:func:`zope.lifecycleevent.copied`.

    >>> from zope.lifecycleevent import copied
    >>> import pickle
    >>> copy = pickle.loads(pickle.dumps(obj))
    >>> copied(copy, obj)

.. note::
   Handlers for :class:`~.IObjectCreatedEvent` can expect to
   receive events for :class:`~.IObjectCopiedEvent` as well.

.. _addition:

Addition
========

After objects are created, it is common to *add* them somewhere for
storage or access. This can be accomplished with the
:class:`~.IObjectAddedEvent` and its implementation
:class:`~.ObjectAddedEvent`, or the API
:func:`zope.lifecycleevent.added`.

    >>> from zope.lifecycleevent import ObjectAddedEvent
    >>> from zope.lifecycleevent import added

    >>> container = {}
    >>> container['name'] = obj
    >>> added(obj, container, 'name')

If the object being added has a non-None ``__name__`` or ``__parent__``
attribute, we can omit those values when we call ``added`` and the
attributes will be used.

    >>> class Location(object):
    ...    __parent__ = None
    ...    __name__ = None

    >>> location = Location()
    >>> location.__name__ = "location"
    >>> location.__parent__ = container
    >>> container[location.__name__] = location
    >>> added(location)

.. tip::
   The interface :class:`zope.location.interfaces.ILocation`
   defines these attributes (although we don't require the object to
   implement that interface), and containers that implement
   :class:`zope.container.interfaces.IWriteContainer` are expected to
   set them (such containers will also automatically send the
   :class:`~.IObjectAddedEvent`).


Modification
============

One of the most common types of events used from this package is the
:class:`~.IObjectModifiedEvent` (implemented by
:class:`~.ObjectModifiedEvent`) that represents object modification.

In the simplest case, it may be enough to simply notify interested
parties that the object has changed. Like the other events, this can
be done manually or through the convenience API
(:func:`zope.lifecycleevent.modified`):

    >>> obj['key'] = 42

    >>> from zope.lifecycleevent import modified
    >>> modified(obj)

Providing Additional Information
--------------------------------

Some event consumers like indexes (catalogs) and caches may need more
information to update themselves in an efficient manner. The necessary
information can be provided as optional "modification descriptions" of
the :class:`~.ObjectModifiedEvent` (or again, via the
:func:`~zope.lifecycleevent.modified` function).

This package doesn't strictly define what a "modification description"
must be. The most common (and thus most interoperable) descriptions
are based on interfaces.

We could simply pass an interface itself to say "something about the
way this object implements the interface changed":

    >>> from zope.interface import Interface, Attribute, implementer
    >>> class IFile(Interface):
    ...     data = Attribute("The data of the file.")
    ...     name = Attribute("The name of the file.")

    >>> @implementer(IFile)
    ... class File(object):
    ...     data = ''
    ...     name = ''

    >>> file = File()
    >>> created(file)
    >>> file.data = "123"
    >>> modified(file, IFile)

Attributes
~~~~~~~~~~

We can also be more specific in a case like this where we know exactly
what attribute of the interface we modified. There is a helper class
:class:`zope.lifecycleevent.Attributes` that assists:

    >>> from zope.lifecycleevent import Attributes
    >>> file.data = "abc"
    >>> modified(file, Attributes(IFile, "data"))

If we modify multiple attributes of an interface at the same time, we
can include that information in a single ``Attributes`` object:

    >>> file.data = "123"
    >>> file.name = "123.txt"
    >>> modified(file, Attributes(IFile, "data", "name"))

Sometimes we may change attributes from multiple interfaces at the
same time. We can also represent this by including more than one
``Attributes`` instance:

   >>> import time
   >>> class IModified(Interface):
   ...    lastModified = Attribute("The timestamp when the object was modified.")

   >>> @implementer(IModified)
   ... class ModifiedFile(File):
   ...    lastModified = 0

   >>> file = ModifiedFile()
   >>> created(file)

   >>> file.data = "abc"
   >>> file.lastModified = time.time()
   >>> modified(file,
   ...          Attributes(IFile, "data"),
   ...          Attributes(IModified, "lastModified"))


Sequences
~~~~~~~~~

When an object is a sequence or container, we can specify
the individual indexes or keys that we changed using
:class:`zope.lifecycleevent.Sequence`.

First we'll need to define a sequence and create an instance:

    >>> from zope.interface.common.sequence import ISequence
    >>> class IFileList(ISequence):
    ...    "A sequence of IFile objects."
    >>> @implementer(IFileList)
    ... class FileList(list):
    ...   pass

    >>> files = FileList()
    >>> created(files)

Now we can modify the sequence by adding an object to it:

    >>> files.append(File())
    >>> from zope.lifecycleevent import Sequence
    >>> modified(files, Sequence(IFileList, len(files) - 1))

We can also replace an existing object:

    >>> files[0] = File()
    >>> modified(files, Sequence(IFileList, 0))

Of course ``Attributes`` and ``Sequences`` can be combined in any
order and length necessary to describe the modifications fully.

Modification Descriptions
~~~~~~~~~~~~~~~~~~~~~~~~~

Although this package does not require any particular definition or
implementation of modification descriptions, it provides the two that
we've already seen: :class:`~zope.lifecycleevent.Attributes` and
:class:`~zope.lifecycleevent.Sequence`. Both of these classes
implement the marker interface
:class:`~zope.lifecycleevent.interfaces.IModificationDescription`. If
you implement custom modification descriptions, consider implementing
this marker interface.

Movement
========

Sometimes objects move from one place to another. This can be
described with the interface :class:`~.IObjectMovedEvent`, its
implementation :class:`~.ObjectMovedEvent` or the API
:func:`zope.lifecycleevent.moved`.

Objects may move within a single container by changing their name:

   >>> from zope.lifecycleevent import moved
   >>> container['new name'] = obj
   >>> del container['name']
   >>> moved(obj,
   ...       oldParent=container, oldName='name',
   ...       newParent=container, newName='new name')

Or they may move to a new container (under the same name, or a
different name):

   >>> container2 = {}
   >>> container2['new name'] = obj
   >>> del container['new name']
   >>> moved(obj,
   ...       oldParent=container,  oldName='new name',
   ...       newParent=container2, newName='new name')

Unlike :ref:`addition <addition>`, any ``__name__`` and ``__parent__``
attribute on the object are ignored and must be provided explicitly.

.. tip::
   Much like the addition of objects,
   :class:`zope.container.interfaces.IWriteContainer` implementations
   are expected to update the ``__name__`` and ``__parent__``
   attributes automatically, and to automatically send the appropriate
   movement event.

Removal
=======

Finally, objects can be removed from the system altogether with
:class:`IObjectRemovedEvent`, :class:`ObjectRemovedEvent` and
:func:`zope.lifecycleevent.removed`.

    >>> from zope.lifecycleevent import removed
    >>> del container2['new name']
    >>> removed(obj, container2, 'new name')

.. note::
   This is a special case of movement where the new parent and
   new name are always ``None``. Handlers for
   :class:`~.IObjectMovedEvent` can expect to receive events for
   :class:`~.IObjectRemovedEvent` as well.

If the object being removed provides the ``__name__`` or
``__parent__`` attribute, those arguments can be omitted and the
attributes will be used instead.

    >>> location = container['location']
    >>> del container[location.__name__]
    >>> removed(location)

.. tip::
   Once again, :class:`~zope.container.interfaces.IWriteContainer`
   implementations will send the correct event automatically.
