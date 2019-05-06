##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import email.charset
import logging
import os
import re
import time
from copy import deepcopy
from email import encoders
from email import message_from_string
from email.charset import Charset
from email.header import Header
from email.message import Message
from email.utils import formataddr
from email.utils import getaddresses
from email.utils import parseaddr
from os.path import realpath
from threading import Lock

import six

from AccessControl.class_init import InitializeClass
from AccessControl.Permissions import change_configuration
from AccessControl.Permissions import use_mailhost_services
from AccessControl.Permissions import view
from AccessControl.SecurityInfo import ClassSecurityInfo
from Acquisition import Implicit
from App.special_dtml import DTMLFile
from DateTime.DateTime import DateTime
from OFS.role import RoleManager
from OFS.SimpleItem import Item
from Persistence import Persistent
from Products.MailHost.decorator import synchronized
from Products.MailHost.interfaces import IMailHost
from zope.interface import implementer
from zope.sendmail.delivery import DirectMailDelivery
from zope.sendmail.delivery import QueuedMailDelivery
from zope.sendmail.delivery import QueueProcessorThread
from zope.sendmail.maildir import Maildir
from zope.sendmail.mailer import SMTPMailer


queue_threads = {}  # maps MailHost path -> queue processor threada

LOG = logging.getLogger('MailHost')

# Encode utf-8 emails as Quoted Printable by default
email.charset.add_charset('utf-8', email.charset.QP, email.charset.QP, 'utf-8')
CHARSET_RE = re.compile(r'charset=[\'"]?([\w-]+)[\'"]?', re.IGNORECASE)


class MailHostError(Exception):
    pass


manage_addMailHostForm = DTMLFile('dtml/addMailHost_form', globals())


def manage_addMailHost(self,
                       id,
                       title='',
                       smtp_host='localhost',
                       localhost='localhost',
                       smtp_port=25,
                       timeout=1.0,
                       REQUEST=None):
    """ Add a MailHost into the system.
    """
    i = MailHost(id, title, smtp_host, smtp_port)
    self._setObject(id, i)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url() + '/manage_main')


add = manage_addMailHost


