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
"""
URL Namespace Implementations

URL namespaces are an extensible mechanism to provide additional
control over traversal (for example, disambiguating :class:`item
<item>` versus :class:`attribute <attr>` access) or access to an
additional set of traversable names (such as :class:`registered views
<view>` or :class:`path adapters <adapter>`).  This mechanism is used
for path segments that look like ``++ns++name``.  (It is also used for
segments like ``@@name``, which is a shortcut for ``++view++name``.
See :func:`nsParse` for details.)

``ns`` is the name of the namespace (a named, registered adapter that
implements `ITraversable`) and ``name`` is the name to traverse to in
that namespace.

The function :func:`namespaceLookup` handles this process.

If you configure this package by loading its ``configure.zcml`` using
:mod:`zope.configuration.xmlconfig`, several namespaces are
registered.  They are registered both as single adapters for any
object, and as multi-adapters (views) for any object together with a
`zope.publisher.interfaces.IRequest`.  Those namespaces are:

etc
    Implemented in `etc`
attribute
    Implemented in `attr`
adapter
    Implemented in `adapter`
item
    Implemented in `item`
acquire
    Implemented in `acquire`
view
    Implemented in `view`
resource
    Implemented in `resource`
lang
    Implemented in `lang`
skin
    Implemented in `skin`
vh
    Implemented in `vh`
debug
    Implemented in `debug` (only if the ZCML feature ``devmode`` is enabled)
    and only registered as a multi-adapter.
"""
__docformat__ = 'restructuredtext'

import re

import six
import zope.component
import zope.interface
from zope.i18n.interfaces import IModifiableUserPreferredLanguages
from zope.interface.interfaces import ComponentLookupError
from zope.interface import providedBy, directlyProvides
from zope.location.interfaces import LocationError
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.skinnable import applySkin
from zope.security.proxy import removeSecurityProxy
from zope.traversing.interfaces import IEtcNamespace
from zope.traversing.interfaces import IPathAdapter
from zope.traversing.interfaces import ITraversable


class UnexpectedParameters(LocationError):
    "Unexpected namespace parameters were provided."


class ExcessiveDepth(LocationError):
    "Too many levels of containment. We don't believe them."


def namespaceLookup(ns, name, object, request=None):
    """
    Lookup a value from a namespace.

    We look up a value by getting an adapter from the *object* to
    :class:`~zope.traversing.interfaces.ITraversable` named *ns*.  If
    the *request* is passed, we get a multi-adapter on the *object*
    and *request* (sometimes this is called a "view").

    Let's start with adapter-based traversal::

        >>> class I(zope.interface.Interface):
        ...     'Test interface'
        >>> @zope.interface.implementer(I)
        ... class C(object):
        ...     pass

    We'll register a simple testing adapter::

        >>> class Adapter(object):
        ...     def __init__(self, context):
        ...         self.context = context
        ...     def traverse(self, name, remaining):
        ...         return name+'42'

        >>> zope.component.provideAdapter(Adapter, (I,), ITraversable, 'foo')

    Then given an object, we can traverse it with a
    namespace-qualified name::

        >>> namespaceLookup('foo', 'bar', C())
        'bar42'

    If we give an invalid namespace, we'll get a not found error::

        >>> namespaceLookup('fiz', 'bar', C())    # doctest: +ELLIPSIS
        Traceback (most recent call last):
          ...
        LocationError: (<zope.traversing.namespace.C object at 0x...>, '++fiz++bar')

    We'll get the same thing if we provide a request::

        >>> from zope.publisher.browser import TestRequest
        >>> request = TestRequest()
        >>> namespaceLookup('foo', 'bar', C(), request)    # doctest: +ELLIPSIS
        Traceback (most recent call last):
          ...
        LocationError: (<zope.traversing.namespace.C object at 0x...>, '++foo++bar')

    We need to provide a view::

        >>> class View(object):
        ...     def __init__(self, context, request):
        ...         pass
        ...     def traverse(self, name, remaining):
        ...         return name+'fromview'
        >>> from zope.traversing.testing import browserView
        >>> browserView(I, 'foo', View, providing=ITraversable)

        >>> namespaceLookup('foo', 'bar', C(), request)
        'barfromview'

    Clean up::

        >>> from zope.testing.cleanup import cleanUp
        >>> cleanUp()
    """
    if request is not None:
        traverser = zope.component.queryMultiAdapter((object, request),
                                                     ITraversable, ns)
    else:
        traverser = zope.component.queryAdapter(object, ITraversable, ns)

    if traverser is None:
        raise LocationError(object, "++%s++%s" % (ns, name))

    return traverser.traverse(name, ())


namespace_pattern = re.compile('[+][+]([a-zA-Z0-9_]+)[+][+]')


