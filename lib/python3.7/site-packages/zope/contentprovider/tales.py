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
"""Provider TALES expression"""
import zope.component
import zope.interface
import zope.schema
import zope.event
from zope.location.interfaces import ILocation
from zope.tales import expressions

from zope.contentprovider import interfaces


def addTALNamespaceData(provider, context):
    """Add the requested TAL attributes to the provider"""
    data = {}

    for interface in zope.interface.providedBy(provider):
        if interfaces.ITALNamespaceData.providedBy(interface):
            for name, field in zope.schema.getFields(interface).items():
                data[name] = context.vars.get(name, field.default)

    provider.__dict__.update(data)


@zope.interface.implementer(interfaces.ITALESProviderExpression)
class TALESProviderExpression(expressions.StringExpr):
    """
    Collect content provider via a TAL namespace.

    Note that this implementation of the TALES ``provider`` namespace
    does not work with interdependent content providers, since each
    content-provider's stage one call is made just before the second
    stage is executed.  If you want to implement interdependent
    content providers, you need to consider a TAL-independent view
    implementation such as zope.viewlet that will complete all content
    providers' stage one before rendering any of them.

    Implements `zope.contentprovider.interfaces.ITALESProviderExpression`
    """

    def __call__(self, econtext):
        name = super(TALESProviderExpression, self).__call__(econtext)
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # Try to look up the provider.
        provider = zope.component.queryMultiAdapter(
            (context, request, view), interfaces.IContentProvider, name)

        # Provide a useful error message, if the provider was not found.
        if provider is None:
            raise interfaces.ContentProviderLookupError(name)

        # add the __name__ attribute if it implements ILocation
        if ILocation.providedBy(provider):
            provider.__name__ = name

        # Insert the data gotten from the context
        addTALNamespaceData(provider, econtext)

        # Stage 1: Do the state update.
        zope.event.notify(interfaces.BeforeUpdateEvent(provider, request))
        provider.update()

        # Stage 2: Render the HTML content.
        return provider.render()
