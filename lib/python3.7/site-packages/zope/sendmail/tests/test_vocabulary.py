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
"""Mail delivery names vocabulary test
"""

import doctest
import unittest

from zope.component.testing import PlacelessSetup


class MailDeliveryNamesTests(PlacelessSetup, unittest.TestCase):

    _marker = object()

    def _register(self, *names):
        from zope.component import provideUtility
        from zope.interface import implementer
        from zope.sendmail.interfaces import IMailDelivery
        from zope.sendmail.vocabulary import MailDeliveryNames

        @implementer(IMailDelivery)
        class StubMailDelivery(object):
            pass

        for name in names:
            provideUtility(StubMailDelivery(), name=name)

        provideUtility(MailDeliveryNames, name='Mail Delivery Names')

    def _callFUT(self):
        from zope.sendmail.vocabulary import MailDeliveryNames
        return MailDeliveryNames()

    def test_default(self):
        NAMES = 'and now for something completely different'.split()
        self._register(*NAMES)
        vocab = self._callFUT()
        names = sorted([term.value for term in vocab])
        self.assertEqual(names, sorted(NAMES))


def test_suite():
    return unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocTestSuite('zope.sendmail.vocabulary'),
    ])
