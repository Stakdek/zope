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
"""Classes to support implenting IContained
"""
__docformat__ = 'restructuredtext'

from zope.interface import implementer

from zope.location.interfaces import ILocationInfo
from zope.location.interfaces import IRoot
from zope.location.interfaces import ISite # zope.component, if present


@implementer(ILocationInfo)
class LocationPhysicallyLocatable(object):
    """Provide location information for location objects
    """
    def __init__(self, context):
        self.context = context

    def getRoot(self):
        """See ILocationInfo.
        """
        context = self.context
        max = 9999
        while context is not None:
            if IRoot.providedBy(context):
                return context
            context = context.__parent__
            max -= 1
            if max < 1:
                raise TypeError("Maximum location depth exceeded, "
                                "probably due to a a location cycle.")

        raise TypeError("Not enough context to determine location root")

    def getPath(self):
        """See ILocationInfo.
        """
        path = []
        context = self.context
        max = 9999
        while context is not None:
            if IRoot.providedBy(context):
                if path:
                    path.append('')
                    path.reverse()
                    return u'/'.join(path)
                return u'/'
            path.append(context.__name__)
            context = context.__parent__
            max -= 1
            if max < 1:
                raise TypeError("Maximum location depth exceeded, "
                                "probably due to a a location cycle.")

        raise TypeError("Not enough context to determine location root")

    def getParent(self):
        """See ILocationInfo.
        """
        parent = getattr(self.context, '__parent__', None)
        if parent is not None:
            return parent

        raise TypeError('Not enough context information to get parent',
                        self.context)

    def getParents(self):
        """See ILocationInfo.
        """
        # XXX Merge this implementation with getPath. This was refactored
        # from zope.traversing.
        parents = []
        w = self.context
        while 1:
            w = getattr(w, '__parent__', None)
            if w is None:
                break
            parents.append(w)

        if parents and IRoot.providedBy(parents[-1]):
            return parents

        raise TypeError("Not enough context information to get all parents")

    def getName(self):
        """See ILocationInfo
        """
        return self.context.__name__

    def getNearestSite(self):
        """See ILocationInfo
        """
        if ISite.providedBy(self.context):
            return self.context
        for parent in self.getParents():
            if ISite.providedBy(parent):
                return parent
        return self.getRoot()

@implementer(ILocationInfo)
class RootPhysicallyLocatable(object):
    """Provide location information for the root object

    This adapter is very simple, because there's no places to search
    for parents and nearest sites, so we are only working with context
    object, knowing that its the root object already.
    """
    def __init__(self, context):
        self.context = context

    def getRoot(self):
        """See ILocationInfo
        """
        return self.context

    def getPath(self):
        """See ILocationInfo
        """
        return u'/'

    def getParent(self):
        """See ILocationInfo.
        """
        return None

    def getParents(self):
        """See ILocationInfo
        """
        return []

    def getName(self):
        """See ILocationInfo
        """
        return u''

    def getNearestSite(self):
        """See ILocationInfo
        """
        return self.context
