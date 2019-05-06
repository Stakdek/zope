import os

#: The environment variable that is consulted when this module
#: is imported to determine the value of `COMPILE_MO_FILES`.
#: Simply set this to a non-empty string to make it True.
COMPILE_MO_FILES_KEY = 'zope_i18n_compile_mo_files'
#: Whether or not the ZCML directives will attempt to compile
#: translation files. Defaults to False.
COMPILE_MO_FILES = os.environ.get(COMPILE_MO_FILES_KEY, False)

#: The environment variable that is consulted when this module
#: is imported to determine the value of `ALLOWED_LANGUAGES`.
#: If set, this should be a comma-separated list of language names.
ALLOWED_LANGUAGES_KEY = 'zope_i18n_allowed_languages'


def _parse_languages(value):
    """
    Utility function to parse languages.

        >>> _parse_languages(None) is None
        True
        >>> _parse_languages("en") == frozenset(('en',))
        True
        >>> _parse_languages('')
        ''
        >>> _parse_languages("en,es") == frozenset(('en', 'es'))
        True

    Leading, trailing and internal whitespace is ignored:

        >>> _parse_languages('en, es') == frozenset(('en', 'es'))
        True
        >>> _parse_languages(" en,es") == frozenset(('en', 'es'))
        True
        >>> _parse_languages("en,es ") == frozenset(('en', 'es'))
        True
    """
    if value:
        value = value.replace(",", " ")
        value = frozenset(value.split())
    return value


#: A set of languages that `zope.i18n.negotiate` will pass to the
#: `zope.i18n.interfaces.INegotiator` utility. If this is None,
#: no utility will be used.
ALLOWED_LANGUAGES = _parse_languages(os.environ.get(ALLOWED_LANGUAGES_KEY, None))
