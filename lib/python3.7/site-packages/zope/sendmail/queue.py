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
"""Queue processor thread

This module contains the queue processor thread.
"""
__docformat__ = 'restructuredtext'

import atexit
import logging
import argparse
import os
import smtplib
import threading
import time
import errno

from zope.sendmail.maildir import Maildir
from zope.sendmail.mailer import SMTPMailer

import sys
if sys.platform == 'win32':  # pragma: no cover
    import win32file

    def _os_link(src, dst):
        return win32file.CreateHardLink(dst, src, None)
else:
    _os_link = os.link

try:
    import ConfigParser as configparser
except ImportError:  # pragma: PY3
    import configparser

# The longest time sending a file is expected to take.  Longer than this and
# the send attempt will be assumed to have failed.  This means that sending
# very large files or using very slow mail servers could result in duplicate
# messages sent.
MAX_SEND_TIME = 60*60*3

# The below diagram depicts the operations performed while sending a message in
# the ``run`` method of ``QueueProcessorThread``.  This sequence of operations
# will be performed for each file in the maildir each time the thread "wakes
# up" to send messages.
#
# Any error conditions not depicted on the diagram will provoke the catch-all
# exception logging of the ``run`` method.
#
# In the diagram the "message file" is the file in the maildir's "cur"
# directory that contains the message and "tmp file" is a hard link to the
# message file created in the maildir's "tmp" directory.
#
#           ( start trying to deliver a message )
#                            |
#                            |
#                            V
#            +-----( get tmp file mtime )
#            |               |
#            |               | file exists
#            |               V
#            |         ( check age )-----------------------------+
#   tmp file |               |                       file is new |
#   does not |               | file is old                       |
#   exist    |               |                                   |
#            |      ( unlink tmp file )-----------------------+  |
#            |               |                      file does |  |
#            |               | file unlinked        not exist |  |
#            |               V                                |  |
#            +---->( touch message file )------------------+  |  |
#                            |                   file does |  |  |
#                            |                   not exist |  |  |
#                            V                             |  |  |
#            ( link message file to tmp file )----------+  |  |  |
#                            |                 tmp file |  |  |  |
#                            |           already exists |  |  |  |
#                            |                          |  |  |  |
#                            V                          V  V  V  V
#                     ( send message )             ( skip this message )
#                            |
#                            V
#                 ( unlink message file )---------+
#                            |                    |
#                            | file unlinked      | file no longer exists
#                            |                    |
#                            |  +-----------------+
#                            |  |
#                            |  V
#                  ( unlink tmp file )------------+
#                            |                    |
#                            | file unlinked      | file no longer exists
#                            V                    |
#                  ( message delivered )<---------+


