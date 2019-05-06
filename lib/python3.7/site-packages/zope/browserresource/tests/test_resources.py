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
"""Test Browser Resources
"""

import re
import doctest
import unittest
from zope.testing import cleanup
from zope.testing.renormalizing import RENormalizing

def setUp(test):
    cleanup.setUp()

def tearDown(test):
    cleanup.tearDown()

def test_suite():
    checker = RENormalizing([
        # Python 3 includes module name in exceptions
        (re.compile(r"zope.publisher.interfaces.NotFound"),
         "NotFound"),
    ])
    return unittest.TestSuite((
        doctest.DocTestSuite(
            'zope.browserresource.resources',
            setUp=setUp, tearDown=tearDown,
            checker=checker,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE),
        ))
