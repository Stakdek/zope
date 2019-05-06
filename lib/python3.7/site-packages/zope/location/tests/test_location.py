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


class ConformsToILocation(object):

    def test_class_conforms_to_ILocation(self):
        from zope.interface.verify import verifyClass
        from zope.location.interfaces import ILocation
        verifyClass(ILocation, self._getTargetClass())

    def test_instance_conforms_to_ILocation(self):
        from zope.interface.verify import verifyObject
        from zope.location.interfaces import ILocation
        verifyObject(ILocation, self._makeOne())


class LocationTests(unittest.TestCase, ConformsToILocation):

    def _getTargetClass(self):
        from zope.location.location import Location
        return Location

    def _makeOne(self):
        return self._getTargetClass()()

    def test_ctor(self):
        loc = self._makeOne()
        self.assertEqual(loc.__parent__, None)
        self.assertEqual(loc.__name__, None)


class Test_locate(unittest.TestCase):

    def _callFUT(self, obj, *args, **kw):
        from zope.location.location import locate
        return locate(obj, *args, **kw)

    def test_wo_name(self):
        class Dummy(object):
            pass
        parent = Dummy()
        dummy = Dummy()
        self._callFUT(dummy, parent)
        self.assertTrue(dummy.__parent__ is parent)
        self.assertEqual(dummy.__name__, None)

    def test_w_name(self):
        class Dummy(object):
            pass
        parent = Dummy()
        dummy = Dummy()
        self._callFUT(dummy, parent, 'name')
        self.assertTrue(dummy.__parent__ is parent)
        self.assertEqual(dummy.__name__, 'name')


class Test_located(unittest.TestCase):

    def _callFUT(self, obj, *args, **kw):
        from zope.location.location import located
        return located(obj, *args, **kw)

    def test_wo_name_obj_implements_ILocation(self):
        from zope.interface import implementer
        from zope.location.interfaces import ILocation
        @implementer(ILocation)
        class Dummy(object):
            __parent__ = None
            __name__ = object()
        parent = Dummy()
        dummy = Dummy()
        self._callFUT(dummy, parent)
        self.assertTrue(dummy.__parent__ is parent)
        self.assertEqual(dummy.__name__, None)

    def test_w_name_adaptable_to_ILocation(self):
        from zope.interface.interface import adapter_hooks
        from zope.location.interfaces import ILocation
        _hooked = []
        def _hook(iface, obj):
            _hooked.append((iface, obj))
            return obj
        class Dummy(object):
            pass
        parent = Dummy()
        dummy = Dummy()
        before = adapter_hooks[:]
        adapter_hooks.insert(0, _hook)
        try:
            self._callFUT(dummy, parent, 'name')
        finally:
            adapter_hooks[:] = before
        self.assertTrue(dummy.__parent__ is parent)
        self.assertEqual(dummy.__name__, 'name')
        self.assertEqual(len(_hooked), 1)
        self.assertEqual(_hooked[0], (ILocation, dummy))

    def test_wo_name_not_adaptable_to_ILocation(self):
        class Dummy(object):
            __parent__ = None
            __name__ = 'before'
        parent = Dummy()
        dummy = Dummy()
        self.assertRaises(TypeError, self._callFUT, dummy, parent, 'name')
        self.assertEqual(dummy.__parent__, None)
        self.assertEqual(dummy.__name__, 'before')


class Test_LocationIterator(unittest.TestCase):

    def _callFUT(self, obj):
        from zope.location.location import LocationIterator
        return LocationIterator(obj)

    def test_w_None(self):
        self.assertEqual(list(self._callFUT(None)), [])

    def test_w_non_location_object(self):
        island = object()
        self.assertEqual(list(self._callFUT(island)), [island])

    def test_w_isolated_location_object(self):
        class Dummy(object):
            __parent__ = None
            __name__ = 'before'
        island = Dummy()
        self.assertEqual(list(self._callFUT(island)), [island])

    def test_w_nested_location_object(self):
        class Dummy(object):
            __parent__ = None
            __name__ = 'before'
        parent = Dummy()
        child = Dummy()
        child.__parent__ = parent
        grand = Dummy()
        grand.__parent__ = child
        self.assertEqual(list(self._callFUT(grand)), [grand, child, parent])