class QueueProcessorThread(threading.Thread):
    """This thread is started at configuration time from the
    `mail:queuedDelivery` directive handler if processorThread is True.
    """

    log = logging.getLogger("QueueProcessorThread")
    _stopped = False
    interval = 3.0   # process queue every X second
    maildir = None
    mailer = None

    def __init__(self, interval=3.0):
        threading.Thread.__init__(
            self, name="zope.sendmail.queue.QueueProcessorThread")
        self.interval = interval
        self._lock = threading.Lock()
        self.setDaemon(True)

    def setMaildir(self, maildir):
        """Set the maildir.

        This method is used just to provide a `maildir` stub.
        """
        self.maildir = maildir

    def _makeMaildir(self, path):
        return Maildir(path, True)

    def setQueuePath(self, path):
        self.setMaildir(self._makeMaildir(path))

    def setMailer(self, mailer):
        self.mailer = mailer

    def _parseMessage(self, message):
        """Extract fromaddr and toaddrs from the first two lines of
        the `message`.

        Returns a fromaddr string, a toaddrs tuple and the message
        string.
        """

        fromaddr = ""
        toaddrs = ()
        rest = ""

        try:
            first, second, rest = message.split('\n', 2)
        except ValueError:
            return fromaddr, toaddrs, message

        if first.startswith("X-Zope-From: "):
            i = len("X-Zope-From: ")
            fromaddr = first[i:]

        if second.startswith("X-Zope-To: "):
            i = len("X-Zope-To: ")
            toaddrs = tuple(second[i:].split(", "))

        return fromaddr, toaddrs, rest

    def _action_if_exists(self, fname, func, default=None):
        # apply the func to the fname, ignoring exceptions that
        # happen when the file does not exist.
        try:
            return func(fname)
        except OSError as e:
            if e.errno != errno.ENOENT:
                # The file existed, but something unexpected
                # happened. Report it
                raise
            return default

    def _unlink_if_exists(self, fname):
        self._action_if_exists(fname, os.unlink)

    def run(self, forever=True):
        atexit.register(self.stop)
        while not self._stopped:
            for filename in self.maildir:
                # if we are asked to stop while sending messages, do so
                if self._stopped:
                    break
                self._process_one_file(filename)
            else:
                if forever:
                    time.sleep(self.interval)

            # A testing plug
            if not forever:
                break

    def _process_one_file(self, filename):
        fromaddr = ''
        toaddrs = ()
        head, tail = os.path.split(filename)
        tmp_filename = os.path.join(head, '.sending-' + tail)
        rejected_filename = os.path.join(head, '.rejected-' + tail)
        try:
            # perform a series of operations in an attempt to ensure
            # that no two threads/processes send this message
            # simultaneously as well as attempting to not generate
            # spurious failure messages in the log; a diagram that
            # represents these operations is included in a
            # comment above this class

            # find the age of the tmp file (if it exists)
            mtime = self._action_if_exists(
                tmp_filename,
                lambda fname: os.stat(fname).st_mtime)
            age = time.time() - mtime if mtime is not None else None

            # if the tmp file exists, check its age
            if age is not None:
                if age > MAX_SEND_TIME:
                    # the tmp file is "too old"; this suggests
                    # that during an attempt to send it, the
                    # process died; remove the tmp file so we
                    # can try again
                    try:
                        os.unlink(tmp_filename)
                    except OSError as e:
                        if e.errno == errno.ENOENT:  # file does not exist
                            # it looks like someone else removed the tmp
                            # file, that's fine, we'll try to deliver the
                            # message again later
                            return
                        # XXX: we're silently ignoring the exception here.
                        # Is that right?
                        # If permissions or something are not right, we'll fail
                        # on _os_link later on.
                    # if we get here, the file existed, but was too
                    # old, so it was unlinked
                else:
                    # the tmp file is "new", so someone else may
                    # be sending this message, try again later
                    return

            # now we know (hope, given the above XXX) that the
            # tmp file doesn't exist, we need to "touch" the
            # message before we create the tmp file so the
            # mtime will reflect the fact that the file is
            # being processed (there is a race here, but it's
            # OK for two or more processes to touch the file
            # "simultaneously")
            try:
                os.utime(filename, None)
            except OSError as e:
                if e.errno == errno.ENOENT:  # file does not exist
                    # someone removed the message before we could
                    # touch it, no need to complain, we'll just keep
                    # going
                    return
                # XXX: Silently ignoring all other errors

            # creating this hard link will fail if another process is
            # also sending this message
            try:
                _os_link(filename, tmp_filename)
            except OSError as e:
                if e.errno == errno.EEXIST:  # file exists, *nix
                    # it looks like someone else is sending this
                    # message too; we'll try again later
                    return
                # XXX: Silently ignoring all other errno
            except Exception as e:  # pragma: no cover
                if e[0] == 183 and e[1] == 'CreateHardLink':
                    # file exists, win32
                    return
                # XXX: Silently ignoring all other causes here.

            # read message file and send contents
            with open(filename) as f:
                message = f.read()

            fromaddr, toaddrs, message = self._parseMessage(message)
            # The next block is the only one that is sensitive to
            # interruptions.  Everywhere else, if this daemon thread
            # stops, we should be able to correctly handle a restart.
            # In this block, if we send the message, but we are
            # stopped before we unlink the file, we will resend the
            # message when we are restarted.  We limit the likelihood
            # of this somewhat by using a lock to link the two
            # operations.  When the process gets an interrupt, it
            # will call the atexit that we registered (``stop``
            # below).  This will try to get the same lock before it
            # lets go.  Because this can cause the daemon thread to
            # continue (that is, to not act like a daemon thread), we
            # still use the _stopped flag to communicate.
            with self._lock:
                try:
                    self.mailer.send(fromaddr, toaddrs, message)
                except smtplib.SMTPResponseException as e:
                    if 500 <= e.smtp_code <= 599:
                        # permanent error, ditch the message
                        self.log.error(
                            "Discarding email from %s to %s due to"
                            " a permanent error: %s",
                            fromaddr, ", ".join(toaddrs), str(e))
                        _os_link(filename, rejected_filename)
                    else:
                        # Log an error and retry later
                        raise
                except smtplib.SMTPRecipientsRefused as e:
                    # All recipients are refused by smtp
                    # server. Dont try to redeliver the message.
                    self.log.error("Email recipients refused: %s",
                                   ', '.join(e.recipients))
                    _os_link(filename, rejected_filename)

                self._unlink_if_exists(filename)

            self._unlink_if_exists(tmp_filename)

            # TODO: maybe log the Message-Id of the message sent
            self.log.info("Mail from %s to %s sent.",
                          fromaddr, ", ".join(toaddrs))
            # Blanket except because we don't want
            # this thread to ever die
        except Exception:
            if fromaddr != '' or toaddrs != ():
                self.log.error(
                    "Error while sending mail from %s to %s.",
                    fromaddr, ", ".join(toaddrs), exc_info=True)
            else:
                self.log.error(
                    "Error while sending mail : %s ",
                    filename, exc_info=True)

    def stop(self):
        self._stopped = True
        self._lock.acquire()
        self._lock.release()


