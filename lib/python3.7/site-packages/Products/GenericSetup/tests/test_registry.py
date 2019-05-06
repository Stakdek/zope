##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Registry unit tests.
"""
from __future__ import absolute_import
import unittest

from OFS.Folder import Folder
from Products.GenericSetup.testing import ExportImportZCMLLayer
from Products.GenericSetup.tests.common import BaseRegistryTests
from Products.GenericSetup import EXTENSION
from zope.interface import Interface

from .conformance import ConformsToIStepRegistry
from .conformance import ConformsToIImportStepRegistry
from .conformance import ConformsToIExportStepRegistry
from .conformance import ConformsToIToolsetRegistry
from .conformance import ConformsToIProfileRegistry


###############################
#   Dummy handlers
###############################
def ONE_FUNC(context): pass


def TWO_FUNC(context): pass


def THREE_FUNC(context): pass


def FOUR_FUNC(context): pass


def DOC_FUNC(site):
    """This is the first line.

    This is the second line.
    """


ONE_FUNC_NAME = '%s.%s' % (__name__, ONE_FUNC.__name__)
TWO_FUNC_NAME = '%s.%s' % (__name__, TWO_FUNC.__name__)
THREE_FUNC_NAME = '%s.%s' % (__name__, THREE_FUNC.__name__)
FOUR_FUNC_NAME = '%s.%s' % (__name__, FOUR_FUNC.__name__)
DOC_FUNC_NAME = '%s.%s' % (__name__, DOC_FUNC.__name__)

###############################
#   SSR tests
###############################


class ImportStepRegistryTests(BaseRegistryTests, ConformsToIStepRegistry,
                              ConformsToIImportStepRegistry):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):

        from Products.GenericSetup.registry import ImportStepRegistry
        return ImportStepRegistry

    def test_empty(self):

        registry = self._makeOne()

        self.assertEqual(len(registry.listSteps()), 0)
        self.assertEqual(len(registry.listStepMetadata()), 0)
        self.assertEqual(len(registry.sortSteps()), 0)

    def test_getStep_nonesuch(self):

        registry = self._makeOne()

        self.assertEqual(registry.getStep('nonesuch'), None)
        self.assertEqual(registry.getStep('nonesuch'), None)
        default = object()
        self.assertTrue(registry.getStepMetadata(
            'nonesuch', default) is default)
        self.assertTrue(registry.getStep('nonesuch', default) is default)
        self.assertTrue(registry.getStepMetadata(
            'nonesuch', default) is default)

    def test_getStep_defaulted(self):

        registry = self._makeOne()
        default = object()

        self.assertTrue(registry.getStep('nonesuch', default) is default)
        self.assertEqual(registry.getStepMetadata('nonesuch', {}), {})

    def test_registerStep_docstring(self):

        registry = self._makeOne()

        registry.registerStep(id='docstring', version='1', handler=DOC_FUNC,
                              dependencies=())

        info = registry.getStepMetadata('docstring')
        self.assertEqual(info['id'], 'docstring')
        self.assertEqual(info['handler'], DOC_FUNC_NAME)
        self.assertEqual(info['dependencies'], ())
        self.assertEqual(info['title'], 'This is the first line.')
        self.assertEqual(info['description'], 'This is the second line.')

    def test_registerStep_docstring_override(self):

        registry = self._makeOne()

        registry.registerStep(id='docstring', version='1', handler=DOC_FUNC,
                              dependencies=(), title='Title')

        info = registry.getStepMetadata('docstring')
        self.assertEqual(info['id'], 'docstring')
        self.assertEqual(info['handler'], DOC_FUNC_NAME)
        self.assertEqual(info['dependencies'], ())
        self.assertEqual(info['title'], 'Title')
        self.assertEqual(info['description'], 'This is the second line.')

    def test_registerStep_single(self):

        registry = self._makeOne()

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=('two', 'three'),
                              title='One Step', description='One small step')

        steps = registry.listSteps()
        self.assertEqual(len(steps), 1)
        self.assertTrue('one' in steps)
        self.assertEqual(registry.getStep('one'), ONE_FUNC)

        info = registry.getStepMetadata('one')
        self.assertEqual(info['id'], 'one')
        self.assertEqual(info['version'], '1')
        self.assertEqual(info['handler'], ONE_FUNC_NAME)
        self.assertEqual(info['dependencies'], ('two', 'three'))
        self.assertEqual(info['title'], 'One Step')
        self.assertEqual(info['description'], 'One small step')

        info_list = registry.listStepMetadata()
        self.assertEqual(len(info_list), 1)
        self.assertEqual(info, info_list[0])

    def test_registerStep_conflict(self):

        registry = self._makeOne()

        registry.registerStep(id='one', version='1', handler=ONE_FUNC_NAME)

        self.assertRaises(KeyError, registry.registerStep, id='one',
                          version='0', handler=ONE_FUNC)

        registry.registerStep(id='one', version='1', handler=ONE_FUNC_NAME)

        info_list = registry.listStepMetadata()
        self.assertEqual(len(info_list), 1)

    def test_registerStep_replacement(self):

        registry = self._makeOne()

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=('two', 'three'),
                              title='One Step', description='One small step')

        registry.registerStep(id='one', version='1.1', handler=ONE_FUNC,
                              dependencies=(), title='Leads to Another',
                              description='Another small step')

        info = registry.getStepMetadata('one')
        self.assertEqual(info['id'], 'one')
        self.assertEqual(info['version'], '1.1')
        self.assertEqual(info['dependencies'], ())
        self.assertEqual(info['title'], 'Leads to Another')
        self.assertEqual(info['description'], 'Another small step')

    def test_registerStep_multiple(self):

        registry = self._makeOne()

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=())

        registry.registerStep(id='two', version='2', handler=TWO_FUNC,
                              dependencies=())

        registry.registerStep(id='three', version='3', handler=THREE_FUNC,
                              dependencies=())

        steps = registry.listSteps()
        self.assertEqual(len(steps), 3)
        self.assertTrue('one' in steps)
        self.assertTrue('two' in steps)
        self.assertTrue('three' in steps)

    def test_sortStep_simple(self):

        registry = self._makeOne()

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=('two',))

        registry.registerStep(id='two', version='2', handler=TWO_FUNC,
                              dependencies=())

        steps = registry.sortSteps()
        self.assertEqual(len(steps), 2)
        one = steps.index('one')
        two = steps.index('two')

        self.assertTrue(0 <= two < one)

    def test_sortStep_chained(self):

        registry = self._makeOne()

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=('three',), title='One small step')

        registry.registerStep(id='two', version='2', handler=TWO_FUNC,
                              dependencies=('one',), title='Texas two step')

        registry.registerStep(id='three', version='3', handler=THREE_FUNC,
                              dependencies=(), title='Gimme three steps')

        steps = registry.sortSteps()
        self.assertEqual(len(steps), 3)
        one = steps.index('one')
        two = steps.index('two')
        three = steps.index('three')

        self.assertTrue(0 <= three < one < two)

    def test_sortStep_complex(self):

        registry = self._makeOne()

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=('two',), title='One small step')

        registry.registerStep(id='two', version='2', handler=TWO_FUNC,
                              dependencies=('four',), title='Texas two step')

        registry.registerStep(id='three', version='3', handler=THREE_FUNC,
                              dependencies=('four',),
                              title='Gimme three steps')

        registry.registerStep(id='four', version='4', handler=FOUR_FUNC,
                              dependencies=(), title='Four step program')

        steps = registry.sortSteps()
        self.assertEqual(len(steps), 4)
        one = steps.index('one')
        two = steps.index('two')
        three = steps.index('three')
        four = steps.index('four')

        self.assertTrue(0 <= four < two < one)
        self.assertTrue(0 <= four < three)

    def test_sortStep_equivalence(self):

        registry = self._makeOne()

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=('two', 'three'),
                              title='One small step')

        registry.registerStep(id='two', version='2', handler=TWO_FUNC,
                              dependencies=('four',), title='Texas two step')

        registry.registerStep(id='three', version='3', handler=THREE_FUNC,
                              dependencies=('four',),
                              title='Gimme three steps')

        registry.registerStep(id='four', version='4', handler=FOUR_FUNC,
                              dependencies=(), title='Four step program')

        steps = registry.sortSteps()
        self.assertEqual(len(steps), 4)
        one = steps.index('one')
        two = steps.index('two')
        three = steps.index('three')
        four = steps.index('four')

        self.assertTrue(0 <= four < two < one)
        self.assertTrue(0 <= four < three < one)

    def test_checkComplete_simple(self):

        registry = self._makeOne()

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=('two',))

        incomplete = registry.checkComplete()
        self.assertEqual(len(incomplete), 1)
        self.assertTrue(('one', 'two') in incomplete)

        registry.registerStep(id='two', version='2', handler=TWO_FUNC,
                              dependencies=())

        self.assertEqual(len(registry.checkComplete()), 0)

    def test_checkComplete_double(self):

        registry = self._makeOne()

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=('two', 'three'))

        incomplete = registry.checkComplete()
        self.assertEqual(len(incomplete), 2)
        self.assertTrue(('one', 'two') in incomplete)
        self.assertTrue(('one', 'three') in incomplete)

        registry.registerStep(id='two', version='2', handler=TWO_FUNC,
                              dependencies=())

        incomplete = registry.checkComplete()
        self.assertEqual(list(incomplete), [('one', 'three')])

        registry.registerStep(id='three', version='3', handler=THREE_FUNC,
                              dependencies=())

        self.assertEqual(list(registry.checkComplete()), [])

        registry.registerStep(id='two', version='2.1', handler=TWO_FUNC,
                              dependencies=('four',))

        incomplete = registry.checkComplete()
        self.assertTrue(('two', 'four') in incomplete)

    def test_generateXML_empty(self):

        registry = self._makeOne().__of__(self.app)

        self._compareDOM(registry.generateXML(), _EMPTY_IMPORT_XML, debug=True)

    def test_generateXML_single(self):

        registry = self._makeOne().__of__(self.app)

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=(), title='One Step',
                              description='One small step')

        self._compareDOM(registry.generateXML(), _SINGLE_IMPORT_XML)

    def test_generateXML_ordered(self):

        registry = self._makeOne().__of__(self.app)

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=('two',), title='One Step',
                              description='One small step')

        registry.registerStep(id='two', version='2', handler=TWO_FUNC,
                              dependencies=('three',), title='Two Steps',
                              description='Texas two step')

        registry.registerStep(id='three', version='3', handler=THREE_FUNC,
                              dependencies=(), title='Three Steps',
                              description='Gimme three steps')

        self._compareDOM(registry.generateXML(), _ORDERED_IMPORT_XML)

    def test_parseXML_empty(self):

        registry = self._makeOne().__of__(self.app)

        registry.registerStep(id='one', version='1', handler=ONE_FUNC,
                              dependencies=(), description='One small step')

        info_list = registry.parseXML(_EMPTY_IMPORT_XML)

        self.assertEqual(len(info_list), 0)

    def test_parseXML_single(self):

        registry = self._makeOne().__of__(self.app)

        registry.registerStep(id='two', version='2', handler=TWO_FUNC,
                              dependencies=(), title='Two Steps',
                              description='Texas two step')

        info_list = registry.parseXML(_SINGLE_IMPORT_XML)

        self.assertEqual(len(info_list), 1)

        info = info_list[0]
        self.assertEqual(info['id'], 'one')
        self.assertEqual(info['version'], '1')
        self.assertEqual(info['handler'], ONE_FUNC_NAME)
        self.assertEqual(info['dependencies'], ())
        self.assertEqual(info['title'], 'One Step')
        self.assertTrue('One small step' in info['description'])


_EMPTY_IMPORT_XML = """\
<?xml version="1.0"?>
<import-steps>
</import-steps>
"""

_SINGLE_IMPORT_XML = """\
<?xml version="1.0"?>
<import-steps>
 <import-step id="one"
             version="1"
             handler="%s"
             title="One Step">
  One small step
 </import-step>
