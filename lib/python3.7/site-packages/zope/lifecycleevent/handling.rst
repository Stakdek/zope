=================
 Handling Events
=================

This document provides information on how to handle the lifycycle
events defined and sent by this package.

Background information on handling events is found in
:mod:`zope.event's documentation <zope.event>`.

Class Based Handling
====================

:mod:`zope.event` includes `a simple framework`_ for dispatching
events based on the class of the event. This could be used to provide
handlers for each of the event classes defined by this package
(:class:`ObjectCreatedEvent`, etc). However, it doesn't allow
configuring handlers based on the kind of *object* the event contains.
To do that, we need another level of dispatching.

Fortunately, that level of dispatching already exists within
:mod:`zope.component`.

.. _a simple framework: https://zopeevent.readthedocs.io/en/latest/classhandler.html


Component Based Handling
========================

:mod:`zope.component` includes an `event dispatching framework`_ that
lets us dispatch events based not just on the kind of the event, but
also on the kind of object the event contains.

All of the events defined by this package are implementations of
:class:`zope.interface.interfaces.IObjectEvent`. :mod:`zope.component`
`includes special support`_ for these kinds of events. That document
walks through a generic example in Python code. Here we will show an
example specific to life cycle events using the type of configuration
that is more likely to be used in a real application.

For this to work, it's important that :mod:`zope.component` is configured
correctly. Usually this is done with ZCML executed at startup time (we
will be using strings in this documentation, but usually this resides
in files, most often named ``configure.zcml``):

   >>> from zope.configuration import xmlconfig
   >>> _ = xmlconfig.string("""
   ...   <configure xmlns="http://namespaces.zope.org/zope">
   ...     <include package="zope.component" />
   ...   </configure>
   ... """)

First we will define an object we're interested in getting events for:

    >>> from zope.interface import Interface, Attribute, implementer
    >>> class IFile(Interface):
    ...     data = Attribute("The data of the file.")
    ...     name = Attribute("The name of the file.")
    >>> @implementer(IFile)
    ... class File(object):
    ...     data = ''
    ...     name = ''


Next, we will write our subscriber. Normally, ``zope.event``
subscribers take just one argument, the event object. But when we use
the automatic dispatching that ``zope.component`` provides, our
function will receive *two* arguments: the object of the event, and
the event. We can use the decorators that ``zope.component`` supplies
to annotate the function with the kinds of arguments it wants to
handle. Alternatively, we could specify that information when we
register the handler with zope.component (we'll see an example of that
later).

    >>> from zope.component import adapter
    >>> from zope.lifecycleevent import IObjectCreatedEvent
    >>> @adapter(IFile, IObjectCreatedEvent)
    ... def on_file_created(file, event):
    ...    print("A file of type '%s' was created" % (file.__class__.__name__))

Finally, we will register our handler with zope.component. This is
also usually done with ZCML executed at startup time:

    >>> _ = xmlconfig.string("""
    ...   <configure xmlns="http://namespaces.zope.org/zope">
    ...     <include package="zope.component" file="meta.zcml" />
    ...     <subscriber handler="__main__.on_file_created"/>
    ...   </configure>
    ... """)

Now we can send an event noting that a file was created, and our handler
will be called:

    >>> from zope.lifecycleevent import created
    >>> file = File()
    >>> created(file)
    A file of type 'File' was created

Other types of objects don't trigger our handler:

    >>> created(object)

The hierarchy is respected, so if we define a subclass of ``File`` and
indeed, even a sub-interface of ``IFile``, our handler will be
invoked.

    >>> class SubFile(File): pass
    >>> created(SubFile())
    A file of type 'SubFile' was created

    >>> class ISubFile(IFile): pass
    >>> @implementer(ISubFile)
    ... class IndependentSubFile(object):
    ...     data = name = ''
    >>> created(IndependentSubFile())
    A file of type 'IndependentSubFile' was created

We can further register a handler just for the subinterface we
created. Here we'll also demonstrate supplying this information in
ZCML.

    >>> def generic_object_event(obj, event):
    ...    print("Got '%s' for an object of type '%s'" % (event.__class__.__name__, obj.__class__.__name__))
    >>> _ = xmlconfig.string("""
    ...   <configure xmlns="http://namespaces.zope.org/zope">
    ...     <include package="zope.component" file="meta.zcml" />
    ...     <subscriber handler="__main__.generic_object_event"
    ...                 for="__main__.ISubFile zope.lifecycleevent.IObjectCreatedEvent" />
    ...   </configure>
    ... """)

