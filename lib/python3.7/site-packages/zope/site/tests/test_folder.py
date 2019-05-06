

import doctest
import unittest

from zope.site.folder import Folder
from zope.site.testing import siteSetUp, siteTearDown, checker
from zope.site.tests.test_site import TestSiteManagerContainer


def setUp(test=None):
    siteSetUp()


def tearDown(test=None):
    siteTearDown()


class FolderTest(TestSiteManagerContainer):

    def makeTestObject(self):
        return Folder()


def test_suite():
    flags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocTestSuite('zope.site.folder',
                             setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite("folder.txt",
                             setUp=setUp, tearDown=tearDown,
                             checker=checker, optionflags=flags),
    ))
