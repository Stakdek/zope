# -*- coding: latin-1 -*-
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
"""HTTP Publisher Tests
"""
import sys
import tempfile
import unittest
from io import BytesIO
from doctest import DocFileSuite

import zope.event
from zope.component import provideAdapter
from zope.i18n.interfaces.locales import ILocale
from zope.interface.verify import verifyObject
from zope.security.checker import ProxyFactory
from zope.security.proxy import removeSecurityProxy

from zope.interface import implementer
from zope.publisher.interfaces.logginginfo import ILoggingInfo
from zope.publisher.http import HTTPRequest, HTTPResponse
from zope.publisher.http import HTTPInputStream, DirectResult, HTTPCharsets
from zope.publisher.publish import publish
from zope.publisher.base import DefaultPublication
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.http import IHTTPRequest, IHTTPResponse
from zope.publisher.interfaces.http import IHTTPApplicationResponse
from zope.publisher.interfaces import IResponse
from zope.publisher.tests.publication import TestPublication
from .._compat import _u

from zope.publisher.tests.basetestipublicationrequest \
     import BaseTestIPublicationRequest
from zope.publisher.tests.basetestipublisherrequest \
     import BaseTestIPublisherRequest
from zope.publisher.tests.basetestiapplicationrequest \
     import BaseTestIApplicationRequest
from zope.publisher.testing import output_checker

if sys.version_info[0] > 2:
    from http.cookies import CookieError
else:
    from Cookie import CookieError


@implementer(ILoggingInfo)
class UserStub(object):

    def __init__(self, id):
        self._id = id

    def getId(self):
        return self._id

    def getLogMessage(self):
        return self._id


data = b'''\
line 1
line 2
line 3'''

# tempfiles have different types on different platforms, therefore use
# this "canonical" way of finding out the type.
with tempfile.TemporaryFile() as t:
    TempFileType = t.__class__

class HTTPInputStreamTests(unittest.TestCase):

    def getCacheStreamValue(self, stream):
        stream.cacheStream.seek(0)
        result = stream.cacheStream.read()
        # We just did a read on a file opened for update.  If the next
        # operation on that file is a write, behavior is 100% undefined,
        # and it in fact frequently (but not always) blows up on Windows.
        # Behavior is 100% defined instead if we explictly seek.  Since
        # we expect to be at EOF now, explicitly seek to the end.
        stream.cacheStream.seek(0, 2)
        return result

    def testRead(self):
        stream = HTTPInputStream(BytesIO(data), {})
        output = b''
        self.assertEqual(output, self.getCacheStreamValue(stream))
        output += stream.read(5)
        self.assertEqual(output, self.getCacheStreamValue(stream))
        output += stream.read()
        self.assertEqual(output, self.getCacheStreamValue(stream))
        self.assertEqual(data, self.getCacheStreamValue(stream))

    def testReadLine(self):
        stream = HTTPInputStream(BytesIO(data), {})
        output = stream.readline()
        self.assertEqual(output, self.getCacheStreamValue(stream))
        output += stream.readline()
        self.assertEqual(output, self.getCacheStreamValue(stream))
        output += stream.readline()
        self.assertEqual(output, self.getCacheStreamValue(stream))
        output += stream.readline()
        self.assertEqual(output, self.getCacheStreamValue(stream))
        self.assertEqual(data, self.getCacheStreamValue(stream))

    def testReadLines(self):
        stream = HTTPInputStream(BytesIO(data), {})
        output = b''.join(stream.readlines(4))
        self.assertEqual(output, self.getCacheStreamValue(stream))
        output += b''.join(stream.readlines())
        self.assertEqual(output, self.getCacheStreamValue(stream))
        self.assertEqual(data, self.getCacheStreamValue(stream))

    def testGetCacheStream(self):
        stream = HTTPInputStream(BytesIO(data), {})
        stream.read(5)
        self.assertEqual(data, stream.getCacheStream().read())

    def testCachingWithContentLength(self):
        # The HTTPInputStream implementation will cache the input
        # stream in a temporary file (instead of in memory) when the
        # reported content length is over a certain number (100000 is
        # definitely over that).

        # HTTPInputStream understands both CONTENT_LENGTH...
        stream1 = HTTPInputStream(BytesIO(data), {'CONTENT_LENGTH': '100000'})
        try:
            self.assertTrue(isinstance(stream1.getCacheStream(), TempFileType))
        finally:
            stream1.cacheStream.close()

        # ... and HTTP_CONTENT_LENGTH.
        stream2 = HTTPInputStream(BytesIO(data), {'HTTP_CONTENT_LENGTH':
                                                  '100000'})
        try:
            self.assertTrue(isinstance(stream2.getCacheStream(), TempFileType))
        finally:
            stream2.cacheStream.close()

        # If CONTENT_LENGTH is absent or empty, it takes the value
        # given in HTTP_CONTENT_LENGTH:
        stream3 = HTTPInputStream(BytesIO(data),
                                 {'CONTENT_LENGTH': '',
                                  'HTTP_CONTENT_LENGTH': '100000'})
        try:
            self.assertTrue(isinstance(stream3.getCacheStream(), TempFileType))
        finally:
            stream3.cacheStream.close()

        # In fact, HTTPInputStream can be instantiated with both an
        # empty CONTENT_LENGTH and an empty HTTP_CONTENT_LENGTH:
        stream4 = HTTPInputStream(BytesIO(data),
                                 {'CONTENT_LENGTH': '',
                                  'HTTP_CONTENT_LENGTH': ''})

    def testWorkingWithNonClosingStreams(self):
        # It turns out that some Web servers (Paste for example) do not send
        # the EOF signal after the data has been transmitted and the read()
        # simply hangs if no expected content length has been specified.
        #
        # In this test we simulate the hanging of the server by throwing an
        # exception.
        class ServerHung(Exception):
            pass

        class NonClosingStream(object):
            def read(self, size=-1):
                if size == -1:
                    raise ServerHung
                return b'a'*size

        stream = HTTPInputStream(NonClosingStream(), {'CONTENT_LENGTH': '10'})
        self.assertEqual(stream.getCacheStream().read(), b'aaaaaaaaaa')
        stream = HTTPInputStream(NonClosingStream(), {})
        self.assertRaises(ServerHung, stream.getCacheStream)

