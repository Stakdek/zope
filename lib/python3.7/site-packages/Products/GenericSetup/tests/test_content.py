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
"""Filesystem exporter / importer adapter unit tests.
"""

import unittest

from .conformance import ConformsToIINIAware
from .conformance import ConformsToIFilesystemExporter
from .conformance import ConformsToIFilesystemImporter


class SimpleINIAwareTests(unittest.TestCase, ConformsToIINIAware):

    def _getTargetClass(self):
        from Products.GenericSetup.content import SimpleINIAware
        return SimpleINIAware

    def test_as_ini_no_properties(self):
        context = _makePropertied('no_properties')
        context._properties = ()
        adapter = self._getTargetClass()(context)
        text = adapter.as_ini()
        parser = _parseINI(text)
        self.assertFalse(parser.sections())
        default_options = parser.defaults()
        self.assertEqual(len(default_options), 0)

    def test_as_ini_string_property(self):
        TITLE = 'String Property'
        DESCR = 'Another property'
        context = _makePropertied('string_property')
        context.title = TITLE
        context._setProperty('description', DESCR)
        adapter = self._getTargetClass()(context)
        text = adapter.as_ini()
        parser = _parseINI(text)
        self.assertFalse(parser.sections())
        default_options = parser.defaults()
        self.assertEqual(len(default_options), 2)
        self.assertEqual(default_options['title'].strip(), TITLE)
        self.assertEqual(default_options['description'].strip(), DESCR)

    def test_as_ini_other_properties(self):
        from DateTime.DateTime import DateTime
        INTPROP = 42
        FLOATPROP = 3.1415926
        DATESTR = '2005-11-07T12:00:00.000Z'
        context = _makePropertied('string_property')
        context._properties = ()
        context._setProperty('int_prop', INTPROP, 'int')
        context._setProperty('float_prop', FLOATPROP, 'float')
        context._setProperty('date_prop', DateTime(DATESTR), 'date')
        adapter = self._getTargetClass()(context)
        text = adapter.as_ini()
        parser = _parseINI(text)
        self.assertFalse(parser.sections())
        default_options = parser.defaults()
        self.assertEqual(len(default_options), 3)
        self.assertEqual(default_options['int_prop'], str(INTPROP))
        self.assertEqual(default_options['float_prop'], str(FLOATPROP))
        self.assertEqual(default_options['date_prop'], str(DateTime(DATESTR)))

    def test_put_ini_empty(self):
        context = _makePropertied('empty_ini')
        adapter = self._getTargetClass()(context)
        context._properties = ()
        self.assertFalse(context.propertyItems())
        adapter.put_ini('')
        self.assertFalse(context.propertyItems())

    def test_put_ini_with_values_stripped(self):
        context = _makePropertied('empty_ini')
        adapter = self._getTargetClass()(context)
        adapter.put_ini('[DEFAULT]\ntitle = Foo \ndescription = bar ')
        props = context.propdict()
        self.assertEqual(len(props), 2)
        self.assertTrue('title' in props)
        self.assertTrue('description' in props)
        self.assertEqual(context.title, 'Foo')
        self.assertEqual(context.description, 'bar')

    def test_put_ini_other_properties(self):
        from DateTime.DateTime import DateTime
        INTPROP = 42
        FLOATPROP = 3.1415926
        DATESTR = '2005-11-07T12:00:00.000Z'
        DATESTR2 = '2005-11-09T12:00:00.000Z'
        context = _makePropertied('string_property')
        context._properties = ()
        context._setProperty('int_prop', INTPROP, 'int')
        context._setProperty('float_prop', FLOATPROP, 'float')
        context._setProperty('date_prop', DateTime(DATESTR), 'date')
        adapter = self._getTargetClass()(context)
        adapter.put_ini('''\
[DEFAULT]
int_prop = 13
\nfloat_prop = 2.818
\ndate_prop = %s''' % DATESTR2)
        self.assertEqual(len(context.propertyIds()), 3)
        self.assertEqual(context.int_prop, 13)
        self.assertEqual(context.float_prop, 2.818)
        self.assertEqual(context.date_prop, DateTime(DATESTR2))


