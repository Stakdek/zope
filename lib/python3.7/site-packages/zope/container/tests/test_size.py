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
"""Test container ISized adapter.
"""
import unittest

from zope.interface import implementer
from zope.size.interfaces import ISized
from zope.container.interfaces import IContainer

@implementer(IContainer)
class DummyContainer(object):

    def __init__(self, numitems):
        self._numitems = numitems

    def __len__(self):
        return self._numitems


class Test(unittest.TestCase):

    def testImplementsISized(self):
        from zope.container.size import ContainerSized
        sized = ContainerSized(DummyContainer(23))
        self.assertTrue(ISized.providedBy(sized))

    def testEmptyContainer(self):
        from zope.container.size import ContainerSized
        obj = DummyContainer(0)
        sized = ContainerSized(obj)
        self.assertEqual(sized.sizeForSorting(), ('item', 0))
        self.assertEqual(sized.sizeForDisplay(), u'${items} items')
        self.assertEqual(sized.sizeForDisplay().mapping['items'], '0')

    def testOneItem(self):
        from zope.container.size import ContainerSized
        obj = DummyContainer(1)
        sized = ContainerSized(obj)
        self.assertEqual(sized.sizeForSorting(), ('item', 1))
        self.assertEqual(sized.sizeForDisplay(), u'1 item')

    def testSeveralItems(self):
        from zope.container.size import ContainerSized
        obj = DummyContainer(2)
        sized = ContainerSized(obj)
        self.assertEqual(sized.sizeForSorting(), ('item', 2))
        self.assertEqual(sized.sizeForDisplay(), u'${items} items')
        self.assertEqual(sized.sizeForDisplay().mapping['items'], '2')

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main()
