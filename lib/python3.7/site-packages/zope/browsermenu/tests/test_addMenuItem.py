#############################################################################
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
"""Test the addMenuItem directive

>>> from zope.browsermenu.metaconfigure import addMenuItem
>>> context = Context()
>>> addMenuItem(context, class_=X, title="Add an X",
...             permission="zope.ManageContent")
>>> context
[('utility',
  <InterfaceClass zope.component.interfaces.IFactory>,
  'BrowserAdd__zope.browsermenu.tests.test_addMenuItem.X'),
 (<function provideInterface>,
  <InterfaceClass zope.component.interfaces.IFactory>),
 ('adapter',
  (<InterfaceClass zope.browser.interfaces.IAdding>,
   <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
  <InterfaceClass zope.browsermenu.interfaces.AddMenu>,
  'Add an X'),
 (<function provideInterface>,
  <InterfaceClass zope.browsermenu.interfaces.AddMenu>),
 (<function provideInterface>,
  <InterfaceClass zope.browser.interfaces.IAdding>),
 (<function provideInterface>,
  <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>)]
"""

import unittest
from doctest import DocTestSuite
import re
import pprint
import io

from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component.interface import provideInterface
from zope.browsermenu.metaconfigure import _checkViewFor

from zope.configuration.xmlconfig import XMLConfig

import zope.browsermenu
import zope.component
from zope.testing import cleanup

atre = re.compile(' at [0-9a-fA-Fx]+')

class IX(Interface):
    pass

class X(object):
    pass

class ILayerStub(IBrowserRequest):
    pass

class MenuStub(object):
    pass


class Context(object):
    info = ''

    def __init__(self):
        self.actions = []

    def action(self, discriminator, callable, args=(), kw=None, order=0):
        if discriminator is None:
            if callable is provideInterface:
                self.actions.append((callable, args[1])) #name is args[0]
            elif callable is _checkViewFor:
                self.actions.append((callable, args[2]))
        else:
            self.actions.append(discriminator)

    def __repr__(self):
        stream = io.BytesIO() if str is bytes else io.StringIO()
        pprinter = pprint.PrettyPrinter(stream=stream, width=60)
        pprinter.pprint(self.actions)
        r = stream.getvalue()
        return (''.join(atre.split(r))).strip()


def test_w_factory():
    """
    >>> from zope.browsermenu.metaconfigure import addMenuItem
    >>> context = Context()
    >>> addMenuItem(context, factory="x.y.z", title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo")
    >>> context
    [('adapter',
      (<InterfaceClass zope.browser.interfaces.IAdding>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>,
      'Add an X'),
     (<function provideInterface>,
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>),
     (<function provideInterface>,
      <InterfaceClass zope.browser.interfaces.IAdding>),
     (<function provideInterface>,
      <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>)]
    """

def test_w_factory_and_view():
    """
    >>> from zope.browsermenu.metaconfigure import addMenuItem

    >>> context = Context()
    >>> addMenuItem(context, factory="x.y.z", title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo", view="AddX")
    >>> context
    [(<function _checkViewFor>, 'AddX'),
     ('adapter',
      (<InterfaceClass zope.browser.interfaces.IAdding>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>,
      'Add an X'),
     (<function provideInterface>,
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>),
     (<function provideInterface>,
      <InterfaceClass zope.browser.interfaces.IAdding>),
     (<function provideInterface>,
      <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>)]
    """

def test_w_factory_class_view():
    """
    >>> from zope.browsermenu.metaconfigure import addMenuItem

    >>> context = Context()
    >>> addMenuItem(context, class_=X, title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo", view="AddX")
    >>> import pprint
    >>> context
    [('utility',
      <InterfaceClass zope.component.interfaces.IFactory>,
      'BrowserAdd__zope.browsermenu.tests.test_addMenuItem.X'),
     (<function provideInterface>,
      <InterfaceClass zope.component.interfaces.IFactory>),
     (<function _checkViewFor>, 'AddX'),
     ('adapter',
      (<InterfaceClass zope.browser.interfaces.IAdding>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>,
      'Add an X'),
     (<function provideInterface>,
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>),
     (<function provideInterface>,
      <InterfaceClass zope.browser.interfaces.IAdding>),
     (<function provideInterface>,
      <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>)]
    """

