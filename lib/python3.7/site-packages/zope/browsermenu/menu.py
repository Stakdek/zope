##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Menu implementation code
"""
__docformat__ = "reStructuredText"
import sys

from zope.component import getAdapters, getUtility
from zope.interface import Interface, implementer, providedBy
from zope.interface.interfaces import IInterface
from zope.pagetemplate.engine import Engine
from zope.publisher.browser import BrowserView
from zope.security import canAccess, checkPermission
from zope.security.interfaces import Forbidden, Unauthorized
from zope.security.proxy import removeSecurityProxy
from zope.traversing.publicationtraverse import PublicationTraverser

from zope.browsermenu.interfaces import IBrowserMenu, IMenuItemType
from zope.browsermenu.interfaces import IBrowserMenuItem, IBrowserSubMenuItem
from zope.browsermenu.interfaces import IMenuAccessView


@implementer(IBrowserMenu)
class BrowserMenu(object):
    """Browser Menu"""

    def __init__(self, id, title=u'', description=u''):
        self.id = id
        self.title = title
        self.description = description

    def getMenuItemType(self):
        return getUtility(IMenuItemType, self.id)

    def getMenuItems(self, object, request):
        """Return menu item entries in a TAL-friendly form."""

        result = []
        for _name, item in getAdapters((object, request),
                                       self.getMenuItemType()):
            if item.available():
                result.append(item)

        # Now order the result. This is not as easy as it seems.
        #
        # (1) Look at the interfaces and put the more specific menu entries
        #     to the front.
        # (2) Sort unambigious entries by order and then by title.
        ifaces = list(providedBy(removeSecurityProxy(object)).__iro__)
        max_key = len(ifaces)
        def iface_index(item):
            iface = item._for or Interface
            if IInterface.providedBy(iface):
                return ifaces.index(iface)
            if isinstance(removeSecurityProxy(object), item._for):
                # directly specified for class, this goes first.
                return -1
            # no idea. This goes last.
            return max_key # pragma: no cover
        result = [(iface_index(item), item.order, item.title, item)
                  for item in result]
        result.sort()

        result = [
            {'title': title,
             'description': item.description,
             'action': item.action,
             'selected': (item.selected() and u'selected') or u'',
             'icon': item.icon,
             'extra': item.extra,
             'submenu': (IBrowserSubMenuItem.providedBy(item) and
                         getMenu(item.submenuId, object, request)) or None}
            for index, order, title, item in result]

        return result


@implementer(IBrowserMenuItem)
class BrowserMenuItem(BrowserView):
    """Browser Menu Item Class"""

    title = u''
    description = u''
    action = u''
    extra = None
    order = 0
    permission = None
    filter = None
    icon = None
    _for = Interface

    def available(self):
        # Make sure we have the permission needed to access the menu's action
        if self.permission is not None:
            # If we have an explicit permission, check that we
            # can access it.
            if not checkPermission(self.permission, self.context):
                return False

        elif self.action != u'':
            # Otherwise, test access by attempting access
            path = self.action
            l = self.action.find('?')
            if l >= 0:
                path = self.action[:l]

            traverser = PublicationTraverser()
            try:
                view = traverser.traverseRelativeURL(
                    self.request, self.context, path)
            except (Unauthorized, Forbidden, LookupError):
                return False
            else:
                # we're assuming that view pages are callable
                # this is a pretty sound assumption
                if not canAccess(view, '__call__'):
                    return False # pragma: no cover

        # Make sure that we really want to see this menu item
        if self.filter is not None:

            try:
                include = self.filter(Engine.getContext(
                    context=self.context,
                    nothing=None,
                    request=self.request,
                    modules=sys.modules,
                ))
            except Unauthorized:
                return False
            else:
                if not include:
                    return False

        return True

    def selected(self):
        request_url = self.request.getURL()

        normalized_action = self.action
        if self.action.startswith('@@'):
            normalized_action = self.action[2:]

        if request_url.endswith('/'+normalized_action):
            return True
        if request_url.endswith('/++view++'+normalized_action):
            return True
        if request_url.endswith('/@@'+normalized_action):
            return True

        return False


@implementer(IBrowserSubMenuItem)
class BrowserSubMenuItem(BrowserMenuItem):
    """Browser Menu Item Base Class"""

    submenuId = None

    def selected(self):
        return False if self.action == u'' else super(BrowserSubMenuItem, self).selected()


def getMenu(id, object, request):
    """Return menu item entries in a TAL-friendly form."""
    menu = getUtility(IBrowserMenu, id)
    return menu.getMenuItems(object, request)


def getFirstMenuItem(id, object, request):
    """Get the first item of a menu."""
    items = getMenu(id, object, request)
    if items:
        return items[0]
    return None


@implementer(IMenuAccessView)
class MenuAccessView(BrowserView):
    """A view allowing easy access to menus."""

    def __getitem__(self, menuId):
        return getMenu(menuId, self.context, self.request)
