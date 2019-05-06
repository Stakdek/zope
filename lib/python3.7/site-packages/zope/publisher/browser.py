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
"""Browser-specific Publisher classes

Here we define the specific 'BrowserRequest' and 'BrowserResponse' class. The
big improvement of the 'BrowserRequest' to 'HTTPRequest' is that is can handle
HTML form data and convert them into a Python-native format. Even file data is
packaged into a nice, Python-friendly 'FileUpload' object.
"""
__docformat__ = 'restructuredtext'

import re
from cgi import FieldStorage
import tempfile

import zope.component
import zope.interface
from zope.interface import implementer, directlyProvides
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.interfaces import IUserPreferredCharsets
from zope.i18n.interfaces import IModifiableUserPreferredLanguages
from zope.location import Location

from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IDefaultSkin
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserApplicationRequest
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.http import HTTPRequest, HTTPResponse, getCharsetUsingRequest

# BBB imports, this compoennts get moved from this module
from zope.publisher.interfaces import ISkinType #BBB import
from zope.publisher.interfaces import ISkinChangedEvent #BBB import
from zope.publisher.skinnable import getDefaultSkin #BBB import
from zope.publisher.skinnable import setDefaultSkin #BBB import
from zope.publisher.skinnable import applySkin #BBB import
from zope.publisher.skinnable import SkinChangedEvent #BBB import

from zope.publisher._compat import PYTHON2, _u


__ArrayTypes = (list, tuple)

start_of_header_search=re.compile(b'(<head[^>]*>)', re.I).search
base_re_search=re.compile(b'(<base.*?>)',re.I).search
isRelative = re.compile("[-_.!~*a-zA-z0-9'()@&=+$,]+(/|$)").match
newlines = re.compile('\r\n|\n\r|\r')

def is_text_html(content_type):
    return content_type.startswith('text/html')

# Flag Constants
SEQUENCE = 1
DEFAULT = 2
RECORD = 4
RECORDS = 8
REC = RECORD | RECORDS
CONVERTED = 32
DEFAULTABLE_METHODS = 'GET', 'POST', 'HEAD'


def field2string(v):
    if hasattr(v, 'read'):
        return v.read()
    return str(v)

def field2text(v, nl=newlines):
    return nl.sub("\n", field2string(v))

def field2required(v):
    v = field2string(v)
    if not v.strip():
        raise ValueError('No input for required field<p>')
    return v

def field2int(v):
    if isinstance(v, __ArrayTypes):
        return list(map(field2int, v))
    v = field2string(v)
    if not v:
        raise ValueError('Empty entry when <strong>integer</strong> expected')
    try:
        return int(v)
    except ValueError:
        raise ValueError("An integer was expected in the value '%s'" % v)

def field2float(v):
    if isinstance(v, __ArrayTypes):
        return list(map(field2float, v))
    v = field2string(v)
    if not v:
        raise ValueError(
            'Empty entry when <strong>floating-point number</strong> expected')
    try:
        return float(v)
    except ValueError:
        raise ValueError(
                "A floating-point number was expected in the value '%s'" % v)

def field2long(v):
    if isinstance(v, __ArrayTypes):
        return list(map(field2long, v))
    v = field2string(v)

    # handle trailing 'L' if present.
    if v and v[-1].upper() == 'L':
        v = v[:-1]
    if not v:
        raise ValueError('Empty entry when <strong>integer</strong> expected')
    try:
        return int(v)
    except ValueError:
        raise ValueError("A long integer was expected in the value '%s'" % v)

def field2tokens(v):
    return field2string(v).split()

def field2lines(v):
    if isinstance(v, __ArrayTypes):
        return [str(item) for item in v]
    return field2text(v).splitlines()

def field2boolean(v):
    return bool(v)

type_converters = {
    'float':    field2float,
    'int':      field2int,
    'long':     field2long,
    'string':   field2string,
    'required': field2required,
    'tokens':   field2tokens,
    'lines':    field2lines,
    'text':     field2text,
    'boolean':  field2boolean,
    }

