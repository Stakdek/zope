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
"""File-based browser resource tests.
"""

import doctest
import os
import re
import unittest
from email.utils import formatdate
import time

from zope.component import getGlobalSiteManager
from zope.component import provideAdapter, adapter
from zope.interface import implementer
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security.checker import NamesChecker

from zope.testing import cleanup
from zope.testing.renormalizing import RENormalizing

from zope.browserresource.file import FileResourceFactory, FileETag
from zope.browserresource.interfaces import IFileResource, IETag


@adapter(IFileResource, IBrowserRequest)
@implementer(IETag)
class MyETag(object):

    def __init__(self, context, request):
        pass

    def __call__(self, mtime, content):
        return 'myetag'


@adapter(IFileResource, IBrowserRequest)
@implementer(IETag)
class NoETag(object):

    def __init__(self, context, request):
        pass

    def __call__(self, mtime, content):
        return None



def setUp(test):
    cleanup.setUp()
    data_dir = os.path.join(os.path.dirname(__file__), 'testfiles')

    test.globs['testFilePath'] = os.path.join(data_dir, 'test.txt')
    test.globs['nullChecker'] = NamesChecker()
    test.globs['TestRequest'] = TestRequest
    provideAdapter(MyETag)


def tearDown(test):
    cleanup.tearDown()

