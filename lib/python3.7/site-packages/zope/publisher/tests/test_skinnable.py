# -*- coding: latin-1 -*-
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
"""HTTP Publisher Tests
"""
import re
import unittest
import doctest

import zope.testing
from zope.testing.renormalizing import RENormalizing


def cleanUp(test):
    zope.testing.cleanup.cleanUp()


def test_suite():
    checker = RENormalizing([
        # Python 3 includes module name in exceptions
        (re.compile(r"__builtin__"), "builtins"),
    ])

    return unittest.TestSuite(
        doctest.DocFileSuite('../skinnable.txt',
            setUp=cleanUp, tearDown=cleanUp, checker=checker))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