get_converter = type_converters.get

def registerTypeConverter(field_type, converter, replace=False):
    """Add a custom type converter to the registry.

    o If 'replace' is not true, raise a KeyError if a converter is
      already registered for 'field_type'.
    """
    existing = type_converters.get(field_type)

    if existing is not None and not replace:
        raise KeyError('Existing converter for field_type: %s' % field_type)

    type_converters[field_type] = converter


isCGI_NAME = lambda key: key in {
    # These fields are placed in request.environ instead of request.form.
    'SERVER_SOFTWARE' : 1,
    'SERVER_NAME' : 1,
    'GATEWAY_INTERFACE' : 1,
    'SERVER_PROTOCOL' : 1,
    'SERVER_PORT' : 1,
    'REQUEST_METHOD' : 1,
    'PATH_INFO' : 1,
    'PATH_TRANSLATED' : 1,
    'SCRIPT_NAME' : 1,
    'QUERY_STRING' : 1,
    'REMOTE_HOST' : 1,
    'REMOTE_ADDR' : 1,
    'AUTH_TYPE' : 1,
    'REMOTE_USER' : 1,
    'REMOTE_IDENT' : 1,
    'CONTENT_TYPE' : 1,
    'CONTENT_LENGTH' : 1,
    'SERVER_URL': 1,
    }

hide_key=lambda key: key in {
    'HTTP_AUTHORIZATION':1,
    'HTTP_CGI_AUTHORIZATION': 1,
     }

class Record(object):

    _attrs = frozenset(('get', 'keys', 'items', 'values', 'copy',
                       'has_key', '__contains__'))

    def __getattr__(self, key, default=None):
        if key in self._attrs:
            return getattr(self.__dict__, key)
        raise AttributeError(key)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __str__(self):
        items = list(self.__dict__.items())
        items.sort()
        return "{" + ", ".join(["%s: %s" % item for item in items]) + "}"

    def __repr__(self):
        items = list(self.__dict__.items())
        items.sort()
        return ("{"
            + ", ".join(["%s: %s" % (key, repr(value))
            for key, value in items]) + "}")

