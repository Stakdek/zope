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
"""TALES Tests
"""
from doctest import DocTestSuite
import unittest
import re

import six
from zope.tales import tales
from zope.tales.tests.simpleexpr import SimpleExpr
from zope.testing import renormalizing


class TestIterator(unittest.TestCase):

    def testIterator0(self):
        # Test sample Iterator class
        context = Harness(self)
        it = tales.Iterator('name', (), context)
        self.assertTrue(not next(it), "Empty iterator")
        context._complete_()

    def testIterator1(self):
        # Test sample Iterator class
        context = Harness(self)
        it = tales.Iterator('name', (1,), context)
        context._assert_('setLocal', 'name', 1)
        self.assertTrue(next(it) and not next(it), "Single-element iterator")
        context._complete_()

    def testIterator2(self):
        # Test sample Iterator class
        context = Harness(self)
        it = tales.Iterator('text', 'text', context)
        for c in 'text':
            context._assert_('setLocal', 'text', c)
        for c in 'text':
            self.assertTrue(next(it), "Multi-element iterator")
        self.assertTrue(not next(it), "Multi-element iterator")
        context._complete_()

class TALESTests(unittest.TestCase):

    def testRegisterType(self):
        # Test expression type registration
        e = tales.ExpressionEngine()
        e.registerType('simple', SimpleExpr)
        self.assertEqual(e.getTypes()['simple'], SimpleExpr)

    def testRegisterTypeUnique(self):
        # Test expression type registration uniqueness
        e = tales.ExpressionEngine()
        e.registerType('simple', SimpleExpr)
        try:
            e.registerType('simple', SimpleExpr)
        except tales.RegistrationError:
            pass
        else:
            self.fail("Duplicate registration accepted.")

    def testRegisterTypeNameConstraints(self):
        # Test constraints on expression type names
        e = tales.ExpressionEngine()
        for name in '1A', 'A!', 'AB ':
            try:
                e.registerType(name, SimpleExpr)
            except tales.RegistrationError:
                pass
            else:
                self.fail('Invalid type name "%s" accepted.' % name)

    def testCompile(self):
        # Test expression compilation
        e = tales.ExpressionEngine()
        e.registerType('simple', SimpleExpr)
        ce = e.compile('simple:x')
        self.assertEqual(ce(None), ('simple', 'x'), (
            'Improperly compiled expression %s.' % repr(ce)))

    def testGetContext(self):
        # Test Context creation
        tales.ExpressionEngine().getContext()
        tales.ExpressionEngine().getContext(v=1)
        tales.ExpressionEngine().getContext(x=1, y=2)

    def getContext(self, **kws):
        e = tales.ExpressionEngine()
        e.registerType('simple', SimpleExpr)
        return e.getContext(*(), **kws)

    def testContext_evaluate(self):
        # Test use of Context
        se = self.getContext().evaluate('simple:x')
        self.assertEqual(se, ('simple', 'x'), (
            'Improperly evaluated expression %s.' % repr(se)))

    def testContext_evaluateText(self):
        # Test use of Context
        se = self.getContext().evaluateText('simple:x')
        self.assertTrue(isinstance(se, six.text_type))
        self.assertEqual(se, "('simple', 'x')")

    def test_context_createErrorInfo(self):
        ei = self.getContext().createErrorInfo(self, (0, 0))
        self.assertEqual(ei.type, self)
        self.assertEqual(ei.value, None)

        e = Exception()
        ei = self.getContext().createErrorInfo(e, (0, 0))
        self.assertEqual(ei.type, Exception)
        self.assertEqual(ei.value, e)


    def testVariables(self):
        # Test variables
        ctxt = self.getContext()
        ctxt.beginScope()
        ctxt.setLocal('v1', 1)
        ctxt.setLocal('v2', 2)

        c = ctxt.vars
        self.assertEqual(c['v1'], 1, 'Variable "v1"')

        ctxt.beginScope()
        ctxt.setLocal('v1', 3)
        ctxt.setGlobal('g', 1)

        c = ctxt.vars
        self.assertEqual(c['v1'], 3, 'Inner scope')
        self.assertEqual(c['v2'], 2, 'Outer scope')
        self.assertEqual(c['g'], 1, 'Global')

        ctxt.endScope()

        c = ctxt.vars
        self.assertEqual(c['v1'], 1, "Uncovered local")
        self.assertEqual(c['g'], 1, "Global from inner scope")

        ctxt.endScope()

class TestExpressionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = tales.ExpressionEngine()

    def test_register_invalid_name(self):
        with self.assertRaisesRegexp(tales.RegistrationError,
                                     "Invalid base name"):
            self.engine.registerBaseName('123', None)

    def test_register_duplicate_name(self):
        self.engine.registerBaseName('abc', 123)
        with self.assertRaisesRegexp(tales.RegistrationError,
                                     "Multiple registrations"):
            self.engine.registerBaseName('abc', None)

        self.assertEqual({'abc': 123}, self.engine.getBaseNames())

    def test_getContext(self):
        contexts = {}
        ctx = self.engine.getContext(contexts)
        self.assertIs(ctx.contexts, contexts)

        ctx = self.engine.getContext(b=2, c=3)
        self.assertEqual(ctx.contexts['b'], 2)
        self.assertEqual(ctx.contexts['c'], 3)

        contexts = {'a': 1, 'c': 1}
        ctx = self.engine.getContext(contexts, b=2, c=3)
        self.assertEqual(ctx.contexts['a'], 1)
        self.assertEqual(ctx.contexts['b'], 2)
        self.assertEqual(ctx.contexts['c'], 1)

