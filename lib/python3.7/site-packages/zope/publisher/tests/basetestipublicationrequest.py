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
"""IPublicationRequest base test
"""
import sys

from zope.interface import Interface, directlyProvides, implementer
from zope.interface.verify import verifyObject
from zope.publisher.interfaces import IPublicationRequest, IHeld
from zope.publisher.interfaces.browser import IBrowserSkinType

@implementer(IHeld)
class Held:

    released = False

    def release(self):
        self.released = True

def getrefcount(o, default=0):
    # PyPy/Jython do not have getrefcount
     return sys.getrefcount(o) if hasattr(sys, 'getrefcount') else default

class BaseTestIPublicationRequest(object):
    def testVerifyIPublicationRequest(self):
        verifyObject(IPublicationRequest, self._Test__new())

    def testHaveCustomTestsForIPublicationRequest(self):
        # Make sure that tests are defined for things we can't test here
        self.test_IPublicationRequest_getPositionalArguments

    def testTraversalStack(self):
        request = self._Test__new()
        stack = ['Engineering', 'ZopeCorp']
        request.setTraversalStack(stack)
        self.assertEqual(list(request.getTraversalStack()), stack)

    def testHoldCloseAndGetResponse(self):
        request = self._Test__new()

        response = request.response
        rcresponse = getrefcount(response)

        resource = object()
        rcresource = getrefcount(resource)

        request.hold(resource)

        resource2 = Held()
        rcresource2 = getrefcount(resource2)
        request.hold(resource2)

        self.assertTrue(getrefcount(resource, 1) > rcresource)
        self.assertTrue(getrefcount(resource2, 1) > rcresource2)
        self.assertFalse(resource2.released)

        request.close()

        self.assertTrue(resource2.released)
        # Responses are not unreferenced during close()
        self.assertTrue(getrefcount(response) >= rcresponse)
        self.assertEqual(getrefcount(resource), rcresource)
        self.assertEqual(getrefcount(resource2), rcresource2)

    def testSkinManagement(self):
        request = self._Test__new()

        class IMoreFoo(Interface):
            pass
        directlyProvides(IMoreFoo, IBrowserSkinType)

        self.assertEqual(IMoreFoo.providedBy(request), False)
        directlyProvides(request, IMoreFoo)
        self.assertEqual(IMoreFoo.providedBy(request), True)
