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
"""Functional tests for virtual hosting.
"""
import os
import unittest
from io import StringIO

import transaction

import zope.component
import zope.interface
from zope.browserresource.resource import Resource
from zope.configuration import xmlconfig
from zope.location.interfaces import IRoot
from zope.publisher.browser import BrowserRequest, BrowserView
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.publish import publish
from zope.publisher.skinnable import setDefaultSkin
from zope.security.checker import defineChecker, NamesChecker, NoProxy
from zope.security.checker import _checkers, undefineChecker
from zope.tales import expressions
from zope.tales.tales import ExpressionEngine
from zope.testing.cleanup import cleanUp

from zope.traversing.adapters import traversePathElement
from zope.traversing.api import traverse
from zope.traversing.testing import browserResource, Contained


class MyObj(Contained):
    def __getitem__(self, key):
        return traverse(self, '/foo/bar/' + key)

class IFolder(zope.interface.Interface):
    pass

@zope.interface.implementer(IFolder, IBrowserPublisher)
class Folder(Contained, dict):
    def __init__(self):
        dict.__init__(self, {})

    def __setitem__(self, name, value):
        value.__parent__ = self
        value.__name__ = name
        dict.__setitem__(self, name, value)

    def publishTraverse(self, request, name):
        subob = self.get(name, None)
        if subob is None:
            raise NotFound(self.context, name, request) # pragma: no cover
        return subob


@zope.interface.implementer(IRoot)
class RootFolder(Folder):
    pass


# Copy some code from zope.pagetemplate to avoid the depedency (break circle)
class ZopeTraverser(object):

    def __call__(self, object, path_items, econtext):
        request = econtext._vars_stack[0].get('request', None)
        path_items = list(path_items)
        path_items.reverse()

        while path_items:
            name = path_items.pop()
            assert getattr(object, '__class__', None) != dict
            object = traversePathElement(object, name, path_items,
                                         request=request)
        return object
zopeTraverser = ZopeTraverser()

class PathExpr(expressions.PathExpr):

    def __init__(self, name, expr, engine):
        super(PathExpr, self).__init__(name, expr, engine, zopeTraverser)

def Engine():
    e = ExpressionEngine()
    for pt in PathExpr._default_type_names:
        e.registerType(pt, PathExpr)
    return e

Engine = Engine()

class MyTalesPage(object):

    def __init__(self, source):
        self.source = source

    def pt_getContext(self, instance, request, **_kw):
        # instance is a View component
        namespace = {}
        namespace['template'] = self
        namespace['request'] = request
        namespace['container'] = namespace['context'] = instance
        return namespace

    def render(self, instance, request, *args, **kw):
        context = self.pt_getContext(instance, request)
        code = Engine.compile(self.source)
        return str(code(Engine.getContext(context)))


class MyPageEval(BrowserView):

    def __call__(self, **kw):
        """Call a Page Template"""
        template = self.context
        request = self.request
        return template.render(template.__parent__, request, **kw)

    index = __call__

class MyFolderPage(BrowserView):

    def __call__(self, **kw):
        """My folder page"""
        self.request.response.redirect('index.html')
        return ''

    index = __call__


