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

import unittest


class TestMethodObject(unittest.TestCase):

    def test_compilation(self):
        from ExtensionClass import _IS_PYPY
        try:
            from MethodObject import _MethodObject
        except ImportError: # pragma: no cover
            self.assertTrue(_IS_PYPY)
        else:
            self.assertTrue(hasattr(_MethodObject, 'Method'))

    def test_methodobject(self):
        from ExtensionClass import Base
        from MethodObject import Method

        class Callable(Method):
            def __call__(self, ob, *args, **kw):
                return (repr(ob), args, kw)

        class ExClass(Base):
            def __repr__(self):
                return "bar()"

            hi = Callable()

        x = ExClass()
        hi = x.hi
        result = hi(1, 2, 3, name='spam')

        self.assertEqual(result,
                         ("bar()", (1, 2, 3), {'name': 'spam'}))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
