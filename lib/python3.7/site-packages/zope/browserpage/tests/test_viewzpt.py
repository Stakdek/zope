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
"""View ZPT Tests
"""
import unittest

from zope.component import getGlobalSiteManager
from zope.component.testing import PlacelessSetup
from zope.interface import Interface, implementer

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.browserpage.viewpagetemplatefile import BoundPageTemplate


class I1(Interface):
    pass

@implementer(I1)
class C1(object):
    pass

class InstanceWithContext(object):
    def __init__(self, context):
        self.context = context

class InstanceWithoutContext(object):
    pass


class TestViewZPT(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestViewZPT, self).setUp()
        self.t = ViewPageTemplateFile('test.pt')
        self.context = C1()

    def testNamespaceContextAvailable(self):
        context = self.context
        request = None

        namespace = self.t.pt_getContext(InstanceWithContext(context), request)
        self.assertTrue(namespace['context'] is context)
        self.assertTrue('views' in namespace)

    def testNamespaceHereNotAvailable(self):
        request = None
        self.assertRaises(AttributeError, self.t.pt_getContext,
                          InstanceWithoutContext(), request)

    def testViewMapper(self):
        the_view = "This is the view"
        the_view_name = "some view name"
        def ViewMaker(*args, **kw):
            return the_view

        from zope.publisher.interfaces import IRequest

        gsm = getGlobalSiteManager()
        gsm.registerAdapter(
            ViewMaker, (I1, IRequest), Interface, the_view_name, event=False)

        @implementer(IRequest)
        class MyRequest(object):
            pass

        request = MyRequest()

        namespace = self.t.pt_getContext(InstanceWithContext(self.context),
                                         request)
        views = namespace['views']
        self.assertTrue(the_view is views[the_view_name])

    def test_debug_flags(self):
        from zope.publisher.browser import TestRequest
        self.request = TestRequest()
        self.request.debug.sourceAnnotations = False
        self.assertFalse('test.pt' in self.t(self))
        self.request.debug.sourceAnnotations = True
        self.assertTrue('test.pt' in self.t(self))

        t = ViewPageTemplateFile('testsimpleviewclass.pt')
        self.request.debug.showTAL = False
        self.assertFalse('metal:' in t(self))
        self.request.debug.showTAL = True
        self.assertTrue('metal:' in t(self))

    def test_render_sets_content_type_unless_set(self):
        from zope.publisher.browser import TestRequest
        t = ViewPageTemplateFile('test.pt')

        self.request = TestRequest()
        response = self.request.response
        self.assertFalse(response.getHeader('Content-Type'))
        t(self)
        self.assertEqual(response.getHeader('Content-Type'), 'text/html')

        self.request = TestRequest()
        response = self.request.response
        response.setHeader('Content-Type', 'application/x-test-junk')
        t(self)
        self.assertEqual(response.getHeader('Content-Type'),
                         'application/x-test-junk')


class TestViewZPTContentType(unittest.TestCase):

    def testInitWithoutType(self):
        t = ViewPageTemplateFile('test.pt')
        t._cook_check()
        self.assertEqual(t.content_type, "text/html")

        t = ViewPageTemplateFile('testxml.pt')
        t._cook_check()
        self.assertEqual(t.content_type, "text/xml")

    def testInitWithType(self):
        t = ViewPageTemplateFile('test.pt', content_type="text/plain")
        t._cook_check()
        self.assertEqual(t.content_type, "text/plain")

        t = ViewPageTemplateFile('testxml.pt', content_type="text/plain")
        t._cook_check()
        self.assertEqual(t.content_type, "text/xml")


class TestBoundPageTemplate(unittest.TestCase):

    def test_call_self_none(self):
        args = []
        def func(*a):
            args.extend(a)

        bpt = BoundPageTemplate(func, None)
        bpt(self, 1, 2)

        self.assertEqual(args, [self, 1, 2])

    def test_cannot_set_attr(self):
        bpt = BoundPageTemplate(None, None)
        with self.assertRaises(AttributeError):
            bpt.thing = 1

        with self.assertRaises(AttributeError):
            bpt.__func__ = 1

        with self.assertRaises(AttributeError):
            bpt.__self__ = 1

    def test_repr(self):
        ob = "WackyWavingInflatableArmFlailingTubeMan"

        bpt = BoundPageTemplate(None, ob)
        self.assertEqual(repr(bpt),
                         "<BoundPageTemplateFile of 'WackyWavingInflatableArmFlailingTubeMan'>")


class TestNoTraverser(unittest.TestCase):

    def test_none(self):
        from zope.browserpage.viewpagetemplatefile import NoTraverser
        self.assertIsNone(NoTraverser(self, self))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
