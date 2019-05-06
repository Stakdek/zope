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
"""Viewlet metadirective
"""
__docformat__ = 'restructuredtext'

import zope.configuration.fields
import zope.schema
from zope.publisher.interfaces import browser
from zope.security.zcml import Permission
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
_ = MessageFactory('zope')

from zope.viewlet import interfaces


class IContentProvider(Interface):
    """A directive to register a simple content provider.

    Content providers are registered by their context (`for` attribute), the
    request (`layer` attribute) and the view (`view` attribute). They also
    must provide a name, so that they can be found using the TALES
    ``provider`` namespace. Other than that, content providers are just like
    any other views.
    """

    view = zope.configuration.fields.GlobalObject(
        title=_("The view the content provider is registered for."),
        description=_("The view can either be an interface or a class. By "
                      "default the provider is registered for all views, "
                      "the most common case."),
        required=False,
        default=browser.IBrowserView)

    name = zope.schema.TextLine(
        title=_("The name of the content provider."),
        description=_("The name of the content provider is used in the TALES "
                      "``provider`` namespace to look up the content "
                      "provider."),
        required=True)

    for_ = zope.configuration.fields.GlobalObject(
        title=u"The interface or class this view is for.",
        required=False
        )

    permission = Permission(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=True
        )

    class_ = zope.configuration.fields.GlobalObject(
        title=_("Class"),
        description=_("A class that provides attributes used by the view."),
        required=False,
        )

    layer = zope.configuration.fields.GlobalInterface(
        title=_("The layer the view is in."),
        description=_("""
        A skin is composed of layers. It is common to put skin
        specific views in a layer named after the skin. If the 'layer'
        attribute is not supplied, it defaults to 'default'."""),
        required=False,
        )

    allowed_interface = zope.configuration.fields.Tokens(
        title=_("Interface that is also allowed if user has permission."),
        description=_("""
        By default, 'permission' only applies to viewing the view and
        any possible sub views. By specifying this attribute, you can
        make the permission also apply to everything described in the
        supplied interface.

        Multiple interfaces can be provided, separated by
        whitespace."""),
        required=False,
        value_type=zope.configuration.fields.GlobalInterface(),
        )

    allowed_attributes = zope.configuration.fields.Tokens(
        title=_("View attributes that are also allowed if the user"
                " has permission."),
        description=_("""
        By default, 'permission' only applies to viewing the view and
        any possible sub views. By specifying 'allowed_attributes',
        you can make the permission also apply to the extra attributes
        on the view object."""),
        required=False,
        value_type=zope.configuration.fields.PythonIdentifier(),
        )


class ITemplatedContentProvider(IContentProvider):
    """A directive for registering a content provider that uses a page
    template to provide its content."""

    template = zope.configuration.fields.Path(
        title=_("Content-generating template."),
        description=_("Refers to a file containing a page template (should "
                      "end in extension ``.pt`` or ``.html``)."),
        required=False)


class IViewletManagerDirective(ITemplatedContentProvider):
    """A directive to register a new viewlet manager.

    Viewlet manager registrations are very similar to content provider
    registrations, since they are just a simple extension of content
    providers. However, viewlet managers commonly have a specific provided
    interface, which is used to discriminate the viewlets they are providing.
    """

    provides = zope.configuration.fields.GlobalInterface(
        title=_("The interface this viewlet manager provides."),
        description=_("A viewlet manager can provide an interface, which "
                      "is used to lookup its contained viewlets."),
        required=False,
        default=interfaces.IViewletManager,
        )


class IViewletDirective(ITemplatedContentProvider):
    """A directive to register a new viewlet.

    Viewlets are content providers that can only be displayed inside a viewlet
    manager. Thus they are additionally discriminated by the manager. Viewlets
    can rely on the specified viewlet manager interface to provide their
    content.

    The viewlet directive also supports an undefined set of keyword arguments
    that are set as attributes on the viewlet after creation. Those attributes
    can then be used to implement sorting and filtering, for example.
    """

    manager = zope.configuration.fields.GlobalObject(
        title=_("view"),
        description=u"The interface of the view this viewlet is for. "
                    u"(default IBrowserView)",
        required=False,
        default=interfaces.IViewletManager)


# Arbitrary keys and values are allowed to be passed to the viewlet.
IViewletDirective.setTaggedValue('keyword_arguments', True)
