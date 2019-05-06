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

import sys
import unittest
from io import BytesIO

from zope.interface import implementer, directlyProvides, Interface
from zope.interface.verify import verifyObject

from zope.publisher.publish import publish as publish_
from zope.publisher.http import HTTPCharsets
from zope.publisher.browser import BrowserRequest
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import ISkinnable
from zope.publisher.interfaces.browser import IBrowserApplicationRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserPublication
from zope.publisher.base import DefaultPublication

from zope.publisher._compat import PYTHON2, _u
from zope.publisher.tests.test_http import HTTPTests
from zope.publisher.tests.publication import TestPublication

from zope.publisher.tests.basetestipublicationrequest \
     import BaseTestIPublicationRequest
from zope.publisher.tests.basetestipublisherrequest \
     import BaseTestIPublisherRequest
from zope.publisher.tests.basetestiapplicationrequest \
     import BaseTestIApplicationRequest

LARGE_FILE_BODY = b''.join([b"""-----------------------------1
Content-Disposition: form-data; name="upload"; filename="test"
Content-Type: text/plain

Here comes some text! """, (b'test'*1000), b"""
-----------------------------1--
"""])

LARGE_POSTED_VALUE = b''.join([b"""-----------------------------1
Content-Disposition: form-data; name="upload"

Here comes some text! """, (b'test'*1000), b"""
-----------------------------1--
"""])

IE_FILE_BODY = b"""-----------------------------1
Content-Disposition: form-data; name="upload"; filename="C:\\Windows\\notepad.exe"
Content-Type: text/plain

Some data
-----------------------------1--
"""

if not PYTHON2:
    unicode = str


def publish(request):
    publish_(request, handle_errors=0)

class Publication(DefaultPublication):

    def getDefaultTraversal(self, request, ob):
        if hasattr(ob, 'browserDefault'):
            return ob.browserDefault(request)
        return ob, ()

class TestBrowserRequest(BrowserRequest, HTTPCharsets):
    """Make sure that our request also implements IHTTPCharsets, so that we do
    not need to register any adapters."""

    def __init__(self, *args, **kw):
        self.request = self
        BrowserRequest.__init__(self, *args, **kw)


