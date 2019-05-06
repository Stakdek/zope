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
"""Vocabulary tests
"""
__docformat__ = "reStructuredText"
import doctest
import re
import unittest

from zope.testing import renormalizing


class TestUtilityComponentInterfacesVocabulary(unittest.TestCase):

    def _getTargetClass(self):
        from zope.componentvocabulary.vocabulary import UtilityComponentInterfacesVocabulary
        return UtilityComponentInterfacesVocabulary

    def _makeOne(self, context):
        return self._getTargetClass()(context)

    def test_construct_without_registration(self):
        context = object()
        vocab = self._makeOne(context)

        self.assertIsNotNone(vocab.getTermByToken('zope.interface.Interface'))

    def test_construct_with_registration_unwraps(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface.interfaces import IUtilityRegistration

        @implementer(IUtilityRegistration)
        class Reg(object):
            def __init__(self, component):
                self.component = component

        class IComponent(Interface):
            "A component interface"

        @implementer(IComponent)
        class Component(object):
            "A component"


        reg = Reg(Component())

        vocab = self._makeOne(reg)
        self.assertIsNotNone(
            vocab.getTermByToken('zope.componentvocabulary.tests.test_vocabulary.IComponent'))


checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    ])


def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTest(
        doctest.DocTestSuite(
            'zope.componentvocabulary.vocabulary', checker=checker)
    )
    return suite
