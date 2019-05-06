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
"""Tests to check talesapi zcml configuration
"""
import unittest
from io import StringIO

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.pagetemplate.engine import Engine
import zope.browserpage

from zope.component.testing import PlacelessSetup

template = u"""<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:tales='http://namespaces.zope.org/tales'>
   %s
   </configure>"""


class Handler(object):
    pass

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.browserpage)()

    def testExpressionType(self):
        xmlconfig(StringIO(
            template %
            u"""
            <tales:expressiontype
              name="test"
              handler="zope.browserpage.tests.test_expressiontype.Handler"
              />
            """
        ))
        self.assertIn("test", Engine.getTypes())
        self.assertIs(Handler, Engine.getTypes()['test'])

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
