##############################################################################
#
# Copyright (c) 2013 Zope Foundation and Contributors.
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
"""Contained Tests
"""

import gc
import unittest

try:
    from ZODB.DemoStorage import DemoStorage
    from ZODB.DB import DB
    import transaction
    HAVE_ZODB = True
except ImportError: # pragma: no cover
    HAVE_ZODB = False

from persistent import Persistent

from zope.container.contained import ContainedProxy


class MyOb(Persistent):
    pass

@unittest.skipUnless(HAVE_ZODB, "Needs ZODB")
class TestContainedZODB(unittest.TestCase):

    def setUp(self):
        self.db = DB(DemoStorage('test_storage'))

    def tearDown(self):
        self.db.close()

    def test_basic_persistent_w_non_persistent_proxied(self):
        p = ContainedProxy([1])
        p.__parent__ = 2
        p.__name__ = 'test'
        db = self.db
        c = db.open()
        c.root()['p'] = p
        transaction.commit()

        c2 = db.open()
        p2 = c2.root()['p']
        self.assertEqual([1], p2)
        self.assertEqual(2, p2.__parent__)
        self.assertEqual('test', p2.__name__)

        self.assertEqual(0, p2._p_changed)
        p2._p_deactivate()
        self.assertFalse(bool(p2._p_changed))

        self.assertEqual(p2.__name__, 'test')

    def test_basic_persistent_w_persistent_proxied(self):
        # Here, we'll verify that shared references work and
        # that updates to both the proxies and the proxied objects
        # are made correctly.
        #
        #        ----------------------
        #        |                    |
        #      parent                other
        #        |                 /
        #       ob  <--------------

        # Here we have an object, parent, that contains ob.  There is another
        # object, other, that has a non-container reference to ob.

        parent = MyOb()
        parent.ob = ContainedProxy(MyOb())
        parent.ob.__parent__ = parent
        parent.ob.__name__ = 'test'
        other = MyOb()
        other.ob = parent.ob

        # We can change ob through either parent or other

        parent.ob.x = 1
        other.ob.y = 2

        # Now we'll save the data:

        db = self.db
        c1 = db.open()
        c1.root()['parent'] = parent
        c1.root()['other'] = other
        transaction.commit()

        # We'll open a second connection and verify that we have the data we
        # expect:

        c2 = db.open()
        p2 = c2.root()['parent']
        self.assertIs(p2.ob.__parent__, p2)

        self.assertEqual(1, p2.ob.x)
        self.assertEqual(2, p2.ob.y)

        o2 = c2.root()['other']
        self.assertIs(o2.ob, p2.ob)
        self.assertIs(o2.ob, p2.ob)
        self.assertEqual('test', o2.ob.__name__)


        # Now we'll change things around a bit. We'll move things around
        # a bit. We'll also add an attribute to ob

        o2.ob.__name__ = 'test 2'
        o2.ob.__parent__ = o2
        o2.ob.z = 3

        self.assertIsNot(p2.ob.__parent__, p2)
        self.assertIs(p2.ob.__parent__, o2)

        # And save the changes:

        transaction.commit()

        # Now we'll reopen the first connection and verify that we can see
        # the changes:

        c1.close()
        c1 = db.open()
        p2 = c1.root()['parent']
        self.assertEqual('test 2', p2.ob.__name__)

        self.assertEqual(3, p2.ob.z)
        self.assertIs(p2.ob.__parent__, c1.root()['other'])

    def test_proxy_cache_interaction(self):
        # Test to make sure the proxy properly interacts with the object cache

        # Persistent objects are their own weak refs.  Thier deallocators
        # need to notify their connection's cache that their object is being
        # deallocated, so that it is removed from the cache.

        db = self.db
        db.setCacheSize(5)
        conn = db.open()
        conn.root()['p'] = ContainedProxy(None)

        # We need to create some filler objects to push our proxy out of the cache:

        for i in range(10):
            conn.root()[i] = MyOb()

        transaction.commit()

        # Let's get the oid of our proxy:

        oid = conn.root()['p']._p_oid

        # Now, we'll access the filler object's:
        for i in range(10):
            getattr(conn.root()[i], 'x', 0)

        # We've also accessed the root object. If we garbage-collect the
        # cache:

        conn._cache.incrgc()

        # Then the root object will still be active, because it was accessed
        # recently:

        self.assertEqual(0, conn.root()._p_changed)

        # And the proxy will be in the cache, because it's refernced from
        # the root object:

        self.assertIsNotNone(conn._cache.get(oid))

        # But it's a ghost:

        self.assertFalse(bool(conn.root()['p']._p_changed))


        # If we deactivate the root object:

        conn.root()._p_deactivate()

        # Then we'll release the last reference to the proxy and it should
        # no longer be in the cache. To be sure, we'll call gc:

        gc.collect()
        self.assertIsNone(conn._cache.get(oid))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main()
