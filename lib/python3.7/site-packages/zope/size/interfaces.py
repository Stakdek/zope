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
"""Interfaces that give the size of an object.
"""

from zope.interface import Interface


class ISized(Interface):
    """
    An object that is sized in some unit.

    Basic units:

    - 'byte'

    - 'item'  for example, number of subobjects for a folder

    - None    for unsized things

    - 'line'  for source-code like things

    """

    def sizeForSorting():
        """Returns a tuple (basic_unit, amount)

        Used for sorting among different kinds of sized objects.
        'amount' need only be sortable among things that share the
        same basic unit."""

    def sizeForDisplay():
        """Returns a string giving the size. The output string may be a
        zope.i18nmessageid.message.Message with an embedded mapping, so
        it should be translated with zope.i18n.translate()
        """
