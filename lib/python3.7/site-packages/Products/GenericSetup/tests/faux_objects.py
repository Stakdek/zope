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
""" Simple, importable content classes.
"""

from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from zope.interface import implementer

from Products.GenericSetup.interfaces import ICSVAware
from Products.GenericSetup.interfaces import IDAVAware
from Products.GenericSetup.interfaces import IINIAware


class TestSimpleItem(SimpleItem):
    pass


class TestSimpleItemWithProperties(SimpleItem, PropertyManager):
    pass


KNOWN_CSV = """\
one,two,three
four,five,six
"""


@implementer(ICSVAware)
class TestCSVAware(SimpleItem):
    _was_put = None
    _csv = KNOWN_CSV

    def as_csv(self):
        return self._csv

    def put_csv(self, text):
        self._was_put = text


KNOWN_INI = """\
[DEFAULT]
title = %s
description = %s
"""


@implementer(IINIAware)
class TestINIAware(SimpleItem):
    _was_put = None
    title = 'INI title'
    description = 'INI description'

    def as_ini(self):
        return KNOWN_INI % (self.title, self.description)

    def put_ini(self, text):
        self._was_put = text


KNOWN_DAV = """\
Title: %s
Description: %s

%s
"""


@implementer(IDAVAware)
class TestDAVAware(SimpleItem):
    _was_put = None
    title = 'DAV title'
    description = 'DAV description'
    body = 'DAV body'

    def manage_FTPget(self):
        return KNOWN_DAV % (self.title, self.description, self.body)

    def PUT(self, REQUEST, RESPONSE):
        self._was_put = REQUEST.get('BODY', '')
        stream = REQUEST.get('BODYFILE', None)
        self._was_put_as_read = stream.read()