class HTTPTests(unittest.TestCase):

    _testEnv =  {
        'PATH_INFO':          '/folder/item',
        'a':                  '5',
        'b':                  6,
        'SERVER_URL':         'http://foobar.com',
        'HTTP_HOST':          'foobar.com',
        'CONTENT_LENGTH':     '0',
        'HTTP_AUTHORIZATION': 'Should be in accessible',
        'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
        'HTTP_OFF_THE_WALL':  "Spam 'n eggs",
        'HTTP_ACCEPT_CHARSET': 'ISO-8859-1, UTF-8;q=0.66, UTF-16;q=0.33',
    }

    def setUp(self):
        class AppRoot(object):
            """Required docstring for the publisher."""

        class Folder(object):
            """Required docstring for the publisher."""

        class Item(object):
            """Required docstring for the publisher."""
            def __call__(self, a, b):
                return ("%s, %s" % (repr(a), repr(b))).encode('latin1')

        self.app = AppRoot()
        self.app.folder = Folder()
        self.app.folder.item = Item()
        self.app.xxx = Item()

    def tearDown(self):
        # unregister adapters registered in tests
        from zope.component.testing import tearDown
        tearDown()

    def _createRequest(self, extra_env={}, body=b""):
        env = self._testEnv.copy()
        env.update(extra_env)
        if len(body):
            env['CONTENT_LENGTH'] = str(len(body))

        publication = DefaultPublication(self.app)
        instream = BytesIO(body)
        request = HTTPRequest(instream, env)
        request.setPublication(publication)
        return request

    def _publisherResults(self, extra_env={}, body=b""):
        request = self._createRequest(extra_env, body)
        response = request.response
        publish(request, handle_errors=False)
        headers = response.getHeaders()
        return (
            "Status: %s\r\n" % response.getStatusString()
            +
            "\r\n".join([("%s: %s" % h) for h in headers]) + "\r\n\r\n"
            +
            response.consumeBody().decode('utf8')
            )

    def test_double_dots(self):
        # the code that parses PATH_INFO once tried to raise NotFound if the
        # path it was given started with double-dots; unfortunately it didn't
        # do it correctly, so it instead generated this error when trying to
        # raise NotFound:
        #     TypeError: __init__() takes at least 3 arguments (2 given)

        # It really shouldn't generate NotFound because it doesn't have enough
        # context to do so, and the publisher will raise it anyway given
        # improper input.  It was fixed and this test added.

        request = self._createRequest(extra_env={'PATH_INFO': '..'})
        self.assertRaises(NotFound, publish, request, handle_errors=0)

        request = self._createRequest(extra_env={'PATH_INFO': '../folder'})
        self.assertRaises(NotFound, publish, request, handle_errors=0)

    def test_repr(self):
        request = self._createRequest()
        expect = '<%s.%s instance URL=http://foobar.com>' % (
            request.__class__.__module__, request.__class__.__name__)
        self.assertEqual(repr(request), expect)

    def testTraversalToItem(self):
        res = self._publisherResults()
        self.assertEqual(
            res,
            "Status: 200 Ok\r\n"
            "X-Powered-By: Zope (www.zope.org), Python (www.python.org)\r\n"
            "Content-Length: 6\r\n"
            "\r\n"
            "'5', 6")

    def testRedirect(self):
        # test HTTP/1.0
        env = {'SERVER_PROTOCOL':'HTTP/1.0'}

        request = self._createRequest(env, b'')
        location = request.response.redirect('http://foobar.com/redirected')
        self.assertEqual(location, 'http://foobar.com/redirected')
        self.assertEqual(request.response.getStatus(), 302)
        self.assertEqual(request.response.getHeader('location'), location)

        # test HTTP/1.1
        env = {'SERVER_PROTOCOL':'HTTP/1.1'}

        request = self._createRequest(env, b'')
        location = request.response.redirect('http://foobar.com/redirected')
        self.assertEqual(request.response.getStatus(), 303)

        # test explicit status
        request = self._createRequest(env, b'')
        request.response.redirect('http://foobar.com/explicit', 304)
        self.assertEqual(request.response.getStatus(), 304)

        # test non-string location, like URLGetter
        request = self._createRequest(env, b'')
        request.response.redirect(request.URL)
        self.assertEqual(request.response.getStatus(), 303)
        self.assertEqual(request.response.getHeader('location'),
                          str(request.URL))

    def testUntrustedRedirect(self):
        # Redirects are by default only allowed to target the same host as the
        # request was directed to. This is to counter fishing.
        request = self._createRequest({}, b'')
        self.assertRaises(
            ValueError,
            request.response.redirect, 'http://phishing-inc.com')

        # Redirects with relative URLs are treated as redirects to the current
        # host. They aren't really allowed per RFC but the response object
        # supports them and people are probably using them.
        location = request.response.redirect('/foo', trusted=False)
        self.assertEqual('/foo', location)

        # If we pass `trusted` for the redirect, we can redirect the browser
        # anywhere we want, though.
        location = request.response.redirect(
            'http://my-friends.com', trusted=True)
        self.assertEqual('http://my-friends.com', location)

        # We can redirect to our own full server URL, with or without a port
        # being specified. Let's explicitly set a host name to test this is
        # this is how virtual hosting works:
        request.setApplicationServer('example.com')
        location = request.response.redirect('http://example.com')
        self.assertEqual('http://example.com', location)

        request.setApplicationServer('example.com', port=8080)
        location = request.response.redirect('http://example.com:8080')
        self.assertEqual('http://example.com:8080', location)

        # The default port for HTTP and HTTPS may be omitted:
        request.setApplicationServer('example.com')
        location = request.response.redirect('http://example.com:80')
        self.assertEqual('http://example.com:80', location)

        request.setApplicationServer('example.com', port=80)
        location = request.response.redirect('http://example.com')
        self.assertEqual('http://example.com', location)

        request.setApplicationServer('example.com', 'https')
        location = request.response.redirect('https://example.com:443')
        self.assertEqual('https://example.com:443', location)

        request.setApplicationServer('example.com', 'https', 443)
        location = request.response.redirect('https://example.com')
        self.assertEqual('https://example.com', location)

    def testUnregisteredStatus(self):
        # verify we can set the status to an unregistered int value
        request = self._createRequest({}, b'')
        request.response.setStatus(289)
        self.assertEqual(request.response.getStatus(), 289)

    def testRequestEnvironment(self):
        req = self._createRequest()
        publish(req, handle_errors=0) # Force expansion of URL variables

        self.assertEqual(str(req.URL), 'http://foobar.com/folder/item')
        self.assertEqual(req.URL['-1'], 'http://foobar.com/folder')
        self.assertEqual(req.URL['-2'], 'http://foobar.com')
        self.assertRaises(KeyError, req.URL.__getitem__, '-3')

        self.assertEqual(req.URL['0'], 'http://foobar.com')
        self.assertEqual(req.URL['1'], 'http://foobar.com/folder')
        self.assertEqual(req.URL['2'], 'http://foobar.com/folder/item')
        self.assertRaises(KeyError, req.URL.__getitem__, '3')

        self.assertEqual(req.URL.get('0'), 'http://foobar.com')
        self.assertEqual(req.URL.get('1'), 'http://foobar.com/folder')
        self.assertEqual(req.URL.get('2'), 'http://foobar.com/folder/item')
        self.assertEqual(req.URL.get('3', 'none'), 'none')

        self.assertEqual(req['SERVER_URL'], 'http://foobar.com')
        self.assertEqual(req['HTTP_HOST'], 'foobar.com')
        self.assertEqual(req['PATH_INFO'], '/folder/item')
        self.assertEqual(req['CONTENT_LENGTH'], '0')
        self.assertRaises(KeyError, req.__getitem__, 'HTTP_AUTHORIZATION')
        self.assertEqual(req['GATEWAY_INTERFACE'], 'TestFooInterface/1.0')
        self.assertEqual(req['HTTP_OFF_THE_WALL'], "Spam 'n eggs")

        self.assertRaises(KeyError, req.__getitem__,
                          'HTTP_WE_DID_NOT_PROVIDE_THIS')

    def testRequestLocale(self):
        eq = self.assertEqual
        unless = self.assertTrue

        from zope.publisher.browser import BrowserLanguages
        from zope.publisher.interfaces.http import IHTTPRequest
        from zope.i18n.interfaces import IUserPreferredLanguages
        provideAdapter(BrowserLanguages, [IHTTPRequest],
                       IUserPreferredLanguages)

        for httplang in ('it', 'it-ch', 'it-CH', 'IT', 'IT-CH', 'IT-ch'):
            req = self._createRequest({'HTTP_ACCEPT_LANGUAGE': httplang})
            locale = req.locale
            unless(ILocale.providedBy(locale))
            parts = httplang.split('-')
            lang = parts.pop(0).lower()
            territory = variant = None
            if parts:
                territory = parts.pop(0).upper()
            if parts:
                variant = parts.pop(0).upper()
            eq(locale.id.language, lang)
            eq(locale.id.territory, territory)
            eq(locale.id.variant, variant)
        # Now test for non-existant locale fallback
        req = self._createRequest({'HTTP_ACCEPT_LANGUAGE': 'xx'})
        locale = req.locale
        unless(ILocale.providedBy(locale))
        eq(locale.id.language, None)
        eq(locale.id.territory, None)
        eq(locale.id.variant, None)

        # If the first language is not available we should try others
        req = self._createRequest({'HTTP_ACCEPT_LANGUAGE': 'xx,en;q=0.5'})
        locale = req.locale
        unless(ILocale.providedBy(locale))
        eq(locale.id.language, 'en')
        eq(locale.id.territory, None)
        eq(locale.id.variant, None)

        # Regression test: there was a bug where territory and variant were
        # not reset
        req = self._createRequest({'HTTP_ACCEPT_LANGUAGE': 'xx-YY,en;q=0.5'})
        locale = req.locale
        unless(ILocale.providedBy(locale))
        eq(locale.id.language, 'en')
        eq(locale.id.territory, None)
        eq(locale.id.variant, None)

        # Now test for improper quality value, should ignore the header
        req = self._createRequest({'HTTP_ACCEPT_LANGUAGE': 'en;q=xx'})
        locale = req.locale
        unless(ILocale.providedBy(locale))
        eq(locale.id.language, None)
        eq(locale.id.territory, None)
        eq(locale.id.variant, None)

        # Now test for very improper quality value, should ignore the header
        req = self._createRequest({'HTTP_ACCEPT_LANGUAGE': 'asdf;qwer'})
        locale = req.locale
        unless(ILocale.providedBy(locale))
        eq(locale.id.language, None)
        eq(locale.id.territory, None)
        eq(locale.id.variant, None)

    def testCookies(self):
        cookies = {
            'HTTP_COOKIE':
                'foo=bar; path=/; spam="eggs"; this="Should be accepted"'
        }
        req = self._createRequest(extra_env=cookies)

        self.assertEqual(req.cookies[_u('foo')], _u('bar'))
        self.assertEqual(req[_u('foo')], _u('bar'))

        self.assertEqual(req.cookies[_u('spam')], _u('eggs'))
        self.assertEqual(req[_u('spam')], _u('eggs'))

        self.assertEqual(req.cookies[_u('this')], _u('Should be accepted'))
        self.assertEqual(req[_u('this')], _u('Should be accepted'))

        # Reserved key
        self.assertFalse(req.cookies.has_key('path'))

    def testCookieErrorToLog(self):
        from zope.testing.loggingsupport import InstalledHandler
        cookies = {
            'HTTP_COOKIE':
                'foo=bar; path=/; spam="eggs"; ldap/OU="Williams"'
        }
        handler = InstalledHandler('eventlog')
        try:
            req = self._createRequest(extra_env=cookies)
        finally:
            handler.uninstall()

        self.assertEqual(len(handler.records), 1)

        message = handler.records[0].getMessage()
        self.assertTrue(message.startswith('Illegal key'))
        self.assertTrue('ldap/OU' in message)

        self.assertFalse(req.cookies.has_key('foo'))
        self.assertFalse(req.has_key('foo'))

        self.assertFalse(req.cookies.has_key('spam'))
        self.assertFalse(req.has_key('spam'))

        self.assertFalse(req.cookies.has_key('ldap/OU'))
        self.assertFalse(req.has_key('ldap/OU'))

        # Reserved key
        self.assertFalse(req.cookies.has_key('path'))

    def testCookiesUnicode(self):
        # Cookie values are assumed to be UTF-8 encoded
        cookies = {'HTTP_COOKIE': r'key="\342\230\243";'}
        req = self._createRequest(extra_env=cookies)
        self.assertEqual(req.cookies[_u('key')], _u('\N{BIOHAZARD SIGN}'))

    def testHeaders(self):
        headers = {
            'TEST_HEADER': 'test',
            'Another-Test': 'another',
        }
        req = self._createRequest(extra_env=headers)
        self.assertEqual(req.headers[_u('TEST_HEADER')], _u('test'))
        self.assertEqual(req.headers[_u('TEST-HEADER')], _u('test'))
        self.assertEqual(req.headers[_u('test_header')], _u('test'))
        self.assertEqual(req.getHeader('TEST_HEADER', literal=True), _u('test'))
        self.assertEqual(req.getHeader('TEST-HEADER', literal=True), None)
        self.assertEqual(req.getHeader('test_header', literal=True), None)
        self.assertEqual(req.getHeader('Another-Test', literal=True),
                          'another')

    def testBasicAuth(self):
        from zope.publisher.interfaces.http import IHTTPCredentials
        import base64
        req = self._createRequest()
        verifyObject(IHTTPCredentials, req)
        lpq = req._authUserPW()
        self.assertEqual(lpq, None)
        env = {}
        login, password = (b"tim", b"123:456")
        s = base64.b64encode(b':'.join((login, password)))
        env['HTTP_AUTHORIZATION'] = "Basic %s" % s.decode('ascii')
        req = self._createRequest(env)
        lpw = req._authUserPW()
        self.assertEqual(lpw, (login, password))

    def testSetPrincipal(self):
        req = self._createRequest()
        req.setPrincipal(UserStub("jim"))
        self.assertEqual(req.response.authUser, 'jim')

    def test_method(self):
        r = self._createRequest(extra_env={'REQUEST_METHOD':'SPAM'})
        self.assertEqual(r.method, 'SPAM')
        r = self._createRequest(extra_env={'REQUEST_METHOD':'eggs'})
        self.assertEqual(r.method, 'EGGS')

    def test_setApplicationServer(self):
        events = []
        zope.event.subscribers.append(events.append)
        req = self._createRequest()
        req.setApplicationServer('foo')
        self.assertEqual(req._app_server, 'http://foo')
        req.setApplicationServer('foo', proto='https')
        self.assertEqual(req._app_server, 'https://foo')
        req.setApplicationServer('foo', proto='https', port=8080)
        self.assertEqual(req._app_server, 'https://foo:8080')
        req.setApplicationServer('foo', proto='http', port='9673')
        self.assertEqual(req._app_server, 'http://foo:9673')
        req.setApplicationServer('foo', proto='https', port=443)
        self.assertEqual(req._app_server, 'https://foo')
        req.setApplicationServer('foo', proto='https', port='443')
        self.assertEqual(req._app_server, 'https://foo')
        req.setApplicationServer('foo', port=80)
        self.assertEqual(req._app_server, 'http://foo')
        req.setApplicationServer('foo', proto='telnet', port=80)
        self.assertEqual(req._app_server, 'telnet://foo:80')
        zope.event.subscribers.pop()
        self.assertEqual(len(events), 8)
        for event in events:
            self.assertEqual(event.request, req)

    def test_setApplicationNames(self):
        events = []
        zope.event.subscribers.append(events.append)
        req = self._createRequest()
        names = ['x', 'y', 'z']
        req.setVirtualHostRoot(names)
        self.assertEqual(req._app_names, ['x', 'y', 'z'])
        names[0] = 'muahahahaha'
        self.assertEqual(req._app_names, ['x', 'y', 'z'])
        zope.event.subscribers.pop()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].request, req)

    def test_setVirtualHostRoot(self):
        events = []
        zope.event.subscribers.append(events.append)
        req = self._createRequest()
        req._traversed_names = ['x', 'y']
        req._last_obj_traversed = object()
        req.setVirtualHostRoot()
        self.assertFalse(req._traversed_names)
        self.assertEqual(req._vh_root, req._last_obj_traversed)
        zope.event.subscribers.pop()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].request, req)

    def test_getVirtualHostRoot(self):
        req = self._createRequest()
        self.assertEqual(req.getVirtualHostRoot(), None)
        req._vh_root = object()
        self.assertEqual(req.getVirtualHostRoot(), req._vh_root)

    def test_traverse(self):
        req = self._createRequest()
        req.traverse(self.app)
        self.assertEqual(req._traversed_names, ['folder', 'item'])

        # setting it during traversal matters
        req = self._createRequest()
        def hook(self, object, req=req, app=self.app):
            if object is app.folder:
                req.setVirtualHostRoot()
        req.publication.callTraversalHooks = hook
        req.traverse(self.app)
        self.assertEqual(req._traversed_names, ['item'])
        self.assertEqual(req._vh_root, self.app.folder)

    def test_traverseDuplicateHooks(self):
        """
        BaseRequest.traverse should not call traversal hooks on elements
        previously traversed but wrapped in a security Proxy.
        """
        hooks = []
        class HookPublication(DefaultPublication):

            def callTraversalHooks(self, request, object):
                hooks.append(object)

            def traverseName(self, request, ob, name, check_auth=1):
                # Fake the virtual host
                if name == "vh":
                    return ProxyFactory(ob)
                return super(HookPublication, self).traverseName(
                    request, removeSecurityProxy(ob), name, check_auth=1)

        publication = HookPublication(self.app)
        req = self._createRequest()
        req.setPublication(publication)
        req.setTraversalStack(req.getTraversalStack() + ["vh"])
        req.traverse(self.app)
        self.assertEqual(len(hooks), 3)

    def testInterface(self):
        from zope.publisher.interfaces.http import IHTTPCredentials
        from zope.publisher.interfaces.http import IHTTPApplicationRequest
        rq = self._createRequest()
        verifyObject(IHTTPRequest, rq)
        verifyObject(IHTTPCredentials, rq)
        verifyObject(IHTTPApplicationRequest, rq)

    def testDeduceServerURL(self):
        req = self._createRequest()
        deduceServerURL = req._HTTPRequest__deduceServerURL
        req._environ = {'HTTP_HOST': 'example.com:80'}
        self.assertEqual(deduceServerURL(), 'http://example.com')
        req._environ = {'HTTP_HOST': 'example.com:8080'}
        self.assertEqual(deduceServerURL(), 'http://example.com:8080')
        req._environ = {'HTTP_HOST': 'example.com:443', 'HTTPS': 'on'}
        self.assertEqual(deduceServerURL(), 'https://example.com')
        req._environ = {'HTTP_HOST': 'example.com:80', 'HTTPS': 'ON'}
        self.assertEqual(deduceServerURL(), 'https://example.com:80')
        req._environ = {'HTTP_HOST': 'example.com:8080',
                        'SERVER_PORT_SECURE': '1'}
        self.assertEqual(deduceServerURL(), 'https://example.com:8080')
        req._environ = {'SERVER_NAME': 'example.com', 'SERVER_PORT':'8080',
                        'SERVER_PORT_SECURE': '0'}
        self.assertEqual(deduceServerURL(), 'http://example.com:8080')
        req._environ = {'SERVER_NAME': 'example.com'}
        self.assertEqual(deduceServerURL(), 'http://example.com')

    def testUnicodeURLs(self):
        # The request expects PATH_INFO to be utf-8 encoded when it gets it.
        req = self._createRequest(
            {'PATH_INFO': '/\xc3\xa4\xc3\xb6/\xc3\xbc\xc3\x9f/foo/bar.html'})
        self.assertEqual(req._traversal_stack,
            [_u('bar.html'), _u('foo'), _u('\u00fc\u00df'), _u('\u00e4\u00f6')])
        # the request should have converted PATH_INFO to unicode
        self.assertEqual(req['PATH_INFO'],
            _u('/\u00e4\u00f6/\u00fc\u00df/foo/bar.html'))

    def testResponseWriteFaile(self):
        self.assertRaises(TypeError,
                          self._createRequest().response.write,
                          'some output',
                          )

    def test_PathTrailingWhitespace(self):
        request = self._createRequest({'PATH_INFO': '/test '})
        self.assertEqual(['test '], request.getTraversalStack())

    def test_unacceptable_charset(self):
        # Regression test for https://bugs.launchpad.net/zope3/+bug/98337
        request = self._createRequest({'HTTP_ACCEPT_CHARSET': 'ISO-8859-1'})
        result = _u("Latin a with ogonek\u0105 Cyrillic ya \u044f")
        provideAdapter(HTTPCharsets)
        request.response.setHeader('Content-Type', 'text/plain')

        # Instead of failing with HTTP code 406 we ignore the
        # Accept-Charset header and return a response in UTF-8.
        request.response.setResult(result)

        body = request.response.consumeBody()
        self.assertEqual(request.response.getStatus(), 200)
        self.assertEqual(request.response.getHeader('Content-Type'),
                          'text/plain;charset=utf-8')
        self.assertEqual(body,
                          b'Latin a with ogonek\xc4\x85 Cyrillic ya \xd1\x8f')

