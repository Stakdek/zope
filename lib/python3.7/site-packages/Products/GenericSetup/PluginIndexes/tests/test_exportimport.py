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
"""PluginIndexes export / import support unit tests.
"""

import unittest

from Products.GenericSetup.testing import NodeAdapterTestCase
from Products.GenericSetup.testing import ExportImportZCMLLayer

_DATE_XML = b"""\
<index name="foo_date" meta_type="DateIndex">
 <property name="index_naive_time_as_local">True</property>
 <property name="precision">0</property>
</index>
"""

_DATERANGE_XML = b"""\
<index name="foo_daterange" meta_type="DateRangeIndex" since_field="bar"
   until_field="baz"/>
"""

_FIELD_XML = b"""\
<index name="foo_field" meta_type="FieldIndex">
 <indexed_attr value="bar"/>
</index>
"""

_KEYWORD_XML = b"""\
<index name="foo_keyword" meta_type="KeywordIndex">
 <indexed_attr value="bar"/>
</index>
"""

_ODDBALL_XML = b"""\
<index name="foo_keyword" meta_type="OddballIndex">
</index>
"""

_PATH_XML = b"""\
<index name="foo_path" meta_type="PathIndex"/>
"""

_SET_XML = b"""\
<filtered_set name="bar" meta_type="PythonFilteredSet" expression="True"/>
"""

_TOPIC_XML = b"""\
<index name="foo_topic" meta_type="TopicIndex">
 <filtered_set name="bar" meta_type="PythonFilteredSet" expression="True"/>
 <filtered_set name="baz" meta_type="PythonFilteredSet" expression="False"/>
</index>
"""


