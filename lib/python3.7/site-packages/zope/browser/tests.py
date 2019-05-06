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
"""Test Suite"""
import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.rst',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),
    ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
