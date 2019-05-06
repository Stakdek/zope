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

import unittest


class TestMultiMapping(unittest.TestCase):

    def _getTargetClass(self):
        from MultiMapping import MultiMapping
        return MultiMapping

    def _makeOne(self):
        return self._getTargetClass()()

    def test_push(self):
        m = self._makeOne()
        m.push({'spam': 1, 'eggs': 2})
        self.assertEqual(m['spam'], 1)
        self.assertEqual(m['eggs'], 2)

    def test_push_multiple(self):
        m = self._makeOne()
        m.push({'spam': 1, 'eggs': 2})
        m.push({'spam': 3})
        self.assertEqual(m['spam'], 3)
        self.assertEqual(m['eggs'], 2)

    def test_pop(self):
        m = self._makeOne()
        m.push({'spam': 1, 'eggs': 2})
        m.push({'spam': 3})
        self.assertEqual(m.pop(), {'spam': 3})
        self.assertEqual(m.pop(), {'spam': 1, 'eggs': 2})
        self.assertRaises(IndexError, m.pop)

    def test_getitem_not_found(self):
        m = self._makeOne()
        self.assertRaises(KeyError, m.__getitem__, 'ham')

    def test_get(self):
        m = self._makeOne()
        m.push({'spam': 1})
        self.assertEqual(m.get('spam'), 1)
        self.assertEqual(m.get('eggs'), None)

    def test_contains(self):
        m = self._makeOne()
        m.push({'spam': 1})
        self.assertTrue('spam' in m)
        self.assertFalse('eggs' in m)

    def test_has_key(self):
        m = self._makeOne()
        m.push({'spam': 1})
        self.assertTrue(m.has_key('spam'))  # NOQA
        self.assertFalse(m.has_key('eggs'))  # NOQA

    def test_len(self):
        m = self._makeOne()
        m.push({'spam': 1})
        self.assertEqual(len(m), 1)

    def test_is_extension_class(self):
        from ExtensionClass import Base
        self.assertTrue(isinstance(self._makeOne(), Base))
