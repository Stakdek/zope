# -*- coding: utf-8 -*-
"""
Tests for expressions.py

"""
import unittest

from zope.testing.cleanup import CleanUp

from z3c.pt import expressions

# pylint:disable=protected-access


class TestRenderContentProvider(CleanUp, unittest.TestCase):
    def test_not_found(self):
        from zope.contentprovider.interfaces import ContentProviderLookupError

        context = object()
        request = object()
        view = object()
        name = "a provider"
        econtext = {"context": context, "request": request, "view": view}

        with self.assertRaises(ContentProviderLookupError) as exc:
            expressions.render_content_provider(econtext, name)

        e = exc.exception
        self.assertEqual(e.args, (name, (context, request, view)))

    def test_sets_ilocation_name(self):
        from zope import component
        from zope import interface
        from zope.location.interfaces import ILocation
        from zope.contentprovider.interfaces import IContentProvider

        attrs = {}

        @interface.implementer(ILocation, IContentProvider)
        class Provider(object):
            def __init__(self, *args):
                pass

            def __setattr__(self, name, value):
                attrs[name] = value

            update = render = lambda s: None

        component.provideAdapter(
            Provider,
            adapts=(object, object, object),
            provides=IContentProvider,
            name="a provider",
        )

        context = object()
        request = object()
        view = object()
        econtext = {"context": context, "request": request, "view": view}

        expressions.render_content_provider(econtext, "a provider")

        self.assertEqual(attrs, {"__name__": "a provider"})


class TestPathExpr(CleanUp, unittest.TestCase):
    def test_translate_empty_string(self):
        import ast

        expr = expressions.PathExpr("")
        result = expr.translate("", "foo")

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ast.Assign)

    def test_translate_invalid_path(self):
        from chameleon.exc import ExpressionError

        expr = expressions.PathExpr("")
        with self.assertRaises(ExpressionError):
            expr.translate("not valid", None)

    def test_translate_components(self):
        from chameleon.codegen import TemplateCodeGenerator
        from chameleon.astutil import ASTCodeGenerator
        from chameleon.astutil import node_annotations

        expr = expressions.PathExpr("")
        comps = expr._find_translation_components(["a"])

        # First component is skipped
        self.assertEqual(comps, [])

        # Single literal
        comps = expr._find_translation_components(["a", "b"])
        self.assertEqual([s.s for s in comps], ["b"])

        # Multiple literals
        comps = expr._find_translation_components(["a", "b", "c"])
        self.assertEqual([s.s for s in comps], ["b", "c"])

        # Single interpolation---must be longer than one character
        comps = expr._find_translation_components(["a", "?b"])
        self.assertEqual([s.s for s in comps], ["?b"])

        comps = expr._find_translation_components(["a", "?var"])
        self.assertEqual(len(comps), 1)
        code = ASTCodeGenerator(comps[0]).code
        self.assertEqual(code, "(format % args)")
        code = TemplateCodeGenerator(comps[0]).code
        self.assertEqual(code, "('%s' % (var, ))")

        args = node_annotations[comps[0].right]
        code = TemplateCodeGenerator(args).code
        self.assertEqual(code, "(var, )")

        # Multiple interpolations
        comps = expr._find_translation_components(["a", "?var", "?var2"])
        self.assertEqual(len(comps), 2)
        code = ASTCodeGenerator(comps[0]).code
        self.assertEqual(code, "(format % args)")
        code = TemplateCodeGenerator(comps[0]).code
        self.assertEqual(code, "('%s' % (var, ))")

        args = node_annotations[comps[0].right]
        code = TemplateCodeGenerator(args).code
        self.assertEqual(code, "(var, )")

        code = ASTCodeGenerator(comps[1]).code
        self.assertEqual(code, "(format % args)")
        code = TemplateCodeGenerator(comps[1]).code
        self.assertEqual(code, "('%s' % (var2, ))")

        args = node_annotations[comps[1].right]
        code = TemplateCodeGenerator(args).code
        self.assertEqual(code, "(var2, )")

        translated = expr.translate("a/?var/?var2", None)
        self.assertEqual(len(translated), 1)
        code = TemplateCodeGenerator(translated[0]).code
        # XXX: Normally this starts with 'None =', but sometimes on Python 2,
        # at least in tox, it starts with '__package__ ='. Why
        # is this?
        code = code.strip().replace("__package__", "None")
        self.assertEqual(
            code,
            "None = _path_traverse(a, econtext, True, (('%s' % (var, )), "
            "('%s' % (var2, )), ))",
        )
