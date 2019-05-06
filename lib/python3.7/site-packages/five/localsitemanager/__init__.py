##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Local site manager for Zope 2.
"""

from Acquisition import aq_base
from zope.component.globalregistry import base
from zope.interface.interfaces import ComponentLookupError
from zope.component.interfaces import ISite

from five.localsitemanager.registry import PersistentComponents
from five.localsitemanager.utils import get_parent
from Products.Five.component import enableSite
from Products.Five.component.interfaces import IObjectManagerSite


def make_site(obj, iface=ISite):
    """Give the specified object required qualities to identify it as a proper
    ISite.
    """
    if ISite.providedBy(obj):
        raise ValueError('This is already a site')

    next = find_next_sitemanager(obj)
    if next is None:
        next = base

    enableSite(obj, iface=iface)

    components = PersistentComponents('++etc++site', bases=(next,))
    obj.setSiteManager(components)
    components.__parent__ = aq_base(obj)


def make_objectmanager_site(obj):
    """Just a bit of sugar coating to make an unnofficial objectmanager
    based site.
    """
    make_site(obj, IObjectManagerSite)


# Original version: zope.site.site._findNextSiteManager
def find_next_sitemanager(site):
    """Find the closest sitemanager that is not the specified site's
    sitemanager.
    """
    while True:
        site = get_parent(site, default=None)
        if site is None:
            return None

        if ISite.providedBy(site):
            return site.getSiteManager()


def update_sitemanager_bases(site):
    """Formulate the most appropriate __bases__ value for a site's site manager
    by asking find_next_sitemanager what the next appropriate site manager
    is.  After this call, the __bases__ is guaranteed to have one and only
    one value in the __bases__ list/tuple.
    """
    next = find_next_sitemanager(site)
    if next is None:
        next = base
    sm = site.getSiteManager()
    sm.__bases__ = (next,)


# Original version: zope.site.site.changeSiteConfigurationAfterMove
def update_sitemanager_bases_handler(site, event):
    """After a site is moved, its site manager links have to be updated."""
    if event.newParent is not None:
        try:
            update_sitemanager_bases(site)
        except ComponentLookupError:
            pass
