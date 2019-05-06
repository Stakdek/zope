##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

class DatabaseOpenedTests(unittest.TestCase):
    def _getTargetClass(self):
        from zope.processlifetime import DatabaseOpened
        return DatabaseOpened

    def test_class_conforms_to_IDatabaseOpened(self):
        from zope.interface.verify import verifyClass
        from zope.processlifetime import IDatabaseOpened
        verifyClass(IDatabaseOpened, self._getTargetClass())

    def test_instance_conforms_to_IDatabaseOpened(self):
        from zope.interface.verify import verifyObject
        from zope.processlifetime import IDatabaseOpened
        verifyObject(IDatabaseOpened, self._getTargetClass()(object()))

class DatabaseOpenedWithRootTests(unittest.TestCase):
    def _getTargetClass(self):
        from zope.processlifetime import DatabaseOpenedWithRoot
        return DatabaseOpenedWithRoot

    def test_class_conforms_to_IDatabaseOpenedWithRoot(self):
        from zope.interface.verify import verifyClass
        from zope.processlifetime import IDatabaseOpenedWithRoot
        verifyClass(IDatabaseOpenedWithRoot, self._getTargetClass())

    def test_instance_conforms_to_IDatabaseOpenedWithRoot(self):
        from zope.interface.verify import verifyObject
        from zope.processlifetime import IDatabaseOpenedWithRoot
        verifyObject(IDatabaseOpenedWithRoot, self._getTargetClass()(object()))

class ProcessStartingTests(unittest.TestCase):
    def _getTargetClass(self):
        from zope.processlifetime import ProcessStarting
        return ProcessStarting

    def test_class_conforms_to_IProcessStarting(self):
        from zope.interface.verify import verifyClass
        from zope.processlifetime import IProcessStarting
        verifyClass(IProcessStarting, self._getTargetClass())

    def test_instance_conforms_to_IProcessStarting(self):
        from zope.interface.verify import verifyObject
        from zope.processlifetime import IProcessStarting
        verifyObject(IProcessStarting, self._getTargetClass()())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
