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
import os
import sys

import six

from zope import i18n
from zope.security.proxy import ProxyFactory

from chameleon.i18n import fast_translate
from chameleon.zpt import template
from chameleon.tales import StringExpr
from chameleon.tales import NotExpr
from chameleon.compiler import ExpressionEvaluator

from z3c.pt import expressions

try:
    from Missing import MV

    MV = MV  # pyflakes pragma: no cover
except ImportError:
    MV = object()

_marker = object()


BOOLEAN_HTML_ATTRS = frozenset(
    [
        # List of Boolean attributes in HTML that should be rendered in
        # minimized form (e.g. <img ismap> rather than <img ismap="">)
        # From http://www.w3.org/TR/xhtml1/#guidelines (C.10)
        # TODO: The problem with this is that this is not valid XML and
        # can't be parsed back!
        "compact",
        "nowrap",
        "ismap",
        "declare",
        "noshade",
        "checked",
        "disabled",
        "readonly",
        "multiple",
        "selected",
        "noresize",
        "defer",
    ]
)


class OpaqueDict(dict):
    def __new__(cls, dictionary):
        inst = dict.__new__(cls)
        inst.dictionary = dictionary
        return inst

    def __getitem__(self, name):
        return self.dictionary[name]

    def __len__(self):
        return len(self.dictionary)

    def __repr__(self):
        return "{...} (%d entries)" % len(self)


sys_modules = ProxyFactory(OpaqueDict(sys.modules))


class BaseTemplate(template.PageTemplate):
    content_type = None
    version = 2

    expression_types = {
        "python": expressions.PythonExpr,
        "string": StringExpr,
        "not": NotExpr,
        "exists": expressions.ExistsExpr,
        "path": expressions.PathExpr,
        "provider": expressions.ProviderExpr,
        "nocall": expressions.NocallExpr,
    }

    default_expression = "path"

    literal_false = True

    strict = False

    trim_attribute_space = True

    @property
    def boolean_attributes(self):
        if self.content_type == "text/xml":
            return set()

        return BOOLEAN_HTML_ATTRS

    @property
    def builtins(self):
        builtins = {"nothing": None, "modules": sys_modules}

        tales = ExpressionEvaluator(self.engine, builtins)
        builtins["tales"] = tales

        return builtins

    def bind(self, ob, request=None):
        def render(request=request, **kwargs):
            context = self._pt_get_context(ob, request, kwargs)
            return self.render(**context)

        return BoundPageTemplate(self, render)

    def render(self, target_language=None, **context):
        # We always include a ``request`` variable; it is (currently)
        # depended on in various expression types and must be defined
        request = context.setdefault("request", None)

        if target_language is None:
            try:
                target_language = i18n.negotiate(request)
            except Exception:
                target_language = None

        context["target_language"] = target_language

        # bind translation-method to request
        def translate(
            msgid,
            domain=None,
            mapping=None,
            target_language=None,
            default=None,
            context=None,
        ):
            if msgid is MV:
                # Special case handling of Zope2's Missing.MV
                # (Missing.Value) used by the ZCatalog but is
                # unhashable.

                # This case cannot arise in ordinary templates; msgid
                # comes from i18n:translate attributes, which does not
                # take a TALES expression, just a literal string.
                # However, the 'context' argument is available as an
                # implementation detail for macros
                return
            return fast_translate(
                msgid, domain, mapping, request, target_language, default
            )

        context["translate"] = translate

        if request is not None and not isinstance(request, six.string_types):
            content_type = self.content_type or "text/html"
            response = request.response
            if response and not response.getHeader("Content-Type"):
                response.setHeader("Content-Type", content_type)

        base_renderer = super(BaseTemplate, self).render
        return base_renderer(**context)

    def __call__(self, *args, **kwargs):
        bound_pt = self.bind(self)
        return bound_pt(*args, **kwargs)

    def _pt_get_context(self, instance, request, kwargs):
        return dict(
            context=instance,
            here=instance,
            options=kwargs,
            request=request,
            template=self,
        )


class BaseTemplateFile(BaseTemplate, template.PageTemplateFile):
    """If ``filename`` is a relative path, the module path of the
    class where the instance is used to get an absolute path."""

    cache = {}

    def __init__(self, filename, path=None, content_type=None, **kwargs):
        if path is not None:
            filename = os.path.join(path, filename)

        if not os.path.isabs(filename):
            for depth in (1, 2):
                frame = sys._getframe(depth)
                package_name = frame.f_globals.get("__name__", None)
                if (
                    package_name is not None
                    and package_name != self.__module__
                ):
                    module = sys.modules[package_name]
                    try:
                        path = module.__path__[0]
                    except AttributeError:
                        path = module.__file__
                        path = path[: path.rfind(os.sep)]
                    break
                else:
                    package_path = frame.f_globals.get("__file__", None)
                    if package_path is not None:
                        path = os.path.dirname(package_path)
                        break

            if path is not None:
                filename = os.path.join(path, filename)

        template.PageTemplateFile.__init__(self, filename, **kwargs)

        # Set content-type last, so that we can override whatever was
        # magically sniffed from the source template.
        self.content_type = content_type


class PageTemplate(BaseTemplate):
    """Page Templates using TAL, TALES, and METAL.

    This class is suitable for standalone use or class
    property. Keyword-arguments are passed into the template as-is.

    Initialize with a template string."""

    version = 1

    def __get__(self, instance, type):
        if instance is not None:
            return self.bind(instance)
        return self


class PageTemplateFile(BaseTemplateFile, PageTemplate):
    """Page Templates using TAL, TALES, and METAL.

    This class is suitable for standalone use or class
    property. Keyword-arguments are passed into the template as-is.

    Initialize with a filename."""

    cache = {}


class ViewPageTemplate(PageTemplate):
    """Template class suitable for use with a Zope browser view; the
    variables ``view``, ``context`` and ``request`` variables are
    brought in to the local scope of the template automatically, while
    keyword arguments are passed in through the ``options``
    dictionary. Note that the default expression type for this class
    is 'path' (standard Zope traversal)."""

    def _pt_get_context(self, view, request, kwargs):
        context = kwargs.get("context")
        if context is None:
            context = view.context
        request = request or kwargs.get("request") or view.request
        return dict(
            view=view,
            context=context,
            request=request,
            options=kwargs,
            template=self,
        )

    def __call__(self, _ob=None, context=None, request=None, **kwargs):
        kwargs.setdefault("context", context)
        kwargs.setdefault("request", request)
        bound_pt = self.bind(_ob)
        return bound_pt(**kwargs)


class ViewPageTemplateFile(ViewPageTemplate, PageTemplateFile):
    """If ``filename`` is a relative path, the module path of the
    class where the instance is used to get an absolute path."""

    cache = {}


class BoundPageTemplate(object):
    """When a page template class is used as a property, it's bound to
    the class instance on access, which is implemented using this
    helper class."""

    __self__ = None
    __func__ = None

    def __init__(self, pt, render):
        object.__setattr__(self, "__self__", pt)
        object.__setattr__(self, "__func__", render)

    im_self = property(lambda self: self.__self__)
    im_func = property(lambda self: self.__func__)
    macros = property(lambda self: self.__self__.macros)
    filename = property(lambda self: self.__self__.filename)

    def __call__(self, *args, **kw):
        kw.setdefault("args", args)
        return self.__func__(**kw)

    def __setattr__(self, name, v):
        raise AttributeError("Can't set attribute", name)

    def __repr__(self):
        return "<%s.Bound%s %r>" % (
            type(self.__self__).__module__,
            type(self.__self__).__name__,
            self.filename,
        )
