##############################################################################
#
# Copyright (c) 2001-2009 Zope Foundation and Contributors.
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
"""Unit tests for ICache interface
"""
import unittest
from zope.interface.verify import verifyObject

from zope.ramcache.interfaces import ICache


class BaseICacheTest(unittest.TestCase):
    """Base class for ICache unit tests.  Subclasses should provide a
    _Test__new() method that returns a new empty cache object.
    """

    def _Test__new(self):
        raise unittest.SkipTest("Subclass must define")

    def testVerifyICache(self):
        # Verify that the object implements ICache
        verifyObject(ICache, self._Test__new())

    def testCaching(self):
        # Verify basic caching
        cache = self._Test__new()
        ob = "obj"
        data = "data"
        marker = []
        self.assertIs(cache.query(ob, None, default=marker), marker,
                      "empty cache should not contain anything")

        cache.set(data, ob, key={'id': 35})
        self.assertEqual(cache.query(ob, {'id': 35}), data,
                         "should return cached result")
        self.assertIs(cache.query(ob, {'id': 33}, default=marker),
                      marker,
                      "should not return cached result for a different key")

        cache.invalidate(ob, {"id": 33})
        self.assertEqual(cache.query(ob, {'id': 35}), data,
                         "should return cached result")
        self.assertIs(cache.query(ob, {'id': 33}, default=marker),
                      marker,
                      "should not return cached result after invalidate")

    def testInvalidateAll(self):
        cache = self._Test__new()
        ob1 = object()
        ob2 = object()
        cache.set("data1", ob1)
        cache.set("data2", ob2, key={'foo': 1})
        cache.set("data3", ob2, key={'foo': 2})
        cache.invalidateAll()
        marker = []
        self.assertIs(cache.query(ob1, default=marker), marker,
                      "should not return cached result after invalidateAll")
        self.assertIs(cache.query(ob2, {'foo': 1}, default=marker),
                      marker,
                      "should not return cached result after invalidateAll")
        self.assertIs(cache.query(ob2, {'foo': 2}, default=marker),
                      marker,
                      "should not return cached result after invalidateAll")
