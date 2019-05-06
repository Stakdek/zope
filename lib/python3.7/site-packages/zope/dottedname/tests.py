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
"""test resolution of dotted names
"""
import unittest


class Test_resolve(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.dottedname.resolve import resolve
        return resolve(*args, **kw)

    def test_no_dots_non_importable(self):
        self.assertRaises(ImportError, 
                          self._callFUT, '_non_importable_module_')

    def test_no_dots(self):
        self.assertTrue(self._callFUT('unittest') is unittest)

    def test_module_attr_nonesuch(self):
        self.assertRaises(ImportError, self._callFUT,'unittest.nonesuch')

    def test_module_attr(self):
        self.assertTrue(
            self._callFUT('unittest.TestCase') is unittest.TestCase)

    def test_submodule(self):
        from zope import dottedname
        self.assertTrue(
            self._callFUT('zope.dottedname') is dottedname)

    def test_submodule_not_yet_imported(self):
        import sys
        import zope.dottedname
        try:
            del sys.modules['zope.dottedname.example']
        except KeyError:
            pass
        try:
            del zope.dottedname.example
        except AttributeError:
            pass
        found = self._callFUT('zope.dottedname.example')
        self.assertTrue(found is sys.modules['zope.dottedname.example'])

    def test_submodule_attr(self):
        from zope.dottedname.resolve import resolve
        self.assertTrue(
            self._callFUT('zope.dottedname.resolve.resolve') is resolve)

    def test_relative_no_module(self):
        self.assertRaises(ValueError, self._callFUT,'.resolve')

    def test_relative_w_module(self):
        from zope.dottedname.resolve import resolve
        self.assertTrue(
            self._callFUT('.resolve.resolve', 'zope.dottedname') is resolve)

    def test_relative_w_module_multiple_dots(self):
        from zope.dottedname import resolve
        self.assertTrue(
            self._callFUT('..resolve', 'zope.dottedname.tests') is resolve)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_resolve),
    ))
