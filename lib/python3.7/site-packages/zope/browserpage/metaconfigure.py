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
"""Browser page ZCML configuration code
"""
import os

from zope.component import queryMultiAdapter
from zope.component.interface import provideInterface
from zope.component.zcml import handler
from zope.interface import implementer, classImplements, Interface
from zope.publisher.interfaces import NotFound
from zope.security.checker import CheckerPublic, Checker, defineChecker
from zope.configuration.exceptions import ConfigurationError
from zope.pagetemplate.engine import Engine
from zope.pagetemplate.engine import _Engine
from zope.pagetemplate.engine import TrustedEngine
from zope.pagetemplate.engine import _TrustedEngine
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.browser import BrowserView

from zope.browserpage.simpleviewclass import SimpleViewClass
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

def _fallbackMenuItemDirective(_context, *args, **kwargs):
    import warnings
    warnings.warn_explicit(
        'Page directive used with "menu" argument, while "zope.browsermenu" '
        'package is not installed. Doing nothing.',
        UserWarning,
        _context.info.file, _context.info.line)
    return []

try:
    from zope.browsermenu.metaconfigure import menuItemDirective
except ImportError: # pragma: no cover
    menuItemDirective = _fallbackMenuItemDirective

# There are three cases we want to suport:
#
# Named view without pages (single-page view)
#
#     <browser:page
#         for=".IContact.IContactInfo."
#         name="info.html"
#         template="info.pt"
#         class=".ContactInfoView."
#         permission="zope.View"
#         />
#
# Unnamed view with pages (multi-page view)
#
#     <browser:pages
#         for=".IContact."
#         class=".ContactEditView."
#         permission="ZopeProducts.Contact.ManageContacts"
#         >
#
#       <browser:page name="edit.html"       template="edit.pt" />
#       <browser:page name="editAction.html" attribute="action" />
#       </browser:pages>
#
# Named view with pages (add view is a special case of this)
#
#        <browser:view
#            name="ZopeProducts.Contact"
#            for="Zope.App.OFS.Container.IAdding."
#            class=".ContactAddView."
#            permission="ZopeProducts.Contact.ManageContacts"
#            >
#
#          <browser:page name="add.html"    template="add.pt" />
#          <browser:page name="action.html" attribute="action" />
#          </browser:view>

# We'll also provide a convenience directive for add views:
#
#        <browser:add
#            name="ZopeProducts.Contact"
#            class=".ContactAddView."
#            permission="ZopeProducts.Contact.ManageContacts"
#            >
#
#          <browser:page name="add.html"    template="add.pt" />
#          <browser:page name="action.html" attribute="action" />
#          </browser:view>

# page

def _norm_template(_context, template):
    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)
    return template


def page(_context, name, permission, for_=Interface,
         layer=IDefaultBrowserLayer, template=None, class_=None,
         allowed_interface=None, allowed_attributes=None,
         attribute='__call__', menu=None, title=None):
    _handle_menu(_context, menu, title, [for_], name, permission, layer)
    required = {}

    permission = _handle_permission(_context, permission)

    if not (class_ or template):
        raise ConfigurationError("Must specify a class or template")

    if attribute != '__call__':
        if template:
            raise ConfigurationError(
                "Attribute and template cannot be used together.")

        assert class_, "Must have class if attribute is used"

    if template:
        template = _norm_template(_context, template)
        required['__getitem__'] = permission

    # TODO: new __name__ attribute must be tested
    if class_:
        if attribute != '__call__':
            if not hasattr(class_, attribute):
                raise ConfigurationError(
                    "The provided class doesn't have the specified attribute "
                    )
        if template:
            # class and template
            new_class = SimpleViewClass(template, bases=(class_, ), name=name)
        else:
            if not hasattr(class_, 'browserDefault'):
                cdict = {
                    'browserDefault':
                    lambda self, request: (getattr(self, attribute), ())
                    }
            else:
                cdict = {}

            cdict['__name__'] = name
            cdict['__page_attribute__'] = attribute
            new_class = type(class_.__name__, (class_, simple,), cdict)

        if hasattr(class_, '__implements__'):
            classImplements(new_class, IBrowserPublisher)

    else:
        # template
        new_class = SimpleViewClass(template, name=name)

    for n in (attribute, 'browserDefault', '__call__', 'publishTraverse'):
        required[n] = permission

    _handle_allowed_interface(_context, allowed_interface, permission,
                              required)
    _handle_allowed_attributes(_context, allowed_attributes, permission,
                               required)

    _handle_for(_context, for_)

    defineChecker(new_class, Checker(required))

    _context.action(
        discriminator=('view', (for_, layer), name, IBrowserRequest),
        callable=handler,
        args=('registerAdapter',
              new_class, (for_, layer), Interface, name, _context.info),
    )


