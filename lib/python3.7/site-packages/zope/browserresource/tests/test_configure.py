from zope.component.testing import setUp, tearDown
import doctest
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
            'configure.txt', setUp=setUp, tearDown=tearDown))
    return suite
