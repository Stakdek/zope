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
import unittest

from zope.annotation.tests.annotations import AnnotationsTestBase

class AttributeAnnotationsTest(AnnotationsTestBase, unittest.TestCase):

    def setUp(self):
        from zope.testing import cleanup
        from zope.interface import implementer
        from zope.annotation.attribute import AttributeAnnotations
        from zope.annotation.interfaces import IAttributeAnnotatable

        cleanup.setUp()

        @implementer(IAttributeAnnotatable)
        class Dummy(object):
            pass

        self.obj = Dummy()
        self.annotations = AttributeAnnotations(self.obj)

    def tearDown(self):
        from zope.testing import cleanup
        cleanup.tearDown()

    def testInterfaceVerifies(self):
        super(AttributeAnnotationsTest, self).testInterfaceVerifies()
        self.assertIs(self.obj, self.annotations.__parent__)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