</import-steps>
""" % ONE_FUNC_NAME

_ORDERED_IMPORT_XML = """\
<?xml version="1.0"?>
<import-steps>
 <import-step id="one"
             version="1"
             handler="%s"
             title="One Step">
  <dependency step="two" />
  One small step
 </import-step>
 <import-step id="three"
             version="3"
             handler="%s"
             title="Three Steps">
  Gimme three steps
 </import-step>
 <import-step id="two"
             version="2"
             handler="%s"
             title="Two Steps">
  <dependency step="three" />
  Texas two step
 </import-step>
</import-steps>
""" % (ONE_FUNC_NAME, THREE_FUNC_NAME, TWO_FUNC_NAME)

###############################
#   ESR tests
###############################


class ExportStepRegistryTests(BaseRegistryTests, ConformsToIStepRegistry,
                              ConformsToIExportStepRegistry):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):

        from Products.GenericSetup.registry import ExportStepRegistry
        return ExportStepRegistry

    def _makeOne(self, *args, **kw):

        return self._getTargetClass()(*args, **kw)

    def test_empty(self):

        registry = self._makeOne()
        self.assertEqual(len(registry.listSteps()), 0)
        self.assertEqual(len(registry.listStepMetadata()), 0)

    def test_getStep_nonesuch(self):

        registry = self._makeOne()
        self.assertEqual(registry.getStep('nonesuch'), None)

    def test_getStep_defaulted(self):
        def default(x):
            return False

        registry = self._makeOne()
        self.assertEqual(registry.getStep('nonesuch', default), default)

    def test_getStepMetadata_nonesuch(self):

        registry = self._makeOne()
        self.assertEqual(registry.getStepMetadata('nonesuch'), None)

    def test_getStepMetadata_defaulted(self):

        registry = self._makeOne()
        self.assertEqual(registry.getStepMetadata('nonesuch', {}), {})

    def test_registerStep_simple(self):

        registry = self._makeOne()
        registry.registerStep('one', ONE_FUNC_NAME)
        info = registry.getStepMetadata('one', {})

        self.assertEqual(info['id'], 'one')
        self.assertEqual(info['handler'], ONE_FUNC_NAME)
        self.assertEqual(info['title'], 'one')
        self.assertEqual(info['description'], '')

    def test_registerStep_docstring(self):

        registry = self._makeOne()
        registry.registerStep('one', DOC_FUNC)
        info = registry.getStepMetadata('one', {})

        self.assertEqual(info['id'], 'one')
        self.assertEqual(info['handler'], DOC_FUNC_NAME)
        self.assertEqual(info['title'], 'This is the first line.')
        self.assertEqual(info['description'], 'This is the second line.')

    def test_registerStep_docstring_with_override(self):

        registry = self._makeOne()
        registry.registerStep('one', DOC_FUNC, description='Description')
        info = registry.getStepMetadata('one', {})

        self.assertEqual(info['id'], 'one')
        self.assertEqual(info['handler'], DOC_FUNC_NAME)
        self.assertEqual(info['title'], 'This is the first line.')
        self.assertEqual(info['description'], 'Description')

    def test_registerStep_collision(self):

        registry = self._makeOne()
        registry.registerStep('one', ONE_FUNC)
        registry.registerStep('one', TWO_FUNC)
        info = registry.getStepMetadata('one', {})

        self.assertEqual(info['id'], 'one')
        self.assertEqual(info['handler'], TWO_FUNC_NAME)
        self.assertEqual(info['title'], 'one')
        self.assertEqual(info['description'], '')

    def test_generateXML_empty(self):

        registry = self._makeOne().__of__(self.app)

        self._compareDOM(registry.generateXML(), _EMPTY_EXPORT_XML)

    def test_generateXML_single(self):

        registry = self._makeOne().__of__(self.app)

        registry.registerStep(id='one', handler=ONE_FUNC, title='One Step',
                              description='One small step')

        self._compareDOM(registry.generateXML(), _SINGLE_EXPORT_XML)

    def test_generateXML_ordered(self):

        registry = self._makeOne().__of__(self.app)

        registry.registerStep(id='one', handler=ONE_FUNC, title='One Step',
                              description='One small step')

        registry.registerStep(id='two', handler=TWO_FUNC, title='Two Steps',
                              description='Texas two step')

        registry.registerStep(id='three', handler=THREE_FUNC,
                              title='Three Steps',
                              description='Gimme three steps')

        self._compareDOM(registry.generateXML(), _ORDERED_EXPORT_XML)

    def test_parseXML_empty(self):

        registry = self._makeOne().__of__(self.app)

        registry.registerStep(id='one', handler=ONE_FUNC,
                              description='One small step'
                              )

        info_list = registry.parseXML(_EMPTY_EXPORT_XML)

        self.assertEqual(len(info_list), 0)

    def test_parseXML_single(self):

        registry = self._makeOne().__of__(self.app)

        registry.registerStep(id='two', handler=TWO_FUNC, title='Two Steps',
                              description='Texas two step'
                              )

        info_list = registry.parseXML(_SINGLE_EXPORT_XML)

        self.assertEqual(len(info_list), 1)

        info = info_list[0]
        self.assertEqual(info['id'], 'one')
        self.assertEqual(info['handler'], ONE_FUNC_NAME)
        self.assertEqual(info['title'], 'One Step')
        self.assertTrue('One small step' in info['description'])

    def test_parseXML_single_as_ascii(self):

        registry = self._makeOne().__of__(self.app)

        registry.registerStep(id='two', handler=TWO_FUNC, title='Two Steps',
                              description='Texas two step'
                              )

        info_list = registry.parseXML(_SINGLE_EXPORT_XML, encoding='ascii')

        self.assertEqual(len(info_list), 1)

        info = info_list[0]
        self.assertEqual(info['id'], 'one')
        self.assertEqual(info['handler'], ONE_FUNC_NAME)
        self.assertEqual(info['title'], 'One Step')
        self.assertTrue('One small step' in info['description'])


_EMPTY_EXPORT_XML = """\
<?xml version="1.0"?>
<export-steps>
</export-steps>
"""

_SINGLE_EXPORT_XML = """\
<?xml version="1.0"?>
<export-steps>
 <export-step id="one"
                handler="%s"
                title="One Step">
  One small step
 </export-step>