def nsParse(name):
    """
    Parse a namespace-qualified name into a namespace name and a name.
    Returns the namespace name and a name.

    A namespace-qualified name is usually of the form ++ns++name, as
    in::

        >>> nsParse('++acquire++foo')
        ('acquire', 'foo')

    The part inside the +s must be an identifier, so::

        >>> nsParse('++hello world++foo')
        ('', '++hello world++foo')
        >>> nsParse('+++acquire+++foo')
        ('', '+++acquire+++foo')

    But it may also be a @@foo, which implies the view namespace::

        >>> nsParse('@@foo')
        ('view', 'foo')

        >>> nsParse('@@@foo')
        ('view', '@foo')

        >>> nsParse('@foo')
        ('', '@foo')
    """
    ns = ''
    if name.startswith('@@'):
        ns = 'view'
        name = name[2:]
    else:
        match = namespace_pattern.match(name)
        if match:
            prefix, ns = match.group(0, 1)
            name = name[len(prefix):]

    return ns, name


def getResource(context, name, request):
    resource = queryResource(context, name, request)
    if resource is None:
        raise LocationError(context, name)
    return resource


def queryResource(context, name, request, default=None):
    resource = zope.component.queryAdapter(request, name=name)
    if resource is None:
        return default

    # We need to set the __parent__ and __name__.  We need the unproxied
    # resource to do this.  We still return the proxied resource.
    r = removeSecurityProxy(resource)

    r.__parent__ = context
    r.__name__ = name

    return resource


# ---- namespace processors below ----

@zope.interface.implementer(ITraversable)
class SimpleHandler(object):

    def __init__(self, context, request=None):
        """
        It ignores its second constructor arg and stores the first
        one in its ``context`` attr.
        """
        self.context = context


class acquire(SimpleHandler):
    """
    Traversal adapter for the ``acquire`` namespace.

    This namespace tries to traverse to the given *name*
    starting with the context object. If it cannot be found,
    it proceeds to look at each ``__parent__`` all the way
    up the tree until it is found.
    """

    def traverse(self, name, remaining):
        """
        Acquire a name

        Let's set up some example data::

          >>> @zope.interface.implementer(ITraversable)
          ... class testcontent(object):
          ...     def traverse(self, name, remaining):
          ...         v = getattr(self, name, None)
          ...         if v is None:
          ...             raise LocationError(self, name)
          ...         return v
          ...     def __repr__(self):
          ...         return 'splat'

          >>> ob = testcontent()
          >>> ob.a = 1
          >>> ob.__parent__ = testcontent()
          >>> ob.__parent__.b = 2
          >>> ob.__parent__.__parent__ = testcontent()
          >>> ob.__parent__.__parent__.c = 3

        And acquire some names:

          >>> adapter = acquire(ob)

          >>> adapter.traverse('a', ())
          1

          >>> adapter.traverse('b', ())
          2

          >>> adapter.traverse('c', ())
          3

          >>> adapter.traverse('d', ())
          Traceback (most recent call last):
          ...
          LocationError: (splat, 'd')
        """
        i = 0
        ob = self.context
        while i < 200:
            i += 1
            traversable = ITraversable(ob, None)
            if traversable is not None:
                try:
                    # ??? what do we do if the path gets bigger?
                    path = []
                    next = traversable.traverse(name, path)
                    if path:
                        continue
                except LocationError:
                    pass

                else:
                    return next

            ob = getattr(ob, '__parent__', None)
            if ob is None:
                raise LocationError(self.context, name)

        raise ExcessiveDepth(self.context, name)


class attr(SimpleHandler):
    """
    Traversal adapter for the ``attribute`` namespace.

    This namespace simply looks for an attribute of the given
    *name*.
    """

    def traverse(self, name, ignored):
        """Attribute traversal adapter

        This adapter just provides traversal to attributes:

          >>> ob = {'x': 1}
          >>> adapter = attr(ob)
          >>> list(adapter.traverse('keys', ())())
          ['x']

        """
        return getattr(self.context, name)


class item(SimpleHandler):
    """
    Traversal adapter for the ``item`` namespace.

    This namespace simply uses ``__getitem__`` to find a
    value of the given *name*.
    """

    def traverse(self, name, ignored):
        """Item traversal adapter

           This adapter just provides traversal to items:

              >>> ob = {'x': 42}
              >>> adapter = item(ob)
              >>> adapter.traverse('x', ())
              42
           """
        return self.context[name]


