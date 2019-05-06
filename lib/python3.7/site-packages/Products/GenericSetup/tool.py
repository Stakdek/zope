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
""" Classes:  SetupTool
"""

try:
    from html import escape
except ImportError:  # BBB Python 2
    from cgi import escape
import logging
import os
import six
import time
import types
from operator import itemgetter

from AccessControl.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from Acquisition import aq_base
from OFS.Folder import Folder
from OFS.Image import File
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from persistent.mapping import PersistentMapping
from zope import event
from zope.interface import implementer

from Products.GenericSetup.context import DirectoryImportContext
from Products.GenericSetup.context import SnapshotExportContext
from Products.GenericSetup.context import SnapshotImportContext
from Products.GenericSetup.context import TarballExportContext
from Products.GenericSetup.context import TarballImportContext
from Products.GenericSetup.differ import ConfigDiff
from Products.GenericSetup.events import BeforeProfileImportEvent
from Products.GenericSetup.events import ProfileImportedEvent
from Products.GenericSetup.interfaces import BASE
from Products.GenericSetup.interfaces import EXTENSION
from Products.GenericSetup.interfaces import ISetupTool
from Products.GenericSetup.interfaces import SKIPPED_FILES
from Products.GenericSetup.permissions import ManagePortal
from Products.GenericSetup.registry import ExportStepRegistry
from Products.GenericSetup.registry import ImportStepRegistry
from Products.GenericSetup.registry import ToolsetRegistry
from Products.GenericSetup.registry import _export_step_registry
from Products.GenericSetup.registry import _import_step_registry
from Products.GenericSetup.registry import _profile_registry
from Products.GenericSetup.upgrade import _upgrade_registry
from Products.GenericSetup.upgrade import listProfilesWithUpgrades
from Products.GenericSetup.upgrade import listUpgradeSteps
from Products.GenericSetup.utils import _computeTopologicalSort
from Products.GenericSetup.utils import _getProductPath
from Products.GenericSetup.utils import _resolveDottedName
from Products.GenericSetup.utils import _wwwdir

IMPORT_STEPS_XML = 'import_steps.xml'
EXPORT_STEPS_XML = 'export_steps.xml'
TOOLSET_XML = 'toolset.xml'
# What do we do with already applied dependency profiles?
# The behavior used to be: reapply.  Now there are more options.
DEPENDENCY_STRATEGY_UPGRADE = 'upgrade'
DEPENDENCY_STRATEGY_REAPPLY = 'reapply'
DEPENDENCY_STRATEGY_NEW = 'new'
DEPENDENCY_STRATEGY_IGNORE = 'ignore'
DEFAULT_DEPENDENCY_STRATEGY = DEPENDENCY_STRATEGY_UPGRADE
# unknown profile version:
UNKNOWN = 'unknown'

generic_logger = logging.getLogger(__name__)


def exportStepRegistries(context):
    """ Built-in handler for exporting import / export step registries.
    """
    setup_tool = context.getSetupTool()
    logger = context.getLogger('registries')

    import_step_registry = setup_tool.getImportStepRegistry()
    if len(import_step_registry.listSteps()) > 0:
        import_steps_xml = import_step_registry.generateXML().encode('utf-8')
        context.writeDataFile('import_steps.xml', import_steps_xml, 'text/xml')
        logger.info('Local import steps exported.')
    else:
        logger.debug('No local import steps.')

    export_step_registry = setup_tool.getExportStepRegistry()
    if len(export_step_registry.listSteps()) > 0:
        export_steps_xml = export_step_registry.generateXML().encode('utf-8')
        context.writeDataFile('export_steps.xml', export_steps_xml, 'text/xml')
        logger.info('Local export steps exported.')
    else:
        logger.debug('No local export steps.')


def importToolset(context):
    """ Import required / forbidden tools from XML file.
    """
    site = context.getSite()
    encoding = context.getEncoding()
    logger = context.getLogger('toolset')

    xml = context.readDataFile(TOOLSET_XML)
    if xml is None:
        logger.debug('Nothing to import.')
        return

    setup_tool = context.getSetupTool()
    toolset = setup_tool.getToolsetRegistry()

    toolset.parseXML(xml, encoding)

    existing_ids = site.objectIds()

    for tool_id in toolset.listForbiddenTools():

        if tool_id in existing_ids:
            site._delObject(tool_id)

    for info in toolset.listRequiredToolInfo():

        tool_id = str(info['id'])
        tool_class = _resolveDottedName(info['class'])
        if tool_class is None:
            logger.warning("Not creating required tool %(id)s, because "
                           "class %(class)s is not found." % info)
            continue

        existing = getattr(aq_base(site), tool_id, None)
        # Don't even initialize the tool again, if it already exists.
        if existing is None:
            try:
                new_tool = tool_class()
            except TypeError:
                new_tool = tool_class(tool_id)
            else:
                new_tool._setId(tool_id)

            site._setObject(tool_id, new_tool)
        else:
            if tool_class is None:
                continue
            unwrapped = aq_base(existing)
            # don't use isinstance here as a subclass may need removing
            if type(unwrapped) != tool_class:
                site._delObject(tool_id)
                site._setObject(tool_id, tool_class())

    logger.info('Toolset imported.')


def exportToolset(context):
    """ Export required / forbidden tools to XML file.
    """
    setup_tool = context.getSetupTool()
    toolset = setup_tool.getToolsetRegistry()
    logger = context.getLogger('toolset')

    xml = toolset.generateXML().encode('utf-8')
    context.writeDataFile(TOOLSET_XML, xml, 'text/xml')

    logger.info('Toolset exported.')


