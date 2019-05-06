##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ZCTextIndex export / import support unit tests.
"""

import unittest

from Acquisition import Implicit

from Products.GenericSetup.testing import NodeAdapterTestCase
from Products.GenericSetup.testing import ExportImportZCMLLayer

_PLEXICON_XML = b"""\
<object name="foo_plexicon" meta_type="ZCTextIndex Lexicon">
 <element name="Whitespace splitter" group="Word Splitter"/>
 <element name="Case Normalizer" group="Case Normalizer"/>
 <element name="Remove listed stop words only" group="Stop Words"/>
</object>
"""

_ZCTEXT_XML = b"""\
<index name="foo_zctext" meta_type="ZCTextIndex">
 <indexed_attr value="foo_zctext"/>
 <indexed_attr value="baz_zctext"/>
 <extra name="index_type" value="Okapi BM25 Rank"/>
 <extra name="lexicon_id" value="foo_plexicon"/>
</index>
"""


class _extra:

    pass


class DummyCatalog(Implicit):

    pass


class ZCLexiconNodeAdapterTests(NodeAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.ZCTextIndex.exportimport \
                import ZCLexiconNodeAdapter

        return ZCLexiconNodeAdapter

    def _populate(self, obj):
        from Products.ZCTextIndex.Lexicon import CaseNormalizer
        from Products.ZCTextIndex.Lexicon import Splitter
        from Products.ZCTextIndex.Lexicon import StopWordRemover
        obj._pipeline = (Splitter(), CaseNormalizer(), StopWordRemover())

    def setUp(self):
        from Products.ZCTextIndex.ZCTextIndex import PLexicon

        self._obj = PLexicon('foo_plexicon')
        self._XML = _PLEXICON_XML


class ZCTextIndexNodeAdapterTests(NodeAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.ZCTextIndex.exportimport \
                import ZCTextIndexNodeAdapter

        return ZCTextIndexNodeAdapter

    def _populate(self, obj):
        obj._indexed_attrs = ['foo_zctext', 'baz_zctext']

    def setUp(self):
        from Products.ZCTextIndex.ZCTextIndex import PLexicon
        from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex

        catalog = DummyCatalog()
        catalog.foo_plexicon = PLexicon('foo_plexicon')
        extra = _extra()
        extra.lexicon_id = 'foo_plexicon'
        extra.index_type = 'Okapi BM25 Rank'
        self._obj = ZCTextIndex('foo_zctext', extra=extra,
                                caller=catalog).__of__(catalog)
        self._XML = _ZCTEXT_XML


class UnchangedTests(unittest.TestCase):

    layer = ExportImportZCMLLayer

    def test_ZCLexicon(self):
        from xml.dom.minidom import parseString
        from Products.GenericSetup.testing import DummySetupEnviron
        from Products.ZCTextIndex.PipelineFactory import element_factory
        from Products.GenericSetup.ZCTextIndex.exportimport \
            import ZCLexiconNodeAdapter

        _XML = b"""\
        <object name="foo_plexicon" meta_type="ZCTextIndex Lexicon">
        <element name="foo" group="gs"/>
        <element name="bar" group="gs"/>
        </object>
        """
        environ = DummySetupEnviron()
        _before = object(), object(), object()

        class DummyLexicon(object):
            _wids, _words, length = _before

        lex = DummyLexicon()
        lex._pipeline = foo, bar = object(), object()
        adapted = ZCLexiconNodeAdapter(lex, environ)
        element_factory._groups['gs'] = {'foo': lambda: foo,
                                         'bar': lambda: bar}
        try:
            adapted.node = parseString(_XML).documentElement  # no raise
        finally:
            del element_factory._groups['gs']
        self.assertTrue(lex._wids is _before[0])
        self.assertTrue(lex._words is _before[1])
        self.assertTrue(lex.length is _before[2])

    def test_ZCTextIndex(self):
        from xml.dom.minidom import parseString
        from Products.ZCTextIndex.ZCTextIndex import PLexicon
        from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
        from Products.GenericSetup.testing import DummySetupEnviron
        from Products.GenericSetup.ZCTextIndex.exportimport \
            import ZCTextIndexNodeAdapter
        _XML = b"""\
        <index name="foo_zctext" meta_type="ZCTextIndex">
        <indexed_attr value="bar"/>
        <extra name="index_type" value="Okapi BM25 Rank"/>
        <extra name="lexicon_id" value="foo_plexicon"/>
        </index>
        """
        environ = DummySetupEnviron()

        def _no_clear(*a):
            raise AssertionError("Don't clear me!")

        catalog = DummyCatalog()
        catalog.foo_plexicon = PLexicon('foo_plexicon')
        extra = _extra()
        extra.lexicon_id = 'foo_plexicon'
        extra.index_type = 'Okapi BM25 Rank'
        index = ZCTextIndex('foo_field', extra=extra, field_name='bar',
                            caller=catalog).__of__(catalog)
        index.clear = _no_clear
        adapted = ZCTextIndexNodeAdapter(index, environ)
        adapted.node = parseString(_XML).documentElement  # no raise


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZCLexiconNodeAdapterTests),
        unittest.makeSuite(ZCTextIndexNodeAdapterTests),
        unittest.makeSuite(UnchangedTests),
    ))
