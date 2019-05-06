Containment constraints
=======================

Containment constraints allow us to express restrictions on the types
of items that can be placed in containers or on the types of
containers an item can be placed in.  We express these constraints in
interfaces.  We will use some container and item interfaces defined
in :mod:`zope.container.tests.constraints_example`:

.. literalinclude:: ../src/zope/container/tests/constraints_example.py
   :lines: 1-9

In this example, we used the contains function to declare that objects
that provide IBuddyFolder can only contain items that provide IBuddy.
Note that we used a string containing a dotted name for the IBuddy
interface. This is because IBuddy hasn't been defined yet.  When we
define IBuddy, we can use IBuddyFolder directly:

.. literalinclude:: ../src/zope/container/tests/constraints_example.py
   :lines: 11-12


Now, with these interfaces in place, we can define Buddy and
BuddyFolder classes:

.. literalinclude:: ../src/zope/container/tests/constraints_example.py
   :lines: 14-20


and verify that we can put buddies in buddy folders:

.. doctest::

    >>> from zope.component.factory import Factory
    >>> from zope.container.constraints import checkFactory
    >>> from zope.container.constraints import checkObject
    >>> from zope.container.tests.constraints_example import Buddy
    >>> from zope.container.tests.constraints_example import BuddyFolder

    >>> checkObject(BuddyFolder(), 'x', Buddy())
    >>> checkFactory(BuddyFolder(), 'x', Factory(Buddy))
    True

If we try to use other containers or folders, we'll get errors:

.. doctest::

    >>> from zope.container.interfaces import IContainer
    >>> from zope.interface import implementer
    >>> @implementer(IContainer)
    ... class Container:
    ...     pass

    >>> from zope.location.interfaces import IContained
    >>> @implementer(IContained)
    ... class Contained:
    ...     pass

    >>> checkObject(Container(), 'x', Buddy())
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    InvalidContainerType: ...

    >>> checkFactory(Container(), 'x', Factory(Buddy))
    False

    >>> checkObject(BuddyFolder(), 'x', Contained())
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    InvalidItemType: ...

    >>> checkFactory(BuddyFolder(), 'x', Factory(Contained))
    False

In the example, we defined the container first and then the items.  We
could have defined these in the opposite order:

.. literalinclude:: ../src/zope/container/tests/constraints_example.py
   :lines: 22-34

.. doctest::

    >>> from zope.container.tests.constraints_example import Contact
    >>> from zope.container.tests.constraints_example import Contacts
    >>> checkObject(Contacts(), 'x', Contact())

    >>> checkFactory(Contacts(), 'x', Factory(Contact))
    True

    >>> checkObject(Contacts(), 'x', Buddy())
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    InvalidItemType: ...

    >>> checkFactory(Contacts(), 'x', Factory(Buddy))
    False

The constraints prevent us from moving a container beneath itself (either into
itself or another folder beneath it):

.. doctest::

    >>> container = Container()
    >>> checkObject(container, 'x', container)
    Traceback (most recent call last):
    TypeError: Cannot add an object to itself or its children.

    >>> from zope.interface import directlyProvides
    >>> from zope.location.interfaces import ILocation
    >>> subcontainer = Container()
    >>> directlyProvides(subcontainer, ILocation)
    >>> subcontainer.__parent__ = container
    >>> checkObject(subcontainer, 'x', container)
    Traceback (most recent call last):
    TypeError: Cannot add an object to itself or its children.
