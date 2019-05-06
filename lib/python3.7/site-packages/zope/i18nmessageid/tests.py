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
"""Message ID tests.
"""
import sys
import unittest
from zope.i18nmessageid import message as messageid


class PyMessageTests(unittest.TestCase):

    _TEST_READONLY = True

    def _getTargetClass(self):
        return messageid.pyMessage

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_defaults(self):
        message = self._makeOne('testing')
        self.assertEqual(message, 'testing')
        self.assertEqual(message.domain, None)
        self.assertEqual(message.default, None)
        self.assertEqual(message.mapping, None)
        self.assertEqual(message.msgid_plural, None)
        self.assertEqual(message.default_plural, None)
        self.assertEqual(message.number, None)
        if self._TEST_READONLY:
            self.assertTrue(message._readonly)

    def test_values(self):
        mapping = {'key': 'value'}
        message = self._makeOne(
            'testing', 'domain', 'default', mapping,
            msgid_plural='testings', default_plural="defaults", number=2)
        self.assertEqual(message, 'testing')
        self.assertEqual(message.domain, 'domain')
        self.assertEqual(message.default, 'default')
        self.assertEqual(message.mapping, mapping)
        self.assertEqual(message.msgid_plural, 'testings')
        self.assertEqual(message.default_plural, 'defaults')
        self.assertEqual(message.number, 2)
        if self._TEST_READONLY:
            self.assertTrue(message._readonly)

    def test_values_without_defaults(self):
        mapping = {'key': 'value'}
        message = self._makeOne(
            'testing', 'domain', mapping=mapping,
            msgid_plural='testings', number=2)
        self.assertEqual(message, 'testing')
        self.assertEqual(message.domain, 'domain')
        self.assertEqual(message.default, None)
        self.assertEqual(message.mapping, mapping)
        self.assertEqual(message.msgid_plural, 'testings')
        self.assertEqual(message.default_plural, None)
        self.assertEqual(message.number, 2)
        if self._TEST_READONLY:
            self.assertTrue(message._readonly)

    def test_values_with_float_for_number(self):
        mapping = {'key': 'value'}
        message = self._makeOne(
            'testing', 'domain', 'default', mapping,
            msgid_plural='testings', default_plural="defaults", number=2.2)
        self.assertEqual(message, 'testing')
        self.assertEqual(message.domain, 'domain')
        self.assertEqual(message.default, 'default')
        self.assertEqual(message.mapping, mapping)
        self.assertEqual(message.msgid_plural, 'testings')
        self.assertEqual(message.default_plural, 'defaults')
        self.assertEqual(message.number, 2.2)
        if self._TEST_READONLY:
            self.assertTrue(message._readonly)

    def test_values_with_zero(self):
        mapping = {'key': 'value'}
        message = self._makeOne(
            'testing', 'domain', 'default', mapping,
            msgid_plural='testings', default_plural="defaults", number=0)
        self.assertEqual(message, 'testing')
        self.assertEqual(message.domain, 'domain')
        self.assertEqual(message.default, 'default')
        self.assertEqual(message.mapping, mapping)
        self.assertEqual(message.msgid_plural, 'testings')
        self.assertEqual(message.default_plural, 'defaults')
        self.assertEqual(message.number, 0)
        if self._TEST_READONLY:
            self.assertTrue(message._readonly)

    def test_copy(self):
        mapping = {'key': 'value'}
        source = self._makeOne(
            'testing', 'domain', 'default', mapping,
            msgid_plural='testings', default_plural="defaults", number=0)
        message = self._makeOne(source)
        self.assertEqual(message, 'testing')
        self.assertEqual(message.domain, 'domain')
        self.assertEqual(message.default, 'default')
        self.assertEqual(message.mapping, mapping)
        self.assertEqual(message.msgid_plural, 'testings')
        self.assertEqual(message.default_plural, 'defaults')
        self.assertEqual(message.number, 0)

        # Besides just being equal, they maintain their identity
        for attr in (
                'domain',
                'default',
                'mapping',
                'msgid_plural',
                'default_plural',
                'number',
        ):
            self.assertIs(getattr(source, attr),
                          getattr(message, attr))

        if self._TEST_READONLY:
            self.assertTrue(message._readonly)

    def test_copy_with_overrides(self):
        mapping = {'key': 'value'}
        source = self._makeOne(
            'testing', 'domain', default='other', mapping=mapping,
            msgid_plural='workings', default_plural='others', number=3)
        message = self._makeOne(
            source, mapping=None, msgid_plural='override', number=0)
        self.assertEqual(message, 'testing')
        self.assertEqual(message.domain, 'domain')
        self.assertEqual(message.default, 'other')
        self.assertEqual(message.mapping, None)
        self.assertEqual(message.msgid_plural, 'override')
        self.assertEqual(message.default_plural, 'others')
        self.assertEqual(message.number, 0)
        if self._TEST_READONLY:
            self.assertTrue(message._readonly)

    def test_copy_no_default(self):
        # https://github.com/zopefoundation/zope.i18nmessageid/issues/14
        pref_msg = self._makeOne("${name} Preferences")
        self.assertIsNone(pref_msg.default)
        copy = self._makeOne(pref_msg, mapping={u'name': u'name'})
        self.assertIsNone(copy.default)

    def test_copy_no_overrides(self):
        # https://github.com/zopefoundation/zope.i18nmessageid/issues/14
        pref_msg = self._makeOne("${name} Preferences")

        copy = self._makeOne(pref_msg)
        for attr in (
                'domain',
                'default',
                'mapping',
                'msgid_plural',
                'default_plural',
                'number',
        ):
            self.assertIsNone(getattr(pref_msg, attr))
            self.assertIsNone(getattr(copy, attr))

    def test_domain_immutable(self):
        message = self._makeOne('testing')
        with self.assertRaises((TypeError, AttributeError)):
            message.domain = 'domain'

    def test_default_immutable(self):
        message = self._makeOne('testing')
        with self.assertRaises((TypeError, AttributeError)):
            message.default = 'default'

    def test_mapping_immutable(self):
        mapping = {'key': 'value'}
        message = self._makeOne('testing')
        with self.assertRaises((TypeError, AttributeError)):
            message.mapping = mapping

    def test_msgid_plural_immutable(self):
        message = self._makeOne('testing')
        with self.assertRaises((TypeError, AttributeError)):
            message.msgid_plural = 'bar'

    def test_default_plural_immutable(self):
        message = self._makeOne('testing')
        with self.assertRaises((TypeError, AttributeError)):
            message.default_plural = 'bar'

    def test_number_immutable(self):
        message = self._makeOne('testing')
        with self.assertRaises((TypeError, AttributeError)):
            message.number = 23

    def test_unknown_immutable(self):
        message = self._makeOne('testing')
        with self.assertRaises((TypeError, AttributeError)):
            message.unknown = 'unknown'

    def test___reduce__(self):
        mapping = {'key': 'value'}
        source = self._makeOne('testing')
        message = self._makeOne(
            source, 'domain', 'default', mapping,
            msgid_plural='testings', default_plural="defaults", number=2)
        klass, state = message.__reduce__()
        self.assertTrue(klass is self._getTargetClass())
        self.assertEqual(
            state,
            ('testing', 'domain', 'default', {'key': 'value'},
             'testings', 'defaults', 2))

    def test_non_unicode_default(self):
        message = self._makeOne(u'str', default=123)
        self.assertEqual(message.default, 123)

    def test_non_numeric_number(self):
        with self.assertRaises((TypeError, AttributeError)):
            self._makeOne(u'str', default=123, number="one")


