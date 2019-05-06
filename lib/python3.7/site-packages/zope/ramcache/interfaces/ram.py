##############################################################################
#
# Copyright (c) 2002-2009 Zope Foundation and Contributors.
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
"""RAM cache interface.
"""
__docformat__ = 'restructuredtext'

from zope.interface import Attribute

from zope.ramcache.interfaces import ICache


class IRAMCache(ICache):
    """Interface for the RAM Cache."""

    maxEntries = Attribute("""A maximum number of cached values.""")

    maxAge = Attribute("""Maximum age for cached values in seconds.""")

    cleanupInterval = Attribute("""An interval between cache cleanups
    in seconds.""")

    def getStatistics():
        """Reports on the contents of a cache.

        The returned value is a sequence of dictionaries with the
        following (string) keys:

          - ``path``: The object being cached.
          - ``hits``: How many times this path (for all its keys)
            has been looked up.
          - ``misses``: How many misses there have been for this path
            and all its keys.
          - ``size``: An integer approximating the RAM usage for this path
            (only available if all values can be pickled; otherwise ``False``)
          - ``entries``: How many total keys there are for this path.
        """

    def update(maxEntries, maxAge, cleanupInterval):
        """Saves the parameters available to the user"""
