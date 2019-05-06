##############################################################################
#
# Copyright (c) 20!2 Zope Foundation and Contributors.
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
"""Test zope.configuration.fields.
"""
import unittest

# pylint:disable=protected-access

class _ConformsToIFromUnicode(object):

    def _getTargetClass(self):
        raise NotImplementedError

    def _makeOne(self, *args, **kw):
        raise NotImplementedError

    def test_class_conforms_to_IFromUnicode(self):
        from zope.interface.verify import verifyClass
        from zope.schema.interfaces import IFromUnicode
        verifyClass(IFromUnicode, self._getTargetClass())

    def test_instance_conforms_to_IFromUnicode(self):
        from zope.interface.verify import verifyObject
        from zope.schema.interfaces import IFromUnicode
        verifyObject(IFromUnicode, self._makeOne())


class GlobalObjectTests(unittest.TestCase, _ConformsToIFromUnicode):

    def _getTargetClass(self):
        from zope.configuration.fields import GlobalObject
        return GlobalObject

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test__validate_wo_value_type(self):
        go = self._makeOne(value_type=None)
        for value in [0, 0.0, (), [], set(), frozenset(), u'', b'']:
            go._validate(value) #noraise

    def test__validate_w_value_type(self):
        from zope.schema import Text
        from zope.schema.interfaces import WrongType
        go = self._makeOne(value_type=Text())
        go.validate(u'')
        for value in [0, 0.0, (), [], set(), frozenset(), b'']:
            with self.assertRaises(WrongType):
                go._validate(value)

    def test_fromUnicode_w_star_and_extra_ws(self):
        go = self._makeOne()
        self.assertEqual(go.fromUnicode(' * '), None)

    def test_fromUnicode_w_resolve_fails(self):
        from zope.schema import ValidationError
        from zope.configuration.config import ConfigurationError
        class Context(object):
            _resolved = None
            def resolve(self, name):
                self._resolved = name
                raise ConfigurationError()
        go = self._makeOne()
        context = Context()
        bound = go.bind(context)
        with self.assertRaises(ValidationError) as exc:
            bound.fromUnicode('tried')
        self.assertEqual(context._resolved, 'tried')
        ex = exc.exception
        self.assertIs(ex.field, bound)
        self.assertEqual(ex.value, 'tried')

    def test_fromUnicode_w_resolve_success(self):
        _target = object()
        class Context(object):
            _resolved = None
            def resolve(self, name):
                self._resolved = name
                return _target
        go = self._makeOne()
        context = Context()
        bound = go.bind(context)
        found = bound.fromUnicode('tried')
        self.assertIs(found, _target)
        self.assertEqual(context._resolved, 'tried')

    def test_fromUnicode_w_resolve_dots(self):
        _target = object()
        class Context(object):
            _resolved = None
            def resolve(self, name):
                self._resolved = name
                return _target
        go = self._makeOne()
        context = Context()
        bound = go.bind(context)
        for name in (
                '.',
                '..',
                '.foo',
                '..foo.bar'
        ):
            __traceback_info__ = name
            found = bound.fromUnicode(name)
            self.assertIs(found, _target)
            self.assertEqual(context._resolved, name)

    def test_fromUnicode_w_resolve_but_validation_fails(self):
        from zope.schema import Text
        from zope.schema import ValidationError
        _target = object()
        class Context(object):
            _resolved = None
            def resolve(self, name):
                self._resolved = name
                return _target
        go = self._makeOne(value_type=Text())
        context = Context()
        bound = go.bind(context)
        with self.assertRaises(ValidationError):
            bound.fromUnicode('tried')
        self.assertEqual(context._resolved, 'tried')

    def test_fromUnicode_rejects_slash(self):
        from zope.schema import ValidationError
        _target = object()
        field = self._makeOne()
        with self.assertRaises(ValidationError) as exc:
            field.fromUnicode('foo/bar')
        ex = exc.exception
        self.assertIs(ex.field, field)
        self.assertEqual(ex.value, 'foo/bar')


class GlobalInterfaceTests(unittest.TestCase, _ConformsToIFromUnicode):

    def _getTargetClass(self):
        from zope.configuration.fields import GlobalInterface
        return GlobalInterface

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        from zope.schema import InterfaceField
        gi = self._makeOne()
        self.assertIsInstance(gi.value_type, InterfaceField)