</export-steps>
""" % ONE_FUNC_NAME

_ORDERED_EXPORT_XML = """\
<?xml version="1.0"?>
<export-steps>
 <export-step id="one"
                handler="%s"
                title="One Step">
  One small step
 </export-step>
 <export-step id="three"
                handler="%s"
                title="Three Steps">
  Gimme three steps
 </export-step>
 <export-step id="two"
                handler="%s"
                title="Two Steps">
  Texas two step
 </export-step>
</export-steps>
""" % (ONE_FUNC_NAME, THREE_FUNC_NAME, TWO_FUNC_NAME)


###############################
#   ToolsetRegistry tests
###############################


class ToolsetRegistryTests(BaseRegistryTests, ConformsToIToolsetRegistry):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):

        from Products.GenericSetup.registry import ToolsetRegistry
        return ToolsetRegistry

    def _initSite(self):

        self.app.site = Folder(id='site')
        site = self.app.site

        return site

    def test_empty(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        self.assertEqual(len(configurator.listForbiddenTools()), 0)
        self.assertEqual(len(configurator.listRequiredTools()), 0)
        self.assertEqual(len(configurator.listRequiredToolInfo()), 0)

        self.assertRaises(
            KeyError, configurator.getRequiredToolInfo, 'nonesuch')

    def test_addForbiddenTool_multiple(self):

        VERBOTTEN = ('foo', 'bar', 'bam')

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        for verbotten in VERBOTTEN:
            configurator.addForbiddenTool(verbotten)

        self.assertEqual(
            len(configurator.listForbiddenTools()), len(VERBOTTEN))

        for verbotten in configurator.listForbiddenTools():
            self.assertTrue(verbotten in VERBOTTEN)

    def test_addForbiddenTool_duplicate(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        configurator.addForbiddenTool('once')
        configurator.addForbiddenTool('once')

        self.assertEqual(len(configurator.listForbiddenTools()), 1)

    def test_addForbiddenTool_but_required(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        configurator.addRequiredTool('required', 'some.dotted.name')
        self.assertEqual(len(configurator.listRequiredToolInfo()), 1)
        self.assertEqual(len(configurator.listForbiddenTools()), 0)

        configurator.addForbiddenTool('required')
        self.assertEqual(len(configurator.listRequiredToolInfo()), 0)
        self.assertEqual(len(configurator.listForbiddenTools()), 1)

    def test_addRequiredTool_multiple(self):

        REQUIRED = (
            ('one', 'path.to.one'),
            ('two', 'path.to.two'),
            ('three', 'path.to.three'),
        )

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        for tool_id, dotted_name in REQUIRED:
            configurator.addRequiredTool(tool_id, dotted_name)

        self.assertEqual(len(configurator.listRequiredTools()), len(REQUIRED))

        for id in [x[0] for x in REQUIRED]:
            self.assertTrue(id in configurator.listRequiredTools())

        self.assertEqual(
            len(configurator.listRequiredToolInfo()), len(REQUIRED))

        for tool_id, dotted_name in REQUIRED:
            info = configurator.getRequiredToolInfo(tool_id)
            self.assertEqual(info['id'], tool_id)
            self.assertEqual(info['class'], dotted_name)

    def test_addRequiredTool_duplicate(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        configurator.addRequiredTool('required', 'some.dotted.name')
        configurator.addRequiredTool('required', 'another.name')

        info = configurator.getRequiredToolInfo('required')
        self.assertEqual(info['id'], 'required')
        self.assertEqual(info['class'], 'another.name')

    def test_addRequiredTool_but_forbidden(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        configurator.addForbiddenTool('forbidden')
        self.assertEqual(len(configurator.listRequiredToolInfo()), 0)
        self.assertEqual(len(configurator.listForbiddenTools()), 1)

        configurator.addRequiredTool('forbidden', 'a.name')
        self.assertEqual(len(configurator.listRequiredToolInfo()), 1)
        self.assertEqual(len(configurator.listForbiddenTools()), 0)

    def test_generateXML_empty(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        self._compareDOM(configurator.generateXML(), _EMPTY_TOOLSET_XML)

    def test_generateXML_normal(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        configurator.addForbiddenTool('doomed')
        configurator.addRequiredTool('mandatory', 'path.to.one')
        configurator.addRequiredTool('obligatory', 'path.to.another')

        configurator.parseXML(_NORMAL_TOOLSET_XML)

    def test_parseXML_empty(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        configurator.parseXML(_EMPTY_TOOLSET_XML)

        self.assertEqual(len(configurator.listForbiddenTools()), 0)
        self.assertEqual(len(configurator.listRequiredTools()), 0)

    def test_parseXML_normal(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        configurator.parseXML(_NORMAL_TOOLSET_XML)

        self.assertEqual(len(configurator.listForbiddenTools()), 1)
        self.assertTrue('doomed' in configurator.listForbiddenTools())

        self.assertEqual(len(configurator.listRequiredTools()), 2)

        self.assertTrue('mandatory' in configurator.listRequiredTools())
        info = configurator.getRequiredToolInfo('mandatory')
        self.assertEqual(info['class'], 'path.to.one')

        self.assertTrue('obligatory' in configurator.listRequiredTools())
        info = configurator.getRequiredToolInfo('obligatory')
        self.assertEqual(info['class'], 'path.to.another')

    def test_parseXML_confused(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        configurator.parseXML(_CONFUSED_TOOLSET_XML)
        self.assertEqual(len(configurator.listForbiddenTools()), 0)
        self.assertEqual(len(configurator.listRequiredToolInfo()), 1)

    def test_parseXML_wrong(self):

        site = self._initSite()
        configurator = self._makeOne().__of__(site)

        # The 'remove' keyword is explicitly not supported.
        self.assertRaises(
            ValueError, configurator.parseXML, _WRONG_TOOLSET_XML)


_EMPTY_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
</tool-setup>
"""

