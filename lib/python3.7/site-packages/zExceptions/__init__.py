##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""General exceptions that wish they were standard exceptions

These exceptions are so general purpose that they don't belong in Zope
application-specific packages.
"""
from zope.interface import implementer
from zope.interface.common.interfaces import IException
from zope.publisher.interfaces.http import (
    IHTTPException,
    IMethodNotAllowed,
)
from zope.publisher.interfaces import (
    IBadRequest,
    INotFound,
    IRedirect,
)
from zope.security.interfaces import IForbidden

from ._compat import builtins
from ._compat import class_types


status_reasons = {
    # Informational
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',

    # Successful
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi-Status',
    226: 'IM Used',

    # Redirection
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',

    # Client Error
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    418: "I'm a teapot",
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    426: 'Upgrade Required',
    428: 'Precondition Required',
    429: 'Too Many Requests',
    431: 'Request Header Fields Too Large',
    451: 'Unavailable for Legal Reasons',

    # Server Error
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    507: 'Insufficient Storage',
    510: 'Not Extended',
    511: 'Network Authentication Required',
}


ERROR_HTML = """\
<!DOCTYPE html>
<html>
<head>
<title>Site Error</title>
<meta charset="utf-8" />
</head>
<body bgcolor="#FFFFFF">
<h2>Site Error</h2>
<p>An error was encountered while publishing this resource.
</p>
<p><strong>{title}</strong></p>

{detail}
<hr noshade="noshade"/>

<p>Troubleshooting Suggestions</p>

<ul>
<li>The URL may be incorrect.</li>
<li>The parameters passed to this resource may be incorrect.</li>
<li>A resource that this resource relies on may be
  encountering an error.</li>
</ul>

