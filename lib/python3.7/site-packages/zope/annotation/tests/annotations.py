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
"""General Annotations Tests

All objects implementing 'IAnnotations' should pass these tests. They might be
used as base tests for real implementations.
"""
from zope.interface.verify import verifyObject
from zope.annotation.interfaces import IAnnotations

class AnnotationsTestBase(object):
    """Test the IAnnotations interface.

    The test case class expects the 'IAnnotations' implementer to be in
    'self.annotations'.
    """

    annotations = None
    obj = None

    def test_nonzero(self):
        self.assertFalse(self.annotations)
        self.annotations['unittest'] = self.obj
        self.assertTrue(self.annotations)
        del self.annotations['unittest']
        self.assertFalse(self.annotations)

    def testInterfaceVerifies(self):
        verifyObject(IAnnotations, self.annotations)

    def testStorage(self):
        # test __getitem__
        self.annotations['unittest'] = self.obj
        res = self.annotations['unittest']
        self.assertEqual(self.obj, res)

    def testGetitemException(self):
        # test __getitem__ raises exception on unknown key
        self.assertRaises(KeyError, self.annotations.__getitem__,'randomkey')

    def testGet(self):
        # test get
        self.annotations['unittest'] = self.obj
        res = self.annotations.get('unittest')
        self.assertEqual(self.obj, res)

    def testGetNoSet(self):
        # test get with no set
        res = self.annotations.get('randomkey')
        self.assertEqual(None, res)

    def testGetDefault(self):
        # test get returns default
        res = self.annotations.get('randomkey', 'default')
        self.assertEqual('default', res)

    def testDel(self):
        self.annotations['unittest'] = self.obj
        del self.annotations['unittest']
        self.assertEqual(None, self.annotations.get('unittest'))
        self.assertEqual([], list(self.annotations.keys()))
        self.assertEqual([], list(self.annotations))
        self.assertEqual(0, len(self.annotations))

    def testDelRaisesKeyError(self):
        self.assertRaises(KeyError, self.annotations.__delitem__, 'unittest')

    def testKeys(self):
        self.assertEqual([], list(self.annotations.keys()))
        self.annotations['unittest'] = self.obj
        self.assertEqual(1, len(self.annotations))
        self.assertEqual(['unittest'], list(self.annotations.keys()))

    def testIter(self):
        self.assertEqual([], list(self.annotations))
        self.annotations['unittest'] = self.obj
        self.assertEqual(1, len(self.annotations))
        self.assertEqual(['unittest'], list(self.annotations))
        self.assertEqual(1, len(self.annotations))
