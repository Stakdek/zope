##############################################################################
#
# Copyright (c) 2005-2009 Zope Foundation and Contributors.
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
"""
import os
import os.path
import unittest

from zope.browserpage import namedtemplate

import zope.component.testing
import zope.traversing.adapters

class TestImplementation(unittest.TestCase):

    def test_call(self):
        inst = namedtemplate.implementation(None)


        nt = namedtemplate.NamedTemplate('name')
        nti = inst(nt)

        self.assertEqual(nti.descriptor, nt)

class TestNamedTemplateImplementation(unittest.TestCase):

    def test_bad_descriptor(self):
        with self.assertRaises(TypeError):
            namedtemplate.NamedTemplateImplementation(None)


class TestNamedTemplate(unittest.TestCase):

    def test_no_instance(self):
        class X(object):
            nt = namedtemplate.NamedTemplate('name')

        self.assertIsInstance(X.nt, namedtemplate.NamedTemplate)

    def test_call_no_adapter(self):
        class X(object):
            nt = namedtemplate.NamedTemplate('name')

        with self.assertRaises(LookupError):
            getattr(X(), 'nt')

        with self.assertRaises(LookupError):
            X.nt(X())

class TestNamedTemplatePathAdapter(unittest.TestCase):

    def test_getitem_no_adapter(self):

        adapter = namedtemplate.NamedTemplatePathAdapter(self)

        with self.assertRaises(LookupError):
            _ = adapter['name']

def pageSetUp(test):
    zope.component.testing.setUp(test)
    zope.component.provideAdapter(
        zope.traversing.adapters.DefaultTraversable,
        [None],
    )


def test_suite():
    import doctest
    filename = os.path.join(os.pardir, 'namedtemplate.rst')
    return unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocFileSuite(
            filename,
            setUp=pageSetUp, tearDown=zope.component.testing.tearDown,
            globs={'__file__':  os.path.abspath(os.path.join(os.path.dirname(__file__), filename))}
        )
    ])