class TestVirtualHosting(unittest.TestCase):

    def setUp(self):
        f = os.path.join(os.path.split(__file__)[0], 'ftesting.zcml')
        xmlconfig.file(f)
        defineChecker(MyObj, NoProxy)
        defineChecker(RootFolder, NoProxy)
        defineChecker(Folder, NoProxy)
        self.app = RootFolder()

    def tearDown(self):
        undefineChecker(MyObj)
        undefineChecker(RootFolder)
        undefineChecker(Folder)
        cleanUp()

    def makeRequest(self, path=''):
        env = {"HTTP_HOST": 'localhost',
               "HTTP_REFERER": 'localhost'}
        p = path.split('?')
        if len(p) == 1:
            env['PATH_INFO'] = p[0]

        request = BrowserRequest(StringIO(u''), env)
        request.setPublication(DummyPublication(self.app))
        setDefaultSkin(request)
        return request

    def publish(self, path):
        return publish(self.makeRequest(path)).response

    def test_request_url(self):
        self.addPage('/pt', u'request/URL')
        self.verify('/pt', 'http://localhost/pt/index.html')
        self.verify('/++vh++/++/pt',
                    'http://localhost/pt/index.html')
        self.verify('/++vh++https:localhost:443/++/pt',
                    'https://localhost/pt/index.html')
        self.verify('/++vh++https:localhost:443/fake/folders/++/pt',
                    'https://localhost/fake/folders/pt/index.html')

        self.addPage('/foo/bar/pt', u'request/URL')
        self.verify('/foo/bar/pt', 'http://localhost/foo/bar/pt/index.html')
        self.verify('/foo/bar/++vh++/++/pt',
                    'http://localhost/pt/index.html')
        self.verify('/foo/bar/++vh++https:localhost:443/++/pt',
                    'https://localhost/pt/index.html')
        self.verify('/foo/++vh++https:localhost:443/fake/folders/++/bar/pt',
                    'https://localhost/fake/folders/bar/pt/index.html')

    def test_request_redirect(self):
        self.addPage('/foo/index.html', u'Spam')
        self.verifyRedirect('/foo', 'http://localhost/foo/index.html')
        self.verifyRedirect('/++vh++https:localhost:443/++/foo',
                            'https://localhost/foo/index.html')
        self.verifyRedirect('/foo/++vh++https:localhost:443/bar/++',
                            'https://localhost/bar/index.html')

    def test_absolute_url(self):
        self.addPage('/pt', u'context/@@absolute_url')
        self.verify('/pt', 'http://localhost')
        self.verify('/++vh++/++/pt',
                    'http://localhost')
        self.verify('/++vh++https:localhost:443/++/pt',
                    'https://localhost')
        self.verify('/++vh++https:localhost:443/fake/folders/++/pt',
                    'https://localhost/fake/folders')

        self.addPage('/foo/bar/pt',
                     u'context/@@absolute_url')
        self.verify('/foo/bar/pt', 'http://localhost/foo/bar')
        self.verify('/foo/bar/++vh++/++/pt',
                    'http://localhost')
        self.verify('/foo/bar/++vh++https:localhost:443/++/pt',
                    'https://localhost')
        self.verify('/foo/++vh++https:localhost:443/fake/folders/++/bar/pt',
                    'https://localhost/fake/folders/bar')

    def test_absolute_url_absolute_traverse(self):
        self.createObject('/foo/bar/obj', MyObj())
        self.addPage('/foo/bar/pt',
                     u'container/obj/pt/@@absolute_url')
        self.verify('/foo/bar/pt', 'http://localhost/foo/bar/pt')
        self.verify('/foo/++vh++https:localhost:443/++/bar/pt',
                    'https://localhost/bar/pt')

    def test_resources(self):
        browserResource('quux', Resource)
        # Only register the checker once, so that multiple test runs pass.
        if Resource not in _checkers:
            defineChecker(Resource, NamesChecker(['__call__']))
        self.addPage(u'/foo/bar/pt',
                     u'context/++resource++quux')
        self.verify(u'/foo/bar/pt', u'http://localhost/@@/quux')
        self.verify(u'/foo/++vh++https:localhost:443/fake/folders/++/bar/pt',
                    u'https://localhost/fake/folders/@@/quux')

    def createFolders(self, path):
        """addFolders('/a/b/c/d') would traverse and/or create three nested
        folders (a, b, c) and return a tuple (c, 'd') where c is a Folder
        instance at /a/b/c."""
        folder = self.app  #self.connection.root()['Application']
        if path[0] == '/':
            path = path[1:]
        path = path.split('/')
        for id in path[:-1]:
            try:
                folder = folder[id]
            except KeyError:
                folder[id] = Folder()
                folder = folder[id]
        return folder, path[-1]

    def createObject(self, path, obj):
        folder, id = self.createFolders(path)
        folder[id] = obj
        transaction.commit()

    def addPage(self, path, content):
        page = MyTalesPage(content)
        self.createObject(path, page)

    def verify(self, path, content):
        result = self.publish(path)
        self.assertEqual(result.getStatus(), 200)
        self.assertEqual(result.consumeBody().decode(), content)

    def verifyRedirect(self, path, location):
        result = self.publish(path)
        self.assertEqual(result.getStatus(), 302)
        self.assertEqual(result.getHeader('Location'), location)


class DummyPublication(object):

    def __init__(self, app):
        self.app = app

    def beforeTraversal(self, request):
        """Pre-traversal hook.

        This is called *once* before any traversal has been done.
        """

    def getApplication(self, request):
        """Returns the object where traversal should commence.
        """
        return self.app

    def callTraversalHooks(self, request, ob):
        """Invokes any traversal hooks associated with the object.

        This is called before traversing each object.  The ob argument
        is the object that is about to be traversed.
        """

    def traverseName(self, request, ob, name):
        """Traverses to the next object.

        Name must be an ASCII string or Unicode object."""
        if name == 'index.html':
            from zope.component import getMultiAdapter
            view = getMultiAdapter((ob, request), name=name)
            return view

        from zope.traversing.publicationtraverse import PublicationTraverserWithoutProxy
        t = PublicationTraverserWithoutProxy()
        return t.traverseName(request, ob, name)

    def afterTraversal(self, request, ob):
        """Post-traversal hook.

        This is called after all traversal.
        """

    def callObject(self, request, ob):
        """Call the object, returning the result.

        For GET/POST this means calling it, but for other methods
        (including those of WebDAV and FTP) this might mean invoking
        a method of an adapter.
        """
        from zope.publisher.publish import mapply
        return mapply(ob, request.getPositionalArguments(), request)

    def afterCall(self, request, ob):
        """Post-callObject hook (if it was successful).
        """

    def handleException(self, ob, request, exc_info, retry_allowed=1): # pragma: no cover
        """Handle an exception

        Either:
        - sets the body of the response, request.response, or
        - raises a Retry exception, or
        - throws another exception, which is a Bad Thing.
        """
        import traceback
        traceback.print_exception(*exc_info)

    def endRequest(self, request, ob):
        """Do any end-of-request cleanup
        """

    def getDefaultTraversal(self, request, ob):
        if hasattr(ob, 'index'):
            return ob, ()
        return ob, ('index.html',)
