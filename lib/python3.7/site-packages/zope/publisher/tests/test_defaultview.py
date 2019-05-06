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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Default View Tests
"""
import unittest
from doctest import DocTestSuite
from zope.testing.cleanup import cleanUp

def cleanUpDoc(args):
    cleanUp()

def test_suite():
    return DocTestSuite('zope.publisher.defaultview',
            setUp=cleanUpDoc, tearDown=cleanUpDoc)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