_get_or_head = 'GET', 'HEAD'
@implementer(IBrowserRequest, IBrowserApplicationRequest)
class BrowserRequest(HTTPRequest):

    __slots__ = (
        '__provides__', # Allow request to directly provide interfaces
        'form', # Form data
        'charsets', # helper attribute
        '__meth',
        '__tuple_items',
        '__defaults',
        '__annotations__',
        )

    # Set this to True in a subclass to redirect GET requests when the
    # effective and actual URLs differ.
    use_redirect = False

    def __init__(self, body_instream, environ, response=None):
        self.form = {}
        self.charsets = None
        super(BrowserRequest, self).__init__(body_instream, environ, response)


    def _createResponse(self):
        return BrowserResponse()

    def _decode(self, text):
        """Try to decode the text using one of the available charsets."""
        # According to PEP-3333, in python-3, QUERY_STRING is a string,
        # representing 'latin-1' encoded byte array. So, if we are in python-3
        # context, encode text as 'latin-1' first, to try to decode
        # resulting byte array using user-supplied charset.
        if not isinstance(text, bytes):
            text = text.encode('latin-1')
        if self.charsets is None:
            envadapter = IUserPreferredCharsets(self)
            self.charsets = envadapter.getPreferredCharsets() or ['utf-8']
            self.charsets = [c for c in self.charsets if c != '*']
        for charset in self.charsets:
            try:
                text = _u(text, charset)
                break
            except UnicodeError:
                pass
        return text

    def processInputs(self):
        'See IPublisherRequest'

        if self.method not in _get_or_head:
            # Process self.form if not a GET request.
            fp = self._body_instream
            if self.method == 'POST':
                content_type = self._environ.get('CONTENT_TYPE')
                if content_type and not (
                    content_type.startswith('application/x-www-form-urlencoded')
                    or
                    content_type.startswith('multipart/')
                    ):
                    # for non-multi and non-form content types, FieldStorage
                    # consumes the body and we have no good place to put it.
                    # So we just won't call FieldStorage. :)
                    return
        else:
            fp = None

        # If 'QUERY_STRING' is not present in self._environ
        # FieldStorage will try to get it from sys.argv[1]
        # which is not what we need.
        if 'QUERY_STRING' not in self._environ:
            self._environ['QUERY_STRING'] = ''

        # The Python 2.6 cgi module mixes the query string and POST values
        # together.  We do not want this.
        env = self._environ
        if self.method == 'POST' and self._environ['QUERY_STRING']:
            env = env.copy()
            del env['QUERY_STRING']


        args = {'encoding': 'utf-8'} if not PYTHON2 else {}
        fs = ZopeFieldStorage(fp=fp, environ=env,
                              keep_blank_values=1, **args)
        # On python 3.4 and up, FieldStorage explictly closes files
        # when it is garbage collected
        # see:
        #   http://bugs.python.org/issue18394
        #   https://hg.python.org/cpython/rev/c0e9ba7b26d5
        # so we keep a reference to the FieldStorage till we are
        # finished processing the request.
        self.hold(fs)

        fslist = getattr(fs, 'list', None)
        if fslist is not None:
            self.__meth = None
            self.__tuple_items = {}
            self.__defaults = {}

            # process all entries in the field storage (form)
            for item in fslist:
                self.__processItem(item)

            if self.__defaults:
                self.__insertDefaults()

            if self.__tuple_items:
                self.__convertToTuples()

            if self.__meth:
                self.setPathSuffix((self.__meth,))

    _typeFormat = re.compile('([a-zA-Z][a-zA-Z0-9_]+|\\.[xy])$')

    def __processItem(self, item):
        """Process item in the field storage."""

        # Check whether this field is a file upload object
        # Note: A field exists for files, even if no filename was
        # passed in and no data was uploaded. Therefore we can only
        # tell by the empty filename that no upload was made.
        key = item.name
        if (hasattr(item, 'file') and hasattr(item, 'filename')
            and hasattr(item,'headers')):
            if (item.file and
                (item.filename is not None and item.filename != ''
                 # RFC 1867 says that all fields get a content-type.
                 # or 'content-type' in map(lower, item.headers.keys())
                 )):
                item = FileUpload(item)
            else:
                item = item.value

        flags = 0
        converter = None

        # Loop through the different types and set
        # the appropriate flags
        # Syntax: var_name:type_name

        # We'll search from the back to the front.
        # We'll do the search in two steps.  First, we'll
        # do a string search, and then we'll check it with
        # a re search.

        while key:
            pos = key.rfind(":")
            if pos < 0:
                break
            match = self._typeFormat.match(key, pos + 1)
            if match is None:
                break

            key, type_name = key[:pos], key[pos + 1:]

            # find the right type converter
            c = get_converter(type_name, None)

            if c is not None:
                converter = c
                flags |= CONVERTED
            elif type_name == 'list':
                flags |= SEQUENCE
            elif type_name == 'tuple':
                self.__tuple_items[key] = 1
                flags |= SEQUENCE
            elif (type_name == 'method' or type_name == 'action'):
                if key:
                    self.__meth = key
                else:
                    self.__meth = item
            elif (type_name == 'default_method'
                    or type_name == 'default_action') and not self.__meth:
                if key:
                    self.__meth = key
                else:
                    self.__meth = item
            elif type_name == 'default':
                flags |= DEFAULT
            elif type_name == 'record':
                flags |= RECORD
            elif type_name == 'records':
                flags |= RECORDS
            elif type_name == 'ignore_empty' and not item:
                # skip over empty fields
                return

        if key is not None:
            key = self._decode(key)

        if isinstance(item, (str, bytes)):
            item = self._decode(item)

        if flags:
            self.__setItemWithType(key, item, flags, converter)
        else:
            self.__setItemWithoutType(key, item)

    def __setItemWithoutType(self, key, item):
        """Set item value without explicit type."""
        form = self.form
        if key not in form:
            form[key] = item
        else:
            found = form[key]
            if isinstance(found, list):
                found.append(item)
            else:
                form[key] = [found, item]

    def __setItemWithType(self, key, item, flags, converter):
        """Set item value with explicit type."""
        #Split the key and its attribute
        if flags & REC:
            key, attr = self.__splitKey(key)

        # defer conversion
        if flags & CONVERTED:
            try:
                item = converter(item)
            except:
                if item or flags & DEFAULT or key not in self.__defaults:
                    raise
                item = self.__defaults[key]
                if flags & RECORD:
                    item = getattr(item, attr)
                elif flags & RECORDS:
                    item = getattr(item[-1], attr)

        # Determine which dictionary to use
        if flags & DEFAULT:
            form = self.__defaults
        else:
            form = self.form

        # Insert in dictionary
        if key not in form:
            if flags & SEQUENCE:
                item = [item]
            if flags & RECORD:
                r = form[key] = Record()
                setattr(r, attr, item)
            elif flags & RECORDS:
                r = Record()
                setattr(r, attr, item)
                form[key] = [r]
            else:
                form[key] = item
        else:
            r = form[key]
            if flags & RECORD:
                if not flags & SEQUENCE:
                    setattr(r, attr, item)
                else:
                    if not hasattr(r, attr):
                        setattr(r, attr, [item])
                    else:
                        getattr(r, attr).append(item)
            elif flags & RECORDS:
                last = r[-1]
                if not hasattr(last, attr):
                    if flags & SEQUENCE:
                        item = [item]
                    setattr(last, attr, item)
                else:
                    if flags & SEQUENCE:
                        getattr(last, attr).append(item)
                    else:
                        new = Record()
                        setattr(new, attr, item)
                        r.append(new)
            else:
                if isinstance(r, list):
                    r.append(item)
                else:
                    form[key] = [r, item]

    def __splitKey(self, key):
        """Split the key and its attribute."""
        i = key.rfind(".")
        if i >= 0:
            return key[:i], key[i + 1:]
        return key, ""

    def __convertToTuples(self):
        """Convert form values to tuples."""
        form = self.form

        for key in self.__tuple_items:
            if key in form:
                form[key] = tuple(form[key])
            else:
                k, attr = self.__splitKey(key)

                # remove any type_names in the attr
                i = attr.find(":")
                if i >= 0:
                    attr = attr[:i]

                if k in form:
                    item = form[k]
                    if isinstance(item, Record):
                        if hasattr(item, attr):
                            setattr(item, attr, tuple(getattr(item, attr)))
                    else:
                        for v in item:
                            if hasattr(v, attr):
                                setattr(v, attr, tuple(getattr(v, attr)))

    def __insertDefaults(self):
        """Insert defaults into form dictionary."""
        form = self.form

        for keys, values in self.__defaults.items():
            if not keys in form:
                form[keys] = values
            else:
                item = form[keys]
                if isinstance(values, Record):
                    for k, v in values.items():
                        if not hasattr(item, k):
                            setattr(item, k, v)
                elif isinstance(values, list):
                    for val in values:
                        if isinstance(val, Record):
                            for k, v in val.items():
                                for r in item:
                                    if not hasattr(r, k):
                                        setattr(r, k, v)
                        elif not val in item:
                            item.append(val)

    def traverse(self, obj):
        'See IPublisherRequest'

        ob = super(BrowserRequest, self).traverse(obj)
        method = self.method

        base_needed = 0
        if self._path_suffix:
            # We had a :method variable, so we need to set the base,
            # but we don't look for default documents any more.
            base_needed = 1
            redirect = 0
        elif method in DEFAULTABLE_METHODS:
            # We need to check for default documents
            publication = self.publication

            nsteps = 0
            ob, add_steps = publication.getDefaultTraversal(self, ob)
            while add_steps:
                nsteps += len(add_steps)
                add_steps = list(add_steps)
                add_steps.reverse()
                self.setTraversalStack(add_steps)
                ob = super(BrowserRequest, self).traverse(ob)
                ob, add_steps = publication.getDefaultTraversal(self, ob)

            if nsteps != self._endswithslash:
                base_needed = 1
                redirect = self.use_redirect and method == 'GET'


        if base_needed:
            url = self.getURL()
            response = self.response
            if redirect:
                response.redirect(url)
                return ''
            elif not response.getBase():
                response.setBase(url)

        return ob

    def keys(self):
        'See Interface.Common.Mapping.IEnumerableMapping'
        d = {}
        d.update(self._environ)
        d.update(self._cookies)
        d.update(self.form)
        return list(d.keys())


    def get(self, key, default=None):
        'See Interface.Common.Mapping.IReadMapping'
        marker = object()
        result = self.form.get(key, marker)
        if result is not marker:
            return result

        return super(BrowserRequest, self).get(key, default)

