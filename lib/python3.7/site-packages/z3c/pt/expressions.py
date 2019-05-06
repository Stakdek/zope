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
import re
import ast
from types import MethodType

import z3c.pt.namespaces

import zope.event

from zope.traversing.adapters import traversePathElement
from zope.contentprovider.interfaces import IContentProvider
from zope.contentprovider.interfaces import ContentProviderLookupError
from zope.contentprovider.tales import addTALNamespaceData
from zope.traversing.interfaces import ITraversable
from zope.location.interfaces import ILocation
from zope.contentprovider.interfaces import BeforeUpdateEvent

from chameleon.tales import TalesExpr
from chameleon.tales import ExistsExpr as BaseExistsExpr
from chameleon.tales import PythonExpr as BasePythonExpr
from chameleon.tales import StringExpr
from chameleon.codegen import template
from chameleon.astutil import load
from chameleon.astutil import Symbol
from chameleon.astutil import Builtin
from chameleon.astutil import NameLookupRewriteVisitor
from chameleon.exc import ExpressionError

_marker = object()


def render_content_provider(econtext, name):
    name = name.strip()

    context = econtext.get("context")
    request = econtext.get("request")
    view = econtext.get("view")

    cp = zope.component.queryMultiAdapter(
        (context, request, view), IContentProvider, name=name
    )

    # provide a useful error message, if the provider was not found.
    # Be sure to provide the objects in addition to the name so
    # debugging ZCML registrations is possible
    if cp is None:
        raise ContentProviderLookupError(name, (context, request, view))

    # add the __name__ attribute if it implements ILocation
    if ILocation.providedBy(cp):
        cp.__name__ = name

    # Insert the data gotten from the context
    addTALNamespaceData(cp, econtext)

    # Stage 1: Do the state update.
    zope.event.notify(BeforeUpdateEvent(cp, request))
    cp.update()

    # Stage 2: Render the HTML content.
    return cp.render()


def path_traverse(base, econtext, call, path_items):
    if path_items:
        request = econtext.get("request")
        path_items = list(path_items)
        path_items.reverse()

        while path_items:
            name = path_items.pop()
            ns_used = ":" in name
            if ns_used:
                namespace, name = name.split(":", 1)
                base = z3c.pt.namespaces.function_namespaces[namespace](base)
                if ITraversable.providedBy(base):
                    base = traversePathElement(
                        base, name, path_items, request=request
                    )

                    # base = proxify(base)

                    continue

            # special-case dicts for performance reasons
            if isinstance(base, dict):
                next = base.get(name, _marker)
            else:
                next = getattr(base, name, _marker)

            if next is not _marker:
                base = next
                if ns_used and isinstance(base, MethodType):
                    base = base()
                # The bytecode peephole optimizer removes the next line:
                continue  # pragma: no cover
            else:
                base = traversePathElement(
                    base, name, path_items, request=request
                )

            # if not isinstance(base, (basestring, tuple, list)):
            #    base = proxify(base)

    if call and getattr(base, "__call__", _marker) is not _marker:
        return base()

    return base


class ContextExpressionMixin(object):
    """Mixin-class for expression compilers."""

    transform = None

    def __call__(self, target, engine):
        # Make call to superclass to assign value to target
        assignment = super(ContextExpressionMixin, self).__call__(
            target, engine
        )

        transform = template(
            "target = transform(econtext, target)",
            target=target,
            transform=self.transform,
        )

        return assignment + transform


class PathExpr(TalesExpr):
    path_regex = re.compile(
        r"^(?:(nocall|not):\s*)*((?:[A-Za-z0-9_][A-Za-z0-9_:]*)"
        + r"(?:/[?A-Za-z0-9_@\-+][?A-Za-z0-9_@\-\.+/:]*)*)$"
    )

    interpolation_regex = re.compile(r"\?[A-Za-z][A-Za-z0-9_]+")

    traverser = Symbol(path_traverse)

    def _find_translation_components(self, parts):
        components = []
        for part in parts[1:]:
            interpolation_args = []

            def replace(match):
                start, end = match.span()
                interpolation_args.append(part[start + 1: end])
                return "%s"

            while True:
                part, count = self.interpolation_regex.subn(replace, part)
                if count == 0:
                    break

            if interpolation_args:
                component = template(
                    "format % args",
                    format=ast.Str(part),
                    args=ast.Tuple(
                        list(map(load, interpolation_args)), ast.Load()
                    ),
                    mode="eval",
                )
            else:
                component = ast.Str(part)

            components.append(component)

        return components

    def translate(self, string, target):
        """
        >>> from chameleon.tales import test
        >>> test(PathExpr('None')) is None
        True
        """
        string = string.strip()

        if not string:
            return template("target = None", target=target)

        m = self.path_regex.match(string)
        if m is None:
            raise ExpressionError("Not a valid path-expression.", string)

        nocall, path = m.groups()

        # note that unicode paths are not allowed
        parts = str(path).split("/")

        components = self._find_translation_components(parts)

        base = parts[0]

        if not components:
            if len(parts) == 1 and (nocall or base == "None"):
                return template("target = base", base=base, target=target)
            else:
                components = ()

        call = template(
            "traverse(base, econtext, call, path_items)",
            traverse=self.traverser,
            base=load(base),
            call=load(str(not nocall)),
            path_items=ast.Tuple(elts=components),
            mode="eval",
        )

        return template("target = value", target=target, value=call)


class NocallExpr(PathExpr):
    """A path-expression which does not call the resolved object."""

    def translate(self, expression, engine):
        return super(NocallExpr, self).translate(
            "nocall:%s" % expression, engine
        )


class ExistsExpr(BaseExistsExpr):
    exceptions = AttributeError, LookupError, TypeError, KeyError, NameError

    def __init__(self, expression):
        super(ExistsExpr, self).__init__("nocall:" + expression)


class ProviderExpr(ContextExpressionMixin, StringExpr):
    transform = Symbol(render_content_provider)


class PythonExpr(BasePythonExpr):
    builtins = {
        name: template(
            "tales(econtext, rcontext, name)",
            tales=Builtin("tales"),
            name=ast.Str(s=name),
            mode="eval",
        )
        for name in ("path", "exists", "string", "nocall")
    }

    def __call__(self, target, engine):
        return self.translate(self.expression, target)

    def rewrite(self, node):
        builtin = self.builtins.get(node.id)
        if builtin is not None:
            return template(
                "get(name) if get(name) is not None else builtin",
                get=Builtin("get"),
                name=ast.Str(s=node.id),
                builtin=builtin,
                mode="eval",
            )

    @property
    def transform(self):
        return NameLookupRewriteVisitor(self.rewrite)
