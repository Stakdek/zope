##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Test for PrincipalLogging adapter.
"""
import unittest
from zope.interface.verify import verifyObject
from .._compat import _u

class PrincipalStub(object):

    id = _u('\xfc principal')


class TestPrincipalLogging(unittest.TestCase):

    def test_interface(self):
        from zope.publisher.interfaces.logginginfo import ILoggingInfo
        from zope.publisher.principallogging import PrincipalLogging
        principal = PrincipalStub()
        pl = PrincipalLogging(principal)
        verifyObject(ILoggingInfo, pl)

    def test_getLogMessage(self):
        from zope.publisher.principallogging import PrincipalLogging
        principal = PrincipalStub()
        pl = PrincipalLogging(principal)
        self.assertEqual(pl.getLogMessage(), b'\\xfc principal')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPrincipalLogging))
    return suite
