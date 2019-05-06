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
"""Test the Choice display and edit widget (function).
"""
import unittest
from zope.component.testing import PlacelessSetup
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import TestRequest
from zope.schema.interfaces import IChoice, IIterableVocabulary
from zope.schema import Choice

from zope.component import provideAdapter
from zope.formlib.interfaces import IInputWidget, IDisplayWidget
from zope.formlib.widgets import ChoiceDisplayWidget, ChoiceInputWidget
from zope.formlib.widgets import ItemDisplayWidget, DropdownWidget


class ChoiceWidgetTest(PlacelessSetup, unittest.TestCase):

    def test_ChoiceDisplayWidget(self):
        provideAdapter(ItemDisplayWidget,
                       (IChoice, IIterableVocabulary, IBrowserRequest),
                       IDisplayWidget)
        field = Choice(values=[1, 2, 3])
        bound = field.bind(object())
        widget = ChoiceDisplayWidget(bound, TestRequest())
        self.assertTrue(isinstance(widget, ItemDisplayWidget))
        self.assertEqual(widget.context, bound)
        self.assertEqual(widget.vocabulary, bound.vocabulary)
    
    def test_ChoiceInputWidget(self):
        provideAdapter(DropdownWidget,
                       (IChoice, IIterableVocabulary, IBrowserRequest),
                       IInputWidget)
        field = Choice(values=[1, 2, 3])
        bound = field.bind(object())
        widget = ChoiceInputWidget(bound, TestRequest())
        self.assertTrue(isinstance(widget, DropdownWidget))
        self.assertEqual(widget.context, bound)
        self.assertEqual(widget.vocabulary, bound.vocabulary)
        


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ChoiceWidgetTest),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
