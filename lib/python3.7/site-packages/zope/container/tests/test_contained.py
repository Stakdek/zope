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
"""Contained Tests
"""
from __future__ import absolute_import
import doctest

import unittest

from persistent import Persistent

import zope.interface
import zope.component

from zope.container.contained import ContainedProxy
from zope.container.contained import NameChooser
from zope.container.contained import contained
from zope.container.contained import uncontained
from zope.container.sample import SampleContainer
from zope.container import testing
from zope.container.interfaces import NameReserved, IContainer, IReservedNames

class MyOb(Persistent):
    pass


class TestContainedProxy(unittest.TestCase):

    def test_basic_proxy_attribute_management_and_picklability(self):
        # Contained-object proxy

        # This is a picklable proxy that can be put around objects that
        # don't implement IContained.

        l = [1, 2, 3]
        p = ContainedProxy(l)
        p.__parent__ = 'Dad'
        p.__name__ = 'p'
        self.assertEqual([1, 2, 3], p)
        self.assertEqual('Dad', p.__parent__)
        self.assertEqual('p', p.__name__)

        import pickle
        p2 = pickle.loads(pickle.dumps(p))
        self.assertEqual([1, 2, 3], p2)
        self.assertEqual('Dad', p2.__parent__)
        self.assertEqual('p', p2.__name__)

    def test_declarations_on_ContainedProxy(self):
        # It is possible to make declarations on ContainedProxy objects.
        from zope.container.interfaces import IContained
        from persistent.interfaces import IPersistent

        class I1(zope.interface.Interface):
            pass
        @zope.interface.implementer(I1)
        class C(object):
            pass

        c = C()
        p = ContainedProxy(c)

        # ContainedProxy provides no interfaces on it's own:

        self.assertEqual((),
                         tuple(zope.interface.providedBy(ContainedProxy)))


        # It implements IContained and IPersistent:
        self.assertEqual((IContained, IPersistent),
                         tuple(zope.interface.implementedBy(ContainedProxy)))

        # A proxied object has IContainer, in addition to what the unproxied
        # object has:
        self.assertEqual(tuple(zope.interface.providedBy(p)),
                         (I1, IContained, IPersistent))

        class I2(zope.interface.Interface):
            pass
        zope.interface.directlyProvides(c, I2)
        self.assertEqual(tuple(zope.interface.providedBy(p)),
                         (I2, I1, IContained, IPersistent))

        # We can declare interfaces through the proxy:

        class I3(zope.interface.Interface):
            pass
        zope.interface.directlyProvides(p, I3)
        self.assertEqual(tuple(zope.interface.providedBy(p)),
                         (I3, I1, IContained, IPersistent))


    def test_ContainedProxy_instances_have_no_instance_dictionaries(self):
        # Make sure that proxies don't introduce extra instance dictionaries
        class C(object):
            pass

        c = C()
        c.x = 1
        self.assertEqual(dict(c.__dict__), {'x': 1})

        p = ContainedProxy(c)
        self.assertEqual(dict(p.__dict__), {'x': 1})

        p.y = 3
        self.assertEqual(dict(p.__dict__), {'x': 1, 'y': 3})
        self.assertEqual(dict(c.__dict__), {'x': 1, 'y': 3})

        self.assertIs(p.__dict__, c.__dict__)

    def test_get_set_ProxiedObject(self):
        from zope.container.contained import getProxiedObject
        from zope.container.contained import setProxiedObject

        proxy = ContainedProxy(self)
        self.assertIs(self, getProxiedObject(proxy))

        o = object()
        self.assertIs(o, getProxiedObject(o))

        old = setProxiedObject(proxy, o)
        self.assertIs(self, old)
        self.assertIs(o, getProxiedObject(proxy))

        with self.assertRaises(TypeError):
            setProxiedObject(self, 1)



