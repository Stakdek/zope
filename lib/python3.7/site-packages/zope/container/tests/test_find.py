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
"""Find functionality tests
"""
import unittest

from zope.container.interfaces import IReadContainer
from zope.container.interfaces import IObjectFindFilter
from zope.container.find import FindAdapter, SimpleIdFindFilter
from zope.container.find import SimpleInterfacesFindFilter
from zope.interface import implementer, Interface, directlyProvides

@implementer(IReadContainer)
class FakeContainer(object):

    def __init__(self, id, objects):
        self._id = id
        self._objects = objects

    def items(self):
        return [(object._id, object) for object in self._objects]

    def __len__(self):
        return len(self._objects)

class FakeInterfaceFoo(Interface):
    """Test interface Foo"""

class FakeInterfaceBar(Interface):
    """Test interface Bar"""

class FakeInterfaceSpam(Interface):
    """Test interface Spam"""

@implementer(IObjectFindFilter)
class TestObjectFindFilter(object):

    def __init__(self, count):
        self._count = count

    def matches(self, object):
        if not IReadContainer.providedBy(object):
            raise AssertionError("Expecting container")
        return len(object) == self._count


class Test(unittest.TestCase):
    def test_idFind(self):
        alpha = FakeContainer('alpha', [])
        delta = FakeContainer('delta', [])
        beta = FakeContainer('beta', [delta])
        gamma = FakeContainer('gamma', [])
        tree = FakeContainer(
            'tree',
            [alpha, beta, gamma])
        find = FindAdapter(tree)
        # some simple searches
        result = find.find([SimpleIdFindFilter(['beta'])])
        self.assertEqual([beta], result)
        result = find.find([SimpleIdFindFilter(['gamma'])])
        self.assertEqual([gamma], result)
        result = find.find([SimpleIdFindFilter(['delta'])])
        self.assertEqual([delta], result)
        # we should not find the container we search on
        result = find.find([SimpleIdFindFilter(['tree'])])
        self.assertEqual([], result)
        # search for multiple ids
        result = find.find([SimpleIdFindFilter(['alpha', 'beta'])])
        self.assertEqual([alpha, beta], result)
        result = find.find([SimpleIdFindFilter(['beta', 'delta'])])
        self.assertEqual([beta, delta], result)
        # search without any filters, find everything
        result = find.find([])
        self.assertEqual([alpha, beta, delta, gamma], result)
        # search for something that doesn't exist
        result = find.find([SimpleIdFindFilter(['foo'])])
        self.assertEqual([], result)
        # find for something that has two ids at the same time,
        # can't ever be the case
        result = find.find([SimpleIdFindFilter(['alpha']),
                            SimpleIdFindFilter(['beta'])])
        self.assertEqual([], result)

    def test_objectFind(self):
        alpha = FakeContainer('alpha', [])
        delta = FakeContainer('delta', [])
        beta = FakeContainer('beta', [delta])
        gamma = FakeContainer('gamma', [])
        tree = FakeContainer(
            'tree',
            [alpha, beta, gamma])
        find = FindAdapter(tree)
        result = find.find(object_filters=[TestObjectFindFilter(0)])
        self.assertEqual([alpha, delta, gamma], result)
        result = find.find(object_filters=[TestObjectFindFilter(1)])
        self.assertEqual([beta], result)
        result = find.find(object_filters=[TestObjectFindFilter(2)])
        self.assertEqual([], result)

    def test_combinedFind(self):
        alpha = FakeContainer('alpha', [])
        delta = FakeContainer('delta', [])
        beta = FakeContainer('beta', [delta])
        gamma = FakeContainer('gamma', [])
        tree = FakeContainer(
            'tree',
            [alpha, beta, gamma])
        find = FindAdapter(tree)
        result = find.find(id_filters=[SimpleIdFindFilter(['alpha'])],
                           object_filters=[TestObjectFindFilter(0)])
        self.assertEqual([alpha], result)

        result = find.find(id_filters=[SimpleIdFindFilter(['alpha'])],
                           object_filters=[TestObjectFindFilter(1)])
        self.assertEqual([], result)

    def test_interfaceFind(self):
        alpha = FakeContainer('alpha', [])
        directlyProvides(alpha, FakeInterfaceBar)
        delta = FakeContainer('delta', [])
        directlyProvides(delta, FakeInterfaceFoo)
        beta = FakeContainer('beta', [delta])
        directlyProvides(beta, FakeInterfaceSpam)
        gamma = FakeContainer('gamma', [])
        tree = FakeContainer(
            'tree',
            [alpha, beta, gamma])
        find = FindAdapter(tree)
        result = find.find(object_filters=[
            SimpleInterfacesFindFilter(FakeInterfaceFoo, FakeInterfaceSpam)])
        self.assertEqual([beta, delta], result)

    def test_find_non_container_return_default(self):
        data = {'a': 42}
        self.assertEqual(FindAdapter(data).find(), [42])

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
