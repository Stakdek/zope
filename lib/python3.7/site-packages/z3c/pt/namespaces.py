##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
import zope.component
from zope.traversing.interfaces import IPathAdapter


class AdapterNamespaces(object):
    """Simulate tales function namespaces with adapter lookup.

    When we are asked for a namespace, we return an object that
    actually computes an adapter when called:

    To demonstrate this, we need to register an adapter:

      >>> def adapter1(ob):
      ...     return 1
      >>> zope.component.getGlobalSiteManager().registerAdapter(
      ...     adapter1, [zope.interface.Interface], IPathAdapter, 'a1')

    Now, with this adapter in place, we can try out the namespaces:

      >>> ob = object()
      >>> namespaces = AdapterNamespaces()
      >>> namespace = namespaces['a1']
      >>> namespace(ob)
      1
      >>> namespace = namespaces['a2']
      >>> namespace(ob)
      Traceback (most recent call last):
      ...
      KeyError: 'a2'
    """

    def __init__(self):
        self.namespaces = {}

    def __getitem__(self, name):
        namespace = self.namespaces.get(name)
        if namespace is None:

            def namespace(object):
                try:
                    return zope.component.getAdapter(
                        object, IPathAdapter, name
                    )
                except zope.component.ComponentLookupError:
                    raise KeyError(name)

            self.namespaces[name] = namespace
        return namespace

    def registerFunctionNamespace(self, namespacename, namespacecallable):
        """Register a function namespace

        namespace - a string containing the name of the namespace to
                    be registered

        namespacecallable - a callable object which takes the following
                            parameter:

                            context - the object on which the functions
                                      provided by this namespace will
                                      be called

                            This callable should return an object which
                            can be traversed to get the functions provided
                            by the this namespace.

        example:

           class stringFuncs(object):

              def __init__(self,context):
                 self.context = str(context)

              def upper(self):
                 return self.context.upper()

              def lower(self):
                 return self.context.lower()

            engine.registerFunctionNamespace('string',stringFuncs)
        """
        self.namespaces[namespacename] = namespacecallable

    def getFunctionNamespace(self, namespacename):
        """
        Returns the function namespace, if registered.

        Unlike ``__getitem__``, this method will immediately raise a
        KeyError if no such function is registered.
        """
        return self.namespaces[namespacename]


function_namespaces = AdapterNamespaces()

try:
    # If zope.pagetemplate is available, use the adapter
    # registered with the main zope.pagetemplate engine so that
    # we don't need to re-register them.
    from zope.pagetemplate.engine import Engine

    function_namespaces = Engine.namespaces
except (ImportError, AttributeError):  # pragma: no cover
    pass
