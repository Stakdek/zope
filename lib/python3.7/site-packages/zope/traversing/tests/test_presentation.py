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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Presentation Traverser Tests
"""
import unittest
from zope.testing.cleanup import CleanUp
from zope.interface import Interface, implementer
from zope.publisher.browser import TestRequest
from zope.traversing.namespace import view, resource
from zope.traversing.testing import browserView, browserResource

class IContent(Interface):
    pass

@implementer(IContent)
class Content(object):
    pass

class Resource(object):

    def __init__(self, request):
        pass

class View(object):

    def __init__(self, content, request):
        self.content = content


class Test(CleanUp, unittest.TestCase):

    def testView(self):
        browserView(IContent, 'foo', View)

        ob = Content()
        v = view(ob, TestRequest()).traverse('foo', ())
        self.assertEqual(v.__class__, View)

    def testResource(self):
        browserResource('foo', Resource)

        ob = Content()
        r = resource(ob, TestRequest()).traverse('foo', ())
        self.assertEqual(r.__class__, Resource)
