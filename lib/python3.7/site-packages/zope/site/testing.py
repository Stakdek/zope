##############################################################################
#
# Copyright (c) 2001-2007 Zope Foundation and Contributors.
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
"""Reusable functionality for testing site-related code
"""
import re
import zope.component
import zope.component.hooks
import zope.component.interfaces
import zope.container.interfaces
import zope.container.testing
import zope.site.site
from zope.interface.interfaces import IComponentLookup
from zope.interface import Interface
from zope.site import LocalSiteManager, SiteManagerAdapter
from zope.site.folder import rootFolder
from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
])


def createSiteManager(folder, setsite=False):
    if not zope.component.interfaces.ISite.providedBy(folder):
        folder.setSiteManager(LocalSiteManager(folder))
    if setsite:
        zope.component.hooks.setSite(folder)
    return folder.getSiteManager()


def addUtility(sitemanager, name, iface, utility, suffix=''):
    """Add a utility to a site manager

    This helper function is useful for tests that need to set up utilities.
    """
    folder_name = (name or (iface.__name__ + 'Utility')) + suffix
    default = sitemanager['default']
    default[folder_name] = utility
    utility = default[folder_name]
    sitemanager.registerUtility(utility, iface, name)
    return utility


def siteSetUp(site=False):
    zope.container.testing.setUp()
    zope.component.hooks.setHooks()

    zope.component.provideAdapter(
        SiteManagerAdapter, (Interface,), IComponentLookup)

    if site:
        site = rootFolder()
        createSiteManager(site, setsite=True)
        return site


def siteTearDown():
    zope.container.testing.tearDown()
    zope.component.hooks.resetHooks()
    zope.component.hooks.setSite()
