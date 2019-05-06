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
"""GenericSetup events and subscribers.
"""

from zope.component import adapter
from zope.interface import implementer

from Products.GenericSetup.interfaces import IBeforeProfileImportEvent
from Products.GenericSetup.interfaces import IProfileImportedEvent


class BaseProfileImportEvent(object):

    def __init__(self, tool, profile_id, steps, full_import):
        self.tool = tool
        self.profile_id = profile_id
        self.steps = steps
        self.full_import = full_import


@implementer(IBeforeProfileImportEvent)
class BeforeProfileImportEvent(BaseProfileImportEvent):
    pass


@implementer(IProfileImportedEvent)
class ProfileImportedEvent(BaseProfileImportEvent):
    pass


@adapter(IProfileImportedEvent)
def handleProfileImportedEvent(event):
    """Update 'last version for profile' after a full import.
    """
    profile_id = event.profile_id
    if not (profile_id and profile_id.startswith('profile-') and
            event.tool.profileExists(profile_id) and event.full_import):
        return

    version = event.tool.getVersionForProfile(profile_id)
    if version and version != 'unknown':
        prefix = 'profile-'
        profile_id = profile_id[len(prefix):]
        event.tool.setLastVersionForProfile(profile_id, version)
