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
"""Traverser Adapter tests (adapter.py)
"""
import unittest

import zope.component
from zope.component.testing import PlacelessSetup
from zope.interface import directlyProvides, implementedBy
from zope.interface.verify import verifyClass
from zope.location.traversing \
    import LocationPhysicallyLocatable, RootPhysicallyLocatable
from zope.location.interfaces \
    import ILocationInfo, IRoot, LocationError
from zope.security.interfaces import Unauthorized
from zope.security.checker \
    import ProxyFactory, defineChecker, CheckerPublic, Checker
from zope.security.management import newInteraction, endInteraction

from zope.traversing.adapters import Traverser, DefaultTraversable
from zope.traversing import adapters
from zope.traversing.interfaces import ITraversable, ITraverser
from zope.traversing.testing import contained, Contained

class ParticipationStub(object):

    def __init__(self, principal):
        self.principal = principal
        self.interaction = None

class C(Contained):
    def __init__(self, name):
        self.name = name

class TraverserTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        # Build up a wrapper chain
        self.root = C('root')
        self.folder = contained(C('folder'), self.root, name='folder')
        self.item = contained(C('item'), self.folder, name='item')
        self.tr = Traverser(self.item)

    def testImplementsITraverser(self):
        self.assertTrue(ITraverser.providedBy(self.tr))

    def testVerifyInterfaces(self):
        for interface in implementedBy(Traverser):
            verifyClass(interface, Traverser)

    def test_traverse_empty_path_is_context(self):
        self.assertIs(self.item, self.tr.traverse(''))

class UnrestrictedNoTraverseTests(unittest.TestCase):
    def setUp(self):
        self.root = root = C('root')
        directlyProvides(self.root, IRoot)
        self.folder = folder = C('folder')
        self.item = item = C('item')

        root.folder = folder
        folder.item = item

        self.tr = Traverser(root)

    def testNoTraversable(self):
        self.assertRaises(LocationError, self.tr.traverse,
                          'folder')

class UnrestrictedTraverseTests(PlacelessSetup, unittest.TestCase):
    def setUp(self):
        PlacelessSetup.setUp(self)

        zope.component.provideAdapter(DefaultTraversable, (None,), ITraversable)
        zope.component.provideAdapter(LocationPhysicallyLocatable, (None,),
                                      ILocationInfo)
        zope.component.provideAdapter(RootPhysicallyLocatable,
                                      (IRoot,), ILocationInfo)

        # Build up a wrapper chain
        self.root = root = C('root')
        directlyProvides(self.root, IRoot)
        self.folder = folder = contained(C('folder'), root, 'folder')
        self.item = item = contained(C('item'), folder, 'item')

        root.folder = folder
        folder.item = item

        self.tr = Traverser(root)

    def testSimplePathString(self):
        tr = self.tr
        item = self.item

        self.assertEqual(tr.traverse('/folder/item'), item)
        self.assertEqual(tr.traverse('folder/item'), item)
        self.assertEqual(tr.traverse('/folder/item/'), item)

    def testSimplePathUnicode(self):
        tr = self.tr
        item = self.item

        self.assertEqual(tr.traverse(u'/folder/item'), item)
        self.assertEqual(tr.traverse(u'folder/item'), item)
        self.assertEqual(tr.traverse(u'/folder/item/'), item)

    def testSimplePathTuple(self):
        tr = self.tr
        item = self.item

        self.assertEqual(tr.traverse(('', 'folder', 'item')), item)
        self.assertEqual(tr.traverse(('folder', 'item')), item)

    def testComplexPathString(self):
        tr = self.tr
        item = self.item

        self.assertEqual(tr.traverse('/folder/../folder/./item'), item)

    def testNotFoundDefault(self):
        self.assertEqual(self.tr.traverse('foo', 'notFound'), 'notFound')

    def testNotFoundNoDefault(self):
        self.assertRaises(LocationError, self.tr.traverse, 'foo')

    def testTraverseOldStyleClass(self):
        class AnOldStyleClass:
            x = object()
        container = {}
        container['theclass'] = AnOldStyleClass

        tr = Traverser(container)
        self.assertTrue(tr.traverse('theclass/x') is AnOldStyleClass.x)

    def testTraversingDictSeesDictAPI(self):
        adict = {
            'foo': 'bar',
            'anotherdict': {'bar': 'foo'},
            'items': '123',
            }
        tr = Traverser(adict)
        self.assertEqual(tr.traverse('items'), adict.items)
        self.assertEqual(tr.traverse('anotherdict/bar'), 'foo')
        self.assertEqual(tr.traverse('anotherdict/items'),
                         adict['anotherdict'].items)

    def testTraversingDoesntFailOnStrings(self):
        adict = {'foo': 'bar'}
        tr = Traverser(adict)
        # This used to raise type error before
        self.assertRaises(LocationError, tr.traverse, 'foo/baz')


