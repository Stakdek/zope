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
"""Test lang traversal.
"""
import unittest

import zope.component
from zope.annotation import IAttributeAnnotatable, IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.interface import directlyProvides
from zope.publisher.browser import ModifiableBrowserLanguages
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.tests import test_browserlanguages
from zope.i18n.interfaces import IModifiableUserPreferredLanguages
from zope.traversing.namespace import lang
from zope.testing.cleanup import CleanUp


class TestRequest(test_browserlanguages.TestRequest):

    def shiftNameToApplication(self):
        self.shifted = True

class Test(CleanUp, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()

        self.request = TestRequest("en")
        directlyProvides(self.request, IHTTPRequest, IAttributeAnnotatable)
        zope.component.provideAdapter(AttributeAnnotations,
                                      (IAttributeAnnotatable,), IAnnotations)
        zope.component.provideAdapter(ModifiableBrowserLanguages,
                                      (IHTTPRequest,),
                                      IModifiableUserPreferredLanguages)

    def test_adapter(self):
        request = self.request
        browser_languages = IModifiableUserPreferredLanguages(request)
        self.assertEqual(["en"], browser_languages.getPreferredLanguages())

        ob = object()
        ob2 = lang(ob, request).traverse('ru', ())
        self.assertTrue(ob is ob2)
        self.assertTrue(request.shifted)
        self.assertEqual(["ru"], browser_languages.getPreferredLanguages())
