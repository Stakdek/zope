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
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Products.BTreeFolder2 import BTreeFolder2


def initialize(context):
    context.registerClass(
        BTreeFolder2.BTreeFolder2,
        constructors=(BTreeFolder2.manage_addBTreeFolderForm,
                      BTreeFolder2.manage_addBTreeFolder),
        icon='btreefolder2.gif',
    )
