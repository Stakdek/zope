#############################################################################
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
"""Unit tests for RAM Cache.
"""
import unittest
from time import time


from zope.interface.verify import verifyClass, verifyObject
from zope.testing.cleanup import CleanUp

from zope.ramcache._compat import dumps
from zope.ramcache.ram import RAMCache
from zope.ramcache.ram import Storage
from zope.ramcache.tests.test_icache import BaseICacheTest
from zope.ramcache.interfaces import ICache
from zope.ramcache.interfaces.ram import IRAMCache

def _data(value, ctime, access_count):
    from zope.ramcache.ram import _StorageData
    data = _StorageData(value)
    data.ctime = ctime
    data.access_count = access_count
    return data

class TestRAMCache(CleanUp,
                   BaseICacheTest,
                   unittest.TestCase):

    def _Test__new(self):
        return RAMCache()

    def test_interface(self):
        verifyObject(IRAMCache, RAMCache())
        verifyClass(ICache, RAMCache)

    def test_init(self):
        c1 = RAMCache()._cacheId
        c2 = RAMCache()._cacheId
        self.assertNotEqual(c1, c2, "The cacheId is not unique")

    def test_getStatistics(self):
        c = RAMCache()
        c.set(42, "object", key={'foo': 'bar'})
        c.set(43, "object", key={'foo': 'bar'})
        c.query("object")
        c.query("object", key={'foo': 'bar'})
        r1 = c._getStorage().getStatistics()
        r2 = c.getStatistics()
        self.assertEqual(r1, r2, "see Storage.getStatistics() tests")

    def test_getStatistics_non_pickle(self):
        # https://github.com/zopefoundation/zope.ramcache/issues/1
        class NoPickle(object):
            def __getstate__(self):
                raise RuntimeError()

        c = RAMCache()
        c.set(NoPickle(), "path")
        stats = c.getStatistics()
        self.assertEqual(stats,
                         ({'entries': 1,
                           'hits': 0,
                           'misses': 0,
                           'path': 'path',
                           'size': False},))
        self.assertEqual(stats[0]['size'] + 1, 1)

    def test_update(self):
        c = RAMCache()
        c.update(1, 2, 3)
        s = c._getStorage()
        self.assertEqual(s.maxEntries, 1, "maxEntries not set")
        self.assertEqual(s.maxAge, 2, "maxAge not set")
        self.assertEqual(s.cleanupInterval, 3, "cleanupInterval not set")

    def test_timedCleanup(self):
        from time import sleep
        c = RAMCache()
        c.update(cleanupInterval=1, maxAge=2)
        lastCleanup = c._getStorage().lastCleanup
        sleep(2)
        c.set(42, "object", key={'foo': 'bar'})
        # last cleanup should now be updated
        self.assertTrue(lastCleanup < c._getStorage().lastCleanup)

    def test_cache(self):
        from zope.ramcache import ram
        self.assertEqual(type(ram.caches), type({}),
                         'no module level cache dictionary')

    def test_getStorage(self):
        c = RAMCache()
        c.maxAge = 123
        c.maxEntries = 2002
        c.cleanupInterval = 42
        storage1 = c._getStorage()
        storage2 = c._getStorage()
        self.assertEqual(storage1, storage2,
                         "_getStorage returns different storages")

        self.assertEqual(storage1.maxAge, 123,
                         "maxAge not set (expected 123, got %s)"
                         % storage1.maxAge)
        self.assertEqual(storage1.maxEntries, 2002,
                         "maxEntries not set (expected 2002, got %s)"
                         % storage1.maxEntries)
        self.assertEqual(storage1.cleanupInterval, 42,
                         "cleanupInterval not set (expected 42, got %s)"
                         % storage1.cleanupInterval)

        # Persist and restore the RamCache which removes
        # all _v_ attributes.
        from pickle import loads
        c2 = loads(dumps(c))
        storage2 = c2._getStorage()
        self.assertEqual(storage1, storage2,
                         "_getStorage returns different storages")

    def test_buildKey(self):
        kw = {'foo': 1, 'bar': 2, 'baz': 3}
        key = RAMCache._buildKey(kw)
        self.assertEqual(key, (('bar', 2), ('baz', 3), ('foo', 1)))

    def test_query(self):
        ob = ('aaa',)

        keywords = {"answer": 42}
        value = "true"
        c = RAMCache()
        key = RAMCache._buildKey(keywords)
        c._getStorage().setEntry(ob, key, value)

        self.assertEqual(c.query(ob, keywords), value,
                         "incorrect value")

        self.assertEqual(c.query(ob, None), None, "defaults incorrect")
        self.assertEqual(c.query(ob, {"answer": 2}, default="bummer"),
                         "bummer", "default doesn't work")

    def test_set(self):
        ob = ('path',)
        keywords = {"answer": 42}
        value = "true"
        c = RAMCache()
        c.requestVars = ('foo', 'bar')
        key = RAMCache._buildKey(keywords)

        c.set(value, ob, keywords)
        self.assertEqual(c._getStorage().getEntry(ob, key), value,
                         "Not stored correctly")

    def test_invalidate(self):
        ob1 = ("loc1",)
        ob2 = ("loc2",)
        keywords = {"answer": 42}
        keywords2 = {"answer": 41}
        value = "true"
        c = RAMCache()
        key1 = RAMCache._buildKey(keywords)
        key2 = RAMCache._buildKey(keywords)
        key3 = RAMCache._buildKey(keywords2)

        # Test invalidating entries with a keyword
        c._getStorage().setEntry(ob1, key1, value)
        c._getStorage().setEntry(ob2, key2, value)
        c._getStorage().setEntry(ob2, key3, value)

        c.invalidate(ob2, keywords)

        c._getStorage().getEntry(ob1, key1)
        self.assertRaises(KeyError, c._getStorage().getEntry, ob2, key2)
        c._getStorage().getEntry(ob2, key3)

        # Test deleting the whole object
        c._getStorage().setEntry(ob1, key1, value)
        c._getStorage().setEntry(ob2, key2, value)
        c._getStorage().setEntry(ob2, key3, value)

        c.invalidate(ob2)
        self.assertRaises(KeyError, c._getStorage().getEntry, ob2, key2)
        self.assertRaises(KeyError, c._getStorage().getEntry, ob2, key3)
        c._getStorage().getEntry(ob1, key1)

        # Try something that's not there
        c.invalidate(('yadda',))


class TestStorage(unittest.TestCase):

    def test_getEntry(self):
        s = Storage()
        object = 'object'
        key = ('view', (), ('answer', 42))
        value = 'yes'
        timestamp = time()

        s._data = {object: {key: _data(value, timestamp, 1)}}
        self.assertEqual(s.getEntry(object, key), value, 'got wrong value')

        self.assertEqual(s._data[object][key].access_count, 2,
                         'access count not updated')

        # See if _misses are updated
        with self.assertRaises(KeyError):
            s.getEntry(object, "Nonexistent")

        self.assertEqual(s._misses[object], 1)

        object2 = "second"
        self.assertNotIn(object2, s._misses)

        with self.assertRaises(KeyError):
            s.getEntry(object2, "Nonexistent")
        self.assertEqual(s._misses[object2], 1)

    def test_getEntry_do_cleanup(self):
        s = Storage(cleanupInterval=300, maxAge=300)
        object = 'object'
        key = ('view', (), ('answer', 42))
        value = 'yes'

        s.setEntry(object, key, value)

        s._data[object][key].ctime = time() - 400
        s.lastCleanup = time() - 400

        self.assertRaises(KeyError, s.getEntry, object, key)

    def test_setEntry(self):
        s = Storage(cleanupInterval=300, maxAge=300)
        object = 'object'
        key = ('view', (), ('answer', 42))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'

        t1 = time()
        s.setEntry(object, key, value)
        t2 = time()

        timestamp = s._data[object][key].ctime
        self.assertTrue(t1 <= timestamp <= t2, 'wrong timestamp')

        self.assertEqual(s._data, {object: {key: _data(value, timestamp, 0)}},
                         'stored data incorrectly')

        s._data[object][key].ctime = time() - 400
        s.lastCleanup = time() - 400

        s.setEntry(object, key2, value)

        timestamp = s._data[object][key2].ctime
        self.assertEqual(s._data, {object: {key2: _data(value, timestamp, 0)}},
                         'cleanup not called')

    def test_set_get(self):
        s = Storage()
        object = 'object'
        key = ('view', (), ('answer', 42))
        value = 'yes'
        s.setEntry(object, key, value)
        self.assertEqual(s.getEntry(object, key), value,
                         'got something other than set')

    def test_do_invalidate(self):
        s = Storage()
        object = 'object'
        object2 = 'object2'
        key = ('view', (), ('answer', 41))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'
        ts = time()
        s._data = {object:  {key: _data(value, ts, 0),
                             key2: _data(value, ts, 0)},
                   object2: {key: _data(value, ts, 0)}}
        s._misses[object] = 42
        s._do_invalidate(object)
        self.assertEqual(s._data, {object2: {key: _data(value, ts, 0)}},
                         'invalidation failed')
        self.assertEqual(s._misses[object], 0, "misses counter not cleared")

        s._data = {object:  {key: _data(value, ts, 0),
                             key2: _data(value, ts, 0)},
                   object2: {key: _data(value, ts, 0)}}
        s._do_invalidate(object, key2)
        self.assertEqual(s._data,
                         {object:  {key: _data(value, ts, 0)},
                          object2: {key: _data(value, ts, 0)}},
                         'invalidation of one key failed')

    def test_invalidate(self):
        s = Storage()
        object = 'object'
        object2 = 'object2'
        key = ('view', (), ('answer', 41))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'
        ts = time()
        s._data = {object:  {key: _data(value, ts, 0),
                             key2: _data(value, ts, 0)},
                   object2: {key: _data(value, ts, 0)}}

        s.writelock.acquire()
        try:
            s.invalidate(object)
        finally:
            s.writelock.release()
        self.assertEqual(s._invalidate_queue, [(object, None)],
                         "nothing in the invalidation queue")

        s._data = {object:  {key: _data(value, ts, 0),
                             key2: _data(value, ts, 0)},
                   object2: {key: _data(value, ts, 0)}}
        s.invalidate(object)
        self.assertEqual(s._data, {object2: {key: _data(value, ts, 0)}},
                         "not invalidated")

    def test_invalidate_queued(self):
        s = Storage()
        object = 'object'
        object2 = 'object2'
        object3 = 'object3'
        key = ('view', (), ('answer', 41))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'
        ts = time()
        s._data = {
            object: {key: _data(value, ts, 0),
                     key2: _data(value, ts, 0)},
            object2: {key: _data(value, ts, 0)},
            object3: "foo"
        }
        s._invalidate_queue = [(object2, None), (object3, None)]
        s._invalidate_queued()
        self.assertEqual(s._data,
                         {object: {key: _data(value, ts, 0),
                                   key2: _data(value, ts, 0)}},
                         "failed to invalidate queued")

    def test_invalidateAll(self):
        s = Storage()
        object = 'object'
        object2 = 'object2'
        key = ('view', (), ('answer', 41))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'
        ts = time()
        s._data = {object:  {key: _data(value, ts, 0),
                             key2: _data(value, ts, 0)},
                   object2: {key: _data(value, ts, 0)}}
        s._invalidate_queue = [(object, None)]
        s._misses = {object: 10, object2: 100}
        s.invalidateAll()
        self.assertEqual(s._data, {}, "not invalidated")
        self.assertEqual(s._misses, {}, "miss counters not reset")
        self.assertEqual(s._invalidate_queue, [], "invalidate queue not empty")

    def test_invalidate_removes_empty(self):
        s = Storage()
        ob = object()
        key = 'key'
        data = {ob: {key: 1}}
        s._data = data
        s._do_invalidate(ob, key)
        self.assertEqual(s._data, {})

    def test_getKeys(self):
        s = Storage()
        object = 'object'
        object2 = 'object2'
        key = ('view', (), ('answer', 41))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'
        ts = time()
        s._data = {object:  {key: _data(value, ts, 0),
                             key2: _data(value, ts, 0)},
                   object2: {key: _data(value, ts, 0)}}
        keys = sorted(s.getKeys(object))
        expected = sorted([key, key2])
        self.assertEqual(keys, expected, 'bad keys')

    def test_removeStale(self):
        s = Storage(maxAge=100)
        object = 'object'
        object2 = 'object2'
        key = ('view', (), ('answer', 42))
        value = 'yes'
        timestamp = time()
        s._data = {object:  {key: _data(value, timestamp-101, 2)},
                   object2: {key: _data(value, timestamp-90, 0)}}
        s.removeStaleEntries()
        self.assertEqual(s._data, {object2: {key: _data(value, timestamp-90, 0)}},
                         'stale records removed incorrectly')

        s = Storage(maxAge=0)
        s._data = {object:  {key: _data(value, timestamp, 2)},
                   object2: {key: _data(value, timestamp-90, 0)}}
        d = s._data.copy()
        s.removeStaleEntries()
        self.assertEqual(s._data, d, 'records removed when maxAge == 0')

    def test_locking(self):
        s = Storage(maxAge=100)
        with s.writelock:
            self.assertTrue(s.writelock.locked(), "locks don't work")

    def test_removeLeastAccessed(self):
        s = Storage(maxEntries=3)
        object = 'object'
        object2 = 'object2'
        key1 = ('view1', (), ('answer', 42))
        key2 = ('view2', (), ('answer', 42))
        key3 = ('view3', (), ('answer', 42))
        value = 'yes'
        timestamp = time()
        s._data = {object:  {key1: _data(value, 1, 10),
                             key2: _data(value, 6, 5),
                             key3: _data(value, 2, 2)},
                   object2: {key1: _data(value, 5, 2),
                             key2: _data(value, 3, 1),
                             key3: _data(value, 4, 1)}}
        s.removeLeastAccessed()
        self.assertEqual(s._data,
                         {object:  {key1: _data(value, 1, 0),
                                    key2: _data(value, 6, 0)}},
                         'least records removed incorrectly')

        s = Storage(maxEntries=6)
        s._data = {object:  {key1: _data(value, timestamp, 10),
                             key2: _data(value, timestamp, 5),
                             key3: _data(value, timestamp, 2)},
                   object2: {key1: _data(value, timestamp, 2),
                             key2: _data(value, timestamp, 1),
                             key3: _data(value, timestamp, 1)}}
        c = s._data.copy()
        s.removeLeastAccessed()
        self.assertEqual(s._data, c, "modified list even though len < max")

    def test__clearAccessCounters(self):
        s = Storage(maxEntries=3)
        object = 'object'
        object2 = 'object2'
        key1 = ('view1', (), ('answer', 42))
        key2 = ('view2', (), ('answer', 42))
        key3 = ('view3', (), ('answer', 42))
        value = 'yes'
        s._data = {object:  {key1: _data(value, 1, 10),
                             key2: _data(value, 2, 5),
                             key3: _data(value, 3, 2)},
                   object2: {key1: _data(value, 4, 2),
                             key2: _data(value, 5, 1),
                             key3: _data(value, 6, 1)}}
        s._misses = {object: 4, object2: 2}

        cleared = {object:  {key1: _data(value, 1, 0),
                             key2: _data(value, 2, 0),
                             key3: _data(value, 3, 0)},
                   object2: {key1: _data(value, 4, 0),
                             key2: _data(value, 5, 0),
                             key3: _data(value, 6, 0)}}
        clearMisses = {}

        s._clearAccessCounters()
        self.assertEqual(s._data, cleared, "access counters not cleared")
        self.assertEqual(s._misses, clearMisses, "misses counter not cleared")

    def test_getStatistics(self):
        s = Storage(maxEntries=3)
        object = 'object'
        object2 = 'object2'
        key1 = ('view1', (), ('answer', 42))
        key2 = ('view2', (), ('answer', 42))
        key3 = ('view3', (), ('answer', 42))
        value = 'yes'
        s._data = {object:  {key1: _data(value, 1, 10),
                             key2: _data(value, 2, 5),
                             key3: _data(value, 3, 2)},
                   object2: {key1: _data(value, 4, 2),
                             key2: _data(value, 5, 1),
                             key3: _data(value, 6, 1)}}
        s._misses = {object: 11, object2: 42}
        len1 = len(dumps(s._data[object]))
        len2 = len(dumps(s._data[object2]))

        expected = (
            {
                'path': object,
                'hits': 17,
                'misses': 11,
                'size': len1,
                'entries': 3
            },
            {
                'path': object2,
                'hits': 4,
                'misses': 42,
                'size': len2,
                'entries': 3
            },
        )

        result = s.getStatistics()
        self.assertEqual(result, expected)


class TestModule(unittest.TestCase):

    def test_locking(self):
        from zope.ramcache.ram import writelock
        with writelock:
            self.assertTrue(writelock.locked(), "locks don't work")
