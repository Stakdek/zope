##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
import unittest


class ConformsToILocationInfo(object):

    def test_class_conforms_to_ILocationInfo(self):
        from zope.interface.verify import verifyClass
        from zope.location.interfaces import ILocationInfo
        verifyClass(ILocationInfo, self._getTargetClass())

    def test_instance_conforms_to_ILocationInfo(self):
        from zope.interface.verify import verifyObject
        from zope.location.interfaces import ILocationInfo
        verifyObject(ILocationInfo, self._makeOne())


class LocationPhysicallyLocatableTests(
                    unittest.TestCase, ConformsToILocationInfo):

    def _getTargetClass(self):
        from zope.location.traversing import LocationPhysicallyLocatable
        return LocationPhysicallyLocatable

    def _makeOne(self, obj=None):
        if obj is None:
            obj = object()
        return self._getTargetClass()(obj)

    def test_getRoot_not_location_aware(self):
        proxy = self._makeOne(object())
        self.assertRaises(AttributeError, proxy.getRoot)

    def test_getRoot_location_but_no_IRoot(self):
        class Dummy(object):
            __parent__ = None
        proxy = self._makeOne(Dummy())
        self.assertRaises(TypeError, proxy.getRoot)

    def test_getRoot_wo_cycle(self):
        from zope.interface import directlyProvides
        from zope.location.interfaces import IRoot
        class Dummy(object):
            __parent__ = None
        one = Dummy()
        directlyProvides(one, IRoot)
        two = Dummy()
        two.__parent__ = one
        three = Dummy()
        three.__parent__ = two
        proxy = self._makeOne(three)
        self.assertTrue(proxy.getRoot() is one)

    def test_getRoot_w_cycle(self):
        class Dummy(object):
            __parent__ = None
        one = Dummy()
        two = Dummy()
        two.__parent__ = one
        three = Dummy()
        three.__parent__ = two
        one.__parent__ = three
        proxy = self._makeOne(two)
        self.assertRaises(TypeError, proxy.getRoot)

    def test_getPath_not_location_aware(self):
        proxy = self._makeOne(object())
        self.assertRaises(AttributeError, proxy.getPath)

    def test_getPath_location_but_no_IRoot(self):
        class Dummy(object):
            __parent__ = __name__ = None
        proxy = self._makeOne(Dummy())
        self.assertRaises(TypeError, proxy.getPath)

    def test_getPath_at_root(self):
        from zope.interface import directlyProvides
        from zope.location.interfaces import IRoot
        class Dummy(object):
            __parent__ = __name__ = None
        one = Dummy()
        directlyProvides(one, IRoot)
        proxy = self._makeOne(one)
        self.assertEqual(proxy.getPath(), '/')

    def test_getPath_wo_cycle(self):
        from zope.interface import directlyProvides
        from zope.location.interfaces import IRoot
        class Dummy(object):
            __parent__ = __name__ = None
        one = Dummy()
        directlyProvides(one, IRoot)
        two = Dummy()
        two.__parent__ = one
        two.__name__ = 'two'
        three = Dummy()
        three.__parent__ = two
        three.__name__ = 'three'
        proxy = self._makeOne(three)
        self.assertEqual(proxy.getPath(), '/two/three')

    def test_getPath_w_cycle(self):
        class Dummy(object):
            __parent__ = __name__ = None
        one = Dummy()
        two = Dummy()
        two.__parent__ = one
        two.__name__ = 'two'
        three = Dummy()
        three.__parent__ = two
        three.__name__ = 'three'
        one.__parent__ = three
        proxy = self._makeOne(two)
        self.assertRaises(TypeError, proxy.getPath)

    def test_getParent_not_location_aware(self):
        proxy = self._makeOne(object())
        self.assertRaises(TypeError, proxy.getParent)

    def test_getParent_location_but_no_IRoot(self):
        class Dummy(object):
            __parent__ = __name__ = None
        proxy = self._makeOne(Dummy())
        self.assertRaises(TypeError, proxy.getParent)

    def test_getParent_at_root(self):
        from zope.interface import directlyProvides
        from zope.location.interfaces import IRoot
        class Dummy(object):
            __parent__ = __name__ = None
        one = Dummy()
        directlyProvides(one, IRoot)
        proxy = self._makeOne(one)
        self.assertRaises(TypeError, proxy.getParent)

    def test_getParent_wo_cycle(self):
        from zope.interface import directlyProvides
        from zope.location.interfaces import IRoot
        class Dummy(object):
            __parent__ = __name__ = None
        one = Dummy()
        directlyProvides(one, IRoot)
        two = Dummy()
        two.__parent__ = one
        two.__name__ = 'two'
        three = Dummy()
        three.__parent__ = two
        three.__name__ = 'three'
        proxy = self._makeOne(three)
        self.assertTrue(proxy.getParent() is two)

    def test_getParents_not_location_aware(self):
        proxy = self._makeOne(object())
        self.assertRaises(TypeError, proxy.getParents)

    def test_getParents_location_but_no_IRoot(self):
        class Dummy(object):
            __parent__ = __name__ = None
        proxy = self._makeOne(Dummy())
        self.assertRaises(TypeError, proxy.getParents)

    def test_getParents_at_root(self):
        from zope.interface import directlyProvides
        from zope.location.interfaces import IRoot
        class Dummy(object):
            __parent__ = __name__ = None
        one = Dummy()
        directlyProvides(one, IRoot)
        proxy = self._makeOne(one)
        self.assertRaises(TypeError, proxy.getParents)

    def test_getParents_wo_cycle(self):
        from zope.interface import directlyProvides
        from zope.location.interfaces import IRoot
        class Dummy(object):
            __parent__ = __name__ = None
        one = Dummy()
        directlyProvides(one, IRoot)
        two = Dummy()
        two.__parent__ = one
        two.__name__ = 'two'
        three = Dummy()
        three.__parent__ = two
        three.__name__ = 'three'
        proxy = self._makeOne(three)
        self.assertEqual(proxy.getParents(), [two, one])

    def test_getName_not_location_aware(self):
        proxy = self._makeOne(object())
        self.assertRaises(AttributeError, proxy.getName)

    def test_getName_location(self):
        class Dummy(object):
            __name__ = None
        proxy = self._makeOne(Dummy())
        self.assertEqual(proxy.getName(), None)

    def test_getName_location_w_name(self):
        class Dummy(object):
            __name__ = 'name'
        proxy = self._makeOne(Dummy())
        self.assertEqual(proxy.getName(), 'name')

    def test_getNearestSite_context_is_site(self):
        from zope.location.interfaces import ISite # zope.component, if present
        from zope.interface import directlyProvides
        class Dummy(object):
            pass
        context = Dummy()
        directlyProvides(context, ISite)
        proxy = self._makeOne(context)
        self.assertTrue(proxy.getNearestSite() is context)

    def test_getNearestSite_ancestor_is_site(self):
        from zope.location.interfaces import ISite # zope.component, if present
        from zope.interface import directlyProvides
        from zope.location.interfaces import IRoot
        class Dummy(object):
            pass
        one = Dummy()
        directlyProvides(one, (ISite, IRoot))
        two = Dummy()
        two.__parent__ = one
        two.__name__ = 'two'
        three = Dummy()
        three.__parent__ = two
        three.__name__ = 'three'
        proxy = self._makeOne(three)
        self.assertTrue(proxy.getNearestSite() is one)

    def test_getNearestSite_no_site(self):
        from zope.interface import directlyProvides
        from zope.location.interfaces import IRoot
        class Dummy(object):
            __parent__ = __name__ = None
        one = Dummy()
        directlyProvides(one, IRoot)
        two = Dummy()
        two.__parent__ = one
        two.__name__ = 'two'
        three = Dummy()
        three.__parent__ = two
        three.__name__ = 'three'
        proxy = self._makeOne(three)
        self.assertTrue(proxy.getNearestSite() is one)


