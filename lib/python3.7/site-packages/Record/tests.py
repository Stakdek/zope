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

import sys
import unittest

from Record import Record

if sys.version_info >= (3, ):
    import pickle
    PY3K = True
else:
    import cPickle as pickle
    PY3K = False


class R(Record):
    __record_schema__ = {'a': 0, 'b': 1, 'c': 2}


class RSameSchema(Record):
    __record_schema__ = {'a': 0, 'b': 1, 'c': 2}


class RDifferentSchema(Record):
    __record_schema__ = {'x': 0, 'y': 1, 'z': 2}


class RecordTest(unittest.TestCase):

    def test_init(self):
        r = R()
        self.assertEqual(tuple(r), (None, None, None))
        r = R((1, 2, 3))
        self.assertEqual(tuple(r), (1, 2, 3))
        r = R([1, 2, 3])
        self.assertEqual(tuple(r), (1, 2, 3))
        r = R({})
        self.assertEqual(tuple(r), (None, None, None))
        r = R({'a': 1, 'c': 3, 'd': 4})
        self.assertEqual(tuple(r), (1, None, 3))
        r = R((1, 2))
        self.assertEqual(tuple(r), (1, 2, None))
        r = R((1, 2, 3, 4))
        self.assertEqual(tuple(r), (1, 2, 3))

    def test_init_two(self):
        parent = object()
        r = R((1, 2, None), parent)
        self.assertEqual(tuple(r), (1, 2, None))

    def test_pickling(self):
        # We can create records from sequences
        r = R(('x', 42, 1.23))
        # We can pickle them
        r2 = pickle.loads(pickle.dumps(r))
        self.assertEqual(list(r), list(r2))
        self.assertEqual(r.__record_schema__, r2.__record_schema__)

    def test_pickle_old(self):
        r = R(('x', 42, 1.23))
        p0 = ("ccopy_reg\n__newobj__\np1\n(cRecord.tests\nR\np2\ntRp3\n"
            "(S'x'\nI42\nF1.23\ntb.")
        p1 = ('ccopy_reg\n__newobj__\nq\x01(cRecord.tests\nR\nq\x02tRq\x03'
            '(U\x01xK*G?\xf3\xae\x14z\xe1G\xaetb.')
        p2 = ('\x80\x02cRecord.tests\nR\nq\x01)\x81q\x02U\x01xK*G?\xf3\xae'
            '\x14z\xe1G\xae\x87b.')
        for p in (p0, p1, p2):
            if PY3K:
                p = p.encode('latin-1')
            r2 = pickle.loads(p)
            self.assertEqual(list(r), list(r2))
            self.assertEqual(r.__record_schema__, r2.__record_schema__)

    def test_pickle_old_empty(self):
        r = R()
        p0 = 'ccopy_reg\n__newobj__\np1\n(cRecord.tests\nR\np2\ntRp3\n(NNNtb.'
        p1 = ('ccopy_reg\n__newobj__\nq\x01(cRecord.tests\nR\nq\x02tRq'
            '\x03(NNNtb.')
        p2 = '\x80\x02cRecord.tests\nR\nq\x01)\x81q\x02NNN\x87b.'
        for p in (p0, p1, p2):
            if PY3K:
                p = p.encode('latin-1')
            r2 = pickle.loads(p)
            self.assertEqual(list(r), list(r2))
            self.assertEqual(r.__record_schema__, r2.__record_schema__)

    def test_no_dict(self):
        r = R((1, 2, 3))
        d = getattr(r, '__dict__', {})
        self.assertEqual(d, {})

    def test_attribute(self):
        r = R()
        self.assertTrue(r.a is None)
        self.assertTrue(r.b is None)
        self.assertTrue(r.c is None)
        r.a = 1
        self.assertEqual(r.a, 1)
        self.assertEqual(getattr(r, 'd', 2), 2)
        self.assertRaises(AttributeError, getattr, r, 'd')
        self.assertRaises(AttributeError, setattr, r, 'd', 2)
        del r.a
        self.assertTrue(r.a is None)
        r.b = 2
        delattr(r, 'b')
        self.assertTrue(r.b is None)

    def test_mapping(self):
        r = R()
        r.a = 1
        self.assertEqual('%(a)s %(b)s %(c)s' % r, '1 None None')
        self.assertEqual(r['a'], 1)
        r['b'] = 42
        self.assertEqual(r['b'], 42)
        self.assertEqual(r.b, 42)
        self.assertRaises(KeyError, r.__getitem__, 'd')
        self.assertRaises(KeyError, r.__setitem__, 'd', 2)
        del r['a']
        self.assertTrue(r.a is None)
        self.assertRaises(TypeError, r.__delitem__, 1)

    def test_sequence(self):
        r = R()
        r.a = 1
        r.b = 42
        self.assertEqual(r[0], 1)
        self.assertEqual(r[1], 42)
        r[1] = 6
        self.assertEqual(r[1], 6)
        self.assertEqual(r.b, 6)
        r[2] = 7
        self.assertEqual(r[2], 7)
        self.assertEqual(r.c, 7)
        self.assertEqual(list(r), [1, 6, 7])

    def test_contains(self):
        r = R((1, 2, None))
        self.assertTrue('a' in r)
        self.assertTrue('c' in r)
        self.assertFalse('d' in r)

    def test_slice(self):
        r = R((1, 2, None))
        self.assertRaises(TypeError, r.__getslice__, 0, 1)
        self.assertRaises(TypeError, r.__setslice__, 0, 1, (1, 2))
        self.assertRaises(TypeError, r.__delslice__, 0, 1)

    def test_add(self):
        r1 = R((1, 2, None))
        r2 = R((1, 2, None))
        self.assertRaises(TypeError, r1.__add__, r2)

    def test_mul(self):
        r = R((1, 2, None))
        self.assertRaises(TypeError, r.__mul__, 3)

    def test_len(self):
        r = R((1, 2, None))
        self.assertEqual(len(r), 3)

    def test_hash(self):
        r1 = R((1, 2, None))
        r2 = R((1, 2, None))
        self.assertNotEqual(hash(r1), hash(r2))

    def test_hash_schema(self):
        r = R((1, 2, None))
        r_same = RSameSchema((1, 2, None))
        r_diff = RDifferentSchema((1, 2, None))
        self.assertNotEqual(hash(r), hash(r_same))
        self.assertNotEqual(hash(r), hash(r_diff))

    def test_set_members(self):
        r1 = R((1, 2, None))
        r2 = R((1, 2, None))
        r3 = R((1, 2, None))
        r_diff = RDifferentSchema((1, 2, None))
        records = set([r1])
        records.add(r2)
        self.assertTrue(r1 in records)
        self.assertTrue(r2 in records)
        self.assertFalse(r3 in records)
        self.assertEqual(len(records), 2)
        records.add(r_diff)
        self.assertEqual(len(records), 3)
        self.assertTrue(r_diff in records)

    def test_cmp(self):
        r1 = R((1, 2, 0))
        r2 = R((1, 2, 0))
        self.assertEqual(r1, r2)
        self.assertFalse(r1 is r2)
        self.assertTrue(r1 <= r2)
        self.assertTrue(r1 >= r2)
        self.assertFalse(r1 != r2)
        self.assertFalse(r1 > r2)
        self.assertFalse(r1 < r2)
        r3 = R((1, 2, 3))
        self.assertNotEqual(r1, r3)
        self.assertFalse(r1 is r3)
        self.assertTrue(r1 <= r3)
        self.assertFalse(r1 >= r3)
        self.assertTrue(r1 != r3)
        self.assertFalse(r1 > r3)
        self.assertTrue(r1 < r3)

    def test_cmp_different_schema(self):
        class R2(Record):
            __record_schema__ = {'a': 0, 'b': 1}
        r1 = R((1, 2, None))
        r2 = R2((1, 2))
        self.assertNotEqual(r1, r2)
        self.assertTrue(r1 > r2)
        self.assertFalse(r1 < r2)
        r1 = R((1, 2, 3))
        self.assertNotEqual(r1, r2)
        self.assertFalse(r1 <= r2)
        self.assertTrue(r1 >= r2)
        self.assertTrue(r1 != r2)
        self.assertTrue(r1 > r2)
        self.assertFalse(r1 < r2)

    def test_cmp_other(self):
        r = R((1, 2, None))
        self.assertNotEqual(r, (1, 2, None))
        self.assertNotEqual(r, [1, 2, None])
        self.assertNotEqual(r, {'a': 1, 'b': 2, 'c': None})
        self.assertNotEqual(r, 1)
        self.assertNotEqual(r, 'a')

    def test_repr(self):
        r = R((1, 2, None))
        self.assertTrue(repr(r).startswith('<Record.tests.R '))
        self.assertTrue(str(r).startswith('<Record.tests.R '))

    def test_schema(self):
        class R(Record):
            __record_schema__ = {'a': 0}
        R.__record_schema__ = {'a': 0, 'b': 1}
        r = R((1, 2))
        self.assertEqual(list(r), [1, 2])
        R.__record_schema__ = {'a': 0}
        # an existing instance won't get a schema update from the class
        self.assertEqual(list(r), [1, 2])
        # but new instances will use the new schema
        r2 = R((1, 2))
        self.assertEqual(list(r2), [1])

    def test_of(self):
        from ExtensionClass import Base

        class R(Record):
            __record_schema__ = {'a': 0}

        r = R((4, ))
        self.assertTrue(isinstance(r, Base))
