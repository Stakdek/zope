##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
import unittest


class ConnectionTests(unittest.TestCase):

    def _getTargetClass(self):
        from Shared.DC.ZRDB.Connection import Connection
        return Connection

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_connect_on_load(self):

        class _Connection(self._getTargetClass()):

            def connect(self, connection_string):
                setattr(self, '_connected_to', connection_string)

        conn1 = _Connection('conn1', '', 'conn string 1')
        conn1.__setstate__(None)
        self.assertEqual(conn1._connected_to, 'conn string 1')

        conn2 = _Connection('conn2', '', 'conn string 2')
        conn2.connect_on_load = False
        conn2.__setstate__(None)
        self.assertFalse(hasattr(conn2, '_connected_to'))

    def test_sql_quote___miss(self):
        TO_QUOTE = "no quoting required"
        conn = self._makeOne('conn', '', 'conn string')
        self.assertEqual(conn.sql_quote__(TO_QUOTE), "'%s'" % TO_QUOTE)

    def test_sql_quote___embedded_apostrophe(self):
        TO_QUOTE = "w'embedded apostrophe"
        conn = self._makeOne('conn', '', 'conn string')
        self.assertEqual(conn.sql_quote__(TO_QUOTE),
                         "'w''embedded apostrophe'")

    def test_sql_quote___embedded_null(self):
        TO_QUOTE = "w'embedded apostrophe and \x00null"
        conn = self._makeOne('conn', '', 'conn string')
        self.assertEqual(conn.sql_quote__(TO_QUOTE),
                         "'w''embedded apostrophe and null'")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ConnectionTests))
    return suite