Now both handlers will be called for implementations of ``ISubFile``,
but still only the original implementation will be called for base ``IFiles``.

    >>> created(IndependentSubFile())
    A file of type 'IndependentSubFile' was created
    Got 'ObjectCreatedEvent' for an object of type 'IndependentSubFile'
    >>> created(File())
    A file of type 'File' was created

Projects That Rely on Dispatched Events
---------------------------------------

Handlers for life cycle events are commonly registered with
``zope.component`` as a means for keeping projects uncoupled. This
section provides a partial list of such projects for reference.

As mentioned in :doc:`quickstart`, the containers provided by
`zope.container`_ generally automatically send the correct life
cycle events.

At a low-level, there are utilities that assign integer IDs to objects
as they are created such as `zope.intid`_ and `zc.intid`_.
``zc.intid``, in particular, `documents the way it uses events`_.

``zope.catalog`` can `automatically index documents`_ as part of
handling life cycle events.

Containers and Sublocations
---------------------------

The events :class:`~ObjectAddedEvent` and :class:`~ObjectRemovedEvent`
usually need to be (eventually) sent in pairs for any given object.
That is, when an added event is sent for an object, for symmetry
eventually a removed event should be sent too. This makes sure that
proper cleanup can happen.

Sometimes one object can be said to contain other objects. This is
obvious in the case of lists, dictionaries and the container objects
provided by `zope.container`_, but the same can sometimes be said for
other types of objects too that reference objects in their own
attributes.

What happens when a life cycle event for such an object is sent? By
default, *nothing*. This may leave the system in an inconsistent
state.

For example, lets create a container and add some objects to
it. First we'll set up a generic event handler so we can see the
events that go out.

    >>> _ = xmlconfig.string("""
    ...   <configure xmlns="http://namespaces.zope.org/zope">
    ...     <include package="zope.component" file="meta.zcml" />
    ...     <subscriber handler="__main__.generic_object_event"
    ...                 for="* zope.interface.interfaces.IObjectEvent" />
    ...   </configure>
    ... """)
    Got...
    >>> from zope.lifecycleevent import added
    >>> container = {}
    >>> created(container)
    Got 'ObjectCreatedEvent' for an object of type 'dict'
    >>> object1 = object()
    >>> container['object1'] = object1
    >>> added(object1, container, 'object1')
    Got 'ObjectAddedEvent' for an object of type 'object'

We can see that we got an "added" event for the object we stored in
the container. What happens when we remove the container?

    >>> from zope.lifecycleevent import removed
    >>> tmp = container
    >>> del container
    >>> removed(tmp, '', '')
    Got 'ObjectRemovedEvent' for an object of type 'dict'
    >>> del tmp

We only got an event for the container, not the objects it contained!
If the handlers that fired when we added "object1" had done anything
that needed to be *undone* for symmetry when "object1" was removed
(e.g., if it had been indexed and needed to be unindexed) the system
is now corrupt because those handlers never got the
``ObjectRemovedEvent`` for "object1".


The solution to this problem comes from `zope.container`_. It defines
the concept of :class:`~zope.container.interfaces.ISubLocations`: a
way for any given object to inform other objects about the objects it
contains (and it provides a :class:`default implementation of
ISubLocations <zope.container.contained.ContainerSublocations>` for
containers). It also provides :func:`a function
<zope.container.contained.dispatchToSublocations>` that will send
events that happen to the *parent* object for all the *child* objects
it contains.

In this way, its possible for any arbitrary life cycle event to
automatically be propagated to its children without any specific
caller of ``remove``, say, needing to have any specific knowledge
about containment relationships.

For this to work, two things must be done:

1. Configure `zope.container`_. This too is usually done in ZCML with
   ``<include package="zope.container"/>``.
2. Provide an adapter to :class:`~.ISubLocations` when some object can
   contain other objects that need events.


.. _zope.intid: https://zopeintid.readthedocs.io/en/latest/
.. _zc.intid: https://zcintid.readthedocs.io/en/latest/
.. _documents the way it uses events: https://zcintid.readthedocs.io/en/latest/subscribers.html
.. _automatically index documents: https://zopecatalog.readthedocs.io/en/latest/events.html
.. _zope.container: https://zopecontainer.readthedocs.io/en/latest/
.. _event dispatching framework: https://zopecomponent.readthedocs.io/en/latest/event.html
.. _includes special support : https://zopecomponent.readthedocs.io/en/latest/event.html#object-events
