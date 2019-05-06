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

from ExtensionClass import Base


class Record(Base):
    """Simple Record Types"""

    __allow_access_to_unprotected_subobjects__ = 1
    __record_schema__ = None
    __slots__ = ('__data__', '__schema__')

    def __new__(cls, data=None, parent=None):
        obj = Base.__new__(cls)
        obj.__setstate__(data)
        return obj

    def __getstate__(self):
        return self.__data__

    def __setstate__(self, data):
        cls_schema = type(self).__record_schema__
        if cls_schema is None:
            cls_schema = {}
        self.__schema__ = schema = cls_schema
        len_schema = len(schema)
        if data is None:
            self.__data__ = (None, ) * len_schema
            return
        if isinstance(data, dict):
            self.__data__ = (None, ) * len_schema
            for k, v in data.items():
                if k in schema:
                    self[k] = v
        elif len(data) == len_schema:
            self.__data__ = tuple(data)
        else:
            self.__data__ = (None, ) * len_schema
            maxlength = min(len(data), len_schema)
            for i in range(maxlength):
                self[i] = data[i]

    def __getitem__(self, key):
        if isinstance(key, int):
            pos = key
        else:
            pos = self.__schema__[key]
        return self.__data__[pos]

    def __getattr__(self, key):
        if key in self.__slots__:
            return object.__getattribute__(self, key)
        try:
            return self.__getitem__(key)
        except KeyError:
            raise AttributeError(key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            pos = key
        else:
            try:
                pos = self.__schema__[key]
            except IndexError:
                raise TypeError('invalid record schema')
        old = self.__data__
        self.__data__ = old[:pos] + (value, ) + old[pos + 1:]

    def __setattr__(self, key, value):
        if key in self.__slots__:
            object.__setattr__(self, key, value)
        else:
            try:
                self.__setitem__(key, value)
            except KeyError:
                raise AttributeError(key)

    def __delattr__(self, key):
        self[key] = None

    def __delitem__(self, key):
        if isinstance(key, int):
            raise TypeError('cannot delete record items')
        self[key] = None

    def __contains__(self, key):
        return key in self.__schema__

    def __getslice__(self, i, j):
        raise TypeError('Record objects do not support slicing')

    def __setslice__(self, i, j, sequence):
        raise TypeError('Record objects do not support slicing')

    def __delslice__(self, i, j):
        raise TypeError('Record objects do not support slicing')

    def __add__(self, other):
        raise TypeError('Record objects do not support concatenation')

    def __mul__(self, other):
        raise TypeError('Record objects do not support repetition')

    def __len__(self):
        return len(self.__schema__)

    def __hash__(self):
        return id(self)

    def __lt__(self, other):
        if isinstance(other, Record):
            return self.__data__ < other.__data__
        return id(self) < id(other)

    def __le__(self, other):
        return self < other or self == other

    def __eq__(self, other):
        if isinstance(other, Record):
            return self.__data__ == other.__data__
        return id(self) == id(other)

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        return not(self <= other)

    def __ge__(self, other):
        return not(self < other)
