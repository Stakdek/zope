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
"""Publication Traverser
"""
__docformat__ = 'restructuredtext'

import six
from zope.component import queryMultiAdapter
from zope.publisher.interfaces import NotFound
from zope.security.checker import ProxyFactory
from zope.traversing.namespace import namespaceLookup
from zope.traversing.namespace import nsParse
from zope.traversing.interfaces import TraversalError
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserPublisher


class PublicationTraverser(object):
    """Traversal used for publication.

    The significant differences from
    `zope.traversing.adapters.traversePathElement` are:

    - Instead of adapting each traversed object to ITraversable,
      this version multi-adapts (ob, request) to
      `zope.publisher.interfaces.IPublishTraverse`.

    - This version wraps a security proxy around each traversed
      object.

    - This version raises `zope.publisher.interfaces.NotFound`
      rather than `zope.location.interfaces.LocationError`.

    - This version has a method, :meth:`traverseRelativeURL`, that
      supports "browserDefault" traversal.
    """
    def proxy(self, ob):
        return ProxyFactory(ob)

    def traverseName(self, request, ob, name):
        nm = name  # the name to look up the object with

        if name and name[:1] in '@+':
            # Process URI segment parameters.
            ns, nm = nsParse(name)
            if ns:
                try:
                    ob2 = namespaceLookup(ns, nm, ob, request)
                except TraversalError:
                    raise NotFound(ob, name)

                return self.proxy(ob2)

        if nm == '.':
            return ob

        if IPublishTraverse.providedBy(ob):
            ob2 = ob.publishTraverse(request, nm)
        else:
            # self is marker
            adapter = queryMultiAdapter((ob, request), IPublishTraverse,
                                        default=self)
            if adapter is not self:
                ob2 = adapter.publishTraverse(request, nm)
            else:
                raise NotFound(ob, name, request)

        return self.proxy(ob2)

    def traversePath(self, request, ob, path):

        if isinstance(path, six.string_types):
            path = path.split('/')
            if len(path) > 1 and not path[-1]:
                # Remove trailing slash
                path.pop()
        else:
            path = list(path)

        # Remove single dots
        path = [x for x in path if x != '.']

        path.reverse()

        # Remove double dots if possible
        while '..' in path:
            parent_index = path.index('..')
            if parent_index + 2 > len(path):
                break
            del path[parent_index:parent_index + 2]

        pop = path.pop

        while path:
            name = pop()
            ob = self.traverseName(request, ob, name)

        return ob

    def traverseRelativeURL(self, request, ob, path):
        """Path traversal that includes browserDefault paths"""
        ob = self.traversePath(request, ob, path)

        while True:
            adapter = IBrowserPublisher(ob, None)
            if adapter is None:
                return ob
            ob, path = adapter.browserDefault(request)
            ob = self.proxy(ob)
            if not path:
                return ob

            ob = self.traversePath(request, ob, path)


# alternate spelling
PublicationTraverse = PublicationTraverser


class PublicationTraverserWithoutProxy(PublicationTraverse):
    """
    A `PublicationTraverse` that does not add security proxies.
    """

    def proxy(self, ob):
        return ob