class RootPhysicallyLocatableTests(
                    unittest.TestCase, ConformsToILocationInfo):

    def _getTargetClass(self):
        from zope.location.traversing import RootPhysicallyLocatable
        return RootPhysicallyLocatable

    def _makeOne(self, obj=None):
        if obj is None:
            obj = object()
        return self._getTargetClass()(obj)

    def test_getRoot(self):
        context = object()
        proxy = self._makeOne(context)
        self.assertTrue(proxy.getRoot() is context)

    def test_getPath(self):
        context = object()
        proxy = self._makeOne(context)
        self.assertEqual(proxy.getPath(), '/')

    def test_getParent(self):
        context = object()
        proxy = self._makeOne(context)
        self.assertEqual(proxy.getParent(), None)

    def test_getParents(self):
        context = object()
        proxy = self._makeOne(context)
        self.assertEqual(proxy.getParents(), [])

    def test_getName(self):
        context = object()
        proxy = self._makeOne(context)
        self.assertEqual(proxy.getName(), '')

    def test_getNearestSite(self):
        context = object()
        proxy = self._makeOne(context)
        self.assertTrue(proxy.getNearestSite() is context)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LocationPhysicallyLocatableTests),
        unittest.makeSuite(RootPhysicallyLocatableTests),
    ))
