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

from . import SiteErrorLog

def commit(note):
    import transaction
    transaction.get().note(note)
    transaction.commit()

def install_errorlog(app):
    if hasattr(app, 'error_log'):
        return

    error_log = SiteErrorLog.SiteErrorLog()
    app._setObject('error_log', error_log)
    commit(u'Added site error_log at /error_log')


def initialize(context):
    context.registerClass(SiteErrorLog.SiteErrorLog,
                          constructors=(SiteErrorLog.manage_addErrorLog,),
                          permission=SiteErrorLog.use_error_logging)

    app = context.getApplication() # new API added in Zope 4.0b5
    if app is not None:
        install_errorlog(app)
