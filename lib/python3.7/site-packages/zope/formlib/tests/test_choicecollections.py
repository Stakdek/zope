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
"""Test the choice collections widgets (function).
"""
import unittest
from zope.component.testing import PlacelessSetup
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import TestRequest
from zope.schema.interfaces import IList, IChoice, IIterableVocabulary
from zope.schema import Choice, List

from zope.component import provideAdapter

from zope.formlib.interfaces import IInputWidget, IDisplayWidget
from zope.formlib.widgets import CollectionDisplayWidget
from zope.formlib.widgets import CollectionInputWidget
from zope.formlib.widgets import ChoiceCollectionDisplayWidget
from zope.formlib.widgets import ChoiceCollectionInputWidget
from zope.formlib.widgets import ItemsMultiDisplayWidget, SelectWidget

class ListOfChoicesWidgetTest(PlacelessSetup, unittest.TestCase):

    def test_ListOfChoicesDisplayWidget(self):
        provideAdapter(ChoiceCollectionDisplayWidget,
                       (IList, IChoice, IBrowserRequest),
                       IDisplayWidget)
        provideAdapter(ItemsMultiDisplayWidget,
                       (IList, IIterableVocabulary, IBrowserRequest),
                       IDisplayWidget)
        field = List(value_type=Choice(values=[1, 2, 3]))
        bound = field.bind(object())
        widget = CollectionDisplayWidget(bound, TestRequest())
        self.assertTrue(isinstance(widget, ItemsMultiDisplayWidget))
        self.assertEqual(widget.context, bound)
        self.assertEqual(widget.vocabulary, bound.value_type.vocabulary)


    def test_ChoiceSequenceEditWidget(self):
        provideAdapter(ChoiceCollectionInputWidget,
                       (IList, IChoice, IBrowserRequest),
                       IInputWidget)
        provideAdapter(SelectWidget,
                       (IList, IIterableVocabulary, IBrowserRequest),
                       IInputWidget)
        field = List(value_type=Choice(values=[1, 2, 3]))
        bound = field.bind(object())
        widget = CollectionInputWidget(bound, TestRequest())
        self.assertTrue(isinstance(widget, SelectWidget))
        self.assertEqual(widget.context, bound)
        self.assertEqual(widget.vocabulary, bound.value_type.vocabulary)
        


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ListOfChoicesWidgetTest),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
