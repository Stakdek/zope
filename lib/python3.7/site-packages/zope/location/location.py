##############################################################################
#
# Copyright (c) 2003-2009 Zope Foundation and Contributors.
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
"""Location support
"""
__docformat__ = 'restructuredtext'

from zope.interface import implementer
from zope.proxy import ProxyBase
from zope.proxy import getProxiedObject
from zope.proxy import non_overridable
from zope.proxy.decorator import DecoratorSpecificationDescriptor

from zope.location.interfaces import ILocation

@implementer(ILocation)
class Location(object):
    """Mix-in that implements ILocation.

    It provides the `__parent__` and `__name__` attributes.
    """

    __parent__ = None
    __name__ = None


def locate(obj, parent, name=None):
    """Update a location's coordinates."""
    obj.__parent__ = parent
    obj.__name__ = name


def located(obj, parent, name=None):
    """Ensure and return the location of an object.

    Updates the location's coordinates.
    """
    location = ILocation(obj)
    locate(location, parent, name)
    return location


def LocationIterator(object):
    """Iterate over an object and all of its parents."""
    while object is not None:
        yield object
        object = getattr(object, '__parent__', None)


def inside(l1, l2):
    """Test whether l1 is a successor of l2.

    l1 is a successor of l2 if l2 is in the chain of parents of l1 or l2
    is l1.

    """
    while l1 is not None:
        if l1 is l2:
            return True
        l1 = getattr(l1, '__parent__', None)
    return False

class ClassAndInstanceDescr(object):

    def __init__(self, *args):
        self.funcs = args

    def __get__(self, inst, cls):
        if inst is None:
            return self.funcs[1](cls)
        return self.funcs[0](inst)


@implementer(ILocation)
class LocationProxy(ProxyBase):
    """Location-object proxy

    This is a non-picklable proxy that can be put around objects that
    don't implement `ILocation`.
    """
    __slots__ = ('__parent__', '__name__')
    __safe_for_unpickling__ = True

    __doc__ = ClassAndInstanceDescr(
        lambda inst: getProxiedObject(inst).__doc__,
        lambda cls, __doc__ = __doc__: __doc__,
        )

    def __new__(self, ob, container=None, name=None):
        return ProxyBase.__new__(self, ob)

    def __init__(self, ob, container=None, name=None):
        ProxyBase.__init__(self, ob)
        self.__parent__ = container
        self.__name__ = name

    def __getattribute__(self, name):
        if name in LocationProxy.__dict__:
            return object.__getattribute__(self, name)
        return ProxyBase.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in self.__slots__ + getattr(ProxyBase, '__slots__', ()):
            #('_wrapped', '__parent__', '__name__'):
            try:
                return object.__setattr__(self, name, value)
            except TypeError: #pragma NO COVER C Optimization
                return ProxyBase.__setattr__(self, name, value)
        return ProxyBase.__setattr__(self, name, value)

    @non_overridable
    def __reduce__(self, proto=None):
        raise TypeError("Not picklable")
    __reduce_ex__ = __reduce__

    __providedBy__ = DecoratorSpecificationDescriptor()
