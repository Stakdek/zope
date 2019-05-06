##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Bound Page Template Tests
"""
import unittest

class Test(unittest.TestCase):

    def testAttributes(self):

        from zope.browserpage.tests.sample import C

        C.index.__func__.foo = 1
        self.assertEqual(C.index.macros, C.index.__func__.macros)
        self.assertEqual(C.index.filename, C.index.__func__.filename)



def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
