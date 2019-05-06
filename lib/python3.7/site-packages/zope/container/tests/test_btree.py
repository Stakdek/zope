##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""BTree Container Tests
"""
import unittest

from zope.interface.verify import verifyObject

from zope.container.tests.test_icontainer import TestSampleContainer
from zope.container.btree import BTreeContainer
from zope.container.interfaces import IBTreeContainer
from zope.container.interfaces import IContainerModifiedEvent
from zope.container.contained import Contained
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


class TestBTreeContainer(TestSampleContainer, unittest.TestCase):

    def makeTestObject(self):
        return BTreeContainer()


class TestBTreeSpecials(unittest.TestCase):

    def testStoredLength(self):
        # This is a lazy property for backward compatibility.  If the len is not
        # stored already we set it to the length of the underlying
        # btree.
        lazy = BTreeContainer._BTreeContainer__len
        self.assertIs(lazy, BTreeContainer.__dict__['_BTreeContainer__len'])
        self.assertTrue(hasattr(lazy, '__get__'))

        bc = BTreeContainer()
        self.assertEqual(bc.__dict__['_BTreeContainer__len'](), 0)
        del bc.__dict__['_BTreeContainer__len']
        self.assertFalse('_BTreeContainer__len' in bc.__dict__)
        bc['1'] = 1
        self.assertEqual(len(bc), 1)
        self.assertEqual(bc.__dict__['_BTreeContainer__len'](), 1)

        del bc.__dict__['_BTreeContainer__len']
        self.assertFalse('_BTreeContainer__len' in bc.__dict__)
        self.assertEqual(len(bc), 1)
        self.assertEqual(bc.__dict__['_BTreeContainer__len'](), 1)


    # The tests which follow test the additional signatures and declarations
    # for the BTreeContainer that allow it to provide the IBTreeContainer
    # interface.

    def testBTreeContainerInterface(self):
        bc = BTreeContainer()
        self.assertTrue(verifyObject(IBTreeContainer, bc))
        self.checkIterable(bc.items())
        self.checkIterable(bc.keys())
        self.checkIterable(bc.values())

    def testEmptyItemsWithArg(self):
        bc = BTreeContainer()
        self.assertEqual(list(bc.items(None)), list(bc.items()))
        self.assertEqual(list(bc.items("")), [])
        self.assertEqual(list(bc.items("not-there")), [])
        self.checkIterable(bc.items(None))
        self.checkIterable(bc.items(""))
        self.checkIterable(bc.items("not-there"))

    def testEmptyKeysWithArg(self):
        bc = BTreeContainer()
        self.assertEqual(list(bc.keys(None)), list(bc.keys()))
        self.assertEqual(list(bc.keys("")), [])
        self.assertEqual(list(bc.keys("not-there")), [])
        self.checkIterable(bc.keys(None))
        self.checkIterable(bc.keys(""))
        self.checkIterable(bc.keys("not-there"))

    def testEmptyValuesWithArg(self):
        bc = BTreeContainer()
        self.assertEqual(list(bc.values(None)), list(bc.values()))
        self.assertEqual(list(bc.values("")), [])
        self.assertEqual(list(bc.values("not-there")), [])
        self.checkIterable(bc.values(None))
        self.checkIterable(bc.values(""))
        self.checkIterable(bc.values("not-there"))

    def testNonemptyItemsWithArg(self):
        bc = BTreeContainer()
        bc["0"] = 1
        bc["1"] = 2
        bc["2"] = 3
        self.assertEqual(list(bc.items(None)), list(bc.items()))
        self.assertEqual(list(bc.items("")), [("0", 1), ("1", 2), ("2", 3)])
        self.assertEqual(list(bc.items("3")), [])
        self.assertEqual(list(bc.items("2.")), [])
        self.assertEqual(list(bc.items("2")), [("2", 3)])
        self.assertEqual(list(bc.items("1.")), [("2", 3)])
        self.assertEqual(list(bc.items("1")), [("1", 2), ("2", 3)])
        self.assertEqual(list(bc.items("0.")), [("1", 2), ("2", 3)])
        self.assertEqual(list(bc.items("0")), [("0", 1), ("1", 2), ("2", 3)])
        self.checkIterable(bc.items(None))
        self.checkIterable(bc.items(""))
        self.checkIterable(bc.items("0."))
        self.checkIterable(bc.items("3"))

    def testNonemptyKeysWithArg(self):
        bc = BTreeContainer()
        bc["0"] = 1
        bc["1"] = 2
        bc["2"] = 3
        self.assertEqual(list(bc.keys(None)), list(bc.keys()))
        self.assertEqual(list(bc.keys("")), ["0", "1", "2"])
        self.assertEqual(list(bc.keys("3")), [])
        self.assertEqual(list(bc.keys("2.")), [])
        self.assertEqual(list(bc.keys("2")), ["2"])
        self.assertEqual(list(bc.keys("1.")), ["2"])
        self.assertEqual(list(bc.keys("1")), ["1", "2"])
        self.assertEqual(list(bc.keys("0.")), ["1", "2"])
        self.assertEqual(list(bc.keys("0")), ["0", "1", "2"])
        self.checkIterable(bc.keys(None))
        self.checkIterable(bc.keys(""))
        self.checkIterable(bc.keys("0."))
        self.checkIterable(bc.keys("3"))

    def testNonemptyValueWithArg(self):
        bc = BTreeContainer()
        bc["0"] = 1
        bc["1"] = 2
        bc["2"] = 3
        self.assertEqual(list(bc.values(None)), list(bc.values()))
        self.assertEqual(list(bc.values("")), [1, 2, 3])
        self.assertEqual(list(bc.values("3")), [])
        self.assertEqual(list(bc.values("2.")), [])
        self.assertEqual(list(bc.values("2")), [3])
        self.assertEqual(list(bc.values("1.")), [3])
        self.assertEqual(list(bc.values("1")), [2, 3])
        self.assertEqual(list(bc.values("0.")), [2, 3])
        self.assertEqual(list(bc.values("0")), [1, 2, 3])
        self.checkIterable(bc.values(None))
        self.checkIterable(bc.values(""))
        self.checkIterable(bc.values("0."))
        self.checkIterable(bc.values("3"))

    def testCorrectLengthWhenAddingExistingItem(self):
        """
        for bug #175388
        """
        bc = BTreeContainer()
        bc[u'x'] = object()
        self.assertEqual(len(bc), 1)
        bc[u'x'] = bc[u'x']
        self.assertEqual(len(bc), 1)
        self.assertEqual(list(bc), [u'x'])


    def checkIterable(self, iterable):
        it = iter(iterable)
        self.assertTrue(callable(it.__iter__))
        self.assertTrue(iter(it) is it)
        # Exhaust the iterator:
        first_time = list(it)
        self.assertRaises(StopIteration, next, it)
        # Subsequent iterations will return the same values:
        self.assertEqual(list(iterable), first_time)
        self.assertEqual(list(iterable), first_time)


class TestBTreeEvents(unittest.TestCase):

    def setUp(self):
        from zope.event import subscribers
        self._old_subscribers = subscribers[:]
        subscribers[:] = []

    def tearDown(self):
        from zope.event import subscribers
        subscribers[:] = self._old_subscribers

    def testDeletion(self):
        from zope.event import subscribers
        tree = BTreeContainer()
        item = Contained()
        tree['42'] = item
        events = []
        def subscriber(event):
            events.append(event)
            # events should happen after the deletion, not before)
            self.assertEqual(len(tree), 0)
            self.assertEqual(list(tree), [])
        subscribers.append(subscriber)

        del tree['42']
        self.assertEqual(item.__name__, None)
        self.assertEqual(item.__parent__, None)

        self.assertEqual(len(events), 2)
        self.assertTrue(IObjectRemovedEvent.providedBy(events[0]))
        self.assertTrue(IContainerModifiedEvent.providedBy(events[1]))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
