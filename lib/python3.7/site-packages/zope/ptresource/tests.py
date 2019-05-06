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
"""Page Template based Resources Test
"""
import os
import tempfile
import unittest

from zope.component import provideAdapter
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import NotFound
from zope.security.checker import NamesChecker
from zope.testing import cleanup
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable

from zope.ptresource.ptresource import PageTemplateResourceFactory
from zope.ptresource.ptresource import PageTemplateResource
from zope.ptresource.ptresource import PageTemplate

checker = NamesChecker(('__call__', 'request', 'publishTraverse'))


class Test(cleanup.CleanUp, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        provideAdapter(DefaultTraversable, (None,), ITraversable)

    def createTestFile(self, contents):
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        f.write(contents)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def testNoTraversal(self):
        path = self.createTestFile('<html><body><p>test</p></body></html>')
        request = TestRequest()
        factory = PageTemplateResourceFactory(path, checker, 'test.pt')
        resource = factory(request)
        self.assertRaises(NotFound, resource.publishTraverse,
                          resource.request, ())

    def testBrowserDefault(self):
        path = self.createTestFile(
            '<html><body tal:content="request/test_data"></body></html>')
        test_data = "Foobar"
        request = TestRequest(test_data=test_data)
        factory = PageTemplateResourceFactory(path, checker, 'testresource.pt')
        resource = factory(request)
        view, next = resource.browserDefault(request)
        self.assertEqual(view(),
                         '<html><body>%s</body></html>' % test_data)
        self.assertEqual('text/html',
                         request.response.getHeader('Content-Type'))
        self.assertEqual(next, ())

        request = TestRequest(test_data=test_data, REQUEST_METHOD='HEAD')
        resource = factory(request)
        view, next = resource.browserDefault(request)
        self.assertEqual(view(), '')
        self.assertEqual('text/html',
                         request.response.getHeader('Content-Type'))
        self.assertEqual(next, ())

    def testContentType(self):
        path = self.createTestFile('<html><body><p>test</p></body></html>')
        request = TestRequest()
        pt = PageTemplate(path, content_type='text/xhtml')

        resource = PageTemplateResource(pt, request)
        resource.GET()
        self.assertEqual('text/xhtml',
                         request.response.getHeader('Content-Type'))

    def testConfigure(self):
        from zope.configuration import xmlconfig
        import zope.ptresource
        xmlconfig.file('configure.zcml', zope.ptresource)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
