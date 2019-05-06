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
"""Object Event Tests
"""
import doctest
import unittest

from zope import interface

from zope.component import testing
from zope.testing import module

from zope.lifecycleevent import ObjectCreatedEvent, created
from zope.lifecycleevent import Attributes, Sequence
from zope.lifecycleevent import ObjectModifiedEvent, modified
from zope.lifecycleevent import ObjectCopiedEvent, copied
from zope.lifecycleevent import ObjectMovedEvent, moved
from zope.lifecycleevent import ObjectRemovedEvent, removed
from zope.lifecycleevent import ObjectAddedEvent, added

from zope.interface.verify import verifyObject
from zope.interface.verify import verifyClass


class Context(object):
    pass


class _AbstractListenerCase(object):

    def setUp(self):
        super(_AbstractListenerCase, self).setUp()
        from zope.event import subscribers
        self._old_subscribers = subscribers[:]
        self.listener = []
        subscribers[:] = [self.listener.append]

    def tearDown(self):
        from zope.event import subscribers
        subscribers[:] = self._old_subscribers
        super(_AbstractListenerCase, self).tearDown()


class _AbstractEventCase(_AbstractListenerCase):

    klass = None
    object = object()
    notifier = None

    def _getTargetClass(self):
        return self.klass

    def _getInitArgs(self):
        return (self.object,)

    def _makeOne(self):
        return self._getTargetClass()(*self._getInitArgs())

    def setUp(self):
        super(_AbstractEventCase, self).setUp()
        self.event = self._makeOne()

    def testGetObject(self):
        self.assertEqual(self.event.object, self.object)

    def test_verifyObject(self):
        iface = list(interface.providedBy(self.event).flattened())[0]
        verifyObject(iface, self.event)

    def test_verifyClass(self):
        iface = list(interface.implementedBy(type(self.event)).flattened())[0]
        verifyClass(iface, self._getTargetClass())

    def test_notify(self):
        notifier = type(self).notifier
        try:
            notifier = notifier.__func__
        except AttributeError:
            pass # Python 3
        notifier(*self._getInitArgs())
        self.assertEqual(len(self.listener), 1)
        self.assertEqual(self.listener[-1].object, self.object)
        return self.listener[-1]


class TestSequence(unittest.TestCase):

    def testSequence(self):

        from zope.interface import Interface, Attribute

        class ISample(Interface):
            field1 = Attribute("A test field")
            field2 = Attribute("A test field")
            field3 = Attribute("A test field")

        desc = Sequence(ISample, 'field1', 'field2')
        self.assertEqual(desc.interface, ISample)
        self.assertEqual(desc.keys, ('field1', 'field2'))


class TestAttributes(unittest.TestCase):

    def testAttributes(self):
        from zope.lifecycleevent.interfaces import IObjectMovedEvent
        desc = Attributes(IObjectMovedEvent, "newName", "newParent")
        self.assertEqual(desc.interface, IObjectMovedEvent)
        self.assertEqual(desc.attributes, ('newName', 'newParent'))


class TestObjectCreatedEvent(_AbstractEventCase,
                             unittest.TestCase):

    klass = ObjectCreatedEvent
    notifier = created

class TestObjectModifiedEvent(_AbstractEventCase,
                              unittest.TestCase):

    klass = ObjectModifiedEvent
    notifier = modified

    def testAttributes(self):
        from zope.interface import implementer, Interface, Attribute

        class ISample(Interface):
            field = Attribute("A test field")

        @implementer(ISample)
        class Sample(object):
            pass
        obj = Sample()
        obj.field = 42
        attrs = Attributes(ISample, "field")

        modified(obj, attrs)
        self.assertEqual(self.listener[-1].object, obj)
        self.assertEqual(self.listener[-1].descriptions, (attrs,))


class TestObjectCopiedEvent(_AbstractEventCase,
                            unittest.TestCase):

    klass = ObjectCopiedEvent
    original = object()
    notifier = copied

    def _getInitArgs(self):
        return (self.object, self.original)

    def test_notify(self):
        delivered = super(TestObjectCopiedEvent, self).test_notify()
        self.assertEqual(delivered.original, self.original)


