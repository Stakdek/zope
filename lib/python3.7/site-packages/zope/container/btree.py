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
"""This module provides a sample btree container implementation.
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
from BTrees.OOBTree import OOBTree
from BTrees.Length import Length

from zope.container.interfaces import IBTreeContainer
from zope.container.contained import Contained, setitem, uncontained
from zope.interface import implementer
from zope.cachedescriptors.property import Lazy


@implementer(IBTreeContainer)
class BTreeContainer(Contained, Persistent):
    """OOBTree-based container"""

    def __init__(self):
        # We keep the previous attribute to store the data
        # for backward compatibility
        self._SampleContainer__data = self._newContainerData()
        self.__len = Length()

    def _newContainerData(self):
        """Construct an item-data container

        Subclasses should override this if they want different data.

        The value returned is a mapping object that also has get,
        has_key, keys, items, and values methods.
        The default implementation uses an OOBTree.
        """
        return OOBTree()

    def __contains__(self, key):
        """See interface IReadContainer
        """
        return key in self._SampleContainer__data

    @Lazy
    def _BTreeContainer__len(self):
        l = Length()
        ol = len(self._SampleContainer__data)
        if ol > 0:
            l.change(ol)
        self._p_changed = True
        return l

    def __len__(self):
        return self.__len()

    def _setitemf(self, key, value):
        # make sure our lazy property gets set
        l = self.__len
        self._SampleContainer__data[key] = value
        l.change(1)

    def __iter__(self):
        return iter(self._SampleContainer__data)

    def __getitem__(self, key):
        '''See interface `IReadContainer`'''
        return self._SampleContainer__data[key]

    def get(self, key, default=None):
        '''See interface `IReadContainer`'''
        return self._SampleContainer__data.get(key, default)

    def __setitem__(self, key, value):
        setitem(self, self._setitemf, key, value)

    def __delitem__(self, key):
        # make sure our lazy property gets set
        l = self.__len
        item = self._SampleContainer__data[key]
        del self._SampleContainer__data[key]
        l.change(-1)
        uncontained(item, self, key)

    has_key = __contains__

    def items(self, key=None):
        return self._SampleContainer__data.items(key)

    def keys(self, key=None):
        return self._SampleContainer__data.keys(key)

    def values(self, key=None):
        return self._SampleContainer__data.values(key)
