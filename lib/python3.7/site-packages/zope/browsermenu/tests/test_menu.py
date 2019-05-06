##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Browser Menu Item Tests
"""
import doctest
import pprint
import re
import unittest
from zope.testing import cleanup, renormalizing

from zope.component import ComponentLookupError
from zope.browsermenu import menu

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    # Python 3 changed builtins name.
    (re.compile('__builtin__'),
     r"builtins"),
    # Python 3 renamed type to class.
    (re.compile('<type'),
     r"<class"),
    # Python 3 adds module name to exceptions.
    (re.compile("zope.configuration.exceptions.ConfigurationError"),
     r"ConfigurationError"),
    ])

class Request(object):

    def __init__(self, url):
        self._url = url

    def getURL(self):
        return self._url

class TestMenuAccessView(unittest.TestCase):

    def test_getitem(self):
        v = menu.MenuAccessView(None, None)
        with self.assertRaises(ComponentLookupError):
            _ = v['id']


class TestBrowserMenuItem(unittest.TestCase):

    def test_selected_ends_with_action(self):
        req = Request('/action')
        item = menu.BrowserMenuItem(None, req)
        item.action = 'action'

        self.assertTrue(item.selected())

    def test_available_with_query(self):
        req = Request('/action?query')
        item = menu.BrowserMenuItem(None, req)
        item.action = 'action?query'
        self.assertFalse(item.available())

    def test_available_filter_unauthorized(self):
        from zope.security.interfaces import Unauthorized

        req = Request('/action')
        item = menu.BrowserMenuItem(None, req)

        filter_called = []
        def f(_):
            filter_called.append(True)
            raise Unauthorized()

        item.filter = f

        self.assertFalse(item.available())
        self.assertTrue(filter_called)


def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocFileSuite(
            '../README.txt',
            setUp=lambda test: cleanup.setUp(),
            tearDown=lambda test: cleanup.tearDown(),
            globs={'pprint': pprint.pprint},
            checker=checker,
            optionflags=doctest.NORMALIZE_WHITESPACE),
    ))
