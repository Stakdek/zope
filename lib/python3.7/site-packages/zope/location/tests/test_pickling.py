##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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


import zope.copy

class LocationCopyHookTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.location.pickling import LocationCopyHook
        return LocationCopyHook

    def _makeOne(self, obj=None):
        if obj is None:
            obj = object()
        return self._getTargetClass()(obj)

    def test_class_conforms_to_ICopyHook(self):
        from zope.interface.verify import verifyClass
        from zope.copy.interfaces import ICopyHook
        verifyClass(ICopyHook, self._getTargetClass())

    def test_instance_conforms_to_ICopyHook(self):
        from zope.interface.verify import verifyObject
        from zope.copy.interfaces import ICopyHook
        verifyObject(ICopyHook, self._makeOne())

    def test___call___w_context_inside_toplevel(self):
        from zope.copy.interfaces import ResumeCopy
        class Dummy(object):
            __parent__ = __name__ = None
        top_level = Dummy()
        context = Dummy()
        context.__parent__ = top_level
        hook = self._makeOne(context)
        self.assertRaises(ResumeCopy, hook, top_level, object())

    def test___call___w_context_outside_toplevel(self):
        class Dummy(object):
            __parent__ = __name__ = None
        top_level = Dummy()
        context = Dummy()
        hook = self._makeOne(context)
        self.assertTrue(hook(top_level, object()) is context)



def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
