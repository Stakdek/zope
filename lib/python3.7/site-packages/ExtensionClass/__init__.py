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
"""ExtensionClass

Extension Class exists to support types derived from the old ExtensionType
meta-class that preceeded Python 2.2 and new-style classes.

As a meta-class, ExtensionClass provides the following features:

- Support for a class initialiser:

  >>> from ExtensionClass import ExtensionClass, Base

  >>> class C(Base):
  ...   def __class_init__(self):
  ...      print('class init called')
  ...      print(self.__name__)
  ...   def bar(self):
  ...      return 'bar called'
  class init called
  C
  >>> c = C()
  >>> int(c.__class__ is C)
  1
  >>> int(c.__class__ is type(c))
  1

- Making sure that every instance of the meta-class has Base as a base class:

  >>> X = ExtensionClass('X', (), {})
  >>> Base in X.__mro__
  1

- Provide an inheritedAttribute method for looking up attributes in
  base classes:

  >>> class C2(C):
  ...   def bar(*a):
  ...      return C2.inheritedAttribute('bar')(*a), 42
  class init called
  C2
  >>> o = C2()
  >>> o.bar()
  ('bar called', 42)

  This is for compatability with old code. New code should use super
  instead.

The base class, Base, exists mainly to support the __of__ protocol.
The __of__ protocol is similar to __get__ except that __of__ is called
when an implementor is retrieved from an instance as well as from a
class:

>>> class O(Base):
...   def __of__(*a):
...      return a

>>> o1 = O()
>>> o2 = O()
>>> C.o1 = o1
>>> c.o2 = o2
>>> c.o1 == (o1, c)
1
>>> C.o1 == o1
1
>>> int(c.o2 == (o2, c))
1

We accomplish this by making a class that implements __of__ a
descriptor and treating all descriptor ExtensionClasses this way. That
is, if an extension class is a descriptor, it's __get__ method will be
called even when it is retrieved from an instance.

>>> class O(Base):
...   def __get__(*a):
...      return a
...
>>> o1 = O()
>>> o2 = O()
>>> C.o1 = o1
>>> c.o2 = o2
>>> int(c.o1 == (o1, c, type(c)))
1
>>> int(C.o1 == (o1, None, type(c)))
1
>>> int(c.o2 == (o2, c, type(c)))
1
"""

import inspect
import os
import platform
import sys

if sys.version_info > (3, ):
    import copyreg as copy_reg
else: # pragma: no cover
    import copy_reg

_IS_PYPY = platform.python_implementation() == 'PyPy'
_IS_PURE = 'PURE_PYTHON' in os.environ
C_EXTENSION = not (_IS_PYPY or _IS_PURE)


def of_get(self, inst, type_=None):
    if not issubclass(type(type_), ExtensionClass):
        return self
    if inst is not None:
        return self.__of__(inst)
    return self


def pmc_init_of(cls):
    # set up __get__ if __of__ is implemented
    of = getattr(cls, '__of__', None)
    if of is not None:
        cls.__get__ = of_get
    else:
        get = getattr(cls, '__get__', None)
        if (get is not None and
           (get is of_get or getattr(get, '__func__', None) is of_get)):
            del cls.__get__


_Base = type('dummy', (), {})
_NoInstanceDictionaryBase = type('dummy', (), {})


def _add_classic_mro(mro, cls):
    if cls not in mro:
        mro.append(cls)
    for base in cls.__bases__:
        if base not in mro:
            mro.append(base)
            _add_classic_mro(mro, base)


