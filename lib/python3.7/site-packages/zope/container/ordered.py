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
"""Ordered container implementation.
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope.container.interfaces import IOrderedContainer
from zope.interface import implementer
from zope.container.contained import Contained, setitem, uncontained
from zope.container.contained import notifyContainerModified
from zope.container.contained import checkAndConvertName

@implementer(IOrderedContainer)
class OrderedContainer(Persistent, Contained):
    """ `OrderedContainer` maintains entries' order as added and moved.

    >>> oc = OrderedContainer()
    >>> int(IOrderedContainer.providedBy(oc))
    1
    >>> len(oc)
    0
    """
    def __init__(self):

        self._data = PersistentDict()
        self._order = PersistentList()

    def keys(self):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> oc['foo'] = 'bar'
        >>> oc.keys()
        ['foo']
        >>> oc['baz'] = 'quux'
        >>> oc.keys()
        ['foo', 'baz']
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        return self._order[:]

    def __iter__(self):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> oc['foo'] = 'bar'
        >>> oc['baz'] = 'quux'
        >>> [i for i in oc]
        ['foo', 'baz']
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        return iter(self.keys())

    def __getitem__(self, key):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> oc['foo'] = 'bar'
        >>> oc['foo']
        'bar'
        """

        return self._data[key]

    def get(self, key, default=None):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> oc['foo'] = 'bar'
        >>> oc.get('foo')
        'bar'
        >>> oc.get('funky', 'No chance, dude.')
        'No chance, dude.'
        """

        return self._data.get(key, default)

    def values(self):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> oc['foo'] = 'bar'
        >>> oc.values()
        ['bar']
        >>> oc['baz'] = 'quux'
        >>> oc.values()
        ['bar', 'quux']
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        return [self._data[i] for i in self._order]

    def __len__(self):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> int(len(oc) == 0)
        1
        >>> oc['foo'] = 'bar'
        >>> int(len(oc) == 1)
        1
        """

        return len(self._data)

    def items(self):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> oc['foo'] = 'bar'
        >>> oc.items()
        [('foo', 'bar')]
        >>> oc['baz'] = 'quux'
        >>> oc.items()
        [('foo', 'bar'), ('baz', 'quux')]
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        return [(i, self._data[i]) for i in self._order]

    def __contains__(self, key):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> oc['foo'] = 'bar'
        >>> int('foo' in oc)
        1
        >>> int('quux' in oc)
        0
        """

        return key in self._data

    has_key = __contains__

    def _setitemf(self, key, value):
        if key not in self._data:
            self._order.append(key)
        self._data[key] = value

    def __setitem__(self, key, object):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> oc['foo'] = 'bar'
        >>> oc._order
        ['foo']
        >>> oc['baz'] = 'quux'
        >>> oc._order
        ['foo', 'baz']
        >>> int(len(oc._order) == len(oc._data))
        1

        >>> oc['foo'] = 'baz'
        Traceback (most recent call last):
        ...
        KeyError: u'foo'
        >>> oc._order
        ['foo', 'baz']
        """
        # This function creates a lot of events that other code
        # listens to. None of them are fired (notified) though, before
        # _setitemf is called. At that point we need to be sure that
        # we have the key in _order too.
        setitem(self, self._setitemf, key, object)
        return key

    def __delitem__(self, key):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> oc['foo'] = 'bar'
        >>> oc['baz'] = 'quux'
        >>> oc['zork'] = 'grue'
        >>> oc.items()
        [('foo', 'bar'), ('baz', 'quux'), ('zork', 'grue')]
        >>> int(len(oc._order) == len(oc._data))
        1
        >>> del oc['baz']
        >>> oc.items()
        [('foo', 'bar'), ('zork', 'grue')]
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        uncontained(self._data[key], self, key)
        del self._data[key]
        self._order.remove(key)

    def updateOrder(self, order):
        """ See `IOrderedContainer`.

        >>> oc = OrderedContainer()
        >>> oc['foo'] = 'bar'
        >>> oc['baz'] = 'quux'
        >>> oc['zork'] = 'grue'
        >>> oc.keys()
        ['foo', 'baz', 'zork']
        >>> oc.updateOrder(['baz', 'foo', 'zork'])
        >>> oc.keys()
        ['baz', 'foo', 'zork']
        >>> oc.updateOrder(['baz', 'zork', 'foo'])
        >>> oc.keys()
        ['baz', 'zork', 'foo']
        >>> oc.updateOrder(['baz', 'zork', 'foo'])
        >>> oc.keys()
        ['baz', 'zork', 'foo']
        >>> oc.updateOrder(('zork', 'foo', 'baz'))
        >>> oc.keys()
        ['zork', 'foo', 'baz']
        >>> oc.updateOrder(['baz', 'zork'])
        Traceback (most recent call last):
        ...
        ValueError: Incompatible key set.
        >>> oc.updateOrder(['foo', 'bar', 'baz', 'quux'])
        Traceback (most recent call last):
        ...
        ValueError: Incompatible key set.
        >>> oc.updateOrder(1)
        Traceback (most recent call last):
        ...
        TypeError: order must be a tuple or a list.
        >>> oc.updateOrder('bar')
        Traceback (most recent call last):
        ...
        TypeError: order must be a tuple or a list.
        >>> oc.updateOrder(['baz', 'zork', 'quux'])
        Traceback (most recent call last):
        ...
        ValueError: Incompatible key set.
        >>> del oc['baz']
        >>> del oc['zork']
        >>> del oc['foo']
        >>> len(oc)
        0
        """

        if not isinstance(order, (list, tuple)):
            raise TypeError('order must be a tuple or a list.')

        if len(order) != len(self._order):
            raise ValueError("Incompatible key set.")

        order = [checkAndConvertName(x) for x in order]

        if frozenset(order) != frozenset(self._order):
            raise ValueError("Incompatible key set.")

        if order == self._order:
            return

        self._order[:] = order

        notifyContainerModified(self)