class ConcreteHTTPTests(HTTPTests):
    """Tests that we don't have to worry about subclasses inheriting and
    breaking.
    """

    def test_shiftNameToApplication(self):
        r = self._createRequest()
        publish(r, handle_errors=0)
        appurl = r.getApplicationURL()

        # Verify that we can shift. It would be a little more realistic
        # if we could test this during traversal, but the api doesn't
        # let us do that.
        r = self._createRequest(extra_env={"PATH_INFO": "/xxx"})
        publish(r, handle_errors=0)
        r.shiftNameToApplication()
        self.assertEqual(r.getApplicationURL(), appurl+"/xxx")

        # Verify that we can only shift if we've traversed only a single name
        r = self._createRequest(extra_env={"PATH_INFO": "/folder/item"})
        publish(r, handle_errors=0)
        self.assertRaises(ValueError, r.shiftNameToApplication)

    def test_non_existing_charset(self):
        # regression test for breakage when getPreferredCharsets returns an
        # unknown charset.  seen in the wild with utf-8q=0 as the charset.

        # Mock charset adapter to inject fake charset
        call_log = []
        class MyCharsets(object):

            def __init__(self, request):
                self.request = request

            def getPreferredCharsets(self):
                call_log.append(None)
                return ['utf-8q=0']

        from zope.publisher.interfaces.http import IHTTPRequest
        from zope.i18n.interfaces import IUserPreferredCharsets
        provideAdapter(MyCharsets, [IHTTPRequest],
                       IUserPreferredCharsets)

        # set the response on a result
        request = self._createRequest()
        request.response.setHeader('Content-Type', 'text/plain')
        result = _u("Latin a with ogonek\u0105 Cyrillic ya \u044f")
        request.response.setResult(result)

        body = request.response.consumeBody()
        self.assertEqual(request.response.getStatus(), 200)
        self.assertEqual(request.response.getHeader('Content-Type'),
                          'text/plain;charset=utf-8')
        self.assertEqual(body,
                          b'Latin a with ogonek\xc4\x85 Cyrillic ya \xd1\x8f')
        # assert that our mock was used
        self.assertEqual(len(call_log), 1)