class BrowserTests(HTTPTests):

    _testEnv =  {
        'PATH_INFO':           '/folder/item',
        'QUERY_STRING':        'a=5&b:int=6',
        'SERVER_URL':          'http://foobar.com',
        'HTTP_HOST':           'foobar.com',
        'CONTENT_LENGTH':      '0',
        'HTTP_AUTHORIZATION':  'Should be in accessible',
        'GATEWAY_INTERFACE':   'TestFooInterface/1.0',
        'HTTP_OFF_THE_WALL':   "Spam 'n eggs",
        'HTTP_ACCEPT_CHARSET': 'ISO-8859-1, UTF-8;q=0.66, UTF-16;q=0.33',
    }

    def setUp(self):
        super(BrowserTests, self).setUp()

        class AppRoot(object):
            """Required docstring for the publisher."""

        class Folder(object):
            """Required docstring for the publisher."""

        class Item(object):
            """Required docstring for the publisher."""
            def __call__(self, a, b):
                return _u("%s, %s") % (repr(a).lstrip('u'), repr(b).lstrip('u'))

        class Item3(object):
            """Required docstring for the publisher."""
            def __call__(self, *args):
                return _u("...")

        class View(object):
            """Required docstring for the publisher."""
            def browserDefault(self, request):
                return self, ['index']

            def index(self, a, b):
                """Required docstring for the publisher."""
                return _u("%s, %s") % (repr(a).lstrip('u'), repr(b).lstrip('u'))

        class Item2(object):
            """Required docstring for the publisher."""
            view = View()

            def browserDefault(self, request):
                return self, ['view']


        self.app = AppRoot()
        self.app.folder = Folder()
        self.app.folder.item = Item()
        self.app.folder.item2 = Item2()
        self.app.folder.item3 = Item3()

    def _createRequest(self, extra_env={}, body=b""):
        env = self._testEnv.copy()
        env.update(extra_env)
        if len(body):
            env['CONTENT_LENGTH'] = str(len(body))

        publication = Publication(self.app)
        instream = BytesIO(body)
        request = TestBrowserRequest(instream, env)
        request.setPublication(publication)
        return request

    def testTraversalToItem(self):
        res = self._publisherResults()
        self.assertEqual(
            res,
            "Status: 200 Ok\r\n"
            "X-Powered-By: Zope (www.zope.org), Python (www.python.org)\r\n"
            "Content-Length: 6\r\n"
            "Content-Type: text/plain;charset=utf-8\r\n"
            "X-Content-Type-Warning: guessed from content\r\n"
            "\r\n"
            "'5', 6")

    def testNoDefault(self):
        request = self._createRequest()
        response = request.response
        publish(request)
        self.assertFalse(response.getBase())

    def testDefault(self):
        extra = {'PATH_INFO': '/folder/item2'}
        request = self._createRequest(extra)
        response = request.response
        publish(request)
        self.assertEqual(response.getBase(),
                         'http://foobar.com/folder/item2/view/index')

    def testDefaultPOST(self):
        extra = {'PATH_INFO': '/folder/item2', "REQUEST_METHOD": "POST"}
        request = self._createRequest(extra, body=b'a=5&b:int=6')
        response = request.response
        publish(request)
        self.assertEqual(response.getBase(),
                         'http://foobar.com/folder/item2/view/index')

    def testNoneFieldNamePost(self):

        """Produce a Fieldstorage with a name wich is None, this
        should be catched"""

        extra = {'REQUEST_METHOD':'POST',
                 'PATH_INFO': _u("/"),
                 'CONTENT_TYPE': 'multipart/form-data;\
                 boundary=---------------------------1'}

        body = b"""-----------------------------1
        Content-Disposition: form-data; name="field.contentType"
        ...
        application/octet-stream
        -----------------------------1--
        """
        request  = self._createRequest(extra,body=body)
        request.processInputs()

    def testFileUploadPost(self):
        """Produce a Fieldstorage with a file handle that exposes
        its filename."""

        extra = {'REQUEST_METHOD':'POST',
                 'PATH_INFO': _u("/"),
                 'CONTENT_TYPE': 'multipart/form-data;\
                 boundary=---------------------------1'}

        request  = self._createRequest(extra, body=LARGE_FILE_BODY)
        request.processInputs()
        self.assertTrue(request.form['upload'].name)

        request  = self._createRequest(extra, body=IE_FILE_BODY)
        request.processInputs()
        self.assertEqual(request.form['upload'].filename, 'notepad.exe')

        # Test that we can actually read the file data
        self.assertEqual(request.form['upload'].read(), b'Some data')

    def testLargePostValue(self):
        extra = {'REQUEST_METHOD':'POST',
                 'PATH_INFO': _u("/"),
                 'CONTENT_TYPE': 'multipart/form-data;\
                 boundary=---------------------------1'}

        request  = self._createRequest(extra, body=LARGE_POSTED_VALUE)
        request.processInputs()

    def testDefault2(self):
        extra = {'PATH_INFO': '/folder/item2/view'}
        request = self._createRequest(extra)
        response = request.response
        publish(request)
        self.assertEqual(response.getBase(),
                         'http://foobar.com/folder/item2/view/index')

    def testDefault3(self):
        extra = {'PATH_INFO': '/folder/item2/view/index'}
        request = self._createRequest(extra)
        response = request.response
        publish(request)
        self.assertFalse(response.getBase())

    def testDefault4(self):
        extra = {'PATH_INFO': '/folder/item2/view/'}
        request = self._createRequest(extra)
        response = request.response
        publish(request)
        self.assertFalse(response.getBase())

    def testDefault6(self):
        extra = {'PATH_INFO': '/folder/item2/'}
        request = self._createRequest(extra)
        response = request.response
        publish(request)
        self.assertEqual(response.getBase(),
                         'http://foobar.com/folder/item2/view/index')

    def testBadPath(self):
        extra = {'PATH_INFO': '/folder/nothere/'}
        request = self._createRequest(extra)
        self.assertRaises(NotFound, publish, request)

    def testBadPath2(self):
        extra = {'PATH_INFO': '/folder%2Fitem2/'}
        request = self._createRequest(extra)
        self.assertRaises(NotFound, publish, request)

    def testForm(self):
        request = self._createRequest()
        publish(request)
        self.assertEqual(request.form,
                         {_u("a"):_u("5"), _u("b"):6})

    def testFormNoEncodingUsesUTF8(self):
        encoded = 'K\xc3\xb6hlerstra\xc3\x9fe'
        extra = {
            # if nothing else is specified, form data should be
            # interpreted as UTF-8, as this stub query string is
            'QUERY_STRING': 'a=5&b:int=6&street=' + encoded
            }
        request = self._createRequest(extra)
        # many mainstream browsers do not send HTTP_ACCEPT_CHARSET
        del request._environ['HTTP_ACCEPT_CHARSET']
        publish(request)
        self.assertTrue(isinstance(request.form[_u("street")], unicode))
        self.assertEqual(_u("K\xf6hlerstra\xdfe"), request.form['street'])

    def testFormAcceptsStarButNotUTF8(self):
        extra = {
            'QUERY_STRING': 'a=5&b:int=6&latin_1=\xf6', # latin-1
            'HTTP_ACCEPT_CHARSET': 'utf-8;q=0.7, *;q=0.7',
            }
        request = self._createRequest(extra)
        # don't error when * is in ACCEPT_CHARSET and data is not UTF-8
        publish(request)

    def testFormListTypes(self):
        extra = {'QUERY_STRING':'a:list=5&a:list=6&b=1'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"):[_u("5"),_u("6")], _u("b"):_u("1")})

    def testQueryStringIgnoredForPOST(self):
        request = self._createRequest(
            {"REQUEST_METHOD": "POST",
             'PATH_INFO': '/folder/item3'}, body=b'c=5&d:int=6')
        publish(request)
        self.assertEqual(request.form, {_u("c"): _u("5"), _u("d"): 6})
        self.assertEqual(request.get('QUERY_STRING'), 'a=5&b:int=6')

    def testFormTupleTypes(self):
        extra = {'QUERY_STRING':'a:tuple=5&a:tuple=6&b=1'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"):(_u("5"),_u("6")), _u("b"):_u("1")})

    def testFormTupleRecordTypes(self):
        extra = {'QUERY_STRING':'a.x:tuple:record=5&a.x:tuple:record=6&b=1'}
        request = self._createRequest(extra)
        publish(request)
        keys = sorted(request.form.keys())
        self.assertEqual(keys, [_u("a"),_u("b")])
        self.assertEqual(request.form[_u("b")], _u("1"))
        self.assertEqual(list(request.form[_u("a")].keys()), [_u("x")])
        self.assertEqual(request.form[_u("a")][_u("x")], (_u("5"),_u("6")))
        self.assertEqual(request.form[_u("a")].x, (_u("5"),_u("6")))
        self.assertEqual(str(request.form[_u("a")]).replace("u'", "'"),
                         "{x: ('5', '6')}")
        self.assertEqual(repr(request.form[_u("a")]).replace("u'", "'"),
                         "{x: ('5', '6')}")

    def testFormRecordsTypes(self):
        extra = {'QUERY_STRING':'a.x:records=5&a.x:records=6&b=1'}
        request = self._createRequest(extra)
        publish(request)
        keys = sorted(request.form.keys())
        self.assertEqual(keys, [_u("a"),_u("b")])
        self.assertEqual(request.form[_u("b")], _u("1"))
        self.assertEqual(len(request.form[_u("a")]), 2)
        self.assertEqual(request.form[_u("a")][0][_u("x")], _u("5"))
        self.assertEqual(request.form[_u("a")][0].x, _u("5"))
        self.assertEqual(request.form[_u("a")][1][_u("x")], _u("6"))
        self.assertEqual(request.form[_u("a")][1].x, _u("6"))
        self.assertEqual(str(request.form[_u("a")]).replace("u'", "'"),
                         "[{x: '5'}, {x: '6'}]")
        self.assertEqual(repr(request.form[_u("a")]).replace("u'", "'"),
                         "[{x: '5'}, {x: '6'}]")

    def testFormMultipleRecordsTypes(self):
        extra = {'QUERY_STRING':'a.x:records:int=5&a.y:records:int=51'
            '&a.x:records:int=6&a.y:records:int=61&b=1'}
        request = self._createRequest(extra)
        publish(request)
        keys = sorted(request.form.keys())
        self.assertEqual(keys, [_u("a"),_u("b")])
        self.assertEqual(request.form[_u("b")], _u("1"))
        self.assertEqual(len(request.form[_u("a")]), 2)
        self.assertEqual(request.form[_u("a")][0][_u("x")], 5)
        self.assertEqual(request.form[_u("a")][0].x, 5)
        self.assertEqual(request.form[_u("a")][0][_u("y")], 51)
        self.assertEqual(request.form[_u("a")][0].y, 51)
        self.assertEqual(request.form[_u("a")][1][_u("x")], 6)
        self.assertEqual(request.form[_u("a")][1].x, 6)
        self.assertEqual(request.form[_u("a")][1][_u("y")], 61)
        self.assertEqual(request.form[_u("a")][1].y, 61)
        self.assertEqual(str(request.form[_u("a")]),
            "[{x: 5, y: 51}, {x: 6, y: 61}]")
        self.assertEqual(repr(request.form[_u("a")]),
            "[{x: 5, y: 51}, {x: 6, y: 61}]")

    def testFormListRecordTypes(self):
        extra = {'QUERY_STRING':'a.x:list:record=5&a.x:list:record=6&b=1'}
        request = self._createRequest(extra)
        publish(request)
        keys = sorted(request.form.keys())
        self.assertEqual(keys, [_u("a"),_u("b")])
        self.assertEqual(request.form[_u("b")], _u("1"))
        self.assertEqual(list(request.form[_u("a")].keys()), [_u("x")])
        self.assertEqual(request.form[_u("a")][_u("x")], [_u("5"),_u("6")])
        self.assertEqual(request.form[_u("a")].x, [_u("5"),_u("6")])
        self.assertEqual(str(request.form[_u("a")]).replace("u'", "'"),
                         "{x: ['5', '6']}")
        self.assertEqual(repr(request.form[_u("a")]).replace("u'", "'"),
                         "{x: ['5', '6']}")

    def testFormListTypes2(self):
        extra = {'QUERY_STRING':'a=5&a=6&b=1'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"):[_u("5"),_u("6")], _u("b"):_u("1")})

    def testFormIntTypes(self):
        extra = {'QUERY_STRING':'a:int=5&b:int=-5&c:int=0&d:int=-0'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"): 5, _u("b"): -5, _u("c"): 0, _u("d"): 0})

        extra = {'QUERY_STRING':'a:int='}
        request = self._createRequest(extra)
        self.assertRaises(ValueError, publish, request)

        extra = {'QUERY_STRING':'a:int=abc'}
        request = self._createRequest(extra)
        self.assertRaises(ValueError, publish, request)

    def testFormFloatTypes(self):
        extra = {'QUERY_STRING':'a:float=5&b:float=-5.01&c:float=0'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"): 5.0, _u("b"): -5.01, _u("c"): 0.0})

        extra = {'QUERY_STRING':'a:float='}
        request = self._createRequest(extra)
        self.assertRaises(ValueError, publish, request)

        extra = {'QUERY_STRING':'a:float=abc'}
        request = self._createRequest(extra)
        self.assertRaises(ValueError, publish, request)

    def testFormLongTypes(self):
        extra = {'QUERY_STRING':'a:long=99999999999999&b:long=0L'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"): 99999999999999, _u("b"): 0})

        extra = {'QUERY_STRING':'a:long='}
        request = self._createRequest(extra)
        self.assertRaises(ValueError, publish, request)

        extra = {'QUERY_STRING':'a:long=abc'}
        request = self._createRequest(extra)
        self.assertRaises(ValueError, publish, request)

    def testFormTokensTypes(self):
        extra = {'QUERY_STRING':'a:tokens=a%20b%20c%20d&b:tokens='}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"): [_u("a"), _u("b"), _u("c"), _u("d")],
                         _u("b"): []})

    def testFormStringTypes(self):
        extra = {'QUERY_STRING':'a:string=test&b:string='}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"): _u("test"), _u("b"): _u("")})

    def testFormLinesTypes(self):
        extra = {'QUERY_STRING':'a:lines=a%0ab%0ac%0ad&b:lines='}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"): [_u("a"), _u("b"), _u("c"), _u("d")],
                         _u("b"): []})

    def testFormTextTypes(self):
        extra = {'QUERY_STRING':'a:text=a%0a%0db%0d%0ac%0dd%0ae&b:text='}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"): _u("a\nb\nc\nd\ne"), _u("b"): _u("")})

    def testFormRequiredTypes(self):
        extra = {'QUERY_STRING':'a:required=%20'}
        request = self._createRequest(extra)
        self.assertRaises(ValueError, publish, request)

    def testFormBooleanTypes(self):
        extra = {'QUERY_STRING':'a:boolean=&b:boolean=1&c:boolean=%20'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"): False, _u("b"): True, _u("c"): True})

    def testFormDefaults(self):
        extra = {'QUERY_STRING':'a:default=10&a=6&b=1'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"):_u("6"), _u("b"):_u("1")})

    def testFormDefaults2(self):
        extra = {'QUERY_STRING':'a:default=10&b=1'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"):_u("10"), _u("b"):_u("1")})

    def testFormFieldName(self):
        extra = {'QUERY_STRING':'c+%2B%2F%3D%26c%3Aint=6',
                 'PATH_INFO': '/folder/item3/'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("c +/=&c"): 6})

    def testFormFieldValue(self):
        extra = {'QUERY_STRING':'a=b+%2B%2F%3D%26b%3Aint',
                 'PATH_INFO': '/folder/item3/'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.form, {_u("a"):_u("b +/=&b:int")})

    def testInterface(self):
        request = self._createRequest()
        verifyObject(IBrowserRequest, request)
        verifyObject(IBrowserApplicationRequest, request)
        verifyObject(ISkinnable, request)

    def testIssue394(self):
        extra = {'PATH_INFO': '/folder/item3/'}
        request = self._createRequest(extra)
        del request._environ["QUERY_STRING"]
        argv = sys.argv
        sys.argv = [argv[0], "test"]
        try:
            publish(request)
            self.assertEqual(request.form, {})
        finally:
            sys.argv = argv

    def testIssue559(self):
        extra = {'QUERY_STRING': 'HTTP_REFERER=peter',
                 'HTTP_REFERER':'http://localhost/',
                 'PATH_INFO': '/folder/item3/'}
        request = self._createRequest(extra)
        publish(request)
        self.assertEqual(request.headers.get('HTTP_REFERER'), 'http://localhost/')
        self.assertEqual(request.form, {_u("HTTP_REFERER"): _u("peter")})


    def test_post_body_not_consumed_unnecessarily(self):
        request = self._createRequest(
            dict(REQUEST_METHOD='POST',
                 CONTENT_TYPE='application/x-foo',
                 ),
            b'test body')
        request.processInputs()
        self.assertEqual(request.bodyStream.read(), b'test body')

    def test_post_body_not_necessarily(self):
        request = self._createRequest(
            dict(REQUEST_METHOD='POST',
                 CONTENT_TYPE='application/x-www-form-urlencoded',
                 QUERY_STRING='',
                 ),
            b'x=1&y=2')
        request.processInputs()
        self.assertEqual(request.bodyStream.read(), b'')
        self.assertEqual(dict(request.form), dict(x='1', y='2'))

        request = self._createRequest(
            dict(REQUEST_METHOD='POST',
                 CONTENT_TYPE=('application/x-www-form-urlencoded'
                               '; charset=UTF-8'),
                 QUERY_STRING='',
                 ),
            b'x=1&y=2')
        request.processInputs()
        self.assertEqual(request.bodyStream.read(), b'')
        self.assertEqual(dict(request.form), dict(x='1', y='2'))

@implementer(IBrowserPublication)
class TestBrowserPublication(TestPublication):

    def getDefaultTraversal(self, request, ob):
        return ob, ()

class APITests(BaseTestIPublicationRequest,
               BaseTestIApplicationRequest,
               BaseTestIPublisherRequest,
               unittest.TestCase):

    def _Test__new(self, environ=None, **kw):
        if environ is None:
            environ = kw
        return BrowserRequest(BytesIO(b''), environ)

    def test_IApplicationRequest_bodyStream(self):
        request = BrowserRequest(BytesIO(b'spam'), {})
        self.assertEqual(request.bodyStream.read(), b'spam')

    # Needed by BaseTestIEnumerableMapping tests:
    def _IEnumerableMapping__stateDict(self):
        return {'id': 'ZopeOrg', 'title': 'Zope Community Web Site',
                'greet': 'Welcome to the Zope Community Web site'}

    def _IEnumerableMapping__sample(self):
        return self._Test__new(**(self._IEnumerableMapping__stateDict()))

    def _IEnumerableMapping__absentKeys(self):
        return 'foo', 'bar'

    def test_IPublicationRequest_getPositionalArguments(self):
        self.assertEqual(self._Test__new().getPositionalArguments(), ())

    def test_IPublisherRequest_retry(self):
        self.assertEqual(self._Test__new().supportsRetry(), True)

    def test_IPublisherRequest_processInputs(self):
        self._Test__new().processInputs()

    def test_IPublisherRequest_traverse(self):
        request = self._Test__new()
        request.setPublication(TestBrowserPublication())
        app = request.publication.getApplication(request)

        request.setTraversalStack([])
        self.assertEqual(request.traverse(app).name, '')
        self.assertEqual(request._last_obj_traversed, app)
        request.setTraversalStack(['ZopeCorp'])
        self.assertEqual(request.traverse(app).name, 'ZopeCorp')
        self.assertEqual(request._last_obj_traversed, app.ZopeCorp)
        request.setTraversalStack(['Engineering', 'ZopeCorp'])
        self.assertEqual(request.traverse(app).name, 'Engineering')
        self.assertEqual(request._last_obj_traversed, app.ZopeCorp.Engineering)

    def test_IBrowserRequest(self):
        verifyObject(IBrowserRequest, self._Test__new())

    def test_ISkinnable(self):
        self.assertEqual(ISkinnable.providedBy(self._Test__new()), True)

    def testVerifyISkinnable(self):
        verifyObject(ISkinnable, self._Test__new())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BrowserTests))
    suite.addTest(unittest.makeSuite(APITests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