@implementer(ISetupTool)
class SetupTool(Folder):

    """ Profile-based site configuration manager.
    """

    meta_type = 'Generic Setup Tool'
    zmi_icon = 'fas fa-industry'
    zmi_show_add_dialog = False

    _baseline_context_id = ''

    # Mapping from profile id to last applied version.  We set this in __init__
    # now, but keep it here to avoid a possible AttributeError for existing
    # tools that have not added any versions here, which would have caused a
    # copy to be made.  The not persistent dict will cause the tool to get its
    # own mapping when setLastVersionForProfile or unsetLastVersionForProfile
    # are called, replacing the one from the class shared by all such existing
    # instances.
    _profile_upgrade_versions = {}

    _exclude_global_steps = False

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = str(id)
        self._import_registry = ImportStepRegistry()
        self._export_registry = ExportStepRegistry()
        self._toolset_registry = ToolsetRegistry()
        self._profile_upgrade_versions = PersistentMapping()

    #
    #   ISetupTool API
    #
    @security.protected(ManagePortal)
    def getEncoding(self):
        """ See ISetupTool.
        """
        return 'utf-8'

    @security.protected(ManagePortal)
    def getBaselineContextID(self):
        """ See ISetupTool.
        """
        return self._baseline_context_id

    @security.protected(ManagePortal)
    def setBaselineContext(self, context_id, encoding=None):
        """ See ISetupTool.
        """
        self._baseline_context_id = context_id
        self.applyContextById(context_id, encoding)

    @security.protected(ManagePortal)
    def getExcludeGlobalSteps(self):
        """ See ISetupTool.
        """
        return self._exclude_global_steps

    @security.protected(ManagePortal)
    def setExcludeGlobalSteps(self, value):
        """ See ISetupTool.
        """
        self._exclude_global_steps = value

    @security.protected(ManagePortal)
    def applyContextById(self, context_id, encoding=None):
        context = self._getImportContext(context_id)
        self.applyContext(context, encoding)

    @security.protected(ManagePortal)
    def applyContext(self, context, encoding=None):
        self._updateImportStepsRegistry(context, encoding)
        self._updateExportStepsRegistry(context, encoding)

    @security.protected(ManagePortal)
    def getImportStepRegistry(self):
        """ See ISetupTool.
        """
        return self._import_registry

    @security.protected(ManagePortal)
    def getExportStepRegistry(self):
        """ See ISetupTool.
        """
        return self._export_registry

    @security.protected(ManagePortal)
    def getImportStep(self, step, default=None):
        """Simple wrapper to query both the global and local step registry."""
        res = self._import_registry.getStep(step, self)
        if res is self and not self._exclude_global_steps:
            res = _import_step_registry.getStep(step, self)
        if res is not self:
            return res
        return default

    @security.protected(ManagePortal)
    def getSortedImportSteps(self):
        if self._exclude_global_steps:
            steps = set()
        else:
            steps = set(_import_step_registry.listSteps())
        steps.update(set(self._import_registry.listSteps()))
        step_infos = [self.getImportStepMetadata(step) for step in steps]
        return tuple(_computeTopologicalSort(step_infos))

    @security.protected(ManagePortal)
    def getImportStepMetadata(self, step, default=None):
        """Simple wrapper to query both the global and local step registry."""
        res = self._import_registry.getStepMetadata(step, self)
        if res is self and not self._exclude_global_steps:
            res = _import_step_registry.getStepMetadata(step, default)
        if res is not self:
            return res
        return default

    @security.protected(ManagePortal)
    def getExportStep(self, step, default=None):
        """Simple wrapper to query both the global and local step registry."""
        res = self._export_registry.getStep(step, self)
        if res is self and not self._exclude_global_steps:
            res = _export_step_registry.getStep(step, self)
        if res is not self:
            return res
        return default

    @security.protected(ManagePortal)
    def listExportSteps(self):
        steps = set(self._export_registry.listSteps())
        if not self._exclude_global_steps:
            steps.update(set(_export_step_registry.listSteps()))
        return tuple(steps)

    @security.protected(ManagePortal)
    def listImportSteps(self):
        steps = set(self._import_registry.listSteps())
        if not self._exclude_global_steps:
            steps.update(set(_import_step_registry.listSteps()))
        return tuple(steps)

    @security.protected(ManagePortal)
    def getExportStepMetadata(self, step, default=None):
        """Simple wrapper to query both the global and local step registry."""
        res = self._export_registry.getStepMetadata(step, self)
        if res is self and not self._exclude_global_steps:
            res = _export_step_registry.getStepMetadata(step, default)
        if res is not self:
            return res
        return default

    @security.protected(ManagePortal)
    def getToolsetRegistry(self):
        """ See ISetupTool.
        """
        return self._toolset_registry

    @security.protected(ManagePortal)
    def runImportStepFromProfile(self, profile_id, step_id,
                                 run_dependencies=True, purge_old=None):
        """ See ISetupTool.
        """
        context = self._getImportContext(profile_id, purge_old)

        self.applyContext(context)

        info = self.getImportStepMetadata(step_id)

        if info is None:
            generic_logger.error(
                "No such import step: '%s' Maybe you meant one of %s",
                step_id, str(self.listImportSteps()))
            raise ValueError('No such import step: %s' % step_id)

        dependencies = info.get('dependencies', ())

        messages = {}
        steps = []

        if run_dependencies:
            for dependency in dependencies:
                if dependency not in steps:
                    steps.append(dependency)
        steps.append(step_id)

        full_import = (set(steps) == set(self.getSortedImportSteps()))
        event.notify(
            BeforeProfileImportEvent(self, profile_id, steps, full_import))

        for step in steps:
            message = self._doRunImportStep(step, context)
            messages[step] = message or ''

        message_list = [i for i in [message] if i]
        message_list.extend(['%s: %s' % x[1:] for x in context.listNotes()])
        messages[step_id] = '\n'.join(message_list)

        event.notify(
            ProfileImportedEvent(self, profile_id, steps, full_import))

        return {'steps': steps, 'messages': messages}

    @security.protected(ManagePortal)
    def runAllImportStepsFromProfile(self,
                                     profile_id,
                                     purge_old=None,
                                     ignore_dependencies=False,
                                     archive=None,
                                     blacklisted_steps=None,
                                     dependency_strategy=None):
        """ See ISetupTool.
        """
        __traceback_info__ = profile_id

        result = self._runImportStepsFromContext(
                            purge_old=purge_old,
                            profile_id=profile_id,
                            archive=archive,
                            ignore_dependencies=ignore_dependencies,
                            blacklisted_steps=blacklisted_steps,
                            dependency_strategy=dependency_strategy)
        if profile_id is None:
            prefix = 'import-all-from-tar'
        else:
            prefix = 'import-all-%s' % profile_id.replace(':', '_')
        name = self._mangleTimestampName(prefix, 'log')
        self._createReport(name, result['steps'], result['messages'])

        return result

    @security.protected(ManagePortal)
    def runExportStep(self, step_id):
        """ See ISetupTool.
        """
        return self._doRunExportSteps([step_id])

    @security.protected(ManagePortal)
    def runAllExportSteps(self):
        """ See ISetupTool.
        """
        return self._doRunExportSteps(self.listExportSteps())

    @security.protected(ManagePortal)
    def createSnapshot(self, snapshot_id):
        """ See ISetupTool.
        """
        context = SnapshotExportContext(self, snapshot_id)
        messages = {}
        steps = self.listExportSteps()

        for step_id in steps:

            handler = self.getExportStep(step_id)

            if handler is None:
                logger = logging.getLogger('GenericSetup')
                logger.error('Step %s has an invalid handler' % step_id)
                continue

            messages[step_id] = handler(context)

        return {'steps': steps,
                'messages': messages,
                'url': context.getSnapshotURL(),
                'snapshot': context.getSnapshotFolder()}

    @security.protected(ManagePortal)
    def compareConfigurations(self,
                              lhs_context,
                              rhs_context,
                              missing_as_empty=False,
                              ignore_blanks=False,
                              skip=SKIPPED_FILES):
        """ See ISetupTool.
        """
        differ = ConfigDiff(lhs_context,
                            rhs_context,
                            missing_as_empty,
                            ignore_blanks,
                            skip)

        return differ.compare()

    @security.protected(ManagePortal)
    def markupComparison(self, lines):
        """ See ISetupTool.
        """
        result = []

        for line in lines.splitlines():

            if line.startswith('** '):

                if line.find('File') > -1:
                    if line.find('replaced') > -1:
                        result.append(('file-to-dir', line))
                    elif line.find('added') > -1:
                        result.append(('file-added', line))
                    else:
                        result.append(('file-removed', line))
                else:
                    if line.find('replaced') > -1:
                        result.append(('dir-to-file', line))
                    elif line.find('added') > -1:
                        result.append(('dir-added', line))
                    else:
                        result.append(('dir-removed', line))

            elif line.startswith('@@'):
                result.append(('diff-range', line))

            elif line.startswith(' '):
                result.append(('diff-context', line))

            elif line.startswith('+'):
                result.append(('diff-added', line))

            elif line.startswith('-'):
                result.append(('diff-removed', line))

            elif line == r'\ No newline at end of file':
                result.append(('diff-context', line))

            else:
                result.append(('diff-header', line))

        return '<pre>\n%s\n</pre>' % (
            '\n'.join([('<span class="%s">%s</span>' % (cl, escape(l)))
                       for cl, l in result]))

    #
    #   ZMI
    #
    manage_options = (
        Folder.manage_options[:1] +
        ({'label': 'Profiles', 'action': 'manage_tool'},
         {'label': 'Import', 'action': 'manage_fullImport'},
         {'label': 'Export', 'action': 'manage_exportSteps'},
         {'label': 'Upgrades', 'action': 'manage_upgrades'},
         {'label': 'Advanced Import', 'action': 'manage_importSteps'},
         {'label': 'Tarball Import', 'action': 'manage_tarballImport'},
         {'label': 'Snapshots', 'action': 'manage_snapshots'},
         {'label': 'Comparison', 'action': 'manage_showDiff'},
         {'label': 'Manage', 'action': 'manage_stepRegistry'}) +
        Folder.manage_options[3:])  # skip "View", "Properties"

    security.declareProtected(ManagePortal, 'manage_tool')
    manage_tool = PageTemplateFile('sutProperties', _wwwdir)

    @security.protected(ManagePortal)
    def manage_updateToolProperties(self, context_id,
                                    exclude_global_steps=False,
                                    RESPONSE=None):
        """ Update the tool's settings.
        """
        self.setExcludeGlobalSteps(exclude_global_steps)
        self.setBaselineContext(context_id)

        if RESPONSE is not None:
            RESPONSE.redirect('%s/manage_tool?manage_tabs_message=%s' %
                              (self.absolute_url(), 'Properties+updated.'))

    security.declareProtected(ManagePortal, 'manage_importSteps')
    manage_importSteps = PageTemplateFile('sutImportSteps', _wwwdir)

    security.declareProtected(ManagePortal, 'manage_fullImport')
    manage_fullImport = PageTemplateFile(
        'sutFullImport', _wwwdir)

    security.declareProtected(ManagePortal, 'manage_tarballImport')
    manage_tarballImport = PageTemplateFile(
        'sutTarballImport', _wwwdir)

    @security.protected(ManagePortal)
    def manage_importSelectedSteps(self, ids, run_dependencies,
                                   context_id=None):
        """ Import the steps selected by the user.
        """
        messages = {}
        if not ids:
            summary = 'No steps selected.'

        else:
            if context_id is None:
                context_id = self.getBaselineContextID()
            steps_run = []
            for step_id in ids:
                result = self.runImportStepFromProfile(context_id,
                                                       step_id,
                                                       run_dependencies)
                steps_run.extend(result['steps'])
                messages.update(result['messages'])

            summary = 'Steps run: %s' % ', '.join(steps_run)

            name = self._mangleTimestampName('import-selected', 'log')
            self._createReport(name, result['steps'], result['messages'])

        return self.manage_importSteps(manage_tabs_message=summary,
                                       messages=messages)

    @security.protected(ManagePortal)
    def manage_importAllSteps(self, context_id=None, dependency_strategy=None):
        """ Import all steps.
        """
        if context_id is None:
            context_id = self.getBaselineContextID()
        result = self.runAllImportStepsFromProfile(
            context_id, purge_old=None,
            dependency_strategy=dependency_strategy)

        steps_run = 'Steps run: %s' % ', '.join(result['steps'])

        return self.manage_fullImport(manage_tabs_message=steps_run,
                                      messages=result['messages'])

    @security.protected(ManagePortal)
    def manage_importExtensions(self, RESPONSE, profile_ids=()):
        """ Import all steps for the selected extension profiles.
        """
        detail = {}
        if len(profile_ids) == 0:
            message = 'Please select one or more extension profiles.'
            RESPONSE.redirect('%s/manage_tool?manage_tabs_message=%s'
                              % (self.absolute_url(), message))
        else:
            message = 'Imported profiles: %s' % ', '.join(profile_ids)

            for profile_id in profile_ids:

                result = self.runAllImportStepsFromProfile(profile_id)

                for k, v in result['messages'].items():
                    detail['%s:%s' % (profile_id, k)] = v

            return self.manage_fullImport(manage_tabs_message=message,
                                          messages=detail)

    @security.protected(ManagePortal)
    def manage_importTarball(self, tarball, submitted=None, purge_old=None):
        """ Import steps from the uploaded tarball.
        """
        if getattr(tarball, 'read', None) is not None:
            tarball = tarball.read()

        if purge_old is None:
            if submitted:
                # The form was submitted, and the purge_old checkbox was not
                # checked, which means it does not end up in the method call.
                # So we must set it to False here.
                purge_old = False
            else:
                # No form was submitted: the method was called manually.
                # To avoid surprises, use the previous default.
                purge_old = True

        result = self.runAllImportStepsFromProfile(
            None, purge_old=purge_old, archive=tarball)

        steps_run = 'Steps run: %s' % ', '.join(result['steps'])

        return self.manage_tarballImport(manage_tabs_message=steps_run,
                                         messages=result['messages'])

    security.declareProtected(ManagePortal, 'manage_exportSteps')
    manage_exportSteps = PageTemplateFile('sutExportSteps', _wwwdir)

    @security.protected(ManagePortal)
    def manage_exportSelectedSteps(self, ids, RESPONSE):
        """ Export the steps selected by the user.
        """
        if not ids:
            RESPONSE.redirect('%s/manage_exportSteps?manage_tabs_message=%s'
                              % (self.absolute_url(), 'No+steps+selected.'))

        result = self._doRunExportSteps(ids)
        RESPONSE.setHeader('Content-type', 'application/x-gzip')
        RESPONSE.setHeader('Content-disposition',
                           'attachment; filename=%s' % result['filename'])
        return result['tarball']

    @security.protected(ManagePortal)
    def manage_exportAllSteps(self, RESPONSE):
        """ Export all steps.
        """
        result = self.runAllExportSteps()
        RESPONSE.setHeader('Content-type', 'application/x-gzip')
        RESPONSE.setHeader('Content-disposition',
                           'attachment; filename=%s' % result['filename'])
        return result['tarball']

    security.declareProtected(ManagePortal, 'manage_upgrades')
    manage_upgrades = PageTemplateFile('setup_upgrades', _wwwdir)

    security.declareProtected(ManagePortal, 'upgradeStepMacro')
    upgradeStepMacro = PageTemplateFile('upgradeStep', _wwwdir)

    security.declareProtected(ManagePortal, 'manage_snapshots')
    manage_snapshots = PageTemplateFile('sutSnapshots', _wwwdir)

    @security.protected(ManagePortal)
    def listSnapshotInfo(self):
        """ Return a list of mappings describing available snapshots.

        o Keys include:

          'id' -- snapshot ID

          'title' -- snapshot title or ID

          'url' -- URL of the snapshot folder
        """
        result = []
        snapshots = self._getOb('snapshots', None)

        if snapshots:
            for id, folder in snapshots.objectItems('Folder'):
                result.append({'id': id,
                               'title': folder.title_or_id(),
                               'url': folder.absolute_url()})
        return result

    @security.protected(ManagePortal)
    def listProfileInfo(self, for_=None):
        """ Return a list of mappings describing registered profiles.
        Base profile is listed first, extensions are sorted.

        o Keys include:

          'id' -- profile ID

          'title' -- profile title or ID

          'description' -- description of the profile

          'path' -- path to the profile within its product

          'product' -- name of the registering product
        """
        base = []
        ext = []
        for info in _profile_registry.listProfileInfo(for_):
            if info.get('type', BASE) == BASE:
                base.append(info)
            else:
                ext.append(info)
        ext.sort(key=lambda x: x['id'])
        return base + ext

    @security.protected(ManagePortal)
    def listContextInfos(self, order_by='sortable_title'):
        """ List registered profiles and snapshots.
        """
        def readableType(x):
            if x is BASE:
                return 'base'
            elif x is EXTENSION:
                return 'extension'
            return 'unknown'

        s_infos = [{
            'id': 'snapshot-%s' % info['id'],
            'sortable_id': info['id'].lower(),
            'title': info['title'],
            'sortable_title': info['title'].lower(),
            'type': 'snapshot',
            } for info in self.listSnapshotInfo()]
        s_infos.sort(key=itemgetter(order_by))
        p_infos = [{
            'id': 'profile-%s' % info['id'],
            'sortable_id': info['id'].lower(),
            'title': info['title'],
            'sortable_title': info['title'].lower(),
            'type': readableType(info['type']),
            } for info in self.listProfileInfo()]
        p_infos.sort(key=itemgetter(order_by))

        return tuple(s_infos + p_infos)

    @security.protected(ManagePortal)
    def getProfileImportDate(self, profile_id):
        """ See ISetupTool.
        """
        prefix = ('import-all-%s-' % profile_id).replace(':', '_')
        candidates = [x for x in self.objectIds('File')
                      if x[:-18] == prefix and x.endswith('.log')]
        if len(candidates) == 0:
            return None
        candidates.sort()
        last = candidates[-1]
        stamp = last[-18:-4]
        return '%s-%s-%sT%s:%s:%sZ' % (stamp[0:4],
                                       stamp[4:6],
                                       stamp[6:8],
                                       stamp[8:10],
                                       stamp[10:12],
                                       stamp[12:14])

    @security.protected(ManagePortal)
    def manage_createSnapshot(self, RESPONSE, snapshot_id=None):
        """ Create a snapshot with the given ID.

        o If no ID is passed, generate one.
        """
        if snapshot_id is None:
            snapshot_id = self._mangleTimestampName('snapshot')

        self.createSnapshot(snapshot_id)

        return RESPONSE.redirect('%s/manage_snapshots?manage_tabs_message=%s'
                                 % (self.absolute_url(), 'Snapshot+created.'))

    security.declareProtected(ManagePortal, 'manage_showDiff')
    manage_showDiff = PageTemplateFile('sutCompare', _wwwdir)

    def manage_downloadDiff(self,
                            lhs,
                            rhs,
                            missing_as_empty,
                            ignore_blanks,
                            RESPONSE):
        """ Crack request vars and call compareConfigurations.

        o Return the result as a 'text/plain' stream, suitable for framing.
        """
        comparison = self.manage_compareConfigurations(lhs,
                                                       rhs,
                                                       missing_as_empty,
                                                       ignore_blanks)
        RESPONSE.setHeader('Content-Type', 'text/plain')
        return _PLAINTEXT_DIFF_HEADER % (lhs, rhs, comparison)

    @security.protected(ManagePortal)
    def manage_compareConfigurations(self,
                                     lhs,
                                     rhs,
                                     missing_as_empty,
                                     ignore_blanks):
        """ Crack request vars and call compareConfigurations.
        """
        lhs_context = self._getImportContext(lhs)
        rhs_context = self._getImportContext(rhs)

        return self.compareConfigurations(lhs_context,
                                          rhs_context,
                                          missing_as_empty,
                                          ignore_blanks)

    security.declareProtected(ManagePortal, 'manage_stepRegistry')
    manage_stepRegistry = PageTemplateFile('sutManage', _wwwdir)

    @security.protected(ManagePortal)
    def manage_deleteImportSteps(self, ids, request=None):
        """ Delete selected import steps.
        """
        if request is None:
            request = self.REQUEST
        for id in ids:
            self._import_registry.unregisterStep(id)
        self._p_changed = True
        url = self.absolute_url()
        request.RESPONSE.redirect("%s/manage_stepRegistry" % url)

    @security.protected(ManagePortal)
    def manage_deleteExportSteps(self, ids, request=None):
        """ Delete selected export steps.
        """
        if request is None:
            request = self.REQUEST
        for id in ids:
            self._export_registry.unregisterStep(id)
        self._p_changed = True
        url = self.absolute_url()
        request.RESPONSE.redirect("%s/manage_stepRegistry" % url)

    #
    # Upgrades management
    #
    @security.protected(ManagePortal)
    def getLastVersionForProfile(self, profile_id):
        """Return the last upgraded version for the specified profile.
        """
        prefix = 'profile-'
        if profile_id.startswith(prefix):
            profile_id = profile_id[len(prefix):]
        version = self._profile_upgrade_versions.get(profile_id, UNKNOWN)
        return version

    @security.protected(ManagePortal)
    def setLastVersionForProfile(self, profile_id, version):
        """Set the last upgraded version for the specified profile.
        """
        if version == UNKNOWN:
            self.unsetLastVersionForProfile(profile_id)
            return
        prefix = 'profile-'
        if profile_id.startswith(prefix):
            profile_id = profile_id[len(prefix):]
        if isinstance(version, six.string_types):
            version = tuple(version.split('.'))
        if not isinstance(self._profile_upgrade_versions, PersistentMapping):
            # migrate to persistent
            self._profile_upgrade_versions = PersistentMapping(
                self._profile_upgrade_versions)
        self._profile_upgrade_versions[profile_id] = version

    @security.protected(ManagePortal)
    def unsetLastVersionForProfile(self, profile_id):
        """Unset the last upgraded version for the specified profile.
        """
        prefix = 'profile-'
        if profile_id.startswith(prefix):
            profile_id = profile_id[len(prefix):]
        if profile_id not in self._profile_upgrade_versions:
            return
        if not isinstance(self._profile_upgrade_versions, PersistentMapping):
            # migrate to persistent
            self._profile_upgrade_versions = PersistentMapping(
                self._profile_upgrade_versions)
        del self._profile_upgrade_versions[profile_id]

    @security.protected(ManagePortal)
    def getVersionForProfile(self, profile_id):
        """Return the registered filesystem version for the specified
        profile.
        """
        return self.getProfileInfo(profile_id).get('version', UNKNOWN)

    @security.protected(ManagePortal)
    def purgeProfileVersions(self):
        """Purge the profile upgrade versions.
        """
        self._profile_upgrade_versions = PersistentMapping()
        generic_logger.info('Profile upgrade versions purged.')

    @security.protected(ManagePortal)
    def profileExists(self, profile_id):
        """Check if a profile exists."""
        if profile_id is None:
            return False
        try:
            self.getProfileInfo(profile_id)
        except KeyError:
            return False
        else:
            return True

    @security.protected(ManagePortal)
    def profilesExist(self, profile_ids):
        """Check if all profiles exist."""
        for profile_id in profile_ids:
            if not self.profileExists(profile_id):
                return False
        return True

    @security.protected(ManagePortal)
    def getProfileInfo(self, profile_id):
        return _profile_registry.getProfileInfo(profile_id)

    @security.protected(ManagePortal)
    def getDependenciesForProfile(self, profile_id, ignore_broken=False):
        """
        If ignore_broken is True, return all referenced dependencies.
        Otherwise fail, if referenced dependency does not exist.
        """
        if profile_id is None:
            return ()
        if profile_id.startswith("snapshot-"):
            return ()

        profile_info = self.getProfileInfo(profile_id)

        dependencies = profile_info.get('dependencies', ())

        if not ignore_broken:

            for dependency_id in dependencies:

                if not self.profileExists(dependency_id):

                    raise KeyError(
                        'Profile "%s" requires the'
                        ' dependency-profile "%s", which does not exist.'
                        % (profile_id, dependency_id))

        return dependencies

    @security.protected(ManagePortal)
    def getBrokenDependencies(self, profile_id):
        """Return referenced dependency-ids, which do not exist."""
        broken_dependencies = []
        dependency_ids = self.getDependenciesForProfile(
            profile_id, ignore_broken=True)
        for dependency_id in dependency_ids:
            if not self.profileExists(dependency_id):
                broken_dependencies.append(dependency_id)
        return broken_dependencies

    @security.protected(ManagePortal)
    def hasBrokenDependencies(self, profile_id):
        return len(self.getBrokenDependencies(profile_id)) > 0

    @security.protected(ManagePortal)
    def listProfilesWithUpgrades(self):
        profiles = listProfilesWithUpgrades()
        profiles.sort()
        return profiles

    @security.private
    def _massageUpgradeInfo(self, info):
        """Add a couple of data points to the upgrade info dictionary.
        """
        info = info.copy()
        info['haspath'] = info['source'] and info['dest']
        info['ssource'] = '.'.join(info['source'] or ('all',))
        info['sdest'] = '.'.join(info['dest'] or ('all',))
        info['done'] = (not info['proposed'] and
                        info['step'].checker is not None and
                        not info['step'].checker(self))
        return info

    @security.protected(ManagePortal)
    def listUpgrades(self, profile_id, show_old=False):
        """Get the list of available upgrades.
        """
        if show_old:
            source = None
        else:
            source = self.getLastVersionForProfile(profile_id)
        upgrades = listUpgradeSteps(self, profile_id, source)
        res = []
        for info in upgrades:
            if type(info) == list:
                subset = []
                for subinfo in info:
                    subset.append(self._massageUpgradeInfo(subinfo))
                res.append(subset)
            else:
                res.append(self._massageUpgradeInfo(info))
        return res

    @security.protected(ManagePortal)
    def hasPendingUpgrades(self, profile_id=None):
        """Are upgrade steps pending?

        Pending means: a not yet applied upgrade step for an already
        applied profile.

        With a profile_id, we only check the given profile.

        Without a profile_id, we check if there is any profile at all
        that has an upgrade available.
        """
        if profile_id is not None:
            profile_ids = [profile_id]
        else:
            profile_ids = self.listProfilesWithUpgrades()
        for profile_id in profile_ids:
            if self.getLastVersionForProfile(profile_id) == UNKNOWN:
                # We are not interested in profiles that have never been
                # applied.
                continue
            if self.listUpgrades(profile_id):
                return True
        return False

    @security.protected(ManagePortal)
    def listProfilesWithPendingUpgrades(self):
        """List profile ids with pending upgrade steps.

        Pending means: a not yet applied upgrade step for an already
        applied profile.
        """
        res = []
        for profile_id in self.listProfilesWithUpgrades():
            if self.getLastVersionForProfile(profile_id) == UNKNOWN:
                # We are not interested in profiles that have never been
                # applied.
                continue
            if self.listUpgrades(profile_id):
                res.append(profile_id)
        return res

    @security.protected(ManagePortal)
    def listUptodateProfiles(self):
        """List profile ids without pending upgrade steps.

        Pending means: a not yet applied upgrade step for an already
        applied profile.

        We ignore profiles that have no upgrade steps at all.
        """
        res = []
        for profile_id in self.listProfilesWithUpgrades():
            if self.getLastVersionForProfile(profile_id) == UNKNOWN:
                # We are not interested in profiles that have never been
                # applied.
                continue
            if not self.listUpgrades(profile_id):
                res.append(profile_id)
        return res

    @security.protected(ManagePortal)
    def manage_doUpgrades(self, request=None):
        """Perform all selected upgrade steps.
        """
        if request is None:
            request = self.REQUEST
        logger = logging.getLogger('GenericSetup')
        steps_to_run = request.form.get('upgrades', [])
        profile_id = request.get('profile_id', '')
        step = None
        for step_id in steps_to_run:
            step = _upgrade_registry.getUpgradeStep(profile_id, step_id)
            if step is not None:
                step.doStep(self)
                msg = "Ran upgrade step %s for profile %s" % (step.title,
                                                              profile_id)
                logger.log(logging.INFO, msg)

        # We update the profile version to the last one we have reached
        # with running an upgrade step.
        if step and step.dest is not None:
            self.setLastVersionForProfile(profile_id, step.dest)

        url = self.absolute_url()
        request.RESPONSE.redirect("%s/manage_upgrades?saved=%s"
                                  % (url, profile_id))

    @security.protected(ManagePortal)
    def upgradeProfile(self, profile_id, dest=None):
        """Upgrade a profile.

        Apply all upgrade steps.

        When 'dest' is given, only update to that version.  If the
        version is not found, give a warning and do nothing.

        If the profile was not applied previously (last version for
        profile is unknown) we do nothing.
        """
        if self.getLastVersionForProfile(profile_id) == UNKNOWN:
            generic_logger.warning('Version of profile %s is unknown, '
                                   'refusing to upgrade.', profile_id)
            return
        if dest is not None:
            # Upgrade to a specific destination version, if found.
            if isinstance(dest, six.string_types):
                dest = tuple(dest.split('.'))
            if self.getLastVersionForProfile(profile_id) == dest:
                generic_logger.warning('Profile %s is already at wanted '
                                       'destination %r.', profile_id, dest)
                return
        upgrades = self.listUpgrades(profile_id)
        # First get a list of single steps to apply.  This may be
        # limited by the wanted destination version.
        to_apply = []
        dest_found = False
        step = None
        for upgrade in upgrades:
            # An upgrade may be a single step (for a bare upgradeStep)
            # or a list of steps (for upgradeSteps containing upgradeStep
            # directives).
            if not isinstance(upgrade, list):
                upgrade = [upgrade]
            for upgradestep in upgrade:
                step = upgradestep['step']
                to_apply.append(step)
                if dest is not None and step.dest == dest:
                    dest_found = True
            if dest_found:
                break
        if dest is not None and not dest_found:
            generic_logger.warning(
                'No route found to destination version %r for profile %s. '
                'Profile stays at current version, %r', dest, profile_id,
                self.getLastVersionForProfile(profile_id))
            return
        if to_apply:
            for step in to_apply:
                step.doStep(self)
            # We update the profile version to the last one we have
            # reached with running an upgrade step.
            if step and step.dest is not None:
                self.setLastVersionForProfile(profile_id, step.dest)
                generic_logger.info(
                    'Profile %s upgraded to version %r.',
                    profile_id, self.getLastVersionForProfile(profile_id))
        else:
            generic_logger.info(
                'No upgrades available for profile %s. '
                'Profile stays at version %r.', profile_id,
                self.getLastVersionForProfile(profile_id))

    #
    #   Helper methods
    #
    @security.private
    def _getImportContext(self, context_id, should_purge=None, archive=None):
        """ Crack ID and generate appropriate import context.

        Note: it seems context_id (profile id) and archive (tarball)
        are mutually exclusive.  Exactly one of the two should be
        None.  There seems to be no use case for a different
        combination.
        """
        encoding = self.getEncoding()

        if context_id is not None:
            prefix = 'snapshot-'
            if context_id.startswith(prefix):
                context_id = context_id[len(prefix):]
                if should_purge is None:
                    should_purge = True
                return SnapshotImportContext(self, context_id, should_purge,
                                             encoding)
            prefix = 'profile-'
            if context_id.startswith(prefix):
                context_id = context_id[len(prefix):]
            info = _profile_registry.getProfileInfo(context_id)
            if info.get('product'):
                path = os.path.join(_getProductPath(info['product']),
                                    info['path'])
            else:
                path = info['path']
            if should_purge is None:
                should_purge = (info.get('type') != EXTENSION)
            return DirectoryImportContext(self, path, should_purge,
                                          encoding)

        if archive is not None:
            return TarballImportContext(tool=self,
                                        archive_bits=archive,
                                        encoding='UTF8',
                                        should_purge=should_purge)

        raise KeyError('Unknown context "%s"' % context_id)

    @security.private
    def _updateImportStepsRegistry(self, context, encoding):
        """ Update our import steps registry from our profile.
        """
        xml = context.readDataFile(IMPORT_STEPS_XML)
        if xml is None:
            return

        info_list = self._import_registry.parseXML(xml, encoding)

        for step_info in info_list:

            id = step_info['id']
            version = step_info.get('version')
            handler = step_info['handler']
            dependencies = tuple(step_info.get('dependencies', ()))
            title = step_info.get('title', id)
            description = ''.join(step_info.get('description', []))

            self._import_registry.registerStep(id=id,
                                               version=version,
                                               handler=handler,
                                               dependencies=dependencies,
                                               title=title,
                                               description=description)

    @security.private
    def _updateExportStepsRegistry(self, context, encoding):
        """ Update our export steps registry from our profile.
        """
        xml = context.readDataFile(EXPORT_STEPS_XML)
        if xml is None:
            return

        info_list = self._export_registry.parseXML(xml, encoding)

        for step_info in info_list:

            id = step_info['id']
            handler = step_info['handler']
            title = step_info.get('title', id)
            description = ''.join(step_info.get('description', []))

            self._export_registry.registerStep(id=id,
                                               handler=handler,
                                               title=title,
                                               description=description)

    @security.private
    def _doRunImportStep(self, step_id, context):
        """ Run a single import step, using a pre-built context.
        """
        __traceback_info__ = step_id
        marker = object()

        handler = self.getImportStep(step_id)

        if handler is marker:
            raise ValueError('Invalid import step: %s' % step_id)

        if handler is None:
            msg = 'Step %s has an invalid import handler' % step_id
            logger = logging.getLogger('GenericSetup')
            logger.error(msg)
            return 'ERROR: ' + msg

        return handler(context)

    @security.private
    def _doRunExportSteps(self, steps):
        """ See ISetupTool.
        """
        context = TarballExportContext(self)
        messages = {}
        marker = object()

        for step_id in steps:

            handler = self.getExportStep(step_id, marker)

            if handler is marker:
                raise ValueError('Invalid export step: %s' % step_id)

            if handler is None:
                msg = 'Step %s has an invalid export handler' % step_id
                logger = logging.getLogger('GenericSetup')
                logger.error(msg)
                messages[step_id] = msg
            else:
                messages[step_id] = handler(context)

        return {'steps': steps,
                'messages': messages,
                'tarball': context.getArchive(),
                'filename': context.getArchiveFilename()}

    @security.private
    def _doRunHandler(self, handler):
        """Run a single handler.

        This is expected to be a function or a dotted name of a
        pre_handler or post_handler of a profile.  It is passed the tool
        as context.
        """
        if isinstance(handler, types.FunctionType):
            handler_function = handler
        else:
            handler_function = _resolveDottedName(handler)
            if handler_function is None:
                raise ValueError('Invalid handler: %s' % handler)
        return handler_function(self)

    @security.protected(ManagePortal)
    def getProfileDependencyChain(self, profile_id, seen=None):
        if seen is None:
            seen = set()
        elif profile_id in seen:
            return []  # cycle break
        seen.add(profile_id)
        chain = []

        dependencies = self.getDependenciesForProfile(profile_id)
        for dependency in dependencies:
            chain.extend(self.getProfileDependencyChain(dependency, seen))

        chain.append(profile_id)

        return chain

    @security.private
    def _runImportStepsFromContext(self,
                                   steps=None,
                                   purge_old=None,
                                   profile_id=None,
                                   archive=None,
                                   ignore_dependencies=False,
                                   blacklisted_steps=None,
                                   dependency_strategy=None):

        # 1. Determine upgrade strategy.
        #    What do we do with already applied dependency profiles?

        # There are two ways to say you want to ignore all
        # dependencies.  If one is enabled, we enable the other too.
        if dependency_strategy == DEPENDENCY_STRATEGY_IGNORE:
            ignore_dependencies = True
        elif ignore_dependencies:
            dependency_strategy = DEPENDENCY_STRATEGY_IGNORE
        # Turn None into the default:
        if dependency_strategy is None:
            dependency_strategy = DEFAULT_DEPENDENCY_STRATEGY
        # Determine the settings based on the strategy.
        if dependency_strategy == DEPENDENCY_STRATEGY_UPGRADE:
            apply_new_profiles = True
            reapply_old_profiles = False
            upgrade_old_profiles = True
        elif dependency_strategy == DEPENDENCY_STRATEGY_REAPPLY:
            apply_new_profiles = True
            reapply_old_profiles = True
            upgrade_old_profiles = False
        elif dependency_strategy == DEPENDENCY_STRATEGY_NEW:
            apply_new_profiles = True
            reapply_old_profiles = False
            upgrade_old_profiles = False
        elif dependency_strategy == DEPENDENCY_STRATEGY_IGNORE:
            apply_new_profiles = False
            reapply_old_profiles = False
            upgrade_old_profiles = False
        else:
            raise ValueError('Unknown dependency_strategy %r.' %
                             dependency_strategy)
        generic_logger.info(
            'Importing profile %s with dependency strategy %s.',
            profile_id, dependency_strategy)

        # 2. Gather a list of profiles to handle.

        if profile_id is not None and not ignore_dependencies:
            try:
                chain = self.getProfileDependencyChain(profile_id)
            except KeyError as e:
                logger = logging.getLogger('GenericSetup')
                logger.error('Unknown step in dependency chain: %s' % str(e))
                raise
        else:
            # Two possibilities:
            # - We ignore dependencies, so we have a single profile id.
            # - Profile id is None and we import a tarball (in the archive).
            chain = [profile_id]

        # 3. For each profile, depending on the keyword arguments, either:
        # a. do nothing or
        # b. apply its upgrade steps or
        # c. apply its full profile.

        results = []
        detect_steps = steps is None

        # The chain is: first all dependency profiles ( recursively if
        # applicable), and as last one the main profile for which we
        # got passed the profile_id.
        last_num = len(chain)
        for num, profile_id in enumerate(chain, 1):
            try:
                profile_info = self.getProfileInfo(profile_id)
            except KeyError:
                # this will be a snapshot profile
                profile_info = {}
                profile_type = None
            else:
                profile_type = profile_info.get('type')
            if num == last_num:
                generic_logger.info('Applying main profile %s', profile_id)
            else:
                # This is a dependency profile.  This means we are not
                # completely ignoring them, otherwise it would not
                # have ended up in the list.  Check if it was already
                # applied.
                if self.getLastVersionForProfile(profile_id) == UNKNOWN:
                    # This is a new profile.
                    if not apply_new_profiles:
                        continue
                    generic_logger.info('Applying profile %s', profile_id)
                else:
                    # Profile was already applied.
                    if upgrade_old_profiles:
                        self.upgradeProfile(profile_id)
                        continue
                    if not reapply_old_profiles:
                        continue
                    generic_logger.info('Reapplying profile %s', profile_id)
            # The next lines are done at least for the main profile.
            # Possibly also for dependency profiles, depending on the
            # condition above.  It applies the profile.
            context = self._getImportContext(profile_id, purge_old, archive)
            self.applyContext(context)
            if detect_steps:
                steps = self.getSortedImportSteps()
            messages = {}
            event.notify(
                BeforeProfileImportEvent(self, profile_id, steps, True))
            # Maybe purge all profile upgrade versions.
            if profile_type == BASE and (purge_old is None or purge_old):
                # purge_old should be None or explicitly true
                self.purgeProfileVersions()
            # Run optional pre_handler if available.
            pre_handler = profile_info.get('pre_handler')
            if pre_handler:
                self._doRunHandler(pre_handler)
            # Run all import steps.
            for step in steps:
                if blacklisted_steps and step in blacklisted_steps:
                    message = 'step skipped'
                else:
                    message = self._doRunImportStep(step, context)
                message_list = [i for i in [message] if i]
                message_list.extend(['%s: %s' % x[1:]
                                     for x in context.listNotes()])
                messages[step] = '\n'.join(message_list)
                context.clearNotes()
            # Run optional post_handler if available.
            post_handler = profile_info.get('post_handler')
            if post_handler:
                self._doRunHandler(post_handler)
            event.notify(ProfileImportedEvent(self, profile_id, steps, True))
            messages[profile_id] = (
                'Imported with dependency strategy %s.' % dependency_strategy)
            results.append({'steps': steps, 'messages': messages})

        # 4. Gather data for reporting back.

        data = {'steps': [], 'messages': {}}
        for result in results:
            for step in result['steps']:
                if step not in data['steps']:
                    data['steps'].append(step)

            for (step, msg) in result['messages'].items():
                if step in data['messages']:
                    data['messages'][step] += "\n" + msg
                else:
                    data['messages'][step] = msg
        data['steps'] = list(data['steps'])

        return data

    @security.private
    def _mangleTimestampName(self, prefix, ext=None):
        """ Create a mangled ID using a timestamp.
        """
        timestamp = time.gmtime()
        items = (prefix,) + timestamp[:6]

        if ext is None:
            fmt = '%s-%4d%02d%02d%02d%02d%02d'
        else:
            fmt = '%s-%4d%02d%02d%02d%02d%02d.%s'
            items += (ext,)

        return fmt % items

    @security.private
    def _createReport(self, basename, steps, messages):
        """ Record the results of a run.
        """
        lines = []
        # Create report
        for step in steps:
            lines.append('=' * 65)
            lines.append('Step: %s' % step)
            lines.append('=' * 65)
            msg = messages[step]
            lines.extend(msg.split('\n'))
            lines.append('')

        report = '\n'.join(lines)
        if isinstance(report, six.text_type):
            report = report.encode('latin-1')

        # BBB: ObjectManager won't allow unicode IDS
        if isinstance(basename, six.text_type) and six.PY2:
            basename = basename.encode('UTF-8')

        name = basename
        index = 0
        while name in self:
            index += 1
            name = basename + '_%i' % index

        file = File(id=name,
                    title='',
                    file=report,
                    content_type='text/plain')

        self._setObject(name, file)


InitializeClass(SetupTool)


_PLAINTEXT_DIFF_HEADER = """\
Comparing configurations: '%s' and '%s'

%s"""

_TOOL_ID = 'setup_tool'

addSetupToolForm = PageTemplateFile('toolAdd.zpt', _wwwdir)


def addSetupTool(dispatcher, RESPONSE):
    """
    """
    dispatcher._setObject(_TOOL_ID, SetupTool(_TOOL_ID))

    RESPONSE.redirect('%s/manage_main' % dispatcher.absolute_url())
