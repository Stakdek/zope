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
import doctest
import unittest

import zope.component.testing
import zope.configuration.xmlconfig
import z3c.pt

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


def setUp(suite):
    zope.component.testing.setUp(suite)
    zope.configuration.xmlconfig.XMLConfig("configure.zcml", z3c.pt)()


def test_suite():
    return unittest.TestSuite(
        [
            doctest.DocFileSuite(
                "README.rst",
                optionflags=OPTIONFLAGS,
                setUp=setUp,
                tearDown=zope.component.testing.tearDown,
                package="z3c.pt",
            ),
            doctest.DocTestSuite(
                "z3c.pt.expressions",
                optionflags=OPTIONFLAGS,
                setUp=setUp,
                tearDown=zope.component.testing.tearDown,
            ),
            doctest.DocTestSuite(
                "z3c.pt.namespaces",
                optionflags=OPTIONFLAGS,
                setUp=setUp,
                tearDown=zope.component.testing.tearDown,
            ),
        ]
    )
