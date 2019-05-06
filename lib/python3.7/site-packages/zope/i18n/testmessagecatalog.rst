======================
 Test Message Catalog
======================

The test message catalog "translates" test by simply outputing (in
unicode) the domain and message id in square-bracket markers:

    >>> import zope.i18n.testmessagecatalog
    >>> cat = zope.i18n.testmessagecatalog.TestMessageCatalog('foo.bar')

    >>> cat.language, cat.domain
    ('test', 'foo.bar')

    >>> print(cat.queryMessage('eek'))
    [[foo.bar][eek]]

    >>> print(cat.getMessage('eek'))
    [[foo.bar][eek]]

    >>> isinstance(cat.getMessage('eek'), str if bytes is not str else unicode)
    True

    >>> cat.getIdentifier()
    'test'

    >>> cat.reload()

If a message id has a default, it will be included in the output:

    >>> id = zope.i18nmessageid.MessageFactory('foo.bar')('eek', default='Eek')

    >>> print(cat.queryMessage(id))
    [[foo.bar][eek (Eek)]]

    >>> print(cat.getMessage(id))
    [[foo.bar][eek (Eek)]]

If a message doesn't have a default, but a default is passed in to
queryMessage, the default will be used used:

    >>> print(cat.queryMessage('eek', default='Eek'))
    [[foo.bar][eek (Eek)]]

    >>> print(cat.getMessage(id, default='Waaa'))
    [[foo.bar][eek (Eek)]]

Fallback domains
================

The testmessagecatalog module also provide a fallback domain factory
that has the test catalog as it's only catalog:

    >>> factory = zope.i18n.testmessagecatalog.TestMessageFallbackDomain
    >>> import zope.i18n.interfaces
    >>> zope.i18n.interfaces.IFallbackTranslationDomainFactory.providedBy(
    ...     factory)
    True

    >>> domain = factory('foo.bar')
    >>> print(domain.translate('eek'))
    eek

    >>> print(domain.translate('eek', target_language='test'))
    [[foo.bar][eek]]

Note that if a default is padded in, it will be included in test
output:

    >>> print(domain.translate('eek', target_language='test', default='Eek'))
    [[foo.bar][eek (Eek)]]
