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
"""Registration Tests
"""
__docformat__ = "reStructuredText"

import unittest


import persistent
import transaction
import zope.component.globalregistry
import zope.component.testing as placelesssetup
import zope.container.contained
import zope.site

from zope import interface


# test class for testing data conversion
class IFoo(interface.Interface):
    pass


@interface.implementer(IFoo)
class Foo(persistent.Persistent, zope.container.contained.Contained):
    name = ''
    def __init__(self, name=''):
        self.name = name

class GlobalRegistry:
    pass


base = zope.component.globalregistry.GlobalAdapterRegistry(
    GlobalRegistry, 'adapters')
GlobalRegistry.adapters = base


def clear_base():
    base.__init__(GlobalRegistry, 'adapters')


class Test(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

    def tearDown(self):
        placelesssetup.tearDown(self)

    def test_deghostification_of_persistent_adapter_registries(self):

        # Note that this test duplicates one from zope.component.tests.
        # We should be able to get rid of this one when we get rid of
        # __setstate__ implementation we have in back35.

        # We want to make sure that we see updates correctly.

        from ZODB.MappingStorage import DB
        db = DB()
        tm1 = transaction.TransactionManager()
        c1 = db.open(transaction_manager=tm1)
        r1 = zope.site.site._LocalAdapterRegistry((base,))
        r2 = zope.site.site._LocalAdapterRegistry((r1,))
        c1.root()[1] = r1
        c1.root()[2] = r2
        tm1.commit()
        r1._p_deactivate()
        r2._p_deactivate()

        tm2 = transaction.TransactionManager()
        c2 = db.open(transaction_manager=tm2)
        r1 = c2.root()[1]
        r2 = c2.root()[2]

        self.assertIsNone(r1.lookup((), IFoo, ''))

        foo_blank = Foo('')
        base.register((), IFoo, '', foo_blank)
        self.assertEqual(r1.lookup((), IFoo, ''),
                         foo_blank)

        self.assertIsNone(r2.lookup((), IFoo, '1'))

        foo_1 = Foo('1')
        r1.register((), IFoo, '1', foo_1)

        self.assertEqual(r2.lookup((), IFoo, '1'),
                         foo_1)

        self.assertIsNone(r1.lookup((), IFoo, '2'))
        self.assertIsNone(r2.lookup((), IFoo, '2'))

        foo_2 = Foo('2')
        base.register((), IFoo, '2', foo_2)

        self.assertEqual(r1.lookup((), IFoo, '2'),
                         foo_2)

        self.assertEqual(r2.lookup((), IFoo, '2'),
                         foo_2)

        # Cleanup:

        db.close()
        clear_base()
