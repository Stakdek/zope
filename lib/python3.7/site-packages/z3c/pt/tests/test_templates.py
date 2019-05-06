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
import unittest

from zope.testing.cleanup import CleanUp
import zope.configuration.xmlconfig

from z3c.pt import pagetemplate
from z3c.pt.pagetemplate import PageTemplateFile
from z3c.pt.pagetemplate import ViewPageTemplateFile


class Setup(CleanUp):
    def setUp(self):
        CleanUp.setUp(self)
        import z3c.pt

        zope.configuration.xmlconfig.file("configure.zcml", z3c.pt)


class TestPageTemplate(Setup, unittest.TestCase):
    def test_string_function(self):
        template = pagetemplate.PageTemplate(
            """<div tal:content="python:string('a string')" />"""
        )
        result = template.render()
        self.assertEqual(result, "<div>a string</div>")

    def test_nocall_function(self):
        class Call(object):
            def __call__(self):
                raise AssertionError("Should not be called")

            def __str__(self):
                return "Not Called"

        arg = {"call": Call()}
        template = pagetemplate.PageTemplate(
            """<div tal:content="python:nocall('arg/call')" />"""
        )
        result = template.render(arg=arg)
        self.assertEqual(result, "<div>Not Called</div>")


class TestPageTemplateFile(Setup, unittest.TestCase):
    def test_nocall(self):
        template = PageTemplateFile("nocall.pt")

        def dont_call():
            raise AssertionError("Should not be called")

        result = template(callable=dont_call)
        self.assertTrue(repr(dont_call) in result)

    def test_exists(self):
        template = PageTemplateFile("exists.pt")

        def dont_call():
            raise AssertionError("Should not be called")

        result = template(callable=dont_call)
        self.assertTrue("ok" in result)

    def test_false_attribute(self):
        template = PageTemplateFile("false.pt")
        result = template()
        self.assertTrue("False" in result)

    def test_boolean_attribute(self):
        template = PageTemplateFile("boolean.pt")
        result = template()
        self.assertFalse("False" in result)
        self.assertTrue('checked="checked"' in result)

    def test_path(self):
        template = PageTemplateFile("path.pt")

        class Context(object):
            dummy_wysiwyg_support = True

        context = Context()
        template = template.__get__(context, Context)

        result = template(editor="dummy")
        self.assertTrue("supported" in result)
        self.assertTrue("some path" in result)


class TestViewPageTemplateFile(Setup, unittest.TestCase):
    def test_provider(self):
        class Context(object):
            pass

        class Request(object):
            response = None

        class View(object):
            __call__ = ViewPageTemplateFile("provider.pt")

        # Test binding descriptor behaviour.
        self.assertIsInstance(View.__call__, ViewPageTemplateFile)

        from zope.interface import Interface
        from zope.schema import Field
        from zope.interface import implementer
        from zope.interface import directlyProvides
        from zope.contentprovider.interfaces import ITALNamespaceData

        class ITestProvider(Interface):
            context = Field(u"Provider context.")

        directlyProvides(ITestProvider, ITALNamespaceData)
        assert ITALNamespaceData.providedBy(ITestProvider)

        @implementer(ITestProvider)
        class Provider(object):
            def __init__(self, *args):
                data.extend(list(args))

            def update(self):
                data.extend("updated")

            def render(self):
                return """<![CDATA[ %r, %r]]>""" % (data, self.__dict__)

        view = View()
        data = []

        from zope.interface import implementedBy
        from zope.component import provideAdapter
        from zope.contentprovider.interfaces import IContentProvider

        provideAdapter(
            Provider,
            (
                implementedBy(Context),
                implementedBy(Request),
                implementedBy(View),
            ),
            IContentProvider,
            name="content",
        )

        context = Context()
        request = Request()

        result = view(context=context, request=request)
        self.assertIn(repr(data), result)
        self.assertIn(repr({"context": context}), result)


class TestOpaqueDict(unittest.TestCase):
    def test_getitem(self):
        import operator

        d = {}
        od = pagetemplate.OpaqueDict(d)
        with self.assertRaises(KeyError):
            operator.itemgetter("key")(od)

        d["key"] = 42
        self.assertEqual(od["key"], 42)

    def test_len(self):
        d = {}
        od = pagetemplate.OpaqueDict(d)
        self.assertEqual(0, len(od))

        d["key"] = 42
        self.assertEqual(1, len(od))

    def test_repr(self):
        d = {}
        od = pagetemplate.OpaqueDict(d)
        self.assertEqual("{...} (0 entries)", repr(od))

        d["key"] = 42
        self.assertEqual("{...} (1 entries)", repr(od))


class TestBaseTemplate(unittest.TestCase):
    def test_negotiate_fails(self):
        class I18N(object):
            request = None

            def negotiate(self, request):
                self.request = request
                raise Exception("This is caught")

        i18n = I18N()
        orig_i18n = pagetemplate.i18n
        pagetemplate.i18n = i18n
        try:
            template = pagetemplate.BaseTemplate("<html />")
            request = "strings are allowed"
            template.render(request=request)
            self.assertIs(i18n.request, request)
        finally:
            pagetemplate.i18n = orig_i18n

    def test_translate_mv(self):
        template = pagetemplate.BaseTemplate(
            """
        <html>
          <body metal:use-macro="m" />
        </html>
        """
        )

        class Macro(object):
            translate = None

            def include(self, stream, econtext, *args, **kwargs):
                self.translate = econtext["translate"]

        macro = Macro()
        template.render(m=macro)

        self.assertIsNone(macro.translate(pagetemplate.MV))


class TestBaseTemplateFile(unittest.TestCase):
    def test_init_with_path(self):

        here = os.path.abspath(os.path.dirname(__file__))

        template = pagetemplate.BaseTemplateFile("view.pt", path=here)

        self.assertEqual(template.filename, os.path.join(here, "view.pt"))


class TestBoundPageTemplate(unittest.TestCase):

    # Avoid DeprecationWarning for assertRaisesRegexp on Python 3 while
    # coping with Python 2 not having the Regex spelling variant
    assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegex',
                                unittest.TestCase.assertRaisesRegexp)

    def test_setattr(self):
        bound = pagetemplate.BoundPageTemplate(None, None)
        with self.assertRaisesRegex(AttributeError, "Can't set attribute"):
            bound.__self__ = 42

    def test_repr(self):
        # It requires the 'filename' attribute
        class Template(object):
            filename = "file.pt"

        bound = pagetemplate.BoundPageTemplate(Template(), "render")
        self.assertEqual(
            "<z3c.pt.tests.test_templates.BoundTemplate 'file.pt'>",
            repr(bound),
        )

    def test_attributes(self):
        func = object()
        bound = pagetemplate.BoundPageTemplate(self, func)
        self.assertIs(self, bound.im_self)
        self.assertIs(self, bound.__self__)
        self.assertIs(func, bound.im_func)
        self.assertIs(func, bound.__func__)