<p>If the error persists please contact the site maintainer.
Thank you for your patience.
</p>
</body></html>"""


@implementer(IHTTPException)
class HTTPException(Exception):
    body = None
    body_template = ERROR_HTML
    detail = None
    empty_body = False
    errmsg = 'Internal Server Error'
    status = 500
    title = 'Sorry, a site error occurred.'

    def setBody(self, body):
        self.body = body

    def getStatus(self):
        return self.status

    def setStatus(self, status, reason=None):
        self.status = status
        if reason is None:
            reason = status_reasons.get(status, 'Unknown')
        else:
            reason = reason
        self.errmsg = reason

    def setHeader(self, name, value):
        if not hasattr(self, 'headers'):
            self.headers = {}
        self.headers[name] = value

    def __call__(self, environ, start_response):
        headers = list(getattr(self, 'headers', {}).items())
        if not self.empty_body:
            headers.append(('content-type', 'text/html;charset=utf-8'))
        if self.errmsg is not None:
            reason = self.errmsg
        reason = status_reasons[self.getStatus()]
        start_response(
            '%d %s' % (self.getStatus(), reason),
            headers)

        if self.empty_body:
            return []

        body = self.body
        if body is None:
            message = str(self)
            detail = self.detail if self.detail is not None else message
            if self.title and detail:
                body = self.body_template.format(
                    title=self.title, detail=detail)
                body = body
            else:
                body = message
        return [body.encode('utf-8')]


class HTTPOk(HTTPException):
    """Base class for 2xx status codes."""
    errmsg = 'OK'
    status = 200


class HTTPCreated(HTTPOk):
    errmsg = 'Created'
    status = 201


class HTTPAccepted(HTTPOk):
    errmsg = 'Accepted'
    status = 202


class HTTPNonAuthoritativeInformation(HTTPOk):
    errmsg = 'Non-Authoritative Information'
    status = 203


class HTTPNoContent(HTTPOk):
    errmsg = 'No Content'
    status = 204
    empty_body = True


class HTTPResetContent(HTTPOk):
    errmsg = 'Reset Content'
    status = 205
    empty_body = True


class HTTPPartialContent(HTTPOk):
    errmsg = 'Partial Content'
    status = 206


class HTTPMultiStatus(HTTPOk):
    errmsg = 'Multi-Status'
    status = 207


class HTTPIMUsed(HTTPOk):
    errmsg = 'IM Used'
    status = 226


class HTTPRedirection(HTTPException):
    """Base class for 3xx status codes."""


class _HTTPMove(HTTPRedirection):
    """Base class for redirections requiring a location header."""

    def __init__(self, *args):
        super(_HTTPMove, self).__init__(*args)
        self.setHeader('Location', args[0])


class HTTPMultipleChoices(_HTTPMove):
    errmsg = 'Multiple Choices'
    status = 300


class HTTPMovedPermanently(_HTTPMove):
    errmsg = 'Moved Permanently'
    status = 301


@implementer(IRedirect)
class Redirect(_HTTPMove):
    errmsg = 'Found'
    status = 302

HTTPFound = Redirect  # Alias


class HTTPSeeOther(_HTTPMove):
    errmsg = 'See Other'
    status = 303


class HTTPNotModified(HTTPRedirection):
    errmsg = 'Not Modified'
    status = 304
    empty_body = True


class HTTPUseProxy(_HTTPMove):
    errmsg = 'Use Proxy'
    status = 305


class HTTPTemporaryRedirect(_HTTPMove):
    errmsg = 'Temporary Redirect'
    status = 307


class HTTPPermanentRedirect(_HTTPMove):
    errmsg = 'Permanent Redirect'
    status = 308


class HTTPError(HTTPException):
    """Base class for 4xx and 5xx status codes."""


class HTTPClientError(HTTPError):
    """Base class for 4xx status codes."""
    errmsg = 'Bad Request'
    status = 400


@implementer(IBadRequest)
class BadRequest(HTTPClientError):
    pass

HTTPBadRequest = BadRequest  # Alias


# Import cycle.
from .unauthorized import Unauthorized  # NOQA
HTTPUnauthorized = Unauthorized  # Alias


class HTTPPaymentRequired(HTTPClientError):
    errmsg = 'Payment Required'
    status = 402


@implementer(IForbidden)
class Forbidden(HTTPException):
    errmsg = 'Forbidden'
    status = 403

HTTPForbidden = Forbidden  # Alias


@implementer(INotFound)
class NotFound(HTTPException):
    errmsg = 'Not Found'
    status = 404

HTTPNotFound = NotFound  # Alias


@implementer(IMethodNotAllowed)
class MethodNotAllowed(HTTPException):
    errmsg = 'Method Not Allowed'
    status = 405

HTTPMethodNotAllowed = MethodNotAllowed  # Alias


class HTTPNotAcceptable(HTTPClientError):
    errmsg = 'Not Acceptable'
    status = 406


class HTTPProxyAuthenticationRequired(HTTPClientError):
    errmsg = 'Proxy Authentication Required'
    status = 407


class HTTPRequestTimeout(HTTPClientError):
    errmsg = 'Request Timeout'
    status = 408


class HTTPConflict(HTTPClientError):
    errmsg = 'Conflict'
    status = 409


class HTTPGone(HTTPClientError):
    errmsg = 'Gone'
    status = 410


class HTTPLengthRequired(HTTPClientError):
    errmsg = 'Length Required'
    status = 411


class HTTPPreconditionFailed(HTTPClientError):
    errmsg = 'Precondition Failed'
    status = 412


class HTTPRequestEntityTooLarge(HTTPClientError):
    errmsg = 'Request Entity Too Large'
    status = 413


class HTTPRequestURITooLong(HTTPClientError):
    errmsg = 'Request-URI Too Long'
    status = 414


class HTTPUnsupportedMediaType(HTTPClientError):
    errmsg = 'Unsupported Media Type'
    status = 415


class HTTPRequestRangeNotSatisfiable(HTTPClientError):
    errmsg = 'Request Range Not Satisfiable'
    status = 416


class HTTPExpectationFailed(HTTPClientError):
    errmsg = 'Expectation Failed'
    status = 417


class HTTPUnprocessableEntity(HTTPClientError):
    errmsg = 'Unprocessable Entity'
    status = 422


class ResourceLockedError(HTTPException):
    # Was defined in webdav.Lockable before.
    errmsg = 'Locked'
    status = 423

HTTPLocked = ResourceLockedError  # Alias


class HTTPFailedDependency(HTTPClientError):
    errmsg = 'Failed Dependency'
    status = 424


class HTTPUpgradeRequired(HTTPClientError):
    errmsg = 'Upgrade Required'
    status = 426


class HTTPPreconditionRequired(HTTPClientError):
    errmsg = 'Precondition Required'
    status = 428


class HTTPTooManyRequests(HTTPClientError):
    errmsg = 'Too Many Requests'
    status = 429


class HTTPRequestHeaderFieldsTooLarge(HTTPClientError):
    errmsg = 'Request Header Fields Too Large'
    status = 431


class HTTPUnavailableForLegalReasons(HTTPClientError):
    errmsg = 'Unavailable For Legal Reasons'
    status = 451


class HTTPServerError(HTTPError):
    """Base class for 5xx status codes."""
    errmsg = 'Internal Server Error'
    status = 500


@implementer(IException)
class InternalError(HTTPServerError):
    pass

HTTPInternalServerError = InternalError  # Alias


class HTTPNotImplemented(HTTPServerError):
    errmsg = 'Not Implemented'
    status = 501


class HTTPBadGateway(HTTPServerError):
    errmsg = 'Bad Gateway'
    status = 502


class HTTPServiceUnavailable(HTTPServerError):
    errmsg = 'Service Unavailable'
    status = 503


class HTTPGatewayTimeout(HTTPServerError):
    errmsg = 'Gateway Timeout'
    status = 504


class HTTPVersionNotSupported(HTTPServerError):
    errmsg = 'HTTP Version Not Supported'
    status = 505


class HTTPInsufficientStorage(HTTPServerError):
    errmsg = 'Insufficient Storage'
    status = 507


class HTTPNotExtended(HTTPServerError):
    errmsg = 'Not Extended'
    status = 510


class HTTPNetworkAuthenticationRequired(HTTPServerError):
    errmsg = 'Network Authentication Required'
    status = 511


def convertExceptionType(name):
    import zExceptions
    etype = None
    if name in builtins.__dict__:
        etype = getattr(builtins, name)
    elif hasattr(zExceptions, name):
        etype = getattr(zExceptions, name)
    if (etype is not None and
            isinstance(etype, class_types) and
            issubclass(etype, Exception)):
        return etype


def upgradeException(t, v):
    etype = convertExceptionType(t.__name__)
    if etype is not None:
        t = etype
    return t, v