@implementer(IMailHost)
class MailBase(Implicit, Item, RoleManager):
    """a mailhost...?"""

    meta_type = 'Mail Host'
    zmi_icon = 'far fa-envelope'
    manage = manage_main = DTMLFile('dtml/manageMailHost', globals())
    manage_main._setName('manage_main')
    index_html = None
    security = ClassSecurityInfo()
    smtp_uid = ''  # Class attributes for smooth upgrades
    smtp_pwd = ''
    smtp_queue = False
    smtp_queue_directory = '/tmp'
    force_tls = False
    lock = Lock()

    manage_options = ((
        {'icon': '', 'label': 'Edit', 'action': 'manage_main'},
    ) + RoleManager.manage_options + Item.manage_options)

    def __init__(self,
                 id='',
                 title='',
                 smtp_host='localhost',
                 smtp_port=25,
                 force_tls=False,
                 smtp_uid='',
                 smtp_pwd='',
                 smtp_queue=False,
                 smtp_queue_directory='/tmp'):
        """Initialize a new MailHost instance.
        """
        self.id = id
        self.title = title
        self.smtp_host = str(smtp_host)
        self.smtp_port = int(smtp_port)
        self.smtp_uid = smtp_uid
        self.smtp_pwd = smtp_pwd
        self.force_tls = force_tls
        self.smtp_queue = smtp_queue
        self.smtp_queue_directory = smtp_queue_directory

    def _init(self, smtp_host, smtp_port):
        # staying for now... (backwards compatibility)
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    @security.protected(change_configuration)
    def manage_makeChanges(self,
                           title,
                           smtp_host,
                           smtp_port,
                           smtp_uid='',
                           smtp_pwd='',
                           smtp_queue=False,
                           smtp_queue_directory='/tmp',
                           force_tls=False,
                           REQUEST=None):
        """Make the changes.
        """
        title = str(title)
        smtp_host = str(smtp_host)
        smtp_port = int(smtp_port)

        self.title = title
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_uid = smtp_uid
        self.smtp_pwd = smtp_pwd
        self.force_tls = force_tls
        self.smtp_queue = smtp_queue
        self.smtp_queue_directory = smtp_queue_directory

        try:
            # restart queue processor thread
            if self.smtp_queue:
                self._stopQueueProcessorThread()
                self._startQueueProcessorThread()
            else:
                self._stopQueueProcessorThread()
            msg = 'MailHost %s updated' % self.id
        except ValueError as exc:
            msg = str(exc)

        if REQUEST is not None:
            return self.manage_main(self, REQUEST, manage_tabs_message=msg)

    @security.protected(use_mailhost_services)
    def sendTemplate(trueself,
                     self,
                     messageTemplate,
                     statusTemplate=None,
                     mto=None,
                     mfrom=None,
                     encode=None,
                     REQUEST=None,
                     immediate=False,
                     charset=None,
                     msg_type=None):
        """Render a mail template, then send it...
        """
        mtemplate = getattr(self, messageTemplate)
        messageText = mtemplate(self, trueself.REQUEST)
        trueself.send(messageText, mto=mto, mfrom=mfrom,
                      encode=encode, immediate=immediate,
                      charset=charset, msg_type=msg_type)

        if not statusTemplate:
            return 'SEND OK'
        try:
            stemplate = getattr(self, statusTemplate)
            return stemplate(self, trueself.REQUEST)
        except Exception:
            return 'SEND OK'

    @security.protected(use_mailhost_services)
    def send(self,
             messageText,
             mto=None,
             mfrom=None,
             subject=None,
             encode=None,
             immediate=False,
             charset=None,
             msg_type=None):
        messageText, mto, mfrom = _mungeHeaders(messageText, mto, mfrom,
                                                subject, charset, msg_type)
        # This encode step is mainly for BBB, encoding should be
        # automatic if charset is passed.  The automated charset-based
        # encoding will be preferred if both encode and charset are
        # provided.
        messageText = _encode(messageText, encode)
        self._send(mfrom, mto, messageText, immediate)

    # This is here for backwards compatibility only. Possibly it could
    # be used to send messages at a scheduled future time, or via a mail queue?
    security.declareProtected(use_mailhost_services,  # NOQA: flake8: D001
                              'scheduledSend')
    scheduledSend = send

    @security.protected(use_mailhost_services)
    def simple_send(self, mto, mfrom, subject, body, immediate=False):
        body = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (
            mfrom, mto, subject, body)

        self._send(mfrom, mto, body, immediate)

    def _makeMailer(self):
        """ Create a SMTPMailer """
        return SMTPMailer(hostname=self.smtp_host,
                          port=int(self.smtp_port),
                          username=self.smtp_uid or None,
                          password=self.smtp_pwd or None,
                          force_tls=self.force_tls)

    @security.private
    def _getThreadKey(self):
        """ Return the key used to find our processor thread.
        """
        return realpath(self.smtp_queue_directory)

    @synchronized(lock)
    def _stopQueueProcessorThread(self):
        """ Stop thread for processing the mail queue.
        """
        key = self._getThreadKey()
        if key in queue_threads:
            thread = queue_threads[key]
            thread.stop()
            while thread.isAlive():
                # wait until thread is really dead
                time.sleep(0.3)
            del queue_threads[key]
            LOG.info('Thread for %s stopped' % key)

    @synchronized(lock)
    def _startQueueProcessorThread(self):
        """ Start thread for processing the mail queue.
        """
        key = self._getThreadKey()
        if key not in queue_threads:
            thread = QueueProcessorThread()
            thread.setMailer(self._makeMailer())
            thread.setQueuePath(self.smtp_queue_directory)
            thread.start()
            queue_threads[key] = thread
            LOG.info('Thread for %s started' % key)

    @security.protected(view)
    def queueLength(self):
        """ return length of mail queue """

        try:
            maildir = Maildir(self.smtp_queue_directory)
            return len([item for item in maildir])
        except ValueError:
            return 'n/a - %s is not a maildir - please verify your ' \
                   'configuration' % self.smtp_queue_directory

    @security.protected(view)
    def queueThreadAlive(self):
        """ return True/False is queue thread is working
        """
        th = queue_threads.get(self._getThreadKey())
        if th:
            return th.isAlive()
        return False

    @security.protected(change_configuration)
    def manage_restartQueueThread(self, action='start', REQUEST=None):
        """ Restart the queue processor thread """

        if action == 'stop':
            self._stopQueueProcessorThread()
        elif action == 'start':
            self._startQueueProcessorThread()
        else:
            raise ValueError('Unsupported action %s' % action)

        if REQUEST is not None:
            msg = 'Queue processor thread %s' % \
                  (action == 'stop' and 'stopped' or 'started')
            return self.manage_main(self, REQUEST, manage_tabs_message=msg)

    @security.private
    def _send(self, mfrom, mto, messageText, immediate=False):
        """ Send the message """

        if immediate:
            self._makeMailer().send(mfrom, mto, messageText)
        else:
            if self.smtp_queue:
                # Start queue processor thread, if necessary
                if not os.environ.get('MAILHOST_QUEUE_ONLY', False):
                    self._startQueueProcessorThread()
                delivery = QueuedMailDelivery(self.smtp_queue_directory)
            else:
                delivery = DirectMailDelivery(self._makeMailer())

            delivery.send(mfrom, mto, messageText)


InitializeClass(MailBase)


class MailHost(Persistent, MailBase):
    """persistent version"""


# All encodings supported by mimetools for BBB
ENCODERS = {
    'base64': encoders.encode_base64,
    'quoted-printable': encoders.encode_quopri,
    '7bit': encoders.encode_7or8bit,
    '8bit': encoders.encode_7or8bit,
}