def test_w_for_factory():
    """
    >>> from zope.browsermenu.metaconfigure import addMenuItem

    >>> context = Context()
    >>> addMenuItem(context, for_=IX, factory="x.y.z", title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo")
    >>> context
    [(<function provideInterface>,
      <InterfaceClass zope.browsermenu.tests.test_addMenuItem.IX>),
     ('adapter',
      (<InterfaceClass zope.browsermenu.tests.test_addMenuItem.IX>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>,
      'Add an X'),
     (<function provideInterface>,
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>),
     (<function provideInterface>,
      <InterfaceClass zope.browsermenu.tests.test_addMenuItem.IX>),
     (<function provideInterface>,
      <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>)]
    """

def test_w_factory_layer():
    """
    >>> from zope.browsermenu.metaconfigure import addMenuItem

    >>> context = Context()
    >>> addMenuItem(context, factory="x.y.z", title="Add an X", layer=ILayerStub,
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo")
    >>> context
    [('adapter',
      (<InterfaceClass zope.browser.interfaces.IAdding>,
       <InterfaceClass zope.browsermenu.tests.test_addMenuItem.ILayerStub>),
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>,
      'Add an X'),
     (<function provideInterface>,
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>),
     (<function provideInterface>,
      <InterfaceClass zope.browser.interfaces.IAdding>),
     (<function provideInterface>,
      <InterfaceClass zope.browsermenu.tests.test_addMenuItem.ILayerStub>)]
    """

def test_w_for_menu_factory():
    """
    >>> from zope.browsermenu.metaconfigure import addMenuItem

    >>> context = Context()
    >>> addMenuItem(context, for_=IX, menu=MenuStub,
    ...             factory="x.y.z", title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo")
    >>> context
    [(<function provideInterface>,
      <InterfaceClass zope.browsermenu.tests.test_addMenuItem.IX>),
     ('adapter',
      (<InterfaceClass zope.browsermenu.tests.test_addMenuItem.IX>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      <class 'zope.browsermenu.tests.test_addMenuItem.MenuStub'>,
      'Add an X'),
     (<function provideInterface>,
      <class 'zope.browsermenu.tests.test_addMenuItem.MenuStub'>),
     (<function provideInterface>,
      <InterfaceClass zope.browsermenu.tests.test_addMenuItem.IX>),
     (<function provideInterface>,
      <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>)]
    """

def test_w_factory_icon_extra_order():
    """
    >>> from zope.browsermenu.metaconfigure import addMenuItem

    >>> context = Context()
    >>> addMenuItem(context, factory="x.y.z", title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo", icon=u'/@@/icon.png', extra='Extra',
    ...             order=99)
    >>> context
    [('adapter',
      (<InterfaceClass zope.browser.interfaces.IAdding>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>,
      'Add an X'),
     (<function provideInterface>,
      <InterfaceClass zope.browsermenu.interfaces.AddMenu>),
     (<function provideInterface>,
      <InterfaceClass zope.browser.interfaces.IAdding>),
     (<function provideInterface>,
      <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>)]
    """


class TestAddMenuItem(cleanup.CleanUp, unittest.TestCase):

    def setUp(self):
        super(TestAddMenuItem, self).setUp()
        XMLConfig('meta.zcml', zope.component)()
        XMLConfig('meta.zcml', zope.browsermenu)()

    def test_addMenuItemDirectives(self):
        XMLConfig('tests/addmenuitems.zcml', zope.browsermenu)()

def test_suite():
    return unittest.TestSuite((
        DocTestSuite(),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))