class ZopeFieldStorage(FieldStorage):

    def make_file(self, binary=None):
        if PYTHON2 or self._binary_file:
            return tempfile.NamedTemporaryFile("w+b")
        else:
            return tempfile.NamedTemporaryFile("w+",
                    encoding=self.encoding, newline='\n')


class FileUpload(object):
    '''File upload objects

    File upload objects are used to represent file-uploaded data.

    File upload objects can be used just like files.

    In addition, they have a 'headers' attribute that is a dictionary
    containing the file-upload headers, and a 'filename' attribute
    containing the name of the uploaded file.
    '''

    def __init__(self, aFieldStorage):

        file = aFieldStorage.file
        if hasattr(file, '__methods__'):
            methods = file.__methods__
        else:
            methods = ['close', 'fileno', 'flush', 'isatty',
                'read', 'readline', 'readlines', 'seek',
                'tell', 'truncate', 'write', 'writelines',
                'name']

        d = self.__dict__
        for m in methods:
            if hasattr(file,m):
                d[m] = getattr(file,m)

        self.headers = aFieldStorage.headers
        filename = aFieldStorage.filename
        if isinstance(aFieldStorage.filename, bytes):
            filename = _u(aFieldStorage.filename, 'UTF-8')
        # fix for IE full paths
        filename = filename[filename.rfind('\\')+1:].strip()
        self.filename = filename

