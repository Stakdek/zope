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
"""A simple implementation of a Message Catalog.
"""

from functools import wraps
from gettext import GNUTranslations
from zope.i18n.interfaces import IGlobalMessageCatalog
from zope.interface import implementer


class _KeyErrorRaisingFallback(object):
    def ugettext(self, message):
        raise KeyError(message)

    def ungettext(self, singular, plural, n):
        raise KeyError(singular)

    gettext = ugettext
    ngettext = ungettext


def plural_formatting(func):
    """This decorator interpolates the possible formatting marker.
    This interpolation marker is usally present for plurals.
    Example: `There are %d apples` or `They have %s pies.`

    Please note that the interpolation can be done, alternatively,
    using the mapping. This is only present as a conveniance.
    """
    @wraps(func)
    def pformat(catalog, singular, plural, n, *args, **kwargs):
        msg = func(catalog, singular, plural, n, *args, **kwargs)
        try:
            return msg % n
        except TypeError:
            # The message cannot be formatted : return it "raw".
            return msg
    return pformat


@implementer(IGlobalMessageCatalog)
class GettextMessageCatalog(object):
    """A message catalog based on GNU gettext and Python's gettext module."""

    _catalog = None

    def __init__(self, language, domain, path_to_file):
        """Initialize the message catalog"""
        self.language = (
            language.decode('utf-8') if isinstance(language, bytes)
            else language)
        self.domain = (
            domain.decode("utf-8") if isinstance(domain, bytes)
            else domain)
        self._path_to_file = path_to_file
        self.reload()
        catalog = self._catalog
        catalog.add_fallback(_KeyErrorRaisingFallback())
        self._gettext = (
            catalog.gettext if str is not bytes else catalog.ugettext)
        self._ngettext = (
            catalog.ngettext if str is not bytes else catalog.ungettext)

    def reload(self):
        'See IMessageCatalog'
        with open(self._path_to_file, 'rb') as fp:
            self._catalog = GNUTranslations(fp)

    def getMessage(self, id):
        'See IMessageCatalog'
        return self._gettext(id)

    @plural_formatting
    def getPluralMessage(self, singular, plural, n):
        'See IMessageCatalog'
        return self._ngettext(singular, plural, n)

    @plural_formatting
    def queryPluralMessage(self, singular, plural, n, dft1=None, dft2=None):
        'See IMessageCatalog'
        try:
            return self._ngettext(singular, plural, n)
        except KeyError:
            # Here, we use the catalog plural function to determine
            # if `n` triggers a plural form or not.
            if self._catalog.plural(n):
                return dft2
            return dft1

    def queryMessage(self, id, default=None):
        'See IMessageCatalog'
        try:
            return self._gettext(id)
        except KeyError:
            return default

    def getIdentifier(self):
        'See IMessageCatalog'
        return self._path_to_file
