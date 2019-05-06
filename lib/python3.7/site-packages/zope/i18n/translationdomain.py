##############################################################################
#
# Copyright (c) 2001-2008 Zope Foundation and Contributors.
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
"""Global Translation Service for providing I18n to file-based code.
"""

import zope.component
import zope.interface

from zope.i18nmessageid import Message
from zope.i18n import translate, interpolate
from zope.i18n.interfaces import ITranslationDomain, INegotiator


# The configuration should specify a list of fallback languages for the
# site.  If a particular catalog for a negotiated language is not available,
# then the zcml specified order should be tried.  If that fails, then as a
# last resort the languages in the following list are tried.  If these fail
# too, then the msgid is returned.
#
# Note that these fallbacks are used only to find a catalog.  If a particular
# message in a catalog is not translated, tough luck, you get the msgid.
LANGUAGE_FALLBACKS = ['en']

text_type = str if bytes is not str else unicode


@zope.interface.implementer(ITranslationDomain)
class TranslationDomain(object):

    def __init__(self, domain, fallbacks=None):
        self.domain = (
            domain.decode("utf-8") if isinstance(domain, bytes) else domain)
        # _catalogs maps (language, domain) to IMessageCatalog instances
        self._catalogs = {}
        # _data maps IMessageCatalog.getIdentifier() to IMessageCatalog
        self._data = {}
        # What languages to fallback to, if there is no catalog for the
        # requested language (no fallback on individual messages)
        self.setLanguageFallbacks(fallbacks)

    def _registerMessageCatalog(self, language, catalog_name):
        key = language
        mc = self._catalogs.setdefault(key, [])
        mc.append(catalog_name)

    def addCatalog(self, catalog):
        self._data[catalog.getIdentifier()] = catalog
        self._registerMessageCatalog(catalog.language,
                                     catalog.getIdentifier())

    def setLanguageFallbacks(self, fallbacks=None):
        if fallbacks is None:
            fallbacks = LANGUAGE_FALLBACKS
        self._fallbacks = fallbacks

    def translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None,
                  msgid_plural=None, default_plural=None, number=None):
        """See zope.i18n.interfaces.ITranslationDomain"""
        # if the msgid is empty, let's save a lot of calculations and return
        # an empty string.
        if msgid == u'':
            return u''

        if target_language is None and context is not None:
            langs = self._catalogs.keys()
            # invoke local or global unnamed 'INegotiator' utilities
            negotiator = zope.component.getUtility(INegotiator)
            # try to determine target language from negotiator utility
            target_language = negotiator.getLanguage(langs, context)

        return self._recursive_translate(
            msgid, mapping, target_language, default, context,
            msgid_plural, default_plural, number)

    def _recursive_translate(self, msgid, mapping, target_language, default,
                             context,  msgid_plural, default_plural, number,
                             seen=None):
        """Recursively translate msg."""
        # MessageID attributes override arguments
        if isinstance(msgid, Message):
            if msgid.domain != self.domain:
                return translate(
                    msgid, msgid.domain, mapping, context, target_language,
                    default, msgid_plural, default_plural, number)
            default = msgid.default
            mapping = msgid.mapping
            msgid_plural = msgid.msgid_plural
            default_plural = msgid.default_plural
            number = msgid.number

        # Recursively translate mappings, if they are translatable
        if (mapping is not None
                and Message in (type(m) for m in mapping.values())):
            if seen is None:
                seen = set()
            seen.add((msgid, msgid_plural))
            mapping = mapping.copy()
            for key, value in mapping.items():
                if isinstance(value, Message):
                    # TODO Why isn't there an IMessage interface?
                    # https://bugs.launchpad.net/zope3/+bug/220122
                    if (value, value.msgid_plural) in seen:
                        raise ValueError(
                            "Circular reference in mappings detected: %s" %
                            value)
                    mapping[key] = self._recursive_translate(
                        value, mapping, target_language, default, context,
                        msgid_plural, default_plural, number, seen)

        if default is None:
            default = text_type(msgid)
        if msgid_plural is not None and default_plural is None:
            default_plural = text_type(msgid_plural)

        # Get the translation. Use the specified fallbacks if this fails
        catalog_names = self._catalogs.get(target_language)
        if catalog_names is None:
            for language in self._fallbacks:
                catalog_names = self._catalogs.get(language)
                if catalog_names is not None:
                    break

        text = default
        if catalog_names:
            if len(catalog_names) == 1:
                # this is a slight optimization for the case when there is a
                # single catalog. More importantly, it is extremely helpful
                # when testing and the test language is used, because it
                # allows the test language to get the default.
                if msgid_plural is not None:
                    # This is a plural
                    text = self._data[catalog_names[0]].queryPluralMessage(
                        msgid, msgid_plural, number, default, default_plural)
                else:
                    text = self._data[catalog_names[0]].queryMessage(
                        msgid, default)
            else:
                for name in catalog_names:
                    catalog = self._data[name]
                    if msgid_plural is not None:
                        # This is a plural
                        s = catalog.queryPluralMessage(
                            msgid, msgid_plural, number,
                            default, default_plural)
                    else:
                        s = catalog.queryMessage(msgid)
                    if s is not None:
                        text = s
                        break

        # Now we need to do the interpolation
        if text and mapping:
            text = interpolate(text, mapping)
        return text

    def getCatalogsInfo(self):
        return self._catalogs

    def reloadCatalogs(self, catalogNames):
        for catalogName in catalogNames:
            self._data[catalogName].reload()
