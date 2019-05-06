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

from zope.proxy import AbstractPyProxyBase

_MARKER = object()

from persistent import Persistent

def _special_name(name):
    "attribute names we delegate to Persistent for"
    return (name.startswith('_Persistent')
            or name.startswith('_p_')
            or name.startswith('_v_')
            or name in PyContainedProxyBase.__slots__)

class PyContainedProxyBase(AbstractPyProxyBase, Persistent):
    """Persistent proxy
    """
    __slots__ = ('_wrapped', '__parent__', '__name__', '__weakref__')

    def __new__(cls, obj):
        inst = super(PyContainedProxyBase, cls).__new__(cls, obj)
        inst.__parent__ = None
        inst.__name__ = None
        return inst

    def __init__(self, obj):
        super(PyContainedProxyBase, self).__init__(obj)
        self.__parent__ = None
        self.__name__ = None

    def __reduce__(self):
        return (type(self),
                (self._wrapped,),
                (self.__parent__, self.__name__))

    def __reduce_ex__(self, protocol):
        return self.__reduce__()

    def __setstate__(self, state):
        object.__setattr__(self, '__parent__', state[0])
        object.__setattr__(self, '__name__', state[1])

    def __getstate__(self):
        return (self.__parent__, self.__name__)

    def __getnewargs__(self):
        return self._wrapped,

    def _p_invalidate(self):
        # The superclass wants to clear the __dict__, which
        # we don't have, but we would otherwise delegate
        # to the wrapped object, which is clearly wrong in this case.
        # This method is a copy of the super method with
        # clearing the dict omitted
        if self._Persistent__jar is not None:
            if self._Persistent__flags is not None:
                self._Persistent__flags = None
            try:
                object.__getattribute__(self, '__dict__').clear()
            except AttributeError:
                pass

    # Attribute protocol
    def __getattribute__(self, name):
        if _special_name(name):
            # Our own attribute names need to go to Persistent so we get
            # activated
            return Persistent.__getattribute__(self, name)

        if name in ('__reduce__', '__reduce_ex__', '__getstate__', '__setstate__', '__getnewargs__'):
            return object.__getattribute__(self, name)

        return super(PyContainedProxyBase,self).__getattribute__(name)

    def __setattr__(self, name, value):
        if _special_name(name):
            # Our own attribute names need to go directly to Persistent
            # so that _p_changed gets set, in addition to the _p values themselves
            return Persistent.__setattr__(self, name, value)

        return super(PyContainedProxyBase, self).__setattr__(name, value)


def py_getProxiedObject(obj):
    if isinstance(obj, PyContainedProxyBase):
        return obj._wrapped
    return obj


def py_setProxiedObject(obj, new_value):
    if not isinstance(obj, PyContainedProxyBase):
        raise TypeError('Not a proxy')
    old, obj._wrapped = obj._wrapped, new_value
    return old
