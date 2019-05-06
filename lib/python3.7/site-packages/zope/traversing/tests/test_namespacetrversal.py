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
"""Traversal Namespace Tests
"""
import re
import unittest
from doctest import DocTestSuite

from zope import interface
from zope import component
from zope.location.interfaces import LocationError
from zope.traversing import namespace

from zope.component.testing import PlacelessSetup
from zope.component.testing import setUp, tearDown
from zope.testing.renormalizing import RENormalizing


class TestSimpleHandler(unittest.TestCase):

    def test_constructor(self):
        h = namespace.SimpleHandler(42)
        self.assertEqual(h.context, 42)

        h = namespace.SimpleHandler(42, 43)
        self.assertEqual(h.context, 42)

class TestFunctions(unittest.TestCase):

    def test_getResource_not_found(self):
        with self.assertRaises(LocationError):
            namespace.getResource(None, '', None)


class TestAcquire(unittest.TestCase):

    def test_excessive_depth_on_path_extension(self):
        from zope.traversing.interfaces import ITraversable
        from zope.traversing.namespace import ExcessiveDepth

        @interface.implementer(ITraversable)
        class Context(object):

            max_call_count = 200

            def traverse(self, name, path):
                if self.max_call_count:
                    path.append("I added something")
                self.max_call_count -= 1

        acq = namespace.acquire(Context(), None)
        with self.assertRaises(ExcessiveDepth):
            acq.traverse(None, None)


class TestEtc(PlacelessSetup, unittest.TestCase):

    def test_traverse_non_site_name(self):
        with self.assertRaises(LocationError) as ctx:
            namespace.etc(None, None).traverse('foobar', ())

        ex = ctx.exception
        self.assertEqual((None, 'foobar'), ex.args)

    def test_traverse_site_no_manager(self):
        test = self
        class Context(object):
            def __getattribute__(self, name):
                test.assertEqual(name, 'getSiteManager')
                return None

        context = Context()
        with self.assertRaises(LocationError) as ctx:
            namespace.etc(context, None).traverse('site', ())

        ex = ctx.exception
        self.assertEqual((context, 'site'), ex.args)

    def test_traverse_site_lookup_error(self):
        class Context(object):
            called = False
            def getSiteManager(self):
                self.called = True
                from zope.component import ComponentLookupError
                raise ComponentLookupError()

        context = Context()
        with self.assertRaises(LocationError) as ctx:
            namespace.etc(context, None).traverse('site', ())

        ex = ctx.exception
        self.assertEqual((context, 'site'), ex.args)
        self.assertTrue(context.called)

    def test_traverse_utility(self):
        from zope.traversing.interfaces import IEtcNamespace
        component.provideUtility(self, provides=IEtcNamespace, name='my etc name')

        result = namespace.etc(None, None).traverse('my etc name', ())
        self.assertIs(result, self)


class TestView(unittest.TestCase):

    def test_not_found(self):
        with self.assertRaises(LocationError) as ctx:
            namespace.view(None, None).traverse('name', ())

        ex = ctx.exception
        self.assertEqual((None, 'name'), ex.args)


class TestVh(unittest.TestCase):

    assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegex',
                                getattr(unittest.TestCase, 'assertRaisesRegexp'))

    def test_invalid_vh(self):
        with self.assertRaisesRegex(ValueError,
                                    'Vhost directive should have the form'):
            namespace.vh(None, None).traverse(u'invalid name', ())

def test_suite():
    checker = RENormalizing([
        # Python 3 includes module name in exceptions
        (re.compile(r"zope.location.interfaces.LocationError"),
         "LocationError"),
    ])

    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTest(DocTestSuite(
        'zope.traversing.namespace',
        setUp=setUp, tearDown=tearDown,
        checker=checker))
    return suite
