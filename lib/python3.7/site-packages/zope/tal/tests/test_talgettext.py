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
"""Tests for the talgettext utility.
"""

from __future__ import print_function

import tempfile
import unittest
import warnings

try:
    # Python 2.x
    from StringIO import StringIO
except ImportError:
    # Python 3.x
    from io import StringIO

from zope.tal.htmltalparser import HTMLTALParser
from zope.tal.talgettext import POTALInterpreter
from zope.tal.talgettext import POEngine

class test_POEngine(unittest.TestCase):
    """Test the PO engine functionality, which simply adds items to a catalog
    as .translate is called
    """

    def test_translate(self):
        test_keys = ['foo', 'bar', 'blarf', 'washington']

        engine = POEngine()
        engine.file = 'foo.pt'
        for key in test_keys:
            engine.translate(key, 'domain')

        for key in test_keys:
            self.assertIn(
                key, engine.catalog['domain'],
                "POEngine catalog does not properly store message ids"
            )

    def test_translate_existing(self):
        engine = POEngine()
        # This tries to reproduce a big surfacing in a template of
        # PloneSoftwareCenter when using the i18ndude package to
        # extract translatable strings, which uses zope.tal.  The
        # relevant html snippet is this:
        #
        # <a href="#" title="Read more&hellip;"
        #    i18n:attributes="title label_read_more"
        #    tal:attributes="href release/absolute_url">
        #    <span i18n:translate="label_read_more">Read more&hellip;</span>
        # </a>
        #
        # Due to the different ways that i18n:attributes and
        # i18n:translate are handled, the attribute gets passed to the
        # translate method with the html entity interpreted as a
        # unicode, and the i18n:translate gets passed as a simple
        # string with the html entity intact.  That may need a fix
        # elsewhere, but at the moment it gives a warning.  The very
        # least we can do is make sure that this does not give a
        # UnicodeDecodeError, which is what we test here.
        engine.file = 'psc_release_listing.pt'
        # position is position in file.
        engine.translate('foo', 'domain',
                         default=u'Read more\u2026', position=7)
        # Adding the same key with the same default is fine.
        engine.translate('foo', 'domain',
                         default=u'Read more\u2026', position=13)
        # Adding the same key with a different default is bad and
        # triggers a warning.
        with warnings.catch_warnings(record=True) as log:
            warnings.simplefilter("always")
            engine.translate('foo', 'domain',
                             default='Read still more&hellip;', position=42)
            self.assertEqual(len(log), 1)
            message = log[0].message
            with tempfile.TemporaryFile('w+') as printfile:
                print(message, file=printfile)
                printfile.seek(0)
                self.assertTrue("already exists with a different default"
                                in printfile.read())

    def test_dynamic_msgids(self):
        sample_source = """
            <p i18n:translate="">
              Some
              <span tal:replace="string:strange">dynamic</span>
              text.
            </p>
            <p i18n:translate="">
              A <a tal:attributes="href path:dynamic">link</a>.
            </p>
        """
        p = HTMLTALParser()
        p.parseString(sample_source)
        program, macros = p.getCode()
        engine = POEngine()
        engine.file = 'sample_source'
        POTALInterpreter(program, macros, engine, stream=StringIO(),
                         metal=False)()
        msgids = []
        for domain in engine.catalog.values():
            msgids += list(domain)
        msgids.sort()
        self.assertEqual(msgids,
                         ['A <a href="${DYNAMIC_CONTENT}">link</a>.',
                          'Some ${DYNAMIC_CONTENT} text.'])

    def test_potalinterpreter_translate_default(self):
        sample_source = '<p i18n:translate="">text</p>'
        p = HTMLTALParser()
        p.parseString(sample_source)
        program, macros = p.getCode()
        engine = POEngine()
        engine.file = 'sample_source'
        interpreter = POTALInterpreter(
            program, macros, engine, stream=StringIO(), metal=False)
        # We simply call this, to make sure we don't get a NameError
        # for 'unicode' in python 3.
        # The return value (strangely: 'x') is not interesting here.
        interpreter.translate('text')
        msgids = []
        for domain in engine.catalog.values():
            msgids += list(domain)
        self.assertIn('text', msgids)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
