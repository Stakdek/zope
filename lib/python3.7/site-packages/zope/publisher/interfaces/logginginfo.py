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
"""An interface for LoggingInfo.
"""

__docformat__ = "reStructuredText"

from zope.interface import Interface


class ILoggingInfo(Interface):
    """Provides information about the object to be included in the logs.

    In the class we need an __init__ method that accepts an object.
    """

    def getLogMessage():
        """Returns a log string made from the object it was adapted from.
        """
