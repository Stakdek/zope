##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""
Unit test logic for setting up and tearing down basic infrastructure.

This relies on :mod:`zope.publisher` being available.
"""

import re

from zope.testing import renormalizing

rules = []
if bytes is not str:
    rules = [
        (re.compile("u('.*?')"), r"\1"),
        (re.compile('u(".*?")'), r"\1"),
    ]
unicode_checker = renormalizing.RENormalizing(rules)


def setUp(test=None):
    import zope.component
    from zope.publisher.browser import BrowserLanguages
    from zope.publisher.http import HTTPCharsets
    zope.component.provideAdapter(HTTPCharsets)
    zope.component.provideAdapter(BrowserLanguages)


class PlacelessSetup(object):

    def setUp(self):
        """
        Install the language and charset negotiators.

        >>> PlacelessSetup().setUp()
        >>> from zope.publisher.browser import TestRequest
        >>> from zope.i18n.interfaces import IUserPreferredCharsets
        >>> from zope.i18n.interfaces import IUserPreferredLanguages
        >>> from zope.component import getAdapter
        >>> getAdapter(TestRequest(), IUserPreferredCharsets)
        <zope.publisher.http.HTTPCharsets ...>
        >>> getAdapter(TestRequest(), IUserPreferredLanguages)
        <zope.publisher.browser.BrowserLanguages ...>

        """
        setUp()
