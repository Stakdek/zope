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
"""External Method Product

This product provides support for external methods, which allow
domain-specific customization of web environments.
"""

import os
import stat
import sys

from AccessControl.class_init import InitializeClass
from AccessControl.Permissions import change_external_methods  # NOQA
from AccessControl.Permissions import view
from AccessControl.Permissions import view_management_screens
from AccessControl.SecurityInfo import ClassSecurityInfo
from Acquisition import Acquired
from Acquisition import Explicit
from App.config import getConfiguration
from App.Extensions import FuncCode
from App.Extensions import getObject
from App.Extensions import getPath
from App.Management import Navigation
from App.special_dtml import DTMLFile
from ComputedAttribute import ComputedAttribute
from OFS.role import RoleManager
from OFS.SimpleItem import Item
from Persistence import Persistent


manage_addExternalMethodForm = DTMLFile('dtml/methodAdd', globals())


def manage_addExternalMethod(self, id, title, module, function, REQUEST=None):
    """Add an external method to a folder

    In addition to the standard object-creation arguments,
    'id' and title, the following arguments are defined:

        function -- The name of the python function. This can be a
          an ordinary Python function, or a bound method.

        module -- The name of the file containing the function
          definition.

        The module normally resides in the 'Extensions' directory.

        If the zope.conf directive 'extensions' was overriden, then
        it will specify where modules should reside.

        However, the file name may have a prefix of
        'product.', indicating that it should be found in a product
        directory.

        For example, if the module is: 'ACMEWidgets.foo', then an
        attempt will first be made to use the file
        'lib/python/Products/ACMEWidgets/Extensions/foo.py'. If this
        failes, then the file 'Extensions/ACMEWidgets.foo.py' will be
        used.
    """
    id = str(id)
    title = str(title)
    module = str(module)
    function = str(function)

    i = ExternalMethod(id, title, module, function)
    self._setObject(id, i)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


class ExternalMethod(Item, Persistent, Explicit,
                     RoleManager, Navigation):
    """Web-callable functions that encapsulate external python functions.

    The function is defined in an external file.  This file is treated
    like a module, but is not a module.  It is not imported directly,
    but is rather read and evaluated.  The file must reside in the
    'Extensions' subdirectory of the Zope installation, or in the directory
     specified by the 'extensions' directive in zope.conf, or in an
    'Extensions' subdirectory of a product directory.

    Due to the way ExternalMethods are loaded, it is not *currently*
    possible to use Python modules that reside in the 'Extensions'
    directory.  It is possible to load modules found in the
    'lib/python' directory of the Zope installation, or in
    packages that are in the 'lib/python' directory.

    """

    meta_type = 'External Method'
    zmi_icon = 'fa fa-external-link-square-alt'

    security = ClassSecurityInfo()
    security.declareObjectProtected(view)

    __defaults__ = ComputedAttribute(lambda self: self.getFuncDefaults())

    __code__ = ComputedAttribute(lambda self: self.getFuncCode())

    ZopeTime = Acquired
    manage_page_header = Acquired

    manage_options = ((
        {'label': 'Properties', 'action': 'manage_main'},
        {'label': 'Test', 'action': ''},
    ) + Item.manage_options + RoleManager.manage_options)

    def __init__(self, id, title, module, function):
        self.id = id
        self.manage_edit(title, module, function)

    security.declareProtected(view_management_screens,  # NOQA: flake8: D001
                              'manage_main')
    manage_main = DTMLFile('dtml/methodEdit', globals())

    @security.protected(change_external_methods)
    def manage_edit(self, title, module, function, REQUEST=None):
        """Change the external method

        See the description of manage_addExternalMethod for a
        description of the arguments 'module' and 'function'.

        Note that calling 'manage_edit' causes the "module" to be
        effectively reloaded.  This is useful during debugging to see
        the effects of changes, but can lead to problems of functions
        rely on shared global data.
        """
        title = str(title)
        module = str(module)
        function = str(function)

        self.title = title
        if module[-3:] == '.py':
            module = module[:-3]
        elif module[-4:] == '.pyc':
            module = module[:-4]
        self._module = module
        self._function = function
        self.getFunction(True)
        if REQUEST:
            message = 'External Method Uploaded.'
            return self.manage_main(self, REQUEST, manage_tabs_message=message)

    def getFunction(self, reload=False):
        f = getObject(self._module, self._function, reload)
        if hasattr(f, '__func__'):
            ff = f.__func__
        else:
            ff = f

        self._v_func_defaults = ff.__defaults__
        self._v_func_code = FuncCode(ff, f is not ff)
        self._v_f = f

        return f

    def reloadIfChanged(self):
        # If the file has been modified since last loaded, force a reload.
        ts = os.stat(self.filepath())[stat.ST_MTIME]
        if (not hasattr(self, '_v_last_read') or (ts != self._v_last_read)):
            self._v_f = self.getFunction(True)
            self._v_last_read = ts

    def getFuncDefaults(self):
        if getConfiguration().debug_mode:
            self.reloadIfChanged()
        if not hasattr(self, '_v_func_defaults'):
            self._v_f = self.getFunction()
        return self._v_func_defaults

    def getFuncCode(self):
        if getConfiguration().debug_mode:
            self.reloadIfChanged()
        if not hasattr(self, '_v_func_code'):
            self._v_f = self.getFunction()
        return self._v_func_code

    @security.protected(view)
    def __call__(self, *args, **kw):
        """Call an ExternalMethod

        Calling an External Method is roughly equivalent to calling
        the original actual function from Python.  Positional and
        keyword parameters can be passed as usual.  Note however that
        unlike the case of a normal Python method, the "self" argument
        must be passed explicitly.  An exception to this rule is made
        if:

        - The supplied number of arguments is one less than the
          required number of arguments, and

        - The name of the function\'s first argument is 'self'.

        In this case, the URL parent of the object is supplied as the
        first argument.
        """
        filePath = self.filepath()
        if filePath is None:
            raise RuntimeError('external method could not be called '
                               'because it is None')

        if not os.path.exists(filePath):
            raise RuntimeError('external method could not be called '
                               'because the file does not exist')

        if getConfiguration().debug_mode:
            self.reloadIfChanged()

        if hasattr(self, '_v_f'):
            f = self._v_f
        else:
            f = self.getFunction()

        __traceback_info__ = args, kw, self._v_func_defaults

        try:
            return f(*args, **kw)
        except TypeError as v:
            tb = sys.exc_info()[2]
            try:
                if ((self._v_func_code.co_argcount -
                     len(self._v_func_defaults or ()) - 1 == len(args)) and
                        self._v_func_code.co_varnames[0] == 'self'):
                    return f(self.aq_parent.this(), *args, **kw)

                raise TypeError(v)
            finally:
                tb = None  # NOQA

    def function(self):
        return self._function

    def module(self):
        return self._module

    def filepath(self):
        if not hasattr(self, '_v_filepath'):
            self._v_filepath = getPath('Extensions', self._module,
                                       suffixes=('', 'py', 'pyc', 'pyp'))
        return self._v_filepath


InitializeClass(ExternalMethod)
