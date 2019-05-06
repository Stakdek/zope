##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""i18n support.
"""
import re

from zope.component import queryUtility
from zope.i18nmessageid import MessageFactory, Message

from zope.i18n.config import ALLOWED_LANGUAGES
from zope.i18n.interfaces import INegotiator
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.interfaces import IFallbackTranslationDomainFactory

text_type = str if bytes is not str else unicode

# Set up regular expressions for finding interpolation variables in text.
# NAME_RE must exactly match the expression of the same name in the
# zope.tal.taldefs module:
NAME_RE = r"[a-zA-Z_][-a-zA-Z0-9_]*"

_interp_regex = re.compile(r'(?<!\$)(\$(?:(%(n)s)|{(%(n)s)}))'
                           % ({'n': NAME_RE}))


class _FallbackNegotiator(object):

    def getLanguage(self, _allowed, _context):
        return None


_fallback_negotiator = _FallbackNegotiator()


def negotiate(context):
    """
    Negotiate language.

    This only works if the languages are set globally, otherwise each
    message catalog needs to do the language negotiation.

    If no languages are set, this always returns None:

      >>> import zope.i18n as i18n
      >>> from zope.component import queryUtility
      >>> old_allowed_languages = i18n.ALLOWED_LANGUAGES
      >>> i18n.ALLOWED_LANGUAGES = None
      >>> i18n.negotiate('anything') is None
      True

    If languages are set, but there is no ``INegotiator`` utility,
    this returns None:

      >>> i18n.ALLOWED_LANGUAGES = ('en',)
      >>> queryUtility(i18n.INegotiator) is None
      True
      >>> i18n.negotiate('anything') is None
      True

    .. doctest::
        :hide:

        >>> i18n.ALLOWED_LANGUAGES = old_allowed_languages

    """
    if ALLOWED_LANGUAGES is None:
        return None

    negotiator = queryUtility(INegotiator, default=_fallback_negotiator)
    return negotiator.getLanguage(ALLOWED_LANGUAGES, context)


def translate(msgid, domain=None, mapping=None, context=None,
              target_language=None, default=None, msgid_plural=None,
              default_plural=None, number=None):
    """Translate text.

    First setup some test components:

    >>> from zope import component, interface
    >>> import zope.i18n.interfaces

    >>> @interface.implementer(zope.i18n.interfaces.ITranslationDomain)
    ... class TestDomain:
    ...
    ...     def __init__(self, **catalog):
    ...         self.catalog = catalog
    ...
    ...     def translate(self, text, *_, **__):
    ...         return self.catalog[text]

    Normally, the translation system will use a domain utility:

    >>> component.provideUtility(TestDomain(eek=u"ook"), name='my.domain')
    >>> print(translate(u"eek", 'my.domain'))
    ook

    If no domain is given, or if there is no domain utility
    for the given domain, then the text isn't translated:

    >>> print(translate(u"eek"))
    eek

    Moreover the text will be converted to unicode:

    >>> not isinstance(translate('eek', 'your.domain'), bytes)
    True

    A fallback domain factory can be provided. This is normally used
    for testing:

    >>> def fallback(domain=u""):
    ...     return TestDomain(eek=u"test-from-" + domain)
    >>> interface.directlyProvides(
    ...     fallback,
    ...     zope.i18n.interfaces.IFallbackTranslationDomainFactory,
    ...     )

    >>> component.provideUtility(fallback)

    >>> print(translate(u"eek"))
    test-from-

    >>> print(translate(u"eek", 'your.domain'))
    test-from-your.domain

    If no target language is provided, but a context is and we were able to
    find a translation domain, we will use the `negotiate` function to
    attempt to determine the language to translate to:

    .. doctest::
        :hide:

        >>> from zope import i18n
        >>> old_negotiate = i18n.negotiate

    >>> def test_negotiate(context):
    ...     print("Negotiating for %r" % (context,))
    ...     return 'en'
    >>> i18n.negotiate = test_negotiate
    >>> print(translate('eek', 'your.domain', context='context'))
    Negotiating for 'context'
    test-from-your.domain

    .. doctest::
        :hide:

        >>> i18n.negotiate = old_negotiate
    """

    if isinstance(msgid, Message):
        domain = msgid.domain
        default = msgid.default
        mapping = msgid.mapping
        msgid_plural = msgid.msgid_plural
        default_plural = msgid.default_plural
        number = msgid.number

    if default is None:
        default = text_type(msgid)
    if msgid_plural is not None and default_plural is None:
        default_plural = text_type(msgid_plural)

    if domain:
        util = queryUtility(ITranslationDomain, domain)
        if util is None:
            util = queryUtility(IFallbackTranslationDomainFactory)
            if util is not None:
                util = util(domain)
    else:
        util = queryUtility(IFallbackTranslationDomainFactory)
        if util is not None:
            util = util()

    if util is None:
        return interpolate(default, mapping)

    if target_language is None and context is not None:
        target_language = negotiate(context)

    return util.translate(
        msgid, mapping, context, target_language, default,
        msgid_plural, default_plural, number)


def interpolate(text, mapping=None):
    """Insert the data passed from mapping into the text.

    First setup a test mapping:

    >>> mapping = {"name": "Zope", "version": 3}

    In the text we can use substitution slots like $varname or ${varname}:

    >>> print(interpolate(u"This is $name version ${version}.", mapping))
    This is Zope version 3.

    Interpolation variables can be used more than once in the text:

    >>> print(interpolate(
    ...     u"This is $name version ${version}. ${name} $version!", mapping))
    This is Zope version 3. Zope 3!

    In case if the variable wasn't found in the mapping or '$$' form
    was used no substitution will happens:

    >>> print(interpolate(
    ...     u"This is $name $version. $unknown $$name $${version}.", mapping))
    This is Zope 3. $unknown $$name $${version}.

    >>> print(interpolate(u"This is ${name}"))
    This is ${name}

    If a mapping value is a message id itself it is interpolated, too:

    >>> from zope.i18nmessageid import Message
    >>> print(interpolate(u"This is $meta.",
    ...             mapping={'meta': Message(u"$name $version",
    ...                                      mapping=mapping)}))
    This is Zope 3.
    """

    def replace(match):
        whole, param1, param2 = match.groups()
        value = mapping.get(param1 or param2, whole)
        if isinstance(value, Message):
            value = interpolate(value, value.mapping)
        return text_type(value)

    if not text or not mapping:
        return text

    return _interp_regex.sub(replace, text)
