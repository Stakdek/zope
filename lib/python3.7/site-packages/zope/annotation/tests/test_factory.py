##############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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

from zope.annotation import factory

from zope import interface
from zope import component
from zope.location.interfaces import ILocation

from zope.annotation.interfaces import IAnnotations


class ITarget(interface.Interface):
    pass

class IContext(IAnnotations):
    pass

@interface.implementer(ITarget)
@component.adapter(IContext)
class Target(object):
    pass

@interface.implementer(IContext)
class Context(dict):
    pass

class TestFactory(unittest.TestCase):

    assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegex',
                                getattr(unittest.TestCase, 'assertRaisesRegexp'))

    def test_no_adapts(self):
        self.assertRaisesRegex(TypeError, "Missing.*on annotation",
                               factory, TestFactory)

    def test_factory_no_location(self):

        getAnnotation = factory(Target)

        context = Context()
        target = getAnnotation(context)

        # Several things have happened now.
        # First, we have an annotation, derived from
        # our class name
        key = 'zope.annotation.tests.test_factory.Target'
        self.assertEqual([key],
                         list(context))

        # Second, a target object is stored at that location.
        self.assertEqual(type(context[key]), Target)

        # Third, the returned object is an ILocation, rooted at the
        # parent and having the given name.
        self.assertTrue(ILocation.providedBy(target))
        self.assertIs(target.__parent__, context)
        self.assertEqual(target.__name__, key)

        # But it's a proxy.
        self.assertNotEqual(type(target), Target)
        self.assertTrue(ITarget.providedBy(target))

    def test_factory_location(self):
        # Given an object that is a location,
        # it is not proxied
        @interface.implementer(ILocation)
        class LocatedTarget(Target):
            __name__ = None
            __parent__ = None

        getAnnotation = factory(LocatedTarget)

        context = Context()
        target = getAnnotation(context)

        key = 'zope.annotation.tests.test_factory.LocatedTarget'
        self.assertEqual([key],
                         list(context))

        # Second, a target object is stored at that location.
        self.assertEqual(type(context[key]), LocatedTarget)

        # Third, the returned object is an ILocation, rooted at the
        # parent and having the given name.
        self.assertTrue(ILocation.providedBy(target))
        self.assertIs(target.__parent__, context)
        self.assertEqual(target.__name__, key)

        # And it's not a proxy.
        self.assertEqual(type(target), LocatedTarget)
        self.assertTrue(ITarget.providedBy(target))
        self.assertIs(target, context[key])

    def test_factory_with_key(self):

        key = 'testkey'
        getAnnotation = factory(Target, key)

        context = Context()
        getAnnotation(context)

        self.assertEqual([key],
                         list(context))

        # Second, a target object is stored at that location.
        self.assertEqual(type(context[key]), Target)
