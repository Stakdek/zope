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
"""ZCatalog export / import support.
"""

from zope.component import adapts
from zope.component import queryMultiAdapter

from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.ZCatalog.interfaces import IZCatalog


class _extra:

    pass


class ZCatalogXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                         PropertyManagerHelpers):

    """XML im- and exporter for ZCatalog.
    """

    adapts(IZCatalog, ISetupEnviron)

    _LOGGER_ID = 'catalog'

    name = 'catalog'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())
        node.appendChild(self._extractIndexes())
        node.appendChild(self._extractColumns())

        self._logger.info('Catalog exported.')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeObjects()
            self._purgeIndexes()
            self._purgeColumns()

        self._initProperties(node)
        self._initObjects(node)
        self._initIndexes(node)
        self._initColumns(node)

        self._logger.info('Catalog imported.')

    def _extractIndexes(self):
        fragment = self._doc.createDocumentFragment()
        indexes = self.context.getIndexObjects()[:]
        indexes.sort(key=lambda x: x.getId())
        for idx in indexes:
            exporter = queryMultiAdapter((idx, self.environ), INode)
            if exporter:
                fragment.appendChild(exporter.node)
        return fragment

    def _purgeIndexes(self):
        indexes = set(self.context.indexes())
        for idx_id in indexes:
            self.context.delIndex(idx_id)

    def _initIndexes(self, node):
        for child in node.childNodes:
            if child.nodeName != 'index':
                continue
            if child.hasAttribute('deprecated'):
                continue
            zcatalog = self.context

            idx_id = str(child.getAttribute('name'))
            if child.hasAttribute('remove'):
                # Remove index if it is there; then continue to the next
                # index.  Removing a non existing index should not cause an
                # error, so you can apply the profile twice without problems.
                if idx_id in zcatalog.indexes():
                    zcatalog.delIndex(idx_id)
                continue

            if idx_id not in zcatalog.indexes():
                extra = _extra()
                for sub in child.childNodes:
                    if sub.nodeName == 'extra':
                        name = str(sub.getAttribute('name'))
                        value = str(sub.getAttribute('value'))
                        setattr(extra, name, value)
                extra = extra.__dict__ and extra or None

                meta_type = str(child.getAttribute('meta_type'))
                zcatalog.addIndex(idx_id, meta_type, extra)

            idx = zcatalog._catalog.getIndex(idx_id)
            importer = queryMultiAdapter((idx, self.environ), INode)
            if importer:
                importer.node = child

    def _extractColumns(self):
        fragment = self._doc.createDocumentFragment()
        schema = sorted(self.context.schema())
        for col in schema:
            child = self._doc.createElement('column')
            child.setAttribute('value', col)
            fragment.appendChild(child)
        return fragment

    def _purgeColumns(self):
        for col in list(self.context.schema()):
            self.context.delColumn(col)

    def _initColumns(self, node):
        for child in node.childNodes:
            if child.nodeName != 'column':
                continue
            col = str(child.getAttribute('value'))
            if child.hasAttribute('remove'):
                # Remove the column if it is there
                if col in list(self.context.schema()):
                    self.context.delColumn(col)
                continue
            if col not in list(self.context.schema()):
                self.context.addColumn(col)