class RedirectingBrowserRequest(BrowserRequest):
    """Browser requests that redirect when the actual and effective URLs differ
    """

    use_redirect = True

class TestRequest(BrowserRequest):
    """Browser request with a constructor convenient for testing
    """

    def __init__(self, body_instream=None, environ=None, form=None,
                 skin=None, **kw):

        _testEnv =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }

        if environ is not None:
            _testEnv.update(environ)

        if kw:
            _testEnv.update(kw)
        if body_instream is None:
            from io import BytesIO
            body_instream = BytesIO()

        super(TestRequest, self).__init__(body_instream, _testEnv)
        if form:
            self.form.update(form)

        # Setup locale object
        langs = BrowserLanguages(self).getPreferredLanguages()
        from zope.i18n.locales import locales
        if not langs or langs[0] == '':
            self._locale = locales.getLocale(None, None, None)
        else:
            parts = (langs[0].split('-') + [None, None])[:3]
            self._locale = locales.getLocale(*parts)

        if skin is not None:
            directlyProvides(self, skin)
        else:
            directlyProvides(self, IDefaultBrowserLayer)



class BrowserResponse(HTTPResponse):
    """Browser response
    """

    __slots__ = (
        '_base', # The base href
        )

    def _implicitResult(self, body):
        content_type = self.getHeader('content-type')
        if content_type is None and self._status != 304:
            if isHTML(body):
                content_type = 'text/html'
            else:
                content_type = 'text/plain'
            self.setHeader('x-content-type-warning', 'guessed from content')
            self.setHeader('content-type', content_type)

        body, headers = super(BrowserResponse, self)._implicitResult(body)
        body = self.__insertBase(body)
        # Update the Content-Length header to account for the inserted
        # <base> tag.
        headers = [
            (name, value) for name, value in headers
            if name != 'content-length'
            ]
        headers.append(('content-length', str(len(body))))
        return body, headers


    def __insertBase(self, body):
        # Only insert a base tag if content appears to be html.
        content_type = self.getHeader('content-type', '')
        if content_type and not is_text_html(content_type):
            return body

        if self.getBase():
            if body:
                match = start_of_header_search(body)
                if match is not None:
                    index = match.start(0) + len(match.group(0))
                    ibase = base_re_search(body)
                    if ibase is None:
                        # Make sure the base URL is not a unicode string.
                        base = self.getBase()
                        if not isinstance(base, bytes):
                            encoding = getCharsetUsingRequest(self._request) or 'utf-8'
                            base = self.getBase().encode(encoding)
                        #body = (b'%s\n<base href="%s" />\n%s' %
                        #        (body[:index], base, body[index:]))
                        body = b''.join([body[:index],
                                         b'\n<base href="',
                                         base,
                                         b'" />\n',
                                         body[index:]])
        return body

    def getBase(self):
        return getattr(self, '_base', '')

    def setBase(self, base):
        self._base = base

    def redirect(self, location, status=None, trusted=False):
        base = getattr(self, '_base', '')
        if base and isRelative(str(location)):
            l = base.rfind('/')
            if l >= 0:
                base = base[:l+1]
            else:
                base += '/'
            location = base + location

        # TODO: HTTP redirects must provide an absolute location, see
        #       http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.30
        #       So, what if location is relative and base is unknown?  Uncomment
        #       the following and you'll see that it actually happens.
        #
        # if isRelative(str(location)):
        #     raise AssertionError('Cannot determine absolute location')

        return super(BrowserResponse, self).redirect(location, status, trusted)

    def reset(self):
        super(BrowserResponse, self).reset()
        self._base = ''

