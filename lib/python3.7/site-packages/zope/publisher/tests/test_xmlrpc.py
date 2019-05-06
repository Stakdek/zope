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
"""Testing the XML-RPC Publisher code.
"""
import doctest
import unittest

import zope.component.testing
from zope.publisher import xmlrpc
from zope.security.checker import defineChecker, Checker, CheckerPublic

try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib

class TestXMLRPCResponse(unittest.TestCase):

    def testConsumeBody(self):
        response = xmlrpc.XMLRPCResponse()
        response.setResult(['hi'])

        body = response.consumeBody()
        self.assertIsInstance(body, bytes)
        self.assertIn(b'<methodResponse>', body)


def doctest_setUp(test):
    zope.component.testing.setUp(test)
    zope.component.provideAdapter(xmlrpc.ListPreMarshaller)
    zope.component.provideAdapter(xmlrpc.TuplePreMarshaller)
    zope.component.provideAdapter(xmlrpc.BinaryPreMarshaller)
    zope.component.provideAdapter(xmlrpc.FaultPreMarshaller)
    zope.component.provideAdapter(xmlrpc.DateTimePreMarshaller)
    zope.component.provideAdapter(xmlrpc.PythonDateTimePreMarshaller)
    zope.component.provideAdapter(xmlrpc.DictPreMarshaller)

    defineChecker(xmlrpclib.Binary,
                  Checker({'data':CheckerPublic,
                           'decode':CheckerPublic,
                           'encode': CheckerPublic}, {}))
    defineChecker(xmlrpclib.Fault,
                  Checker({'faultCode':CheckerPublic,
                           'faultString': CheckerPublic}, {}))
    defineChecker(xmlrpclib.DateTime,
                  Checker({'value':CheckerPublic}, {}))

def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocFileSuite(
            "xmlrpc.txt",
            package="zope.publisher",
            setUp=doctest_setUp,
            tearDown=zope.component.testing.tearDown,
            optionflags=doctest.ELLIPSIS
        ),
    ))
