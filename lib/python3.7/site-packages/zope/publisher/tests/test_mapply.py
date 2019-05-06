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
"""Test mapply() function
"""
import unittest

from zope.publisher.publish import mapply
from zope.publisher._compat import PYTHON2


class AncientMethodCode(object):
    """Pretend to be pre Python 2.6 method code.

    See https://docs.python.org/2/reference/datamodel.html
    """

    def __init__(self, code, defaults=None):
        self.my_code = code
        self.func_defaults = defaults

    def actual_func(self, first, second=None):
        if second is None:
            second = self.func_defaults[0]
        return eval(self.my_code % (first, second))

    @property
    def func_code(self):
        return self.actual_func.__code__

    def __call__(self, *args, **kwargs):
        return self.actual_func(*args, **kwargs)


class AncientMethod(object):
    """Pretend to be a Python 2.6 method.

    Before Python 2.6, methods did not have __func__ and __code__.
    They had im_func and func_code instead.
    This may still be the case for RestrictedPython scripts.

    See https://docs.python.org/2/reference/datamodel.html
    """

    def __init__(self, code, defaults=None):
        self.im_func = AncientMethodCode(code, defaults=defaults)

    def __call__(self, *args, **kwargs):
        return self.im_func(*args, **kwargs)


class MapplyTests(unittest.TestCase):
    def testMethod(self):
        def compute(a,b,c=4):
            return '%d%d%d' % (a, b, c)
        values = {'a':2, 'b':3, 'c':5}
        v = mapply(compute, (), values)
        self.assertEqual(v, '235')

        v = mapply(compute, (7,), values)
        self.assertEqual(v, '735')

    def testClass(self):
        values = {'a':2, 'b':3, 'c':5}
        class c(object):
            a = 3
            def __call__(self, b, c=4):
                return '%d%d%d' % (self.a, b, c)
            compute = __call__
        cc = c()
        v = mapply(cc, (), values)
        self.assertEqual(v, '335')

        del values['c']
        v = mapply(cc.compute, (), values)
        self.assertEqual(v, '334')

    def testClassicClass(self):
        if not PYTHON2:
            # Classic classes are only available in py3
            return

        values = {'a':2, 'b':3}
        class c(object):
            a = 3
            def __call__(self, b, c=4):
                return '%d%d%d' % (self.a, b, c)
            compute = __call__
        cc = c()

        class c2:
            """Must be a classic class."""

        c2inst = c2()
        c2inst.__call__ = cc
        v = mapply(c2inst, (), values)
        self.assertEqual(v, '334')

    def testAncientMethod(self):
        # Before Python 2.6, methods did not have __func__ and __code__.
        # They had im_func and func_code instead.
        # This may still be the case for RestrictedPython scripts.
        # Pretend a method that accepts one argument and one keyword argument.
        # The default value for the keyword argument is given as a tuple.
        method = AncientMethod('7 * %d + %d', (0,))
        values = {}
        v = mapply(method, (6,), values)
        self.assertEqual(v, 42)
        v = mapply(method, (5, 4), values)
        self.assertEqual(v, 39)


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(MapplyTests)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
