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
"""Test the gts ZCML namespace directives.
"""
import doctest
import os
import shutil
import stat
import unittest

from zope.component import getUtility
from zope.component import queryUtility
from zope.component.testing import PlacelessSetup
from zope.configuration import xmlconfig

import zope.i18n.tests
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n import config

text_type = str if bytes is not str else unicode

template = """\
<configure
    xmlns='http://namespaces.zope.org/zope'
    xmlns:i18n='http://namespaces.zope.org/i18n'>
  %s
</configure>"""

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    # This test suite needs the [zcml] and [compile] extra dependencies

    def setUp(self):
        super(DirectivesTest, self).setUp()
        self.context = xmlconfig.file('meta.zcml', zope.i18n)
        self.allowed = config.ALLOWED_LANGUAGES
        config.ALLOWED_LANGUAGES = None

    def tearDown(self):
        super(DirectivesTest, self).tearDown()
        config.ALLOWED_LANGUAGES = self.allowed

    def testRegisterTranslations(self):
        self.assertTrue(queryUtility(ITranslationDomain) is None)
        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations directory="locale" />
            </configure>
            ''', self.context)
        path = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                            'locale', 'en', 'LC_MESSAGES', 'zope-i18n.mo')
        util = getUtility(ITranslationDomain, 'zope-i18n')
        self.assertEqual(util._catalogs.get('test'), ['test'])
        self.assertEqual(util._catalogs.get('en'), [text_type(path)])

    def testAllowedTranslations(self):
        self.assertTrue(queryUtility(ITranslationDomain) is None)
        config.ALLOWED_LANGUAGES = ('de', 'fr')
        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations directory="locale" />
            </configure>
            ''', self.context)
        path = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                            'locale', 'de', 'LC_MESSAGES', 'zope-i18n.mo')
        util = getUtility(ITranslationDomain, 'zope-i18n')
        self.assertEqual(util._catalogs,
                         {'test': ['test'], 'de': [text_type(path)]})

    def testRegisterDistributedTranslations(self):
        self.assertTrue(queryUtility(ITranslationDomain, 'zope-i18n') is None)
        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations directory="locale" />
            </configure>
            ''', self.context)
        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations directory="locale2" />
            </configure>
            ''', self.context)
        path1 = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                             'locale', 'en', 'LC_MESSAGES', 'zope-i18n.mo')
        path2 = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                             'locale2', 'en', 'LC_MESSAGES', 'zope-i18n.mo')
        util = getUtility(ITranslationDomain, 'zope-i18n')
        self.assertEqual(util._catalogs.get('test'), ['test', 'test'])
        self.assertEqual(util._catalogs.get('en'),
                         [text_type(path1), text_type(path2)])

        msg = util.translate(u"Additional message", target_language='en')
        self.assertEqual(msg, u"Additional message translated")

        msg = util.translate(u"New Domain", target_language='en')
        self.assertEqual(msg, u"New Domain translated")

        msg = util.translate(u"New Language", target_language='en')
        self.assertEqual(msg, u"New Language translated")

    def testRegisterAndCompileTranslations(self):
        config.COMPILE_MO_FILES = True
        self.assertTrue(queryUtility(ITranslationDomain) is None)

        # Copy an old and outdated file over, so we can test if the
        # newer file check works
        testpath = os.path.join(os.path.dirname(zope.i18n.tests.__file__))
        basepath = os.path.join(testpath, 'locale3', 'en', 'LC_MESSAGES')
        in_ = os.path.join(basepath, 'zope-i18n.in')
        path = os.path.join(basepath, 'zope-i18n.mo')
        shutil.copy2(in_, path)

        # Make sure the older mo file always has an older time stamp
        # than the po file
        path_atime = os.stat(path)[stat.ST_ATIME]
        path_mtime = os.stat(path)[stat.ST_MTIME]
        os.utime(path, (path_atime, path_mtime - 6000))

        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations directory="locale3" />
            </configure>
            ''', self.context)
        util = getUtility(ITranslationDomain, 'zope-i18n')
        self.assertEqual(util._catalogs,
                         {'test': ['test'], 'en': [text_type(path)]})

        msg = util.translate(u"I'm a newer file", target_language='en')
        self.assertEqual(msg, u"I'm a newer file translated")

        util = getUtility(ITranslationDomain, 'zope-i18n2')
        msg = util.translate(u"I'm a new file", target_language='en')
        self.assertEqual(msg, u"I'm a new file translated")

        # Reset the mtime of the mo file
        os.utime(path, (path_atime, path_mtime))

    def testRegisterTranslationsForDomain(self):
        self.assertTrue(queryUtility(ITranslationDomain, 'zope-i18n') is None)
        self.assertTrue(queryUtility(ITranslationDomain, 'zope-i18n2') is None)
        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations directory="locale3" domain="zope-i18n" />
            </configure>
            ''', self.context)
        path = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                            'locale3', 'en', 'LC_MESSAGES', 'zope-i18n.mo')
        util = getUtility(ITranslationDomain, 'zope-i18n')
        self.assertEqual(util._catalogs,
                         {'test': ['test'], 'en': [text_type(path)]})

        self.assertTrue(queryUtility(ITranslationDomain, 'zope-i18n2') is None)


def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocFileSuite('configure.txt'),
    ))
