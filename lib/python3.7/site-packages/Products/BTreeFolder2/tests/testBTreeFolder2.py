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
"""Unit tests for BTreeFolder2.
"""

from functools import total_ordering
import six
import unittest

from Acquisition import aq_base
from OFS.ObjectManager import BadRequestException
from OFS.Folder import Folder

from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.BTreeFolder2.BTreeFolder2 import ExhaustedUniqueIdsError


class BTreeFolder2Tests(unittest.TestCase):

    def getBase(self, ob):
        # This is overridden in subclasses.
        return aq_base(ob)

    def setUp(self):
        self.f = BTreeFolder2('root')
        ff = BTreeFolder2('item')
        self.f._setOb(ff.id, ff)
        self.ff = self.f._getOb(ff.id)

    def testAdded(self):
        self.assertEqual(self.ff.id, 'item')

    def testSetItem(self):
        self.f['ff2'] = BTreeFolder2('item2')
        self.assertEqual(self.f.ff2.id, 'item2')

    def test_getattr_found(self):
        self.assertEqual(getattr(self.f, 'item'), self.ff)

    def test_getattr_notfound(self):
        self.assertRaises(AttributeError, getattr, self.f, 'none')

    def test_getattr_default(self):
        self.assertEqual(getattr(self.f, 'none', '1'), '1')

    def testCount(self):
        self.assertEqual(self.f.objectCount(), 1)
        self.assertEqual(self.ff.objectCount(), 0)

    def testLen(self):
        self.assertEqual(len(self.f), 1)
        self.assertEqual(len(self.ff), 0)

    def testNonZero(self):
        self.assertEqual(bool(self.f), True)
        self.assertEqual(bool(self.ff), True)

    def testObjectIds(self):
        self.assertEqual(list(self.f.objectIds()), ['item'])
        self.assertEqual(list(self.ff.objectIds()), [])
        f3 = BTreeFolder2('item3')
        self.f._setOb(f3.id, f3)
        lst = list(self.f.objectIds())
        lst.sort()
        self.assertEqual(lst, ['item', 'item3'])

    def testKeys(self):
        self.assertEqual(list(self.f.keys()), ['item'])
        self.assertEqual(list(self.ff.keys()), [])
        f3 = BTreeFolder2('item3')
        self.f[f3.id] = f3
        lst = list(self.f.keys())
        lst.sort()
        self.assertEqual(lst, ['item', 'item3'])

    def testObjectIdsWithMetaType(self):
        f2 = Folder()
        f2.id = 'subfolder'
        self.f._setOb(f2.id, f2)
        mt1 = self.ff.meta_type
        mt2 = Folder.meta_type
        self.assertEqual(list(self.f.objectIds(mt1)), ['item'])
        self.assertEqual(list(self.f.objectIds((mt1, ))), ['item'])
        self.assertEqual(list(self.f.objectIds(mt2)), ['subfolder'])
        lst = list(self.f.objectIds([mt1, mt2]))
        lst.sort()
        self.assertEqual(lst, ['item', 'subfolder'])
        self.assertEqual(list(self.f.objectIds('blah')), [])

    def testObjectValues(self):
        values = self.f.objectValues()
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].id, 'item')
        self.assertTrue(values[0].aq_parent is self.f)

    def testValues(self):
        values = self.f.values()
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].id, 'item')

    def testObjectItems(self):
        items = self.f.objectItems()
        self.assertEqual(len(items), 1)
        id, val = items[0]
        self.assertEqual(id, 'item')
        self.assertEqual(val.id, 'item')
        self.assertTrue(val.aq_parent is self.f)

    def testItems(self):
        items = self.f.items()
        self.assertEqual(len(items), 1)
        id, val = items[0]
        self.assertEqual(id, 'item')
        self.assertEqual(val.id, 'item')

    def testHasKey(self):
        self.assertTrue(self.f.hasObject('item'))  # Old spelling
        self.assertTrue(self.f.has_key('item'))  # NOQA, New spelling

    def testContains(self):
        self.assertTrue('item' in self.f)

    def testDelete(self):
        self.f._delOb('item')
        self.assertEqual(list(self.f.objectIds()), [])
        self.assertEqual(self.f.objectCount(), 0)

    def testDelItem(self):
        del self.f['item']
        self.assertTrue('item' not in self.f)
        self.assertEqual(len(self.f), 0)

    def testIter(self):
        iterator = iter(self.f)
        first = six.next(iterator)
        self.assertEqual(first, 'item')
        self.assertRaises(StopIteration, six.next, iterator)

    def testObjectMap(self):
        map = self.f.objectMap()
        self.assertEqual(list(map), [{'id': 'item', 'meta_type':
                                      self.ff.meta_type}])
        # I'm not sure why objectMap_d() exists, since it appears to be
        # the same as objectMap(), but it's implemented by Folder.
        self.assertEqual(list(self.f.objectMap_d()), list(self.f.objectMap()))

    def testObjectIds_d(self):
        self.assertEqual(self.f.objectIds_d(), {'item': 1})

    def testCheckId(self):
        self.assertEqual(self.f._checkId('xyz'), None)
        self.assertRaises(BadRequestException, self.f._checkId, 'item')
        self.assertRaises(BadRequestException, self.f._checkId, 'REQUEST')

    def testSetObject(self):
        f2 = BTreeFolder2('item2')
        self.f._setObject(f2.id, f2)
        self.assertTrue('item2' in self.f)
        self.assertEqual(self.f.objectCount(), 2)

    def testWrapped(self):
        # Verify that the folder returns wrapped versions of objects.
        base = self.getBase(self.f._getOb('item'))
        self.assertTrue(self.f._getOb('item') is not base)
        self.assertTrue(self.f['item'] is not base)
        self.assertTrue(self.f.get('item') is not base)
        self.assertTrue(self.getBase(self.f._getOb('item')) is base)

    def testGenerateId(self):
        ids = {}
        for n in range(10):
            ids[self.f.generateId()] = 1
        self.assertEqual(len(ids), 10)  # All unique
        for id in ids.keys():
            self.f._checkId(id)  # Must all be valid

    def testGenerateIdDenialOfServicePrevention(self):
        for n in range(10):
            item = Folder()
            item.id = 'item%d' % n
            self.f._setOb(item.id, item)
        self.f.generateId('item', rand_ceiling=20)  # Shouldn't be a problem
        self.assertRaises(ExhaustedUniqueIdsError,
                          self.f.generateId, 'item', rand_ceiling=9)

    def testReplace(self):
        old_f = Folder()
        old_f.id = 'item'
        inner_f = BTreeFolder2('inner')
        old_f._setObject(inner_f.id, inner_f)
        self.ff._populateFromFolder(old_f)
        self.assertEqual(self.ff.objectCount(), 1)
        self.assertTrue('inner' in self.ff)
        self.assertEqual(self.getBase(self.ff._getOb('inner')), inner_f)

    def testObjectListing(self):
        f2 = BTreeFolder2('somefolder')
        self.f._setObject(f2.id, f2)
        # Hack in an absolute_url() method that works without context.
        self.f.absolute_url = lambda: ''
        info = self.f.getBatchObjectListing()
        self.assertEqual(info['b_start'], 1)
        self.assertEqual(info['b_end'], 2)
        self.assertEqual(info['prev_batch_url'], '')
        self.assertEqual(info['next_batch_url'], '')
        self.assertTrue(info['formatted_list'].find('</select>') > 0)
        self.assertTrue(info['formatted_list'].find('item') > 0)
        self.assertTrue(info['formatted_list'].find('somefolder') > 0)

        # Ensure batching is working.
        info = self.f.getBatchObjectListing({'b_count': 1})
        self.assertEqual(info['b_start'], 1)
        self.assertEqual(info['b_end'], 1)
        self.assertEqual(info['prev_batch_url'], '')
        self.assertTrue(info['next_batch_url'] != '')
        self.assertTrue(info['formatted_list'].find('item') > 0)
        self.assertTrue(info['formatted_list'].find('somefolder') < 0)

        info = self.f.getBatchObjectListing({'b_start': 2})
        self.assertEqual(info['b_start'], 2)
        self.assertEqual(info['b_end'], 2)
        self.assertTrue(info['prev_batch_url'] != '')
        self.assertEqual(info['next_batch_url'], '')
        self.assertTrue(info['formatted_list'].find('item') < 0)
        self.assertTrue(info['formatted_list'].find('somefolder') > 0)

    def testObjectListingWithSpaces(self):
        # The option list must use value attributes to preserve spaces.
        name = " some folder "
        f2 = BTreeFolder2(name)
        self.f._setObject(f2.id, f2)
        self.f.absolute_url = lambda: ''
        info = self.f.getBatchObjectListing()
        expect = '<option value="%s">%s</option>' % (name, name)
        self.assertTrue(info['formatted_list'].find(expect) > 0)

    def testCleanup(self):
        self.assertTrue(self.f._cleanup())
        key = TrojanKey('a')
        self.f._tree[key] = 'b'
        self.assertTrue(self.f._cleanup())
        key.value = 'z'

        # With a key in the wrong place, there should now be damage.
        self.assertTrue(not self.f._cleanup())
        # Now it's fixed.
        self.assertTrue(self.f._cleanup())

        from BTrees.OIBTree import OIBTree
        tree = self.f._mt_index['d'] = OIBTree()
        tree['e'] = 1
        self.assertTrue(not self.f._cleanup())

        # Verify the management interface also works,
        # but don't test return values.
        self.f.manage_cleanup()
        key.value = 'a'
        self.f.manage_cleanup()


@total_ordering
class TrojanKey(object):
    """Pretends to be a consistent, immutable, humble citizen...

    then sweeps the rug out from under the BTree.
    """
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other

    def __lt__(self, other):
        return self.value < other

    def __hash__(self):
        return hash(self.value)