def _encode(body, encode=None):
    """Manually sets an encoding and encodes the message if not
    already encoded."""
    if encode is None:
        return body
    mo = message_from_string(body)
    current_coding = mo['Content-Transfer-Encoding']
    if current_coding == encode:
        # already encoded correctly, may have been automated
        return body
    if mo['Content-Transfer-Encoding'] not in ['7bit', None]:
        raise MailHostError('Message already encoded')
    if encode in ENCODERS:
        ENCODERS[encode](mo)
        if not mo['Content-Transfer-Encoding']:
            mo['Content-Transfer-Encoding'] = encode
        if not mo['Mime-Version']:
            mo['Mime-Version'] = '1.0'
    return mo.as_string()


def _string_transform(text, charset=None):
    if six.PY2 and isinstance(text, six.text_type):
        # Unicode under Python 2
        return _try_encode(text, charset)

    if six.PY3 and isinstance(text, bytes):
        # Already-encoded byte strings which the email module does not like
        return text.decode(charset)

    return text


def _mungeHeaders(messageText, mto=None, mfrom=None, subject=None,
                  charset=None, msg_type=None):
    """Sets missing message headers, and deletes Bcc.
       returns fixed message, fixed mto and fixed mfrom"""
    messageText = _string_transform(messageText, charset)
    mto = _string_transform(mto, charset)
    mfrom = _string_transform(mfrom, charset)
    subject = _string_transform(subject, charset)

    if isinstance(messageText, Message):
        # We already have a message, make a copy to operate on
        mo = deepcopy(messageText)
    else:
        # Otherwise parse the input message
        mo = message_from_string(messageText)

    if msg_type and not mo.get('Content-Type'):
        # we don't use get_content_type because that has a default
        # value of 'text/plain'
        mo.set_type(msg_type)

    charset = _set_recursive_charset(mo, charset=charset)

    # Parameters given will *always* override headers in the messageText.
    # This is so that you can't override or add to subscribers by adding
    # them to # the message text.
    if subject:
        # remove any existing header otherwise we get two
        del mo['Subject']
        # Perhaps we should ignore errors here and pass 8bit strings
        # on encoding errors
        mo['Subject'] = Header(subject, charset, errors='replace')
    elif not mo.get('Subject'):
        mo['Subject'] = '[No Subject]'

    if mto:
        if isinstance(mto, six.string_types):
            mto = [formataddr(addr) for addr in getaddresses((mto, ))]
        if not mo.get('To'):
            mo['To'] = ', '.join(str(_encode_address_string(e, charset))
                                 for e in mto)
    else:
        # If we don't have recipients, extract them from the message
        mto = []
        for header in ('To', 'Cc', 'Bcc'):
            v = ','.join(mo.get_all(header) or [])
            if v:
                mto += [formataddr(addr) for addr in getaddresses((v, ))]
        if not mto:
            raise MailHostError('No message recipients designated')

    if mfrom:
        # ??? do we really want to override an explicitly set From
        # header in the messageText
        del mo['From']
        mo['From'] = _encode_address_string(mfrom, charset)
    else:
        if mo.get('From') is None:
            raise MailHostError("Message missing SMTP Header 'From'")
        mfrom = mo['From']

    if mo.get('Bcc'):
        del mo['Bcc']

    if not mo.get('Date'):
        mo['Date'] = DateTime().rfc822()

    return mo.as_string(), mto, mfrom


def _set_recursive_charset(payload, charset=None):
    """Set charset for all parts of an multipart message."""
    def _set_payload_charset(payload, charset=None, index=None):
        payload_from_string = False
        if not isinstance(payload, Message):
            payload = message_from_string(payload)
            payload_from_string = True
        charset_match = CHARSET_RE.search(payload['Content-Type'] or '')
        if charset and not charset_match:
            # Don't change the charset if already set
            # This encodes the payload automatically based on the default
            # encoding for the charset
            if payload_from_string:
                payload.get_payload()[index] = payload
            else:
                payload.set_charset(charset)
        elif charset_match and not charset:
            # If a charset parameter was provided use it for header encoding
            # below, otherwise, try to use the charset provided in the message.
            charset = charset_match.groups()[0]
        return charset
    if payload.is_multipart():
        for index, payload in enumerate(payload.get_payload()):
            if payload.get_filename() is None:
                if not payload.is_multipart():
                    charset = _set_payload_charset(payload,
                                                   charset=charset,
                                                   index=index)
                else:
                    _set_recursive_charset(payload, charset=charset)
    else:
        charset = _set_payload_charset(payload, charset=charset)
    return charset


def _try_encode(text, charset):
    """Attempt to encode using the default charset if none is
    provided.  Should we permit encoding errors?"""
    if charset:
        return text.encode(charset)
    else:
        return text.encode()


def _encode_address_string(text, charset):
    """Split the email into parts and use header encoding on the name
    part if needed. We do this because the actual addresses need to be
    ASCII with no encoding for most SMTP servers, but the non-address
    parts should be encoded appropriately."""
    header = Header()
    name, addr = parseaddr(text)
    if isinstance(name, six.binary_type):
        try:
            name.decode('us-ascii')
        except UnicodeDecodeError:
            if charset:
                charset = Charset(charset)
                name = charset.header_encode(name)
    # We again replace rather than raise an error or pass an 8bit string
    header.append(formataddr((name, addr)), errors='replace')
    return header
