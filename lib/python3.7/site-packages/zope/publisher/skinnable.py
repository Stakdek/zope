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
"""Browser-specific skin implementations.

"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.interface.interfaces

from zope.publisher import interfaces


@zope.interface.implementer(interfaces.ISkinChangedEvent)
class SkinChangedEvent(object):
    """Skin changed event."""


    def __init__(self, request):
        self.request = request


def getDefaultSkin(request):
    """Returns the IDefaultSkin layer for IBrowserRequest."""
    return interfaces.browser.IDefaultBrowserLayer


def setDefaultSkin(request):
    """Sets the default skin for a given request."""
    adapters = zope.component.getSiteManager().adapters
    skin = adapters.lookup((zope.interface.providedBy(request),),
        interfaces.IDefaultSkin, '')
    if skin is None:
        # Find a named ``default`` adapter providing IDefaultSkin as fallback.
        skin = adapters.lookup((zope.interface.providedBy(request),),
            interfaces.IDefaultSkin, 'default')
        if skin is None:
            # Let's be nice and continue to work for IBrowserRequest's
            # without relying on adapter registrations.
            if interfaces.browser.IBrowserRequest.providedBy(request):
                skin = getDefaultSkin
    if skin is not None:
        if not zope.interface.interfaces.IInterface.providedBy(skin):
            # The default fallback skin is registered as a named adapter.
            skin = skin(request)
        else:
            # The defaultSkin directive registers skins as interfaces and not
            # as adapters.  We will not try to adapt the request to an
            # interface to produce an interface.
            pass
        if interfaces.ISkinType.providedBy(skin):
            # silently ignore skins which do not provide ISkinType
            zope.interface.directlyProvides(request, skin)
        else:
            raise TypeError("Skin interface %s doesn't provide ISkinType" %
                skin)


def applySkin(request, skin):
    """Change the presentation skin for this request."""
    # Remove all existing skin type declarations (commonly the default skin)
    # based on the given skin type.
    ifaces = [iface for iface in zope.interface.directlyProvidedBy(request)
              if not interfaces.ISkinType.providedBy(iface)]
    # Add the new skin.
    ifaces.append(skin)
    zope.interface.directlyProvides(request, *ifaces)
    zope.event.notify(SkinChangedEvent(request))
