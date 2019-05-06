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
"""MailHost export / import support.
"""

import six

from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import XMLAdapterBase
from Products.MailHost.interfaces import IMailHost
from zope.component import adapts


class MailHostXMLAdapter(XMLAdapterBase):

    """XML im- and exporter for MailHost.
    """

    adapts(IMailHost, ISetupEnviron)

    _LOGGER_ID = 'mailhost'

    name = 'mailhost'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.setAttribute('smtp_host', str(self.context.smtp_host))
        node.setAttribute('smtp_port', str(self.context.smtp_port))
        smtp_uid = self.context.smtp_uid
        if smtp_uid is None:
            # None would give an AttributeError during export.
            smtp_uid = ''
        node.setAttribute('smtp_uid', smtp_uid)
        smtp_pwd = self.context.smtp_pwd
        if smtp_pwd is None:
            smtp_pwd = ''
        node.setAttribute('smtp_pwd', smtp_pwd)

        # Older MH instances won't have 'smtp_queue' in instance dict
        smtp_queue = bool(getattr(self.context, 'smtp_queue', False))
        node.setAttribute('smtp_queue', str(smtp_queue))

        qdir = getattr(self.context, 'smtp_queue_directory', '/tmp')
        if qdir is None:
            qdir = ''
        node.setAttribute('smtp_queue_directory', str(qdir))

        self._logger.info('Mailhost exported.')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        self.context.smtp_host = str(node.getAttribute('smtp_host'))
        self.context.smtp_port = int(node.getAttribute('smtp_port'))
        smtp_uid = node.getAttribute('smtp_uid')
        smtp_pwd = node.getAttribute('smtp_pwd')
        if six.PY2:
            # ??? Why?
            self.context.smtp_uid = smtp_uid.encode('utf-8')
            self.context.smtp_pwd = smtp_pwd.encode('utf-8')
        else:
            self.context.smtp_uid = smtp_uid
            self.context.smtp_pwd = smtp_pwd

        # Older MH instances won't have 'smtp_queue' in instance dict
        if 'smtp_queue' in self.context.__dict__:
            if node.hasAttribute('smtp_queue'):
                queue = node.getAttribute('smtp_queue')
                self.context.smtp_queue = self._convertToBoolean(queue)
            if node.hasAttribute('smtp_queue_directory'):
                qd = node.getAttribute('smtp_queue_directory')
                self.context.smtp_queue_directory = str(qd)

        self._logger.info('Mailhost imported.')
