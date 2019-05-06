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
"""Test the OrderedContainer.
"""
import unittest
from doctest import DocTestSuite

from zope.component.eventtesting import getEvents, clearEvents
from zope.container import testing
from zope.container.tests.test_icontainer import TestSampleContainer

class TestOrderedContainer(TestSampleContainer):

    def test_order_events(self):
        # Prepare the setup::
        from zope.container.contained import ContainerModifiedEvent

        # Prepare some objects::

        from zope.container.ordered import OrderedContainer
        oc = OrderedContainer()
        oc['foo'] = 'bar'
        oc['baz'] = 'quux'
        oc['zork'] = 'grue'
        self.assertEqual(oc.keys(),
                         ['foo', 'baz', 'zork'])

        # Now change the order::

        clearEvents()
        oc.updateOrder(['baz', 'foo', 'zork'])
        self.assertEqual(oc.keys(),
                         ['baz', 'foo', 'zork'])

        # Check what events have been sent::

        events = getEvents()
        self.assertEqual(1, len(events))
        self.assertIsInstance(events[0], ContainerModifiedEvent)

        # This is in fact a specialized modification event::

        from zope.lifecycleevent.interfaces import IObjectModifiedEvent
        self.assertTrue(IObjectModifiedEvent.providedBy(events[0]))


    def test_order_all_items_available_at_object_added_event(self):
        # Now register an event subscriber to object added events.
        import zope.component
        from zope.lifecycleevent.interfaces import IObjectAddedEvent

        keys = []
        @zope.component.adapter(IObjectAddedEvent)
        def printContainerKeys(event):
            keys.extend(event.newParent.keys())


        zope.component.provideHandler(printContainerKeys)

        # Now we are adding an object to the container.

        from zope.container.ordered import OrderedContainer
        oc = OrderedContainer()
        oc['foo'] = 'FOO'

        self.assertEqual(keys, ['foo'])

    def test_order_adding_none(self):
        # This is a regression test: adding None to an OrderedContainer
        # used to corrupt its internal data structure (_order and _data
        # would get out of sync, causing KeyErrors when you tried to iterate).

        from zope.container.ordered import OrderedContainer
        oc = OrderedContainer()
        oc['foo'] = None
        self.assertEqual(oc.keys(), ['foo'])
        self.assertEqual(oc.values(), [None])
        self.assertEqual(oc.items(),
                         [('foo', None)])
        # None got proxied, so 'is None is not true
        self.assertIsNotNone(oc['foo'])
        self.assertEqual(None, oc['foo'])

    def test_order_updateOrder_bytes(self):
        # https://github.com/zopefoundation/zope.container/issues/21
        from zope.container.ordered import OrderedContainer
        keys = [u'a', u'b']
        oc = OrderedContainer()
        oc[keys[0]] = 0
        oc[keys[1]] = 1

        self.assertEqual(keys, oc.keys())

        # Updating with bytes keys...
        oc.updateOrder((b'b', b'a'))
        # still produces text keys
        text_type = str if str is not bytes else unicode
        self.assertEqual(list(reversed(keys)), oc.keys())
        self.assertIsInstance(oc.keys()[0], text_type)


def test_suite():
    suite = unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ])
    suite.addTest(DocTestSuite("zope.container.ordered",
                               setUp=testing.setUp,
                               tearDown=testing.tearDown,
                               checker=testing.checker))

    return suite

if __name__ == '__main__':
    unittest.main()
