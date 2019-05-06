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
"""Mail Delivery utility implementation

This module contains various implementations of `MailDeliverys`.
"""
__docformat__ = 'restructuredtext'

import os
import email.parser
import logging
import warnings
from random import randrange
from time import strftime
from socket import gethostname

from transaction.interfaces import IDataManager
import transaction

from zope.interface import implementer
from zope.sendmail.interfaces import IDirectMailDelivery, IQueuedMailDelivery
from zope.sendmail.maildir import Maildir

# BBB: this import is needed for backward compatibility with older versions of
# zope.sendmail which defined QueueProcessorThread in this module
from zope.sendmail.queue import QueueProcessorThread  # noqa: F401


log = logging.getLogger("MailDataManager")


@implementer(IDataManager)
class MailDataManager(object):

    def __init__(self, callable, args=(), vote=None, onAbort=None):
        self.callable = callable
        self.args = args
        self.vote = vote
        self.onAbort = onAbort
        # Use the default thread transaction manager.
        self.transaction_manager = transaction.manager

    def commit(self, txn):
        pass

    def abort(self, txn):
        if self.onAbort:
            self.onAbort()

    def sortKey(self):
        return str(id(self))

    # No subtransaction support.
    def abort_sub(self, txn):
        "This object does not do anything with subtransactions"

    commit_sub = abort_sub

    def beforeCompletion(self, txn):
        "This object does not do anything in beforeCompletion"

    afterCompletion = beforeCompletion

    def tpc_begin(self, txn, subtransaction=False):
        assert not subtransaction

    def tpc_vote(self, txn):
        if self.vote is not None:
            return self.vote(*self.args)

    def tpc_finish(self, txn):
        try:
            self.callable(*self.args)
        except Exception:
            # Any exceptions here can cause database corruption.
            # Better to protect the data and potentially miss emails than
            # leave a database in an inconsistent state which requires a
            # guru to fix.
            log.exception("Failed in tpc_finish for %r", self.callable)

    tpc_abort = abort


class AbstractMailDelivery(object):

    def newMessageId(self):
        """Generates a new message ID according to RFC 2822 rules"""
        randmax = 0x7fffffff
        left_part = '%s.%d.%d' % (strftime('%Y%m%d%H%M%S'),
                                  os.getpid(),
                                  randrange(0, randmax))
        return "%s@%s" % (left_part, gethostname())

    def send(self, fromaddr, toaddrs, message):
        parser = email.parser.Parser()
        msg = parser.parsestr(message)
        messageid = msg.get('Message-Id')
        if messageid:
            if not messageid.startswith('<') or not messageid.endswith('>'):
                raise ValueError('Malformed Message-Id header')
            messageid = messageid[1:-1]
        else:
            messageid = self.newMessageId()
            message = 'Message-Id: <%s>\n%s' % (messageid, message)
        transaction.get().join(
            self.createDataManager(fromaddr, toaddrs, message))
        return messageid

    def createDataManager(self, fromaddr, toaddrs, message):
        raise NotImplementedError()


@implementer(IDirectMailDelivery)
class DirectMailDelivery(AbstractMailDelivery):
    __doc__ = IDirectMailDelivery.__doc__

    def __init__(self, mailer):
        self.mailer = mailer

    def createDataManager(self, fromaddr, toaddrs, message):
        try:
            vote = self.mailer.vote
        except AttributeError:
            # We've got an old mailer, just pass through voting
            warnings.warn("The mailer %s does not provide a vote method"
                          % (repr(self.mailer)), DeprecationWarning)

            def vote(*args, **kwargs):
                pass

        return MailDataManager(self.mailer.send,
                               args=(fromaddr, toaddrs, message),
                               vote=vote,
                               onAbort=self.mailer.abort)


@implementer(IQueuedMailDelivery)
class QueuedMailDelivery(AbstractMailDelivery):
    __doc__ = IQueuedMailDelivery.__doc__

    def __init__(self, queuePath):
        self._queuePath = queuePath

    queuePath = property(lambda self: self._queuePath)

    def createDataManager(self, fromaddr, toaddrs, message):
        maildir = Maildir(self.queuePath, True)
        msg = maildir.newMessage()
        msg.write('X-Zope-From: %s\n' % fromaddr)
        msg.write('X-Zope-To: %s\n' % ", ".join(toaddrs))
        msg.write(message)
        msg.close()
        return MailDataManager(msg.commit, onAbort=msg.abort)
