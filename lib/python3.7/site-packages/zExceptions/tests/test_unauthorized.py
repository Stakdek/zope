##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
"""Unit tests for unauthorized module.
"""

import unittest
from zope.interface.verify import verifyClass
from .._compat import unicode


class UnauthorizedTests(unittest.TestCase):

    def _getTargetClass(self):
        from zExceptions.unauthorized import Unauthorized
        return Unauthorized

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_interfaces(self):
        from zope.security.interfaces import IUnauthorized

        verifyClass(IUnauthorized, self._getTargetClass())

    def test_empty(self):
        exc = self._makeOne()

        self.assertEqual(exc.name, None)
        self.assertEqual(exc.message, None)
        self.assertEqual(exc.value, None)
        self.assertEqual(exc.needed, None)

        self.assertEqual(bytes(exc), b'Unauthorized()')
        self.assertEqual(unicode(exc), u'Unauthorized()')

    def test_ascii_message(self):
        arg = b'ERROR MESSAGE'
        exc = self._makeOne(arg)

        self.assertEqual(exc.name, None)
        self.assertEqual(exc.message, arg)
        self.assertEqual(exc.value, None)
        self.assertEqual(exc.needed, None)

        self.assertEqual(bytes(exc), arg)
        self.assertEqual(unicode(exc), arg.decode('ascii'))

    def test_encoded_message(self):
        arg = u'ERROR MESSAGE \u03A9'.encode('utf-8')
        exc = self._makeOne(arg)

        self.assertEqual(exc.name, None)
        self.assertEqual(exc.message, arg)
        self.assertEqual(exc.value, None)
        self.assertEqual(exc.needed, None)

        self.assertEqual(bytes(exc), arg)
        self.assertEqual(unicode(exc), arg.decode('utf-8'))

    def test_unicode_message(self):
        arg = u'ERROR MESSAGE \u03A9'
        exc = self._makeOne(arg)

        self.assertEqual(exc.name, None)
        self.assertEqual(exc.message, arg)
        self.assertEqual(exc.value, None)
        self.assertEqual(exc.needed, None)

        self.assertEqual(bytes(exc), arg.encode('utf-8'))
        self.assertEqual(unicode(exc), arg)

    def test_ascii_name(self):
        arg = b'ERROR_NAME'
        exc = self._makeOne(arg)

        self.assertEqual(exc.name, arg)
        self.assertEqual(exc.message, None)
        self.assertEqual(exc.value, None)
        self.assertEqual(exc.needed, None)

        self.assertEqual(
            bytes(exc),
            b"You are not allowed to access 'ERROR_NAME' in this context")
        self.assertEqual(
            unicode(exc),
            u"You are not allowed to access 'ERROR_NAME' in this context")

    def test_encoded_name(self):
        arg = u'ERROR_NAME_\u03A9'.encode('utf-8')
        exc = self._makeOne(arg)

        self.assertEqual(exc.name, arg)
        self.assertEqual(exc.message, None)
        self.assertEqual(exc.value, None)
        self.assertEqual(exc.needed, None)

        self.assertEqual(
            bytes(exc),
            (b"You are not allowed to access "
             b"'ERROR_NAME_\xce\xa9' in this context"))
        self.assertEqual(
            unicode(exc),
            u"You are not allowed to access "
            u"'ERROR_NAME_\u03A9' in this context")

    def test_unicode_name(self):
        arg = u'ERROR_NAME_\u03A9'
        exc = self._makeOne(arg)

        self.assertEqual(exc.name, arg)
        self.assertEqual(exc.message, None)
        self.assertEqual(exc.value, None)
        self.assertEqual(exc.needed, None)

        self.assertEqual(
            bytes(exc),
            (b"You are not allowed to access "
             b"'ERROR_NAME_\xce\xa9' in this context"))
        self.assertEqual(
            unicode(exc),
            u"You are not allowed to access "
            u"'ERROR_NAME_\u03A9' in this context")
