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
"""PythonScript export / import support unit tests.
"""

import six
import unittest

from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import ExportImportZCMLLayer

_PYTHONSCRIPT_BODY = b"""\
## Script (Python) "foo_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
"""


class PythonScriptBodyAdapterTests(BodyAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.PythonScripts.exportimport \
                import PythonScriptBodyAdapter

        return PythonScriptBodyAdapter

    def setUp(self):
        from Products.PythonScripts.PythonScript import PythonScript

        self._obj = PythonScript('foo_script')
        self._BODY = _PYTHONSCRIPT_BODY

    def _verifyImport(self, obj):
        # Imported script body should be a native string
        expected = _PYTHONSCRIPT_BODY
        if six.PY3:
            expected = _PYTHONSCRIPT_BODY.decode('utf-8')
        self.assertEqual(obj.read(), expected)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PythonScriptBodyAdapterTests),
        ))
