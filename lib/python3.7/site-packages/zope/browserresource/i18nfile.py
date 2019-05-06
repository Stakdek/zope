##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Internationalized file resource.
"""
from zope.i18n.interfaces import II18nAware
from zope.i18n.negotiator import negotiator
from zope.interface import implementer, provider

from zope.browserresource.file import FileResource
from zope.browserresource.interfaces import IResourceFactory
from zope.browserresource.interfaces import IResourceFactoryFactory


@implementer(II18nAware)
class I18nFileResource(FileResource):
    """
    A :class:`zope.i18n.interfaces.II18nAware` file resource.

    .. seealso:: `.II18nResourceDirective`
    """

    def __init__(self, data, request, defaultLanguage='en'):
        """
        Creates an internationalized file resource.

        :param dict data: A mapping from languages to `.File` objects.
        """
        self._data = data
        self.request = request
        self.defaultLanguage = defaultLanguage

    def chooseContext(self):
        """
        Choose the appropriate context (file) according to language.
        """
        langs = self.getAvailableLanguages()
        language = negotiator.getLanguage(langs, self.request)
        try:
            return self._data[language]
        except KeyError:
            return self._data[self.defaultLanguage]

    def getDefaultLanguage(self):
        'See II18nAware'
        return self.defaultLanguage

    def setDefaultLanguage(self, language):
        'See II18nAware'
        if language not in self._data:
            raise ValueError(
                'cannot set nonexistent language (%s) as default' % language)
        self.defaultLanguage = language

    def getAvailableLanguages(self):
        """
        The available languages are those defined in the *data*
        mapping given to this object.
        """
        return self._data.keys()

    # for unit tests
    def _testData(self, language):
        with open(self._data[language].path, 'rb') as f:
            return f.read()


@implementer(IResourceFactory)
@provider(IResourceFactoryFactory)
class I18nFileResourceFactory(object):


    def __init__(self, data, defaultLanguage):
        self.__data = data
        self.__defaultLanguage = defaultLanguage

    def __call__(self, request):
        return I18nFileResource(self.__data, request, self.__defaultLanguage)
