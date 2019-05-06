##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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

import unittest
import zope.component
import zope.componentvocabulary
import zope.configuration.xmlconfig


class ZCMLTest(unittest.TestCase):

    def test_configure_zcml_should_be_loadable(self):
        # If this raises, let it be a test error.
        # We get a more clear exception than if we catch
        # what it raises and do self.fail(ex)
        zope.configuration.xmlconfig.XMLConfig(
                'configure.zcml', zope.componentvocabulary)()

    def test_configure_should_register_n_utilities(self):
        gsm = zope.component.getGlobalSiteManager()
        count = len(list(gsm.registeredUtilities()))
        zope.configuration.xmlconfig.XMLConfig(
            'configure.zcml', zope.componentvocabulary)()
        self.assertEqual(count + 5, len(list(gsm.registeredUtilities())))