# pages, which are just a short-hand for multiple page directives.

# Note that a class might want to access one of the defined
# templates. If it does though, it should use getMultiAdapter.

class pages(object):

    def __init__(self, _context, permission, for_=Interface,
                 layer=IDefaultBrowserLayer, class_=None,
                 allowed_interface=None, allowed_attributes=None):
        self.opts = dict(
            for_=for_, permission=permission,
            layer=layer, class_=class_,
            allowed_interface=allowed_interface,
            allowed_attributes=allowed_attributes,
        )

    def page(self, _context, name, attribute='__call__', template=None,
             menu=None, title=None):
        return page(_context,
                    name=name,
                    attribute=attribute,
                    template=template,
                    menu=menu, title=title,
                    **(self.opts))

    def __call__(self):
        return ()

# view (named view with pages)

# This is a different case. We actually build a class with attributes
# for all of the given pages.

class view(object):

    default = None

    def __init__(self, _context, permission, for_=Interface,
                 name='', layer=IDefaultBrowserLayer, class_=None,
                 allowed_interface=None, allowed_attributes=None,
                 menu=None, title=None, provides=Interface):

        _handle_menu(_context, menu, title, [for_], name, permission, layer)

        permission = _handle_permission(_context, permission)

        self.args = (_context, name, (for_, layer), permission, class_,
                     allowed_interface, allowed_attributes)

        self.pages = []
        self.menu = menu
        self.provides = provides

    def page(self, _context, name, attribute=None, template=None):
        if template:
            template = _norm_template(_context, template)
        else:
            if not attribute:
                raise ConfigurationError(
                    "Must specify either a template or an attribute name")

        self.pages.append((name, attribute, template))
        return ()

    def defaultPage(self, _context, name):
        self.default = name
        return ()

    def __call__(self):
        (_context, name, (for_, layer), permission, class_,
         allowed_interface, allowed_attributes) = self.args

        required = {}

        cdict = {}
        pages = {}

        for pname, attribute, template in self.pages:

            if template:
                cdict[pname] = ViewPageTemplateFile(template)
                if attribute and attribute != name:
                    cdict[attribute] = cdict[pname]
            else:
                if not hasattr(class_, attribute):
                    raise ConfigurationError("Undefined attribute",
                                             attribute)

            attribute = attribute or pname
            required[pname] = permission

            pages[pname] = attribute

        # This should go away, but noone seems to remember what to do. :-(
        if hasattr(class_, 'publishTraverse'):

            def publishTraverse(self, request, name,
                                pages=pages, getattr=getattr):

                if name in pages:
                    return getattr(self, pages[name])
                view = queryMultiAdapter((self, request), name=name)
                if view is not None:
                    return view

                m = class_.publishTraverse.__get__(self)
                return m(request, name)

        else:
            def publishTraverse(self, request, name,
                                pages=pages, getattr=getattr):

                if name in pages:
                    return getattr(self, pages[name])
                view = queryMultiAdapter((self, request), name=name)
                if view is not None:
                    return view

                raise NotFound(self, name, request)

        cdict['publishTraverse'] = publishTraverse

        if not hasattr(class_, 'browserDefault'):
            if self.default or self.pages:
                _default = self.default or self.pages[0][0]
                cdict['browserDefault'] = (
                    lambda self, request, default=_default:
                    (self, (default, ))
                )
            elif providesCallable(class_):
                cdict['browserDefault'] = (
                    lambda self, request: (self, ())
                )

        bases = (simple,) if class_ is None else (class_, simple)

        try:
            cname = str(name)
        except Exception: # pragma: no cover
            cname = "GeneratedClass"

        cdict['__name__'] = name
        newclass = type(cname, bases, cdict)

        for n in ('publishTraverse', 'browserDefault', '__call__'):
            required[n] = permission

        _handle_allowed_interface(_context, allowed_interface, permission,
                                  required)
        _handle_allowed_attributes(_context, allowed_attributes, permission,
                                   required)
        _handle_for(_context, for_)

        defineChecker(newclass, Checker(required))

        if self.provides is not None:
            _context.action(
                discriminator=None,
                callable=provideInterface,
                args=('', self.provides)
            )

        _context.action(
            discriminator=('view', (for_, layer), name, self.provides),
            callable=handler,
            args=('registerAdapter',
                  newclass, (for_, layer), self.provides, name,
                  _context.info),
        )

