##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Test zope.publisher.browser doctests
"""
import re
import unittest
from doctest import DocTestSuite

from zope.testing.renormalizing import RENormalizing

__docformat__ = "reStructuredText"

def test_suite():

    checker = RENormalizing([
        # Python 3 includes module name in exceptions
        (re.compile(r"zope.publisher.interfaces.NotFound"), "NotFound"),
    ])

    return unittest.TestSuite((
        DocTestSuite('zope.publisher.browser', checker=checker),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
