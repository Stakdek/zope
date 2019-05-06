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
"""Management view for local site manager.
"""

from Products.Five.component.browser import ObjectManagerSiteView
from zope.component.globalregistry import base
from zope.component.hooks import setSite

from five.localsitemanager import make_objectmanager_site


class ObjectManagerSiteView(ObjectManagerSiteView):

    """Configure the site setup for an ObjectManager.
    """

    def makeSite(self):
        make_objectmanager_site(self.context)
        setSite(self.context)

    def sitemanagerTrail(self):
        if not self.isSite():
            return None

        sm = self.context.getSiteManager()
        trail = []
        while sm is not None and sm != base:
            trail.append(repr(sm))
            sm = sm.__bases__[0]

        if sm == base:
            trail.append('Global Registry')

        trail.reverse()

        return ' => '.join(trail)
