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
"""PageTemplate export / import support unit tests.
"""

import unittest

from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import ExportImportZCMLLayer

_PAGETEMPLATE_BODY = b"""\
<html>
  <div>Foo</div>
</html>
"""


class ZopePageTemplateBodyAdapterTests(BodyAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.PageTemplates.exportimport \
                import ZopePageTemplateBodyAdapter

        return ZopePageTemplateBodyAdapter

    def _populate(self, obj):
        obj.write(_PAGETEMPLATE_BODY)

    def setUp(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

        self._obj = ZopePageTemplate('foo_template')
        self._BODY = _PAGETEMPLATE_BODY


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZopePageTemplateBodyAdapterTests),
        ))
