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
"""Attribute Annotations implementation"""
import logging

try:
    from collections.abc import MutableMapping as DictMixin
except ImportError:
    # Python 2
    from collections import MutableMapping as DictMixin

try:
    from BTrees.OOBTree import OOBTree as _STORAGE
except ImportError: # pragma: no cover
    logging.getLogger(__name__).warning(
        'BTrees not available: falling back to dict for attribute storage')
    _STORAGE = dict

from zope import component, interface
from zope.annotation import interfaces


_EMPTY_STORAGE = _STORAGE()

@interface.implementer(interfaces.IAnnotations)
@component.adapter(interfaces.IAttributeAnnotatable)
class AttributeAnnotations(DictMixin):
    """Store annotations on an object

    Store annotations in the `__annotations__` attribute on a
    `IAttributeAnnotatable` object.
    """

    # Yes, there's a lot of repetition of the `getattr` call,
    # but that turns out to be the most efficient for the ways
    # instances are typically used without sacrificing any semantics.
    # See https://github.com/zopefoundation/zope.annotation/issues/8
    # for a discussion of alternatives (which included functools.partial,
    # a closure, capturing the annotations in __init__, and versions
    # with getattr and exceptions).

    def __init__(self, obj, context=None):
        self.obj = obj

    @property
    def __parent__(self):
        return self.obj

    def __bool__(self):
        return bool(getattr(self.obj, '__annotations__', 0))

    __nonzero__ = __bool__

    def get(self, key, default=None):
        """See zope.annotation.interfaces.IAnnotations"""
        annotations = getattr(self.obj, '__annotations__', _EMPTY_STORAGE)
        return annotations.get(key, default)

    def __getitem__(self, key):
        annotations = getattr(self.obj, '__annotations__', _EMPTY_STORAGE)
        return annotations[key]

    def keys(self):
        annotations = getattr(self.obj, '__annotations__', _EMPTY_STORAGE)
        return annotations.keys()

    def __iter__(self):
        annotations = getattr(self.obj, '__annotations__', _EMPTY_STORAGE)
        return iter(annotations)

    def __len__(self):
        annotations = getattr(self.obj, '__annotations__', _EMPTY_STORAGE)
        return len(annotations)

    def __setitem__(self, key, value):
        """See zope.annotation.interfaces.IAnnotations"""
        try:
            annotations = self.obj.__annotations__
        except AttributeError:
            annotations = self.obj.__annotations__ = _STORAGE()

        annotations[key] = value

    def __delitem__(self, key):
        """See zope.app.interfaces.annotation.IAnnotations"""
        try:
            annotation = self.obj.__annotations__
        except AttributeError:
            raise KeyError(key)

        del annotation[key]
