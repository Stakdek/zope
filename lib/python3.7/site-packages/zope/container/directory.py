##############################################################################
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""File-system representation adapters for containers

This module includes two adapters (adapter factories, really) for
providing a file-system representation for containers:

`noop`
  Factory that "adapts" `IContainer` to `IWriteDirectory`.
  This is a lie, since it just returns the original object.

`Cloner`
  An `IDirectoryFactory` adapter that just clones the original object.
"""
__docformat__ = 'restructuredtext'

from zope.interface import implementer

from zope.component.interfaces import ISite
from zope.container.folder import Folder
from zope.security.proxy import removeSecurityProxy
import zope.filerepresentation.interfaces

from six.moves import map


MARKER = object()

def noop(container):
    """Adapt an `IContainer` to an `IWriteDirectory` by just returning it

    This "works" because `IContainer` and `IWriteDirectory` have the same
    methods, however, the output doesn't actually implement `IWriteDirectory`.
    """
    return container


@implementer(zope.filerepresentation.interfaces.IDirectoryFactory)
class Cloner(object):
    """
    `IContainer` to
    :class:`zope.filerepresentation.interfaces.IDirectoryFactory` adapter
    that clones.

    This adapter provides a factory that creates a new empty container
    of the same class as it's context.
    """
    def __init__(self, context):
        self.context = context

    def __call__(self, name):

        # We remove the security proxy so we can actually call the
        # class and return an unproxied new object.  (We can't use a
        # trusted adapter, because the result must be unproxied.)  By
        # registering this adapter, one effectively gives permission
        # to clone the class.  Don't use this for classes that have
        # exciting side effects as a result of instantiation. :)

        return removeSecurityProxy(self.context).__class__()


class RootDirectoryFactory(object):

    def __init__(self, context):
        pass

    def __call__(self, name):
        return Folder()


class ReadDirectory(object):
    """Adapter to provide a file-system rendition of folders."""

    def __init__(self, context):
        self.context = context

    def keys(self):
        keys = self.context.keys()
        if ISite.providedBy(self.context):
            return list(keys) + ['++etc++site']
        return keys

    def get(self, key, default=None):
        if key == '++etc++site' and ISite.providedBy(self.context):
            return self.context.getSiteManager()
        return self.context.get(key, default)

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, key):
        v = self.get(key, MARKER)
        if v is MARKER:
            raise KeyError(key)
        return v

    def values(self):
        return map(self.get, self.keys())

    def __len__(self):
        l = len(self.context)
        if ISite.providedBy(self.context):
            l += 1
        return l

    def items(self):
        get = self.get
        return [(key, get(key)) for key in self.keys()]

    def __contains__(self, key):
        return self.get(key) is not None
