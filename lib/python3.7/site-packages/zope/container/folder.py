##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""The standard Zope Folder.
"""
__docformat__ = 'restructuredtext'
from zope.interface import implementer
from zope.container import btree, interfaces

@implementer(interfaces.IContentContainer)
class Folder(btree.BTreeContainer):
    """The standard Zope Folder implementation."""

    # BBB: The data attribute used to be exposed.
    # For compatibility with existing pickles, we read and write that name
    @property
    def data(self):
        return self._SampleContainer__data

    @data.setter
    def data(self, value):
        self._SampleContainer__data = value

    def __getstate__(self):
        state = super(Folder, self).__getstate__()
        data = state.pop('_SampleContainer__data')
        state['data'] = data
        return state

    def __setstate__(self, state):
        if 'data' in state and '_SampleContainer__data' not in state:
            state['_SampleContainer__data'] = state.pop('data')
        super(Folder, self).__setstate__(state)
