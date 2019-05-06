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
"""Menu Directives Configuration Handlers
"""
import six
from zope.browser.interfaces import IAdding
from zope.component import getGlobalSiteManager, queryUtility
from zope.component.interface import provideInterface
from zope.component.zcml import adapter, proxify, utility
from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.pagetemplate.engine import Engine
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.checker import InterfaceChecker, CheckerPublic
from zope.security.metaconfigure import ClassDirective

from zope.browsermenu.menu import BrowserMenu, BrowserMenuItem, BrowserSubMenuItem
from zope.browsermenu.interfaces import IBrowserMenu, IMenuItemType
from zope.browsermenu.interfaces import IBrowserMenuItem, IBrowserSubMenuItem
from zope.browsermenu.interfaces import AddMenu


# Create special modules that contain all menu item types
from types import ModuleType as module
import sys
try:
    import zope.app
except ImportError: # we doesn't always have zope.app now
    sys.modules['zope.app'] = module('app')
menus = module('menus')
sys.modules['zope.app.menus'] = menus


_order_counter = {}


def menuDirective(_context, id=None, class_=BrowserMenu, interface=None,
                  title=u'', description=u''):
    """Registers a new browser menu."""
    if id is None and interface is None:
        raise ConfigurationError(
            "You must specify the 'id' or 'interface' attribute.")

    if interface is None:
        if id in dir(menus):
            # reuse existing interfaces for the id, without this we are not
            # able to override menus.
            interface = getattr(menus, id)
        else:
            interface = InterfaceClass(id, (),
                                       __doc__='Menu Item Type: %s' %id,
                                       __module__='zope.app.menus')
            # Add the menu item type to the `menus` module.
            # Note: We have to do this immediately, so that directives using the
            # MenuField can find the menu item type.
            setattr(menus, id, interface)
        path = 'zope.app.menus.' + id
    else:
        path = interface.__module__ + '.' + interface.getName()

        # If an id was specified, make this menu available under this id.
        # Note that the menu will be still available under its path, since it
        # is an adapter, and the `MenuField` can resolve paths as well.
        if id is None:
            id = path
        else:
            # Make the interface available in the `zope.app.menus` module, so
            # that other directives can find the interface under the name
            # before the CA is setup.
            _context.action(
                discriminator=('browser', 'MenuItemType', path),
                callable=provideInterface,
                args=(path, interface, IMenuItemType, _context.info)
            )
            setattr(menus, id, interface)

    # Register the layer interface as an interface
    _context.action(
        discriminator=('interface', path),
        callable=provideInterface,
        args=(path, interface),
        kw={'info': _context.info}
    )

    # Register the menu item type interface as an IMenuItemType
    _context.action(
        discriminator=('browser', 'MenuItemType', id),
        callable=provideInterface,
        args=(id, interface, IMenuItemType, _context.info)
    )

    # Register the menu as a utility
    utility(_context, IBrowserMenu, class_(id, title, description), name=id)


def menuItemDirective(_context, menu, for_,
                      action, title, description=u'', icon=None, filter=None,
                      permission=None, layer=IDefaultBrowserLayer, extra=None,
                      order=0, item_class=None):
    """Register a single menu item."""
    return menuItemsDirective(_context, menu, for_, layer).menuItem(
        _context, action, title, description, icon, filter,
        permission, extra, order, item_class)


def subMenuItemDirective(_context, menu, for_, title, submenu,
                         action=u'', description=u'', icon=None, filter=None,
                         permission=None, layer=IDefaultBrowserLayer,
                         extra=None, order=0, item_class=None):
    """Register a single sub-menu menu item."""
    return menuItemsDirective(_context, menu, for_, layer).subMenuItem(
        _context, submenu, title, description, action, icon, filter,
        permission, extra, order, item_class)


class MenuItemFactory(object):
    """generic factory for menu items."""

    def __init__(self, factory, **kwargs):
        self.factory = factory
        if 'permission' in kwargs and kwargs['permission'] == 'zope.Public':
            kwargs['permission'] = CheckerPublic
        self.kwargs = kwargs

    def __call__(self, context, request):
        item = self.factory(context, request)

        for key, value in self.kwargs.items():
            setattr(item, key, value)

        if item.permission is not None:
            checker = InterfaceChecker(IBrowserMenuItem, item.permission)
            item = proxify(item, checker)

        return item


