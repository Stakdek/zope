##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from AccessControl.Permissions import change_database_methods
from AccessControl.SecurityInfo import ClassSecurityInfo
from App.special_dtml import DTMLFile
from Acquisition import aq_inner
from Acquisition import aq_parent
from Shared.DC.ZRDB.DA import DA

# BBB Zope 2.12
try:
    from AccessControl.class_init import InitializeClass
except ImportError:
    from App.class_init import InitializeClass


def SQLConnectionIDs(container):
    """Find SQL database connections in the current folder and above

    This function returns a list of two-element tuples. The second element
    is the connection ID, the first element either its title, or if the
    title is empty, its ID.
    """
    ids = {}

    while container is not None:
        if getattr(container, 'objectValues', None) is not None:
            for ob in container.objectValues():
                if (getattr(ob, '_isAnSQLConnection', None) and
                        getattr(ob, 'id', None)):
                    ob_id = ob.id

                    if callable(ob_id):
                        ob_id = ob_id()

                    if ob_id not in ids:
                        if hasattr(ob, 'title_and_id'):
                            title = ob.title_and_id()
                        else:
                            title = ob_id
                        ids[ob_id] = title

        container = aq_parent(aq_inner(container))

    ids = [(item[1], item[0]) for item in ids.items()]
    ids.sort()

    return ids


manage_addZSQLMethodForm = DTMLFile('dtml/add', globals())


def manage_addZSQLMethod(self, id, title,
                         connection_id, arguments, template,
                         REQUEST=None, submit=None):
    """Add an SQL Method

    The 'connection_id' argument is the id of a database connection
    that resides in the current folder or in a folder above the
    current folder.  The database should understand SQL.

    The 'arguments' argument is a string containing an arguments
    specification, as would be given in the SQL method cration form.

    The 'template' argument is a string containing the source for the
    SQL Template.
    """

    # Note - type checking is handled by _setObject and constructor.
    self._setObject(id, SQL(id, title, connection_id, arguments, template))
    if REQUEST is not None:
        try:
            u = self.DestinationURL()
        except Exception:
            u = REQUEST['URL1']
        if submit == " Add and Edit ":
            u = "%s/%s/manage_main" % (u, id)
        elif submit == " Add and Test ":
            u = "%s/%s/manage_testForm" % (u, id)
        else:
            u = u + '/manage_main'

        REQUEST.RESPONSE.redirect(u)
    return ''


class SQL(DA):
    """SQL Database methods

    SQL Database methods are used to access external SQL databases.

    They support three important abstractions:

      - Method

        SQL Methods behave like methods of the folders they are
        accessed in.  In particular, they can be used from other
        methods, like Documents, ExternalMethods, and even other SQL
        Methods.

      - Searchability

        Database methods support the Searchable Object Interface.
        Search interface wizards can be used to build user
        interfaces to them.  They can be used in joins and
        unions. They provide meta-data about their input parameters
        and result data.

        For more information, see the searchable-object interface
        specification.

      - Containment

        Database methods support URL traversal to access and invoke
        methods on individual record objects. For example, suppose you
        had an 'employees' database method that took a single argument
        'employee_id'.  Suppose that employees had a 'service_record'
        method (defined in a record class or acquired from a
        folder). The 'service_record' method could be accessed with a
        URL like::

           employees/employee_id/1234/service_record

    """
    meta_type = 'Z SQL Method'
    zmi_icon = 'far fa-puzzle-piece'

    security = ClassSecurityInfo()

    security.declareProtected(change_database_methods, 'manage')
    security.declareProtected(change_database_methods, 'manage_main')
    manage = manage_main = DTMLFile('dtml/edit', globals())
    manage_main._setName('manage_main')


InitializeClass(SQL)
