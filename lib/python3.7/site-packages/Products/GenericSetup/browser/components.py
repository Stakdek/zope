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
"""Components setup view.
"""

from Products.Five import BrowserView
from Products.Five.browser.decode import processInputs
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.component.interfaces import IObjectManagerSite
from zope.component import adapts
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import Text
from ZPublisher import HTTPRequest

from Products.GenericSetup.context import SetupEnviron
from Products.GenericSetup.interfaces import IBody


class IComponentsSetupSchema(Interface):

    """Schema for components setup views.
    """

    body = Text(
        title=u'Settings')


@implementer(IComponentsSetupSchema)
class ComponentsSetupSchemaAdapter(object):

    adapts(IObjectManagerSite)

    def __init__(self, context):
        self.context = context

    def _getBody(self):
        sm = self.context.aq_inner.getSiteManager()
        return getMultiAdapter((sm, SetupEnviron()), IBody).body

    def _setBody(self, value):
        sm = self.context.aq_inner.getSiteManager()
        getMultiAdapter((sm, SetupEnviron()), IBody).body = value

    body = property(_getBody, _setBody)


class ComponentsSetupView(BrowserView):

    """Components setup view for IObjectManagerSite.
    """

    template = form_template = ViewPageTemplateFile('components_form.pt')
    status = ''

    def update(self):
        # BBB: for Zope < 2.14
        if not getattr(self.request, 'postProcessInputs', False):
            processInputs(self.request, [HTTPRequest.default_encoding])

        self.adapter = getAdapter(self.context, IComponentsSetupSchema)

        if 'apply' in self.request.form:
            self.adapter.body = self.request.form['body']
            self.status = 'Saved changes.'

    def __call__(self):
        self.update()
        return self.template()


class ComponentsSetupTab(ComponentsSetupView):

    """Components setup ZMI tab for IObjectManagerSite.
    """

    template = ViewPageTemplateFile('components.pt')
