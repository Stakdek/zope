##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Tests of PublicationTraverser
"""
import unittest

from zope.testing.cleanup import CleanUp
from zope.component import provideAdapter
from zope.interface import Interface, implementer
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.security.proxy import removeSecurityProxy
from zope.traversing.interfaces import ITraversable
from zope.traversing.publicationtraverse import PublicationTraverser

class TestPublicationTraverser(CleanUp, unittest.TestCase):

    def testViewNotFound(self):
        ob = Content()
        t = PublicationTraverser()
        request = TestRequest()
        self.assertRaises(NotFound, t.traverseName, request, ob, '@@foo')

    def testViewFound(self):
        provideAdapter(DummyViewTraverser, (Interface, Interface),
                       ITraversable, name='view')
        ob = Content()
        t = PublicationTraverser()
        request = TestRequest()
        proxy = t.traverseName(request, ob, '@@foo')
        view = removeSecurityProxy(proxy)
        self.assertTrue(proxy is not view)
        self.assertEqual(view.__class__, View)
        self.assertEqual(view.name, 'foo')

    def testDot(self):
        ob = Content()
        t = PublicationTraverser()
        request = TestRequest()
        self.assertEqual(ob, t.traverseName(request, ob, '.'))

    def testNameNotFound(self):
        ob = Content()
        t = PublicationTraverser()
        request = TestRequest()
        self.assertRaises(NotFound, t.traverseName, request, ob, 'foo')

    def testNameFound(self):
        provideAdapter(DummyPublishTraverse, (Interface, Interface),
                       IPublishTraverse)
        ob = Content()
        t = PublicationTraverser()
        request = TestRequest()
        proxy = t.traverseName(request, ob, 'foo')
        view = removeSecurityProxy(proxy)
        self.assertTrue(proxy is not view)
        self.assertEqual(view.__class__, View)
        self.assertEqual(view.name, 'foo')

    def testDirectTraversal(self):
        request = TestRequest()
        ob = DummyPublishTraverse(Content(), request)
        t = PublicationTraverser()
        proxy = t.traverseName(request, ob, 'foo')
        view = removeSecurityProxy(proxy)
        self.assertTrue(proxy is not view)
        self.assertEqual(view.__class__, View)
        self.assertEqual(view.name, 'foo')

    def testPathNotFound(self):
        ob = Content()
        t = PublicationTraverser()
        request = TestRequest()
        self.assertRaises(NotFound, t.traversePath, request, ob, 'foo/bar')

    def testPathFound(self):
        provideAdapter(DummyPublishTraverse, (Interface, Interface),
                       IPublishTraverse)
        ob = Content()
        t = PublicationTraverser()
        request = TestRequest()
        proxy = t.traversePath(request, ob, 'foo/bar')
        view = removeSecurityProxy(proxy)
        self.assertTrue(proxy is not view)
        self.assertEqual(view.__class__, View)
        self.assertEqual(view.name, 'bar')

    def testComplexPath(self):
        provideAdapter(DummyPublishTraverse, (Interface, Interface),
                       IPublishTraverse)
        ob = Content()
        t = PublicationTraverser()
        request = TestRequest()
        proxy = t.traversePath(request, ob, 'foo/../alpha//beta/./bar')
        view = removeSecurityProxy(proxy)
        self.assertTrue(proxy is not view)
        self.assertEqual(view.__class__, View)
        self.assertEqual(view.name, 'bar')

    def testTraverseRelativeURL(self):
        provideAdapter(DummyPublishTraverse, (Interface, Interface),
                       IPublishTraverse)
        provideAdapter(DummyBrowserPublisher, (Interface,),
                       IBrowserPublisher)
        ob = Content()

        t = PublicationTraverser()
        request = TestRequest()
        proxy = t.traverseRelativeURL(request, ob, 'foo/bar')
        view = removeSecurityProxy(proxy)
        self.assertTrue(proxy is not view)
        self.assertEqual(view.__class__, View)
        self.assertEqual(view.name, 'more')

    def testMissingSkin(self):
        ob = Content()
        t = PublicationTraverser()
        request = TestRequest()
        self.assertRaises(
            NotFound, t.traversePath, request, ob, '/++skin++missingskin')


    def test_traversePath_trailing_slash(self):
        class Traverser(PublicationTraverser):
            def __init__(self):
                self.names = []

            def traverseName(self, request, ob, name):
                self.names.append(name)


        t = Traverser()
        t.traversePath(None, None, 'abc/def/')
        self.assertEqual(t.names, ['abc', 'def'])

        t = Traverser()
        t.traversePath(None, None, 'abc/def///')

        # Note that only *one* trailing slash is removed
        # leaving empty trailing path segments.
        # This could be considered a bug, although no one has
        # complained yet.
        self.assertEqual(t.names, ['abc', 'def', '', ''])


    def test_traversePath_double_dots_cannot_remove(self):
        class Traverser(PublicationTraverser):
            def __init__(self):
                self.names = []

            def traverseName(self, request, ob, name):
                self.names.append(name)


        t = Traverser()
        t.traversePath(None, None, '..')
        self.assertEqual(t.names, ['..'])

    def test_traverseRelativeURL_to_no_browser_publisher(self):
        test = self
        class Traverser(PublicationTraverser):
            def traversePath(self, request, ob, path):
                return ob


        class Context(object):
            called = False
            def __conform__(self, iface):
                self.called = True
                test.assertEqual(iface, IBrowserPublisher)
                return None

        t = Traverser()
        context = Context()
        ob = t.traverseRelativeURL(None, context, None)
        self.assertIs(ob, context)

        self.assertTrue(context.called)

class TestBeforeTraverseEvent(unittest.TestCase):

    def test_interfaces(self):
        from zope.traversing.interfaces import IBeforeTraverseEvent
        from zope.traversing.interfaces import BeforeTraverseEvent
        from zope.interface.verify import verifyObject

        request = object()
        target = object()
        ob = BeforeTraverseEvent(target, request)
        self.assertIs(request, ob.request)
        self.assertIs(target, ob.object)
        verifyObject(IBeforeTraverseEvent, ob)

class IContent(Interface):
    pass

@implementer(IContent)
class Content(object):
    pass

class View(object):
    def __init__(self, name):
        self.name = name

@implementer(ITraversable)
class DummyViewTraverser(object):

    def __init__(self, content, request):
        self.content = content

    def traverse(self, name, furtherPath):
        return View(name)

@implementer(IPublishTraverse)
class DummyPublishTraverse(object):

    def __init__(self, context, request):
        pass

    def publishTraverse(self, request, name):
        return View(name)

@implementer(IBrowserPublisher)
class DummyBrowserPublisher(object):

    def __init__(self, context):
        self.context = removeSecurityProxy(context)

    def browserDefault(self, request):
        if self.context.name != 'more':
            return self.context, ['more']
        return self.context, ()
