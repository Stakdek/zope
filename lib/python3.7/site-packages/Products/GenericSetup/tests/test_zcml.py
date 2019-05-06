##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests for zcml module.
"""

import doctest
import unittest
from doctest import ELLIPSIS
from zope.testing.cleanup import cleanUp

from Products.GenericSetup.registry import _import_step_registry
from Products.GenericSetup.registry import _export_step_registry

from Zope2.App import zcml


def dummy_importstep(context):
    pass


def dummy_exportstep(context):
    pass


def dummy_upgrade(context):
    pass


def b_dummy_upgrade(context):
    pass


def c_dummy_upgrade(context):
    pass


def test_simpleRegisterProfile():
    """
    Use the genericsetup:registerProfile directive::

      >>> import Products.GenericSetup
      >>> configure_zcml = '''
      ... <configure
      ...     xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
      ...     i18n_domain="foo">
      ...   <genericsetup:registerProfile
      ...       provides="Products.GenericSetup.interfaces.EXTENSION"
      ...       />
      ... </configure>'''
      >>> zcml.load_config('meta.zcml', Products.GenericSetup)
      >>> zcml.load_string(configure_zcml)

    Make sure the profile is registered correctly::

      >>> from Products.GenericSetup.registry import _profile_registry
      >>> profile_id = 'Products.GenericSetup:default'
      >>> info = _profile_registry.getProfileInfo(profile_id)
      >>> info['id'] == 'Products.GenericSetup:default'
      True
      >>> info['title'] == "Profile 'default' from 'Products.GenericSetup'"
      True
      >>> info['description'] == ''
      True
      >>> info['path'] == 'profiles/default'
      True
      >>> info['product']
      'Products.GenericSetup'
      >>> from Products.GenericSetup.interfaces import EXTENSION
      >>> info['type'] is EXTENSION
      True
      >>> info['for'] is None
      True

    Clean up and make sure the cleanup works::

      >>> cleanUp()
    """


def test_registerProfile():
    """
    Use the genericsetup:registerProfile directive::

      >>> import Products.GenericSetup
      >>> configure_zcml = '''
      ... <configure
      ...     xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
      ...     i18n_domain="foo">
      ...   <genericsetup:registerProfile
      ...       name="default"
      ...       title="Install Foo Extension"
      ...       description="Adds foo support."
      ...       provides="Products.GenericSetup.interfaces.EXTENSION"
      ...       />
      ... </configure>'''
      >>> zcml.load_config('meta.zcml', Products.GenericSetup)
      >>> zcml.load_string(configure_zcml)

    Make sure the profile is registered correctly::

      >>> from Products.GenericSetup.registry import _profile_registry
      >>> profile_id = 'Products.GenericSetup:default'
      >>> info = _profile_registry.getProfileInfo(profile_id)
      >>> info['id'] == 'Products.GenericSetup:default'
      True
      >>> info['title'] == 'Install Foo Extension'
      True
      >>> info['description'] == 'Adds foo support.'
      True
      >>> info['path'] == 'profiles/default'
      True
      >>> info['product']
      'Products.GenericSetup'
      >>> from Products.GenericSetup.interfaces import EXTENSION
      >>> info['type'] is EXTENSION
      True
      >>> info['for'] is None
      True

    Clean up and make sure the cleanup works::

      >>> cleanUp()
    """


def test_registerUpgradeStep(self):
    """
    Use the standalone genericsetup:upgradeStep directive::

      >>> import Products.GenericSetup
      >>> configure_zcml = '''
      ... <configure
      ...     xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
      ...     i18n_domain="foo">
      ...   <genericsetup:upgradeStep
      ...       title="Upgrade Foo Product"
      ...       description="Upgrades Foo from 1.0 to 1.1."
      ...       source="1.0"
      ...       destination="1.1"
      ...       handler="Products.GenericSetup.tests.test_zcml.dummy_upgrade"
      ...       sortkey="1"
      ...       profile="default"
      ...       />
      ... </configure>'''
      >>> zcml.load_config('meta.zcml', Products.GenericSetup)
      >>> zcml.load_string(configure_zcml)

    Make sure the upgrade step is registered correctly::

      >>> from Products.GenericSetup.upgrade import _upgrade_registry as _ur
      >>> profile_steps = _ur.getUpgradeStepsForProfile('default')
      >>> keys = profile_steps.keys()
      >>> len(keys)
      1
      >>> step = profile_steps[keys[0]]
      >>> step.source
      ('1', '0')
      >>> step.dest
      ('1', '1')
      >>> step.handler
      <function dummy_upgrade at ...>
      >>> step_id = step.id
      >>> step_id == keys[0]
      True

    Get the step in a different way::

      >>> step2 = _ur.getUpgradeStep('default', step_id)
      >>> step == step2
      True

    We strip off any 'profile-' at the beginning of the profile id::

      >>> profile_steps2 = _ur.getUpgradeStepsForProfile('profile-default')
      >>> profile_steps == profile_steps2
      True
      >>> step3 = _ur.getUpgradeStep('profile-default', step_id)
      >>> step == step3
      True

    Clean up and make sure the cleanup works::

      >>> cleanUp()
    """


def test_registerUpgradeDepends(self):
    """
    Use the standalone genericsetup:upgradeDepends directive::

      >>> import Products.GenericSetup
      >>> configure_zcml = '''
      ... <configure
      ...     xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
      ...     i18n_domain="foo">
      ...   <genericsetup:upgradeDepends
      ...       title="Upgrade Foo Product"
      ...       source="1.0"
      ...       destination="1.1"
      ...       sortkey="1"
      ...       profile="default"
      ...       />
      ... </configure>'''
      >>> zcml.load_config('meta.zcml', Products.GenericSetup)
      >>> zcml.load_string(configure_zcml)

    Make sure the upgrade step is registered correctly::

      >>> from Products.GenericSetup.upgrade import _upgrade_registry as _ur
      >>> profile_steps = _ur.getUpgradeStepsForProfile('default')
      >>> keys = profile_steps.keys()
      >>> len(keys)
      1
      >>> step = profile_steps[keys[0]]
      >>> step.source
      ('1', '0')
      >>> step.dest
      ('1', '1')
      >>> step.import_steps
      []
      >>> step.run_deps
      False
      >>> step.purge
      False

    Clean up and make sure the cleanup works::

      >>> cleanUp()
    """


def test_registerUpgradeSteps(self):
    """
    Use the nested genericsetup:upgradeSteps directive::

      >>> import Products.GenericSetup
      >>> configure_zcml = '''
      ... <configure
      ...     xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
      ...     i18n_domain="foo">
      ...  <genericsetup:upgradeSteps
      ...       profile="default"
      ...       source="1.0"
      ...       destination="1.1"
      ...       sortkey="2"
      ...       >
      ...   <genericsetup:upgradeStep
      ...       title="Foo Upgrade Step 1"
      ...       description="Does some Foo upgrade thing."
      ...       handler="Products.GenericSetup.tests.test_zcml.b_dummy_upgrade"
      ...       />
      ...   <genericsetup:upgradeStep
      ...       title="Foo Upgrade Step 2"
      ...       description="Does another Foo upgrade thing."
      ...       handler="Products.GenericSetup.tests.test_zcml.c_dummy_upgrade"
      ...       />
      ...  </genericsetup:upgradeSteps>
      ...  <genericsetup:upgradeSteps
      ...       profile="default"
      ...       source="1.0"
      ...       destination="1.1"
      ...       sortkey="1"
      ...       >
      ...   <genericsetup:upgradeStep
      ...       title="Bar Upgrade Step 1"
      ...       description="Does some Bar upgrade thing."
      ...       handler="Products.GenericSetup.tests.test_zcml.b_dummy_upgrade"
      ...       />
      ...   <genericsetup:upgradeStep
      ...       title="Bar Upgrade Step 2"
      ...       description="Does another Bar upgrade thing."
      ...       handler="Products.GenericSetup.tests.test_zcml.c_dummy_upgrade"
      ...       />
      ...   <genericsetup:upgradeDepends
      ...       title="Bar Upgrade dependency profile import steps"
      ...       description="Re-imports steps from the profile"
      ...       import_profile="profile-Products.CMFDefault:default"
      ...       import_steps="baz bat"
      ...       run_deps="True"
      ...       purge="True"
      ...       />
      ...  </genericsetup:upgradeSteps>
      ... </configure>'''
      >>> zcml.load_config('meta.zcml', Products.GenericSetup)
      >>> zcml.load_string(configure_zcml)

    Make sure the upgrade steps are registered correctly::

      >>> from Products.GenericSetup.upgrade import listUpgradeSteps
      >>> from Products.GenericSetup.tool import SetupTool
      >>> tool = SetupTool('setup_tool')
      >>> profile_steps = listUpgradeSteps(tool, 'default', '1.0')
      >>> len(profile_steps)
      2
      >>> steps = profile_steps[0]
      >>> isinstance(steps, list)
      True
      >>> len(steps)
      3
      >>> step1, step2, step3 = steps
      >>> step1['source'] == step2['source'] == step3['source'] == ('1', '0')
      True
      >>> step1['dest'] == step2['dest'] == step3['dest'] == ('1', '1')
      True
      >>> step1['step'].handler
      <function b_dummy_upgrade at ...>
      >>> str(step1['title'])
      'Bar Upgrade Step 1'
      >>> step2['step'].handler
      <function c_dummy_upgrade at ...>
      >>> str(step2['title'])
      'Bar Upgrade Step 2'
      >>> str(step3['step'].import_profile)
      'profile-Products.CMFDefault:default'
      >>> [str(step) for step in step3['step'].import_steps]
      ['baz', 'bat']
      >>> step3['step'].run_deps
      True
      >>> step3['step'].purge
      True

    First one listed should be second in the registry due to sortkey:

      >>> steps = profile_steps[1]
      >>> isinstance(steps, list)
      True
      >>> len(steps)
      2
      >>> step1, step2 = steps
      >>> step1['source'] == step2['source'] == ('1', '0')
      True
      >>> step1['dest'] == step2['dest'] == ('1', '1')
      True
      >>> step1['step'].handler
      <function b_dummy_upgrade at ...>
      >>> str(step1['title'])
      'Foo Upgrade Step 1'
      >>> step2['step'].handler
      <function c_dummy_upgrade at ...>
      >>> str(step2['title'])
      'Foo Upgrade Step 2'

    Clean up and make sure the cleanup works::

      >>> cleanUp()
    """


class ImportStepTests(unittest.TestCase):

    def setUp(self):
        import Products.GenericSetup
        zcml.load_config('meta.zcml', Products.GenericSetup)

    def tearDown(self):
        cleanUp()

    def testNoDependencies(self):
        zcml.load_string("""\
        <configure xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
                   i18n_domain="genericsetup">
         <genericsetup:importStep
             name="name"
             title="title"
             description="description"
             handler="Products.GenericSetup.tests.test_zcml.dummy_importstep">
         </genericsetup:importStep>
        </configure>""")
        self.assertEqual(_import_step_registry.listSteps(), ['name'])
        data = _import_step_registry.getStepMetadata(u'name')
        expected = 'Products.GenericSetup.tests.test_zcml.dummy_importstep'
        self.assertEqual(data["handler"], expected)
        self.assertEqual(data["description"], u"description")
        self.assertEqual(data["title"], u"title")
        self.assertEqual(data["dependencies"], ())
        self.assertEqual(data["id"], u"name")

    def testWithDependency(self):
        zcml.load_string("""
        <configure xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
                   i18n_domain="genericsetup">
         <genericsetup:importStep
             name="name"
             title="title"
             description="description"
             handler="Products.GenericSetup.tests.test_zcml.dummy_importstep">
          <depends name="something.else"/>
         </genericsetup:importStep>
        </configure>""")
        data = _import_step_registry.getStepMetadata(u'name')
        self.assertEqual(data["dependencies"], (u"something.else",))


class ExportStepTests(unittest.TestCase):

    def setUp(self):
        import Products.GenericSetup
        zcml.load_config('meta.zcml', Products.GenericSetup)

    def tearDown(self):
        cleanUp()

    def testRegistration(self):
        zcml.load_string("""\
        <configure xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
                   i18n_domain="genericsetup">
        <genericsetup:exportStep
            name="name"
            title="title"
            description="description"
            handler="Products.GenericSetup.tests.test_zcml.dummy_exportstep"
            />
        </configure>""")
        self.assertEqual(_export_step_registry.listSteps(), [u'name'])
        data = _export_step_registry.getStepMetadata(u'name')
        expected = 'Products.GenericSetup.tests.test_zcml.dummy_exportstep'
        self.assertEqual(data["handler"], expected)
        self.assertEqual(data["description"], u"description")
        self.assertEqual(data["title"], u"title")
        self.assertEqual(data["id"], u"name")


class UpgradeStepTests(unittest.TestCase):

    def setUp(self):
        import Products.GenericSetup
        zcml.load_config('meta.zcml', Products.GenericSetup)

    def tearDown(self):
        cleanUp()

    def testSimilarStepsForDifferentProfilesDoNotConflict(self):
        from zope.configuration.config import ConfigurationConflictError
        try:
            zcml.load_string("""
<configure xmlns="http://namespaces.zope.org/genericsetup"
      i18n_domain="genericsetup">
 <upgradeStep
     profile="profile1"
     title="title"
     description="description"
     source="1"
     destination="2"
     handler="Products.GenericSetup.tests.test_zcml.b_dummy_upgrade" />
 <upgradeStep
     profile="profile2"
     title="title"
     description="description"
     source="1"
     destination="2"
     handler="Products.GenericSetup.tests.test_zcml.b_dummy_upgrade" />
</configure>""")
        except ConfigurationConflictError:
            self.fail('Upgrade steps should not conflict')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(optionflags=ELLIPSIS))
    suite.addTest(unittest.makeSuite(ImportStepTests))
    suite.addTest(unittest.makeSuite(ExportStepTests))
    suite.addTest(unittest.makeSuite(UpgradeStepTests))
    return suite
