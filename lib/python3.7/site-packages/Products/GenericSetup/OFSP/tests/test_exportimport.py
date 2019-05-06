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
"""OFSP export / import support unit tests.
"""

import unittest

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import ExportImportZCMLLayer
from Products.GenericSetup.testing import DummySetupEnviron
from zope.component import getMultiAdapter

_FOLDER_BODY = b"""\
<?xml version="1.0" encoding="utf-8"?>
<object name="foo_folder" meta_type="Folder">
 <property name="title">Foo</property>
</object>
"""


class FolderXMLAdapterTests(BodyAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.OFSP.exportimport import FolderXMLAdapter

        return FolderXMLAdapter

    def _populate(self, obj):
        obj._setPropValue('title', 'Foo')

    def _verifyImport(self, obj):
        self.assertEqual(type(obj.title), str)
        self.assertEqual(obj.title, 'Foo')

    def setUp(self):
        from OFS.Folder import Folder

        self._obj = Folder('foo_folder')
        self._BODY = _FOLDER_BODY

    def test_body_set_without_encoding(self):
        context = DummySetupEnviron()
        adapted = getMultiAdapter((self._obj, context), IBody)
        adapted.body = self._BODY.replace(b'encoding="utf-8"', b'')
        self._verifyImport(self._obj)
        self.assertEqual(adapted.body, self._BODY)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FolderXMLAdapterTests),
        ))
