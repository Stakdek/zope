##############################################################################
#
# Copyright (c) 2003-2009 Zope Foundation and Contributors.
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
"""Test ZCML loading
"""
import unittest

class Test_ZCML_loads(unittest.TestCase):

    def test_it(self):
        import zope.component # no registrations made if not present
        ADAPTERS_REGISTERED = 4
        from zope.configuration.xmlconfig import _clearContext
        from zope.configuration.xmlconfig import _getContext
        from zope.configuration.xmlconfig import XMLConfig
        import zope.location

        _clearContext()
        context = _getContext()
        XMLConfig('configure.zcml', zope.location)
        adapters = ([x for x in context.actions
                     if x['discriminator'] is not None])
        self.assertEqual(len(adapters), ADAPTERS_REGISTERED)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
