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
"""Adapters that give the size of an object.
"""
from zope.interface import implementer
from zope.size.interfaces import ISized
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zope')

@implementer(ISized)
class DefaultSized(object):
    """
    A default :class:`zope.size.interfaces.ISized` adapter
    producing bytes for any object that has a ``getSize`` method and
    (None, None) for all other objects.
    """

    def __init__(self, obj):
        try:
            size = int(obj.getSize())
        except (AttributeError, ValueError, TypeError):
            self._sortingSize = None, None
        else:
            self._sortingSize = 'byte', size

    def sizeForSorting(self):
        """See ISized"""
        return self._sortingSize

    def sizeForDisplay(self):
        """See ISized"""
        units, size = self._sortingSize
        if units == 'byte':
            return byteDisplay(size)
        return _('not-available', 'n/a')

def byteDisplay(size):
    """
    Returns a size with the correct unit (KB, MB), given the size in bytes.
    The output should be given to zope.i18n.translate()
    """
    if size == 0:
        return _('0 KB')
    if size <= 1024:
        return _('1 KB')
    if size > 1048576:
        return _('${size} MB', mapping={'size': '%0.02f' % (size / 1048576.0)})
    return _('${size} KB', mapping={'size': '%d' % (size / 1024.0)})