class menuItemsDirective(object):
    """Register several menu items for a particular menu."""

    menuItemClass = BrowserMenuItem
    subMenuItemClass = BrowserSubMenuItem

    def __init__(self, _context, menu, for_, layer=IDefaultBrowserLayer,
                 permission=None):
        self.for_ = for_
        self.menuItemType = menu
        self.layer = layer
        self.permission = permission

    def menuItem(self, _context, action, title, description=u'',
                 icon=None, filter=None, permission=None, extra=None,
                 order=0, item_class=None):

        if filter is not None:
            filter = Engine.compile(filter)

        if permission is None:
            permission = self.permission

        if order == 0:
            order = _order_counter.get(self.for_, 1)
            _order_counter[self.for_] = order + 1

        if item_class is None:
            item_class = self.menuItemClass

        if not IBrowserMenuItem.implementedBy(item_class):
            raise ValueError("Item class (%s) must implement IBrowserMenuItem" % item_class)

        factory = MenuItemFactory(
            item_class,
            title=title, description=description, icon=icon, action=action,
            filter=filter, permission=permission, extra=extra, order=order,
            _for=self.for_)
        adapter(_context, (factory,), self.menuItemType,
                (self.for_, self.layer), name=title)

    def subMenuItem(self, _context, submenu, title, description=u'',
                    action=u'', icon=None, filter=None, permission=None,
                    extra=None, order=0, item_class=None):
        filter = Engine.compile(filter) if filter is not None else None

        if permission is None:
            permission = self.permission

        if order == 0:
            order = _order_counter.get(self.for_, 1)
            _order_counter[self.for_] = order + 1

        if item_class is None:
            item_class = self.subMenuItemClass

        if not IBrowserSubMenuItem.implementedBy(item_class):
            raise ValueError("Item class (%s) must implement IBrowserSubMenuItem" % item_class)

        factory = MenuItemFactory(
            item_class,
            title=title, description=description, icon=icon, action=action,
            filter=filter, permission=permission, extra=extra, order=order,
            _for=self.for_, submenuId=submenu)
        adapter(_context, (factory,), self.menuItemType,
                (self.for_, self.layer), name=title)

    def __call__(self, _context):
        """
        See menuItem or subMenuItem.
        """


def _checkViewFor(for_=None, layer=None, view_name=None):
    """Check if there is a view of that name registered for IAdding
    and IBrowserRequest. If not raise a ConfigurationError

    It will raise a ConfigurationError if :
        o view=""
        o if view_name is not registred
    """

    if view_name is None:
        raise ConfigurationError(
            "Within a addMenuItem directive the view attribute"
            " is optional but can\'t be empty"
            )

    gsm = getGlobalSiteManager()
    if gsm.adapters.lookup((for_, layer),
                           Interface, view_name) is None:
        raise ConfigurationError(
            "view name %s not found " %view_name
            )

def addMenuItem(_context, title, description='', menu=None, for_=None,
                class_=None, factory=None, view=None, icon=None, filter=None,
                permission=None, layer=IDefaultBrowserLayer, extra=None,
                order=0, item_class=None):
    """Create an add menu item for a given class or factory

    As a convenience, a class can be provided, in which case, a
    factory is automatically defined based on the class.  In this
    case, the factory id is based on the class name.

    """

    if for_ is not None:
        _context.action(
            discriminator=None,
            callable=provideInterface,
            args=('', for_)
        )
        forname = 'For' + for_.getName()
    else:
        for_ = IAdding
        forname = ''

    if menu is not None:
        if isinstance(menu, six.string_types):
            menu_name = menu
            menu = queryUtility(IMenuItemType, menu)
            if menu is None:
                raise ValueError("Missing menu id '%s'" % menu_name)

    if class_ is None:
        if factory is None:
            raise ValueError("Must specify either class or factory")
    else:
        if factory is not None:
            raise ValueError("Can't specify both class and factory")
        if permission is None:
            raise ValueError(
                "A permission must be specified when a class is used")
        factory = "BrowserAdd%s__%s.%s" % (
            forname, class_.__module__, class_.__name__)
        ClassDirective(_context, class_).factory(_context, id=factory)

    extra = {'factory': factory}

    if view:
        action = view
        # This action will check if the view exists
        _context.action(
            discriminator=None,
            callable=_checkViewFor,
            args=(for_, layer, view),
            order=999999
        )
    else:
        action = factory

    if menu is None:
        menu = AddMenu

    return menuItemsDirective(_context, menu, for_, layer=layer).menuItem(
        _context, action, title, description, icon, filter,
        permission, extra, order, item_class)
