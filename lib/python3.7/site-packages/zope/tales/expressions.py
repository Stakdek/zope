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
Basic Page Template expression types.

Expression objects are created by the :class:`.ExpressionEngine`
(they must have previously been registered with
:func:`~zope.tales.tales.ExpressionEngine.registerType`).  The expression object itself
is a callable object taking one argument, *econtext*, which is the local
expression namespace.

"""
import re
import sys
import types

import six

from zope.interface import implementer
from zope.tales.tales import _valid_name, _parse_expr, NAME_RE, Undefined
from zope.tales.interfaces import ITALESExpression, ITALESFunctionNamespace

Undefs = (Undefined, AttributeError, LookupError, TypeError)

_marker = object()
namespace_re = re.compile(r'(\w+):(.+)')

PY2 = sys.version_info[0] == 2

def simpleTraverse(object, path_items, econtext):
    """Traverses a sequence of names, first trying attributes then items.
    """

    for name in path_items:
        next = getattr(object, name, _marker)
        if next is not _marker:
            object = next
        elif hasattr(object, '__getitem__'):
            object = object[name]
        else:
            # Allow AttributeError to propagate
            object = getattr(object, name)
    return object


class SubPathExpr(object):
    """
    Implementation of a single path expression.
    """

    def __init__(self, path, traverser, engine):
        self._traverser = traverser
        self._engine = engine

        # Parse path
        compiledpath = []
        currentpath = []
        for element in str(path).strip().split('/'):
            if not element:
                raise engine.getCompilerError()(
                    'Path element may not be empty in %r' % path)
            if element.startswith('?'):
                if currentpath:
                    compiledpath.append(tuple(currentpath))
                    currentpath = []
                if not _valid_name(element[1:]):
                    raise engine.getCompilerError()(
                        'Invalid variable name "%s"' % element[1:])
                compiledpath.append(element[1:])
            else:
                match = namespace_re.match(element)
                if match:
                    if currentpath:
                        compiledpath.append(tuple(currentpath))
                        currentpath = []
                    namespace, functionname = match.groups()
                    if not _valid_name(namespace):
                        raise engine.getCompilerError()(
                            'Invalid namespace name "%s"' % namespace)
                    try:
                        compiledpath.append(
                            self._engine.getFunctionNamespace(namespace))
                    except KeyError:
                        raise engine.getCompilerError()(
                            'Unknown namespace "%s"' % namespace)
                    currentpath.append(functionname)
                else:
                    currentpath.append(element)

        if currentpath:
            compiledpath.append(tuple(currentpath))

        first = compiledpath[0]

        if callable(first):
            # check for initial function
            raise engine.getCompilerError()(
                'Namespace function specified in first subpath element')
        elif isinstance(first, six.string_types):
            # check for initial ?
            raise engine.getCompilerError()(
                'Dynamic name specified in first subpath element')

        base = first[0]
        if base and not _valid_name(base):
            raise engine.getCompilerError()(
                'Invalid variable name "%s"' % element)
        self._base = base
        compiledpath[0] = first[1:]
        self._compiled_path = tuple(compiledpath)

    def _eval(self, econtext,
              isinstance=isinstance):
        vars = econtext.vars

        compiled_path = self._compiled_path

        base = self._base
        if base == 'CONTEXTS' or not base:  # Special base name
            ob = econtext.contexts
        else:
            ob = vars[base]
        if isinstance(ob, DeferWrapper):
            ob = ob()

        for element in compiled_path:
            if isinstance(element, tuple):
                ob = self._traverser(ob, element, econtext)
            elif isinstance(element, six.string_types):
                val = vars[element]
                # If the value isn't a string, assume it's a sequence
                # of path names.
                if isinstance(val, six.string_types):
                    val = (val,)
                ob = self._traverser(ob, val, econtext)
            elif callable(element):
                ob = element(ob)
                # TODO: Once we have n-ary adapters, use them.
                if ITALESFunctionNamespace.providedBy(ob):
                    ob.setEngine(econtext)
            else:
                raise ValueError(repr(element))
        return ob


@implementer(ITALESExpression)
class PathExpr(object):
    """
    One or more :class:`subpath expressions <SubPathExpr>`, separated
    by ``|``.
    """

    # _default_type_names contains the expression type names this
    # class is usually registered for.
    _default_type_names = (
        'standard',
        'path',
        'exists',
        'nocall',
        )

    def __init__(self, name, expr, engine, traverser=simpleTraverse):
        self._s = expr
        self._name = name
        self._hybrid = False
        paths = expr.split('|')
        self._subexprs = []
        add = self._subexprs.append
        for i, path in enumerate(paths):
            path = path.lstrip()
            if _parse_expr(path):
                # This part is the start of another expression type,
                # so glue it back together and compile it.
                add(engine.compile('|'.join(paths[i:]).lstrip()))
                self._hybrid = True
                break
            add(SubPathExpr(path, traverser, engine)._eval)

    def _exists(self, econtext):
        for expr in self._subexprs:
            try:
                expr(econtext)
            except Undefs:
                pass
            else:
                return 1
        return 0

    def _eval(self, econtext):
        for expr in self._subexprs[:-1]:
            # Try all but the last subexpression, skipping undefined ones.
            try:
                ob = expr(econtext)
            except Undefs:
                pass
            else:
                break
        else:
            # On the last subexpression allow exceptions through, and
            # don't autocall if the expression was not a subpath.
            ob = self._subexprs[-1](econtext)
            if self._hybrid:
                return ob

        if self._name == 'nocall':
            return ob

        # Call the object if it is callable.  Note that checking for
        # callable() isn't safe because the object might be security
        # proxied (and security proxies report themselves callable, no
        # matter what the underlying object is).  We therefore check
        # for the __call__ attribute, but not with hasattr as that
        # eats babies, err, exceptions.  In addition to that, we
        # support calling old style classes which don't have a
        # __call__.
        if getattr(ob, '__call__', _marker) is not _marker:
            return ob()
        return ob() if PY2 and isinstance(ob, types.ClassType) else ob

    def __call__(self, econtext):
        if self._name == 'exists':
            return self._exists(econtext)
        return self._eval(econtext)

    def __str__(self):
        return '%s expression (%s)' % (self._name, repr(self._s))

    def __repr__(self):
        return '<PathExpr %s:%s>' % (self._name, repr(self._s))



_interp = re.compile(
    r'\$(%(n)s)|\${(%(n)s(?:/[^}|]*)*(?:\|%(n)s(?:/[^}|]*)*)*)}'
    % {'n': NAME_RE})

@implementer(ITALESExpression)
class StringExpr(object):
    """
    An expression that produces a string.

    Sub-sequences of the string that begin with ``$`` are
    interpreted as path expressions to evaluate.
    """

    def __init__(self, name, expr, engine):
        self._s = expr
        if '%' in expr:
            expr = expr.replace('%', '%%')
        self._vars = vars = []
        if '$' in expr:
            # Use whatever expr type is registered as "path".
            path_type = engine.getTypes()['path']
            parts = []
            for exp in expr.split('$$'):
                if parts: parts.append('$')
                m = _interp.search(exp)
                while m is not None:
                    parts.append(exp[:m.start()])
                    parts.append('%s')
                    vars.append(path_type(
                        'path', m.group(1) or m.group(2), engine))
                    exp = exp[m.end():]
                    m = _interp.search(exp)
                if '$' in exp:
                    raise engine.getCompilerError()(
                        '$ must be doubled or followed by a simple path')
                parts.append(exp)
            expr = ''.join(parts)
        self._expr = expr

    def __call__(self, econtext):
        vvals = []
        for var in self._vars:
            v = var(econtext)
            vvals.append(v)
        return self._expr % tuple(vvals)

    def __str__(self):
        return 'string expression (%s)' % repr(self._s)

    def __repr__(self):
        return '<StringExpr %s>' % repr(self._s)


@implementer(ITALESExpression)
class NotExpr(object):
    """
    An expression that negates the boolean value
    of its sub-expression.
    """

    def __init__(self, name, expr, engine):
        self._s = expr = expr.lstrip()
        self._c = engine.compile(expr)

    def __call__(self, econtext):
        return int(not econtext.evaluateBoolean(self._c))

    def __repr__(self):
        return '<NotExpr %s>' % repr(self._s)


class DeferWrapper(object):
    def __init__(self, expr, econtext):
        self._expr = expr
        self._econtext = econtext

    def __str__(self):
        return str(self())

    def __call__(self):
        return self._expr(self._econtext)


@implementer(ITALESExpression)
class DeferExpr(object):
    """
    An expression that will defer evaluation of the sub-expression
    until necessary, preserving the execution context it was created
    with.

    This is useful in ``tal:define`` expressions::

       <div tal:define="thing defer:some/path">
         ...
         <!-- some/path is only evaluated if condition is true -->
         <span tal:condition="condition" tal:content="thing"/>
       </div>
    """

    def __init__(self, name, expr, compiler):
        self._s = expr = expr.lstrip()
        self._c = compiler.compile(expr)

    def __call__(self, econtext):
        return DeferWrapper(self._c, econtext)

    def __repr__(self):
        return '<DeferExpr %s>' % repr(self._s)


class LazyWrapper(DeferWrapper):
    """Wrapper for lazy: expression
    """
    _result = _marker

    def __init__(self, expr, econtext):
        DeferWrapper.__init__(self, expr, econtext)

    def __call__(self):
        r = self._result
        if r is _marker:
            self._result = r = self._expr(self._econtext)
        return r

class LazyExpr(DeferExpr):
    """
    An expression that will defer evaluation of its
    sub-expression until the first time it is  necessary.

    This is like :class:`DeferExpr`, but caches the result of
    evaluating the expression.
    """
    def __call__(self, econtext):
        return LazyWrapper(self._c, econtext)

    def __repr__(self):
        return 'lazy:%s' % repr(self._s)


class SimpleModuleImporter(object):
    """Minimal module importer with no security."""

    def __getitem__(self, module):
        mod = self._get_toplevel_module(module)
        path = module.split('.')
        for name in path[1:]:
            mod = getattr(mod, name)
        return mod

    def _get_toplevel_module(self, module):
        # This can be overridden to add security proxies.
        return __import__(module)