class TestFile(unittest.TestCase):


    def setUp(self):
        cleanup.setUp()
        data_dir = os.path.join(os.path.dirname(__file__), 'testfiles')

        self.testFilePath = os.path.join(data_dir, 'test.txt')
        self.nullChecker = NamesChecker()
        provideAdapter(MyETag)

    def tearDown(self):
        cleanup.tearDown()

    def test_FileETag(self):
        # Tests for FileETag

        etag_maker = FileETag(object(), TestRequest())
        self.assertTrue(verifyObject(IETag, etag_maker))

        # By default we constuct an ETag from the file's mtime and size

        self.assertEqual(etag_maker(1234, 'abc'), '1234-3')

    def test_FileResource_GET_sets_cache_headers(self):
        # Test caching headers set by FileResource.GET
        factory = FileResourceFactory(self.testFilePath, self.nullChecker, 'test.txt')

        timestamp = time.time()

        file = factory._FileResourceFactory__file # get mangled file
        file.lmt = timestamp
        file.lmh = formatdate(timestamp, usegmt=True)

        request = TestRequest()
        resource = factory(request)
        self.assertTrue(resource.GET())

        self.assertEqual(request.response.getHeader('Last-Modified'), file.lmh)

        self.assertEqual(request.response.getHeader('ETag'),
                         '"myetag"')
        self.assertEqual(request.response.getHeader('Cache-Control'),
                         'public,max-age=86400')
        self.assertTrue(request.response.getHeader('Expires'))

    def test_FileResource_GET_if_modified_since(self):
        #Test If-Modified-Since header support

        factory = FileResourceFactory(self.testFilePath, self.nullChecker, 'test.txt')

        timestamp = time.time()

        file = factory._FileResourceFactory__file # get mangled file
        file.lmt = timestamp
        file.lmh = formatdate(timestamp, usegmt=True)

        before = timestamp - 1000
        request = TestRequest(HTTP_IF_MODIFIED_SINCE=formatdate(before, usegmt=True))
        resource = factory(request)
        self.assertTrue(resource.GET())

        after = timestamp + 1000
        request = TestRequest(HTTP_IF_MODIFIED_SINCE=formatdate(after, usegmt=True))
        resource = factory(request)
        self.assertFalse(resource.GET())

        self.assertEqual(request.response.getStatus(),
                         304)

        # Cache control headers and ETag are set on 304 responses

        self.assertEqual(request.response.getHeader('ETag'),
                         '"myetag"')
        self.assertEqual(request.response.getHeader('Cache-Control'),
                         'public,max-age=86400')
        self.assertTrue(request.response.getHeader('Expires'))

        # Other entity headers are not

        self.assertIsNone(request.response.getHeader('Last-Modified'))
        self.assertIsNone(request.response.getHeader('Content-Type'))

        # It won't fail on bad If-Modified-Since headers.

        request = TestRequest(HTTP_IF_MODIFIED_SINCE='bad header')
        resource = factory(request)
        self.assertTrue(resource.GET())

        # it also won't fail if we don't have a last modification time for the
        # resource

        file.lmt = None
        request = TestRequest(HTTP_IF_MODIFIED_SINCE=formatdate(after, usegmt=True))
        resource = factory(request)
        self.assertTrue(resource.GET())

    def test_FileResource_GET_if_none_match(self):
        # Test If-None-Match header support

        factory = FileResourceFactory(self.testFilePath, self.nullChecker, 'test.txt')

        timestamp = time.time()

        file = factory._FileResourceFactory__file # get mangled file
        file.lmt = timestamp
        file.lmh = formatdate(timestamp, usegmt=True)

        request = TestRequest(HTTP_IF_NONE_MATCH='"othertag"')
        resource = factory(request)
        self.assertTrue(resource.GET())

        request = TestRequest(HTTP_IF_NONE_MATCH='"myetag"')
        resource = factory(request)
        self.assertEqual(resource.GET(), b'')

        self.assertEqual(request.response.getStatus(),
                         304)

        # Cache control headers and ETag are set on 304 responses

        self.assertEqual(request.response.getHeader('ETag'),
                         '"myetag"')
        self.assertEqual(request.response.getHeader('Cache-Control'),
                         'public,max-age=86400')
        self.assertTrue(request.response.getHeader('Expires'))

        # Other entity headers are not

        self.assertIsNone(request.response.getHeader('Last-Modified'))
        self.assertIsNone(request.response.getHeader('Content-Type'))

        # It won't fail on bad If-None-Match headers.

        request = TestRequest(HTTP_IF_NONE_MATCH='bad header')
        resource = factory(request)
        self.assertTrue(resource.GET())

        # it also won't fail if we don't have an etag for the resource

        provideAdapter(NoETag)
        request = TestRequest(HTTP_IF_NONE_MATCH='"someetag"')
        resource = factory(request)
        self.assertTrue(resource.GET())

    def test_FileResource_GET_if_none_match_and_if_modified_since(self):
        # Test combined If-None-Match and If-Modified-Since header support

        factory = FileResourceFactory(self.testFilePath, self.nullChecker, 'test.txt')

        timestamp = time.time()

        file = factory._FileResourceFactory__file # get mangled file
        file.lmt = timestamp
        file.lmh = formatdate(timestamp, usegmt=True)

        # We've a match

        after = timestamp + 1000
        request = TestRequest(HTTP_IF_MODIFIED_SINCE=formatdate(after, usegmt=True),
                              HTTP_IF_NONE_MATCH='"myetag"')
        resource = factory(request)
        self.assertFalse(resource.GET())

        self.assertEqual(request.response.getStatus(),
                         304)

        # Last-modified matches, but ETag doesn't

        request = TestRequest(HTTP_IF_MODIFIED_SINCE=formatdate(after, usegmt=True),
                              HTTP_IF_NONE_MATCH='"otheretag"')
        resource = factory(request)
        self.assertTrue(resource.GET())

        # ETag matches but last-modified doesn't

        before = timestamp - 1000
        request = TestRequest(HTTP_IF_MODIFIED_SINCE=formatdate(before, usegmt=True),
                              HTTP_IF_NONE_MATCH='"myetag"')
        resource = factory(request)
        self.assertTrue(resource.GET())


        # Both don't match

        before = timestamp - 1000
        request = TestRequest(HTTP_IF_MODIFIED_SINCE=formatdate(before, usegmt=True),
                              HTTP_IF_NONE_MATCH='"otheretag"')
        resource = factory(request)
        self.assertTrue(resource.GET())

    def test_FileResource_GET_works_without_IETag_adapter(self):
        # Test backwards compatibility with users of <3.11 that do not provide an ETagAdatper

        getGlobalSiteManager().unregisterAdapter(MyETag)
        factory = FileResourceFactory(self.testFilePath, self.nullChecker, 'test.txt')
        request = TestRequest()
        resource = factory(request)
        self.assertTrue(resource.GET())
        self.assertIsNone(request.response.getHeader('ETag'))


def test_suite():
    checker = RENormalizing([
        # Python 3 includes module name in exceptions
        (re.compile(r"zope.publisher.interfaces.NotFound"),
         "NotFound"),
    ])

    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocTestSuite(
            'zope.browserresource.file',
            setUp=setUp, tearDown=tearDown,
            checker=checker,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE),
    ))
