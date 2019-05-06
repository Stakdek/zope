##############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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
# Test BWC shims

import unittest
import warnings

class TestNext(unittest.TestCase):

    def test_import(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')

            from zope.site import next as FUT
            self.assertTrue(hasattr(FUT, 'queryNextUtility'))


class TestHooks(unittest.TestCase):

    def test_import(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')

            from zope.site import hooks as FUT
            self.assertTrue(hasattr(FUT, 'setSite'))
