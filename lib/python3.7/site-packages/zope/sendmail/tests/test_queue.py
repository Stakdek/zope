##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Mail Delivery Tests

Simple implementation of the MailDelivery, Mailers and MailEvents.
"""
import errno
import os.path
import shutil
import sys
from tempfile import mkdtemp
import unittest
import io
from contextlib import contextmanager

from zope.sendmail.queue import ConsoleApp
from zope.sendmail.tests.test_delivery import WritableMaildirStub
from zope.sendmail.tests.test_delivery import LoggerStub
from zope.sendmail.tests.test_delivery import BrokenMailerStub
from zope.sendmail.tests.test_delivery import SMTPResponseExceptionMailerStub
from zope.sendmail.tests.test_delivery import MailerStub
from zope.sendmail.tests.test_delivery import BizzarreMailError

from zope.sendmail import queue


class QPTesting(queue.QueueProcessorThread):

    test = None

    def _makeMaildir(self, path):
        return WritableMaildirStub(self.test, path)


class SMTPRecipientsRefusedMailerStub(object):

    def __init__(self, recipients):
        self.recipients = recipients

    def send(self, fromaddr, toaddrs, message):
        import smtplib
        raise smtplib.SMTPRecipientsRefused(self.recipients)


@contextmanager
def patched(module, attr, func):
    orig = getattr(module, attr)
    setattr(module, attr, func)
    try:
        yield
    finally:
        setattr(module, attr, orig)


class TestQueueProcessorThread(unittest.TestCase):

    def setUp(self):
        self.thread = QPTesting()
        self.thread.test = self
        self.thread.setQueuePath('/foo/bar/baz')
        self.md = self.thread.maildir
        self.dir = self.md.stub_directory
        self.mailer = MailerStub()
        self.thread.setMailer(self.mailer)
        self.thread.log = LoggerStub()
        self.filename = None

    def _assertEmptyErrorLog(self):
        self.assertEqual(self.thread.log.errors, [])

    def _assertErrorLog(
        self,
        From=WritableMaildirStub.STUB_DEFAULT_MESSAGE_SENT[0],
        to=", ".join(WritableMaildirStub.STUB_DEFAULT_MESSAGE_SENT[1]),
        exception_kind=None,
    ):
        expected = ('Error while sending mail from %s to %s.',
                    (From, to,),
                    {'exc_info': True},)
        error = self.thread.log.errors[0]
        if exception_kind:
            error = error[:4]
            expected += (exception_kind,)
        else:
            error = error[:3]
        self.assertEqual(error, expected)

    def _assertGenericErrorLog(self, filename="message",
                               exception=None):
        full_path = os.path.join(self.dir, filename)
        expected = ('Error while sending mail : %s ',
                    (full_path,),
                    {'exc_info': True})
        error = self.thread.log.errors[0]
        error = error[:5]
        expected += (type(exception), exception,)
        self.assertEqual(error, expected)

    def _assertTmpMessagePathDoesNotExist(self, filename="message"):
        full_path = self.md.stub_getTmpFilename(filename)
        self.assertFalse(
            os.path.exists(full_path),
            "The temporary path '%s' should not exist" % full_path)

    def _assertTmpMessagePathExists(self, filename="message"):
        full_path = self.md.stub_getTmpFilename(filename)
        self.assertTrue(os.path.exists(full_path),
                        "The temporary path '%s' should exist" % full_path)

    def _assertRejectedMessagePathExists(self, filename="message"):
        full_path = self.md.stub_getFailedFilename(filename)
        self.assertTrue(os.path.exists(full_path),
                        "The rejected path '%s' should exist" % full_path)

    def _assertMessagePathExists(self, filename="message"):
        full_path = os.path.join(self.dir, filename)
        self.assertTrue(os.path.exists(full_path),
                        "The path '%s' should exist" % full_path)

    def _assertMessagePathDoesNotExist(self, filename="message"):
        full_path = os.path.join(self.dir, filename)
        self.assertFalse(os.path.exists(full_path),
                         "The path '%s' should not exist" % full_path)

    def test_makeMaildir_creates(self):
        md = queue.QueueProcessorThread()._makeMaildir(
            os.path.join(self.dir, 'testing'))
        self.assertTrue(os.path.exists(md.path))

    def test_threadName(self):
        self.assertEqual(self.thread.getName(),
                         "zope.sendmail.queue.QueueProcessorThread")

    def test_parseMessage(self):
        hdr = ('X-Zope-From: foo@example.com\n'
               'X-Zope-To: bar@example.com, baz@example.com\n')
        msg = ('Header: value\n'
               '\n'
               'Body\n')
        f, t, m = self.thread._parseMessage(hdr + msg)
        self.assertEqual(f, 'foo@example.com')
        self.assertEqual(t, ('bar@example.com', 'baz@example.com'))
        self.assertEqual(m, msg)

    def test_parseMessage_error(self):
        msg = "bad message"
        f, t, m = self.thread._parseMessage(msg)
        self.assertEqual(f, "")
        self.assertEqual(t, ())
        self.assertEqual(m, msg)

    def test_deliveration(self):
        self.filename = self.md.stub_createFile('message')
        self._assertMessagePathExists("message")
        self.thread.run(forever=False)
        self.assertEqual(self.mailer.sent_messages,
                         [self.md.STUB_DEFAULT_MESSAGE_SENT])
        self._assertMessagePathDoesNotExist('message')
        self.assertEqual(self.thread.log.infos,
                         [('Mail from %s to %s sent.',
                           ('foo@example.com',
                            'bar@example.com, baz@example.com'),
                           {})])

    def test_error_logging(self):
        self.thread.setMailer(BrokenMailerStub())
        self.filename = self.md.stub_createFile('message')
        self._assertMessagePathExists("message")
        self.thread.run(forever=False)
        self._assertErrorLog(exception_kind=BizzarreMailError)

    def test_smtp_response_error_transient(self):
        # Test a transient error
        self.thread.setMailer(SMTPResponseExceptionMailerStub(451))
        self.filename = self.md.stub_createFile('message')

        self.thread.run(forever=False)

        # File must remain were it was, so it will be retried
        self._assertMessagePathExists("message")
        self._assertErrorLog()

    def test_smtp_response_error_permanent(self):
        # Test a permanent error
        self.thread.setMailer(SMTPResponseExceptionMailerStub(550))
        self.filename = self.md.stub_createFile('message')
        self._assertMessagePathExists("message")

        self.thread.run(forever=False)

        # File must be moved aside
        self._assertMessagePathDoesNotExist("message")
        self._assertRejectedMessagePathExists('message')

        self.assertEqual(self.thread.log.errors,
                         [('Discarding email from %s to %s due to a '
                           'permanent error: %s',
                           ('foo@example.com',
                            'bar@example.com, baz@example.com',
                            "(550, 'Serious Error')"), {})])

    def test_smtp_recipients_refused(self):
        # Test a permanent error
        self.thread.setMailer(SMTPRecipientsRefusedMailerStub(
            [self.md.STUB_DEFAULT_MESSAGE_RECPT[0]]))
        self.md.stub_createFile()
        self.thread.run(forever=False)

        # File must be moved aside
        self._assertMessagePathDoesNotExist()
        self._assertRejectedMessagePathExists()

        self.assertEqual(self.thread.log.errors,
                         [('Email recipients refused: %s',
                           (self.md.STUB_DEFAULT_MESSAGE_RECPT[0],), {})])

    def test_stop_while_running(self):
        test = self

        class Maildir(object):
            count = 0

            def __iter__(self):
                return self

            def __next__(self):
                self.count += 1
                if self.count == 1:
                    test.thread.stop()
                    return
                raise AssertionError("Should have stopped")

            next = __next__  # Python 2

        self.thread.setMaildir(Maildir())
        self.thread.run()
        self.assertEqual(1, self.thread.maildir.count)

    def test_tmpfile_exists(self):
        self.md.stub_createFile()
        self.md.stub_createTmpFile()

        self.thread.run(forever=False)

        # Both of them are still there because this was a brand new
        # file
        self._assertMessagePathExists()
        self._assertTmpMessagePathExists()

    def test_tmpfile_cannot_stat(self):
        self.md.stub_createFile()
        tmp_file = self.md.stub_createTmpFile()

        err = OSError(tmp_file)

        def stat(fname):
            # Note that this interferes with debuggers
            self.assertEqual(fname, tmp_file)
            raise err

        with patched(os, 'stat', stat):
            self.thread.run(forever=False)

        # Both of them are still there because of the exception
        self._assertMessagePathExists()
        self._assertTmpMessagePathExists()

        # And we logged the random error
        self._assertGenericErrorLog(exception=err)

    def test_tmpfile_too_old(self):
        self.md.stub_createFile()
        self.md.stub_createTmpFile()

        with patched(queue, 'MAX_SEND_TIME', -1):
            self.thread.run(forever=False)

        # Neither of them are there any more
        # file
        self._assertMessagePathDoesNotExist()
        self._assertTmpMessagePathDoesNotExist()

    def test_tmpfile_too_old_unlink_fails_generic(self):
        # generic unlink exceptions are ignored and processing just continues.
        # Later we fail to link the message file to the tempfile and catch that
        # and bail.
        self.md.stub_createFile()
        tmp_file = self.md.stub_createTmpFile()

        def unlink(fname):
            self.assertEqual(fname, tmp_file)
            raise OSError(fname)

        with patched(queue, 'MAX_SEND_TIME', -1):
            with patched(os, 'unlink', unlink):
                self.thread.run(forever=False)

        # The message was not processed
        self._assertMessagePathExists()
        # And our patch kept the tmpfile in place
        self._assertTmpMessagePathExists()
        self._assertEmptyErrorLog()

    def test_tmpfile_too_old_unlink_fails_dne(self):
        # If we try to remove a tempfile and its already gone,
        # skip it
        self.md.stub_createFile()
        tmp_file = self.md.stub_createTmpFile()

        def unlink(fname):
            self.assertEqual(fname, tmp_file)
            raise OSError(errno.ENOENT, fname)

        with patched(queue, 'MAX_SEND_TIME', -1):
            with patched(os, 'unlink', unlink):
                self.thread.run(forever=False)

        # The message was not processed
        self._assertMessagePathExists()
        # But our patch kept the tmpfile in place
        self._assertTmpMessagePathExists()
        self._assertEmptyErrorLog()

    def test_utime_fails_dne(self):
        # A DNE error from utime causes the process to continue
        filename = self.md.stub_createFile()

        def utime(fname, atm):
            self.assertEqual(fname, filename)
            self.assertIsNone(atm)
            raise OSError(errno.ENOENT, fname)

        with patched(os, 'utime', utime):
            self.thread.run(forever=False)

        # The message was not processed
        self._assertMessagePathExists()
        self._assertEmptyErrorLog()

    def test_run_forever(self):
        import time

        class DoneSleeping(Exception):
            pass

        def sleep(i):
            self.assertEqual(i, self.thread.interval)
            raise DoneSleeping()

        with patched(time, 'sleep', sleep):
            with self.assertRaises(DoneSleeping):
                self.thread.run()


test_ini = """[app:zope-sendmail]
interval = 33
hostname = testhost
port = 2525
username = Chris
password = Rossi
force_tls = False
no_tls = True
queue_path = hammer/dont/hurt/em
"""


class TestConsoleApp(unittest.TestCase):
    def setUp(self):
        from zope.sendmail.delivery import QueuedMailDelivery
        from zope.sendmail.maildir import Maildir
        self.dir = mkdtemp()
        self.queue_dir = os.path.join(self.dir, "queue")
        self.delivery = QueuedMailDelivery(self.queue_dir)
        self.maildir = Maildir(self.queue_dir, True)
        self.mailer = MailerStub()
        io_type = io.StringIO if bytes is not str else io.BytesIO
        self.stderr = io_type()
        self.stdout = io_type()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def _make_one(self, cmdline):
        cmdline = cmdline.split() if isinstance(cmdline, str) else cmdline
        with patched(sys, 'stdout', self.stdout), \
                patched(sys, 'stderr', self.stderr):
            return ConsoleApp(cmdline, verbose=False)

    def _get_output(self):
        return self.stderr.getvalue() + self.stdout.getvalue()

    def test_args_processing(self):
        # simplest case that works
        cmdline = "zope-sendmail %s" % self.dir
        app = self._make_one(cmdline)
        self.assertEqual("zope-sendmail", app.script_name)
        self.assertEqual(self.dir, app.queue_path)
        self.assertFalse(app.daemon)
        self.assertEqual(3, app.interval)
        self.assertEqual("localhost", app.hostname)
        self.assertEqual(25, app.port)
        self.assertEqual(None, app.username)
        self.assertEqual(None, app.password)
        self.assertFalse(app.force_tls)
        self.assertFalse(app.no_tls)

    def test_args_processing_no_queue_path(self):
        # simplest case that doesn't work: no queue path specified
        cmdline = "zope-sendmail"

        with self.assertRaises(SystemExit):
            self._make_one(cmdline)

        self.assertIn('please specify the queue path', self._get_output())

    def test_args_processing_almost_all_options(self):
        # use (almost) all of the options
        cmdline = (
            "zope-sendmail --daemon --interval 7 --hostname foo --port 75 "
            "--username chris --password rossi --force-tls "
            "%s" % self.dir
        )
        app = self._make_one(cmdline)
        self.assertEqual("zope-sendmail", app.script_name)
        self.assertEqual(self.dir, app.queue_path)
        self.assertTrue(app.daemon)
        self.assertEqual(7, app.interval)
        self.assertEqual("foo", app.hostname)
        self.assertEqual(75, app.port)
        self.assertEqual("chris", app.username)
        self.assertEqual("rossi", app.password)
        self.assertTrue(app.force_tls)
        self.assertFalse(app.no_tls)

        # Add an extra argument
        cmdline += ' another-one'
        with self.assertRaises(SystemExit):
            self._make_one(cmdline)

        self.assertIn('unrecognized argument', self._get_output())

    def test_args_processing_username_without_password(self):
        # test username without password
        cmdline = "zope-sendmail --username chris %s" % self.dir

        with self.assertRaises(SystemExit):
            self._make_one(cmdline)

        self.assertIn('Must use username and password together',
                      self._get_output())

    def test_args_processing_force_tls_and_no_tls(self):
        # test force_tls and no_tls
        cmdline = "zope-sendmail --force-tls --no-tls %s" % self.dir

        with self.assertRaises(SystemExit):
            self._make_one(cmdline)

        self.assertIn('--no-tls: not allowed with argument',
                      self._get_output())

    def test_ini_parse(self):
        ini_path = os.path.join(self.dir, "zope-sendmail.ini")
        with open(ini_path, "w") as f:
            f.write(test_ini)
        # override most everything
        cmdline = """zope-sendmail --config %s""" % ini_path
        app = ConsoleApp(cmdline.split(), verbose=False)
        self.assertEqual("zope-sendmail", app.script_name)
        self.assertEqual("hammer/dont/hurt/em", app.queue_path)
        self.assertFalse(app.daemon)
        self.assertEqual(33, app.interval)
        self.assertEqual("testhost", app.hostname)
        self.assertEqual(2525, app.port)
        self.assertEqual("Chris", app.username)
        self.assertEqual("Rossi", app.password)
        self.assertFalse(app.force_tls)
        self.assertTrue(app.no_tls)
        # override nothing, make sure defaults come through
        with open(ini_path, "w") as f:
            f.write("[app:zope-sendmail]\n\nqueue_path=foo\n")
        cmdline = """zope-sendmail --config %s %s""" % (ini_path, self.dir)
        app = ConsoleApp(cmdline.split(), verbose=False)
        self.assertEqual("zope-sendmail", app.script_name)
        self.assertEqual(self.dir, app.queue_path)
        self.assertFalse(app.daemon)
        self.assertEqual(3, app.interval)
        self.assertEqual("localhost", app.hostname)
        self.assertEqual(25, app.port)
        self.assertEqual(None, app.username)
        self.assertEqual(None, app.password)
        self.assertFalse(app.force_tls)
        self.assertFalse(app.no_tls)

    def test_ini_not_exist(self):
        cmdline = ['sendmail', '--config', 'this path cannot be opened']
        with self.assertRaises(SystemExit) as exc:
            self._make_one(cmdline)

        self.assertIn('No such file or directory', self._get_output())
        self.assertEqual(exc.exception.code, 2)

    def test_run(self):
        cmdline = ['sendmail', self.dir]

        with patched(QPTesting, 'test', self), \
                patched(ConsoleApp, 'QueueProcessorKind', QPTesting), \
                patched(ConsoleApp, 'MailerKind', MailerStub):
            queue.run(cmdline)

    def test_help(self):
        cmdline = ['prog', '--help']

        with self.assertRaises(SystemExit) as exc:
            self._make_one(cmdline)

        self.assertIn('usage', self._get_output())
        self.assertEqual(exc.exception.code, 0)