class DateIndexNodeAdapterTests(NodeAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.PluginIndexes.exportimport \
                import DateIndexNodeAdapter
        return DateIndexNodeAdapter

    def setUp(self):
        from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
        self._obj = DateIndex('foo_date')
        self._obj._setPropValue('precision', 0)
        self._XML = _DATE_XML

    def _verifyImport(self, obj):
        self.assertEqual(obj.id, 'foo_date')


class DateRangeIndexNodeAdapterTests(NodeAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.PluginIndexes.exportimport \
                import DateRangeIndexNodeAdapter
        return DateRangeIndexNodeAdapter

    def _populate(self, obj):
        obj._edit('bar', 'baz')

    def setUp(self):
        from Products.PluginIndexes.DateRangeIndex.DateRangeIndex \
                import DateRangeIndex
        self._obj = DateRangeIndex('foo_daterange')
        self._XML = _DATERANGE_XML

    def _verifyImport(self, obj):
        self.assertEqual(obj.id, 'foo_daterange')
        self.assertEqual(obj._since_field, 'bar')
        self.assertEqual(obj._until_field, 'baz')


class FieldIndexNodeAdapterTests(NodeAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.PluginIndexes.exportimport \
                import PluggableIndexNodeAdapter
        return PluggableIndexNodeAdapter

    def _populate(self, obj):
        obj.indexed_attrs = ('bar',)

    def setUp(self):
        from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
        self._obj = FieldIndex('foo_field')
        self._XML = _FIELD_XML

    def _verifyImport(self, obj):
        self.assertEqual(obj.id, 'foo_field')
        self.assertEqual(obj.indexed_attrs, ['bar'])


class KeywordIndexNodeAdapterTests(NodeAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.PluginIndexes.exportimport \
                import PluggableIndexNodeAdapter
        return PluggableIndexNodeAdapter

    def _populate(self, obj):
        obj.indexed_attrs = ('bar',)

    def setUp(self):
        from Products.PluginIndexes.KeywordIndex.KeywordIndex \
                import KeywordIndex
        self._obj = KeywordIndex('foo_keyword')
        self._XML = _KEYWORD_XML

    def _verifyImport(self, obj):
        self.assertEqual(obj.id, 'foo_keyword')
        self.assertEqual(obj.indexed_attrs, ['bar'])


class PathIndexNodeAdapterTests(NodeAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.PluginIndexes.exportimport \
                import PathIndexNodeAdapter
        return PathIndexNodeAdapter

    def setUp(self):
        from Products.PluginIndexes.PathIndex.PathIndex import PathIndex
        self._obj = PathIndex('foo_path')
        self._XML = _PATH_XML

    def _verifyImport(self, obj):
        self.assertEqual(obj.id, 'foo_path')


class FilteredSetNodeAdapterTests(NodeAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.PluginIndexes.exportimport \
                import FilteredSetNodeAdapter
        return FilteredSetNodeAdapter

    def _populate(self, obj):
        obj.setExpression('True')

    def setUp(self):
        from Products.PluginIndexes.TopicIndex.FilteredSet \
                import PythonFilteredSet
        self._obj = PythonFilteredSet('bar', '')
        self._XML = _SET_XML

    def _verifyImport(self, obj):
        self.assertEqual(obj.id, 'bar')
        self.assertEqual(obj.getExpression(), 'True')


class TopicIndexNodeAdapterTests(NodeAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.PluginIndexes.exportimport \
                import TopicIndexNodeAdapter
        return TopicIndexNodeAdapter

    def _populate(self, obj):
        obj.addFilteredSet('bar', 'PythonFilteredSet', 'True')
        obj.addFilteredSet('baz', 'PythonFilteredSet', 'False')

    def setUp(self):
        from Products.PluginIndexes.TopicIndex.TopicIndex import TopicIndex
        self._obj = TopicIndex('foo_topic')
        self._XML = _TOPIC_XML

    def _verifyImport(self, obj):
        self.assertEqual(obj.id, 'foo_topic')
        self.assertEqual(len(obj.filteredSets), 2)


class UnchangedTests(unittest.TestCase):

    layer = ExportImportZCMLLayer

    def test_FieldIndex(self):
        from xml.dom.minidom import parseString
        from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
        from Products.GenericSetup.testing import DummySetupEnviron
        from Products.GenericSetup.PluginIndexes.exportimport \
            import PluggableIndexNodeAdapter
        environ = DummySetupEnviron()

        def _no_clear(*a):
            raise AssertionError("Don't clear me!")

        index = FieldIndex('foo_field')
        index.indexed_attrs = ['bar']
        index.clear = _no_clear
        adapted = PluggableIndexNodeAdapter(index, environ)
        adapted.node = parseString(_FIELD_XML).documentElement  # no raise

    def test_KeywordIndex(self):
        from xml.dom.minidom import parseString
        from Products.PluginIndexes.KeywordIndex.KeywordIndex \
            import KeywordIndex
        from Products.GenericSetup.testing import DummySetupEnviron
        from Products.GenericSetup.PluginIndexes.exportimport \
            import PluggableIndexNodeAdapter
        environ = DummySetupEnviron()

        def _no_clear(*a):
            raise AssertionError("Don't clear me!")

        index = KeywordIndex('foo_keyword')
        index.indexed_attrs = ['bar']
        index.clear = _no_clear
        adapted = PluggableIndexNodeAdapter(index, environ)
        adapted.node = parseString(_KEYWORD_XML).documentElement  # no raise

    def test_OddballIndex(self):
        # Some indexes, e.g. Plone's 'GopipIndex', use ths adapter but don't
        # have 'indexed_attrs'.
        from xml.dom.minidom import parseString
        from Products.GenericSetup.testing import DummySetupEnviron
        from Products.GenericSetup.PluginIndexes.exportimport \
            import PluggableIndexNodeAdapter

        class Oddball(object):
            def clear(*a):
                raise AssertionError("Don't clear me!")

        index = Oddball()
        environ = DummySetupEnviron()
        adapted = PluggableIndexNodeAdapter(index, environ)
        adapted.node = parseString(_ODDBALL_XML).documentElement  # no raise

    def test_DateIndex(self):
        from xml.dom.minidom import parseString
        from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
        from Products.GenericSetup.testing import DummySetupEnviron
        from Products.GenericSetup.PluginIndexes.exportimport \
            import DateIndexNodeAdapter
        environ = DummySetupEnviron()

        def _no_clear(*a):
            raise AssertionError("Don't clear me!")

        index = DateIndex('foo_date')
        index._setPropValue('index_naive_time_as_local', True)
        index._setPropValue('precision', 0)
        index.clear = _no_clear
        adapted = DateIndexNodeAdapter(index, environ)
        adapted.node = parseString(_DATE_XML).documentElement  # no raise

    def test_DateRangeIndex(self):
        from xml.dom.minidom import parseString
        from Products.PluginIndexes.DateRangeIndex.DateRangeIndex \
            import DateRangeIndex
        from Products.GenericSetup.testing import DummySetupEnviron
        from Products.GenericSetup.PluginIndexes.exportimport \
            import DateRangeIndexNodeAdapter
        environ = DummySetupEnviron()

        def _no_clear(*a):
            raise AssertionError("Don't clear me!")

        index = DateRangeIndex('foo_daterange')
        index._since_field = 'bar'
        index._until_field = 'baz'
        index.clear = _no_clear
        adapted = DateRangeIndexNodeAdapter(index, environ)
        adapted.node = parseString(_DATERANGE_XML).documentElement  # no raise

    def test_FilteredSet(self):
        from xml.dom.minidom import parseString
        from Products.PluginIndexes.TopicIndex.FilteredSet \
            import PythonFilteredSet
        from Products.GenericSetup.testing import DummySetupEnviron
        from Products.GenericSetup.PluginIndexes.exportimport \
            import FilteredSetNodeAdapter
        environ = DummySetupEnviron()

        def _no_clear(*a):
            raise AssertionError("Don't clear me!")

        index = PythonFilteredSet('bar', 'True')
        index.clear = _no_clear
        adapted = FilteredSetNodeAdapter(index, environ)
        adapted.node = parseString(_SET_XML).documentElement  # no raise

    def test_TopicIndex(self):
        from xml.dom.minidom import parseString
        from Products.PluginIndexes.TopicIndex.TopicIndex import TopicIndex
        from Products.GenericSetup.testing import DummySetupEnviron
        from Products.GenericSetup.PluginIndexes.exportimport \
            import TopicIndexNodeAdapter
        environ = DummySetupEnviron()

        def _no_clear(*a):
            raise AssertionError("Don't clear me!")

        index = TopicIndex('topics')
        index.addFilteredSet('bar', 'PythonFilteredSet', 'True')
        index.addFilteredSet('baz', 'PythonFilteredSet', 'False')
        bar = index.filteredSets['bar']
        baz = index.filteredSets['baz']
        bar.clear = baz.clear = _no_clear
        adapted = TopicIndexNodeAdapter(index, environ)
        adapted.node = parseString(_SET_XML).documentElement  # no raise


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DateIndexNodeAdapterTests),
        unittest.makeSuite(DateRangeIndexNodeAdapterTests),
        unittest.makeSuite(FieldIndexNodeAdapterTests),
        unittest.makeSuite(KeywordIndexNodeAdapterTests),
        unittest.makeSuite(PathIndexNodeAdapterTests),
        unittest.makeSuite(FilteredSetNodeAdapterTests),
        unittest.makeSuite(TopicIndexNodeAdapterTests),
        unittest.makeSuite(UnchangedTests),
        ))
