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
"""Simple View Class
"""
__docformat__ = 'restructuredtext'

import sys
from zope.interface import implementer
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces import NotFound
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

@implementer(IBrowserPublisher)
class simple(BrowserView):

    def browserDefault(self, request):
        return self, ()

    def publishTraverse(self, request, name):
        if name == 'index.html':
            return self.index

        raise NotFound(self, name, request)

    def __getitem__(self, name):
        return self.index.macros[name]

    def __call__(self, *args, **kw):
        return self.index(*args, **kw)


def SimpleViewClass(src, offering=None, used_for=None, bases=(), name=u''):
    if offering is None:
        offering = sys._getframe(1).f_globals

    bases += (simple, )

    class_ = type("SimpleViewClass from %s" % src, bases,
                  {'index': ViewPageTemplateFile(src, offering),
                   '__name__': name})

    if used_for is not None:
        class_.__used_for__ = used_for

    return class_
