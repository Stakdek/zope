##############################################################################
#
# Copyright (c) 2013 Zope Foundation and Contributors.
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


class TestSkipppedWithLayer(unittest.TestCase):
    layer = "sample_skipped_tests.Layer"
    @unittest.skip('Hop, skipped')
    def test_layer_skipped(self):
        pass

    def test_layer_pass(self):
        pass


class Layer:
    pass


class TestSkipppedNoLayer(unittest.TestCase):
    # Only one test, so we don't have to bother about ordering when the runner
    # displays the tests' list while in verbose mode.

    @unittest.skip("I'm a skipped test!")
    def test_skipped(self):
        pass