def boolean(s):
    s = str(s).lower()
    return s.startswith("t") or s.startswith("y") or s.startswith("1")


def string_or_none(s):
    if s == 'None':
        return None
    return s


class ConsoleApp(object):
    """Allows running of Queue Processor from the console."""

    INI_SECTION = "app:zope-sendmail"
    INI_NAMES = [
        "interval",
        "hostname",
        "port",
        "username",
        "password",
        "force_tls",
        "no_tls",
        "queue_path",
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--daemon', action='store_true',
        help=("Run in daemon mode, periodically checking queue "
              "and sending messages.  Default is to send all "
              "messages in queue once and exit."))
    parser.add_argument(
        '--interval', metavar='<#secs>', type=float, default=3,
        help=("How often to check queue when in daemon mode. "
              "Default is %(default)s seconds."))
    smtp_group = parser.add_argument_group(
        "SMTP Server",
        "Connection information for the SMTP server")
    smtp_group.add_argument(
        '--hostname', default='localhost',
        help=("Name of SMTP host to use for delivery.  Default is "
              "%(default)s."))
    smtp_group.add_argument(
        '--port', type=int, default=25,
        help=("Which port on SMTP server to deliver mail to. "
              "Default is %(default)s."))

    auth_group = parser.add_argument_group(
        "Authentication",
        ("Authentication information for the SMTP server. "
         "If one is provided, they must both be. One or both "
         "can be provided in the --config file."))
    auth_group.add_argument(
        '--username',
        help=("Username to use to log in to SMTP server.  Default "
              "is none."))
    auth_group.add_argument(
        '--password',
        help=("Password to use to log in to SMTP server.  Must be "
              "specified if username is specified."))
    del auth_group
    tls_group = smtp_group.add_mutually_exclusive_group()
    tls_group.add_argument(
        '--force-tls', action='store_true',
        help=("Do not connect if TLS is not available.  Not "
              "enabled by default."))
    tls_group.add_argument(
        '--no-tls', action='store_true',
        help=("Do not use TLS even if is available.  Not enabled "
              "by default."))
    del tls_group
    del smtp_group
    parser.add_argument(
        '--config', metavar='<inifile>',
        type=argparse.FileType(),
        help=("Get configuration from specified ini file; it must "
              "contain a section [%s] that can contain the "
              "following keys: %s. If you specify the queue path "
              "in the ini file, you don't need to specify it on "
              "the command line. With the exception of the queue path, "
              "options specified in the ini file override options on the "
              "command line." % (INI_SECTION, ', '.join(INI_NAMES))))
    parser.add_argument(
        "maildir", default=None, nargs="?",
        help=("The path to the mail queue directory."
              "If not given, it must be found in the --config file."
              "If given, this overrides a value in the --config file"))

    daemon = False
    interval = 3
    hostname = 'localhost'
    port = 25
    username = None
    password = None
    force_tls = False
    no_tls = False
    queue_path = None

    QueueProcessorKind = QueueProcessorThread
    MailerKind = SMTPMailer

    def __init__(self, argv=None, verbose=True):
        argv = sys.argv if argv is None else argv
        self.script_name = argv[0]
        self.verbose = verbose
        self._process_args(argv[1:])
        self.mailer = self.MailerKind(
            self.hostname, self.port, self.username, self.password,
            self.no_tls, self.force_tls)

    def main(self):
        queue = self.QueueProcessorKind(self.interval)
        queue.setMailer(self.mailer)
        queue.setQueuePath(self.queue_path)
        queue.run(forever=self.daemon)

    def _process_args(self, args):
        opts = self.parser.parse_args(args)
        self.daemon = opts.daemon
        self.interval = opts.interval
        self.hostname = opts.hostname
        self.port = opts.port
        self.username = opts.username
        self.password = opts.password
        self.force_tls = opts.force_tls
        self.no_tls = opts.no_tls

        if opts.config:
            fname = opts.config.name
            opts.config.close()
            self._load_config(fname)
        self.queue_path = opts.maildir or self.queue_path

        if not self.queue_path:
            self.parser.error('please specify the queue path')
        if (self.username or self.password) and \
           not (self.username and self.password):
            self.parser.error('Must use username and password together.')

    def _load_config(self, path):
        section = self.INI_SECTION
        names = self.INI_NAMES
        defaults = dict([(name, str(getattr(self, name))) for name in names])
        config = configparser.ConfigParser(defaults)
        config.read(path)
        self.interval = float(config.get(section, "interval"))
        self.hostname = config.get(section, "hostname")
        self.port = int(config.get(section, "port"))
        self.username = string_or_none(config.get(section, "username"))
        self.password = string_or_none(config.get(section, "password"))
        self.force_tls = boolean(config.get(section, "force_tls"))
        self.no_tls = boolean(config.get(section, "no_tls"))
        self.queue_path = string_or_none(config.get(section, "queue_path"))


def run(argv=None):
    logging.basicConfig()
    app = ConsoleApp(argv)
    app.main()


if __name__ == '__main__':
    run()
