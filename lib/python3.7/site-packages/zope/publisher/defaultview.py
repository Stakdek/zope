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
"""Default view name API
"""
from zope.interface.interfaces import ComponentLookupError
from zope.component import getSiteManager

import zope.interface
from zope.publisher.interfaces import IDefaultViewName


class IDefaultViewNameAPI(zope.interface.Interface):

    def getDefaultViewName(object, request, context=None):
        """Get the name of the default view for the object and request.

        If a matching default view name cannot be found, raises
        ComponentLookupError.

        If context is not specified, attempts to use
        object to specify a context.
        """

    def queryDefaultViewName(object, request, default=None, context=None):
        """Look for the name of the default view for the object and request.

        If a matching default view name cannot be found, returns the default.

        If context is not specified, attempts to use object to specify
        a context.
        """

def getDefaultViewName(object, request, context=None):
    name = queryDefaultViewName(object, request, context=context)
    if name is not None:
        return name
    raise ComponentLookupError("Couldn't find default view name",
                               context, request)

def queryDefaultViewName(object, request, default=None, context=None):
    """
    query the default view for a given object and request.

      >>> from zope.publisher.defaultview import queryDefaultViewName

    lets create an object with a default view.

      >>> import zope.interface
      >>> class IMyObject(zope.interface.Interface):
      ...   pass
      >>> @zope.interface.implementer(IMyObject)
      ... class MyObject(object):
      ...   pass
      >>> queryDefaultViewName(MyObject(), object()) is None
      True

    Now we can will set a default view.

      >>> import zope.component
      >>> import zope.publisher.interfaces
      >>> zope.component.provideAdapter('name',
      ...     adapts=(IMyObject, zope.interface.Interface),
      ...     provides=zope.publisher.interfaces.IDefaultViewName)
      >>> queryDefaultViewName(MyObject(), object())
      'name'

    This also works if the name is empty

      >>> zope.component.provideAdapter('',
      ...     adapts=(IMyObject, zope.interface.Interface),
      ...     provides=zope.publisher.interfaces.IDefaultViewName)
      >>> queryDefaultViewName(MyObject(), object())
      ''
    """
    name = getSiteManager(context).adapters.lookup(
        map(zope.interface.providedBy, (object, request)), IDefaultViewName)
    if name is None:
        return default
    return name
