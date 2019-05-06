##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Annotation factory helper
"""
import zope.component
import zope.interface
import zope.location.location
import zope.location.interfaces
import zope.proxy

import zope.annotation.interfaces


def factory(factory, key=None):
    """Adapter factory to help create annotations easily.
    """
    # if no key is provided,
    # we'll determine the unique key based on the factory's dotted name
    if key is None:
        key = factory.__module__ + '.' + factory.__name__

    adapts = zope.component.adaptedBy(factory)
    if adapts is None:
        raise TypeError("Missing 'zope.component.adapts' on annotation")

    @zope.component.adapter(list(adapts)[0])
    @zope.interface.implementer(list(zope.component.implementedBy(factory))[0])
    def getAnnotation(context):
        annotations = zope.annotation.interfaces.IAnnotations(context)
        try:
            result = annotations[key]
        except KeyError:
            result = factory()
            annotations[key] = result
            if zope.location.interfaces.ILocation.providedBy(result):
                zope.location.location.locate(result,
                        zope.proxy.removeAllProxies(context), key)
        if not (zope.location.interfaces.ILocation.providedBy(result)
                and result.__parent__ is context
                and result.__name__ == key):
            result = zope.location.location.LocationProxy(result, context, key)
        return result

    # Convention to make adapter introspectable, used by apidoc
    getAnnotation.factory = factory
    return getAnnotation
