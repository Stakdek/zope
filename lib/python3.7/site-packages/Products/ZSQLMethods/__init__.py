##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""SQL Method Product.
"""

from AccessControl.Permissions import open_close_database_connection

import Shared.DC.ZRDB.Search
import Shared.DC.ZRDB.Aqueduct
import Shared.DC.ZRDB.RDB
import Shared.DC.ZRDB.sqlvar
import Shared.DC.ZRDB.sqlgroup
import Shared.DC.ZRDB.sqltest

from Products.ZSQLMethods import SQL


def initialize(context):

    context.registerClass(
        SQL.SQL,
        permission='Add Database Methods',
        constructors=(SQL.manage_addZSQLMethodForm, SQL.manage_addZSQLMethod),
        icon='sqlmethod.gif',
        permissions=(open_close_database_connection, ),
        legacy=(SQL.SQLConnectionIDs, ))

    context.registerClass(
        meta_type='Z Search Interface',
        permission='Add Documents, Images, and Files',
        constructors=(Shared.DC.ZRDB.Search.addForm,
                      Shared.DC.ZRDB.Search.manage_addZSearch),
        legacy=(Shared.DC.ZRDB.Search.ZQueryIds, ))

    context.registerHelp()
    context.registerHelpTitle('Zope Help')


__module_aliases__ = (
    ('Products.AqueductSQLMethods', 'Products.ZSQLMethods'),
    ('Aqueduct', Shared.DC.ZRDB),
    ('AqueductDA', Shared.DC.ZRDB),
    ('Products.AqueductSQLMethods.SQL', SQL),
    ('Aqueduct.Aqueduct', Shared.DC.ZRDB.Aqueduct),
    ('AqueductDA.DA', Shared.DC.ZRDB.DA),
    ('Aqueduct.RDB', Shared.DC.ZRDB.RDB),
    ('AqueductDA.sqlvar', Shared.DC.ZRDB.sqlvar),
    ('AqueductDA.sqltest', Shared.DC.ZRDB.sqltest),
    ('AqueductDA.sqlgroup', Shared.DC.ZRDB.sqlgroup),
)
