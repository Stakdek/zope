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
"""Container constraint tests
"""
import unittest

class TestUnaddableError(unittest.TestCase):

    def test_str(self):
        from zope.container.interfaces import UnaddableError
        e = UnaddableError("'container'", "'obj'", "Extra")
        self.assertEqual(str(e),
                         "'obj' cannot be added to 'container': Extra")

class TestCheckObject(unittest.TestCase):

    def test_non_container(self):
        from zope.container.constraints import checkObject

        with self.assertRaisesRegexp(TypeError,
                                     "Container is not a valid Zope container."):
            checkObject({}, 'foo', 42)


class TestCheckFactory(unittest.TestCase):

    def test_no_validate_on_parent(self):
        # Does nothing if no constraints are provided
        from zope.container.constraints import checkFactory

        class Factory(object):
            def getInterfaces(self):
                return {}

        result = checkFactory({}, 'name', Factory())
        self.assertTrue(result)


class TestTypesBased(unittest.TestCase):

    def test_raw_types(self):
        from zope.container.constraints import _TypesBased

        t = _TypesBased('.TestTypesBased', module=__name__)
        self.assertEqual(t.types, [TestTypesBased])

    def test_raw_types_property(self):
        from zope.container.constraints import _TypesBased

        t = _TypesBased.types
        self.assertTrue(hasattr(t, '__get__'))

def test_suite():
    import doctest
    from zope.container import testing
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocTestSuite(
            'zope.container.constraints',
            checker=testing.checker),
        doctest.DocFileSuite(
            '../constraints.rst',
            checker=testing.checker),
    ))
