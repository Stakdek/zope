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
"""PluginIndexes export / import support.
"""

from zope.component import adapts
from zope.component import queryMultiAdapter

from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import NodeAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers

from Products.PluginIndexes.interfaces import IDateIndex
from Products.PluginIndexes.interfaces import IDateRangeIndex
from Products.PluginIndexes.interfaces import IFilteredSet
from Products.PluginIndexes.interfaces import IPathIndex
from Products.PluginIndexes.interfaces import IPluggableIndex
from Products.PluginIndexes.interfaces import ITopicIndex


class PluggableIndexNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for FieldIndex, KeywordIndex.
    """

    adapts(IPluggableIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('index')
        for value in self.context.getIndexSourceNames():
            child = self._doc.createElement('indexed_attr')
            child.setAttribute('value', value)
            node.appendChild(child)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        indexed_attrs = []
        _before = getattr(self.context, 'indexed_attrs', [])
        for child in node.childNodes:
            if child.nodeName == 'indexed_attr':
                indexed_attrs.append(
                                  child.getAttribute('value'))
        if _before != indexed_attrs:
            self.context.indexed_attrs = indexed_attrs
            self.context.clear()

    node = property(_exportNode, _importNode)


class DateIndexNodeAdapter(NodeAdapterBase, PropertyManagerHelpers):

    """Node im- and exporter for DateIndex.
    """

    adapts(IDateIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('index')
        node.appendChild(self._extractProperties())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        _before = {'map': self.context._properties,
                   'items': self.context.propertyItems()}
        if self.environ.shouldPurge():
            self._purgeProperties()

        self._initProperties(node)
        _after = {'map': self.context._properties,
                  'items': self.context.propertyItems()}
        if _before != _after:
            self.context.clear()

    node = property(_exportNode, _importNode)


class DateRangeIndexNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for DateRangeIndex.
    """

    adapts(IDateRangeIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('index')
        node.setAttribute('since_field', self.context.getSinceField())
        node.setAttribute('until_field', self.context.getUntilField())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        _before = (self.context._since_field, self.context._until_field)
        self.context._edit(node.getAttribute('since_field'),
                           node.getAttribute('until_field'))
        _after = (self.context._since_field, self.context._until_field)
        if _before != _after:
            self.context.clear()

    node = property(_exportNode, _importNode)


class PathIndexNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for PathIndex.
    """

    adapts(IPathIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        return self._getObjectNode('index')

    node = property(_exportNode, lambda self, val: None)


class FilteredSetNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for FilteredSet.
    """

    adapts(IFilteredSet, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('filtered_set')
        node.setAttribute('expression', self.context.getExpression())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        _before = self.context.expr
        self.context.setExpression(
                              node.getAttribute('expression'))
        _after = self.context.expr
        if _before != _after:
            self.context.clear()

    node = property(_exportNode, _importNode)


class TopicIndexNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for TopicIndex.
    """

    adapts(ITopicIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('index')
        for set in self.context.filteredSets.values():
            exporter = queryMultiAdapter((set, self.environ), INode)
            node.appendChild(exporter.node)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        for child in node.childNodes:
            if child.nodeName == 'filtered_set':
                set_id = str(child.getAttribute('name'))
                if set_id not in self.context.filteredSets:
                    set_meta_type = str(child.getAttribute('meta_type'))
                    self.context.addFilteredSet(set_id, set_meta_type, '')
                set = self.context.filteredSets[set_id]
                importer = queryMultiAdapter((set, self.environ), INode)
                importer.node = child
        # Let the filtered sets handle themselves:  we have no state
        # self.context.clear()

    node = property(_exportNode, _importNode)