class TestHTTPResponse(unittest.TestCase):

    def testInterface(self):
        rp = HTTPResponse()
        verifyObject(IHTTPResponse, rp)
        verifyObject(IHTTPApplicationResponse, rp)
        verifyObject(IResponse, rp)

    def _createResponse(self):
        response = HTTPResponse()
        return response

    def _parseResult(self, response):
        return dict(response.getHeaders()), response.consumeBody()

    def _getResultFromResponse(self, body, charset='utf-8', headers=None):
        response = self._createResponse()
        assert(charset == 'utf-8')
        if headers is not None:
            for hdr, val in headers.items():
                response.setHeader(hdr, val)
        response.setResult(body)
        return self._parseResult(response)

    def testWrite_noContentLength(self):
        response = self._createResponse()
        # We have to set all the headers ourself, we choose not to provide a
        # content-length header
        response.setHeader('Content-Type', 'text/plain;charset=us-ascii')

        # Output the data
        data = b'a'*10
        response.setResult(DirectResult(data))

        headers, body = self._parseResult(response)
        # Check that the data have been written, and that the header
        # has been preserved
        self.assertEqual(headers['Content-Type'],
                         'text/plain;charset=us-ascii')
        self.assertEqual(body, data)

        # Make sure that no Content-Length header was added
        self.assertTrue('Content-Length' not in headers)

    def testContentLength(self):
        eq = self.assertEqual

        headers, body = self._getResultFromResponse("test", "utf-8",
            {"content-type": "text/plain"})
        eq("4", headers["Content-Length"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(
            _u('\u0442\u0435\u0441\u0442'), "utf-8",
            {"content-type": "text/plain"})
        eq("8", headers["Content-Length"])
        eq(b'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82', body)

    def testContentType(self):
        eq = self.assertEqual

        headers, body = self._getResultFromResponse(b"test", "utf-8")
        eq("", headers.get("Content-Type", ""))
        eq(b"test", body)

        headers, body = self._getResultFromResponse(_u("test"),
            headers={"content-type": "text/plain"})
        eq("text/plain;charset=utf-8", headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(_u("test"), "utf-8",
            {"content-type": "text/html"})
        eq("text/html;charset=utf-8", headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(_u("test"), "utf-8",
            {"content-type": "text/plain;charset=cp1251"})
        eq("text/plain;charset=cp1251", headers["Content-Type"])
        eq(b"test", body)

        # see https://bugs.launchpad.net/zope.publisher/+bug/98395
        # RFC 3023 types and */*+xml output as unicode

        headers, body = self._getResultFromResponse(_u("test"), "utf-8",
            {"content-type": "text/xml"})
        eq("text/xml;charset=utf-8", headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(_u("test"), "utf-8",
            {"content-type": "application/xml"})
        eq("application/xml;charset=utf-8", headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(_u("test"), "utf-8",
            {"content-type": "text/xml-external-parsed-entity"})
        eq("text/xml-external-parsed-entity;charset=utf-8",
           headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(_u("test"), "utf-8",
            {"content-type": "application/xml-external-parsed-entity"})
        eq("application/xml-external-parsed-entity;charset=utf-8",
           headers["Content-Type"])
        eq(b"test", body)

        # Mozilla XUL
        headers, body = self._getResultFromResponse(_u("test"), "utf-8",
            {"content-type": "application/vnd+xml"})
        eq("application/vnd+xml;charset=utf-8", headers["Content-Type"])
        eq(b"test", body)

        # end RFC 3023 / xml as unicode

        headers, body = self._getResultFromResponse(b"test", "utf-8",
            {"content-type": "image/gif"})
        eq("image/gif", headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(_u("test"), "utf-8",
            {"content-type": "application/json"})
        eq("application/json", headers["Content-Type"])
        eq(b"test", body)

    def _getCookieFromResponse(self, cookies):
        # Shove the cookies through request, parse the Set-Cookie header
        # and spit out a list of headers for examination
        response = self._createResponse()
        for name, value, kw in cookies:
            response.setCookie(name, value, **kw)
        response.setResult(b'test')
        return [header[1]
                for header in response.getHeaders()
                if header[0] == "Set-Cookie"]

    def testSetCookie(self):
        c = self._getCookieFromResponse([
                ('foo', 'bar', {}),
                ])
        self.assertTrue('foo=bar;' in c or 'foo=bar' in c,
                        'foo=bar; not in %r' % c)

        c = self._getCookieFromResponse([
                ('foo', 'bar', {}),
                ('alpha', 'beta', {}),
                ])
        self.assertTrue('foo=bar;' in c or 'foo=bar' in c)
        self.assertTrue('alpha=beta;' in c or 'alpha=beta' in c)

        c = self._getCookieFromResponse([
                ('sign', _u('\N{BIOHAZARD SIGN}'), {}),
                ])
        self.assertTrue((r'sign="\342\230\243";' in c) or
                        (r'sign="\342\230\243"' in c))

        self.assertRaises(
                CookieError,
                self._getCookieFromResponse,
                [('path', 'invalid key', {}),]
                )

        c = self._getCookieFromResponse([
                ('foo', 'bar', {
                    'Expires': 'Sat, 12 Jul 2014 23:26:28 GMT',
                    'domain': 'example.com',
                    'pAth': '/froboz',
                    'max_age': 3600,
                    'comment': _u('blah;\N{BIOHAZARD SIGN}?'),
                    'seCure': True,
                    }),
                ])[0]
        self.assertTrue('foo=bar;' in c or 'foo=bar' in c)
        self.assertTrue('expires=Sat, 12 Jul 2014 23:26:28 GMT;' in c, repr(c))
        self.assertTrue('Domain=example.com;' in c)
        self.assertTrue('Path=/froboz;' in c)
        self.assertTrue('Max-Age=3600;' in c)
        # The first variant is the more modern one,
        # see https://bugs.python.org/issue991266:
        self.assertTrue('Comment="blah%3B%E2%98%A3?";' in c
                        or 'Comment=blah%3B%E2%98%A3?;' in c, repr(c))
        self.assertTrue('secure;' in c or 'secure' in c.lower())

        c = self._getCookieFromResponse([('foo', 'bar', {'secure': False})])[0]
        self.assertTrue('foo=bar;' in c or 'foo=bar' in c)
        self.assertFalse('secure' in c)

    def test_handleException(self):
        response = HTTPResponse()
        try:
            raise ValueError(1)
        except:
            exc_info = sys.exc_info()

        response.handleException(exc_info)
        self.assertEqual(response.getHeader("content-type"),
            "text/html;charset=utf-8")
        self.assertEqual(response.getStatus(), 500)
        self.assertTrue(response.consumeBody() in
             [b"<html><head>"
              b"<title>&lt;type 'exceptions.ValueError'&gt;</title></head>\n"
              b"<body><h2>&lt;type 'exceptions.ValueError'&gt;</h2>\n"
              b"A server error occurred.\n"
              b"</body></html>\n",
              b"<html><head><title>ValueError</title></head>\n"
              b"<body><h2>ValueError</h2>\n"
              b"A server error occurred.\n"
              b"</body></html>\n"]
             )


class APITests(BaseTestIPublicationRequest,
               BaseTestIApplicationRequest,
               BaseTestIPublisherRequest,
               unittest.TestCase):

    def _Test__new(self, environ=None, **kw):
        if environ is None:
            environ = kw
        return HTTPRequest(BytesIO(b''), environ)

    def test_IApplicationRequest_bodyStream(self):
        request = HTTPRequest(BytesIO(b'spam'), {})
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
        request.setPublication(TestPublication())
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

def cleanUp(test):
    from zope.testing import cleanup
    cleanup.cleanUp()


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ConcreteHTTPTests),
        unittest.makeSuite(TestHTTPResponse),
        unittest.makeSuite(HTTPInputStreamTests),
        DocFileSuite('../httpresults.txt',
            setUp=cleanUp,
            tearDown=cleanUp,
            checker=output_checker),
        unittest.makeSuite(APITests),
    ))
