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

import math
import os
import unittest

import App.config
from Products.ExternalMethod.ExternalMethod import ExternalMethod


class TestExternalMethod(unittest.TestCase):

    def setUp(self):
        test_dir, _ = os.path.split(__file__)
        self._old = App.config.getConfiguration()
        cfg = App.config.DefaultConfiguration()
        cfg.instancehome = test_dir
        App.config.setConfiguration(cfg)

    def tearDown(self):
        App.config.setConfiguration(self._old)

    def testStorage(self):
        em1 = ExternalMethod('em', 'test method', 'Test', 'testf')
        self.assertEqual(em1(4), math.sqrt(4))
        state = em1.__getstate__()
        em2 = ExternalMethod.__basicnew__()
        em2.__setstate__(state)
        self.assertEqual(em2(9), math.sqrt(9))
        self.assertNotIn('__defaults__', state)

    def test_mapply(self):
        from ZPublisher.mapply import mapply

        em1 = ExternalMethod('em', 'test method', 'Test', 'testf')
        self.assertEqual(mapply(em1, (), {'arg1': 4}), math.sqrt(4))
        state = em1.__getstate__()
        em2 = ExternalMethod.__basicnew__()
        em2.__setstate__(state)
        self.assertEqual(mapply(em1, (), {'arg1': 9}), math.sqrt(9))
