##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""Traversing test fixtures
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.location.traversing \
    import LocationPhysicallyLocatable, RootPhysicallyLocatable
from zope.location.interfaces import IContained, ILocationInfo, IRoot
from zope.traversing.interfaces import ITraversable, ITraverser
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.adapters import Traverser
from zope.traversing.browser import SiteAbsoluteURL, AbsoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.namespace import etc

@zope.interface.implementer(IContained)
class Contained(object):
    __parent__ = None
    __name__ = None

@zope.interface.implementer(IContained)
class ContainedProxy(object):
    __parent__ = None
    __name__ = None
    __obj__ = None

    def __init__(self, obj):
        self.__obj__ = obj

    def __getattr__(self, name):
        return getattr(self.__obj__, name)

    def __setattr__(self, name, value):
        if name in ['__parent__', '__name__', '__obj__']:
            self.__dict__[name] = value
            return
        setattr(self.__obj__, name, value) # pragma: no cover

    def __eq__(self, value):
        return self.__obj__ == value


def contained(obj, root, name=None):
    if not IContained.providedBy(obj):
        obj = ContainedProxy(obj)
    obj.__parent__ = root
    obj.__name__ = name
    return obj

# BBB: Kept for backward-compatibility, in case some package depends on it.
def setUp(): # pragma: no cover
    zope.component.provideAdapter(Traverser, (None,), ITraverser)
    zope.component.provideAdapter(DefaultTraversable, (None,), ITraversable)
    zope.component.provideAdapter(LocationPhysicallyLocatable,
                                  (None,), ILocationInfo)
    zope.component.provideAdapter(RootPhysicallyLocatable,
                                  (IRoot,), ILocationInfo)
    # set up the 'etc' namespace
    zope.component.provideAdapter(etc, (None,), ITraversable, name="etc")
    zope.component.provideAdapter(etc, (None, None), ITraversable, name="etc")

    browserView(None, "absolute_url", AbsoluteURL)
    browserView(IRoot, "absolute_url", SiteAbsoluteURL)

    browserView(None, '', AbsoluteURL, providing=IAbsoluteURL)
    browserView(IRoot, '', SiteAbsoluteURL, providing=IAbsoluteURL)


def browserView(for_, name, factory, providing=zope.interface.Interface):
    zope.component.provideAdapter(factory, (for_, IDefaultBrowserLayer),
                                  providing, name=name)


def browserResource(name, factory, providing=zope.interface.Interface):
    zope.component.provideAdapter(factory, (IDefaultBrowserLayer,),
                                  providing, name=name)