class TestNameChooser(unittest.TestCase):
    def test_checkName(self):
        container = SampleContainer()
        container['foo'] = 'bar'
        checkName = NameChooser(container).checkName

        # invalid type for the name
        self.assertRaises(TypeError, checkName, 2, object())
        self.assertRaises(TypeError, checkName, [], object())
        self.assertRaises(TypeError, checkName, None, object())
        self.assertRaises(TypeError, checkName, None, None)

        # invalid names
        self.assertRaises(ValueError, checkName, '+foo', object())
        self.assertRaises(ValueError, checkName, '@foo', object())
        self.assertRaises(ValueError, checkName, 'f/oo', object())
        self.assertRaises(ValueError, checkName, '', object())

        # existing names
        self.assertRaises(KeyError, checkName, 'foo', object())
        self.assertRaises(KeyError, checkName, u'foo', object())

        # correct names
        self.assertEqual(True, checkName('2', object()))
        self.assertEqual(True, checkName(u'2', object()))
        self.assertEqual(True, checkName('other', object()))
        self.assertEqual(True, checkName(u'reserved', object()))
        self.assertEqual(True, checkName(u'r\xe9served', object()))

        # reserved names
        @zope.component.adapter(IContainer)
        @zope.interface.implementer(IReservedNames)
        class ReservedNames(object):
            def __init__(self, context):
                self.reservedNames = set(('reserved', 'other'))
        zope.component.getSiteManager().registerAdapter(ReservedNames)

        self.assertRaises(NameReserved, checkName, 'reserved', object())
        self.assertRaises(NameReserved, checkName, 'other', object())
        self.assertRaises(NameReserved, checkName, u'reserved', object())
        self.assertRaises(NameReserved, checkName, u'other', object())

    def test_chooseName(self):
        container = SampleContainer()
        container['foo.old.rst'] = 'rst doc'
        nc = NameChooser(container)

        # correct name without changes
        self.assertEqual(nc.chooseName('foobar.rst', None),
                         u'foobar.rst')
        self.assertEqual(nc.chooseName(u'\xe9', None),
                         u'\xe9')

        # automatically modified named
        self.assertEqual(nc.chooseName('foo.old.rst', None),
                         u'foo.old-2.rst')
        self.assertEqual(nc.chooseName('+@+@foo.old.rst', None),
                         u'foo.old-2.rst')
        self.assertEqual(nc.chooseName('+@+@foo/foo+@', None),
                         u'foo-foo+@')

        # empty name
        self.assertEqual(nc.chooseName('', None), u'NoneType')
        self.assertEqual(nc.chooseName('@+@', []), u'list')

        # if the name is not a string it is converted
        self.assertEqual(nc.chooseName(None, None), u'None')
        self.assertEqual(nc.chooseName(2, None), u'2')
        self.assertEqual(nc.chooseName([], None), u'[]')
        container['None'] = 'something'
        self.assertEqual(nc.chooseName(None, None), u'None-2')
        container['None-2'] = 'something'
        self.assertEqual(nc.chooseName(None, None), u'None-3')

        # even if the given name cannot be converted to unicode
        class BadBoy(object):
            def __unicode__(self):
                raise Exception
            # Py3: Support
            __str__ = __unicode__

        self.assertEqual(nc.chooseName(BadBoy(), set()), u'set')

class TestFunctions(unittest.TestCase):

    def test_contained(self):
        obj = contained(self, 42, 'name')
        self.assertEqual(obj, self)
        self.assertEqual(obj.__name__, 'name')
        self.assertEqual(obj.__parent__, 42)

    def test_uncontained_no_attr(self):
        with self.assertRaises(AttributeError):
            uncontained(self, 42)

    def test_uncontained_no_attr_fixing_up(self):
        # Causes the attribute error to be ignored
        import zope.container.contained
        zope.container.contained.fixing_up = True
        try:
            uncontained(self, 42)
        finally:
            zope.container.contained.fixing_up = False


class TestPlacefulSetup(unittest.TestCase):

    def test_cover(self):
        # We don't actually use this anywhere in this package, this just makes sure
        # it's still around.
        from zope.container.testing import ContainerPlacefulSetup
        setup = ContainerPlacefulSetup()
        setup.setUp()
        setup.buildFolders()
        setup.tearDown()

def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTest(doctest.DocTestSuite(
        'zope.container.contained',
        setUp=testing.setUp, tearDown=testing.tearDown,
        checker=testing.checker))
    return suite
