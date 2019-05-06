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
"""Test traversal convenience functions.
"""
import unittest

from zope import interface
import zope.component
from zope.component.testing import PlacelessSetup
from zope.location.traversing \
    import LocationPhysicallyLocatable, RootPhysicallyLocatable
from zope.location.interfaces import ILocationInfo, IRoot, LocationError

from zope.traversing.adapters import Traverser, DefaultTraversable
from zope.traversing.interfaces import ITraversable, ITraverser
from zope.traversing.testing import contained

class C(object):
    __parent__ = None
    __name__ = None
    def __init__(self, name):
        self.name = name



class TestFunctional(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        # Build up a wrapper chain
        root = C('root')
        interface.directlyProvides(root, IRoot)
        folder = C('folder')
        item = C('item')

        self.root = root  # root is not usually wrapped
        self.folder = contained(folder, self.root, name='folder')
        self.item = contained(item, self.folder, name='item')
        self.unwrapped_item = item
        self.broken_chain_folder = contained(folder, None)
        self.broken_chain_item = contained(
            item,
            self.broken_chain_folder,
            name='item'
        )
        root.folder = folder
        folder.item = item

        self.tr = Traverser(root)
        zope.component.provideAdapter(Traverser, (None,), ITraverser)
        zope.component.provideAdapter(DefaultTraversable, (None,), ITraversable)
        zope.component.provideAdapter(LocationPhysicallyLocatable, (None,),
                                      ILocationInfo)
        zope.component.provideAdapter(RootPhysicallyLocatable,
                                      (IRoot,), ILocationInfo)

    def testTraverse(self):
        from zope.traversing.api import traverse
        self.assertEqual(
            traverse(self.item, '/folder/item'),
            self.tr.traverse('/folder/item')
            )

    def test_traverse_with_default(self):
        from zope.traversing.api import traverse
        self.assertIs(
            traverse(self.item, '/no/path', self),
            self
        )

    def testTraverseFromUnwrapped(self):
        from zope.traversing.api import traverse
        self.assertRaises(
            TypeError,
            traverse,
            self.unwrapped_item, '/folder/item'
            )

    def testTraverseName(self):
        from zope.traversing.api import traverseName
        self.assertEqual(
            traverseName(self.folder, 'item'),
            self.tr.traverse('/folder/item')
        )
        self.assertEqual(
            traverseName(self.item, '.'),
            self.tr.traverse('/folder/item')
        )
        self.assertEqual(
            traverseName(self.item, '..'),
            self.tr.traverse('/folder')
        )
        self.assertEqual(
            traverseName(self.folder, 'item', default=self),
            self.tr.traverse('/folder/item')
        )
        self.assertIs(
            traverseName(self.folder, 'nothing', default=self),
            self,
        )

        # TODO test that ++names++ and @@names work too

    def testTraverseNameBadValue(self):
        from zope.traversing.api import traverseName
        self.assertRaises(
            LocationError,
            traverseName,
            self.folder, '../root'
            )
        self.assertRaises(
            LocationError,
            traverseName,
            self.folder, '/root'
            )
        self.assertRaises(
            LocationError,
            traverseName,
            self.folder, './item'
            )

    def testTraverseNameUnicode(self):
        from zope.traversing.api import traverseName
        from zope.interface import implementer

        @implementer(ITraversable)
        class BrokenTraversable(object):
            def traverse(self, name, furtherPath):
                getattr(self, u'\u2019', None)
                # The above actually works on Python 3
                raise unittest.SkipTest("Unicode attrs legal on Py3")

        self.assertRaises(
            LocationError,
            traverseName,
            BrokenTraversable(), '')


    def testGetName(self):
        from zope.traversing.api import getName
        self.assertEqual(
            getName(self.item),
            'item'
            )

    def testGetParent(self):
        from zope.traversing.api import getParent
        self.assertEqual(
            getParent(self.item),
            self.folder
            )

    def testGetParentFromRoot(self):
        from zope.traversing.api import getParent
        self.assertEqual(
            getParent(self.root),
            None
            )

    def testGetParentBrokenChain(self):
        from zope.traversing.api import getParent
        self.assertRaises(
            TypeError,
            getParent,
            self.broken_chain_folder
            )

    def testGetParentFromUnwrapped(self):
        from zope.traversing.api import getParent
        self.assertRaises(
            TypeError,
            getParent,
            self.unwrapped_item
            )

    def testGetParents(self):
        from zope.traversing.api import getParents
        self.assertEqual(
            getParents(self.item),
            [self.folder, self.root]
            )

    def testGetParentsBrokenChain(self):
        from zope.traversing.api import getParents
        self.assertRaises(
            TypeError,
            getParents,
            self.broken_chain_item
            )

    def testGetPath(self):
        from zope.traversing.api import getPath
        self.assertEqual(
            getPath(self.item),
            u'/folder/item'
            )

    def testGetPathOfRoot(self):
        from zope.traversing.api import getPath
        self.assertEqual(
            getPath(self.root),
            u'/',
            )

    def testGetNameOfRoot(self):
        from zope.traversing.api import getName
        self.assertEqual(
            getName(self.root),
            u'',
            )

    def testGetRoot(self):
        from zope.traversing.api import getRoot
        self.assertEqual(
            getRoot(self.item),
            self.root
            )

    def testCanonicalPath(self):

        _bad_locations = (
            (ValueError, '\xa323'),
            (ValueError, ''),
            (ValueError, '//'),
            (ValueError, '/foo//bar'),

            # regarding the next two errors:
            # having a trailing slash on a location is undefined.
            # we might want to give it a particular meaning for zope3 later
            # for now, it is an invalid location identifier
            (ValueError, '/foo/bar/'),
            (ValueError, 'foo/bar/'),

            (IndexError, '/a/../..'),
            (ValueError, '/a//v'),
            )

        # sequence of N-tuples:
        #   (loc_returned_as_string, input, input, ...)
        # The string and tuple are tested as input as well as being the
        # specification for output.

        _good_locations = (
            # location returned as string
            (u'/xx/yy/zz',
             # arguments to try in addition to the above
             '/xx/yy/zz',
             '/xx/./yy/ww/../zz',
            ),
            (u'/xx/yy/zz',
             '/xx/yy/zz',
            ),
            (u'/xx',
             '/xx',
            ),
            (u'/',
             '/',
             self.root,
            ),
        )

        from zope.traversing.api import canonicalPath

        for error_type, value in _bad_locations:
            self.assertRaises(error_type, canonicalPath, value)

        for spec in _good_locations:
            correct_answer = spec[0]
            for argument in spec:
                self.assertEqual(canonicalPath(argument), correct_answer,
                                 "failure on %s" % argument)


    def test_normalizePath(self):

        _bad_locations = (
            (ValueError, '//'),
            (ValueError, '/foo//bar'),
            (IndexError, '/a/../..'),
            (IndexError, '/a/./../..'),
            )

        # sequence of N-tuples:
        #   (loc_returned_as_string, input, input, ...)
        # The string and tuple are tested as input as well as being the
        # specification for output.

        _good_locations = (
            # location returned as string
            ('/xx/yy/zz',
             # arguments to try in addition to the above
             '/xx/yy/zz',
             '/xx/./yy/ww/../zz',
             '/xx/./yy/ww/./../zz',
            ),
            ('xx/yy/zz',
             # arguments to try in addition to the above
             'xx/yy/zz',
             'xx/./yy/ww/../zz',
             'xx/./yy/ww/./../zz',
            ),
            ('/xx/yy/zz',
             '/xx/yy/zz',
            ),
            ('/xx',
             '/xx',
            ),
            ('/',
             '/',
            ),
        )


        from zope.traversing.api import _normalizePath

        for error_type, value in _bad_locations:
            self.assertRaises(error_type, _normalizePath, value)

        for spec in _good_locations:
            correct_answer = spec[0]
            for argument in spec:
                self.assertEqual(_normalizePath(argument), correct_answer,
                                 "failure on %s" % argument)

    def test_joinPath_slashes(self):
        from zope.traversing.api import joinPath
        path = u'/'
        args = ('/test', 'bla', '/foo', 'bar')
        self.assertRaises(ValueError, joinPath, path, *args)

        args = ('/test', 'bla', 'foo/', '/bar')
        self.assertRaises(ValueError, joinPath, path, *args)

    def test_joinPath(self):
        from zope.traversing.api import joinPath
        path = u'/bla'
        args = ('foo', 'bar', 'baz', 'bone')
        self.assertEqual(joinPath(path, *args), u'/bla/foo/bar/baz/bone')

        path = u'bla'
        args = ('foo', 'bar', 'baz', 'bone')
        self.assertEqual(joinPath(path, *args), u'bla/foo/bar/baz/bone')

        path = u'bla'
        args = ('foo', 'bar/baz', 'bone')
        self.assertEqual(joinPath(path, *args), u'bla/foo/bar/baz/bone')

        path = u'bla/'
        args = ('foo', 'bar', 'baz', 'bone')
        self.assertRaises(ValueError, joinPath, path, *args)

    def test_joinPath_normalize(self):
        from zope.traversing.api import joinPath
        path = u'/bla'
        args = ('foo', 'bar', '..', 'baz', 'bone')
        self.assertEqual(joinPath(path, *args), u'/bla/foo/baz/bone')

        path = u'bla'
        args = ('foo', 'bar', '.', 'baz', 'bone')
        self.assertEqual(joinPath(path, *args), u'bla/foo/bar/baz/bone')

        path = u'/'
        args = ('foo', 'bar', '.', 'baz', 'bone')
        self.assertEqual(joinPath(path, *args), u'/foo/bar/baz/bone')

    def test_joinPath_empty_args(self):
        from zope.traversing.api import joinPath
        path = 'abc'
        self.assertEqual(joinPath(path), u'abc')


class TestStandalone(unittest.TestCase):
    # Unlike TestFunctional, we don't register gobs of
    # adapters, making these tests more self-contained

    assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegex',
                                getattr(unittest.TestCase, 'assertRaisesRegexp'))

    def test_getParent_no_location_info(self):
        from zope.traversing.api import getParent
        test = self
        class Context(object):
            called = False
            def __conform__(self, iface):
                self.called = True
                test.assertEqual(iface, ILocationInfo)
                raise TypeError()

        context = Context()
        with self.assertRaisesRegex(TypeError,
                                    "Not enough context"):
            getParent(context)

        self.assertTrue(context.called)
        context.called = False

        # Now give it a parent
        context.__parent__ = self
        self.assertIs(self, getParent(context))

        self.assertTrue(context.called)
        context.called = False

        # Now if it's a root, it has no parent
        interface.alsoProvides(context, IRoot)
        self.assertIsNone(getParent(context))