@unittest.skipIf(messageid.Message is messageid.pyMessage, "Duplicate tests")
class MessageTests(PyMessageTests):

    _TEST_READONLY = False

    def _getTargetClass(self):
        return messageid.Message


@unittest.skipIf('java' in sys.platform or hasattr(sys, 'pypy_version_info'),
                 "We don't expect the C implementation here")
class OptimizationTests(unittest.TestCase):

    def test_optimizations_available(self):
        self.assertIsNot(messageid.Message, messageid.pyMessage)


class MessageFactoryTests(unittest.TestCase):

    def _getTargetClass(self):
        return messageid.MessageFactory

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test___call___defaults(self):
        factory = self._makeOne('domain')
        message = factory('testing')
        self.assertTrue(isinstance(message, messageid.Message))
        self.assertEqual(message, 'testing')
        self.assertEqual(message.domain, 'domain')
        self.assertEqual(message.default, None)
        self.assertEqual(message.mapping, None)
        self.assertEqual(message.msgid_plural, None)
        self.assertEqual(message.default_plural, None)
        self.assertEqual(message.number, None)

    def test___call___explicit(self):
        mapping = {'key': 'value'}
        factory = self._makeOne('domain')
        message = factory(
            'testing', 'default', mapping,
            msgid_plural='testings', default_plural="defaults", number=2)
        self.assertTrue(isinstance(message, messageid.Message))
        self.assertEqual(message, 'testing')
        self.assertEqual(message.domain, 'domain')
        self.assertEqual(message.default, 'default')
        self.assertEqual(message.mapping, mapping)
        self.assertEqual(message.msgid_plural, 'testings')
        self.assertEqual(message.default_plural, 'defaults')
        self.assertEqual(message.number, 2)


def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))