class TestContext(unittest.TestCase):

    def setUp(self):
        from zope.tales.engine import Engine
        self.engine = Engine
        self.context = tales.Context(self.engine, {})

    def test_setRepeat_false(self):
        self.context.vars['it'] = ()
        self.context.beginScope()
        self.context.setRepeat('name', 'it')
        self.assertNotIn('name', self.context.repeat_vars)

    def test_endScope_with_repeat_active(self):
        self.context.vars['it'] = [1, 2, 3]
        self.context.vars['it2'] = [1, 2, 3]
        self.context.beginScope()
        self.context.setRepeat('name', 'it')
        # shadow it
        self.context.setRepeat('name', 'it2')
        self.assertIn('name', self.context.repeat_vars)
        self.context.endScope()
        self.assertNotIn('name', self.context.repeat_vars)

    def test_getValue_simple(self):
        self.context.vars['it'] = 1
        self.assertEqual(self.context.getValue('it'), 1)
        self.assertEqual(self.context.getValue('missing', default=self), self)

    def test_getValue_nested(self):
        self.context.vars['it'] = 1
        self.context.beginScope()
        self.context.vars['it'] = 2
        self.assertEqual(self.context.getValue('it'), 1)

    def test_evaluate_boolean(self):
        # Make sure it always returns a regular bool, no matter
        # what the class returns
        class WithCustomBool(object):

            def __init__(self, value):
                self.value = value

            def __bool__(self):
                return self.value

            __nonzero__ = __bool__

        # On Python 2, you can return only bool or int from __nonzero__
        # Python 3 requires just a bool from __bool__. This is true whether
        # you pass it to the bool builtin on the not operator
        # On both 2 and 3, you cannot subclass bool()
        bool_value = 1 if str is bytes else True
        self.context.vars['it'] = WithCustomBool(bool_value)
        self.assertEqual(bool_value, self.context.evaluate('it').__bool__())
        self.assertIs(True, self.context.evaluateBoolean('it'))

    def test_evaluateText_none(self):
        self.context.vars['it'] = None
        self.assertIsNone(self.context.evaluateText('it'))

    def test_evaluateText_text(self):
        self.context.vars['it'] = u'text'
        self.assertEqual(u'text', self.context.evaluateText("it"))

    def test_traceback_supplement(self):
        import sys
        def raises(self):
            raise Exception()

        self.context.contexts['modules'] = 1
        self.context.setSourceFile("source")
        self.context.setPosition((0, 1))

        try:
            self.context.evaluate(raises)
        except Exception:
            tb = sys.exc_info()[2]

        try:
            supp = tb.tb_next.tb_frame.f_locals['__traceback_supplement__']
        finally:
            del tb

        supp = supp[0](supp[1], supp[2])
        self.assertIs(supp.context, self.context)
        self.assertEqual(supp.source_url, self.context.source_file)
        self.assertEqual(supp.line, 0)
        self.assertEqual(supp.column, 1)
        self.assertEqual(supp.expression, repr(raises))

        info = supp.getInfo()
        # We stripped this info
        self.assertNotIn('modules', info)
        self.assertIn(' - Names', info)

        html_info = supp.getInfo(as_html=True)
        self.assertIn('<b>Names', html_info)

        # And we didn't change the data in the context
        self.assertIn('modules', self.context.contexts)

    def test_translate(self):
        import six
        self.assertIsInstance(self.context.translate(b'abc'), six.text_type)


class Harness(object):
    def __init__(self, testcase):
        self._callstack = []
        self._testcase = testcase

    def _assert_(self, name, *args, **kwargs):
        self._callstack.append((name, args, kwargs))

    def _complete_(self):
        self._testcase.assertEqual(len(self._callstack), 0,
                                   "Harness methods called")

    def __getattr__(self, name):
        return HarnessMethod(self, name)

class HarnessMethod(object):

    def __init__(self, harness, name):
        self._harness = harness
        self._name = name

    def __call__(self, *args, **kwargs):
        name = self._name
        self = self._harness

        cs = self._callstack
        self._testcase.assertTrue(
            len(cs),
            'Unexpected harness method call "%s".' % name
        )
        self._testcase.assertEqual(
            cs[0][0], name,
            'Harness method name "%s" called, "%s" expected.' %
            (name, cs[0][0])
        )

        name, aargs, akwargs = self._callstack.pop(0)
        self._testcase.assertEqual(aargs, args, "Harness method arguments")
        self._testcase.assertEqual(akwargs, kwargs,
                                   "Harness method keyword args")


def test_suite():
    checker = renormalizing.RENormalizing(
        [(re.compile(r"object of type 'MyIter' has no len\(\)"),
          r"len() of unsized object"),
        ]
    )
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTest(DocTestSuite("zope.tales.tales",
                               checker=checker))
    return suite
