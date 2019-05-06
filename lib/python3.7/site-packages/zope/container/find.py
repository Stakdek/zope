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
"""Find Support
"""
__docformat__ = 'restructuredtext'

from zope.interface import implementer
from .interfaces import IFind, IIdFindFilter, IObjectFindFilter
from .interfaces import IReadContainer

@implementer(IFind)
class FindAdapter(object):
    """Adapts :class:`zope.container.interfaces.IReadContainer`"""

    __used_for__ = IReadContainer

    def __init__(self, context):
        self._context = context

    def find(self, id_filters=None, object_filters=None):
        'See IFind'
        id_filters = id_filters or []
        object_filters = object_filters or []
        result = []
        container = self._context
        for id, object in container.items():
            _find_helper(id, object, container,
                         id_filters, object_filters,
                         result)
        return result


def _find_helper(id, object, container, id_filters, object_filters, result):
    for id_filter in id_filters:
        if not id_filter.matches(id):
            break
    else:
        # if we didn't break out of the loop, all name filters matched
        # now check all object filters
        for object_filter in object_filters:
            if not object_filter.matches(object):
                break
        else:
            # if we didn't break out of the loop, all filters matched
            result.append(object)

    if not IReadContainer.providedBy(object):
        return

    container = object
    for id, object in container.items():
        _find_helper(id, object, container, id_filters, object_filters, result)

@implementer(IIdFindFilter)
class SimpleIdFindFilter(object):
    """Filter objects by ID"""

    def __init__(self, ids):
        self._ids = ids

    def matches(self, id):
        'See INameFindFilter'
        return id in self._ids

@implementer(IObjectFindFilter)
class SimpleInterfacesFindFilter(object):
    """Filter objects on the provided interfaces"""

    def __init__(self, *interfaces):
        self.interfaces = interfaces

    def matches(self, object):
        for iface in self.interfaces:
            if iface.providedBy(object):
                return True
        return False
