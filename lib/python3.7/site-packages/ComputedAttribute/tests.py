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
"""Computed Attributes

Computed attributes work much like properties:

>>> import math
>>> from ComputedAttribute import ComputedAttribute
>>> from ExtensionClass import Base
>>> class Point(Base):
...    def __init__(self, x, y):
...        self.x, self.y = x, y
...    length = ComputedAttribute(lambda self: math.sqrt(self.x**2+self.y**2))

>>> p = Point(3, 4)
>>> "%.1f" % p.length
'5.0'

Except that you can also use computed attributes with instances:

>>> p.angle = ComputedAttribute(lambda self: math.atan(self.y*1.0/self.x))
>>> "%.2f" % p.angle
'0.93'
"""

from doctest import DocTestSuite
import unittest

from ComputedAttribute import ComputedAttribute
from ExtensionClass import Base


def test_wrapper_support():
    """Wrapper support

    To support acquisition wrappers, computed attributes have a level.
    The computation is only done when the level is zero. Retrieving a
    computed attribute with a level > 0 returns a computed attribute
    with a decremented level.

    >>> from ExtensionClass import Base
    >>> class X(Base):
    ...     pass

    >>> x = X()
    >>> x.n = 1

    >>> from ComputedAttribute import ComputedAttribute
    >>> x.n2 = ComputedAttribute(lambda self: self.n*2)
    >>> x.n2
    2
    >>> x.n2.__class__.__name__
    'int'

    >>> x.n2 = ComputedAttribute(lambda self: self.n*2, 2)
    >>> x.n2.__class__.__name__
    'ComputedAttribute'
    >>> x.n2 = x.n2
    >>> x.n2.__class__.__name__
    'ComputedAttribute'
    >>> x.n2 = x.n2
    >>> x.n2.__class__.__name__
    'int'
    """


class TestComputedAttribute(unittest.TestCase):
    def _construct_class(self, level):
        class X(Base):
            def _get_a(self):
                return 1

            a = ComputedAttribute(_get_a, level)

        return X

    def test_computed_attribute_on_class_level0(self):
        x = self._construct_class(0)()
        self.assertEqual(x.a, 1)

    def test_computed_attribute_on_class_level1(self):
        x = self._construct_class(1)()
        self.assertIsInstance(x.a, ComputedAttribute)

    def test_compilation(self):
        from ExtensionClass import _IS_PYPY
        try:
            from ComputedAttribute import _ComputedAttribute
        except ImportError: # pragma: no cover
            self.assertTrue(_IS_PYPY)
        else:
            self.assertTrue(hasattr(_ComputedAttribute, 'ComputedAttribute'))

def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTest(DocTestSuite())
    return suite
