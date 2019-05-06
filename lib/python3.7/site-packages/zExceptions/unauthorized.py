##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope.interface import implementer
from zope.security.interfaces import IUnauthorized

from zExceptions import HTTPClientError
from ._compat import PY3
from ._compat import string_types
from ._compat import unicode


@implementer(IUnauthorized)
class Unauthorized(HTTPClientError):
    """Some user wasn't allowed to access a resource
    """
    errmsg = 'Unauthorized'
    realm = None
    status = 401

    def _get_message(self):
        return self._message

    message = property(_get_message,)

    def __init__(self, message=None, value=None, needed=None,
                 name=None, realm=None, **kw):
        """Possible signatures:

        Unauthorized()
        Unauthorized(message) # Note that message includes a space
        Unauthorized(name)
        Unauthorized(name, value)
        Unauthorized(name, value, needed)
        Unauthorized(message, value, needed, name)
        Unauthorized(message, value, needed, name, realm)

        Where needed is a mapping objects with items representing requirements
        (e.g. {'permission': 'add spam'}). Any extra keyword arguments
        provides are added to needed.
        """
        if (name is None and (
                not isinstance(message, string_types) or
                len(message.split()) <= 1)):
            # First arg is a name, not a message
            name = message
            message = None

        self.name = name
        self._message = message
        self.value = value
        self.setRealm(realm)

        if kw:
            if needed:
                needed.update(kw)
            else:
                needed = kw

        self.needed = needed

    def __unicode__(self):
        if self.message is not None:
            message = (self.message if
                       isinstance(self.message, unicode) else
                       self.message.decode('utf-8'))
            return message
        if self.name is not None:
            name = (self.name if
                    isinstance(self.name, unicode) else
                    self.name.decode('utf-8'))
            return ("You are not allowed to access '%s' in this context"
                    % name)
        elif self.value is not None:
            return ("You are not allowed to access '%s' in this context"
                    % self.getValueName())
        return repr(self)

    if PY3:
        __str__ = __unicode__

        def __bytes__(self):
            return self.__unicode__().encode('utf-8')
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

    def setRealm(self, value):
        self.realm = value
        if value:
            self.setHeader('WWW-Authenticate', 'basic realm="%s"' % value)

    def getValueName(self):
        v = self.value
        vname = getattr(v, '__name__', None)
        if vname:
            return vname
        c = getattr(v, '__class__', type(v))
        c = getattr(c, '__name__', 'object')
        return "a particular %s" % c
