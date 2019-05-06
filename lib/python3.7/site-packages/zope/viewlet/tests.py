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
"""Viewlet tests
"""
import os
import doctest
import re
import sys
import unittest

import zope.component
from zope.component import eventtesting
from zope.traversing.testing import setUp as traversingSetUp
from zope.testing import cleanup, renormalizing

from zope.viewlet import manager as managers

class TestWeightOrderedViewletManager(unittest.TestCase):

    def test_render_no_viewlets(self):
        manager = managers.WeightOrderedViewletManager(None, None, None)
        self.assertEqual(u'', manager.render())

    def test_render_with_template(self):
        manager = managers.WeightOrderedViewletManager(None, None, None)
        manager.template = lambda viewlets: viewlets
        manager.viewlets = self

        self.assertIs(self, manager.render())

    def test_render_without_template(self):
        manager = managers.WeightOrderedViewletManager(None, None, None)

        class Viewlet(object):
            def render(self):
                return u"Hi"

        manager.viewlets = [Viewlet(), Viewlet()]

        self.assertEqual(u"Hi\nHi", manager.render())


class TestViewletManagerBase(unittest.TestCase):

    # Avoid DeprecationWarning for assertRaisesRegexp on Python 3 while
    # coping with Python 2 not having the Regex spelling variant
    assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegex',
                                unittest.TestCase.assertRaisesRegexp)

    def test_unauthorized(self):
        from zope.security.interfaces import Unauthorized
        import zope.security

        orig_query = zope.component.queryMultiAdapter
        orig_canAccess = zope.security.canAccess

        def query(*args, **kwargs):
            return self
        def canAccess(*args):
            return False

        zope.component.queryMultiAdapter = query
        self.addCleanup(lambda: setattr(zope.component, 'queryMultiAdapter', orig_query))
        zope.security.canAccess = canAccess
        self.addCleanup(lambda: setattr(zope.security, 'canAccess', orig_canAccess))


        manager = managers.ViewletManagerBase(None, None, None)
        with self.assertRaisesRegex(Unauthorized,
                                    "You are not authorized to access the provider"):

            manager['name']

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    ])


def doctestSetUp(test):
    cleanup.setUp()
    eventtesting.setUp()
    traversingSetUp()

    # resource namespace setup
    from zope.traversing.interfaces import ITraversable
    from zope.traversing.namespace import resource
    zope.component.provideAdapter(
        resource, (None,), ITraversable, name="resource")
    zope.component.provideAdapter(
        resource, (None, None), ITraversable, name="resource")

    from zope.browserpage import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

def doctestTearDown(test):
    cleanup.tearDown()

class FakeModule(object):
    """A fake module."""

    def __init__(self, dict):
        self.__dict__ = dict


def directivesSetUp(test):
    doctestSetUp(test)
    test.globs['__name__'] = 'zope.viewlet.directives'
    sys.modules['zope.viewlet.directives'] = FakeModule(test.globs)

def directivesTearDown(test):
    doctestTearDown(test)
    del sys.modules[test.globs['__name__']]
    test.globs.clear()

def test_suite():
    flags = (doctest.NORMALIZE_WHITESPACE
             | doctest.ELLIPSIS
             | doctest.IGNORE_EXCEPTION_DETAIL)

    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTests((
        doctest.DocFileSuite(
            'README.rst',
            setUp=doctestSetUp, tearDown=doctestTearDown,
            optionflags=flags, checker=checker,
            globs={
                '__file__': os.path.join(
                    os.path.dirname(__file__), 'README.rst')}
        ),
        doctest.DocFileSuite(
            'directives.rst',
            setUp=directivesSetUp, tearDown=directivesTearDown,
            optionflags=flags, checker=checker,
            globs={'__file__': os.path.join(
                os.path.dirname(__file__), 'directives.rst')}
        ),
    ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
