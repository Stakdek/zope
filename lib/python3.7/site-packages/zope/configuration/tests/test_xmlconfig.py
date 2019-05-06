##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Test zope.configuration.xmlconfig.
"""
import unittest


NS = u'ns'
FOO = u'foo'
XXX = u'xxx'
SPLAT = u'splat'
SPLATV = u'splatv'
A = u'a'
AVALUE = u'avalue'
B = u'b'
BVALUE = u'bvalue'

# pylint:disable=protected-access

class ZopeXMLConfigurationErrorTests(unittest.TestCase):
    maxDiff = None

    def _getTargetClass(self):
        from zope.configuration.xmlconfig import ZopeXMLConfigurationError
        return ZopeXMLConfigurationError

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test___str___uses_repr_of_info(self):
        zxce = self._makeOne('info', Exception('value'))
        self.assertEqual(
            str(zxce),
            "'info'\n    Exception: value"
        )



class ZopeSAXParseExceptionTests(unittest.TestCase):
    maxDiff = None

    def _getTargetClass(self):
        from zope.configuration.xmlconfig import ZopeSAXParseException
        return ZopeSAXParseException

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test___str___not_a_sax_error(self):
        zxce = self._makeOne("info", Exception('Not a SAX error'))
        self.assertEqual(
            str(zxce),
            "info\n    Exception: Not a SAX error")

    def test___str___w_a_sax_error(self):
        zxce = self._makeOne("info", Exception('filename.xml:24:32:WAAA'))
        self.assertEqual(
            str(zxce),
            'info\n    Exception: filename.xml:24:32:WAAA')


class ParserInfoTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.configuration.xmlconfig import ParserInfo
        return ParserInfo

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test___repr___w_eline_ecolumn_match_line_column(self):
        pi = self._makeOne('filename.xml', 24, 32)
        pi.end(24, 32)
        self.assertEqual(repr(pi), 'File "filename.xml", line 24.32')

    def test___repr___w_eline_ecolumn_dont_match_line_column(self):
        pi = self._makeOne('filename.xml', 24, 32)
        pi.end(33, 21)
        self.assertEqual(repr(pi), 'File "filename.xml", line 24.32-33.21')

    def test___str___w_eline_ecolumn_match_line_column(self):
        pi = self._makeOne('filename.xml', 24, 32)
        pi.end(24, 32)
        self.assertEqual(str(pi), 'File "filename.xml", line 24.32')

    def test___str___w_eline_ecolumn_dont_match_line_column_bad_file(self):
        pi = self._makeOne('/path/to/nonesuch.xml', 24, 32)
        pi.end(33, 21)
        self.assertEqual(str(pi),
                         'File "/path/to/nonesuch.xml", line 24.32-33.21\n'
                         '  Could not read source.')

    def test___str___w_good_file(self):
        pi = self._makeOne('tests//sample.zcml', 3, 2)
        pi.end(3, 57)
        self.assertEqual(
            str(pi),
            'File "tests//sample.zcml", line 3.2-3.57\n'
            '    <directives namespace="http://namespaces.zope.org/zope">')


class ConfigurationHandlerTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.configuration.xmlconfig import ConfigurationHandler
        return ConfigurationHandler

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        context = FauxContext()
        handler = self._makeOne(context)
        self.assertTrue(handler.context is context)
        self.assertFalse(handler.testing)
        self.assertEqual(handler.ignore_depth, 0)

    def test_ctor_explicit(self):
        context = FauxContext()
        handler = self._makeOne(context, True)
        self.assertTrue(handler.context is context)
        self.assertTrue(handler.testing)
        self.assertEqual(handler.ignore_depth, 0)
        self.assertTrue(handler.locator is None)

    def test_setDocumentLocator(self):
        context = FauxContext()
        locator = FauxLocator('tests//sample.zcml', 1, 1)
        handler = self._makeOne(context, True)
        handler.setDocumentLocator(locator)
        self.assertTrue(handler.locator is locator)

    def test_startElementNS_w_zcml_condition_failing(self):
        from zope.configuration.xmlconfig import ZCML_CONDITION
        context = FauxContext()
        handler = self._makeOne(context, True)
        # No locator set:  we won't need it, due to a failed condition.
        handler.startElementNS((NS, FOO), FOO,
                               {ZCML_CONDITION: 'have nonesuch',
                                (None, A): AVALUE,
                                (None, B): BVALUE,
                               })
        self.assertEqual(handler.ignore_depth, 1)

    def test_startElementNS_w_ignore_depth_already_set(self):
        context = FauxContext()
        handler = self._makeOne(context, True)
        handler.ignore_depth = 1
        # No locator set:  we won't need it, as an ancestor had a
        # failed condition.
        handler.startElementNS((NS, FOO), FOO,
                               {(XXX, SPLAT): SPLATV,
                                (None, A): AVALUE,
                                (None, B): BVALUE,
                               })
        self.assertEqual(handler.ignore_depth, 2)

    def _check_elementNS_context_raises(self, raises, catches,
                                        testing=False,
                                        meth='endElementNS',
                                        meth_args=((NS, FOO), FOO)):
        class ErrorContext(FauxContext):
            def end(self, *args):
                raise raises("xxx")
            begin = end
        class Info(object):
            _line = _col = None
            def end(self, line, col):
                self._line, self._col = line, col
        context = ErrorContext()
        info = Info()
        context.setInfo(info)
        locator = FauxLocator('tests//sample.zcml', 1, 1)
        handler = self._makeOne(context, testing)
        handler.setDocumentLocator(locator)
        locator.line, locator.column = 7, 16
        meth = getattr(handler, meth)
        with self.assertRaises(catches) as exc:
            meth(*meth_args)
        return exc.exception, info

    def _check_startElementNS_context_begin_raises(self, raises, catches, testing=False):
        return self._check_elementNS_context_raises(
            raises, catches, testing,
            meth='startElementNS',
            meth_args=((NS, FOO),
                       FOO,
                       {(XXX, SPLAT): SPLATV,
                        (None, A): AVALUE,
                        (None, B): BVALUE,
                       })
        )

    def test_startElementNS_context_begin_raises_wo_testing(self):
        from zope.configuration.xmlconfig import ZopeXMLConfigurationError
        raised, _ = self._check_startElementNS_context_begin_raises(AttributeError,
                                                                    ZopeXMLConfigurationError)
        info = raised.info
        self.assertEqual(info.file, 'tests//sample.zcml')
        self.assertEqual(info.line, 7)
        self.assertEqual(info.column, 16)

    def test_startElementNS_context_begin_raises_w_testing(self):
        self._check_startElementNS_context_begin_raises(AttributeError,
                                                        AttributeError,
                                                        True)

    def test_startElementNS_context_begin_raises_BaseException(self):
        class Bex(BaseException):
            pass
        self._check_startElementNS_context_begin_raises(Bex,
                                                        Bex)


    def test_startElementNS_normal(self):
        # Integration test of startElementNS / endElementNS pair.
        context = FauxContext()
        locator = FauxLocator('tests//sample.zcml', 1, 1)
        handler = self._makeOne(context)
        handler.setDocumentLocator(locator)

        handler.startElementNS((NS, FOO), FOO,
                               {(XXX, SPLAT): SPLATV,
                                (None, A): AVALUE,
                                (None, B): BVALUE,
                               })
        self.assertEqual(context.info.file, 'tests//sample.zcml')
        self.assertEqual(context.info.line, 1)
        self.assertEqual(context.info.column, 1)
        self.assertEqual(context.begin_args,
                         ((NS, FOO),
                          {'a': AVALUE, 'b': BVALUE}))
        self.assertFalse(context._end_called)

    def test_endElementNS_w_ignore_depth_already_set(self):
        context = FauxContext()
        handler = self._makeOne(context, True)
        handler.ignore_depth = 1
        # No locator set:  we won't need it, as we had a
        # failed condition.
        handler.endElementNS((NS, FOO), FOO)
        self.assertEqual(handler.ignore_depth, 0)

    def _check_endElementNS_context_end_raises(self, raises, catches, testing=False):
        return self._check_elementNS_context_raises(raises, catches, testing)

    def test_endElementNS_context_end_raises_wo_testing(self):
        from zope.configuration.xmlconfig import ZopeXMLConfigurationError

        raised, info = self._check_endElementNS_context_end_raises(AttributeError,
                                                                   ZopeXMLConfigurationError)

        self.assertIs(raised.info, info)
        self.assertEqual(raised.info._line, 7)
        self.assertEqual(raised.info._col, 16)

    def test_endElementNS_context_end_raises_w_testing(self):
        _, info = self._check_endElementNS_context_end_raises(AttributeError,
                                                              AttributeError,
                                                              True)
        self.assertEqual(info._line, 7)
        self.assertEqual(info._col, 16)

    def test_endElementNS_context_end_raises_BaseException(self):
        class Bex(BaseException):
            pass
        self._check_endElementNS_context_end_raises(Bex,
                                                    Bex)

    def test_evaluateCondition_w_have_no_args(self):
        context = FauxContext()
        handler = self._makeOne(context)
        with self.assertRaises(ValueError) as exc:
            handler.evaluateCondition('have')
        self.assertEqual(str(exc.exception.args[0]),
                         "Feature name missing: 'have'")

    def test_evaluateCondition_w_not_have_too_many_args(self):
        context = FauxContext()
        handler = self._makeOne(context)
        with self.assertRaises(ValueError) as exc:
            handler.evaluateCondition('not-have a b')
        self.assertEqual(str(exc.exception.args[0]),
                         "Only one feature allowed: 'not-have a b'")

    def test_evaluateCondition_w_have_miss(self):
        context = FauxContext()
        handler = self._makeOne(context)
        self.assertFalse(handler.evaluateCondition('have feature'))

    def test_evaluateCondition_w_have_hit(self):
        context = FauxContext()
        context._features = ('feature',)
        handler = self._makeOne(context)
        self.assertTrue(handler.evaluateCondition('have feature'))

    def test_evaluateCondition_w_not_have_miss(self):
        context = FauxContext()
        context._features = ('feature',)
        handler = self._makeOne(context)
        self.assertFalse(handler.evaluateCondition('not-have feature'))

    def test_evaluateCondition_w_not_have_hit(self):
        context = FauxContext()
        handler = self._makeOne(context)
        self.assertTrue(handler.evaluateCondition('not-have feature'))

    def test_evaluateCondition_w_installed_no_args(self):
        context = FauxContext()
        handler = self._makeOne(context)
        with self.assertRaises(ValueError) as exc:
            handler.evaluateCondition('installed')
        self.assertEqual(str(exc.exception.args[0]),
                         "Package name missing: 'installed'")

    def test_evaluateCondition_w_not_installed_too_many_args(self):
        context = FauxContext()
        handler = self._makeOne(context)
        with self.assertRaises(ValueError) as exc:
            handler.evaluateCondition('not-installed a b')
        self.assertEqual(str(exc.exception.args[0]),
                         "Only one package allowed: 'not-installed a b'")

    def test_evaluateCondition_w_installed_miss(self):
        context = FauxContext()
        handler = self._makeOne(context)
        self.assertFalse(
            handler.evaluateCondition('installed nonsuch.package'))

    def test_evaluateCondition_w_installed_hit(self):
        context = FauxContext()
        handler = self._makeOne(context)
        self.assertTrue(handler.evaluateCondition('installed os'))

    def test_evaluateCondition_w_not_installed_miss(self):
        context = FauxContext()
        handler = self._makeOne(context)
        self.assertFalse(handler.evaluateCondition('not-installed os'))

    def test_evaluateCondition_w_not_installed_hit(self):
        context = FauxContext()
        handler = self._makeOne(context)
        self.assertTrue(
            handler.evaluateCondition('not-installed nonsuch.package'))

    def test_evaluateCondition_w_unknown_verb(self):
        context = FauxContext()
        handler = self._makeOne(context)
        with self.assertRaises(ValueError) as exc:
            handler.evaluateCondition('nonesuch')
        self.assertEqual(str(exc.exception.args[0]),
                         "Invalid ZCML condition: 'nonesuch'")

    def test_endElementNS_normal(self):
        class Info(object):
            _line = _col = None
            def end(self, line, col):
                self._line, self._col = line, col
        context = FauxContext()
        info = Info()
        context.setInfo(info)
        locator = FauxLocator('tests//sample.zcml', 7, 16)
        handler = self._makeOne(context, True)
        handler.setDocumentLocator(locator)
        handler.endElementNS((NS, FOO), FOO)
        self.assertEqual(context.info._line, 7)
        self.assertEqual(context.info._col, 16)
        self.assertTrue(context._end_called)


class Test_processxmlfile(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.xmlconfig import processxmlfile
        return processxmlfile(*args, **kw)

    def test_w_empty_xml(self):
        from io import StringIO
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.xmlconfig import registerCommonDirectives
        from zope.configuration.xmlconfig import ZopeSAXParseException

        context = ConfigurationMachine()
        registerCommonDirectives(context)
        with self.assertRaises(ZopeSAXParseException) as exc:
            self._callFUT(StringIO(), context)
        self.assertEqual(str(exc.exception.evalue),
                         '<string>:1:0: no element found')

    def test_w_valid_xml_fp(self):
        # Integration test, really
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.xmlconfig import registerCommonDirectives
        from zope.configuration.tests.samplepackage import foo

        context = ConfigurationMachine()
        registerCommonDirectives(context)

        with open(path("samplepackage", "configure.zcml")) as file:
            self._callFUT(file, context)
        self.assertEqual(foo.data, [])
        context.execute_actions()
        data = foo.data.pop()
        self.assertEqual(data.args, (('x', (b'blah')), ('y', 0)))
        self.assertEqual(clean_info_path(repr(data.info)),
                         'File "tests/samplepackage/configure.zcml", line 12.2-12.29')
        self.assertEqual(clean_info_path(str(data.info)),
                         'File "tests/samplepackage/configure.zcml", line 12.2-12.29\n'
                         + '    <test:foo x="blah" y="0" />')
        self.assertEqual(data.package, None)
        self.assertEqual(data.basepath, None)


class Test_openInOrPlain(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.xmlconfig import openInOrPlain
        return openInOrPlain(*args, **kw)

    def _makeFilename(self, fn):
        import os
        from zope.configuration.tests.samplepackage import __file__
        return os.path.join(os.path.dirname(__file__), fn)

    def test_file_present(self):
        import os
        with self._callFUT(self._makeFilename('configure.zcml')) as fp:
            self.assertEqual(os.path.basename(fp.name), 'configure.zcml')

    def test_file_missing_but_dot_in_present(self):
        import os
        with self._callFUT(self._makeFilename('foo.zcml')) as fp:
            self.assertEqual(os.path.basename(fp.name), 'foo.zcml.in')

    def test_file_missing_and_dot_in_not_present(self):
        import errno
        with self.assertRaises(IOError) as exc:
            self._callFUT(self._makeFilename('nonesuch.zcml'))
        self.assertEqual(exc.exception.errno, errno.ENOENT)


class Test_include(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.xmlconfig import include
        return include(*args, **kw)

    def test_both_file_and_files_passed(self):
        context = FauxContext()
        with self.assertRaises(ValueError) as exc:
            self._callFUT(
                context, 'tests//sample.zcml', files=['tests/*.zcml'])
        self.assertEqual(str(exc.exception),
                         "Must specify only one of file or files")

    def test_neither_file_nor_files_passed_already_seen(self):
        from zope.configuration import xmlconfig
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.xmlconfig import registerCommonDirectives
        from zope.configuration.tests import samplepackage
        context = ConfigurationMachine()
        registerCommonDirectives(context)
        context.package = samplepackage
        fqn = _packageFile(samplepackage, 'configure.zcml')
        context._seen_files.add(fqn)
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            self._callFUT(context) #skips
        self.assertEqual(len(logger.debugs), 0)
        self.assertEqual(len(context.actions), 0)

    def test_neither_file_nor_files_passed(self):
        from zope.configuration import xmlconfig
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.xmlconfig import registerCommonDirectives
        from zope.configuration.tests import samplepackage
        from zope.configuration.tests.samplepackage import foo
        context = ConfigurationMachine()
        registerCommonDirectives(context)
        before_stack = context.stack[:]
        context.package = samplepackage
        fqn = _packageFile(samplepackage, 'configure.zcml')
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            self._callFUT(context)
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (fqn,), {}))
        self.assertEqual(len(context.actions), 1)
        action = context.actions[0]
        self.assertEqual(action['callable'], foo.data.append)
        self.assertEqual(action['includepath'], (fqn,))
        self.assertEqual(context.stack, before_stack)
        self.assertEqual(len(context._seen_files), 1)
        self.assertIn(fqn, context._seen_files)

    def test_w_file_passed(self):
        from zope.configuration import xmlconfig
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.xmlconfig import registerCommonDirectives
        from zope.configuration import tests
        from zope.configuration.tests import simple
        context = ConfigurationMachine()
        registerCommonDirectives(context)
        before_stack = context.stack[:]
        context.package = tests
        fqn = _packageFile(tests, 'simple.zcml')
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            self._callFUT(context, 'simple.zcml')
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (fqn,), {}))
        self.assertEqual(len(context.actions), 3)
        action = context.actions[0]
        self.assertEqual(action['callable'], simple.file_registry.append)
        self.assertEqual(action['includepath'], (fqn,))
        self.assertEqual(action['args'][0].path,
                         _packageFile(tests, 'simple.py'))
        action = context.actions[1]
        self.assertEqual(action['callable'], simple.file_registry.append)
        self.assertEqual(action['includepath'], (fqn,))
        self.assertEqual(action['args'][0].path,
                         _packageFile(tests, 'simple.zcml'))
        action = context.actions[2]
        self.assertEqual(action['callable'], simple.file_registry.append)
        self.assertEqual(action['includepath'], (fqn,))
        self.assertEqual(action['args'][0].path,
                         _packageFile(tests, '__init__.py'))
        self.assertEqual(context.stack, before_stack)
        self.assertEqual(len(context._seen_files), 1)
        self.assertIn(fqn, context._seen_files)

    def test_w_files_passed_and_package(self):
        from zope.configuration import xmlconfig
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.xmlconfig import registerCommonDirectives
        from zope.configuration.tests import samplepackage
        from zope.configuration.tests.samplepackage import foo
        context = ConfigurationMachine()
        registerCommonDirectives(context)
        before_stack = context.stack[:]
        fqn1 = _packageFile(samplepackage, 'baz1.zcml')
        fqn2 = _packageFile(samplepackage, 'baz2.zcml')
        fqn3 = _packageFile(samplepackage, 'baz3.zcml')
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            self._callFUT(context, package=samplepackage, files='baz*.zcml')
        self.assertEqual(len(logger.debugs), 3)
        self.assertEqual(logger.debugs[0], ('include %s', (fqn1,), {}))
        self.assertEqual(logger.debugs[1], ('include %s', (fqn2,), {}))
        self.assertEqual(logger.debugs[2], ('include %s', (fqn3,), {}))
        self.assertEqual(len(context.actions), 2)
        action = context.actions[0]
        self.assertEqual(action['callable'], foo.data.append)
        self.assertEqual(action['includepath'], (fqn2,))
        self.assertIsInstance(action['args'][0], foo.stuff)
        self.assertEqual(action['args'][0].args, (('x', (b'foo')), ('y', 2)))
        action = context.actions[1]
        self.assertEqual(action['callable'], foo.data.append)
        self.assertEqual(action['includepath'], (fqn3,))
        self.assertIsInstance(action['args'][0], foo.stuff)
        self.assertEqual(action['args'][0].args, (('x', (b'foo')), ('y', 3)))
        self.assertEqual(context.stack, before_stack)
        self.assertEqual(len(context._seen_files), 3)
        self.assertIn(fqn1, context._seen_files)
        self.assertIn(fqn2, context._seen_files)
        self.assertIn(fqn3, context._seen_files)


class Test_exclude(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.xmlconfig import exclude
        return exclude(*args, **kw)

    def test_both_file_and_files_passed(self):
        context = FauxContext()
        with self.assertRaises(ValueError) as exc:
            self._callFUT(
                context, 'tests//sample.zcml', files=['tests/*.zcml'])
        self.assertEqual(str(exc.exception),
                         "Must specify only one of file or files")

    def test_neither_file_nor_files_passed(self):
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.tests import samplepackage
        context = ConfigurationMachine()
        context.package = samplepackage
        fqn = _packageFile(samplepackage, 'configure.zcml')
        self._callFUT(context)
        self.assertEqual(len(context.actions), 0)
        self.assertEqual(len(context._seen_files), 1)
        self.assertIn(fqn, context._seen_files)

    def test_w_file_passed(self):
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration import tests
        context = ConfigurationMachine()
        context.package = tests
        fqn = _packageFile(tests, 'simple.zcml')
        self._callFUT(context, 'simple.zcml')
        self.assertEqual(len(context.actions), 0)
        self.assertEqual(len(context._seen_files), 1)
        self.assertIn(fqn, context._seen_files)

    def test_w_files_passed_and_package(self):
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.tests import samplepackage
        context = ConfigurationMachine()
        fqn1 = _packageFile(samplepackage, 'baz1.zcml')
        fqn2 = _packageFile(samplepackage, 'baz2.zcml')
        fqn3 = _packageFile(samplepackage, 'baz3.zcml')
        self._callFUT(context, package=samplepackage, files='baz*.zcml')
        self.assertEqual(len(context.actions), 0)
        self.assertEqual(len(context._seen_files), 3)
        self.assertIn(fqn1, context._seen_files)
        self.assertIn(fqn2, context._seen_files)
        self.assertIn(fqn3, context._seen_files)

    def test_w_subpackage(self):
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.tests import excludedemo
        from zope.configuration.tests.excludedemo import sub
        context = ConfigurationMachine()
        fqne_spam = _packageFile(excludedemo, 'spam.zcml')
        fqne_config = _packageFile(excludedemo, 'configure.zcml')
        fqns_config = _packageFile(sub, 'configure.zcml')
        self._callFUT(context, package=sub)
        self.assertEqual(len(context.actions), 0)
        self.assertEqual(len(context._seen_files), 1)
        self.assertFalse(fqne_spam in context._seen_files)
        self.assertFalse(fqne_config in context._seen_files)
        self.assertIn(fqns_config, context._seen_files)


class Test_includeOverrides(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.xmlconfig import includeOverrides
        return includeOverrides(*args, **kw)

    def test_actions_have_parents_includepath(self):
        from zope.configuration import xmlconfig
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.xmlconfig import registerCommonDirectives
        from zope.configuration import tests
        from zope.configuration.tests import simple
        context = ConfigurationMachine()
        fqp = _packageFile(tests, 'configure.zcml')
        registerCommonDirectives(context)
        before_stack = context.stack[:]
        context.package = tests
        # dummy action, path from "previous" include
        context.includepath = (fqp,)
        def _callable():
            raise AssertionError("should not be called")
        context.actions.append({'discriminator': None,
                                'callable': _callable,
                               })
        fqn = _packageFile(tests, 'simple.zcml')
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            self._callFUT(context, 'simple.zcml')
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (fqn,), {}))
        self.assertEqual(len(context.actions), 4)
        action = context.actions[0]
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['callable'], _callable)
        action = context.actions[1]
        self.assertEqual(action['callable'], simple.file_registry.append)
        self.assertEqual(action['includepath'], (fqp,))
        self.assertEqual(action['args'][0].path,
                         _packageFile(tests, 'simple.py'))
        action = context.actions[2]
        self.assertEqual(action['callable'], simple.file_registry.append)
        self.assertEqual(action['includepath'], (fqp,))
        self.assertEqual(action['args'][0].path,
                         _packageFile(tests, 'simple.zcml'))
        action = context.actions[3]
        self.assertEqual(action['callable'], simple.file_registry.append)
        self.assertEqual(action['includepath'], (fqp,))
        self.assertEqual(action['args'][0].path,
                         _packageFile(tests, '__init__.py'))
        self.assertEqual(context.stack, before_stack)
        self.assertEqual(len(context._seen_files), 1)
        self.assertIn(fqn, context._seen_files)


class Test_file(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.xmlconfig import file
        return file(*args, **kw)

    def test_wo_execute_wo_context_wo_package(self):
        from zope.configuration import xmlconfig
        from zope.configuration.tests.samplepackage import foo
        file_name = path("samplepackage", "configure.zcml")
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            context = self._callFUT(file_name, execute=False)
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (file_name,), {}))
        self.assertEqual(len(foo.data), 0)
        self.assertEqual(len(context.actions), 1)
        action = context.actions[0]
        self.assertEqual(action['discriminator'],
                         (('x', (b'blah')), ('y', 0)))
        self.assertEqual(action['callable'], foo.data.append)

    def test_wo_execute_wo_context_w_package(self):
        from zope.configuration import xmlconfig
        from zope.configuration.tests import samplepackage
        from zope.configuration.tests.samplepackage import foo
        file_name = path("samplepackage", "configure.zcml")
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            context = self._callFUT('configure.zcml', package=samplepackage,
                                    execute=False)
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (file_name,), {}))
        self.assertEqual(len(foo.data), 0)
        self.assertTrue(context.package is samplepackage)
        self.assertEqual(len(context.actions), 1)
        action = context.actions[0]
        self.assertEqual(action['discriminator'],
                         (('x', (b'blah')), ('y', 0)))
        self.assertEqual(action['callable'], foo.data.append)

    def test_wo_execute_w_context(self):
        from zope.configuration import xmlconfig
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.xmlconfig import registerCommonDirectives
        from zope.configuration.tests import samplepackage
        from zope.configuration.tests.samplepackage import foo
        context = ConfigurationMachine()
        context.package = samplepackage
        registerCommonDirectives(context)
        file_name = path("samplepackage", "configure.zcml")
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            ret = self._callFUT('configure.zcml', context=context,
                                execute=False)
        self.assertTrue(ret is context)
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (file_name,), {}))
        self.assertEqual(len(foo.data), 0)
        self.assertEqual(len(context.actions), 1)
        action = context.actions[0]
        self.assertEqual(action['discriminator'],
                         (('x', (b'blah')), ('y', 0)))
        self.assertEqual(action['callable'], foo.data.append)

    def test_w_execute(self):
        import os
        from zope.configuration import xmlconfig
        from zope.configuration.tests.samplepackage import foo
        file_name = path("samplepackage", "configure.zcml")
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            self._callFUT(file_name)
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (file_name,), {}))
        data = foo.data.pop()
        self.assertEqual(data.args, (('x', (b'blah')), ('y', 0)))
        self.assertTrue(
            data.info.file.endswith(
                os.path.normpath('tests/samplepackage/configure.zcml')))
        self.assertEqual(data.info.line, 12)
        self.assertEqual(data.info.column, 2)
        self.assertEqual(data.info.eline, 12)
        self.assertEqual(data.info.ecolumn, 29)
        self.assertEqual(data.package, None)
        self.assertTrue(data.basepath.endswith(
            os.path.normpath('tests/samplepackage')))


class Test_string(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.xmlconfig import string
        return string(*args, **kw)

    def test_wo_execute_wo_context(self):
        from zope.configuration.tests.samplepackage import foo
        file_name = path("samplepackage", "configure.zcml")
        with open(file_name) as f:
            xml = f.read()
        context = self._callFUT(xml, execute=False)
        self.assertEqual(len(foo.data), 0)
        self.assertEqual(len(context.actions), 1)
        action = context.actions[0]
        self.assertEqual(action['discriminator'],
                         (('x', (b'blah')), ('y', 0)))
        self.assertEqual(action['callable'], foo.data.append)

    def test_wo_execute_w_context(self):
        from zope.configuration.config import ConfigurationMachine
        from zope.configuration.xmlconfig import registerCommonDirectives
        from zope.configuration.tests.samplepackage import foo
        context = ConfigurationMachine()
        registerCommonDirectives(context)
        file_name = path("samplepackage", "configure.zcml")
        with open(file_name) as f:
            xml = f.read()
        ret = self._callFUT(xml, context=context, execute=False)
        self.assertTrue(ret is context)
        self.assertEqual(len(foo.data), 0)
        self.assertEqual(len(context.actions), 1)
        action = context.actions[0]
        self.assertEqual(action['discriminator'],
                         (('x', (b'blah')), ('y', 0)))
        self.assertEqual(action['callable'], foo.data.append)

    def test_w_execute(self):
        from zope.configuration.tests.samplepackage import foo
        file_name = path("samplepackage", "configure.zcml")
        with open(file_name) as f:
            xml = f.read()
        self._callFUT(xml)
        data = foo.data.pop()
        self.assertEqual(data.args, (('x', (b'blah')), ('y', 0)))
        self.assertTrue(data.info.file, '<string>')
        self.assertEqual(data.info.line, 12)
        self.assertEqual(data.info.column, 2)
        self.assertEqual(data.info.eline, 12)
        self.assertEqual(data.info.ecolumn, 29)
        self.assertEqual(data.package, None)
        self.assertEqual(data.basepath, None)


class XMLConfigTests(unittest.TestCase):

    def setUp(self):
        from zope.configuration.xmlconfig import _clearContext
        from zope.configuration.tests.samplepackage.foo import data
        _clearContext()
        del data[:]

    def tearDown(self):
        from zope.configuration.xmlconfig import _clearContext
        from zope.configuration.tests.samplepackage.foo import data
        _clearContext()
        del data[:]

    def _getTargetClass(self):
        from zope.configuration.xmlconfig import XMLConfig
        return XMLConfig

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_w_global_context_missing(self):
        import os
        from zope.configuration import xmlconfig
        from zope.configuration.tests.samplepackage import foo
        here = os.path.dirname(__file__)
        path = os.path.join(here, "samplepackage", "configure.zcml")
        logger = LoggerStub()
        xmlconfig._context = None
        with _Monkey(xmlconfig, logger=logger):
            xc = self._makeOne(path)
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (path,), {}))
        self.assertEqual(len(foo.data), 0) # no execut_actions
        self.assertEqual(len(xc.context.actions), 1)
        action = xc.context.actions[0]
        self.assertEqual(action['discriminator'],
                         (('x', (b'blah')), ('y', 0)))
        self.assertEqual(action['callable'], foo.data.append)

    def test_ctor(self):
        from zope.configuration import xmlconfig
        from zope.configuration.tests import samplepackage
        from zope.configuration.tests.samplepackage import foo
        fqn = _packageFile(samplepackage, 'configure.zcml')
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            xc = self._makeOne(fqn)
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (fqn,), {}))
        self.assertEqual(len(foo.data), 0) # no execut_actions
        self.assertEqual(len(xc.context.actions), 1)
        action = xc.context.actions[0]
        self.assertEqual(action['discriminator'],
                         (('x', (b'blah')), ('y', 0)))
        self.assertEqual(action['callable'], foo.data.append)

    def test_ctor_w_module(self):
        from zope.configuration import xmlconfig
        from zope.configuration.tests.samplepackage import foo
        from zope.configuration.tests import samplepackage
        fqn = _packageFile(samplepackage, 'configure.zcml')
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            xc = self._makeOne("configure.zcml", samplepackage)
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (fqn,), {}))
        self.assertEqual(len(foo.data), 0) # no execut_actions
        self.assertEqual(len(xc.context.actions), 1)
        action = xc.context.actions[0]
        self.assertEqual(action['discriminator'],
                         (('x', (b'blah')), ('y', 0)))
        self.assertEqual(action['callable'], foo.data.append)

    def test___call__(self):
        import os
        from zope.configuration import xmlconfig
        from zope.configuration.tests import samplepackage
        from zope.configuration.tests.samplepackage import foo
        fqn = _packageFile(samplepackage, 'configure.zcml')
        logger = LoggerStub()
        with _Monkey(xmlconfig, logger=logger):
            xc = self._makeOne(fqn)
        self.assertEqual(len(logger.debugs), 1)
        self.assertEqual(logger.debugs[0], ('include %s', (fqn,), {}))
        self.assertEqual(len(foo.data), 0)
        xc() # call to process the actions
        self.assertEqual(len(foo.data), 1)
        data = foo.data.pop(0)
        self.assertEqual(data.args, (('x', (b'blah')), ('y', 0)))
        self.assertTrue(
            data.info.file.endswith(
                os.path.normpath('tests/samplepackage/configure.zcml')))
        self.assertEqual(data.info.line, 12)
        self.assertEqual(data.info.column, 2)
        self.assertEqual(data.info.eline, 12)
        self.assertEqual(data.info.ecolumn, 29)



class Test_xmlconfig(unittest.TestCase):

    def setUp(self):
        from zope.configuration.xmlconfig import _clearContext
        from zope.configuration.tests.samplepackage.foo import data
        _clearContext()
        del data[:]

    def tearDown(self):
        from zope.configuration.xmlconfig import _clearContext
        from zope.configuration.tests.samplepackage.foo import data
        _clearContext()
        del data[:]

    def _callFUT(self, *args, **kw):
        from zope.configuration.xmlconfig import xmlconfig
        return xmlconfig(*args, **kw)

    def test_wo_testing_passed(self):
        import os
        from zope.configuration import xmlconfig
        from zope.configuration.tests import samplepackage
        from zope.configuration.tests.samplepackage import foo
        def _assertTestingFalse(func):
            def _wrapper(*args, **kw):
                assert not kw['testing']
                return func(*args, **kw)
            return _wrapper
        fqn = _packageFile(samplepackage, 'configure.zcml')
        context = xmlconfig._getContext()
        context.execute_actions = _assertTestingFalse(context.execute_actions)
        with _Monkey(xmlconfig,
                     processxmlfile=_assertTestingFalse(
                         xmlconfig.processxmlfile)):
            self._callFUT(open(fqn), False)
        self.assertEqual(len(foo.data), 1)
        data = foo.data.pop(0)
        self.assertEqual(data.args, (('x', (b'blah')), ('y', 0)))
        self.assertTrue(
            data.info.file.endswith(
                os.path.normpath('tests/samplepackage/configure.zcml')))
        self.assertEqual(data.info.line, 12)
        self.assertEqual(data.info.column, 2)
        self.assertEqual(data.info.eline, 12)
        self.assertEqual(data.info.ecolumn, 29)

    def test_w_testing_passed(self):
        import os
        from zope.configuration import xmlconfig
        from zope.configuration.tests import samplepackage
        from zope.configuration.tests.samplepackage import foo
        def _assertTestingTrue(func):
            def _wrapper(*args, **kw):
                assert kw['testing']
                return func(*args, **kw)
            return _wrapper
        fqn = _packageFile(samplepackage, 'configure.zcml')
        context = xmlconfig._getContext()
        context.execute_actions = _assertTestingTrue(context.execute_actions)
        with _Monkey(xmlconfig,
                     processxmlfile=_assertTestingTrue(
                         xmlconfig.processxmlfile)):
            self._callFUT(open(fqn), True)
        self.assertEqual(len(foo.data), 1)
        data = foo.data.pop(0)
        self.assertEqual(data.args, (('x', (b'blah')), ('y', 0)))
        self.assertTrue(
            data.info.file.endswith(
                os.path.normpath('tests/samplepackage/configure.zcml')))
        self.assertEqual(data.info.line, 12)
        self.assertEqual(data.info.column, 2)
        self.assertEqual(data.info.eline, 12)
        self.assertEqual(data.info.ecolumn, 29)


class Test_testxmlconfig(unittest.TestCase):

    def setUp(self):
        from zope.configuration.xmlconfig import _clearContext
        from zope.configuration.tests.samplepackage.foo import data
        _clearContext()
        del data[:]

    def tearDown(self):
        from zope.configuration.xmlconfig import _clearContext
        from zope.configuration.tests.samplepackage.foo import data
        _clearContext()
        del data[:]

    def _callFUT(self, *args, **kw):
        from zope.configuration.xmlconfig import testxmlconfig
        return testxmlconfig(*args, **kw)

    def test_w_testing_passed(self):
        import os
        from zope.configuration import xmlconfig
        from zope.configuration.tests import samplepackage
        from zope.configuration.tests.samplepackage import foo
        def _assertTestingTrue(func):
            def _wrapper(*args, **kw):
                assert kw['testing']
                return func(*args, **kw)
            return _wrapper
        fqn = _packageFile(samplepackage, 'configure.zcml')
        context = xmlconfig._getContext()
        context.execute_actions = _assertTestingTrue(context.execute_actions)
        with _Monkey(xmlconfig,
                     processxmlfile=_assertTestingTrue(
                         xmlconfig.processxmlfile)):
            self._callFUT(open(fqn))
        self.assertEqual(len(foo.data), 1)
        data = foo.data.pop(0)
        self.assertEqual(data.args, (('x', (b'blah')), ('y', 0)))
        self.assertTrue(
            data.info.file.endswith(
                os.path.normpath('tests/samplepackage/configure.zcml')))
        self.assertEqual(data.info.line, 12)
        self.assertEqual(data.info.column, 2)
        self.assertEqual(data.info.eline, 12)
        self.assertEqual(data.info.ecolumn, 29)



class FauxLocator(object):
    def __init__(self, file, line, column):
        self.file, self.line, self.column = file, line, column
    def getSystemId(self):
        return self.file
    def getLineNumber(self):
        return self.line
    def getColumnNumber(self):
        return self.column


class FauxContext(object):
    includepath = ()
    _features = ()
    _end_called = False
    def setInfo(self, info):
        self.info = info
    def getInfo(self):
        return self.info
    def begin(self, name, data, info):
        self.begin_args = name, data
        self.info = info
    def end(self):
        self._end_called = 1
    def hasFeature(self, feature):
        return feature in self._features


def path(*p):
    import os
    return os.path.join(os.path.dirname(__file__), *p)

def clean_info_path(s):
    import os
    part1 = s[:6]
    part2 = s[6:s.find('"', 6)]
    part2 = part2[part2.rfind("tests"):]
    part2 = part2.replace(os.sep, '/')
    part3 = s[s.find('"', 6):].rstrip()
    return part1+part2+part3

def clean_path(s):
    import os
    s = s[s.rfind("tests"):]
    s = s.replace(os.sep, '/')
    return s

def clean_actions(actions):
    return [
        {
            'discriminator': action['discriminator'],
            'info': clean_info_path(repr(action['info'])),
            'includepath': [clean_path(p) for p in action['includepath']],
        }
        for action in actions
    ]

def clean_text_w_paths(error):
    r = []
    for line in str(error).split("\n"):
        line = line.rstrip()
        if not line:
            continue
        l = line.find('File "')
        if l >= 0:
            line = line[:l] + clean_info_path(line[l:])
        r.append(line)
    return '\n'.join(r)


def _packageFile(package, filename):
    import os
    return os.path.join(os.path.dirname(package.__file__), filename)

class _Monkey(object):

    def __init__(self, module, **replacements):
        self.module = module
        self.orig = {}
        self.replacements = replacements

    def __enter__(self):
        for k, v in self.replacements.items():
            orig = getattr(self.module, k, self)
            if orig is not self:
                self.orig[k] = orig
            setattr(self.module, k, v)

    def __exit__(self, *exc_info):
        for k in self.replacements:
            if k in self.orig:
                setattr(self.module, k, self.orig[k])
            else: # pragma: no cover
                delattr(self.module, k)


class LoggerStub(object):

    debugs = errors = warnings = infos = ()

    def __init__(self):
        def make_append(lst):
            return lambda msg, *args, **kwargs: lst.append((msg, args, kwargs))

        for name in 'error', 'warning', 'info', 'debug':
            lst = []
            setattr(self, name + 's', lst)

            func = make_append(lst)
            setattr(self, name, func)
