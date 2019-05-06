##############################################################################
#
# Copyright (c) 20!2 Zope Foundation and Contributors.
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
"""Test zope.configuration.__init__
"""
import unittest


class Test_namespace(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration import namespace
        return namespace(*args, **kw)

    def test_empty(self):
        self.assertEqual(self._callFUT(''),
                         'http://namespaces.zope.org/')

    def test_non_empty(self):
        self.assertEqual(self._callFUT('test'),
                         'http://namespaces.zope.org/test')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_namespace),
    ))