class TestObjectMovedEvent(_AbstractEventCase,
                           unittest.TestCase):

    klass = ObjectMovedEvent
    object = Context()
    old_parent = Context()
    new_parent = Context()
    notifier = moved

    def _getInitArgs(self):
        return (self.object,
                self.old_parent, 'old_name',
                self.new_parent, 'new_name')

    def test_it(self):
        event = self.event
        self.assertEqual(event.object, self.object)
        self.assertEqual(event.oldParent, self.old_parent)
        self.assertEqual(event.newParent, self.new_parent)
        self.assertEqual(event.newName, 'new_name')
        self.assertEqual(event.oldName, 'old_name')


class TestObjectAddedEvent(_AbstractEventCase,
                           unittest.TestCase):

    klass = ObjectAddedEvent
    parent = Context()
    name = 'new_name'
    notifier = added

    def _getInitArgs(self):
        return (self.object, self.parent, self.name)

    def test_it(self):
        ob = self.object
        new_parent = self.parent
        event = self.event
        self.assertEqual(event.object, ob)
        self.assertEqual(event.newParent, new_parent)
        self.assertEqual(event.newName, 'new_name')
        self.assertEqual(event.oldParent, None)
        self.assertEqual(event.oldName, None)

    def test_it_Nones(self):
        self.object = ob = Context()
        new_parent = Context()
        self.parent = None
        self.name = None
        ob.__parent__ = new_parent
        ob.__name__ = 'new_name'
        event = self._makeOne()
        self.assertEqual(event.object, ob)
        self.assertEqual(event.newParent, new_parent)
        self.assertEqual(event.newName, 'new_name')
        self.assertEqual(event.oldParent, None)
        self.assertEqual(event.oldName, None)


class TestObjectRemovedEvent(_AbstractEventCase,
                             unittest.TestCase):

    klass = ObjectRemovedEvent
    old_parent = Context()
    name = 'name'
    notifier = removed

    def _getInitArgs(self):
        return (self.object, self.old_parent, self.name)

    def test_it(self):
        ob = self.object
        parent = self.old_parent
        event = self.event
        self.assertEqual(event.object, ob)
        self.assertEqual(event.newParent, None)
        self.assertEqual(event.newName, None)
        self.assertEqual(event.oldParent, parent)
        self.assertEqual(event.oldName, 'name')

    def test_it_Nones(self):
        self.object = ob = Context()
        parent = Context()
        self.old_parent = None
        self.name = None
        ob.__parent__ = parent
        ob.__name__ = 'name'
        event = self._makeOne()
        self.assertEqual(event.object, ob)
        self.assertEqual(event.newParent, None)
        self.assertEqual(event.newName,  None)
        self.assertEqual(event.oldParent, parent)
        self.assertEqual(event.oldName, 'name')


class TestMoved(_AbstractListenerCase,
                unittest.TestCase):

    def test_it(self):
        moved('object', 'oldParent', 'oldName', 'newParent', 'newName')
        self.assertEqual(1, len(self.listener))
        event = self.listener[0]
        self.assertTrue(isinstance(event, ObjectMovedEvent))
        self.assertEqual(event.object, 'object')
        self.assertEqual(event.oldParent, 'oldParent')
        self.assertEqual(event.oldName, 'oldName')
        self.assertEqual(event.newParent, 'newParent')
        self.assertEqual(event.newName, 'newName')

def setUp(test):
    testing.setUp(test)
    module.setUp(test)

def tearDown(test):
    module.tearDown(test)
    testing.tearDown(test)

def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocFileSuite('README.rst'),
        doctest.DocFileSuite('manual.rst'),
        doctest.DocFileSuite('handling.rst',
                             setUp=setUp,
                             tearDown=tearDown,
                             optionflags=doctest.ELLIPSIS),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
