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
"""Container Traverser tests.
"""
from __future__ import absolute_import
import unittest
from zope.testing.cleanup import CleanUp
from zope.interface import implementer
from zope.traversing.interfaces import TraversalError

from zope.container.traversal import ContainerTraversable
from zope.container.interfaces import IContainer
import six

@implementer(IContainer)
class Container(object):

    def __init__(self, attrs=None, objs=None):
        for attr, value in six.iteritems(attrs or {}):
            setattr(self, attr, value)

        self.__objs = {}
        for name, value in six.iteritems(objs or {}):
            self.__objs[name] = value

    def get(self, name, default=None):
        return self.__objs.get(name, default)


class Test(CleanUp, unittest.TestCase):
    def testAttr(self):
        # test container path traversal
        foo = Container()
        bar = Container()
        baz = Container()
        c = Container({'foo': foo}, {'bar': bar, 'foo': baz})

        T = ContainerTraversable(c)
        self.assertTrue(T.traverse('foo', []) is baz)
        self.assertTrue(T.traverse('bar', []) is bar)
        self.assertRaises(TraversalError, T.traverse, 'morebar', [])

    def test_unicode_obj(self):
        # test traversal with unicode
        voila = Container()
        c = Container({}, {u'voil\xe0': voila})
        self.assertIs(ContainerTraversable(c).traverse(u'voil\xe0', []),
                      voila)

    def test_unicode_attr(self):
        c = Container()
        with self.assertRaises(TraversalError):
            ContainerTraversable(c).traverse(u'voil\xe0', [])


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main()
