##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test the gts ZCML namespace directives.
"""
import os
import shutil
import unittest
import tempfile


import zope.component
from zope.component.testing import PlacelessSetup
from zope.configuration import xmlconfig
from zope.interface import implementer

from zope.sendmail.interfaces import \
     IMailDelivery, IMailer, ISMTPMailer
from zope.sendmail import delivery
from zope.sendmail import zcml
import zope.sendmail.tests


class MaildirStub(object):
    pass


@implementer(IMailer)
class Mailer(object):
    pass


class MockQueueProcessorThread(object):

    def setMailer(self, mailer):
        pass

    setQueuePath = setMailer

    def start(self):
        pass


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(DirectivesTest, self).setUp()

        self.mailbox = os.path.join(tempfile.mkdtemp(), "mailbox")
        self.addCleanup(shutil.rmtree, self.mailbox, True)
        self.testMailer = Mailer()
        self.smtpmailer = Mailer()
        gsm = zope.component.getGlobalSiteManager()

        gsm.registerUtility(self.smtpmailer, IMailer, "test.smtp")
        gsm.registerUtility(self.testMailer, IMailer, "test.mailer")

        here = os.path.dirname(__file__)
        with open(os.path.join(here, "mail.zcml"), 'r') as f:
            self.zcml = f.read()
        self.zcml = self.zcml.replace('path/to/tmp/mailbox', self.mailbox)

        self.orig_quethread = zcml.QueueProcessorThread
        self.orig_maildir = delivery.Maildir
        delivery.Maildir = MaildirStub
        zcml.QueueProcessorThread = MockQueueProcessorThread

        self.context = xmlconfig.string(self.zcml)

    def tearDown(self):
        delivery.Maildir = self.orig_maildir
        zcml.QueueProcessorThread = self.orig_quethread

        super(DirectivesTest, self).tearDown()

    def testQueuedDelivery(self):
        delivery = zope.component.getUtility(IMailDelivery, "Mail")
        self.assertEqual('QueuedMailDelivery', delivery.__class__.__name__)
        self.assertEqual(self.mailbox, delivery.queuePath)

    def testDirectDelivery(self):
        delivery = zope.component.getUtility(IMailDelivery, "Mail2")
        self.assertEqual('DirectMailDelivery', delivery.__class__.__name__)
        self.assertTrue(self.testMailer is delivery.mailer)

    def testSMTPMailer(self):
        mailer = zope.component.getUtility(IMailer, "smtp")
        self.assertTrue(ISMTPMailer.providedBy(mailer))

    def _check_zcml_without_registration(self, utility, name):
        gsm = zope.component.getGlobalSiteManager()
        gsm.unregisterUtility(utility, IMailer, name)
        from zope.configuration.exceptions import ConfigurationError
        with self.assertRaises(ConfigurationError) as exc:
            xmlconfig.string(self.zcml)

        msg = str(exc.exception)
        self.assertIn(name, msg)
        self.assertIn('is not defined', msg)

    def test_zcml_without_registered_smtp_mailer(self):
        self._check_zcml_without_registration(self.smtpmailer, 'test.smtp')

    def test_zcml_without_registered_mailer(self):
        self._check_zcml_without_registration(self.testMailer, 'test.mailer')
