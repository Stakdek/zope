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
"""Tests for browser:page directive and friends
"""

import os
import unittest
from io import StringIO

from zope import component
from zope.interface import Interface, implementer, directlyProvides

import zope.security.management
from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.browser import TestRequest

from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.security.proxy import removeSecurityProxy, ProxyFactory
from zope.security.permission import Permission
from zope.security.interfaces import IPermission
from zope.testing import cleanup
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable

import zope.publisher.defaultview
import zope.browserpage
import zope.browsermenu
from zope.browsermenu.menu import getFirstMenuItem
from zope.browsermenu.interfaces import IMenuItemType
#from zope.component.testfiles.views import IC, V1, VZMI, R1, IV

tests_path = os.path.dirname(__file__)

template = u"""<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""

class templateclass(object):
    def data(self):
        return 42

class IR(Interface):
    pass

class IV(Interface):
    def index():
        "A method"

class IC(Interface):
    pass

@implementer(IV)
class V1(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def index(self):
        return 'V1 here'

    def action(self):
        return 'done'

class VZMI(V1):
    def index(self):
        raise AssertionError("Not called")

@implementer(IV)
class R1(object):
    pass

class RZMI(R1):
    pass

class V2(V1, object):

    def action(self):
        return self.action2()

    def action2(self):
        return "done"

class VT(V1, object):
    def publishTraverse(self, request, name):
        raise AssertionError("Not called")

@implementer(IC)
class Ob(object):
    pass

ob = Ob()

class NCV(object):
    "non callable view"

    def __init__(self, context, request):
        pass

class CV(NCV):
    "callable view"
    def __call__(self):
        raise AssertionError("Not called")


@implementer(Interface)
class C_w_implements(NCV):

    def index(self):
        return self

class ITestLayer(IBrowserRequest):
    """Test Layer."""

class ITestSkin(ITestLayer):
    """Test Skin."""


class ITestMenu(Interface):
    """Test menu."""

directlyProvides(ITestMenu, IMenuItemType)

class Test(cleanup.CleanUp, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.browserpage)()
        XMLConfig('meta.zcml', zope.browsermenu)()
        component.provideAdapter(DefaultTraversable, (None,), ITraversable, )
        zope.security.management.newInteraction()
        self.request = TestRequest()

    def testPage(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)

        xmlconfig(StringIO(template % (
            '''
            <browser:page
                name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                attribute="index"
                />
            '''
            )))

        v = component.queryMultiAdapter((ob, self.request), name='test')
        self.assertTrue(issubclass(v.__class__, V1))


    def testPageWithClassWithMenu(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)
        testtemplate = os.path.join(tests_path, 'testfiles', 'test.pt')


        xmlconfig(StringIO(template % (
            '''
            <browser:menu
                id="test_menu" title="Test menu" />
            <browser:page
                name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                template="%s"
                menu="test_menu"
                title="Test View"
                />
            ''' % testtemplate
            )))
        menuItem = getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = component.queryMultiAdapter((ob, self.request), name='test')
        self.assertEqual(v().replace('\r\n', '\n'),
                         "<html><body><p>test</p></body></html>\n")


    def testPageWithTemplateWithMenu(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)
        testtemplate = os.path.join(tests_path, 'testfiles', 'test.pt')

        xmlconfig(StringIO(template % (
            '''
            <browser:menu
                id="test_menu" title="Test menu"/>
            <browser:page
                name="test"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                template="%s"
                menu="test_menu"
                title="Test View"
                />
            ''' % testtemplate
            )))

        menuItem = getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = component.queryMultiAdapter((ob, self.request), name='test')
        self.assertEqual(v().replace('\r\n', '\n'),
                         "<html><body><p>test</p></body></html>\n")


    def testPageInPagesWithTemplateWithMenu(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)
        testtemplate = os.path.join(tests_path, 'testfiles', 'test.pt')

        xmlconfig(StringIO(template % (
            '''
            <browser:menu
                id="test_menu" title="Test menu" />
            <browser:pages
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public">
              <browser:page
                  name="test"
                  template="%s"
                  menu="test_menu"
                  title="Test View"
                  />
            </browser:pages>
            ''' % testtemplate
            )))

        menuItem = getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = component.queryMultiAdapter((ob, self.request), name='test')
        self.assertEqual(v().replace('\r\n', '\n'),
                         "<html><body><p>test</p></body></html>\n")


    def testPageInPagesWithClassWithMenu(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)
        testtemplate = os.path.join(tests_path, 'testfiles', 'test.pt')

        xmlconfig(StringIO(template % (
            '''
            <browser:menu
                id="test_menu" title="Test menu" />
            <browser:pages
                for="zope.browserpage.tests.test_page.IC"
                class="zope.browserpage.tests.test_page.V1"
                permission="zope.Public">
              <browser:page
                  name="test"
                  template="%s"
                  menu="test_menu"
                  title="Test View"
                  />
            </browser:pages>
            ''' % testtemplate
            )))

        menuItem = getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = component.queryMultiAdapter((ob, self.request), name='test')
        self.assertEqual(v().replace('\r\n', '\n'),
                         "<html><body><p>test</p></body></html>\n")

    def testSkinPage(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:page name="test"
                class="zope.browserpage.tests.test_page.VZMI"
                for="zope.browserpage.tests.test_page.IC"
                layer="zope.browserpage.tests.test_page.ITestLayer"
                permission="zope.Public"
                attribute="index"
                />
            <browser:page name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                attribute="index"
                />
            '''
        ))

        v = component.queryMultiAdapter((ob, self.request), name='test')
        self.assertTrue(issubclass(v.__class__, V1))
        v = component.queryMultiAdapter(
            (ob, TestRequest(skin=ITestSkin)), name='test')
        self.assertTrue(issubclass(v.__class__, VZMI))


    def testInterfaceProtectedPage(self):
        xmlconfig(StringIO(
            template %
            u'''
            <browser:page name="test"
                class="zope.browserpage.tests.test_page.V1"
                attribute="index"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                allowed_interface="zope.browserpage.tests.test_page.IV"
                />
            '''
        ))

        v = component.getMultiAdapter((ob, self.request), name='test')
        v = ProxyFactory(v)
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedPage(self):
        xmlconfig(StringIO(
            template %
            u'''
            <browser:page name="test"
                class="zope.browserpage.tests.test_page.V2"
                for="zope.browserpage.tests.test_page.IC"
                attribute="action"
                permission="zope.Public"
                allowed_attributes="action2"
                />
            '''
        ))

        v = component.getMultiAdapter((ob, self.request), name='test')
        v = ProxyFactory(v)
        self.assertEqual(v.action(), 'done')
        self.assertEqual(v.action2(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testAttributeProtectedView(self):
        xmlconfig(StringIO(
            template %
            u'''
            <browser:view name="test"
                class="zope.browserpage.tests.test_page.V2"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                allowed_attributes="action2"
                >
              <browser:page name="index.html" attribute="action" />
           </browser:view>
            '''
        ))

        v = component.getMultiAdapter((ob, self.request), name='test')
        v = ProxyFactory(v)
        page = v.publishTraverse(self.request, 'index.html')
        self.assertEqual(page(), 'done')
        self.assertEqual(v.action2(), 'done')
        self.assertRaises(Exception, getattr, page, 'index')

    def testInterfaceAndAttributeProtectedPage(self):
        xmlconfig(StringIO(
            template %
            u'''
            <browser:page name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                attribute="index"
                allowed_attributes="action"
                allowed_interface="zope.browserpage.tests.test_page.IV"
                />
            '''
        ))

        v = component.getMultiAdapter((ob, self.request), name='test')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedPage(self):
        xmlconfig(StringIO(
            template %
            u'''
            <browser:page name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                attribute="index"
                permission="zope.Public"
                allowed_attributes="action index"
                allowed_interface="zope.browserpage.tests.test_page.IV"
                />
            '''
        ))

        v = component.getMultiAdapter((ob, self.request), name='test')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def test_class_w_implements(self):
        xmlconfig(StringIO(
            template %
            u'''
            <browser:page
                name="test"
                class="
             zope.browserpage.tests.test_page.C_w_implements"
                for="zope.browserpage.tests.test_page.IC"
                attribute="index"
                permission="zope.Public"
                />
            '''
        ))

        v = component.getMultiAdapter((ob, self.request), name='test')
        self.assertEqual(v.index(), v)
        self.assertTrue(IBrowserPublisher.providedBy(v))

    def testIncompleteProtectedPageNoPermission(self):
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(
                template %
                u'''
            <browser:page name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                attribute="index"
                allowed_attributes="action index"
                />
            '''
            ))


    def testPageViews(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)
        test3 = os.path.join(tests_path, 'testfiles', 'test3.pt')

        xmlconfig(StringIO(
            template %
            u'''
            <browser:pages
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                >

              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
              <browser:page name="test.html" template="%s" />
            </browser:pages>
            ''' % test3
        ))

        v = component.getMultiAdapter((ob, self.request), name='index.html')
        self.assertEqual(v(), 'V1 here')
        v = component.getMultiAdapter((ob, self.request), name='action.html')
        self.assertEqual(v(), 'done')
        v = component.getMultiAdapter((ob, self.request), name='test.html')
        self.assertEqual(str(v()).replace('\r\n', '\n'),
                         "<html><body><p>done</p></body></html>\n")

    def testNamedViewPageViewsCustomTraversr(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                >

              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
            </browser:view>
            '''
        ))

        view = component.getMultiAdapter((ob, self.request), name='test')
        view = removeSecurityProxy(view)
        self.assertEqual(view.browserDefault(self.request)[1], (u'index.html', ))


        v = view.publishTraverse(self.request, 'index.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'V1 here')
        v = view.publishTraverse(self.request, 'action.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'done')


    def testNamedViewNoPagesForCallable(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                name="test"
                class="zope.browserpage.tests.test_page.CV"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                />
            '''
        ))

        view = component.getMultiAdapter((ob, self.request), name='test')
        view = removeSecurityProxy(view)
        self.assertEqual(view.browserDefault(self.request), (view, ()))

    def testNamedViewNoPagesForNonCallable(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                name="test"
                class="zope.browserpage.tests.test_page.NCV"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                />
            '''
        ))

        view = component.getMultiAdapter((ob, self.request), name='test')
        view = removeSecurityProxy(view)
        self.assertEqual(getattr(view, 'browserDefault', None), None)

    def testNamedViewPageViewsNoDefault(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)
        test3 = os.path.join(tests_path, 'testfiles', 'test3.pt')

        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                >

              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
              <browser:page name="test.html" template="%s" />
            </browser:view>
            ''' % test3
        ))

        view = component.getMultiAdapter((ob, self.request), name='test')
        view = removeSecurityProxy(view)
        self.assertEqual(view.browserDefault(self.request)[1], (u'index.html', ))


        v = view.publishTraverse(self.request, 'index.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'V1 here')
        v = view.publishTraverse(self.request, 'action.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'done')
        v = view.publishTraverse(self.request, 'test.html')
        v = removeSecurityProxy(v)
        self.assertEqual(str(v()).replace('\r\n', '\n'),
                         "<html><body><p>done</p></body></html>\n")

    def testNamedViewPageViewsWithDefault(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)
        test3 = os.path.join(tests_path, u'testfiles', u'test3.pt')

        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                >

              <browser:defaultPage name="test.html" />
              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
              <browser:page name="test.html" template="%s" />
            </browser:view>
            ''' % test3
        ))

        view = component.getMultiAdapter((ob, self.request), name='test')
        view = removeSecurityProxy(view)
        self.assertEqual(view.browserDefault(self.request)[1], (u'test.html', ))


        v = view.publishTraverse(self.request, 'index.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'V1 here')
        v = view.publishTraverse(self.request, 'action.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'done')
        v = view.publishTraverse(self.request, 'test.html')
        v = removeSecurityProxy(v)
        self.assertEqual(str(v()).replace('\r\n', '\n'),
                         "<html><body><p>done</p></body></html>\n")

    def testTraversalOfPageForView(self):
        """Tests proper traversal of a page defined for a view."""

        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public" />

            <browser:page name="index.html"
                for="zope.browserpage.tests.test_page.IV"
                class="zope.browserpage.tests.test_page.CV"
                permission="zope.Public" />
            '''
        ))

        view = component.getMultiAdapter((ob, self.request), name='test')
        view = removeSecurityProxy(view)
        view.publishTraverse(self.request, 'index.html')

    def testTraversalOfPageForViewWithPublishTraverse(self):
        """Tests proper traversal of a page defined for a view.

        This test is different from testTraversalOfPageForView in that it
        tests the behavior on a view that has a publishTraverse method --
        the implementation of the lookup is slightly different in such a
        case.
        """
        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                name="test"
                class="zope.browserpage.tests.test_page.VT"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public" />

            <browser:page name="index.html"
                for="zope.browserpage.tests.test_page.IV"
                class="zope.browserpage.tests.test_page.CV"
                permission="zope.Public" />
            '''
        ))

        view = component.getMultiAdapter((ob, self.request), name='test')
        view = removeSecurityProxy(view)
        view.publishTraverse(self.request, 'index.html')

    def testProtectedPageViews(self):
        component.provideUtility(Permission('p', 'P'), IPermission, 'p')

        request = TestRequest()
        self.assertEqual(
            component.queryMultiAdapter((ob, request), name='test'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <include package="zope.security" file="meta.zcml" />

            <permission id="zope.TestPermission" title="Test permission" />

            <browser:pages
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.TestPermission"
                >

              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
            </browser:pages>
            '''
        ))

        v = component.getMultiAdapter((ob, request), name='index.html')
        v = ProxyFactory(v)
        zope.security.management.getInteraction().add(request)
        self.assertRaises(Exception, v)
        v = component.getMultiAdapter((ob, request), name='action.html')
        v = ProxyFactory(v)
        self.assertRaises(Exception, v)

    def testProtectedNamedViewPageViews(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <include package="zope.security" file="meta.zcml" />

            <permission id="zope.TestPermission" title="Test permission" />

            <browser:view
                name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                >

              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
            </browser:view>
            '''
        ))

        view = component.getMultiAdapter((ob, self.request), name='test')
        self.assertEqual(view.browserDefault(self.request)[1], (u'index.html', ))

        v = view.publishTraverse(self.request, 'index.html')
        self.assertEqual(v(), 'V1 here')

    def testSkinnedPageView(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='test'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:pages
                class="zope.browserpage.tests.test_page.V1"
                for="*"
                permission="zope.Public"
                >
              <browser:page name="index.html" attribute="index" />
            </browser:pages>

            <browser:pages
                class="zope.browserpage.tests.test_page.V1"
                for="*"
                layer="zope.browserpage.tests.test_page.ITestLayer"
                permission="zope.Public"
                >
              <browser:page name="index.html" attribute="action" />
            </browser:pages>
            '''
        ))

        v = component.getMultiAdapter((ob, self.request), name='index.html')
        self.assertEqual(v(), 'V1 here')
        v = component.getMultiAdapter((ob, TestRequest(skin=ITestSkin)),
                                      name='index.html')
        self.assertEqual(v(), 'done')


    def test_template_page(self):
        path = os.path.join(tests_path, 'testfiles', 'test.pt')

        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='index.html'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:page
                name="index.html"
                template="%s"
                permission="zope.Public"
                for="zope.browserpage.tests.test_page.IC" />
            ''' % path
        ))

        v = component.getMultiAdapter((ob, self.request), name='index.html')
        self.assertEqual(v().strip(), '<html><body><p>test</p></body></html>')

    def test_page_menu_within_different_layers(self):
        path = os.path.join(tests_path, 'testfiles', 'test.pt')
        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='index.html'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:menu
                id="test_menu"
                title="Test menu"
                interface="zope.browserpage.tests.test_page.ITestMenu"/>

            <browser:page
                name="index.html"
                permission="zope.Public"
                for="zope.browserpage.tests.test_page.IC"
                template="%s"
                menu="test_menu" title="Index"/>

            <browser:page
                name="index.html"
                permission="zope.Public"
                for="zope.browserpage.tests.test_page.IC"
                menu="test_menu" title="Index"
                template="%s"
                layer="zope.browserpage.tests.test_page.ITestLayer"/>
            ''' % (path, path)
            ))

        v = component.getMultiAdapter((ob, self.request), name='index.html')
        self.assertEqual(v().strip(), '<html><body><p>test</p></body></html>')

    def testtemplateWClass(self):
        path = os.path.join(tests_path, 'testfiles', 'test2.pt')

        self.assertEqual(
            component.queryMultiAdapter((ob, self.request), name='index.html'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:page
                name="index.html"
                template="%s"
                permission="zope.Public"
          class="zope.browserpage.tests.test_page.templateclass"
                for="zope.browserpage.tests.test_page.IC" />
            ''' % path
        ))

        v = component.getMultiAdapter((ob, self.request), name='index.html')
        self.assertEqual(v().strip(), '<html><body><p>42</p></body></html>')

    def testProtectedtemplate(self):

        path = os.path.join(tests_path, 'testfiles', 'test.pt')

        request = TestRequest()
        self.assertEqual(
            component.queryMultiAdapter((ob, request), name='test'),
            None)

        xmlconfig(StringIO(
            template %
            u'''
            <include package="zope.security" file="meta.zcml" />

            <permission id="zope.TestPermission" title="Test permission" />

            <browser:page
                name="xxx.html"
                template="%s"
                permission="zope.TestPermission"
                for="zope.browserpage.tests.test_page.IC" />
            ''' % path
        ))

        xmlconfig(StringIO(
            template %
            u'''
            <browser:page
                name="index.html"
                template="%s"
                permission="zope.Public"
                for="zope.browserpage.tests.test_page.IC" />
            ''' % path
        ))

        v = component.getMultiAdapter((ob, request), name='xxx.html')
        v = ProxyFactory(v)
        zope.security.management.getInteraction().add(request)
        self.assertRaises(Exception, v)

        v = component.getMultiAdapter((ob, request), name='index.html')
        v = ProxyFactory(v)
        self.assertEqual(v().strip(), '<html><body><p>test</p></body></html>')


    def testtemplateNoName(self):
        path = os.path.join(tests_path, 'testfiles', 'test.pt')
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(
                template %
                u'''
            <browser:page
                template="%s"
                for="zope.browserpage.tests.test_page.IC"
                />
            ''' % path
            ))

    def testtemplateAndPage(self):
        path = os.path.join(tests_path, u'testfiles', u'test.pt')
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(
                template %
                u'''
            <browser:view
                name="index.html"
                template="%s"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                >
              <browser:page name="foo.html" attribute="index" />
            </browser:view>
            ''' % path
            ))

    def testViewThatProvidesAnInterface(self):
        request = TestRequest()
        self.assertEqual(
            component.queryMultiAdapter((ob, request), IV, name='test'), None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                />
            '''
        ))

        v = component.queryMultiAdapter((ob, request), IV, name='test')
        self.assertEqual(v, None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                name="test"
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                provides="zope.browserpage.tests.test_page.IV"
                permission="zope.Public"
                />
            '''
        ))

        v = component.queryMultiAdapter((ob, request), IV, name='test')
        self.assertTrue(isinstance(v, V1))

    def testUnnamedViewThatProvidesAnInterface(self):
        request = TestRequest()
        self.assertEqual(component.queryMultiAdapter((ob, request), IV),
                         None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                permission="zope.Public"
                />
            '''
        ))

        v = component.queryMultiAdapter((ob, request), IV)
        self.assertEqual(v, None)

        xmlconfig(StringIO(
            template %
            u'''
            <browser:view
                class="zope.browserpage.tests.test_page.V1"
                for="zope.browserpage.tests.test_page.IC"
                provides="zope.browserpage.tests.test_page.IV"
                permission="zope.Public"
                />
            '''
        ))

        v = component.queryMultiAdapter((ob, request), IV)

        self.assertTrue(isinstance(v, V1))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
