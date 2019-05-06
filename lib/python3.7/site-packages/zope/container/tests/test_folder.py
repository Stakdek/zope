from unittest import TestCase, makeSuite

from zope.container.folder import Folder
from zope.container.tests.test_icontainer import TestSampleContainer

import pickle

class Test(TestSampleContainer, TestCase):

    def makeTestObject(self):
        return Folder()

    def testDataAccess(self):
        folder = self.makeTestObject()
        self.assertNotEqual(folder.data, None)
        folder.data = 'foo'
        self.assertEqual(folder.data, 'foo')

    def testPickleCompatibility(self):
        folder = self.makeTestObject()
        folder['a'] = 1
        self.assertEqual(folder.__getstate__()['data'], folder._SampleContainer__data)

        folder_clone = pickle.loads(pickle.dumps(folder))
        self.assertEqual(folder_clone['a'], folder['a'])


def test_suite():
    return makeSuite(Test)
