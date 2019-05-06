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
"""Test fields.
"""
import unittest
import doctest
from zope.testing import cleanup

class TestMenuField(unittest.TestCase):


    def test_unconfigured(self):
        from zope.browsermenu.field import MenuField
        from zope.configuration.exceptions import ConfigurationError
        from zope.schema import ValidationError

        class Resolver(object):
            def resolve(self, name):
                raise ConfigurationError(name)

        field = MenuField()
        field = field.bind(Resolver())

        with self.assertRaises(ValidationError):
            field.fromUnicode(u'')

def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocTestSuite(
            'zope.browsermenu.field',
            setUp=lambda test: cleanup.setUp(),
            tearDown=lambda test: cleanup.tearDown()),
    ))
