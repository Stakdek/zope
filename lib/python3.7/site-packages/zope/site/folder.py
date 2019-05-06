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
import zope.component.interfaces
import zope.container.folder
from zope.interface import implementer, directlyProvides
from zope.site.interfaces import IFolder, IRootFolder
from zope.site.site import SiteManagerContainer


@implementer(IFolder)
class Folder(zope.container.folder.Folder, SiteManagerContainer):
    """Implementation of :class:`~.IFolder`"""


def rootFolder():
    """Factory for a :class:`~.IRootFolder`"""
    f = Folder()
    directlyProvides(f, IRootFolder)
    return f


class FolderSublocations(object):
    """Get the sublocations of a folder

    The subobjects of a folder include it's contents and it's site manager if
    it is a site.

      >>> from zope.container.contained import Contained
      >>> folder = Folder()
      >>> folder['ob1'] = Contained()
      >>> folder['ob2'] = Contained()
      >>> folder['ob3'] = Contained()
      >>> subs = list(FolderSublocations(folder).sublocations())
      >>> subs.remove(folder['ob1'])
      >>> subs.remove(folder['ob2'])
      >>> subs.remove(folder['ob3'])
      >>> subs
      []

      >>> sm = Contained()
      >>> from zope.interface import directlyProvides
      >>> from zope.interface.interfaces import IComponentLookup
      >>> directlyProvides(sm, IComponentLookup)
      >>> folder.setSiteManager(sm)
      >>> directlyProvides(folder, zope.component.interfaces.ISite)
      >>> subs = list(FolderSublocations(folder).sublocations())
      >>> subs.remove(folder['ob1'])
      >>> subs.remove(folder['ob2'])
      >>> subs.remove(folder['ob3'])
      >>> subs.remove(sm)
      >>> subs
      []
    """

    def __init__(self, folder):
        self.folder = folder

    def sublocations(self):
        folder = self.folder
        for key in folder:
            yield folder[key]

        if zope.component.interfaces.ISite.providedBy(folder):
            yield folder.getSiteManager()
