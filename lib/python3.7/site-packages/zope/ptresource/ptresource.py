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
"""Page Template Resource
"""

from zope.interface import implementer, provider
from zope.pagetemplate.engine import TrustedAppPT
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.browserresource.resource import Resource
from zope.browserresource.interfaces import IResourceFactory
from zope.browserresource.interfaces import IResourceFactoryFactory

class PageTemplate(TrustedAppPT, PageTemplateFile):
    """
    Resource that is a page template
    """

    def __init__(self, filename, _prefix=None, content_type=None):
        _prefix = self.get_path_from_prefix(_prefix)
        super(PageTemplate, self).__init__(filename, _prefix)
        if content_type is not None:
            self.content_type = content_type

    def pt_getContext(self, request, **kw):
        namespace = super(PageTemplate, self).pt_getContext(**kw)
        namespace['context'] = None
        namespace['request'] = request
        return namespace

    def __call__(self, request, **keywords):
        namespace = self.pt_getContext(
            request=request,
            options=keywords
            )
        return self.pt_render(namespace)

@implementer(IBrowserPublisher)
class PageTemplateResource(BrowserView, Resource):

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''
        raise NotFound(None, name)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        return getattr(self, request.method), ()

    def HEAD(self):
        pt = self.context
        response = self.request.response
        if not response.getHeader("Content-Type"):
            response.setHeader("Content-Type", pt.content_type)
        return ''

    def GET(self):
        pt = self.context
        response = self.request.response
        if not response.getHeader("Content-Type"):
            response.setHeader("Content-Type", pt.content_type)
        return pt(self.request)

@implementer(IResourceFactory)
@provider(IResourceFactoryFactory)
class PageTemplateResourceFactory(object):

    def __init__(self, path, checker, name):
        self.__pt = PageTemplate(path)
        self.__checker = checker
        self.__name = name

    def __call__(self, request):
        resource = PageTemplateResource(self.__pt, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource
