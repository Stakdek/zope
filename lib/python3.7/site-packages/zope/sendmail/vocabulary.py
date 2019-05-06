##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Mail vocabularies
"""
__docformat__ = 'restructuredtext'

import zope.component
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.sendmail.interfaces import IMailDelivery


def MailDeliveryNames(context=None):
    """Vocabulary with names of mail delivery utilities

    Let's provide a few stub utilities:

      >>> from zope.interface import implementer
      >>> @implementer(IMailDelivery)
      ... class StubMailDelivery(object):
      ...     pass

      >>> from zope.component import provideUtility
      >>> for name in 'and now for something completely different'.split():
      ...     provideUtility(StubMailDelivery(), name=name)

    Let's also provide another utility to verify that we only see mail
    delivery utilities:

      >>> provideUtility(MailDeliveryNames, name='Mail Delivery Names')

    Let's see what's in the vocabulary:

      >>> vocabulary = MailDeliveryNames(None)
      >>> names = [term.value for term in vocabulary]
      >>> names.sort()
      >>> print(' '.join(names))
      and completely different for now something
    """
    utils = zope.component.getUtilitiesFor(IMailDelivery, context)
    terms = [SimpleTerm(name) for name, util in utils]
    return SimpleVocabulary(terms)


directlyProvides(MailDeliveryNames, IVocabularyFactory)
