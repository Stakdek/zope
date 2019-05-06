import unittest


class TestHTTPException(unittest.TestCase):

    def _getTargetClass(self):
        from zExceptions import HTTPException
        return HTTPException

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_body(self):
        exc = self._makeOne()
        self.assertEqual(exc.body, None)
        exc.setBody('Foo')
        self.assertEqual(exc.body, 'Foo')

    def test_headers(self):
        url = 'http://localhost/foo'
        exc = self._makeOne(url)
        self.assertTrue(getattr(exc, 'headers', None) is None)

        exc.setHeader('Location', url)
        self.assertEqual(exc.headers, {'Location': url})

    def test_status(self):
        exc = self._makeOne()
        self.assertEqual(exc.getStatus(), 500)
        self.assertEqual(exc.errmsg, 'Internal Server Error')
        exc.setStatus(503)
        self.assertEqual(exc.getStatus(), 503)
        self.assertEqual(exc.errmsg, 'Service Unavailable')

    def test_call(self):
        exc = self._makeOne('Foo Error')
        called = []

        def start_response(status, headers):
            called.append((status, headers))

        response = exc({'Foo': 1}, start_response)
        self.assertEqual(called, [(
            '500 Internal Server Error',
            [('content-type', 'text/html;charset=utf-8')]
        )])
        response = b''.join(response)
        self.assertTrue(response.startswith(b'<!DOCTYPE html>'))
        self.assertTrue(b'Sorry, a site error occurred.' in response)
        self.assertTrue(b'Foo Error' in response)

    def test_call_custom(self):
        exc = self._makeOne('Foo Error')
        exc.setBody('<html>Foo</html>')
        exc.setStatus(503)

        called = []

        def start_response(status, headers):
            called.append((status, headers))

        response = exc({'Foo': 1}, start_response)
        self.assertEqual(called, [(
            '503 Service Unavailable',
            [('content-type', 'text/html;charset=utf-8')]
        )])
        self.assertEqual(response, [b'<html>Foo</html>'])

    def test_call_detail(self):
        exc = self._makeOne('Foo Error')
        exc.title = 'Foo'
        exc.detail = '<p>Some foo is going on.</p>'
        exc.setStatus(503)

        called = []

        def start_response(status, headers):
            called.append((status, headers))

        response = exc({'Foo': 1}, start_response)
        self.assertEqual(called, [(
            '503 Service Unavailable',
            [('content-type', 'text/html;charset=utf-8')]
        )])
        response = b''.join(response)
        self.assertTrue(response.startswith(b'<!DOCTYPE html>'))
        self.assertTrue(b'<p><strong>Foo</strong></p>' in response)
        self.assertTrue(b'<p>Some foo is going on.</p>' in response)

    def test_call_empty_body(self):
        exc = self._makeOne()
        exc.empty_body = True
        exc.setBody('Foo')
        exc.setStatus(204)

        called = []

        def start_response(status, headers):
            called.append((status, headers))

        response = exc({'Foo': 1}, start_response)
        self.assertEqual(called, [(
            '204 No Content', []
        )])
        self.assertEqual(response, [])

    def test_call_extra_headers(self):
        url = 'http://localhost/foo'
        exc = self._makeOne(url)
        exc.setStatus(302)
        exc.setHeader('Location', url)

        called = []

        def start_response(status, headers):
            called.append((status, headers))

        response = exc({'Foo': 1}, start_response)
        self.assertEqual(called, [(
            '302 Found',
            [('Location', url),
             ('content-type', 'text/html;charset=utf-8')]
        )])
        response = b''.join(response)
        self.assertTrue(response.startswith(b'<!DOCTYPE html>'))


class TestRedirect(unittest.TestCase):

    def test_location_header_302(self):
        from zExceptions import HTTPFound
        exc = HTTPFound('/redirect_to')
        self.assertEqual(exc.headers, {'Location': '/redirect_to'})

    def test_location_header_304(self):
        from zExceptions import HTTPNotModified
        exc = HTTPNotModified('/not_modified')
        self.assertFalse(getattr(exc, 'headers', None))


class TestUnauthorized(unittest.TestCase):

    def _getTargetClass(self):
        from zExceptions import Unauthorized
        return Unauthorized

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_realm(self):
        exc = self._makeOne('message', realm='special')
        self.assertEqual(exc.headers,
                         {'WWW-Authenticate': 'basic realm="special"'})

    def test_location_header_304(self):
        from zExceptions import HTTPNotModified
        exc = HTTPNotModified('/not_modified')
        self.assertFalse(getattr(exc, 'headers', None))


class TestConvertExceptionType(unittest.TestCase):

    def _callFUT(self, name):
        from zExceptions import convertExceptionType
        return convertExceptionType(name)

    def test_name_in___builtins__(self):
        self.assertTrue(self._callFUT('SyntaxError') is SyntaxError)

    def test_name_in___builtins___not_an_exception_returns_None(self):
        self.assertTrue(self._callFUT('unichr') is None)

    def test_name_in_zExceptions(self):
        from zExceptions import Redirect
        self.assertTrue(self._callFUT('Redirect') is Redirect)

    def test_name_in_zExceptions_not_an_exception_returns_None(self):
        self.assertTrue(self._callFUT('convertExceptionType') is None)


class TestUpgradeException(unittest.TestCase):

    def _callFUT(self, t, v):
        from zExceptions import upgradeException
        return upgradeException(t, v)

    def test_non_string(self):
        t, v = self._callFUT(SyntaxError, 'TEST')
        self.assertEqual(t, SyntaxError)
        self.assertEqual(v, 'TEST')

    def test_non_string_match_by_name(self):
        class NotFound(Exception):
            pass

        t, v = self._callFUT(NotFound, 'TEST')
        from zExceptions import NotFound as zExceptions_NotFound
        self.assertIs(t, zExceptions_NotFound)
        self.assertEqual(v, 'TEST')
