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
"""Node adapter testing utils.
"""

import six

from Testing.ZopeTestCase.layer import ZopeLite

from xml.dom.minidom import parseString

from OFS.interfaces import IItem
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface.verify import verifyClass
from zope.testing.cleanup import cleanUp

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import ISetupEnviron


class DummyLogger:

    def __init__(self, id, messages):
        self._id = id
        self._messages = messages

    def info(self, msg, *args, **kwargs):
        self._messages.append((20, self._id, msg))

    def warning(self, msg, *args, **kwargs):
        self._messages.append((30, self._id, msg))


@implementer(ISetupEnviron)
class DummySetupEnviron(object):

    """Context for body im- and exporter.
    """

    def __init__(self):
        self._notes = []
        self._should_purge = True

    def getLogger(self, name):
        return DummyLogger(name, self._notes)

    def shouldPurge(self):
        return self._should_purge


class IDummyMarker(IItem):

    pass


class _AdapterTestCaseBase:

    def _populate(self, obj):
        pass

    def _verifyImport(self, obj):
        pass


class BodyAdapterTestCase(_AdapterTestCaseBase):

    def test_z3interfaces(self):
        verifyClass(IBody, self._getTargetClass())

    def test_body_get(self):
        self._populate(self._obj)
        context = DummySetupEnviron()
        adapted = getMultiAdapter((self._obj, context), IBody)
        self.assertEqual(adapted.body, self._BODY)
        self.assertTrue(isinstance(adapted.body, six.binary_type))

    def test_body_set(self):
        context = DummySetupEnviron()
        adapted = getMultiAdapter((self._obj, context), IBody)
        adapted.body = self._BODY
        self._verifyImport(self._obj)
        self.assertEqual(adapted.body, self._BODY)

        # now in update mode
        context._should_purge = False
        adapted = getMultiAdapter((self._obj, context), IBody)
        adapted.body = self._BODY
        self._verifyImport(self._obj)
        self.assertEqual(adapted.body, self._BODY)

        # and again in update mode
        adapted = getMultiAdapter((self._obj, context), IBody)
        adapted.body = self._BODY
        self._verifyImport(self._obj)
        self.assertEqual(adapted.body, self._BODY)


class NodeAdapterTestCase(_AdapterTestCaseBase):

    def test_z3interfaces(self):
        verifyClass(INode, self._getTargetClass())

    def test_node_get(self):
        self._populate(self._obj)
        context = DummySetupEnviron()
        adapted = getMultiAdapter((self._obj, context), INode)
        self.assertEqual(adapted.node.toprettyxml(' ', encoding='utf-8'),
                         self._XML)

    def test_node_set(self):
        context = DummySetupEnviron()
        adapted = getMultiAdapter((self._obj, context), INode)
        adapted.node = parseString(self._XML).documentElement
        self._verifyImport(self._obj)
        self.assertEqual(adapted.node.toprettyxml(' ', encoding='utf-8'),
                         self._XML)

        # now in update mode
        context._should_purge = False
        adapted = getMultiAdapter((self._obj, context), INode)
        adapted.node = parseString(self._XML).documentElement
        self._verifyImport(self._obj)
        self.assertEqual(adapted.node.toprettyxml(' ', encoding='utf-8'),
                         self._XML)

        # and again in update mode
        adapted = getMultiAdapter((self._obj, context), INode)
        adapted.node = parseString(self._XML).documentElement
        self._verifyImport(self._obj)
        self.assertEqual(adapted.node.toprettyxml(' ', encoding='utf-8'),
                         self._XML)


class ExportImportZCMLLayer(ZopeLite):

    @classmethod
    def setUp(cls):
        import Zope2.App
        import AccessControl
        import Products.Five
        import Products.GenericSetup
        import zope.traversing
        from Zope2.App import zcml

        zcml.load_config('meta.zcml', Zope2.App)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('meta.zcml', Products.GenericSetup)
        zcml.load_config('permissions.zcml', AccessControl)
        zcml.load_config('configure.zcml', zope.traversing)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.GenericSetup)

    @classmethod
    def tearDown(cls):
        cleanUp()