def _handle_menu(_context, menu, title, for_, name, permission,
                 layer=IDefaultBrowserLayer):
    if not menu and not title:
        # Neither of them
        return []

    if not menu or not title:
        # Only one or the other
        raise ConfigurationError(
            "If either menu or title are specified, they must "
            "both be specified.")

    if len(for_) != 1:
        raise ConfigurationError(
            "Menus can be specified only for single-view, not for "
            "multi-views.")

    return menuItemDirective(
        _context, menu, for_[0], '@@' + name, title,
        permission=permission, layer=layer)


def _handle_permission(_context, permission):
    if permission == 'zope.Public':
        permission = CheckerPublic

    return permission

def _handle_allowed_interface(_context, allowed_interface, permission,
                              required):
    # Allow access for all names defined by named interfaces
    if allowed_interface:
        for i in allowed_interface:
            _context.action(
                discriminator=None,
                callable=provideInterface,
                args=(None, i)
            )

            for name in i:
                required[name] = permission

def _handle_allowed_attributes(_context, allowed_attributes, permission,
                               required):
    # Allow access for all named attributes
    if allowed_attributes:
        for name in allowed_attributes:
            required[name] = permission

def _handle_for(_context, for_):
    if for_ is not None:
        _context.action(
            discriminator=None,
            callable=provideInterface,
            args=('', for_)
        )

@implementer(IBrowserPublisher)
class simple(BrowserView):

    def publishTraverse(self, request, name):
        raise NotFound(self, name, request)

    def __call__(self, *a, **k):
        # If a class doesn't provide it's own call, then get the attribute
        # given by the browser default.

        attr = self.__page_attribute__
        if attr == '__call__':
            raise AttributeError("__call__")

        meth = getattr(self, attr)
        return meth(*a, **k)

def providesCallable(class_):
    if hasattr(class_, '__call__'):
        for c in class_.__mro__:
            if '__call__' in c.__dict__:
                return True
    return False


def expressiontype(_context, name, handler):
    _context.action(
        discriminator=("tales:expressiontype", name),
        callable=registerType,
        args=(name, handler)
    )

def registerType(name, handler):
    Engine.registerType(name, handler)
    TrustedEngine.registerType(name, handler)


def clear():
    Engine.__init__()
    _Engine(Engine)
    TrustedEngine.__init__()
    _TrustedEngine(TrustedEngine)


try:
    from zope.testing.cleanup import addCleanUp
except ImportError: # pragma: no cover
    pass
else:
    addCleanUp(clear)
