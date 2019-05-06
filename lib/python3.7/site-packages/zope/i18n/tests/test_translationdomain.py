##############################################################################
#
# Copyright (c) 2001-2008 Zope Foundation and Contributors.
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
"""This module tests the regular persistent Translation Domain.
"""
import unittest
import os
from zope.i18n.translationdomain import TranslationDomain
from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
from zope.i18n.tests.test_itranslationdomain import \
     TestITranslationDomain, Environment
from zope.i18nmessageid import MessageFactory
from zope.i18n.interfaces import ITranslationDomain

import zope.component

testdir = os.path.dirname(__file__)

en_file = os.path.join(testdir, 'en-default.mo')
de_file = os.path.join(testdir, 'de-default.mo')


class TestGlobalTranslationDomain(TestITranslationDomain, unittest.TestCase):

    def _getTranslationDomain(self):
        domain = TranslationDomain('default')
        en_catalog = GettextMessageCatalog('en', 'default',
                                           en_file)
        de_catalog = GettextMessageCatalog('de', 'default',
                                           de_file)
        domain.addCatalog(en_catalog)
        domain.addCatalog(de_catalog)
        return domain

    def testNoTargetLanguage(self):
        # Having a fallback would interfere with this test
        self._domain.setLanguageFallbacks([])
        TestITranslationDomain.testNoTargetLanguage(self)

    def testSimpleNoTranslate(self):
        translate = self._domain.translate
        eq = self.assertEqual
        # Unset fallback translation languages
        self._domain.setLanguageFallbacks([])

        # Test that a translation in an unsupported language returns the
        # default, if there is no fallback language
        eq(translate('short_greeting', target_language='es'), 'short_greeting')
        eq(translate('short_greeting', target_language='es',
                     default='short_greeting'), 'short_greeting')

        # Same test, but use the context argument instead of target_language
        context = Environment()
        eq(translate('short_greeting', context=context), 'short_greeting')
        eq(translate('short_greeting', context=context,
                     default='short_greeting'), 'short_greeting')

    def testEmptyStringTranslate(self):
        translate = self._domain.translate
        self.assertEqual(translate(u"", target_language='en'), u"")
        self.assertEqual(translate(u"", target_language='foo'), u"")

    def testStringTranslate(self):
        self.assertEqual(
            self._domain.translate(u"short_greeting", target_language='en'),
            u"Hello!")

    def testMessageIDTranslate(self):
        factory = MessageFactory('default')
        translate = self._domain.translate
        msgid = factory(u"short_greeting", 'default')
        self.assertEqual(translate(msgid, target_language='en'), u"Hello!")
        # MessageID attributes override arguments
        msgid = factory('43-not-there', 'this ${that} the other',
                        mapping={'that': 'THAT'})
        self.assertEqual(
            translate(msgid, target_language='en', default="default",
                      mapping={"that": "that"}), "this THAT the other")

    def testMessageIDRecursiveTranslate(self):
        factory = MessageFactory('default')
        translate = self._domain.translate
        msgid_sub1 = factory(u"44-not-there", '${blue}',
                             mapping={'blue': 'BLUE'})
        msgid_sub2 = factory(u"45-not-there", '${yellow}',
                             mapping={'yellow': 'YELLOW'})
        mapping = {'color1': msgid_sub1,
                   'color2': msgid_sub2}
        msgid = factory(u"46-not-there", 'Color: ${color1}/${color2}',
                        mapping=mapping)
        self.assertEqual(
            translate(msgid, target_language='en', default="default"),
            "Color: BLUE/YELLOW")
        # The recursive translation must not change the mappings
        self.assertEqual(msgid.mapping, {'color1': msgid_sub1,
                                         'color2': msgid_sub2})
        # A circular reference should not lead to crashes
        msgid1 = factory(u"47-not-there", 'Message 1 and $msg2',
                         mapping={})
        msgid2 = factory(u"48-not-there", 'Message 2 and $msg1',
                         mapping={})
        msgid1.mapping['msg2'] = msgid2
        msgid2.mapping['msg1'] = msgid1
        self.assertRaises(ValueError,
                          translate, msgid1, None, None, 'en', "default")
        # Recursive translations also work if the original message id wasn't a
        # message id but a Unicode with a directly passed mapping
        self.assertEqual(
            "Color: BLUE/YELLOW",
            translate(u"Color: ${color1}/${color2}", mapping=mapping,
                      target_language='en'))

        # If we have mapping with a message id from a different
        # domain, make sure we use that domain, not ours. If the
        # message domain is not registered yet, we should return a
        # default translation.
        alt_factory = MessageFactory('alt')
        msgid_sub = alt_factory(u"special", default=u"oohhh")
        mapping = {'message': msgid_sub}
        msgid = factory(u"46-not-there", 'Message: ${message}',
                        mapping=mapping)
        # test we get a default with no domain registered
        self.assertEqual(
            translate(msgid, target_language='en', default="default"),
            "Message: oohhh")
        # provide the domain
        domain = TranslationDomain('alt')
        path = testdir
        en_catalog = GettextMessageCatalog('en', 'alt',
                                           os.path.join(path, 'en-alt.mo'))
        domain.addCatalog(en_catalog)
        # test that we get the right translation
        zope.component.provideUtility(domain, ITranslationDomain, 'alt')
        self.assertEqual(
            translate(msgid, target_language='en', default="default"),
            "Message: Wow")

    def testMessageIDTranslateForDifferentDomain(self):
        domain = TranslationDomain('alt')
        path = testdir
        en_catalog = GettextMessageCatalog('en', 'alt',
                                           os.path.join(path, 'en-alt.mo'))
        domain.addCatalog(en_catalog)

        zope.component.provideUtility(domain, ITranslationDomain, 'alt')

        factory = MessageFactory('alt')
        msgid = factory(u"special", 'default')
        self.assertEqual(
            self._domain.translate(msgid, target_language='en'), u"Wow")

    def testSimpleFallbackTranslation(self):
        translate = self._domain.translate
        eq = self.assertEqual
        # Test that a translation in an unsupported language returns a
        # translation in the fallback language (by default, English)
        eq(translate('short_greeting', target_language='es'),
           u"Hello!")
        # Same test, but use the context argument instead of target_language
        context = Environment()
        eq(translate('short_greeting', context=context),
           u"Hello!")

    def testInterpolationWithoutTranslation(self):
        translate = self._domain.translate
        self.assertEqual(
            translate('42-not-there', target_language="en",
                      default="this ${that} the other",
                      mapping={"that": "THAT"}),
            "this THAT the other")

    def test_getCatalogInfos(self):
        cats = self._domain.getCatalogsInfo()
        self.assertEqual(
            cats,
            {'en': [en_file],
             'de': [de_file]})

    def test_releoadCatalogs(self):
        # It uses the keys we pass
        # so this does nothing
        self._domain.reloadCatalogs(())

        # The catalogNames, somewhat confusingly, are
        # the paths to the files.
        self._domain.reloadCatalogs((en_file, de_file))

        with self.assertRaises(KeyError):
            self._domain.reloadCatalogs(('dne',))
