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

import logging
import sys
import unittest

import transaction
from Testing.makerequest import makerequest
from zope.component import adapter, provideHandler
from zope.event import notify
from ZPublisher.pubevents import PubFailure
import Zope2

from Products.SiteErrorLog.interfaces import IErrorRaisedEvent


class SiteErrorLogTests(unittest.TestCase):

    def setUp(self):
        Zope2.startup_wsgi()
        transaction.begin()
        self.app = makerequest(Zope2.app())
        try:
            if not hasattr(self.app, 'error_log'):
                # If ZopeLite was imported, we have no default error_log
                from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
                self.app._setObject('error_log', SiteErrorLog())
            self.app.manage_addDTMLMethod('doc', '')

            self.logger = logging.getLogger('Zope.SiteErrorLog')
            self.log = logging.handlers.BufferingHandler(sys.maxsize)
            self.logger.addHandler(self.log)
            self.old_level = self.logger.level
            self.logger.setLevel(logging.ERROR)
        except:
            self.tearDown()

    def tearDown(self):
        self.logger.removeHandler(self.log)
        self.logger.setLevel(self.old_level)
        transaction.abort()
        self.app._p_jar.close()

    def testInstantiation(self):
        # Retrieve the error_log by ID
        sel_ob = getattr(self.app, 'error_log', None)

        # Does the error log exist?
        self.assertTrue(sel_ob is not None)

        # Is the __error_log__ hook in place?
        self.assertEqual(self.app.__error_log__, sel_ob)

    def testSimpleException(self):
        # Grab the Site Error Log and make sure it's empty
        sel_ob = self.app.error_log
        previous_log_length = len(sel_ob.getLogEntries())

        # Fill the DTML method at self.root.doc with bogus code
        dmeth = self.app.doc
        dmeth.manage_upload(file="""<dtml-var expr="1/0">""")

        # Faking the behavior of the WSGIPublisher (object acquisition,
        # view calling and failure notification on exception).
        try:
            dmeth.__call__()
        except ZeroDivisionError:
            self.app.REQUEST['PUBLISHED'] = dmeth
            notify(PubFailure(self.app.REQUEST, sys.exc_info(), False))

        # Now look at the SiteErrorLog, it has one more log entry
        self.assertEqual(len(sel_ob.getLogEntries()), previous_log_length + 1)

    def testEventSubscription(self):
        sel_ob = self.app.error_log
        # Fill the DTML method at self.root.doc with bogus code
        dmeth = self.app.doc
        dmeth.manage_upload(file="""<dtml-var expr="1/0">""")

        event_logs = []

        @adapter(IErrorRaisedEvent)
        def notifyError(evt):
            event_logs.append(evt)

        provideHandler(notifyError)
        # Faking the behavior of the WSGIPublisher (object acquisition,
        # view calling and failure notification on exception).
        try:
            dmeth.__call__()
        except ZeroDivisionError:
            self.app.REQUEST['PUBLISHED'] = dmeth
            notify(PubFailure(self.app.REQUEST, sys.exc_info(), False))

        self.assertEqual(len(event_logs), 1)
        self.assertEqual(event_logs[0]['type'], 'ZeroDivisionError')
        self.assertEqual(event_logs[0]['username'], 'Anonymous User')

    def testForgetException(self):
        elog = self.app.error_log

        # Create a predictable error
        try:
            raise AttributeError("DummyAttribute")
        except AttributeError:
            self.app.REQUEST['PUBLISHED'] = elog
            notify(PubFailure(self.app.REQUEST, sys.exc_info(), False))

        previous_log_length = len(elog.getLogEntries())

        entries = elog.getLogEntries()
        self.assertEqual(entries[0]['value'], "DummyAttribute")

        # Kick it
        elog.forgetEntry(entries[0]['id'])

        # Really gone?
        self.assertEqual(len(elog.getLogEntries()), previous_log_length - 1)

    def testIgnoredException(self):
        # Grab the Site Error Log
        sel_ob = self.app.error_log
        previous_log_length = len(sel_ob.getLogEntries())

        # Tell the SiteErrorLog to ignore ZeroDivisionErrors
        current_props = sel_ob.getProperties()
        ignored = list(current_props['ignored_exceptions'])
        ignored.append('ZeroDivisionError')
        sel_ob.setProperties(current_props['keep_entries'],
                             copy_to_zlog=current_props['copy_to_zlog'],
                             ignored_exceptions=ignored)

        # Fill the DTML method at self.root.doc with bogus code
        dmeth = self.app.doc
        dmeth.manage_upload(file="""<dtml-var expr="1/0">""")

        # Faking the behavior of the WSGIPublisher (object acquisition,
        # view calling and failure notification on exception).
        try:
            dmeth.__call__()
        except ZeroDivisionError:
            self.app.REQUEST['PUBLISHED'] = dmeth
            notify(PubFailure(self.app.REQUEST, sys.exc_info(), False))

        # Now look at the SiteErrorLog, it must have the same number of
        # log entries
        self.assertEqual(len(sel_ob.getLogEntries()), previous_log_length)

    def testEntryID(self):
        elog = self.app.error_log

        # Create a predictable error
        try:
            raise AttributeError("DummyAttribute")
        except AttributeError:
            self.app.REQUEST['PUBLISHED'] = elog
            notify(PubFailure(self.app.REQUEST, sys.exc_info(), False))

        entries = elog.getLogEntries()
        entry_id = entries[0]['id']

        self.assertTrue(entry_id in self.log.buffer[-1].msg,
                        (entry_id, self.log.buffer[-1].msg))

    def testCleanup(self):
        # Need to make sure that the __error_log__ hook gets cleaned up
        self.app._delObject('error_log')
        self.assertEqual(getattr(self.app, '__error_log__', None), None)
