##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Interfaces for the Local Component Architecture
"""

import zope.interface
import zope.interface.interfaces
import zope.container.interfaces
import zope.container.constraints
import zope.location.interfaces

from zope.annotation.interfaces import IAttributeAnnotatable


class INewLocalSite(zope.interface.Interface):
    """Event: a local site was created
    """
    manager = zope.interface.Attribute("The new site manager")


@zope.interface.implementer(INewLocalSite)
class NewLocalSite(object):
    """Event: a local site was created
    """
    def __init__(self, manager):
        self.manager = manager


class ILocalSiteManager(zope.interface.interfaces.IComponents):
    """Site Managers act as containers for registerable components.

    If a Site Manager is asked for an adapter or utility, it checks for those
    it contains before using a context-based lookup to find another site
    manager to delegate to.  If no other site manager is found they defer to
    the global site manager which contains file based utilities and adapters.
    """

    subs = zope.interface.Attribute(
        "A collection of registries that describe the next level "
        "of the registry tree. They are the children of this "
        "registry node. This attribute should never be "
        "manipulated manually. Use `addSub()` and `removeSub()` "
        "instead.")

    def addSub(sub):
        """Add a new sub-registry to the node.

        Important: This method should *not* be used manually. It is
        automatically called by `setNext()`. To add a new registry to the
        tree, use `sub.setNext(self, self.base)` instead!
        """

    def removeSub(sub):
        """Remove a sub-registry to the node.

        Important: This method should *not* be used manually. It is
        automatically called by `setNext()`. To remove a registry from the
        tree, use `sub.setNext(None)` instead!
        """


class ISiteManagementFolder(zope.container.interfaces.IContainer):
    """Component and component registration containers."""

    zope.container.constraints.containers(
        ILocalSiteManager, '.ISiteManagementFolder')


class IFolder(zope.container.interfaces.IContainer,
              zope.component.interfaces.IPossibleSite,
              IAttributeAnnotatable):
    """The standard Zope Folder object interface."""


class IRootFolder(IFolder, zope.location.interfaces.IRoot):
    """The standard Zope root Folder object interface."""