def isHTML(str):
     """Try to determine whether str is HTML or not."""
     s = str.lstrip().lower()
     if s.startswith('<!doctype html'):
         return True
     if s.startswith('<html') and (s[5:6] in ' >'):
         return True
     if s.startswith('<!--'):
         idx = s.find('<html')
         return idx > 0 and (s[idx+5:idx+6] in ' >')
     else:
         return False

def normalize_lang(lang):
    lang = lang.strip().lower()
    lang = lang.replace('_', '-')
    lang = lang.replace(' ', '')
    return lang

@zope.component.adapter(IHTTPRequest)
@implementer(IUserPreferredLanguages)
class BrowserLanguages(object):

    def __init__(self, request):
        self.request = request

    def getPreferredLanguages(self):
        '''See interface IUserPreferredLanguages'''
        accept_langs = self.request.get('HTTP_ACCEPT_LANGUAGE', '').split(',')

        # Normalize lang strings
        accept_langs = [normalize_lang(l) for l in accept_langs]
        # Then filter out empty ones
        accept_langs = [l for l in accept_langs if l]

        accepts = []
        for index, lang in enumerate(accept_langs):
            l = lang.split(';', 2)

            # If not supplied, quality defaults to 1...
            quality = 1.0

            if len(l) == 2:
                q = l[1]
                if q.startswith('q='):
                    q = q.split('=', 2)[1]
                    try:
                        quality = float(q)
                    except ValueError:
                        # malformed quality value, skip it.
                        continue

            if quality == 1.0:
                # ... but we use 1.9 - 0.001 * position to
                # keep the ordering between all items with
                # 1.0 quality, which may include items with no quality
                # defined, and items with quality defined as 1.
                quality = 1.9 - (0.001 * index)

            accepts.append((quality, l[0]))

        # Filter langs with q=0, which means
        # unwanted lang according to the spec
        # See: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
        accepts = [acc for acc in accepts if acc[0]]

        accepts.sort()
        accepts.reverse()

        return [lang for quality, lang in accepts]

