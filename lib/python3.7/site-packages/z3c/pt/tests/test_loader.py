##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
import unittest


class LoadTests:
    def _makeOne(self, search_path=None, **kwargs):
        klass = self._getTargetClass()
        return klass(search_path, **kwargs)

    def _getTargetClass(self):
        from z3c.pt.loader import TemplateLoader

        return TemplateLoader

    def test_load_relative(self):
        import os

        here = os.path.dirname(__file__)
        loader = self._makeOne(search_path=[here])

        result = self._load(loader, "view.pt")
        self.assertEqual(result.filename, os.path.join(here, "view.pt"))

    def test_consecutive_loads(self):
        import os

        here = os.path.dirname(__file__)
        loader = self._makeOne(search_path=[here])

        self.assertTrue(
            self._load(loader, "view.pt") is self._load(loader, "view.pt")
        )

    def test_load_relative_badpath_in_searchpath(self):
        import os

        here = os.path.dirname(__file__)
        loader = self._makeOne(search_path=[os.path.join(here, "none"), here])
        result = self._load(loader, "view.pt")
        self.assertEqual(result.filename, os.path.join(here, "view.pt"))

    def test_load_abs(self):
        import os

        here = os.path.dirname(__file__)
        loader = self._makeOne()
        abs = os.path.join(here, "view.pt")
        result = self._load(loader, abs)
        self.assertEqual(result.filename, abs)


class LoadPageTests(unittest.TestCase, LoadTests):
    def _load(self, loader, filename):
        return loader.load_page(filename)


def test_suite():
    import sys

    return unittest.findTestCases(sys.modules[__name__])