_NORMAL_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
 <forbidden tool_id="doomed" />
 <required tool_id="mandatory" class="path.to.one" />
 <required tool_id="obligatory" class="path.to.another" />
</tool-setup>
"""

_CONFUSED_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
 <forbidden tool_id="confused" />
 <required tool_id="confused" class="path.to.one" />
</tool-setup>
"""

_WRONG_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
 <required tool_id="confused" class="path.to.one" remove="" />
</tool-setup>
"""


class ISite(Interface):
    pass


class IDerivedSite(ISite):
    pass


class IAnotherSite(Interface):
    pass


class ProfileRegistryTests(BaseRegistryTests, ConformsToIProfileRegistry):

    def _getTargetClass(self):

        from Products.GenericSetup.registry import ProfileRegistry
        return ProfileRegistry

    def test_empty(self):

        registry = self._makeOne()

        self.assertEqual(len(registry.listProfiles()), 0)
        self.assertEqual(len(registry.listProfiles()), 0)
        self.assertRaises(KeyError, registry.getProfileInfo, 'nonesuch')

    def test_registerProfile_normal(self):

        NAME = 'one'
        TITLE = 'One'
        DESCRIPTION = 'One profile'
        PATH = '/path/to/one'
        PRODUCT = 'TestProduct'
        PROFILE_TYPE = EXTENSION
        PROFILE_ID = 'TestProduct:one'

        registry = self._makeOne()
        registry.registerProfile(NAME, TITLE, DESCRIPTION, PATH, PRODUCT,
                                 PROFILE_TYPE)

        self.assertEqual(len(registry.listProfiles()), 1)
        self.assertEqual(len(registry.listProfileInfo()), 1)

        info = registry.getProfileInfo(PROFILE_ID)

        self.assertEqual(info['id'], PROFILE_ID)
        self.assertEqual(info['title'], TITLE)
        self.assertEqual(info['description'], DESCRIPTION)
        self.assertEqual(info['path'], PATH)
        self.assertEqual(info['product'], PRODUCT)
        self.assertEqual(info['type'], PROFILE_TYPE)
        self.assertEqual(info['for'], None)
        self.assertEqual(info['pre_handler'], None)
        self.assertEqual(info['post_handler'], None)

        # We strip off any 'profile-' or 'snapshot-' at the beginning
        # of the profile id.
        info2 = registry.getProfileInfo('profile-' + PROFILE_ID)
        self.assertEqual(info, info2)
        info3 = registry.getProfileInfo('snapshot-' + PROFILE_ID)
        self.assertEqual(info, info3)

    def test_registerProfile_duplicate_same(self):

        NAME = 'one'
        TITLE = 'One'
        DESCRIPTION = 'One profile'
        PATH = '/path/to/one'

        registry = self._makeOne()
        registry.registerProfile(NAME, TITLE, DESCRIPTION, PATH)
        # If we register the exact same profile, this should be fine.
        # We will just keep the old one.
        info = registry.getProfileInfo('other:one')
        registry.registerProfile(NAME, TITLE, DESCRIPTION, PATH)
        new_info = registry.getProfileInfo('other:one')
        self.assertEqual(info, new_info)

    def test_registerProfile_duplicate_other(self):

        NAME = 'one'
        TITLE = 'One'
        DESCRIPTION = 'One profile'
        PATH = '/path/to/one'

        registry = self._makeOne()
        registry.registerProfile(NAME, TITLE, DESCRIPTION, PATH)
        DESCRIPTION = 'Other profile'
        self.assertRaises(KeyError, registry.registerProfile,
                          NAME, TITLE, DESCRIPTION, PATH)

    def test_registerProfile_site_type(self):

        NAME = 'one'
        TITLE = 'One'
        DESCRIPTION = 'One profile'
        PATH = '/path/to/one'
        PRODUCT = 'TestProduct'
        PROFILE_ID = 'TestProduct:one'
        PROFILE_TYPE = EXTENSION
        FOR = ISite
        NOT_FOR = IAnotherSite
        DERIVED_FOR = IDerivedSite

        registry = self._makeOne()
        registry.registerProfile(NAME, TITLE, DESCRIPTION, PATH, PRODUCT,
                                 PROFILE_TYPE, for_=FOR)

        self.assertEqual(len(registry.listProfiles()), 1)
        self.assertEqual(len(registry.listProfiles(for_=FOR)), 1)
        self.assertEqual(len(registry.listProfiles(for_=DERIVED_FOR)), 1)
        self.assertEqual(len(registry.listProfiles(for_=NOT_FOR)), 0)

        self.assertEqual(len(registry.listProfileInfo()), 1)
        self.assertEqual(len(registry.listProfileInfo(for_=FOR)), 1)
        self.assertEqual(len(registry.listProfileInfo(for_=DERIVED_FOR)), 1)
        self.assertEqual(len(registry.listProfileInfo(for_=NOT_FOR)), 0)

        # Verify that these lookups succeed...
        info1 = registry.getProfileInfo(PROFILE_ID)
        info2 = registry.getProfileInfo(PROFILE_ID, for_=FOR)
        info3 = registry.getProfileInfo(PROFILE_ID, for_=DERIVED_FOR)

        self.assertEqual(info1, info2)
        self.assertEqual(info1, info3)

        # ...and that this one fails.
        self.assertRaises(KeyError, registry.getProfileInfo, PROFILE_ID,
                          for_=NOT_FOR)

        info = registry.getProfileInfo(PROFILE_ID, for_=FOR)

        self.assertEqual(info['id'], PROFILE_ID)
        self.assertEqual(info['title'], TITLE)
        self.assertEqual(info['description'], DESCRIPTION)
        self.assertEqual(info['path'], PATH)
        self.assertEqual(info['product'], PRODUCT)
        self.assertEqual(info['type'], PROFILE_TYPE)
        self.assertEqual(info['for'], FOR)

    def test_getProfileInfo_tarball(self):
        # When importing a tarball, some code calls getProfileInfo with id
        # None.  This must not crash.
        registry = self._makeOne()
        self.assertEqual(registry.getProfileInfo(None),
                         {'description': u'',
                          'for': None,
                          'id': u'',
                          'path': u'',
                          'product': u'',
                          'title': u'',
                         'type': None})


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ImportStepRegistryTests),
        unittest.makeSuite(ExportStepRegistryTests),
        unittest.makeSuite(ToolsetRegistryTests),
        unittest.makeSuite(ProfileRegistryTests),
    ))
