##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Fallback collator
"""

from unicodedata import normalize

class FallbackCollator:

    def __init__(self, locale):
        pass

    def key(self, s):
        s = normalize('NFKC', s)
        return s.lower(), s

    def cmp(self, s1, s2):
        k1, k2 = self.key(s1), self.key(s2)
        if k1 == k2:
            return 0
        return -1 if k1 < k2 else 1
