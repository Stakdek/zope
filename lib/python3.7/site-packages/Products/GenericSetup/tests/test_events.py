import unittest
from zope.interface.verify import verifyObject
from Products.GenericSetup.events import BeforeProfileImportEvent
from Products.GenericSetup.interfaces import IBeforeProfileImportEvent
from Products.GenericSetup.events import ProfileImportedEvent
from Products.GenericSetup.interfaces import IProfileImportedEvent


class BaseEventTests:

    def testInterface(self):
        event = self.klass("tool", "profile_id", "steps", "full_import")
        verifyObject(self.iface, event)

    def testNormalConstruction(self):
        event = self.klass("tool", "profile_id", "steps", "full_import")
        self.assertEqual(event.tool, "tool")
        self.assertEqual(event.profile_id, "profile_id")
        self.assertEqual(event.steps, "steps")
        self.assertEqual(event.full_import, "full_import")

    def testKeywordConstruction(self):
        event = self.klass(tool="tool", profile_id="profile_id", steps="steps",
                           full_import="full_import")
        self.assertEqual(event.tool, "tool")
        self.assertEqual(event.profile_id, "profile_id")
        self.assertEqual(event.steps, "steps")
        self.assertEqual(event.full_import, "full_import")


class BeforeProfileImportEventTests(BaseEventTests, unittest.TestCase):
    klass = BeforeProfileImportEvent
    iface = IBeforeProfileImportEvent


class ProfileImportedEventTests(BaseEventTests, unittest.TestCase):
    klass = ProfileImportedEvent
    iface = IProfileImportedEvent


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BeforeProfileImportEventTests))
    suite.addTest(unittest.makeSuite(ProfileImportedEventTests))
    return suite