class TokensTests(unittest.TestCase, _ConformsToIFromUnicode):

    def _getTargetClass(self):
        from zope.configuration.fields import Tokens
        return Tokens

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_fromUnicode_empty(self):
        tok = self._makeOne()
        self.assertEqual(tok.fromUnicode(''), [])

    def test_fromUnicode_strips_ws(self):
        from zope.schema import Text
        tok = self._makeOne(value_type=Text())
        self.assertEqual(tok.fromUnicode(u' one two three '),
                         [u'one', u'two', u'three'])

    def test_fromUnicode_invalid(self):
        from zope.schema import Int
        from zope.configuration.interfaces import InvalidToken
        tok = self._makeOne(value_type=Int(min=0))
        with self.assertRaises(InvalidToken) as exc:
            tok.fromUnicode(u' 1 -1 3 ')

        ex = exc.exception
        self.assertIs(ex.field, tok)
        self.assertEqual(ex.value, '-1')


class PathTests(unittest.TestCase, _ConformsToIFromUnicode):

    def _getTargetClass(self):
        from zope.configuration.fields import Path
        return Path

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_fromUnicode_absolute(self):
        import os
        path = self._makeOne()
        self.assertEqual(path.fromUnicode('/'), os.path.normpath('/'))

    def test_fromUnicode_relative(self):
        class Context(object):
            _pathed = None
            def path(self, value):
                self._pathed = value
                return '/hard/coded'
        context = Context()
        path = self._makeOne()
        bound = path.bind(context)
        self.assertEqual(bound.fromUnicode('relative/path'), '/hard/coded')
        self.assertEqual(context._pathed, 'relative/path')


class BoolTests(unittest.TestCase, _ConformsToIFromUnicode):

    def _getTargetClass(self):
        from zope.configuration.fields import Bool
        return Bool

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_fromUnicode_w_true_values(self):
        values = ['1', 'true', 'yes', 't', 'y']
        values += [x.upper() for x in values]
        bo = self._makeOne()
        for value in values:
            self.assertEqual(bo.fromUnicode(value), True)

    def test_fromUnicode_w_false_values(self):
        values = ['0', 'false', 'no', 'f', 'n']
        values += [x.upper() for x in values]
        bo = self._makeOne()
        for value in values:
            self.assertEqual(bo.fromUnicode(value), False)

    def test_fromUnicode_w_invalid(self):
        from zope.schema.interfaces import InvalidValue
        bo = self._makeOne()
        with self.assertRaises(InvalidValue) as exc:
            bo.fromUnicode('notvalid')
        ex = exc.exception
        self.assertIs(ex.field, bo)
        self.assertEqual(ex.value, 'notvalid')


class MessageIDTests(unittest.TestCase, _ConformsToIFromUnicode):

    def _getTargetClass(self):
        from zope.configuration.fields import MessageID
        return MessageID

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeContext(self, domain='testing_domain'):
        class Info(object):
            file = 'test_file'
            line = 42
        class Context(object):
            i18n_domain = domain
            def __init__(self):
                self.i18n_strings = {}
                self.info = Info()
        return Context()

    def test_wo_domain(self):
        import warnings
        mid = self._makeOne()
        context = self._makeContext(None)
        bound = mid.bind(context)
        with warnings.catch_warnings(record=True) as log:
            msgid = bound.fromUnicode(u'testing')
        self.assertEqual(len(log), 1)
        self.assertTrue(str(log[0].message).startswith(
            'You did not specify an i18n translation domain'))
        self.assertEqual(msgid, 'testing')
        self.assertEqual(msgid.default, None)
        self.assertEqual(msgid.domain, 'untranslated')
        self.assertEqual(context.i18n_strings,
                         {'untranslated': {'testing': [('test_file', 42)]}})

    def test_w_empty_id(self):
        import warnings
        mid = self._makeOne()
        context = self._makeContext()
        bound = mid.bind(context)
        with warnings.catch_warnings(record=True) as log:
            msgid = bound.fromUnicode(u'[] testing')
        self.assertEqual(len(log), 0)
        self.assertEqual(msgid, 'testing')
        self.assertEqual(msgid.default, None)
        self.assertEqual(msgid.domain, 'testing_domain')
        self.assertEqual(context.i18n_strings,
                         {'testing_domain': {'testing': [('test_file', 42)]}})

    def test_w_id_and_default(self):
        import warnings
        mid = self._makeOne()
        context = self._makeContext()
        bound = mid.bind(context)
        with warnings.catch_warnings(record=True) as log:
            msgid = bound.fromUnicode(u'[testing] default')
        self.assertEqual(len(log), 0)
        self.assertEqual(msgid, 'testing')
        self.assertEqual(msgid.default, 'default')
        self.assertEqual(msgid.domain, 'testing_domain')
        self.assertEqual(context.i18n_strings,
                         {'testing_domain': {'testing': [('test_file', 42)]}})

    def test_domain_decodes_bytes(self):
        mid = self._makeOne()
        context = self._makeContext(domain=b'domain')
        bound = mid.bind(context)
        msgid = bound.fromUnicode(u'msgid')
        self.assertIsInstance(msgid.domain, str)
        self.assertEqual(msgid.domain, 'domain')

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
