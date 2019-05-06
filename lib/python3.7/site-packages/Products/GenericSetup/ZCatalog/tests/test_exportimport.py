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
"""ZCatalog export / import support unit tests.
"""

import unittest
from Testing import ZopeTestCase
from zope.component import getMultiAdapter

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import DummySetupEnviron
from Products.GenericSetup.testing import ExportImportZCMLLayer

ZopeTestCase.installProduct('ZCTextIndex', 1)
ZopeTestCase.installProduct('PluginIndexes', 1)


class _extra:

    pass


_CATALOG_BODY = b"""\
<?xml version="1.0" encoding="utf-8"?>
<object name="foo_catalog" meta_type="ZCatalog">
 <property name="title"></property>
 <object name="foo_plexicon" meta_type="ZCTextIndex Lexicon">
  <element name="Whitespace splitter" group="Word Splitter"/>
  <element name="Case Normalizer" group="Case Normalizer"/>
  <element name="Remove listed stop words only" group="Stop Words"/>
 </object>
%s <index name="foo_date" meta_type="DateIndex">
  <property name="index_naive_time_as_local">True</property>
  <property name="precision">1</property>
 </index>
 <index name="foo_daterange" meta_type="DateRangeIndex" since_field="bar"
    until_field="baz"/>
 <index name="foo_field" meta_type="FieldIndex">
  <indexed_attr value="bar"/>
 </index>
 <index name="foo_keyword" meta_type="KeywordIndex">
  <indexed_attr value="bar"/>
 </index>
 <index name="foo_path" meta_type="PathIndex"/>
%s <index name="foo_topic" meta_type="TopicIndex">
  <filtered_set name="bar" meta_type="PythonFilteredSet" expression="True"/>
  <filtered_set name="baz" meta_type="PythonFilteredSet" expression="False"/>
 </index>
 <index name="foo_zctext" meta_type="ZCTextIndex">
  <indexed_attr value="foo_zctext"/>
  <extra name="index_type" value="Okapi BM25 Rank"/>
  <extra name="lexicon_id" value="foo_plexicon"/>
 </index>
%s <column value="eggs"/>
 <column value="spam"/>
</object>
"""

_CATALOG_UPDATE_BODY = b"""\
<?xml version="1.0" encoding="utf-8"?>
<object name="foo_catalog">
 <object name="old_plexicon" remove="True"/>
 <index name="foo_text" remove="True"/>
 <index name="foo_text" meta_type="ZCTextIndex">
  <indexed_attr value="foo_text"/>
  <extra name="index_type" value="Okapi BM25 Rank"/>
  <extra name="lexicon_id" value="foo_plexicon"/>
 </index>
 <index name="non_existing" remove="True"/>
 <column value="non_existing" remove="True"/>
 <column value="bacon" remove="True"/>
</object>
"""

# START SITUATION
#
# The catalog starts out as the _CATALOG_BODY above with the following
# xml snippets inserted.

_LEXICON_XML = b"""\
 <object name="old_plexicon" meta_type="ZCTextIndex Lexicon"/>
"""

_TEXT_XML = b"""\
 <index name="foo_text" meta_type="ZCTextIndex">
  <indexed_attr value="foo_text"/>
  <extra name="index_type" value="Cosine Measure"/>
  <extra name="lexicon_id" value="old_plexicon"/>
 </index>
"""

_COLUMN_XML = b"""\
 <column value="bacon"/>
"""

# END SITUATION
#
# The catalog ends as the _CATALOG_BODY above with the following
# xml snippets and some empty strings inserted.

_ZCTEXT_XML = b"""\
 <index name="foo_text" meta_type="ZCTextIndex">
  <indexed_attr value="foo_text"/>
  <extra name="index_type" value="Okapi BM25 Rank"/>
  <extra name="lexicon_id" value="foo_plexicon"/>
 </index>
"""


class ZCatalogXMLAdapterTests(BodyAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.ZCatalog.exportimport \
                import ZCatalogXMLAdapter

        return ZCatalogXMLAdapter

    def _populate(self, obj):
        from Products.ZCTextIndex.Lexicon import CaseNormalizer
        from Products.ZCTextIndex.Lexicon import Splitter
        from Products.ZCTextIndex.Lexicon import StopWordRemover
        from Products.ZCTextIndex.ZCTextIndex import PLexicon

        obj._setObject('foo_plexicon', PLexicon('foo_plexicon'))
        lex = obj.foo_plexicon
        lex._pipeline = (Splitter(), CaseNormalizer(), StopWordRemover())

        obj.addIndex('foo_date', 'DateIndex')

        obj.addIndex('foo_daterange', 'DateRangeIndex')
        idx = obj._catalog.getIndex('foo_daterange')
        idx._edit('bar', 'baz')

        obj.addIndex('foo_field', 'FieldIndex')
        idx = obj._catalog.getIndex('foo_field')
        idx.indexed_attrs = ('bar',)

        obj.addIndex('foo_keyword', 'KeywordIndex')
        idx = obj._catalog.getIndex('foo_keyword')
        idx.indexed_attrs = ('bar',)

        obj.addIndex('foo_path', 'PathIndex')

        obj.addIndex('foo_topic', 'TopicIndex')
        idx = obj._catalog.getIndex('foo_topic')
        idx.addFilteredSet('bar', 'PythonFilteredSet', 'True')
        idx.addFilteredSet('baz', 'PythonFilteredSet', 'False')

        extra = _extra()
        extra.lexicon_id = 'foo_plexicon'
        extra.index_type = 'Okapi BM25 Rank'
        obj.addIndex('foo_zctext', 'ZCTextIndex', extra)

        obj.addColumn('spam')
        obj.addColumn('eggs')

    def _populate_special(self, obj):
        from Products.ZCTextIndex.ZCTextIndex import PLexicon

        self._populate(self._obj)
        obj._setObject('old_plexicon', PLexicon('old_plexicon'))

        extra = _extra()
        extra.lexicon_id = 'old_plexicon'
        extra.index_type = 'Cosine Measure'
        obj.addIndex('foo_text', 'ZCTextIndex', extra)

        obj.addColumn('bacon')

    def setUp(self):
        from Products.ZCatalog.ZCatalog import ZCatalog

        self._obj = ZCatalog('foo_catalog')
        self._BODY = _CATALOG_BODY % (b'', b'', b'')

    def test_body_get_special(self):
        # Assert that the catalog starts out the way we expect it to.
        self._populate_special(self._obj)
        context = DummySetupEnviron()
        adapted = getMultiAdapter((self._obj, context), IBody)
        expected = _CATALOG_BODY % (_LEXICON_XML, _TEXT_XML, _COLUMN_XML)
        self.assertEqual(adapted.body, expected)

    def test_body_set_update(self):
        # Assert that the catalog ends up the way we expect it to.
        self._populate_special(self._obj)
        context = DummySetupEnviron()
        context._should_purge = False
        adapted = getMultiAdapter((self._obj, context), IBody)
        adapted.body = _CATALOG_UPDATE_BODY
        self.assertEqual(adapted.body, _CATALOG_BODY % (b'', _ZCTEXT_XML, b''))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZCatalogXMLAdapterTests),
        ))
