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
"""Default view and default skin ZCML configuration feature.
"""
from zope import component
from zope.component.interface import provideInterface
from zope.component.zcml import handler
from zope.configuration.fields import GlobalObject, GlobalInterface
from zope.interface import Interface
from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import IDefaultSkin
from ._compat import _u
from zope.schema import TextLine


class IDefaultSkinDirective(Interface):
    """Sets the default browser skin"""

    name = TextLine(
        title=_u("Default skin name"),
        description=_u("Default skin name"),
        required=True
        )


class IDefaultViewDirective(Interface):
    """
    The name of the view that should be the default.

    This name refers to view that should be the
    view used by default (if no view name is supplied
    explicitly).
    """

    name = TextLine(
        title=_u("The name of the view that should be the default."),
        description=_u("""
        This name refers to view that should be the view used by
        default (if no view name is supplied explicitly)."""),
        required=True
        )

    for_ = GlobalObject(
        title=_u("The interface this view is the default for."),
        description=_u("""
        Specifies the interface for which the view is registered.

        All objects implementing this interface can make use of
        this view. If this attribute is not specified, the view is available
        for all objects."""),
        required=False
        )

    layer = GlobalInterface(
        title=_u("The layer the default view is declared for"),
        description=_u("The default layer for which the default view is "
                       "applicable. By default it is applied to all layers."),
        required=False
        )


def setDefaultSkin(name, info=''):
    """Set the default skin.

    >>> from zope.interface import directlyProvides
    >>> from zope.app.testing import ztapi

    >>> class Skin1: pass
    >>> directlyProvides(Skin1, IBrowserSkinType)

    >>> ztapi.provideUtility(IBrowserSkinType, Skin1, 'Skin1')
    >>> setDefaultSkin('Skin1')
    >>> adapters = component.getSiteManager().adapters

	Lookup the default skin for a request that has the

    >>> adapters.lookup((IBrowserRequest,), IDefaultSkin, '') is Skin1
    True
    """
    skin = component.getUtility(IBrowserSkinType, name)
    handler('registerAdapter',
            skin, (IBrowserRequest,), IDefaultSkin, '', info)


def defaultSkin(_context, name):

    _context.action(
        discriminator = 'defaultSkin',
        callable = setDefaultSkin,
        args = (name, _context.info)
        )


def defaultView(_context, name, for_=None, layer=IBrowserRequest):

    _context.action(
        discriminator = ('defaultViewName', for_, layer, name),
        callable = handler,
        args = ('registerAdapter',
                name, (for_, layer), IDefaultViewName, '', _context.info)
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )
