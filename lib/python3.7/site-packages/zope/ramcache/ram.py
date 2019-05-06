##############################################################################
#
# Copyright (c) 2002-2009 Zope Foundation and Contributors.
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
"""RAM cache implementation.
"""
__docformat__ = 'restructuredtext'

from contextlib import contextmanager
from time import time
from threading import Lock

from six import iteritems
from six import itervalues

from persistent import Persistent
from zope.interface import implementer
from zope.location.interfaces import IContained

from zope.ramcache.interfaces.ram import IRAMCache
from zope.ramcache._compat import dumps

# A global caches dictionary shared between threads
caches = {}

# A writelock for caches dictionary
writelock = Lock()

# A counter for cache ids and its lock
cache_id_counter = 0
cache_id_writelock = Lock()


@implementer(IRAMCache, IContained)
class RAMCache(Persistent):
    """The design of this class is heavily based on RAMCacheManager in Zope2.

    The idea behind the `RAMCache` is that it should be shared between threads,
    so that the same objects are not cached in each thread. This is achieved by
    storing the cache data structure itself as a module level variable
    (`RAMCache.caches`). This, of course, requires locking on modifications of
    that data structure.

    `RAMCache` is a persistent object. The actual data storage is a volatile
    object, which can be acquired/created by calling ``_getStorage()``. Storage
    objects are shared between threads and handle their blocking internally.
    """

    __parent__ = __name__ = None

    def __init__(self):
        # A timestamp and a counter are used here because using just a
        # timestamp and an id (address) produced unit test failures on
        # Windows (where ticks are 55ms long).  If we want to use just
        # the counter, we need to make it persistent, because the
        # RAMCaches are persistent.

        with cache_id_writelock:
            global cache_id_counter
            cache_id_counter += 1
            self._cacheId = "%s_%f_%d" % (id(self), time(), cache_id_counter)

        self.requestVars = ()
        self.maxEntries = 1000
        self.maxAge = 3600
        self.cleanupInterval = 300

    def getStatistics(self):
        s = self._getStorage()
        return s.getStatistics()

    def update(self, maxEntries=None, maxAge=None, cleanupInterval=None):
        if maxEntries is not None:
            self.maxEntries = maxEntries

        if maxAge is not None:
            self.maxAge = maxAge

        if cleanupInterval is not None:
            self.cleanupInterval = cleanupInterval

        self._getStorage().update(maxEntries, maxAge, cleanupInterval)

    def invalidate(self, ob, key=None):
        s = self._getStorage()
        if key:
            key = self._buildKey(key)
            s.invalidate(ob, key)
        else:
            s.invalidate(ob)

    def invalidateAll(self):
        s = self._getStorage()
        s.invalidateAll()

    def query(self, ob, key=None, default=None):
        s = self._getStorage()
        key = self._buildKey(key)
        try:
            return s.getEntry(ob, key)
        except KeyError:
            return default

    def set(self, data, ob, key=None):
        s = self._getStorage()
        key = self._buildKey(key)
        s.setEntry(ob, key, data)

    def _getStorage(self):
        """Finds or creates a storage object."""
        cacheId = self._cacheId
        with writelock:
            if cacheId not in caches:
                caches[cacheId] = Storage(self.maxEntries, self.maxAge,
                                          self.cleanupInterval)
            return caches[cacheId]

    @staticmethod
    def _buildKey(kw):
        """Build a tuple which can be used as an index for a cached value"""
        if kw:
            items = sorted(kw.items())
            return tuple(items)
        return ()

class _StorageData(object):
    __slots__ = ('value', 'ctime', 'access_count')

    def __init__(self, value):
        self.value = value
        self.ctime = time()
        self.access_count = 0

    def __eq__(self, other):
        # For tests
        return (self.value == other.value
                and self.ctime == other.ctime
                and self.access_count == other.access_count)

    def __getstate__(self):
        # For getStatistics only.
        return self.value

class Storage(object):
    """Storage keeps the count and does the aging and cleanup of cached
    entries.

    This object is shared between threads. It corresponds to a single
    persistent `RAMCache` object. Storage does the locking necessary
    for thread safety.
    """

    def __init__(self, maxEntries=1000, maxAge=3600, cleanupInterval=300):
        self._data = {}
        self._misses = {}
        self._invalidate_queue = []
        self.maxEntries = maxEntries
        self.maxAge = maxAge
        self.cleanupInterval = cleanupInterval
        self.writelock = Lock()
        self.lastCleanup = time()

    def update(self, maxEntries=None, maxAge=None, cleanupInterval=None):
        """Set the registration options. ``None`` values are ignored."""
        if maxEntries is not None:
            self.maxEntries = maxEntries

        if maxAge is not None:
            self.maxAge = maxAge

        if cleanupInterval is not None:
            self.cleanupInterval = cleanupInterval

    def getEntry(self, ob, key):
        if self.lastCleanup <= time() - self.cleanupInterval:
            self.cleanup()

        try:
            data = self._data[ob][key]
        except KeyError:
            if ob not in self._misses:
                self._misses[ob] = 0
            self._misses[ob] += 1
            raise
        else:
            data.access_count += 1
            return data.value


    def setEntry(self, ob, key, value):
        """Stores a value for the object.  Creates the necessary
        dictionaries."""

        if self.lastCleanup <= time() - self.cleanupInterval:
            self.cleanup()

        with self._invalidate_queued_after_writelock():
            if ob not in self._data:
                self._data[ob] = {}

            self._data[ob][key] = _StorageData(value)

    def _do_invalidate(self, ob, key=None):
        """This does the actual invalidation, but does not handle the locking.

        This method is supposed to be called from `invalidate`
        """
        try:
            if key is None:
                del self._data[ob]
                self._misses[ob] = 0
            else:
                del self._data[ob][key]
                if not self._data[ob]:
                    del self._data[ob]
        except KeyError:
            pass

    @contextmanager
    def _invalidate_queued_after_writelock(self):
        """
        A context manager that obtains the writelock for the body, and
        then, after it is released, invalidates the queue.
        """
        try:
            with self.writelock:
                yield
        finally:
            self._invalidate_queued()

    def _invalidate_queued(self):
        while self._invalidate_queue:
            obj, key = self._invalidate_queue.pop()
            self.invalidate(obj, key)

    def invalidate(self, ob, key=None):
        """Drop the cached values.

        Drop all the values for an object if no key is provided or
        just one entry if the key is provided.
        """
        if self.writelock.acquire(0):
            try:
                self._do_invalidate(ob, key)
            finally:
                self.writelock.release()
        else:
            self._invalidate_queue.append((ob, key))

    def invalidateAll(self):
        """Drop all the cached values.
        """
        with self.writelock:
            self._data = {}
            self._misses = {}
            self._invalidate_queue = []

    def removeStaleEntries(self):
        """Remove the entries older than `maxAge`"""

        if self.maxAge > 0:
            punchline = time() - self.maxAge

            with self._invalidate_queued_after_writelock():
                data = self._data
                for path, path_data in tuple(iteritems(data)): # copy, we modify
                    for key, val in tuple(iteritems(path_data)): # likewise
                        if val.ctime < punchline:
                            del path_data[key]
                            if not path_data:
                                del data[path]

    def cleanup(self):
        """Cleanup the data"""
        self.removeStaleEntries()
        self.removeLeastAccessed()
        self.lastCleanup = time()

    def removeLeastAccessed(self):
        with self._invalidate_queued_after_writelock():
            data = self._data
            keys = [(ob, k) for ob, v in iteritems(data) for k in v]

            if len(keys) > self.maxEntries:
                def getKey(item):
                    ob, key = item
                    return data[ob][key].access_count
                keys.sort(key=getKey)

                ob, key = keys[self.maxEntries]
                maxDropCount = data[ob][key].access_count

                keys.reverse()

                for ob, key in keys:
                    if data[ob][key].access_count <= maxDropCount:
                        del data[ob][key]
                        if not data[ob]:
                            del data[ob]

                self._clearAccessCounters()

    def _clearAccessCounters(self):
        for path_data in itervalues(self._data):
            for val in itervalues(path_data):
                val.access_count = 0
        self._misses = {}

    def getKeys(self, object):
        return self._data[object].keys()

    def getStatistics(self):
        objects = sorted(iteritems(self._data))
        result = []

        for path, path_data in objects:
            try:
                size = len(dumps(path_data))
            except Exception:
                # Some value couldn't be pickled properly.
                # That's OK, they shouldn't have to be. Return
                # a distinct value that can be recognized as such,
                # but that also works in arithmetic.
                size = False
            hits = sum(entry.access_count for entry in itervalues(path_data))
            result.append({'path': path,
                           'hits': hits,
                           'misses': self._misses.get(path, 0),
                           'size': size,
                           'entries': len(path_data)})
        return tuple(result)
