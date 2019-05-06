#############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""
"""

import unittest

import zope.component
from zope.component import getSiteManager
import zope.container.testing
from zope.event import notify
from zope.lifecycleevent import ObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

from zope.site.folder import rootFolder
from zope.site.site import SiteManagerContainer
import zope.site.testing


class Dummy(object):
    pass


removed_called = False


def removed_event(obj, event):
    global removed_called
    removed_called = True


def dispatch_event(obj, event):
    sm = obj._sm
    if sm is not None:
        for k, v in sm.items():
            notify(ObjectRemovedEvent(v, sm, k))


class SiteManagerContainerTest(unittest.TestCase):

    def setUp(self):
        self.root = rootFolder()
        zope.site.testing.siteSetUp(self.root)

        global removed_called
        removed_called = False

        sm = getSiteManager()
        sm.registerHandler(removed_event, (Dummy, IObjectRemovedEvent))
        sm.registerHandler(
            dispatch_event, (SiteManagerContainer, IObjectRemovedEvent))

    def tearDown(self):
        zope.site.testing.siteTearDown()

    def test_delete_smc_should_propagate_removed_event(self):
        container = SiteManagerContainer()
        self.root['container'] = container

        zope.site.testing.createSiteManager(container)
        container.getSiteManager()['child'] = Dummy()

        del self.root['container']
        self.assertTrue(removed_called)

    def test_delete_when_smc_has_no_sitemanager(self):
        container = SiteManagerContainer()
        self.root['container'] = container

        del self.root['container']


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
