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
"""MailHost export / import support unit tests.
"""

import unittest


try:
    from Products.GenericSetup.testing import BodyAdapterTestCase
    from Products.GenericSetup.testing import ExportImportZCMLLayer
    HAVE_GS = True
except ImportError:
    HAVE_GS = False
    class BodyAdapterTestCase: pass  # noqa
    class ExportImportZCMLLayer: pass  # noqa

_MAILHOST_BODY = b"""\
<?xml version="1.0" encoding="utf-8"?>
<object name="foo_mailhost" meta_type="Mail Host" smtp_host="localhost"
   smtp_port="25" smtp_pwd="" smtp_queue="False" smtp_queue_directory="/tmp"
   smtp_uid=""/>
"""

_MAILHOST_BODY_v2 = b"""\
<?xml version="1.0" encoding="utf-8"?>
<object name="foo_mailhost" meta_type="Mail Host" smtp_host="localhost"
   smtp_port="25" smtp_pwd="" smtp_queue="True"
   smtp_queue_directory="/tmp/mailqueue" smtp_uid=""/>
"""


@unittest.skipUnless(HAVE_GS, 'Products.GenericSetup not available.')
class MailHostXMLAdapterTests(BodyAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.MailHost.exportimport import MailHostXMLAdapter

        return MailHostXMLAdapter

    def _verifyImport(self, obj):
        self.assertEqual(obj.smtp_host, 'localhost')
        self.assertEqual(obj.smtp_port, 25)
        self.assertEqual(obj.smtp_pwd, '')
        self.assertEqual(obj.smtp_uid, '')
        self.assertEqual(obj.smtp_queue, False)
        self.assertEqual(obj.smtp_queue_directory, '/tmp')

    def setUp(self):
        from Products.MailHost.MailHost import MailHost

        self._obj = MailHost('foo_mailhost')
        self._BODY = _MAILHOST_BODY


@unittest.skipUnless(HAVE_GS, 'Products.GenericSetup not available.')
class MailHostXMLAdapterTestsWithoutQueue(MailHostXMLAdapterTests):

    def _verifyImport(self, obj):
        self.assertFalse('smtp_queue' in obj.__dict__)
        self.assertFalse('smtp_queue_directory' in obj.__dict__)

    def setUp(self):
        from Products.MailHost.MailHost import MailHost

        mh = self._obj = MailHost('foo_mailhost')
        del mh.smtp_queue
        del mh.smtp_queue_directory
        self._BODY = _MAILHOST_BODY


@unittest.skipUnless(HAVE_GS, 'Products.GenericSetup not available.')
class MailHostXMLAdapterTestsWithQueue(BodyAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.MailHost.exportimport import MailHostXMLAdapter

        return MailHostXMLAdapter

    def _verifyImport(self, obj):
        self.assertEqual(obj.smtp_queue, True)
        self.assertEqual(obj.smtp_queue_directory, '/tmp/mailqueue')

    def test_body_get(self):
        # Default Correctly Handled in MailHostXMLAdapterTests
        pass

    def setUp(self):
        from Products.MailHost.MailHost import MailHost

        self._obj = MailHost('foo_mailhost')
        self._BODY = _MAILHOST_BODY_v2


@unittest.skipUnless(HAVE_GS, 'Products.GenericSetup not available.')
class MailHostXMLAdapterTestsWithNoneValue(MailHostXMLAdapterTests):

    def _verifyImport(self, obj):
        self.assertEqual(obj.smtp_host, 'localhost')
        self.assertEqual(obj.smtp_port, 25)
        self.assertEqual(obj.smtp_pwd, '')
        self.assertEqual(obj.smtp_uid, '')

    def setUp(self):
        from Products.MailHost.MailHost import MailHost

        self._obj = MailHost('foo_mailhost')
        self._obj.smtp_uid = None
        self._BODY = _MAILHOST_BODY


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(MailHostXMLAdapterTests),
        unittest.makeSuite(MailHostXMLAdapterTestsWithoutQueue),
        unittest.makeSuite(MailHostXMLAdapterTestsWithQueue),
        unittest.makeSuite(MailHostXMLAdapterTestsWithNoneValue)))