class Test_inside(unittest.TestCase):

    def _callFUT(self, i1, i2):
        from zope.location.location import inside
        return inside(i1, i2)

    def test_w_non_location_objects(self):
        island = object()
        atoll = object()
        self.assertTrue(self._callFUT(island, island))
        self.assertFalse(self._callFUT(island, atoll))
        self.assertFalse(self._callFUT(atoll, island))
        self.assertTrue(self._callFUT(atoll, atoll))

    def test_w_isolated_location_objects(self):
        class Dummy(object):
            __parent__ = None
            __name__ = 'before'
        island = Dummy()
        atoll = Dummy()
        self.assertTrue(self._callFUT(island, island))
        self.assertFalse(self._callFUT(island, atoll))
        self.assertFalse(self._callFUT(atoll, island))
        self.assertTrue(self._callFUT(atoll, atoll))

    def test_w_nested_location_object(self):
        class Dummy(object):
            __parent__ = None
            __name__ = 'before'
        parent = Dummy()
        child = Dummy()
        child.__parent__ = parent
        grand = Dummy()
        grand.__parent__ = child
        self.assertTrue(self._callFUT(child, parent))
        self.assertFalse(self._callFUT(parent, child))
        self.assertTrue(self._callFUT(child, child))
        self.assertTrue(self._callFUT(grand, parent))
        self.assertFalse(self._callFUT(parent, grand))
        self.assertTrue(self._callFUT(grand, child))
        self.assertFalse(self._callFUT(child, grand))
        self.assertTrue(self._callFUT(grand, grand))


class ClassAndInstanceDescrTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.location.location import ClassAndInstanceDescr
        return ClassAndInstanceDescr

    def _makeOne(self, _inst, _class):
        return self._getTargetClass()(_inst, _class)

    def _makeScaffold(self):
        _inst_called = []
        def _inst(*args, **kw):
            _inst_called.append((args, kw))
            return 'INST'
        _class_called = []
        def _class(*args, **kw):
            _class_called.append((args, kw))
            return 'CLASS'
        class Foo(object):
            descr = self._makeOne(_inst, _class)
        return Foo, _class_called, _inst_called

    def test_fetched_from_class(self):
        Foo, _class_called, _inst_called = self._makeScaffold()
        self.assertEqual(Foo.descr, 'CLASS')
        self.assertEqual(_class_called, [((Foo,),{})])
        self.assertEqual(_inst_called, [])

    def test_fetched_from_instance(self):
        Foo, _class_called, _inst_called = self._makeScaffold()
        foo = Foo()
        self.assertEqual(foo.descr, 'INST')
        self.assertEqual(_class_called, [])
        self.assertEqual(_inst_called, [((foo,),{})])


_MARKER = object()