class ExceptionRaiser(C):
    @property
    def valueerror(self):
        raise ValueError('booom')

    @property
    def attributeerror(self):
        raise AttributeError('booom')


class RestrictedTraverseTests(PlacelessSetup, unittest.TestCase):
    _oldPolicy = None
    _deniedNames = ()

    def setUp(self):
        PlacelessSetup.setUp(self)

        zope.component.provideAdapter(DefaultTraversable, (None,), ITraversable)
        zope.component.provideAdapter(LocationPhysicallyLocatable, (None,),
                                      ILocationInfo)
        zope.component.provideAdapter(RootPhysicallyLocatable,
                                      (IRoot,), ILocationInfo)

        self.root = root = C('root')
        directlyProvides(root, IRoot)
        self.folder = folder = contained(C('folder'), root, 'folder')
        self.item = item = contained(C('item'), folder, 'item')

        root.folder = folder
        folder.item = item

        self.tr = Traverser(ProxyFactory(root))

    def testAllAllowed(self):
        defineChecker(C,
                      Checker({
                          'folder': CheckerPublic,
                          'item': CheckerPublic,
                      }))
        tr = Traverser(ProxyFactory(self.root))
        item = self.item

        self.assertEqual(tr.traverse(('', 'folder', 'item')), item)
        self.assertEqual(tr.traverse(('folder', 'item')), item)

    def testItemDenied(self):
        endInteraction()
        newInteraction(ParticipationStub('no one'))
        defineChecker(C, Checker({'item': 'Waaaa', 'folder': CheckerPublic}))
        tr = Traverser(ProxyFactory(self.root))
        folder = self.folder

        self.assertRaises(Unauthorized, tr.traverse,
                          ('', 'folder', 'item'))
        self.assertRaises(Unauthorized, tr.traverse,
                          ('folder', 'item'))
        self.assertEqual(tr.traverse(('', 'folder')), folder)
        self.assertEqual(tr.traverse(('folder', '..', 'folder')),
                         folder)
        self.assertEqual(tr.traverse(('folder',)), folder)

    def testException(self):
        # nail the fact that AttributeError raised in a @property
        # decorated method gets masked by traversal
        self.root.foobar = ExceptionRaiser('foobar')

        endInteraction()
        newInteraction(ParticipationStub('no one'))
        tr = Traverser(self.root)

        # AttributeError becomes LocationError if there's no __getitem__
        # on the object
        self.assertRaises(LocationError, tr.traverse,
                          ('foobar', 'attributeerror'))
        # Other exceptions raised as usual
        self.assertRaises(ValueError, tr.traverse,
                          ('foobar', 'valueerror'))


class DefaultTraversableTests(unittest.TestCase):
    def testImplementsITraversable(self):
        self.assertTrue(ITraversable.providedBy(DefaultTraversable(None)))

    def testVerifyInterfaces(self):
        for interface in implementedBy(DefaultTraversable):
            verifyClass(interface, DefaultTraversable)

    def testAttributeTraverse(self):
        root = C('root')
        item = C('item')
        root.item = item
        df = DefaultTraversable(root)

        further = []
        next = df.traverse('item', further)
        self.assertTrue(next is item)
        self.assertEqual(further, [])

    def testDictionaryTraverse(self):
        dict = {}
        foo = C('foo')
        dict['foo'] = foo
        df = DefaultTraversable(dict)

        further = []
        next = df.traverse('foo', further)
        self.assertTrue(next is foo)
        self.assertEqual(further, [])

    def testNotFound(self):
        df = DefaultTraversable(C('dummy'))

        self.assertRaises(LocationError, df.traverse, 'bar', [])

    def testUnicodeTraversal(self):
        df = DefaultTraversable(object())
        self.assertRaises(LocationError, df.traverse, u'\u2019', ())


class TestFunctions(unittest.TestCase):

    def test_traversePathElement_UnicodeEncodeError_with_default(self):
        test = self
        class Traversable(object):
            called = False
            fail = test.fail
            def traverse(self, nm, further_path):
                self.called = True
                u'\xff'.encode("ascii")
                self.fail("Should not be reached")

        t = Traversable()
        self.assertIs(self,
                      adapters.traversePathElement(None, None, (),
                                                   default=self,
                                                   traversable=t))
        self.assertTrue(t.called)


    def test_traversePathElement_LocationError_with_default(self):
        class Traversable(object):
            called = False
            def traverse(self, nm, further_path):
                self.called = True
                raise LocationError()

        t = Traversable()
        self.assertIs(self,
                      adapters.traversePathElement(None, None, (),
                                                   default=self,
                                                   traversable=t))
        self.assertTrue(t.called)
