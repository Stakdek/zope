##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Locale Inheritance Support

This module provides support for locale inheritance.

Note: In many respects this is similar to Zope 2's acquisition model, since
locale inheritance is not inheritance in the programming sense.
"""
__docformat__ = 'restructuredtext'

from zope.deprecation import deprecate

from zope.interface import implementer
from zope.i18n.interfaces.locales import \
     ILocaleInheritance, IAttributeInheritance, IDictionaryInheritance

class NoParentException(AttributeError):
    pass

@implementer(ILocaleInheritance)
class Inheritance(object):
    """A simple base version of locale inheritance.

    This object contains some shared code amongst the various
    'ILocaleInheritance' implementations.
    """


    # See zope.i18n.interfaces.locales.ILocaleInheritance
    __parent__ = None

    # See zope.i18n.interfaces.locales.ILocaleInheritance
    __name__ = None

    def getInheritedSelf(self):
        """See zope.i18n.interfaces.locales.ILocaleInheritance"""
        if self.__parent__ is None:
            raise NoParentException('No parent was specified.')
        parent = self.__parent__.getInheritedSelf()
        if isinstance(parent, dict):
            return parent[self.__name__]
        return getattr(parent, self.__name__)


@implementer(IAttributeInheritance)
class AttributeInheritance(Inheritance):
    r"""Implementation of locale inheritance for attributes.

    Example::

      >>> from zope.i18n.locales.tests.test_docstrings import \
      ...     LocaleInheritanceStub

      >>> root = LocaleInheritanceStub()
      >>> root.data = 'value'
      >>> root.attr = 'bar value'
      >>> root.data2 = AttributeInheritance()
      >>> root.data2.attr = 'value2'

      >>> locale = LocaleInheritanceStub(root)
      >>> locale.attr = 'foo value'
      >>> locale.data2 = AttributeInheritance()

    Here is an attribute lookup directly from the locale::

      >>> locale.data
      'value'
      >>> locale.attr
      'foo value'

    ... however, we can also have any amount of nesting::

      >>> locale.data2.attr
      'value2'

    Once we have looked up a particular attribute, it should be cached,
    i.e. exist in the dictionary of this inheritance object::

      >>> 'attr' in locale.data2.__dict__
      True
      >>> locale.data2.__dict__['attr']
      'value2'

    Make sure that None can be assigned as value as well::

      >>> locale.data2.attr = None
      >>> locale.data2.attr is None
      True
    """


    def __setattr__(self, name, value):
        """See zope.i18n.interfaces.locales.ILocaleInheritance"""
        # If we have a value that can also inherit data from other locales, we
        # set its parent and name, so that we know how to get to it.
        if (ILocaleInheritance.providedBy(value) and
                not name.startswith('__')):
            value.__parent__ = self
            value.__name__ = name
        super(AttributeInheritance, self).__setattr__(name, value)


    def __getattr__(self, name):
        """See zope.i18n.interfaces.locales.ILocaleInheritance"""
        try:
            selfUp = self.getInheritedSelf()
        except NoParentException:
            # There was simply no parent anymore, so let's raise an error
            # for good
            raise AttributeError("'%s' object (or any of its parents) has no "
                                 "attribute '%s'" % (self.__class__.__name__,
                                                     name))
        else:
            value = getattr(selfUp, name)
            # Since a locale hierarchy never changes after startup, we can
            # cache the value locally, saving the time to ever look it up
            # again.
            # Note that we cannot use the normal setattr function, since
            # __setattr__ of this class tries to assign a parent and name,
            # which we do not want to override.
            super(AttributeInheritance, self).__setattr__(name, value)
            return value



@implementer(IDictionaryInheritance)
class InheritingDictionary(Inheritance, dict):
    """Implementation of a dictionary that can also inherit values.

    Example::

      >>> from zope.i18n.locales.tests.test_docstrings import \\
      ...     LocaleInheritanceStub

      >>> root = LocaleInheritanceStub()
      >>> root.data = InheritingDictionary({1: 'one', 2: 'two', 3: 'three'})
      >>> root.data2 = AttributeInheritance()
      >>> root.data2.dict = InheritingDictionary({1: 'i', 2: 'ii', 3: 'iii'})

      >>> locale = LocaleInheritanceStub(root)
      >>> locale.data = InheritingDictionary({1: 'eins'})
      >>> locale.data2 = AttributeInheritance()
      >>> locale.data2.dict = InheritingDictionary({1: 'I'})

    Here is a dictionary lookup directly from the locale::

      >>> locale.data[1]
      'eins'
      >>> locale.data[2]
      'two'

    ... however, we can also have any amount of nesting::

      >>> locale.data2.dict[1]
      'I'
      >>> locale.data2.dict[2]
      'ii'

    We also have to overwrite `get`, `keys` and `items` since we want
    to make sure that all upper locales are consulted before returning the
    default or to construct the list of elements, respectively::

      >>> locale.data2.dict.get(2)
      'ii'
      >>> locale.data2.dict.get(4) is None
      True
      >>> sorted(locale.data.keys())
      [1, 2, 3]
      >>> sorted(locale.data.items())
      [(1, 'eins'), (2, 'two'), (3, 'three')]

    We also override `values`::

      >>> sorted(locale.data.values())
      ['eins', 'three', 'two']

    Historically, `value` was a synonym of this method; it is still
    available, but is deprecated::

      >>> import warnings
      >>> with warnings.catch_warnings(record=True) as w:
      ...     sorted(locale.data.value())
      ['eins', 'three', 'two']
      >>> print(w[0].message)
      `value` is a deprecated synonym for `values`
    """


    def __setitem__(self, name, value):
        """See zope.i18n.interfaces.locales.ILocaleInheritance"""
        if ILocaleInheritance.providedBy(value):
            value.__parent__ = self
            value.__name__ = name
        super(InheritingDictionary, self).__setitem__(name, value)

    def __getitem__(self, name):
        """See zope.i18n.interfaces.locales.ILocaleInheritance"""
        if name not in self:
            try:
                selfUp = self.getInheritedSelf()
            except NoParentException:
                pass
            else:
                return selfUp.__getitem__(name)
        return super(InheritingDictionary, self).__getitem__(name)

    def get(self, name, default=None):
        """See zope.i18n.interfaces.locales.ILocaleInheritance"""
        try:
            return self[name]
        except KeyError:
            return default

    def _make_reified_inherited_dict(self):
        try:
            d = dict(self.getInheritedSelf())
        except NoParentException:
            d = {}
        d.update(self)
        return d

    def items(self):
        return self._make_reified_inherited_dict().items()

    def keys(self):
        return list(self._make_reified_inherited_dict().keys())

    def values(self):
        return list(self._make_reified_inherited_dict().values())

    value = deprecate("`value` is a deprecated synonym for `values`")(values)
