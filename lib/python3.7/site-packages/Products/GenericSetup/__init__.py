##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" GenericSetup product initialization.
"""

from AccessControl.SecurityInfo import ModuleSecurityInfo

from Products.GenericSetup.interfaces import BASE
from Products.GenericSetup.interfaces import EXTENSION
from Products.GenericSetup.permissions import ManagePortal
from Products.GenericSetup.registry import _profile_registry \
    as profile_registry

# This is for easier imports by add-ons.
BASE, EXTENSION, profile_registry  # pyflakes

security = ModuleSecurityInfo('Products.GenericSetup')
security.declareProtected(ManagePortal, 'profile_registry')


def initialize(context):

    from . import tool

    context.registerClass(tool.SetupTool,
                          constructors=(tool.addSetupTool,),
                          permissions=(ManagePortal,),
                          interfaces=None,
                          icon='www/tool.png')
