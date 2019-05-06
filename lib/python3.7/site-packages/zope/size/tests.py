##############################################################################
#
# Copyright (c) 2001, 2002, 2011 Zope Foundation and Contributors.
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
"""Test ISized Adapter
"""
from __future__ import unicode_literals
import unittest
from zope.size.interfaces import ISized
import zope.size

import zope.component
import zope.configuration.xmlconfig


class ZCMLTest(unittest.TestCase):

    def test_configure_zcml_should_be_loadable(self):
        try:
            zope.configuration.xmlconfig.XMLConfig(
                'configure.zcml', zope.size)()
        except Exception as e: # pragma: no cover
            self.fail(e)

    def test_configure_should_register_n_components(self):
        gsm = zope.component.getGlobalSiteManager()
        u_count = len(list(gsm.registeredUtilities()))
        a_count = len(list(gsm.registeredAdapters()))
        s_count = len(list(gsm.registeredSubscriptionAdapters()))
        h_count = len(list(gsm.registeredHandlers()))
        zope.configuration.xmlconfig.XMLConfig(
            'configure.zcml', zope.size)()
        self.assertEqual(u_count + 8, len(list(gsm.registeredUtilities())))
        self.assertEqual(a_count + 1, len(list(gsm.registeredAdapters())))
        self.assertEqual(
            s_count, len(list(gsm.registeredSubscriptionAdapters())))
        self.assertEqual(h_count, len(list(gsm.registeredHandlers())))


class DummyObject(object):

    def __init__(self, size):
        self._size = size

    def getSize(self):
        return self._size


class Test(unittest.TestCase):

    def testImplementsISized(self):
        from zope.size import DefaultSized
        sized = DefaultSized(object())
        self.assertTrue(ISized.providedBy(sized))

    def testSizeWithBytes(self):
        from zope.size import DefaultSized
        obj = DummyObject(1023)
        sized = DefaultSized(obj)
        self.assertEqual(sized.sizeForSorting(), ('byte', 1023))
        self.assertEqual(sized.sizeForDisplay(), '1 KB')

    def testSizeWithNone(self):
        from zope.size import DefaultSized
        obj = DummyObject(None)
        sized = DefaultSized(obj)
        self.assertEqual(sized.sizeForSorting(), (None, None))
        self.assertEqual(sized.sizeForDisplay(), 'not-available')

    def testSizeNotAvailable(self):
        from zope.size import DefaultSized
        sized = DefaultSized(object())
        self.assertEqual(sized.sizeForSorting(), (None, None))
        self.assertEqual(sized.sizeForDisplay(), 'not-available')

    def testVariousSizes(self):
        from zope.size import DefaultSized

        sized = DefaultSized(DummyObject(0))
        self.assertEqual(sized.sizeForSorting(), ('byte', 0))
        self.assertEqual(sized.sizeForDisplay(), '0 KB')

        sized = DefaultSized(DummyObject(1))
        self.assertEqual(sized.sizeForSorting(), ('byte', 1))
        self.assertEqual(sized.sizeForDisplay(), '1 KB')

        sized = DefaultSized(DummyObject(2048))
        self.assertEqual(sized.sizeForSorting(), ('byte', 2048))
        self.assertEqual(sized.sizeForDisplay(), '${size} KB')
        self.assertEqual(sized.sizeForDisplay().mapping, {'size': '2'})

        sized = DefaultSized(DummyObject(2000000))
        self.assertEqual(sized.sizeForSorting(), ('byte', 2000000))
        self.assertEqual(sized.sizeForDisplay(), '${size} MB')
        self.assertEqual(sized.sizeForDisplay().mapping, {'size': '1.91'})

    def test_byteDisplay(self):
        from zope.size import byteDisplay
        self.assertEqual(byteDisplay(0), '0 KB')
        self.assertEqual(byteDisplay(1), '1 KB')
        self.assertEqual(byteDisplay(2048), '${size} KB')
        self.assertEqual(byteDisplay(2048).mapping, {'size': '2'})
        self.assertEqual(byteDisplay(2000000), '${size} MB')
        self.assertEqual(byteDisplay(2000000).mapping, {'size': '1.91'})