class NotCompatibleAdapterError(Exception):
    """Adapter not compatible with
       zope.i18n.interfaces.IModifiableBrowserLanguages has been used.
    """

BROWSER_LANGUAGES_KEY = "zope.publisher.browser.IUserPreferredLanguages"

@implementer(IUserPreferredLanguages)
class CacheableBrowserLanguages(BrowserLanguages):

    def getPreferredLanguages(self):
        languages_data = self._getLanguagesData()
        if "overridden" in languages_data:
            return languages_data["overridden"]
        elif "cached" not in languages_data:
            languages_data["cached"] = super(
                CacheableBrowserLanguages, self).getPreferredLanguages()
        return languages_data["cached"]

    def _getLanguagesData(self):
        annotations = self.request.annotations
        languages_data = annotations.get(BROWSER_LANGUAGES_KEY)
        if languages_data is None:
            annotations[BROWSER_LANGUAGES_KEY] = languages_data = {}
        return languages_data

@implementer(IModifiableUserPreferredLanguages)
class ModifiableBrowserLanguages(CacheableBrowserLanguages):

    def setPreferredLanguages(self, languages):
        languages_data = self.request.annotations.get(BROWSER_LANGUAGES_KEY)
        if languages_data is None:
            # Better way to create a compatible with
            # IModifiableUserPreferredLanguages adapter is to use
            # CacheableBrowserLanguages as base class or as example.
            raise NotCompatibleAdapterError("Adapter not compatible with "
                "zope.i18n.interfaces.IModifiableBrowserLanguages "
                "has been used.")
        languages_data["overridden"] = languages
        self.request.setupLocale()

@implementer(IBrowserView)
class BrowserView(Location):
    """Browser View.

    >>> view = BrowserView("context", "request")
    >>> view.context
    'context'
    >>> view.request
    'request'

    >>> view.__parent__
    'context'
    >>> view.__parent__ = "parent"
    >>> view.__parent__
    'parent'
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __getParent(self):
        return getattr(self, '_parent', self.context)

    def __setParent(self, parent):
        self._parent = parent

    __parent__ = property(__getParent, __setParent)

@implementer(IBrowserPage)
class BrowserPage(BrowserView):
    """Browser page

    To create a page, which is an object that is published as a page,
    you need to provide an object that:

    - has a __call__ method and that

    - provides IBrowserPublisher, and

    - if ZPT is going to be used, then your object should also provide
      request and context attributes.

    The BrowserPage base class provides a standard constructor and a
    simple implementation of IBrowserPublisher:

      >>> class MyPage(BrowserPage):
      ...     pass

      >>> request = TestRequest()
      >>> context = object()
      >>> page = MyPage(context, request)

      >>> from zope.publisher.interfaces.browser import IBrowserPublisher
      >>> IBrowserPublisher.providedBy(page)
      True

      >>> page.browserDefault(request) == (page, ())
      True

      >>> page.publishTraverse(request, 'bob') # doctest: +ELLIPSIS
      Traceback (most recent call last):
      ...
      NotFound: Object: <zope.publisher.browser.MyPage object at ...>, name: 'bob'

      >>> page.request is request
      True

      >>> page.context is context
      True

    But it doesn't supply a __call__ method:

      >>> page()
      Traceback (most recent call last):
        ...
      NotImplementedError: Subclasses should override __call__ to provide a response body

    It is the subclass' responsibility to do that.

    """

    def browserDefault(self, request):
        return self, ()

    def publishTraverse(self, request, name):
        raise NotFound(self, name, request)

    def __call__(self, *args, **kw):
        raise NotImplementedError("Subclasses should override __call__ to "
                                  "provide a response body")
