##############################################################################
#
# Copyright (c) 2004-2009 Zope Foundation and Contributors.
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
"""Doc tests for the pagetemplate's 'engine' module
"""
import doctest
import re
import unittest
import zope.pagetemplate.engine
from zope.testing.renormalizing import RENormalizing
from zope.component.testing import PlacelessSetup

class EngineTests(PlacelessSetup,
                  unittest.TestCase):

    def _makeOne(self):
        return zope.pagetemplate.engine._Engine()

    def test_function_namespaces_return_secured_proxies(self):
        # See https://bugs.launchpad.net/zope3/+bug/98323
        from zope.proxy import isProxy
        engine = self._makeOne()
        namespace = engine.getFunctionNamespace('test')
        self.assertTrue(isProxy(namespace))

    def test_getContext_namespace(self):
        engine = self._makeOne()
        ctx = engine.getContext({'a': 1}, b=2, request=3, context=4)
        self.assertEqual(ctx.getValue('a'), 1)
        self.assertEqual(ctx.getValue('b'), 2)
        self.assertEqual(ctx.getValue('request'), 3)
        self.assertEqual(ctx.getValue('context'), 4)

class DummyEngine(object):

    def getTypes(self):
        return {}

class DummyContext(object):

    _engine = DummyEngine()

    def __init__(self, **kw):
        self.vars = kw

class ZopePythonExprTests(unittest.TestCase):

    def test_simple(self):
        from zope.pagetemplate.engine import ZopePythonExpr
        expr = ZopePythonExpr('python', 'max(a,b)', DummyEngine())
        self.assertEqual(expr(DummyContext(a=1, b=2)), 2)

    def test_allowed_module_name(self):
        from zope.pagetemplate.engine import ZopePythonExpr
        expr = ZopePythonExpr('python', '__import__("sys").__name__',
                              DummyEngine())
        self.assertEqual(expr(DummyContext()), 'sys')

    @unittest.skipUnless(zope.pagetemplate.engine.HAVE_UNTRUSTED,
                         "Needs untrusted")
    def test_forbidden_module_name(self):
        from zope.pagetemplate.engine import ZopePythonExpr
        from zope.security.interfaces import Forbidden
        expr = ZopePythonExpr('python', '__import__("sys").exit',
                              DummyEngine())
        self.assertRaises(Forbidden, expr, DummyContext())

    @unittest.skipUnless(zope.pagetemplate.engine.HAVE_UNTRUSTED,
                         "Needs untrusted")
    def test_disallowed_builtin(self):
        from zope.pagetemplate.engine import ZopePythonExpr
        expr = ZopePythonExpr('python', 'open("x", "w")', DummyEngine())
        self.assertRaises(NameError, expr, DummyContext())


class TestZopeContext(PlacelessSetup,
                      unittest.TestCase):

    assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegex',
                                getattr(unittest.TestCase, 'assertRaisesRegexp'))

    def _makeOne(self):
        return zope.pagetemplate.engine.ZopeContext(None, {})

    def test_translate(self):
        ctx = self._makeOne()
        self.assertEqual(ctx.translate('msgid'), 'msgid')

    def test_evaluate_error(self):
        ctx = self._makeOne()
        with self.assertRaisesRegex(zope.pagetemplate.engine.InlineCodeError,
                                    "Inline Code Evaluation is deactivated"):
            ctx.evaluateCode('lang', 'code')

    def test_evaluate_interpreter_not_importable(self):
        ctx = self._makeOne()
        ctx.evaluateInlineCode = True
        with self.assertRaises(ImportError):
            ctx.evaluateCode('lang', 'code')

    def test_evaluate_interpreter_not_found(self):
        get = zope.pagetemplate.engine._get_iinterpreter
        from zope import interface
        class IInterpreter(interface.Interface):
            pass
        def mock_get():
            return IInterpreter

        ctx = self._makeOne()
        ctx.evaluateInlineCode = True
        zope.pagetemplate.engine._get_iinterpreter = mock_get
        try:
            with self.assertRaisesRegex(zope.pagetemplate.engine.InlineCodeError,
                                        "No interpreter named"):
                ctx.evaluateCode('lang', 'code')
        finally:
            zope.pagetemplate.engine._get_iinterpreter = get

    def test_evaluate_interpreter_found(self):
        get = zope.pagetemplate.engine._get_iinterpreter
        from zope import interface
        from zope import component
        class IInterpreter(interface.Interface):
            pass
        def mock_get():
            return IInterpreter

        @interface.implementer(IInterpreter)
        class Interpreter(object):
            def evaluateRawCode(self, code, globs):
                globs['new'] = code
                return 42

        component.provideUtility(Interpreter(), name='lang')

        ctx = self._makeOne()
        ctx.evaluateInlineCode = True
        zope.pagetemplate.engine._get_iinterpreter = mock_get
        try:
            result = ctx.evaluateCode('lang', 'code')
        finally:
            zope.pagetemplate.engine._get_iinterpreter = get

        self.assertEqual(result, 42)
        self.assertEqual('code', ctx.getValue('new'))


class TestTraversableModuleImporter(unittest.TestCase):

    def test_traverse_fails(self):
        from zope.traversing.interfaces import TraversalError

        tmi = zope.pagetemplate.engine.TraversableModuleImporter()
        with self.assertRaises(TraversalError):
            tmi.traverse('zope.cannot exist', ())

        with self.assertRaises(TraversalError):
            tmi.traverse('zope.pagetemplate.engine.DNE', ())


        with self.assertRaises(TraversalError):
            tmi.traverse('pickle.no_sub_module', ())


class TestAppPT(unittest.TestCase):

    def test_apppt_engine(self):
        self.assertIs(zope.pagetemplate.engine.AppPT().pt_getEngine(),
                      zope.pagetemplate.engine.Engine)

    def test_trustedapppt_engine(self):
        self.assertIs(zope.pagetemplate.engine.TrustedAppPT().pt_getEngine(),
                      zope.pagetemplate.engine.TrustedEngine)


def test_suite():

    checker = RENormalizing([
        # Python 3 includes module name in exceptions
        (re.compile(r"zope.security.interfaces.ForbiddenAttribute"),
         "ForbiddenAttribute"),
        (re.compile(r"<class 'zope.security._proxy._Proxy'>"),
         "<type 'zope.security._proxy._Proxy'>"),
        (re.compile(r"<class 'list'>"), "<type 'list'>"),
        # PyPy/pure-Python implementation
        (re.compile(r"<class 'zope.security.proxy.ProxyPy'>"),
         "<type 'zope.security._proxy._Proxy'>"),
    ])

    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTest(doctest.DocTestSuite('zope.pagetemplate.engine',
                                       checker=checker))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
