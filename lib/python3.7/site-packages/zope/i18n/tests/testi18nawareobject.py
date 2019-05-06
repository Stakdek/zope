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
"""This is a test for the II18nAware interface.
"""
import unittest

from zope.i18n.interfaces import II18nAware
from zope.interface import implementer


@implementer(II18nAware)
class I18nAwareContentObject(object):

    def __init__(self):
        self.content = {}
        self.defaultLanguage = 'en'

    def getContent(self, language):
        return self.content[language]

    def queryContent(self, language, default=None):
        return self.content.get(language, default)

    def setContent(self, content, language):
        self.content[language] = content

    ############################################################
    # Implementation methods for interface
    # II18nAware.py

    def getDefaultLanguage(self):
        'See II18nAware'
        return self.defaultLanguage

    def setDefaultLanguage(self, language):
        'See II18nAware'
        self.defaultLanguage = language

    def getAvailableLanguages(self):
        'See II18nAware'
        return self.content.keys()

    #
    ############################################################

class AbstractTestII18nAwareMixin(object):

    def setUp(self):
        self.object = self._createObject()
        self.object.setDefaultLanguage('fr')

    def _createObject(self):
        # Should create an object that has lt, en and fr as available
        # languages
        raise NotImplementedError()

    def testGetDefaultLanguage(self):
        self.assertEqual(self.object.getDefaultLanguage(), 'fr')

    def testSetDefaultLanguage(self):
        self.object.setDefaultLanguage('lt')
        self.assertEqual(self.object.getDefaultLanguage(), 'lt')

    def testGetAvailableLanguages(self):
        self.assertEqual(sorted(self.object.getAvailableLanguages()), ['en', 'fr', 'lt'])


class TestI18nAwareObject(AbstractTestII18nAwareMixin, unittest.TestCase):

    def _createObject(self):
        object = I18nAwareContentObject()
        object.setContent('English', 'en')
        object.setContent('Lithuanian', 'lt')
        object.setContent('French', 'fr')
        return object

    def testSetContent(self):
        self.object.setContent('German', 'de')
        self.assertEqual(self.object.content['de'], 'German')

    def testGetContent(self):
        self.assertEqual(self.object.getContent('en'), 'English')
        with self.assertRaises(KeyError):
            self.object.getContent('es')

    def testQueryContent(self):
        self.assertEqual(self.object.queryContent('en'), 'English')
        self.assertEqual(self.object.queryContent('es', 'N/A'), 'N/A')