class etc(SimpleHandler):
    """
    Traversal adapter for the ``etc`` namespace.

    This namespace provides for a layer of indirection.  The given
    **name** is used to find a utility of that name that implements
    `zope.traversing.interfaces.IEtcNamespace`.

    As a special case, if there is no such utility, and the name is
    "site", then we will attempt to call a method named ``getSiteManager``
    on the *context* object.
    """

    def traverse(self, name, ignored):
        utility = zope.component.queryUtility(IEtcNamespace, name)
        if utility is not None:
            return utility

        ob = self.context

        if name not in ('site',):
            raise LocationError(ob, name)

        method_name = "getSiteManager"
        method = getattr(ob, method_name, None)
        if method is None:
            raise LocationError(ob, name)

        try:
            return method()
        except ComponentLookupError:
            raise LocationError(ob, name)


@zope.interface.implementer(ITraversable)
class view(object):
    """
    Traversal adapter for the ``view`` (``@@``) namespace.

    This looks for the default multi-adapter from the *context* and
    *request* of the given *name*.

    :raises zope.location.interfaces.LocationError: If no such
      adapter can be found.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        view = zope.component.queryMultiAdapter((self.context, self.request),
                                                name=name)
        if view is None:
            raise LocationError(self.context, name)

        return view


class resource(view):
    """
    Traversal adapter for the ``resource`` namespace.

    Resources are default adapters of the given *name* for the
    *request* (**not** the *context*).  The returned object will have
    its ``__parent__`` set to the *context* and its ``__name__`` will
    match the *name* we traversed.
    """

    def traverse(self, name, ignored):
        # The context is important here, since it becomes the parent of the
        # resource, which is needed to generate the absolute URL.
        return getResource(self.context, name, self.request)


class lang(view):
    """
    Traversal adapter for the ``lang`` namespace.

    Traversing to *name* means to adapt the request to
    :class:`zope.i18n.interfaces.IModifiableUserPreferredLanguages`
    and set the *name* as the only preferred language.

    This needs the *request* to support
    :class:`zope.publisher.interfaces.http.IVirtualHostRequest` because
    it shifts the language name to the application.
    """

    def traverse(self, name, ignored):
        self.request.shiftNameToApplication()
        languages = IModifiableUserPreferredLanguages(self.request)
        languages.setPreferredLanguages([name])
        return self.context


class skin(view):
    """
    Traversal adapter for the ``skin`` namespace.

    Traversing to *name* looks for the
    :class:`zope.publisher.interfaces.browser.IBrowserSkinType`
    utility having the given name, and then applies it to the
    *request* with :func:`.applySkin`.

    This needs the *request* to support
    :class:`zope.publisher.interfaces.http.IVirtualHostRequest`
    because it shifts the skin name to the application.
    """

    def traverse(self, name, ignored):
        self.request.shiftNameToApplication()
        try:
            skin = zope.component.getUtility(IBrowserSkinType, name)
        except ComponentLookupError:
            raise LocationError("++skin++%s" % name)
        applySkin(self.request, skin)
        return self.context


class vh(view):
    """
    Traversal adapter for the ``vh`` namespace.

    Traversing to *name*, which must be of the form
    ``protocol:host:port`` causes a call to
    :meth:`zope.publisher.interfaces.http.IVirtualHostRequest.setApplicationServer`.
    Segments in the request's traversal stack up to a prior ``++`` are
    collected and become the application names given to
    :meth:`zope.publisher.interfaces.http.IVirtualHostRequest.setVirtualHostRoot`.
    """

    def traverse(self, name, ignored):

        request = self.request

        if not six.PY3:
            # `name` comes in as unicode, we need to make it a string
            # so absolute URLs don't all become unicode.
            name = name.encode('utf-8')

        if name:
            try:
                proto, host, port = name.split(":")
            except ValueError:
                raise ValueError("Vhost directive should have the form "
                                 "++vh++protocol:host:port")

            request.setApplicationServer(host, proto, port)

        traversal_stack = request.getTraversalStack()
        app_names = []

        if '++' in traversal_stack:
            segment = traversal_stack.pop()
            while segment != '++':
                app_names.append(segment)
                segment = traversal_stack.pop()
            request.setTraversalStack(traversal_stack)
        else:
            raise ValueError(
                "Must have a path element '++' after a virtual host "
                "directive.")

        request.setVirtualHostRoot(app_names)

        return self.context


class adapter(SimpleHandler):
    """
    Traversal adapter for the ``adapter`` namespace.

    This adapter provides traversal to named adapters for the
    *context* registered to provide
    `zope.traversing.interfaces.IPathAdapter`.
    """""


    def traverse(self, name, ignored):
        """
        To demonstrate this, we need to register some adapters:

          >>> def adapter1(ob):
          ...     return 1
          >>> def adapter2(ob):
          ...     return 2
          >>> zope.component.provideAdapter(
          ...     adapter1, (None,), IPathAdapter, 'a1')
          >>> zope.component.provideAdapter(
          ...     adapter2, (None,), IPathAdapter, 'a2')

        Now, with these adapters in place, we can use the traversal adapter:

          >>> ob = object()
          >>> adapter = adapter(ob)
          >>> adapter.traverse('a1', ())
          1
          >>> adapter.traverse('a2', ())
          2
          >>> try:
          ...     adapter.traverse('bob', ())
          ... except LocationError:
          ...     print('no adapter')
          no adapter

        Clean up:

          >>> from zope.testing.cleanup import cleanUp
          >>> cleanUp()
        """
        try:
            return zope.component.getAdapter(self.context, IPathAdapter, name)
        except ComponentLookupError:
            raise LocationError(self.context, name)


class debug(view):
    """
    Traversal adapter for the ``debug`` namespace.

    This adapter allows debugging flags to be set in the request.

    .. seealso:: :class:`zope.publisher.interfaces.IDebugFlags`
    """

    enable_debug = __debug__

    def traverse(self, name, ignored):
        """
        Setup for demonstration:

            >>> from zope.publisher.browser import TestRequest
            >>> request = TestRequest()
            >>> ob = object()
            >>> adapter = debug(ob, request)

        in debug mode, ``++debug++source`` enables source annotations

            >>> request.debug.sourceAnnotations
            False
            >>> adapter.traverse('source', ()) is ob
            True
            >>> request.debug.sourceAnnotations
            True

        ``++debug++tal`` enables TAL markup in output

            >>> request.debug.showTAL
            False
            >>> adapter.traverse('tal', ()) is ob
            True
            >>> request.debug.showTAL
            True

        ``++debug++errors`` enables tracebacks (by switching to debug skin)

            >>> from zope.publisher.interfaces.browser import IBrowserRequest

            >>> class Debug(IBrowserRequest):
            ...     pass
            >>> directlyProvides(Debug, IBrowserSkinType)
            >>> zope.component.provideUtility(
            ...     Debug, IBrowserSkinType, name='Debug')

            >>> Debug.providedBy(request)
            False
            >>> adapter.traverse('errors', ()) is ob
            True
            >>> Debug.providedBy(request)
            True

        You can specify several flags separated by commas

            >>> adapter.traverse('source,tal', ()) is ob
            True

        Unknown flag names cause exceptions

            >>> try:
            ...     adapter.traverse('badflag', ())
            ... except ValueError:
            ...     print('unknown debugging flag')
            unknown debugging flag

        Of course, if Python was started with the ``-O`` flag to
        disable debugging, none of this is allowed (we simulate this
        with a private setting on the instance):

            >>> adapter.enable_debug = False
            >>> adapter.traverse('source', ())
            Traceback (most recent call last):
            ...
            ValueError: Debug flags only allowed in debug mode

        """
        if not self.enable_debug or not __debug__:
            raise ValueError("Debug flags only allowed in debug mode")

        request = self.request
        for flag in name.split(','):
            if flag == 'source':
                request.debug.sourceAnnotations = True
            elif flag == 'tal':
                request.debug.showTAL = True
            elif flag == 'errors':
                # TODO: I am not sure this is the best solution.  What
                # if we want to enable tracebacks when also trying to
                # debug a different skin?
                skin = zope.component.getUtility(IBrowserSkinType, 'Debug')
                directlyProvides(request, providedBy(request) + skin)
            else:
                raise ValueError("Unknown debug flag: %s" % flag)
        return self.context

    if not __debug__: # pragma: no cover
        # If not in debug mode, we should get an error:
        traverse.__doc__ = """Disabled debug traversal adapter

        This adapter allows debugging flags to be set in the request,
        but it is disabled because Python was run with -O.

        Setup for demonstration:

            >>> from zope.publisher.browser import TestRequest
            >>> request = TestRequest()
            >>> ob = object()
            >>> adapter = debug(ob, request)

        in debug mode, ++debug++source enables source annotations

            >>> request.debug.sourceAnnotations
            False
            >>> adapter.traverse('source', ()) is ob
            Traceback (most recent call last):
            ...
            ValueError: Debug flags only allowed in debug mode

        ++debug++tal enables TAL markup in output

            >>> request.debug.showTAL
            False
            >>> adapter.traverse('tal', ()) is ob
            Traceback (most recent call last):
            ...
            ValueError: Debug flags only allowed in debug mode

        ++debug++errors enables tracebacks (by switching to debug skin)

            >>> Debug.providedBy(request)
            False
            >>> adapter.traverse('errors', ()) is ob
            Traceback (most recent call last):
            ...
            ValueError: Debug flags only allowed in debug mode

        You can specify several flags separated by commas

            >>> adapter.traverse('source,tal', ()) is ob
            Traceback (most recent call last):
            ...
            ValueError: Debug flags only allowed in debug mode
        """
