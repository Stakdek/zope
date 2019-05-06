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
"""'mail' ZCML Namespaces Schemas
"""
__docformat__ = 'restructuredtext'

from zope.component import getUtility
from zope.component.zcml import handler
from zope.configuration.fields import Path
from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface
from zope.schema import TextLine, ASCIILine, Int, Bool

from zope.sendmail.delivery import QueuedMailDelivery, DirectMailDelivery
from zope.sendmail.interfaces import IMailer, IMailDelivery
from zope.sendmail.mailer import SMTPMailer
from zope.sendmail.queue import QueueProcessorThread

try:
    from zope.component.security import proxify
    from zope.security.zcml import Permission
except ImportError:  # pragma: no cover
    SECURITY_SUPPORT = False
    Permission = TextLine

    def _assertPermission(permission, interfaces, component):
        raise ConfigurationError(
            "security proxied components are not "
            "supported because zope.security is not available")
else:
    SECURITY_SUPPORT = True

    def _assertPermission(permission, interfaces, component):
        return proxify(component, provides=interfaces, permission=permission)


class IDeliveryDirective(Interface):
    """This abstract directive describes a generic mail delivery utility
    registration."""

    name = TextLine(
        title=u"Name",
        description=u'Specifies the Delivery name of the mail utility. '
                    u'The default is "Mail".',
        default=u"Mail",
        required=False)

    mailer = TextLine(
        title=u"Mailer",
        description=u"Defines the mailer to be used for sending mail.",
        required=True)

    permission = Permission(
        title=u"Permission",
        description=u"Defines the permission needed to use this service.",
        required=False)


class IQueuedDeliveryDirective(IDeliveryDirective):
    """This directive creates and registers a global queued mail utility. It
    should be only called once during startup."""

    queuePath = Path(
        title=u"Queue Path",
        description=u"Defines the path for the queue directory.",
        required=True)

    processorThread = Bool(
        title=u"Run Queue Processor Thread",
        description=(u"Indicates whether to run queue processor in a thread "
                     u"in this process."),
        required=False,
        default=True)


def _get_mailer(mailer):
    try:
        return getUtility(IMailer, mailer)
    except LookupError:
        raise ConfigurationError("Mailer %r is not defined" % mailer)


def queuedDelivery(_context, queuePath, mailer, permission=None, name="Mail",
                   processorThread=True):

    def createQueuedDelivery():
        delivery = QueuedMailDelivery(queuePath)
        if permission is not None:
            delivery = _assertPermission(permission, IMailDelivery, delivery)

        handler('registerUtility', delivery, IMailDelivery, name)

        mailerObject = _get_mailer(mailer)

        if processorThread:
            thread = QueueProcessorThread()
            thread.setMailer(mailerObject)
            thread.setQueuePath(queuePath)
            thread.start()

    _context.action(
        discriminator=('utility', IMailDelivery, name),
        callable=createQueuedDelivery,
        args=())


class IDirectDeliveryDirective(IDeliveryDirective):
    """This directive creates and registers a global direct mail utility. It
    should be only called once during startup."""


def directDelivery(_context, mailer, permission=None, name="Mail"):

    def createDirectDelivery():
        mailerObject = _get_mailer(mailer)

        delivery = DirectMailDelivery(mailerObject)
        if permission is not None:
            delivery = _assertPermission(permission, IMailDelivery, delivery)

        handler('registerUtility', delivery, IMailDelivery, name)

    _context.action(
        discriminator=('utility', IMailDelivery, name),
        callable=createDirectDelivery,
        args=())


class IMailerDirective(Interface):
    """A generic directive registering a mailer for the mail utility."""

    name = TextLine(
        title=u"Name",
        description=u"Name of the Mailer.",
        required=True)


class ISMTPMailerDirective(IMailerDirective):
    """Registers a new SMTP mailer."""

    hostname = ASCIILine(
        title=u"Hostname",
        description=u"Hostname of the SMTP host.",
        default="localhost",
        required=False)

    port = Int(
        title=u"Port",
        description=u"Port of the SMTP server.",
        default=25,
        required=False)

    username = TextLine(
        title=u"Username",
        description=u"A username for SMTP AUTH.",
        required=False)

    password = TextLine(
        title=u"Password",
        description=u"A password for SMTP AUTH.",
        required=False)


def smtpMailer(_context, name, hostname="localhost", port="25",
               username=None, password=None):
    _context.action(
        discriminator=('utility', IMailer, name),
        callable=handler,
        args=('registerUtility',
              SMTPMailer(hostname, port, username, password), IMailer, name)
    )