class ExtensionClass(type):

    def __new__(cls, name, bases=(), attrs=None):
        attrs = {} if attrs is None else attrs
        # Make sure we have an ExtensionClass instance as a base
        if (name != 'Base' and
           not any(isinstance(b, ExtensionClass) for b in bases)):
            bases += (_Base,)
        if ('__slots__' not in attrs and
           any(issubclass(b, _NoInstanceDictionaryBase) for b in bases)):
            attrs['__slots__'] = []

        cls = type.__new__(cls, name, bases, attrs)

        # Inherit docstring
        if not cls.__doc__:
            cls.__doc__ = super(cls, cls).__doc__

        # set up __get__ if __of__ is implemented
        pmc_init_of(cls)

        # call class init method
        if hasattr(cls, '__class_init__'):
            class_init = cls.__class_init__
            if hasattr(class_init, '__func__'):
                class_init = class_init.__func__
            class_init(cls)
        return cls

    def __basicnew__(self):
        """Create a new empty object"""
        return self.__new__(self)


    def mro(self):
        """Compute an mro using the 'encapsulated base' scheme"""
        mro = [self]
        for base in self.__bases__:
            if hasattr(base, '__mro__'):
                for c in base.__mro__:
                    if c in (_Base, _NoInstanceDictionaryBase, object):
                        continue
                    if c in mro:
                        continue
                    mro.append(c)
            else: # pragma: no cover (python 2 only)
                _add_classic_mro(mro, base)

        if _NoInstanceDictionaryBase in self.__bases__:
            mro.append(_NoInstanceDictionaryBase)
        elif self.__name__ != 'Base':
            mro.append(_Base)
        mro.append(object)
        return mro

    def inheritedAttribute(self, name):
        """Look up an inherited attribute"""
        return getattr(super(self, self), name)

    def __setattr__(self, name, value):
        if name not in ('__get__', '__doc__', '__of__'):
            if (name.startswith('__') and name.endswith('__') and
               name.count('_') == 4):
                raise TypeError(
                    "can't set attributes of built-in/extension type '%s.%s' "
                    "if the attribute name begins and ends with __ and "
                    "contains only 4 _ characters" %
                    (self.__module__, self.__name__))
        return type.__setattr__(self, name, value)


# Base and object are always moved to the last two positions
# in a subclasses mro, no matter how they are declared in the
# hierarchy. This means the Base_* methods effectively don't have
# to care or worry about using super(): it's always object.

def Base_getattro(self, name):
    descr = None

    for base in type(self).__mro__:
        if name in base.__dict__:
            descr = base.__dict__[name]
            break

    if descr is not None and inspect.isdatadescriptor(descr):
        return descr.__get__(self, type(self))

    try:
        # Don't do self.__dict__ otherwise you get recursion.
        inst_dict = object.__getattribute__(self, '__dict__')
    except AttributeError:
        pass
    else:
        if name in inst_dict:
            descr = inst_dict[name]
            # If the tp_descr_get of res is of_get, then call it.
            if name == '__parent__' or not isinstance(descr, Base):
                return descr

    if descr is not None:
        descr_get = getattr(descr, '__get__', None)
        if descr_get is None:
            return descr

        return descr_get(self, type(self))

    raise AttributeError(
            "'%.50s' object has not attribute '%s'",
            type(self).__name__, name)


def _slotnames(self):
    slotnames = copy_reg._slotnames(type(self))
    return [x for x in slotnames
            if not x.startswith('_p_') and
            not x.startswith('_v_')]


def Base__getstate__(self):
    idict = getattr(self, '__dict__', None)
    slotnames = _slotnames(self)
    if idict is not None:
        d = dict([x for x in idict.items()
                  if not x[0].startswith('_p_') and
                  not x[0].startswith('_v_')])
    else:
        d = None
    if slotnames:
        s = {}
        for slotname in slotnames:
            value = getattr(self, slotname, self)
            if value is not self:
                s[slotname] = value
        return d, s
    return d


def Base__setstate__(self, state):
    """ See IPersistent.
    """
    try:
        inst_dict, slots = state
    except:
        inst_dict, slots = state, ()
    idict = getattr(self, '__dict__', None)
    if inst_dict is not None:
        if idict is None:
            raise TypeError('No instance dict')  # pragma no cover
        idict.clear()
        idict.update(inst_dict)
    slotnames = _slotnames(self)
    if slotnames:
        for k, v in slots.items():
            setattr(self, k, v)


def Base__reduce__(self):
    gna = getattr(self, '__getnewargs__', lambda: ())
    return (copy_reg.__newobj__,
            (type(self),) + gna(), self.__getstate__())


def Base__new__(cls, *args, **kw):
    return object.__new__(cls)


Base = ExtensionClass("Base", (object, ), {
    '__slots__': (),
    '__getattribute__': Base_getattro,
    '__getstate__': Base__getstate__,
    '__setstate__': Base__setstate__,
    '__reduce__': Base__reduce__,
    '__new__': Base__new__,
})

_Base = Base


class NoInstanceDictionaryBase(Base):
    __slots__ = ()


_NoInstanceDictionaryBase = NoInstanceDictionaryBase


if C_EXTENSION:  # pragma no cover
    from ._ExtensionClass import *  # NOQA

# We always want to get the CAPI2 value (if possible) so that
# MethodObject and anything else using the PyExtensionClass_Export
# macro from ExtensionClass.h doesn't break with an AttributeError
try:
    from ._ExtensionClass import CAPI2
except ImportError: # pragma: no cover
    pass