class LocationProxyTests(unittest.TestCase, ConformsToILocation):

    def _getTargetClass(self):
        from zope.location.location import LocationProxy
        return LocationProxy

    def _makeOne(self, obj=None, container=_MARKER, name=_MARKER):
        if obj is None:
            obj = object()
        if container is _MARKER:
            self.assertIs(name, _MARKER)
            return self._getTargetClass()(obj)
        self.assertIsNot(name, _MARKER)
        return self._getTargetClass()(obj, container, name)

    def test_ctor_defaults(self):
        dummy = object() # can't setattr
        proxy = self._makeOne(dummy)
        self.assertEqual(proxy.__parent__, None)
        self.assertEqual(proxy.__name__, None)

    def test_ctor_explicit(self):
        dummy = object() # can't setattr
        parent = object()
        proxy = self._makeOne(dummy, parent, 'name')
        self.assertTrue(proxy.__parent__ is parent)
        self.assertEqual(proxy.__name__, 'name')

    def test___getattribute___wrapped(self):
        class Context(object):
            attr = 'ATTR'
        context = Context()
        proxy = self._makeOne(context)
        self.assertEqual(proxy.attr, 'ATTR')

    def test___setattr___wrapped(self):
        class Context(object):
            attr = 'BEFORE'
        context = Context()
        proxy = self._makeOne(context)
        proxy.attr = 'AFTER'
        self.assertEqual(context.attr, 'AFTER')

    def test___doc___from_derived_class(self):
        klass = self._getTargetClass()
        class Derived(klass):
            """DERIVED"""
        self.assertEqual(Derived.__doc__, 'DERIVED')

    def test___doc___from_target_class(self):
        klass = self._getTargetClass()
        class Context(object):
            """CONTEXT"""
        proxy = self._makeOne(Context())
        self.assertEqual(proxy.__doc__, 'CONTEXT')

    def test___doc___from_target_instance(self):
        klass = self._getTargetClass()
        class Context(object):
            """CONTEXT"""
        context = Context()
        context.__doc__ = 'INSTANCE'
        proxy = self._makeOne(context)
        self.assertEqual(proxy.__doc__, 'INSTANCE')

    def test___reduce__(self):
        proxy = self._makeOne()
        self.assertRaises(TypeError, proxy.__reduce__)

    def test___reduce_ex__(self):
        proxy = self._makeOne()
        self.assertRaises(TypeError, proxy.__reduce_ex__, 1)

    def test___reduce___via_pickling(self):
        import pickle
        class Context(object):
            def __reduce__(self):
                raise AssertionError("This is not called")
        proxy = self._makeOne(Context())
        # XXX: this TypeError is not due to LocationProxy.__reduce__:
        #      it's descriptor (under pure Python) isn't begin triggered
        #      properly
        self.assertRaises(TypeError, pickle.dumps, proxy)

    def test__providedBy___class(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface import providedBy
        from zope.interface import provider
        class IProxyFactory(Interface):
            pass
        class IProxy(Interface):
            pass
        @provider(IProxyFactory)
        @implementer(IProxy)
        class Foo(self._getTargetClass()):
            pass
        self.assertEqual(list(providedBy(Foo)), [IProxyFactory])

    def test__providedBy___instance(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface import providedBy
        from zope.interface import provider
        from zope.location.interfaces import ILocation
        class IProxyFactory(Interface):
            pass
        class IProxy(Interface):
            pass
        class IContextFactory(Interface):
            pass
        class IContext(Interface):
            pass
        @provider(IProxyFactory)
        @implementer(IProxy)
        class Proxy(self._getTargetClass()):
            pass
        @provider(IContextFactory)
        @implementer(IContext)
        class Context(object):
            pass
        context = Context()
        proxy = Proxy(context)
        self.assertEqual(list(providedBy(proxy)), [IContext, IProxy, ILocation])


class LocationPyProxyTests(LocationProxyTests):

    def setUp(self):
        import sys
        for mod in ('zope.location.location',
                    'zope.proxy.decorator'):
            try:
                del sys.modules[mod]
            except KeyError: # pragma: no cover
                pass
        import zope.proxy
        self.orig = (zope.proxy.ProxyBase,
                     zope.proxy.getProxiedObject,
                     zope.proxy.setProxiedObject,
                     zope.proxy.isProxy,
                     zope.proxy.sameProxiedObjects,
                     zope.proxy.queryProxy,
                     zope.proxy.queryInnerProxy,
                     zope.proxy.removeAllProxies,
                     zope.proxy.non_overridable)
        zope.proxy.ProxyBase = zope.proxy.PyProxyBase
        zope.proxy.getProxiedObject = zope.proxy.py_getProxiedObject
        zope.proxy.setProxiedObject = zope.proxy.py_setProxiedObject
        zope.proxy.isProxy = zope.proxy.py_isProxy
        zope.proxy.sameProxiedObjects = zope.proxy.py_sameProxiedObjects
        zope.proxy.queryProxy = zope.proxy.py_queryProxy
        zope.proxy.queryInnerProxy = zope.proxy.py_queryInnerProxy
        zope.proxy.removeAllProxies = zope.proxy.py_removeAllProxies
        zope.proxy.non_overridable = zope.proxy.PyNonOverridable


    def tearDown(self):
        import zope.proxy
        (zope.proxy.ProxyBase,
         zope.proxy.getProxiedObject,
         zope.proxy.setProxiedObject,
         zope.proxy.isProxy,
         zope.proxy.sameProxiedObjects,
         zope.proxy.queryProxy,
         zope.proxy.queryInnerProxy,
         zope.proxy.removeAllProxies,
         zope.proxy.non_overridable) = self.orig


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
