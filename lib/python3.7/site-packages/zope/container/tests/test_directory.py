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
"""FS-based directory implementation tests for containers
"""

import doctest
import unittest

from zope.container import testing
from zope.container import directory


class Directory(object):
    a = None

class TestCloner(unittest.TestCase):

    def test_Cloner(self):
        d = Directory()
        d.a = 1
        clone = directory.Cloner(d)('foo')
        self.assertIsNot(clone, d)
        self.assertEqual(clone.__class__, d.__class__)


class TestNoop(unittest.TestCase):

    def test_noop(self):
        self.assertIs(self, directory.noop(self))


class TestRootDirectoryFactory(unittest.TestCase):

    def test_returns_folder(self):
        from zope.container.folder import Folder
        factory = directory.RootDirectoryFactory(None)
        self.assertIsInstance(factory(None), Folder)

def test_suite():
    flags = doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocFileSuite("directory.rst",
                             setUp=testing.setUp, tearDown=testing.tearDown,
                             optionflags=flags),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