class FolderishExporterImporterTests(unittest.TestCase):

    def setUp(self):
        from zope.component.testing import setUp
        setUp()

    def tearDown(self):
        from zope.component.testing import tearDown
        tearDown()

    def _getExporter(self):
        from Products.GenericSetup.content import exportSiteStructure
        return exportSiteStructure

    def _getImporter(self):
        from Products.GenericSetup.content import importSiteStructure
        return importSiteStructure

    def _makeSetupTool(self):
        from Products.GenericSetup.tool import SetupTool
        return SetupTool('portal_setup')

    def _setUpAdapters(self):
        from zope.component import getSiteManager

        from OFS.interfaces import IObjectManager
        from OFS.interfaces import IPropertyManager

        from Products.GenericSetup.interfaces import IFilesystemExporter
        from Products.GenericSetup.interfaces import IFilesystemImporter
        from Products.GenericSetup.interfaces import ICSVAware
        from Products.GenericSetup.interfaces import IINIAware
        from Products.GenericSetup.interfaces import IDAVAware

        from Products.GenericSetup.content import \
            SimpleINIAware
        from Products.GenericSetup.content import \
            FolderishExporterImporter
        from Products.GenericSetup.content import \
            CSVAwareFileAdapter
        from Products.GenericSetup.content import \
            INIAwareFileAdapter
        from Products.GenericSetup.content import \
            DAVAwareFileAdapter

        sm = getSiteManager()

        sm.registerAdapter(FolderishExporterImporter,
                           (IObjectManager,),
                           IFilesystemExporter,
                           )

        sm.registerAdapter(FolderishExporterImporter,
                           (IObjectManager,),
                           IFilesystemImporter,
                           )

        sm.registerAdapter(SimpleINIAware,
                           (IPropertyManager,),
                           IINIAware,
                           )

        sm.registerAdapter(CSVAwareFileAdapter,
                           (ICSVAware,),
                           IFilesystemExporter,
                           )

        sm.registerAdapter(CSVAwareFileAdapter,
                           (ICSVAware,),
                           IFilesystemImporter,
                           )

        sm.registerAdapter(INIAwareFileAdapter,
                           (IINIAware,),
                           IFilesystemExporter,
                           )

        sm.registerAdapter(INIAwareFileAdapter,
                           (IINIAware,),
                           IFilesystemImporter,
                           )

        sm.registerAdapter(DAVAwareFileAdapter,
                           (IDAVAware,),
                           IFilesystemExporter,
                           )

        sm.registerAdapter(DAVAwareFileAdapter,
                           (IDAVAware,),
                           IFilesystemImporter,
                           )

    def test_export_empty_site(self):
        from Products.GenericSetup.tests.common import DummyExportContext
        self._setUpAdapters()
        site = _makeFolder('site')
        site.title = 'test_export_empty_site'
        site.description = 'Testing export of an empty site.'
        context = DummyExportContext(site)
        exporter = self._getExporter()
        exporter(context)

        self.assertEqual(len(context._wrote), 2)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'structure/.objects')
        self.assertEqual(content_type, 'text/comma-separated-values')

        objects = _parseCSV(text)
        self.assertEqual(len(objects), 0)

        filename, text, content_type = context._wrote[1]
        self.assertEqual(filename, 'structure/.properties')
        self.assertEqual(content_type, 'text/plain')

        parser = _parseINI(text)

        defaults = parser.defaults()
        self.assertEqual(len(defaults), 1)
        self.assertEqual(defaults['title'], site.title)

    def test_export_empty_site_with_setup_tool(self):
        from Products.GenericSetup.tests.common import DummyExportContext
        self._setUpAdapters()
        site = _makeFolder('site')
        site._setObject('setup_tool', self._makeSetupTool())
        site._updateProperty('title', 'test_export_empty_site_with_setup_tool')
        site._setProperty('description',
                          'Testing export of an empty site with setup tool.')
        context = DummyExportContext(site)
        exporter = self._getExporter()
        exporter(context)

        self.assertEqual(len(context._wrote), 2)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'structure/.objects')
        self.assertEqual(content_type, 'text/comma-separated-values')

        objects = _parseCSV(text)
        self.assertEqual(len(objects), 0)

        filename, text, content_type = context._wrote[1]
        self.assertEqual(filename, 'structure/.properties')
        self.assertEqual(content_type, 'text/plain')

        parser = _parseINI(text)

        defaults = parser.defaults()
        self.assertEqual(len(defaults), 2)
        self.assertEqual(defaults['title'], site.title)
        self.assertEqual(defaults['description'], site.description)

    def test_export_site_with_non_exportable_simple_items(self):
        from Products.GenericSetup.tests.common import DummyExportContext
        from Products.GenericSetup.utils import _getDottedName
        self._setUpAdapters()
        ITEM_IDS = ('foo', 'bar', 'baz')

        site = _makeFolder('site')
        site.title = 'AAA'
        site._setProperty('description', 'CCC')
        item = _makeItem('aside')
        dotted = _getDottedName(item.__class__)
        for id in ITEM_IDS:
            site._setObject(id, _makeItem(id))

        context = DummyExportContext(site)
        exporter = self._getExporter()
        exporter(context)

        self.assertEqual(len(context._wrote), 2)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'structure/.objects')
        self.assertEqual(content_type, 'text/comma-separated-values')

        objects = _parseCSV(text)
        self.assertEqual(len(objects), 3)
        for index in range(len(ITEM_IDS)):
            self.assertEqual(objects[index][0], ITEM_IDS[index])
            self.assertEqual(objects[index][1], dotted)

        filename, text, content_type = context._wrote[1]
        self.assertEqual(filename, 'structure/.properties')
        self.assertEqual(content_type, 'text/plain')
        parser = _parseINI(text)

        defaults = parser.defaults()
        self.assertEqual(len(defaults), 2)
        self.assertEqual(defaults['title'], 'AAA')
        self.assertEqual(defaults['description'], 'CCC')

    def test_export_site_with_exportable_simple_items(self):
        from Products.GenericSetup.tests.common import DummyExportContext
        from Products.GenericSetup.utils import _getDottedName
        self._setUpAdapters()
        ITEM_IDS = ('foo', 'bar', 'baz')

        site = _makeFolder('site')
        site.title = 'AAA'
        site._setProperty('description', 'CCC')
        aware = _makeINIAware('aside')
        dotted = _getDottedName(aware.__class__)
        for id in ITEM_IDS:
            site._setObject(id, _makeINIAware(id))

        context = DummyExportContext(site)
        exporter = self._getExporter()
        exporter(context)

        self.assertEqual(len(context._wrote), 2 + len(ITEM_IDS))
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'structure/.objects')
        self.assertEqual(content_type, 'text/comma-separated-values')

        objects = _parseCSV(text)
        self.assertEqual(len(objects), 3)
        for index in range(len(ITEM_IDS)):
            self.assertEqual(objects[index][0], ITEM_IDS[index])
            self.assertEqual(objects[index][1], dotted)

            filename, text, content_type = context._wrote[index + 2]
            self.assertEqual(filename, 'structure/%s.ini' % ITEM_IDS[index])
            object = site._getOb(ITEM_IDS[index])
            self.assertEqual(text.strip(),
                             object.as_ini().strip())
            self.assertEqual(content_type, 'text/plain')

        filename, text, content_type = context._wrote[1]
        self.assertEqual(filename, 'structure/.properties')
        self.assertEqual(content_type, 'text/plain')
        parser = _parseINI(text)

        defaults = parser.defaults()
        self.assertEqual(len(defaults), 2)
        self.assertEqual(defaults['title'], 'AAA')
        self.assertEqual(defaults['description'], 'CCC')

    def test_export_site_with_subfolders(self):
        from Products.GenericSetup.tests.common import DummyExportContext
        from Products.GenericSetup.utils import _getDottedName
        self._setUpAdapters()
        FOLDER_IDS = ('foo', 'bar', 'baz')

        site = _makeFolder('site')
        site.title = 'AAA'
        site._setProperty('description', 'CCC')
        aside = _makeFolder('aside')
        dotted = _getDottedName(aside.__class__)
        for id in FOLDER_IDS:
            folder = _makeFolder(id)
            folder.title = 'Title: %s' % id
            site._setObject(id, folder)

        context = DummyExportContext(site)
        exporter = self._getExporter()
        exporter(context)

        self.assertEqual(len(context._wrote), 2 + (2 * len(FOLDER_IDS)))
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'structure/.objects')
        self.assertEqual(content_type, 'text/comma-separated-values')

        objects = _parseCSV(text)
        self.assertEqual(len(objects), 3)

        for index in range(len(FOLDER_IDS)):
            id = FOLDER_IDS[index]
            self.assertEqual(objects[index][0], id)
            self.assertEqual(objects[index][1], dotted)

            filename, text, content_type = context._wrote[2 + (2 * index)]
            self.assertEqual(filename, '/'.join(('structure', id, '.objects')))
            self.assertEqual(content_type, 'text/comma-separated-values')
            subobjects = _parseCSV(text)
            self.assertEqual(len(subobjects), 0)

            filename, text, content_type = context._wrote[2 + (2 * index) + 1]
            self.assertEqual(filename,
                             '/'.join(('structure', id, '.properties')))
            self.assertEqual(content_type, 'text/plain')
            parser = _parseINI(text)

            defaults = parser.defaults()
            self.assertEqual(len(defaults), 1)
            self.assertEqual(defaults['title'], 'Title: %s' % id)

        filename, text, content_type = context._wrote[1]
        self.assertEqual(filename, 'structure/.properties')
        self.assertEqual(content_type, 'text/plain')

        parser = _parseINI(text)

        defaults = parser.defaults()
        self.assertEqual(len(defaults), 2)
        self.assertEqual(defaults['title'], 'AAA')
        self.assertEqual(defaults['description'], 'CCC')

    def test_export_site_with_csvaware(self):
        from Products.GenericSetup.tests.common import DummyExportContext
        from Products.GenericSetup.utils import _getDottedName
        self._setUpAdapters()

        site = _makeFolder('site')
        site.title = 'test_export_site_with_csvaware'
        site._setProperty('description',
                          'Testing export of an site with CSV-aware content.')

        aware = _makeCSVAware('aware')
        site._setObject('aware', aware)

        context = DummyExportContext(site)
        exporter = self._getExporter()
        exporter(context)

        self.assertEqual(len(context._wrote), 3)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'structure/.objects')
        self.assertEqual(content_type, 'text/comma-separated-values')

        objects = _parseCSV(text)
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0][0], 'aware')
        self.assertEqual(objects[0][1], _getDottedName(aware.__class__))

        filename, text, content_type = context._wrote[1]
        self.assertEqual(filename, 'structure/.properties')
        self.assertEqual(content_type, 'text/plain')

        parser = _parseINI(text)

        defaults = parser.defaults()
        self.assertEqual(len(defaults), 2)
        self.assertEqual(defaults['title'], site.title)
        self.assertEqual(defaults['description'], site.description)

        filename, text, content_type = context._wrote[2]
        self.assertEqual(filename, 'structure/aware.csv')
        self.assertEqual(content_type, 'text/comma-separated-values')
        rows = _parseCSV(text)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], 'one')
        self.assertEqual(rows[0][1], 'two')
        self.assertEqual(rows[0][2], 'three')
        self.assertEqual(rows[1][0], 'four')
        self.assertEqual(rows[1][1], 'five')
        self.assertEqual(rows[1][2], 'six')

    def test_import_empty_site(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        self._setUpAdapters()
        site = _makeFolder('site')
        context = DummyImportContext(site)
        context._files['structure/.objects'] = ''
        importer = self._getImporter()
        self.assertEqual(len(site.objectIds()), 0)
        importer(context)
        self.assertEqual(len(site.objectIds()), 0)

    def test_import_empty_site_with_setup_tool(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        self._setUpAdapters()
        site = _makeFolder('site')
        site._setObject('setup_tool', self._makeSetupTool())
        context = DummyImportContext(site)
        importer = self._getImporter()

        self.assertEqual(len(site.objectIds()), 1)
        self.assertEqual(site.objectIds()[0], 'setup_tool')
        importer(context)
        self.assertEqual(len(site.objectIds()), 1)
        self.assertEqual(site.objectIds()[0], 'setup_tool')

    def test_import_site_with_subfolders(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from Products.GenericSetup.utils import _getDottedName
        self._setUpAdapters()
        FOLDER_IDS = ('foo', 'bar', 'baz')

        site = _makeFolder('site')
        dotted = _getDottedName(site.__class__)

        context = DummyImportContext(site)

        for id in FOLDER_IDS:
            context._files['structure/%s/.objects' % id] = ''
            context._files['structure/%s/.properties' % id] = (
                _PROPERTIES_TEMPLATE % id)

        _ROOT_OBJECTS = '\n'.join(['%s,%s' % (id, dotted)
                                   for id in FOLDER_IDS])

        context._files['structure/.objects'] = _ROOT_OBJECTS
        context._files['structure/.properties'] = (
            _PROPERTIES_TEMPLATE % 'Test Site')

        importer = self._getImporter()
        importer(context)

        content = site.objectValues()
        self.assertEqual(len(content), len(FOLDER_IDS))

    def test_import_site_with_subitems(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from Products.GenericSetup.utils import _getDottedName
        from Products.GenericSetup.tests.faux_objects import KNOWN_INI
        from Products.GenericSetup.tests.faux_objects import TestINIAware
        dotted = _getDottedName(TestINIAware)
        self._setUpAdapters()
        ITEM_IDS = ('foo', 'bar', 'baz')

        site = _makeFolder('site')

        context = DummyImportContext(site)
        # We want to add 'baz' to 'foo', without losing 'bar'
        context._files['structure/.objects'] = '\n'.join(
            ['%s,%s' % (x, dotted) for x in ITEM_IDS])
        for index in range(len(ITEM_IDS)):
            id = ITEM_IDS[index]
            context._files[
                'structure/%s.ini' % id] = KNOWN_INI % ('Title: %s' % id,
                                                        'xyzzy',
                                                        )
        importer = self._getImporter()
        importer(context)

        after = site.objectIds()
        self.assertEqual(len(after), len(ITEM_IDS))
        for found_id, expected_id in zip(after, ITEM_IDS):
            self.assertEqual(found_id, expected_id)

    def test_import_site_with_subitems_wo_adapter(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from Products.GenericSetup.utils import _getDottedName
        item = _makeItem('no_adapter')
        dotted = _getDottedName(item.__class__)
        self._setUpAdapters()

        site = _makeFolder('site')

        context = DummyImportContext(site)
        # We want to add 'baz' to 'foo', without losing 'bar'
        context._files['structure/.objects'] = '\n'.join(
            ['%s,%s' % (x, dotted) for x in ('no_adapter',)])
        importer = self._getImporter()
        importer(context)

        after = site.objectIds()
        self.assertEqual(len(after), 1)
        self.assertEqual(after[0], 'no_adapter')

    def test_import_site_with_subitems_and_blanklines_dotobjects(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from Products.GenericSetup.utils import _getDottedName
        from Products.GenericSetup.tests.faux_objects import KNOWN_INI
        from Products.GenericSetup.tests.faux_objects import TestINIAware
        dotted = _getDottedName(TestINIAware)
        self._setUpAdapters()
        ITEM_IDS = ('foo', 'bar', 'baz')

        site = _makeFolder('site')

        context = DummyImportContext(site)
        # We want to add 'baz' to 'foo', without losing 'bar'
        correct = '\n'.join(['%s,%s' % (x, dotted) for x in ITEM_IDS])
        broken = correct + '\n\n'
        context._files['structure/.objects'] = broken
        for index in range(len(ITEM_IDS)):
            id = ITEM_IDS[index]
            context._files[
                'structure/%s.ini' % id] = KNOWN_INI % ('Title: %s' % id,
                                                        'xyzzy',
                                                        )
        importer = self._getImporter()
        importer(context)

        after = site.objectIds()
        self.assertEqual(len(after), len(ITEM_IDS))
        for found_id, expected_id in zip(after, ITEM_IDS):
            self.assertEqual(found_id, expected_id)

    def test_import_site_with_subitem_unknown_portal_type(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from Products.GenericSetup.tests.faux_objects import KNOWN_INI
        self._setUpAdapters()
        ITEM_IDS = ('foo', 'bar', 'baz')

        site = _makeFolder('site')

        context = DummyImportContext(site)
        # We want to add 'baz' to 'foo', without losing 'bar'
        context._files['structure/.objects'] = '\n'.join(
            ['%s,Unknown Type' % x for x in ITEM_IDS])
        for index in range(len(ITEM_IDS)):
            id = ITEM_IDS[index]
            context._files[
                'structure/%s.ini' % id] = KNOWN_INI % ('Title: %s' % id,
                                                        'xyzzy',
                                                        )

        importer = self._getImporter()
        importer(context)

        after = site.objectIds()
        self.assertEqual(len(after), 0)
        self.assertEqual(len(context._notes), len(ITEM_IDS))
        for level, component, message in context._notes:
            self.assertEqual(component, 'SFWA')
            self.assertTrue(message.startswith("Couldn't make"))

    def test_import_site_with_subitems_and_no_preserve(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        self._setUpAdapters()
        ITEM_IDS = ('foo', 'bar', 'baz')

        site = _makeFolder('site')
        for id in ITEM_IDS:
            site._setObject(id, _makeItem(id))

        context = DummyImportContext(site)
        # We want to add 'baz' to 'foo', without losing 'bar'
        context._files['structure/.objects'] = ''

        importer = self._getImporter()
        importer(context)

        self.assertEqual(len(site.objectIds()), 0)

    def test_import_site_with_subitemss_and_preserve(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        self._setUpAdapters()
        ITEM_IDS = ('foo', 'bar', 'baz')

        site = _makeFolder('site')
        for id in ITEM_IDS:
            site._setObject(id, _makeItem(id))

        context = DummyImportContext(site)
        # We want to add 'baz' to 'foo', without losing 'bar'
        context._files['structure/.objects'] = ''
        context._files['structure/.preserve'] = '*'

        importer = self._getImporter()
        importer(context)

        after = site.objectIds()
        self.assertEqual(len(after), len(ITEM_IDS))
        for i in range(len(ITEM_IDS)):
            self.assertEqual(after[i], ITEM_IDS[i])

    def test_import_site_with_subitemss_and_preserve_partial(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        self._setUpAdapters()
        ITEM_IDS = ('foo', 'bar', 'baz')

        site = _makeFolder('site')
        for id in ITEM_IDS:
            site._setObject(id, _makeItem(id))

        context = DummyImportContext(site)
        # We want to add 'baz' to 'foo', without losing 'bar'
        context._files['structure/.objects'] = ''
        context._files['structure/.preserve'] = 'b*'

        importer = self._getImporter()
        importer(context)

        after = site.objectIds()
        self.assertEqual(len(after), 2)
        self.assertEqual(after[0], 'bar')
        self.assertEqual(after[1], 'baz')

    def test_import_site_with_subfolders_and_preserve(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from Products.GenericSetup.utils import _getDottedName
        self._setUpAdapters()

        site = _makeFolder('site')
        site._setObject('foo', _makeFolder('foo'))
        foo = site._getOb('foo')
        foo._setObject('bar', _makeFolder('bar'))
        bar = foo._getOb('bar')

        context = DummyImportContext(site)
        # We want to add 'baz' to 'foo', without losing 'bar'
        context._files['structure/.objects'
                       ] = 'foo,%s' % _getDottedName(foo.__class__)
        context._files['structure/.preserve'] = '*'
        context._files['structure/foo/.objects'
                       ] = 'baz,%s' % _getDottedName(bar.__class__)
        context._files['structure/foo/.preserve'] = '*'
        context._files['structure/foo/baz/.objects'] = ''

        importer = self._getImporter()
        importer(context)

        self.assertEqual(len(site.objectIds()), 1)
        self.assertEqual(site.objectIds()[0], 'foo')

        self.assertEqual(len(foo.objectIds()), 2, site.foo.objectIds())
        self.assertEqual(foo.objectIds()[0], 'bar')
        self.assertEqual(foo.objectIds()[1], 'baz')


class Test_globpattern(unittest.TestCase):

    NAMELIST = ('foo', 'bar', 'baz', 'bam', 'qux', 'quxx', 'quxxx')

    def _checkResults(self, globpattern, namelist, expected):
        from Products.GenericSetup.content import _globtest
        found = _globtest(globpattern, namelist)
        self.assertEqual(len(found), len(expected))
        for found_item, expected_item in zip(found, expected):
            self.assertEqual(found_item, expected_item)

    def test_star(self):
        self._checkResults('*', self.NAMELIST, self.NAMELIST)

    def test_simple(self):
        self._checkResults('b*', self.NAMELIST,
                           [x for x in self.NAMELIST if x.startswith('b')])

    def test_multiple(self):
        self._checkResults('b*\n*x', self.NAMELIST,
                           [x for x in self.NAMELIST
                            if x.startswith('b') or x.endswith('x')])


class CSVAwareFileAdapterTests(unittest.TestCase,
                               ConformsToIFilesystemExporter,
                               ConformsToIFilesystemImporter,
                               ):

    def _getTargetClass(self):
        from Products.GenericSetup.content import CSVAwareFileAdapter
        return CSVAwareFileAdapter

    def _makeOne(self, context, *args, **kw):
        return self._getTargetClass()(context, *args, **kw)

    def test_export_with_known_CSV(self):
        from Products.GenericSetup.tests.common import DummyExportContext
        from Products.GenericSetup.tests.faux_objects import KNOWN_CSV
        sheet = _makeCSVAware('config')

        adapter = self._makeOne(sheet)
        context = DummyExportContext(None)
        adapter.export(context, 'subpath/to/sheet')

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'subpath/to/sheet/config.csv')
        self.assertEqual(content_type, 'text/comma-separated-values')

        self.assertEqual(text.strip(), KNOWN_CSV.strip())

    def test_import_with_known_CSV(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        ORIG_CSV = """\
one,two,three
four,five,six
"""
        NEW_CSV = """\
four,five,six
one,two,three
"""
        sheet = _makeCSVAware('config', ORIG_CSV)

        adapter = self._makeOne(sheet)
        context = DummyImportContext(None)
        context._files['subpath/to/sheet/config.csv'] = NEW_CSV
        adapter.import_(context, 'subpath/to/sheet')

        self.assertEqual(sheet._was_put.getvalue().strip(), NEW_CSV.strip())


_PROPERTIES_TEMPLATE = """
[DEFAULT]
Title = %s
Description = This is a test
"""


class INIAwareFileAdapterTests(unittest.TestCase,
                               ConformsToIFilesystemExporter,
                               ConformsToIFilesystemImporter,
                               ):

    def _getTargetClass(self):
        from Products.GenericSetup.content import INIAwareFileAdapter
        return INIAwareFileAdapter

    def _makeOne(self, context, *args, **kw):
        return self._getTargetClass()(context, *args, **kw)

    def test_export_ini_file(self):
        from Products.GenericSetup.tests.common import DummyExportContext
        ini_file = _makeINIAware('ini_file.html')
        adapter = self._makeOne(ini_file)
        context = DummyExportContext(None)
        adapter.export(context, 'subpath/to')

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'subpath/to/ini_file.html.ini')
        self.assertEqual(content_type, 'text/plain')

        self.assertEqual(text.strip(), ini_file.as_ini().strip())

    def test_import_ini_file(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from Products.GenericSetup.tests.faux_objects import KNOWN_INI
        ini_file = _makeINIAware('ini_file.html')
        adapter = self._makeOne(ini_file)
        context = DummyImportContext(None)
        context._files['subpath/to/ini_file.html.ini'] = (
            KNOWN_INI % ('Title: ini_file', 'abc'))

        adapter.import_(context, 'subpath/to')
        text = ini_file._was_put
        parser = _parseINI(text)
        self.assertEqual(parser.get('DEFAULT', 'title'), 'Title: ini_file')
        self.assertEqual(parser.get('DEFAULT', 'description'), 'abc')


class DAVAwareFileAdapterTests(unittest.TestCase,
                               ConformsToIFilesystemExporter,
                               ConformsToIFilesystemImporter,
                               ):

    def _getTargetClass(self):
        from Products.GenericSetup.content import DAVAwareFileAdapter
        return DAVAwareFileAdapter

    def _makeOne(self, context, *args, **kw):
        return self._getTargetClass()(context, *args, **kw)

    def test_export_dav_file(self):
        from Products.GenericSetup.tests.common import DummyExportContext
        dav_file = _makeDAVAware('dav_file.html')
        adapter = self._makeOne(dav_file)
        context = DummyExportContext(None)
        adapter.export(context, 'subpath/to')

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'subpath/to/dav_file.html')
        self.assertEqual(content_type, 'text/plain')
        self.assertEqual(text.strip(), dav_file.manage_FTPget().strip())

    def test_import_dav_file(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from Products.GenericSetup.tests.faux_objects import KNOWN_DAV
        VALUES = ('Title: dav_file', 'Description: abc', 'body goes here')
        dav_file = _makeDAVAware('dav_file.html')
        adapter = self._makeOne(dav_file)
        context = DummyImportContext(None)
        context._files['subpath/to/dav_file.html'] = KNOWN_DAV % VALUES

        adapter.import_(context, 'subpath/to')
        self.assertEqual(dav_file._was_put, KNOWN_DAV % VALUES)


def _makePropertied(id):
    from Products.GenericSetup.tests.faux_objects \
        import TestSimpleItemWithProperties

    propertied = TestSimpleItemWithProperties()
    propertied._setId(id)

    return propertied


def _makeCSVAware(id, csv=None):
    from Products.GenericSetup.tests.faux_objects import TestCSVAware

    aware = TestCSVAware()
    aware._setId(id)
    if csv is not None:
        aware._csv = csv

    return aware


def _makeINIAware(id):
    from Products.GenericSetup.tests.faux_objects import TestINIAware

    aware = TestINIAware()
    aware._setId(id)

    return aware


def _makeDAVAware(id):
    from Products.GenericSetup.tests.faux_objects import TestDAVAware

    aware = TestDAVAware()
    aware._setId(id)

    return aware


def _makeItem(id):
    from Products.GenericSetup.tests.faux_objects import TestSimpleItem

    aware = TestSimpleItem()
    aware._setId(id)

    return aware


def _makeFolder(id):
    from OFS.Folder import Folder
    from OFS.interfaces import IObjectManager
    from OFS.interfaces import IPropertyManager
    from zope.interface import directlyProvides
    from zope.interface import providedBy

    folder = Folder(id)
    directlyProvides(folder, providedBy(folder)
                     + IObjectManager + IPropertyManager)

    return folder


def _parseCSV(text):
    from csv import reader
    from six.moves import cStringIO
    return [x for x in reader(cStringIO(text))]


def _parseINI(text):
    from six.moves.configparser import ConfigParser
    from six.moves import cStringIO
    parser = ConfigParser()
    try:
        parser.read_file(cStringIO(text))
    except AttributeError:  # Python 2
        parser.readfp(cStringIO(text))
    return parser


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SimpleINIAwareTests))
    suite.addTest(unittest.makeSuite(FolderishExporterImporterTests))
    suite.addTest(unittest.makeSuite(Test_globpattern))
    suite.addTest(unittest.makeSuite(CSVAwareFileAdapterTests))
    suite.addTest(unittest.makeSuite(INIAwareFileAdapterTests))
    suite.addTest(unittest.makeSuite(DAVAwareFileAdapterTests))
    return suite
