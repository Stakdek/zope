# -*- coding: utf-8 -*-
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
"""Default TALES expression implementations tests.
"""
import sys
import unittest

from zope.tales.engine import Engine
from zope.tales.interfaces import ITALESFunctionNamespace
from zope.tales.tales import Undefined
from zope.interface import implementer

text_type = str if str is not bytes else unicode

PY3 = sys.version_info[0] == 3

class Data(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __getattr__(self, name):
        # Let linters (like pylint) know this is a dynamic class and they shouldn't
        # emit "Data has no attribute" errors
        return object.__getattribute__(self, name)

    def __repr__(self):
        return self.name

    __str__ = __repr__

class ErrorGenerator(object):

    def __getitem__(self, name):
        from six.moves import builtins
        if name == 'Undefined':
            e = Undefined
        else:
            e = getattr(builtins, name, None) or SystemError
        raise e('mess')

class Callable(object):

    def __call__(self):
        return 42

class OldStyleCallable: # NOT object

    pass

class ExpressionTestBase(unittest.TestCase):

    def setUp(self):
        # Test expression compilation
        d = Data(
            name='xander',
            y=Data(
                name='yikes',
                z=Data(name='zope')
            )
        )
        at = Data(
            name='yikes',
            _d=d
        )
        self.context = Data(
            vars=dict(
                x=d,
                y=Data(z=3),
                b='boot',
                B=2,
                adapterTest=at,
                dynamic='z',
                eightBits=u'déjà vu'.encode('utf-8'),
                ErrorGenerator=ErrorGenerator(),
                callable=Callable(),
                old_callable_class=OldStyleCallable,
            )
        )

        self.engine = Engine

        self.py3BrokenEightBits = "a b'd\\xc3\\xa9j\\xc3\\xa0 vu'"


    def _compiled_expr(self, expr):
        return self.engine.compile(expr) if isinstance(expr, str) else expr

    def _check_evals_to(self, expr, result):
        expr = self._compiled_expr(expr)
        self.assertEqual(expr(self.context), result)
        return expr

    def _check_evals_to_instance(self, expr, result_kind):
        expr = self._compiled_expr(expr)
        self.assertIsInstance(expr(self.context), result_kind)
        return expr

    def _check_raises_compiler_error(self, expr_str, regex=None):
        from zope.tales.tales import CompilerError
        meth = self.assertRaises if regex is None else self.assertRaisesRegexp
        args = (regex,) if regex is not None else ()
        with meth(CompilerError, *args) as exc:
            self.engine.compile(expr_str)
        return exc.exception

    def _check_subexpr_raises_compiler_error(self, expr, regexp):
        from zope.tales.expressions import SubPathExpr
        from zope.tales.tales import CompilerError
        with self.assertRaisesRegexp(CompilerError,
                                     regexp):
            SubPathExpr(expr, None, self.engine)


class TestParsedExpressions(ExpressionTestBase):
    # Whitebox tests of expressions that have been compiled by the engine

    def testSimple(self):
        expr = self.engine.compile('x')
        self._check_evals_to(expr, self.context.vars['x'])

    def testPath(self):
        expr = self.engine.compile('x/y')
        self._check_evals_to(expr, self.context.vars['x'].y)
        self.assertEqual("standard expression ('x/y')", str(expr))
        self.assertEqual("<PathExpr standard:'x/y'>", repr(expr))

    def test_path_nocall_call(self):
        self._check_evals_to('callable', 42)
        self._check_evals_to('nocall:callable', self.context.vars['callable'])

        self._check_evals_to_instance('old_callable_class', OldStyleCallable)
        self._check_evals_to('nocall:old_callable_class', OldStyleCallable)

    def test_path_exists(self):
        self._check_evals_to('exists:x', 1)
        self._check_evals_to('exists:' + 'i' + str(id(self)), 0)

    def testLongPath(self):
        expr = self.engine.compile('x/y/z')
        self._check_evals_to(expr, self.context.vars['x'].y.z)

    def testOrPath(self):
        expr = self.engine.compile('path:a|b|c/d/e')
        self._check_evals_to(expr, 'boot')

        for e in 'Undefined', 'AttributeError', 'LookupError', 'TypeError':
            expr = self.engine.compile('path:ErrorGenerator/%s|b|c/d/e' % e)
            self._check_evals_to(expr, 'boot')

    def test_path_CONTEXTS(self):
        self.context.contexts = 42
        self._check_evals_to('CONTEXTS', 42)

    def testDynamic(self):
        expr = self.engine.compile('x/y/?dynamic')
        self._check_evals_to(expr, self.context.vars['x'].y.z)

    def testBadInitalDynamic(self):
        from zope.tales.tales import CompilerError
        with self.assertRaises(CompilerError) as exc:
            self.engine.compile('?x')
        e = exc.exception
        self.assertEqual(e.args[0],
                         'Dynamic name specified in first subpath element')

    def test_dynamic_invalid_variable_name(self):
        from zope.tales.tales import CompilerError
        with self.assertRaisesRegexp(CompilerError,
                                     "Invalid variable name"):
            self.engine.compile('path:a/?123')

    def testOldStyleClassIsCalled(self):
        class AnOldStyleClass:
            pass
        self.context.vars['oldstyleclass'] = AnOldStyleClass
        expr = self.engine.compile('oldstyleclass')
        self.assertTrue(isinstance(expr(self.context), AnOldStyleClass))

    def testString(self):
        expr = self.engine.compile('string:Fred')
        context = self.context
        result = expr(context)
        self.assertEqual(result, 'Fred')
        self.assertIsInstance(result, str)
        self.assertEqual("string expression ('Fred')", str(expr))
        self.assertEqual("<StringExpr 'Fred'>", repr(expr))

    def testStringSub(self):
        expr = self.engine.compile('string:A$B')
        self._check_evals_to(expr, 'A2')

    def testStringSub_w_python(self):
        CompilerError = self.engine.getCompilerError()
        self.assertRaises(CompilerError,
                          self.engine.compile,
                          'string:${python:1}')

    def testStringSubComplex(self):
        expr = self.engine.compile('string:a ${x/y} b ${y/z} c')
        self._check_evals_to(expr, 'a yikes b 3 c')

    def testStringSubComplex_w_miss_and_python(self):
        # See https://bugs.launchpad.net/zope.tales/+bug/1002242
        CompilerError = self.engine.getCompilerError()
        self.assertRaises(CompilerError,
                          self.engine.compile,
                          'string:${nothig/nothing|python:1}')

    def testString8Bits(self):
        # Simple eight bit string interpolation should just work.
        # Except on Py3, where we really mess it up.
        expr = self.engine.compile('string:a ${eightBits}')
        expected = 'a ' + self.context.vars['eightBits'] if not PY3 else self.py3BrokenEightBits
        self._check_evals_to(expr, expected)

    def testStringUnicode(self):
        # Unicode string expressions should return unicode strings
        expr = self.engine.compile(u'string:Fred')
        context = self.context
        result = expr(context)
        self.assertEqual(result, u'Fred')
        self.assertIsInstance(result, text_type)

    def testStringFailureWhenMixed(self):
        # Mixed Unicode and 8bit string interpolation fails with a
        # UnicodeDecodeError, assuming there is no default encoding
        expr = self.engine.compile(u'string:a ${eightBits}')
        with self.assertRaises(UnicodeDecodeError):
            result = expr(self.context)
            # If we get here, we're on Python 3, which handles this
            # poorly.
            self.assertTrue(PY3)
            self.assertEqual(result, self.py3BrokenEightBits)
            self.context.vars['eightBits'].decode('ascii') # raise UnicodeDecodeError

    def test_string_escape_percent(self):
        self._check_evals_to('string:%', '%')

    def testPython(self):
        expr = self.engine.compile('python: 2 + 2')
        self._check_evals_to(expr, 4)

    def testPythonCallableIsntCalled(self):
        self.context.vars['acallable'] = lambda: 23
        expr = self.engine.compile('python: acallable')
        self.assertEqual(expr(self.context), self.context.vars['acallable'])

    def testPythonNewline(self):
        expr = self.engine.compile('python: 2 \n+\n 2\n')
        self._check_evals_to(expr, 4)

    def testPythonDosNewline(self):
        expr = self.engine.compile('python: 2 \r\n+\r\n 2\r\n')
        self._check_evals_to(expr, 4)

    def testPythonErrorRaisesCompilerError(self):
        self.assertRaises(self.engine.getCompilerError(),
                          self.engine.compile, 'python: splat.0')

    def testHybridPathExpressions(self):
        def eval(expr):
            e = self.engine.compile(expr)
            return e(self.context)
        self.context.vars['one'] = 1
        self.context.vars['acallable'] = lambda: 23

        self.assertEqual(eval('foo | python:1+1'), 2)
        self.assertEqual(eval('foo | python:acallable'),
                         self.context.vars['acallable'])
        self.assertEqual(eval('foo | string:x'), 'x')
        self.assertEqual(eval('foo | string:$one'), '1')
        self.assertTrue(eval('foo | exists:x'))

    def testEmptyPathSegmentRaisesCompilerError(self):
        CompilerError = self.engine.getCompilerError()
        def check(expr):
            self.assertRaises(CompilerError, self.engine.compile, expr)

        # path expressions on their own:
        check('/ab/cd | c/d | e/f')
        check('ab//cd | c/d | e/f')
        check('ab/cd/ | c/d | e/f')
        check('ab/cd | /c/d | e/f')
        check('ab/cd | c//d | e/f')
        check('ab/cd | c/d/ | e/f')
        check('ab/cd | c/d | /e/f')
        check('ab/cd | c/d | e//f')
        check('ab/cd | c/d | e/f/')

        # path expressions embedded in string: expressions:
        check('string:${/ab/cd}')
        check('string:${ab//cd}')
        check('string:${ab/cd/}')
        check('string:foo${/ab/cd | c/d | e/f}bar')
        check('string:foo${ab//cd | c/d | e/f}bar')
        check('string:foo${ab/cd/ | c/d | e/f}bar')
        check('string:foo${ab/cd | /c/d | e/f}bar')
        check('string:foo${ab/cd | c//d | e/f}bar')
        check('string:foo${ab/cd | c/d/ | e/f}bar')
        check('string:foo${ab/cd | c/d | /e/f}bar')
        check('string:foo${ab/cd | c/d | e//f}bar')
        check('string:foo${ab/cd | c/d | e/f/}bar')

    def test_defer_expression_returns_wrapper(self):
        from zope.tales.expressions import DeferWrapper
        from zope.tales.expressions import DeferExpr
        expr = self.engine.compile('defer: B')
        self.assertIsInstance(expr, DeferExpr)
        self.assertEqual(str(expr), "<DeferExpr 'B'>")
        self._check_evals_to_instance(expr, DeferWrapper)

        wrapper = expr(self.context)
        # It evaluates to what its underlying expression evaluates to
        self.assertEqual(wrapper(), self.context.vars['B'])
        # The str() of defer is the same as the str() of evaluating it
        self.assertEqual(str(wrapper), str(self.context.vars['B']))
        self.assertEqual(str(wrapper()), str(self.context.vars['B']))

    def test_eval_defer_wrapper(self):
        expr = self.engine.compile('defer: b')
        self.context.vars['deferred'] = expr(self.context)
        self._check_evals_to('deferred', self.context.vars['b'])

    def test_lazy_expression_returns_wrapper(self):
        from zope.tales.expressions import LazyWrapper
        from zope.tales.expressions import LazyExpr
        expr = self.engine.compile('lazy: b')
        self.assertIsInstance(expr, LazyExpr)
        self.assertEqual(repr(expr), "lazy:'b'")
        lazy = expr(self.context)
        self.assertIsInstance(lazy, LazyWrapper)

        first_result = lazy()
        second_result = lazy()
        self.assertIs(first_result, second_result)

    def test_not(self):
        # self.context is a Data object, not a real
        # zope.tales.tales.Context object, and as such
        # it doesn't define the evaluateBoolean function that
        # not expressions need. Add it locally to avoid disturbing
        # other tests.
        def evaluateBoolean(expr):
            return bool(expr(self.context))
        self.context.evaluateBoolean = evaluateBoolean
        self._check_evals_to('not:exists:x', 0)
        expr = self._check_evals_to('not:exists:v_42', 1)
        self.assertEqual("<NotExpr 'exists:v_42'>", repr(expr))

    def test_bad_initial_name_subexpr(self):
        self._check_subexpr_raises_compiler_error(
            '123',
            "Invalid variable name"
        )


class FunctionTests(ExpressionTestBase):

    def setUp(self):
        ExpressionTestBase.setUp(self)

        # a test namespace
        @implementer(ITALESFunctionNamespace)
        class TestNameSpace(object):

            def __init__(self, context):
                self.context = context

            def setEngine(self, engine):
                self._engine = engine

            def engine(self):
                return self._engine

            def upper(self):
                return str(self.context).upper()

            def __getitem__(self, key):
                if key == 'jump':
                    return self.context._d
                raise KeyError(key)

        self.TestNameSpace = TestNameSpace
        self.engine.registerFunctionNamespace('namespace', self.TestNameSpace)
        self.engine.registerFunctionNamespace('not_callable_ns', None)

    ## framework-ish tests

    def testSetEngine(self):
        expr = self.engine.compile('adapterTest/namespace:engine')
        self.assertEqual(expr(self.context), self.context)

    def testGetFunctionNamespace(self):
        self.assertEqual(
            self.engine.getFunctionNamespace('namespace'),
            self.TestNameSpace
        )

    def testGetFunctionNamespaceBadNamespace(self):
        self.assertRaises(KeyError,
                          self.engine.getFunctionNamespace,
                          'badnamespace')

    ## compile time tests

    def testBadNamespace(self):
        # namespace doesn't exist
        self._check_raises_compiler_error(
            'adapterTest/badnamespace:title',
            'Unknown namespace "badnamespace"')

    def testBadInitialNamespace(self):
        # first segment in a path must not have modifier
        self._check_raises_compiler_error(
            'namespace:title',
            'Unrecognized expression type "namespace"')

        # In an ideal world there would be another test here to test
        # that a nicer error was raised when you tried to use
        # something like:
        # standard:namespace:upper
        # ...as a path.
        # However, the compilation stage of PathExpr currently
        # allows any expression type to be nested, so something like:
        # standard:standard:context/attribute
        # ...will work fine.
        # When that is changed so that only expression types which
        # should be nested are nestable, then the additional test
        # should be added here.

    def test_bad_initial_namespace_subpath(self):
        self._check_subexpr_raises_compiler_error(
            'namespace:title',
            "Namespace function specified in first subpath element")

    def testInvalidNamespaceName(self):
        self._check_raises_compiler_error(
            'adapterTest/1foo:bar',
            'Invalid namespace name "1foo"')

    def testBadFunction(self):
        # namespace is fine, adapter is not defined
        expr = self.engine.compile('adapterTest/namespace:title')
        with self.assertRaises(KeyError) as exc:
            expr(self.context)

        e = exc.exception
        self.assertEqual(e.args[0], 'title')

    ## runtime tests

    def testNormalFunction(self):
        expr = self.engine.compile('adapterTest/namespace:upper')
        self.assertEqual(expr(self.context), 'YIKES')

    def testFunctionOnFunction(self):
        expr = self.engine.compile('adapterTest/namespace:jump/namespace:upper')
        self.assertEqual(expr(self.context), 'XANDER')

    def testPathOnFunction(self):
        expr = self.engine.compile('adapterTest/namespace:jump/y/z')
        self._check_evals_to(expr, self.context.vars['x'].y.z)

    def test_path_through_non_callable_nampspace(self):
        expr = self.engine.compile('adapterTest/not_callable_ns:nope')
        with self.assertRaisesRegexp(ValueError,
                                     'None'):
            expr(self.context)

class TestSimpleModuleImporter(unittest.TestCase):

    def _makeOne(self):
        from zope.tales.expressions import SimpleModuleImporter
        return SimpleModuleImporter()

    def test_simple(self):
        imp = self._makeOne()
        import os
        import os.path
        self.assertIs(os, imp['os'])
        self.assertIs(os.path, imp['os.path'])

    def test_no_such_toplevel_possible(self):
        with self.assertRaises(ImportError):
            self._makeOne()['this cannot exist']


    def test_no_such_submodule_not_package(self):
        with self.assertRaises(ImportError):
            self._makeOne()['zope.tales.tests.test_expressions.submodule']

    def test_no_such_submodule_package(self):
        with self.assertRaises(ImportError):
            self._makeOne()['zope.tales.tests.submodule']
