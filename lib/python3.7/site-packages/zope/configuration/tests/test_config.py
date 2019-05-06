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
"""Test configuration machinery.
"""
import unittest
import sys

# pylint:disable=inherit-non-class,protected-access
# pylint:disable=attribute-defined-outside-init, arguments-differ

class ConfigurationContextTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.configuration.config import ConfigurationContext
        return ConfigurationContext

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def tearDown(self):
        for name in ('zope.configuration.tests.victim',
                     'zope.configuration.tests.bad'
                     'zope.configuration.tests.unicode_all',
                     'zope.configuration.tests.unicode_all.__future__'):
            sys.modules.pop(name, None)

    def test_resolve_empty(self):
        c = self._makeOne()
        with self.assertRaises(ValueError):
            c.resolve('')

    def test_resolve_whitespace(self):
        c = self._makeOne()
        with self.assertRaises(ValueError):
            c.resolve('   ')

    def test_resolve_dot(self):
        c = self._makeOne()
        package = c.package = object()
        self.assertTrue(c.resolve('.') is package)

    def test_resolve_trailing_dot_in_resolve(self):
        #Dotted names are no longer allowed to end in dots
        c = self._makeOne()
        with self.assertRaises(ValueError):
            c.resolve('zope.')

    def test_resolve_builtin(self):
        c = self._makeOne()
        self.assertTrue(c.resolve('str') is str)

    def test_resolve_single_non_builtin(self):
        import os
        c = self._makeOne()
        self.assertTrue(c.resolve('os') is os)

    def test_resolve_relative_miss_no_package(self):
        from zope.configuration.exceptions import ConfigurationError
        c = self._makeOne()
        c.package = None
        with self.assertRaises(ConfigurationError):
            c.resolve('.nonesuch')

    def test_resolve_relative_miss_w_package_too_many_dots(self):
        class FauxPackage(object):
            __name__ = None
        from zope.configuration.exceptions import ConfigurationError
        c = self._makeOne()
        package = c.package = FauxPackage()
        package.__name__ = 'one.dot'
        with self.assertRaises(ConfigurationError):
            c.resolve('....nonesuch')

    def test_resolve_bad_dotted_last_import(self):
        # Import error caused by a bad last component in the dotted name.
        from zope.configuration.exceptions import ConfigurationError
        c = self._makeOne()
        with self.assertRaises(ConfigurationError) as exc:
            c.resolve('zope.configuration.tests.nosuch')
        self.assertIn('ImportError', str(exc.exception))

    def test_resolve_bad_dotted_import(self):
        # Import error caused by a totally wrong dotted name.
        from zope.configuration.exceptions import ConfigurationError
        c = self._makeOne()
        with self.assertRaises(ConfigurationError) as exc:
            c.resolve('zope.configuration.nosuch.noreally')
        self.assertIn('ImportError', str(exc.exception))

    def test_resolve_bad_sub_last_import(self):
        #Import error caused by a bad sub import inside the referenced
        #dotted name. Here we keep the standard traceback.
        c = self._makeOne()
        with self.assertRaises(ImportError):
            c.resolve('zope.configuration.tests.victim')

    def test_resolve_bad_sub_import(self):
        #Import error caused by a bad sub import inside part of the referenced
        #dotted name. Here we keep the standard traceback.
        c = self._makeOne()
        with self.assertRaises(ImportError):
            c.resolve('zope.configuration.tests.victim.nosuch')

    def test_resolve_unicode_all(self):
        # If a package's __init__.py is in the process of being ported from
        # Python 2 to Python 3 using unicode_literals, then it can end up
        # with unicode items in __all__, which breaks star imports from that
        # package; but we tolerate this.
        c = self._makeOne()
        self.assertEqual(
            c.resolve('zope.configuration.tests.unicode_all').foo, 'sentinel')
        self.assertEqual(
            c.resolve('zope.configuration.tests.unicode_all.foo'), 'sentinel')

    def test_path_w_absolute_filename(self):
        import os
        c = self._makeOne()
        self.assertEqual(c.path('/path/to/somewhere'),
                         os.path.normpath('/path/to/somewhere'))

    def test_path_w_relative_filename_w_basepath(self):
        import os
        c = self._makeOne()
        c.basepath = '/path/to'
        self.assertEqual(c.path('somewhere'),
                         os.path.normpath('/path/to/somewhere'))

    def test_path_w_relative_filename_wo_basepath_wo_package(self):
        import os
        c = self._makeOne()
        c.package = None
        self.assertEqual(c.path('somewhere'),
                         os.path.join(os.getcwd(), 'somewhere'))

    def test_path_wo_basepath_w_package_having_file(self):
        #Path must always return an absolute path.
        import os
        class stub:
            __file__ = os.path.join('relative', 'path')
        c = self._makeOne()
        c.package = stub()
        self.assertTrue(os.path.isabs(c.path('y/z')))

    def test_path_wo_basepath_w_package_having_no_file_but_path(self):
        #Determine package path using __path__ if __file__ isn't available.
        # (i.e. namespace package installed with
        #--single-version-externally-managed)
        import os
        class stub:
            __path__ = [os.path.join('relative', 'path')]
        c = self._makeOne()
        c.package = stub()
        self.assertTrue(os.path.isabs(c.path('y/z')))

    def test_path_expand_filenames(self):
        import os
        c = self._makeOne()
        os.environ['path-test'] = '42'
        try:
            path = c.path(os.path.join(os.sep, '${path-test}'))
            self.assertEqual(path, os.path.join(os.sep, '42'))
        finally:
            del os.environ['path-test']

    def test_path_expand_user(self):
        import os
        c = self._makeOne()
        old_home = os.environ.get('HOME')
        # HOME should be absolute
        os.environ['HOME'] = os.path.join(os.sep, 'HOME')
        try:
            path = c.path('~')
            self.assertEqual(path, os.path.join(os.sep, 'HOME'))
        finally: # pragma: no cover
            if old_home:
                os.environ['HOME'] = old_home
            else:
                del os.environ['HOME']

    def test_checkDuplicate_miss(self):
        import os
        c = self._makeOne()
        c.checkDuplicate('/path') # doesn't raise
        self.assertEqual(list(c._seen_files), [os.path.normpath('/path')])

    def test_checkDuplicate_hit(self):
        import os
        from zope.configuration.exceptions import ConfigurationError
        c = self._makeOne()
        c.checkDuplicate('/path')
        with self.assertRaises(ConfigurationError):
            c.checkDuplicate('/path')
        self.assertEqual(list(c._seen_files), [os.path.normpath('/path')])

    def test_processFile_miss(self):
        import os
        c = self._makeOne()
        self.assertEqual(c.processFile('/path'), True)
        self.assertEqual(list(c._seen_files), [os.path.normpath('/path')])

    def test_processFile_hit(self):
        import os
        c = self._makeOne()
        c.processFile('/path')
        self.assertEqual(c.processFile('/path'), False)
        self.assertEqual(list(c._seen_files), [os.path.normpath('/path')])

    def test_action_defaults_no_info_no_includepath(self):
        DISCRIMINATOR = ('a', ('b',), 0)
        c = self._makeOne()
        c.actions = [] # normally provided by subclass
        c.action(DISCRIMINATOR)
        self.assertEqual(len(c.actions), 1)
        info = c.actions[0]
        self.assertEqual(info['discriminator'], DISCRIMINATOR)
        self.assertEqual(info['callable'], None)
        self.assertEqual(info['args'], ())
        self.assertEqual(info['kw'], {})
        self.assertEqual(info['includepath'], ())
        self.assertEqual(info['info'], '')
        self.assertEqual(info['order'], 0)

    def test_action_defaults_w_info_w_includepath(self):
        DISCRIMINATOR = ('a', ('b',), 0)
        c = self._makeOne()
        c.actions = [] # normally provided by subclass
        c.info = 'INFO' # normally provided by subclass
        c.includepath = ('a', 'b') # normally provided by subclass
        c.action(DISCRIMINATOR)
        self.assertEqual(len(c.actions), 1)
        info = c.actions[0]
        self.assertEqual(info['discriminator'], DISCRIMINATOR)
        self.assertEqual(info['callable'], None)
        self.assertEqual(info['args'], ())
        self.assertEqual(info['kw'], {})
        self.assertEqual(info['order'], 0)
        self.assertEqual(info['includepath'], ('a', 'b'))
        self.assertEqual(info['info'], 'INFO')

    def test_action_explicit_no_extra(self):
        DISCRIMINATOR = ('a', ('b',), 0)
        ARGS = (12, 'z')
        KW = {'one': 1}
        INCLUDE_PATH = ('p', 'q/r')
        INFO = 'INFO'
        def _callable():
            raise AssertionError("should not be called")
        c = self._makeOne()
        c.actions = [] # normally provided by subclass
        c.action(DISCRIMINATOR,
                 _callable,
                 ARGS,
                 KW,
                 42,
                 INCLUDE_PATH,
                 INFO,
                )
        self.assertEqual(len(c.actions), 1)
        info = c.actions[0]
        self.assertEqual(info['discriminator'], DISCRIMINATOR)
        self.assertEqual(info['callable'], _callable)
        self.assertEqual(info['args'], ARGS)
        self.assertEqual(info['kw'], KW)
        self.assertEqual(info['order'], 42)
        self.assertEqual(info['includepath'], INCLUDE_PATH)
        self.assertEqual(info['info'], INFO)

    def test_action_explicit_w_extra(self):
        DISCRIMINATOR = ('a', ('b',), 0)
        ARGS = (12, 'z')
        KW = {'one': 1}
        INCLUDE_PATH = ('p', 'q/r')
        INFO = 'INFO'
        def _callable():
            raise AssertionError("should not be called")
        c = self._makeOne()
        c.actions = [] # normally provided by subclass
        c.action(DISCRIMINATOR,
                 _callable,
                 ARGS,
                 KW,
                 42,
                 INCLUDE_PATH,
                 INFO,
                 foo='bar',
                 baz=17,
                )
        self.assertEqual(len(c.actions), 1)
        info = c.actions[0]
        self.assertEqual(info['discriminator'], DISCRIMINATOR)
        self.assertEqual(info['callable'], _callable)
        self.assertEqual(info['args'], ARGS)
        self.assertEqual(info['kw'], KW)
        self.assertEqual(info['order'], 42)
        self.assertEqual(info['includepath'], INCLUDE_PATH)
        self.assertEqual(info['info'], INFO)
        self.assertEqual(info['foo'], 'bar')
        self.assertEqual(info['baz'], 17)

    def test_hasFeature_miss(self):
        c = self._makeOne()
        self.assertFalse(c.hasFeature('nonesuch'))

    def test_hasFeature_hit(self):
        c = self._makeOne()
        c._features.add('a.feature')
        self.assertTrue(c.hasFeature('a.feature'))

    def test_provideFeature(self):
        c = self._makeOne()
        c.provideFeature('a.feature')
        self.assertTrue(c.hasFeature('a.feature'))


class ConfigurationAdapterRegistryTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.configuration.config import ConfigurationAdapterRegistry
        return ConfigurationAdapterRegistry

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        reg = self._makeOne()
        self.assertEqual(len(reg._registry), 0)
        self.assertEqual(len(reg._docRegistry), 0)

    def test_register(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        def _factory():
            raise AssertionError("should not be called")
        reg = self._makeOne()
        reg.register(IFoo, (NS, NAME), _factory)
        self.assertEqual(len(reg._registry), 1)
        areg = reg._registry[(NS, NAME)]
        self.assertTrue(areg.lookup1(IFoo, Interface) is _factory)
        self.assertEqual(len(reg._docRegistry), 0)

    def test_register_replacement(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        def _factory():
            raise AssertionError("should not be called")
        def _rival():
            raise AssertionError("should not be called")
        reg = self._makeOne()
        reg.register(IFoo, (NS, NAME), _factory)
        reg.register(IFoo, (NS, NAME), _rival)
        self.assertEqual(len(reg._registry), 1)
        areg = reg._registry[(NS, NAME)]
        self.assertTrue(areg.lookup1(IFoo, Interface) is _rival)
        self.assertEqual(len(reg._docRegistry), 0)

    def test_register_new_name(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        NAME2 = 'other'
        def _factory():
            raise AssertionError("should not be called")
        def _rival():
            raise AssertionError("should not be called")
        reg = self._makeOne()
        reg.register(IFoo, (NS, NAME), _factory)
        reg.register(IFoo, (NS, NAME2), _rival)
        self.assertEqual(len(reg._registry), 2)
        areg = reg._registry[(NS, NAME)]
        self.assertTrue(areg.lookup1(IFoo, Interface) is _factory)
        areg = reg._registry[(NS, NAME2)]
        self.assertTrue(areg.lookup1(IFoo, Interface) is _rival)
        self.assertEqual(len(reg._docRegistry), 0)

    def test_document_non_string_name(self):
        from zope.interface import Interface
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        HANDLER = object()
        INFO = 'INFO'
        PARENT = object()
        reg = self._makeOne()
        reg.document((NS, NAME), ISchema, IUsedIn, HANDLER, INFO, PARENT)
        self.assertEqual(len(reg._registry), 0)
        self.assertEqual(len(reg._docRegistry), 1)
        name, schema, used_in, handler, info, parent = reg._docRegistry[0]
        self.assertEqual(name, (NS, NAME))
        self.assertEqual(schema, ISchema)
        self.assertEqual(used_in, IUsedIn)
        self.assertEqual(info, INFO)
        self.assertEqual(parent, PARENT)

    def test_document_w_string_name(self):
        from zope.interface import Interface
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        NAME = 'testing'
        HANDLER = object()
        INFO = 'INFO'
        PARENT = object()
        reg = self._makeOne()
        reg.document(NAME, ISchema, IUsedIn, HANDLER, INFO, PARENT)
        self.assertEqual(len(reg._registry), 0)
        self.assertEqual(len(reg._docRegistry), 1)
        name, schema, used_in, handler, info, parent = reg._docRegistry[0]
        self.assertEqual(name, ('', NAME))
        self.assertEqual(schema, ISchema)
        self.assertEqual(used_in, IUsedIn)
        self.assertEqual(info, INFO)
        self.assertEqual(parent, PARENT)

    def test_factory_miss(self):
        from zope.configuration.exceptions import ConfigurationError
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = object()
        reg = self._makeOne()
        with self.assertRaises(ConfigurationError):
            reg.factory(context, (NS, NAME))

    def test_factory_hit_on_fqn(self):
        from zope.interface import Interface
        from zope.interface import implementer
        class IFoo(Interface):
            pass
        @implementer(IFoo)
        class Context(object):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = Context()
        def _factory():
            raise AssertionError("should not be called")
        reg = self._makeOne()
        reg.register(IFoo, (NS, NAME), _factory)
        self.assertEqual(reg.factory(context, (NS, NAME)), _factory)

    def test_factory_miss_on_fqn_hit_on_bare_name(self):
        from zope.interface import Interface
        from zope.interface import implementer
        class IFoo(Interface):
            pass
        @implementer(IFoo)
        class Context(object):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = Context()
        def _factory():
            raise AssertionError("should not be called")
        reg = self._makeOne()
        reg.register(IFoo, NAME, _factory)
        self.assertEqual(reg.factory(context, (NS, NAME)), _factory)

    def test_factory_hit_on_fqn_lookup_fails(self):
        from zope.interface import Interface
        from zope.configuration.exceptions import ConfigurationError
        class IFoo(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = object() # doesn't provide IFoo
        def _factory():
            raise AssertionError("should not be called")
        reg = self._makeOne()
        reg.register(IFoo, (NS, NAME), _factory)
        with self.assertRaises(ConfigurationError):
            reg.factory(context, (NS, NAME))


class _ConformsToIConfigurationContext(object):

    def _getTargetClass(self):
        raise NotImplementedError

    def _makeOne(self, *args, **kwargs):
        raise NotImplementedError

    def test_class_conforms_to_IConfigurationContext(self):
        from zope.interface.verify import verifyClass
        from zope.configuration.interfaces import IConfigurationContext
        verifyClass(IConfigurationContext, self._getTargetClass())

    def test_instance_conforms_to_IConfigurationContext(self):
        from zope.interface.verify import verifyObject
        from zope.configuration.interfaces import IConfigurationContext
        verifyObject(IConfigurationContext, self._makeOne())


class ConfigurationMachineTests(_ConformsToIConfigurationContext,
                                unittest.TestCase,
                               ):

    def _getTargetClass(self):
        from zope.configuration.config import ConfigurationMachine
        return ConfigurationMachine

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        from zope.configuration.config import RootStackItem
        from zope.configuration.config import metans
        cm = self._makeOne()
        self.assertEqual(cm.package, None)
        self.assertEqual(cm.basepath, None)
        self.assertEqual(cm.includepath, ())
        self.assertEqual(cm.info, '')
        self.assertEqual(len(cm.actions), 0)
        self.assertEqual(len(cm.stack), 1)
        root = cm.stack[0]
        self.assertIsInstance(root, RootStackItem)
        self.assertTrue(root.context is cm)
        self.assertEqual(len(cm.i18n_strings), 0)
        # Check bootstrapped meta:*.
        self.assertIn((metans, 'directive'), cm._registry)
        self.assertIn((metans, 'directives'), cm._registry)
        self.assertIn((metans, 'complexDirective'), cm._registry)
        self.assertIn((metans, 'groupingDirective'), cm._registry)
        self.assertIn((metans, 'provides'), cm._registry)
        self.assertIn((metans, 'subdirective'), cm._registry)

    def test_begin_w___data_and_kw(self):
        from zope.configuration.config import IConfigurationContext
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        def _factory(context, data, info):
            raise AssertionError("should not be called")
        cm = self._makeOne()
        cm.register(IConfigurationContext, (NS, NAME), _factory)
        with self.assertRaises(TypeError):
            cm.begin((NS, NAME), {'foo': 'bar'}, baz='bam')

    def test_begin_w___data_no_kw(self):
        from zope.interface import Interface
        from zope.configuration.config import IConfigurationContext
        from zope.configuration.config import RootStackItem
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        def _handler(*args, **kw):
            raise AssertionError("should not be called")
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        _called_with = []
        item = object()
        def _factory(context, data, info):
            _called_with.append((context, data, info))
            return item
        cm = self._makeOne()
        cm.register(IConfigurationContext, (NS, NAME), _factory)
        cm.begin((NS, NAME), {
            'name': 'testing',
            'schema': ISchema,
            'usedIn': IUsedIn,
            'handler': _handler,
        }, 'INFO')
        self.assertEqual(len(cm.stack), 2)
        root = cm.stack[0]
        self.assertIsInstance(root, RootStackItem)
        nested = cm.stack[1]
        self.assertTrue(nested is item)
        self.assertEqual(_called_with,
                         [(cm, {
                             'name': 'testing',
                             'schema': ISchema,
                             'usedIn': IUsedIn,
                             'handler': _handler,
                         }, 'INFO')])

    def test_begin_wo___data_w_kw(self):
        from zope.interface import Interface
        from zope.configuration.config import IConfigurationContext
        from zope.configuration.config import RootStackItem
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        def _handler(*args, **kw):
            raise AssertionError("should not be called")
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        _called_with = []
        item = object()
        def _factory(context, data, info):
            _called_with.append((context, data, info))
            return item
        cm = self._makeOne()
        cm.register(IConfigurationContext, (NS, NAME), _factory)
        cm.begin(
            (NS, NAME), None, 'INFO',
            name='testing',
            schema=ISchema,
            usedIn=IUsedIn,
            handler=_handler,
        )
        self.assertEqual(len(cm.stack), 2)
        root = cm.stack[0]
        self.assertIsInstance(root, RootStackItem)
        nested = cm.stack[1]
        self.assertTrue(nested is item)
        self.assertEqual(_called_with,
                         [(cm, {
                             'name': 'testing',
                             'schema': ISchema,
                             'usedIn': IUsedIn,
                             'handler': _handler,
                         }, 'INFO')])

    def test_end(self):
        from zope.configuration.config import RootStackItem
        class FauxItem(object):
            _finished = False
            def finish(self):
                self._finished = True
        cm = self._makeOne()
        item = FauxItem()
        cm.stack.append(item)
        cm.end()
        self.assertEqual(len(cm.stack), 1)
        root = cm.stack[0]
        self.assertIsInstance(root, RootStackItem)
        self.assertTrue(item._finished)

    def test___call__(self):
        from zope.interface import Interface
        from zope.configuration.config import IConfigurationContext
        from zope.configuration.config import RootStackItem
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        class FauxItem(object):
            _finished = False
            def finish(self):
                self._finished = True
        def _handler(*args, **kw):
            raise AssertionError("should not be called")
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        _called_with = []
        item = FauxItem()
        def _factory(context, data, info):
            _called_with.append((context, data, info))
            return item
        cm = self._makeOne()
        cm.register(IConfigurationContext, (NS, NAME), _factory)
        cm(
            (NS, NAME), 'INFO',
            name='testing',
            schema=ISchema,
            usedIn=IUsedIn,
            handler=_handler,
        )
        self.assertEqual(len(cm.stack), 1)
        root = cm.stack[0]
        self.assertIsInstance(root, RootStackItem)
        self.assertEqual(_called_with,
                         [(cm, {
                             'name': 'testing',
                             'schema': ISchema,
                             'usedIn': IUsedIn,
                             'handler': _handler,
                         }, 'INFO')])
        self.assertTrue(item._finished)

    def test_getInfo_only_root_default(self):
        cm = self._makeOne()
        self.assertEqual(cm.getInfo(), '')

    def test_getInfo_only_root(self):
        cm = self._makeOne()
        cm.info = 'INFO'
        self.assertEqual(cm.getInfo(), 'INFO')

    def test_getInfo_w_item(self):
        class FauxItem(object):
            info = 'FAUX'
            def __init__(self):
                self.context = self
        cm = self._makeOne()
        cm.stack.append(FauxItem())
        self.assertEqual(cm.getInfo(), 'FAUX')

    def test_setInfo_only_root(self):
        cm = self._makeOne()
        cm.setInfo('INFO')
        self.assertEqual(cm.info, 'INFO')

    def test_setInfo_w_item(self):
        class FauxItem(object):
            info = 'FAUX'
            def __init__(self):
                self.context = self
        cm = self._makeOne()
        item = FauxItem()
        cm.stack.append(item)
        cm.setInfo('UPDATED')
        self.assertEqual(item.info, 'UPDATED')

    def test_execute_actions_empty(self):
        cm = self._makeOne()
        cm.execute_actions() # noop

    def test_execute_actions_wo_errors(self):
        _called_with = {}
        def _a1(*args, **kw):
            _called_with.setdefault('_a1', []).append((args, kw))
        def _a2(*args, **kw):
            _called_with.setdefault('_a2', []).append((args, kw))
        cm = self._makeOne()
        cm.action(None, None) # will be skipped
        cm.action(None, _a1, ('a', 0), {'foo': 'bar'}, 4)
        cm.action(None, _a2, ('a', 1), {'foo': 'baz'}, 3)
        cm.action(None, _a1, ('b', 2), {'foo': 'qux'}, 2)
        cm.execute_actions()
        self.assertEqual(_called_with['_a1'],
                         [(('b', 2), {'foo': 'qux'}),
                          (('a', 0), {'foo': 'bar'}),
                         ])
        self.assertEqual(_called_with['_a2'],
                         [(('a', 1), {'foo': 'baz'}),
                         ])

    def test_execute_actions_w_errors_w_testing(self):
        def _err(*args, **kw):
            raise ValueError('XXX')
        cm = self._makeOne()
        cm.action(None, _err)
        with self.assertRaises(ValueError) as exc:
            cm.execute_actions(testing=True)
        self.assertEqual(str(exc.exception), 'XXX')

    def test_execute_actions_w_errors_wo_testing(self):
        from zope.configuration.config import ConfigurationExecutionError
        def _err(*args, **kw):
            raise ValueError('XXX')
        cm = self._makeOne()
        cm.info = 'INFO'
        cm.action(None, _err)
        with self.assertRaises(ConfigurationExecutionError) as exc:
            cm.execute_actions()
        self.assertIs(exc.exception.etype, ValueError)
        self.assertEqual(str(exc.exception.evalue), "XXX")
        self.assertEqual(exc.exception.info, "INFO")

    def _check_execute_actions_w_errors_wo_testing(self, ex_kind, cm=None):
        ex = ex_kind('XXX')
        def _err(*args, **kw):
            raise ex
        cm = cm if cm is not None else self._makeOne()
        cm.info = 'INFO'
        cm.action(None, _err)
        with self.assertRaises(ex_kind) as exc:
            cm.execute_actions()

        self.assertIs(exc.exception, ex)

    def test_execute_actions_w_errors_wo_testing_SystemExit(self):
        # It gets passed through as-is
        self._check_execute_actions_w_errors_wo_testing(SystemExit)

    def test_execute_actions_w_errors_wo_testing_KeyboardInterrupt(self):
        # It gets passed through as-is
        self._check_execute_actions_w_errors_wo_testing(KeyboardInterrupt)

    def test_execute_actions_w_errors_wo_testing_BaseException(self):
        # It gets passed through as-is
        class Bex(BaseException):
            pass
        self._check_execute_actions_w_errors_wo_testing(Bex)

    def test_execute_actions_w_errors_custom(self):
        # It gets passed through as-is, if we ask it to
        class Ex(Exception):
            pass
        cm = self._makeOne()
        cm.pass_through_exceptions += (Ex,)
        self._check_execute_actions_w_errors_wo_testing(Ex, cm)

    def test_keyword_handling(self):
        # This is really an integraiton test.
        from zope.configuration.config import metans
        from zope.configuration.tests.directives import f
        machine = self._makeOne()
        ns = "http://www.zope.org/testing"

        #Register some test directives, starting with a grouping directive
        # that sets a package:

        machine(
            (metans, "groupingDirective"),
            name="package", namespace=ns,
            schema="zope.configuration.tests.directives.IPackaged",
            handler="zope.configuration.tests.directives.Packaged",
        )

        # set the package:
        machine.begin(
            (ns, "package"),
            package="zope.configuration.tests.directives",
        )

        #Which makes it easier to define the other directives:
        machine((metans, "directive"),
                namespace=ns, name="k",
                schema=".Ik", handler=".k")

        machine((ns, "k"), "yee ha",
                **{"for": u"f", "class": u"c", "x": u"x"})

        self.assertEqual(len(machine.actions), 1)
        self.assertEqual(machine.actions[0],
                         {'args': ('f', 'c', 'x'),
                          'callable': f,
                          'discriminator': ('k', 'f'),
                          'includepath': (),
                          'info': 'yee ha',
                          'kw': {},
                          'order': 0,
                         })


class _ConformsToIStackItem(object):

    def _getTargetClass(self):
        raise NotImplementedError

    def _makeOne(self, *args, **kwargs):
        raise NotImplementedError

    def test_class_conforms_to_IStackItem(self):
        from zope.interface.verify import verifyClass
        from zope.configuration.config import IStackItem
        verifyClass(IStackItem, self._getTargetClass())

    def test_instance_conforms_to_IStackItem(self):
        from zope.interface.verify import verifyObject
        from zope.configuration.config import IStackItem
        verifyObject(IStackItem, self._makeOne())


class SimpleStackItemTests(_ConformsToIStackItem,
                           unittest.TestCase,
                          ):

    def _getTargetClass(self):
        from zope.configuration.config import SimpleStackItem
        return SimpleStackItem

    def _makeOne(self,
                 context=None, handler=None, info=None,
                 schema=None, data=None):
        from zope.interface import Interface
        if context is None:
            context = FauxContext()
        if handler is None:
            def handler():
                raise AssertionError("should not be called")
        if info is None:
            info = 'INFO'
        if schema is None:
            schema = Interface
        if data is None:
            data = {}
        return self._getTargetClass()(context, handler, info, schema, data)

    def test_ctor(self):
        from zope.interface import Interface
        from zope.configuration.config import GroupingContextDecorator
        class ISchema(Interface):
            pass
        context = FauxContext()
        def _handler():
            raise AssertionError("should not be called")
        _data = {}
        ssi = self._makeOne(context, _handler, 'INFO', ISchema, _data)
        self.assertIsInstance(ssi.context, GroupingContextDecorator)
        self.assertTrue(ssi.context.context is context)
        self.assertEqual(ssi.context.info, 'INFO')
        self.assertEqual(ssi.handler, _handler)
        self.assertEqual(ssi.argdata, (ISchema, _data))

    def test_contained_raises(self):
        from zope.configuration.exceptions import ConfigurationError
        ssi = self._makeOne()
        with self.assertRaises(ConfigurationError):
            ssi.contained(('ns', 'name'), {}, '')

    def test_finish_handler_returns_no_actions(self):
        from zope.interface import Interface
        from zope.schema import Text
        class ISchema(Interface):
            name = Text(required=True)
        context = FauxContext()
        def _handler(context, **kw):
            return ()
        _data = {'name': 'NAME'}
        ssi = self._makeOne(context, _handler, 'INFO', ISchema, _data)
        ssi.finish() # noraise
        self.assertEqual(context.actions, [])

    def test_finish_handler_returns_oldstyle_actions(self):
        from zope.interface import Interface
        from zope.schema import Text
        class ISchema(Interface):
            name = Text(required=True)
        context = FauxContext()
        def _action(context, **kw):
            raise AssertionError("should not be called")
        def _handler(context, **kw):
            return [(None, _action)]
        _data = {'name': 'NAME'}
        ssi = self._makeOne(context, _handler, 'INFO', ISchema, _data)
        ssi.finish()
        self.assertEqual(context.actions,
                         [{'discriminator': None,
                           'callable': _action,
                           'args': (),
                           'kw': {},
                           'includepath': (),
                           'info': 'INFO',
                           'order': 0,
                          }])

    def test_finish_handler_returns_newstyle_actions(self):
        from zope.interface import Interface
        from zope.schema import Text
        class ISchema(Interface):
            name = Text(required=True)
        context = FauxContext()
        def _action(context, **kw):
            raise AssertionError("should not be called")
        def _handler(context, **kw):
            return [{'discriminator': None, 'callable': _action}]
        _data = {'name': 'NAME'}
        ssi = self._makeOne(context, _handler, 'INFO', ISchema, _data)
        ssi.finish()
        self.assertEqual(context.actions,
                         [{'discriminator': None,
                           'callable': _action,
                           'args': (),
                           'kw': {},
                           'includepath': (),
                           'info': 'INFO',
                           'order': 0,
                          }])



class RootStackItemTests(_ConformsToIStackItem,
                         unittest.TestCase,
                        ):

    def _getTargetClass(self):
        from zope.configuration.config import RootStackItem
        return RootStackItem

    def _makeOne(self, context=None):
        if context is None:
            context = object()
        return self._getTargetClass()(context)

    def test_contained_context_factory_fails(self):
        from zope.configuration.exceptions import ConfigurationError
        class _Context(object):
            def factory(self, context, name):
                "does nothing"
        rsi = self._makeOne(_Context())
        with self.assertRaises(ConfigurationError):
            rsi.contained(('ns', 'name'), {}, '')

    def test_contained_context_factory_normal(self):
        _called_with = []
        _adapter = object()
        def _factory(context, data, info):
            _called_with.append((context, data, info))
            return _adapter
        class _Context(object):
            def factory(self, context, name):
                return _factory
        context = _Context()
        rsi = self._makeOne(context)
        adapter = rsi.contained(('ns', 'name'), {'a': 'b'}, 'INFO')
        self.assertTrue(adapter is _adapter)
        self.assertEqual(_called_with, [(context, {'a': 'b'}, 'INFO')])

    def test_finish(self):
        rsi = self._makeOne()
        rsi.finish() #noraise


class GroupingStackItemTests(_ConformsToIStackItem,
                             unittest.TestCase,
                            ):

    def _getTargetClass(self):
        from zope.configuration.config import GroupingStackItem
        return GroupingStackItem

    def _makeOne(self, context=None):
        if context is None:
            context = object()
        return self._getTargetClass()(context)

    def test_contained_context_before_returns_oldstyle_actions(self):
        _called_with = []
        _adapter = object()
        def _factory(context, data, info):
            _called_with.append((context, data, info))
            return _adapter
        def _action(*args, **kw):
            raise AssertionError("should not be called")
        class _Context(FauxContext):
            def factory(self, context, name):
                return _factory
            def before(self):
                return [(None, _action)]
            def after(self):
                return ()
        context = _Context()
        rsi = self._makeOne(context)
        adapter = rsi.contained(('ns', 'name'), {'a': 'b'}, 'INFO')
        self.assertTrue(adapter is _adapter)
        self.assertEqual(_called_with, [(context, {'a': 'b'}, 'INFO')])
        self.assertEqual(len(context.actions), 1)
        self.assertEqual(context.actions[0],
                         {'discriminator': None,
                          'callable': _action,
                          'args': (),
                          'kw': {},
                          'includepath': (),
                          'info': None,
                          'order': 0,
                         })
        rsi.finish() # doesn't re-do the 'before' dance
        self.assertEqual(len(context.actions), 1)

    def test_contained_context_before_returns_newstyle_actions(self):
        _called_with = []
        _adapter = object()
        def _factory(context, data, info):
            _called_with.append((context, data, info))
            return _adapter
        def _before(*args, **kw):
            raise AssertionError("should not be called")
        def _after(*args, **kw):
            raise AssertionError("should not be called")
        class _Context(FauxContext):
            def factory(self, context, name):
                return _factory
            def before(self):
                return [{'discriminator': None, 'callable': _before}]
            def after(self):
                return [{'discriminator': None, 'callable': _after}]
        context = _Context()
        rsi = self._makeOne(context)
        adapter = rsi.contained(('ns', 'name'), {'a': 'b'}, 'INFO')
        self.assertTrue(adapter is _adapter)
        self.assertEqual(_called_with, [(context, {'a': 'b'}, 'INFO')])
        self.assertEqual(len(context.actions), 1)
        self.assertEqual(context.actions[0], # no GSI to add extras
                         {'discriminator': None,
                          'callable': _before,
                         })
        rsi.finish() # doesn't re-do the 'before' dance
        self.assertEqual(len(context.actions), 2)
        self.assertEqual(context.actions[1],
                         {'discriminator': None,
                          'callable': _after,
                         })

    def test_finish_calls_before_if_not_already_called(self):
        def _before(*args, **kw):
            raise AssertionError("should not be called")
        def _after(*args, **kw):
            raise AssertionError("should not be called")
        class _Context(FauxContext):
            def before(self):
                return [(None, _before)]
            def after(self):
                return [(None, _after)]
        context = _Context()
        rsi = self._makeOne(context)
        rsi.finish()
        self.assertEqual(len(context.actions), 2)
        self.assertEqual(context.actions[0], # no GSI to add extras
                         {'discriminator': None,
                          'callable': _before,
                          'args': (),
                          'kw': {},
                          'includepath': (),
                          'info': None,
                          'order': 0,
                         })
        self.assertEqual(context.actions[1],
                         {'discriminator': None,
                          'callable': _after,
                          'args': (),
                          'kw': {},
                          'includepath': (),
                          'info': None,
                          'order': 0,
                         })


class ComplexStackItemTests(_ConformsToIStackItem,
                            unittest.TestCase,
                           ):

    def _getTargetClass(self):
        from zope.configuration.config import ComplexStackItem
        return ComplexStackItem

    def _makeOne(self, meta=None, context=None, data=None, info=None):
        if meta is None:
            meta = self._makeMeta()
        if context is None:
            context = object()
        if data is None:
            data = {'name': 'NAME'}
        if info is None:
            info = 'INFO'
        return self._getTargetClass()(meta, context, data, info)

    def _makeMeta(self):
        from zope.interface import Interface
        from zope.schema import Text
        class ISchema(Interface):
            name = Text()
        class FauxMeta(dict):
            schema = ISchema
            _handler_args = None
            _handler = object()
            def handler(self, newcontext, **kw):
                self._handler_kwargs = kw
                return self._handler
        return FauxMeta()

    def test_ctor(self):
        from zope.configuration.config import GroupingContextDecorator
        meta = self._makeMeta()
        context = FauxContext()
        _data = {'name': 'NAME'}
        csi = self._makeOne(meta, context, _data, 'INFO')
        self.assertIsInstance(csi.context, GroupingContextDecorator)
        self.assertTrue(csi.context.context is context)
        self.assertEqual(csi.context.info, 'INFO')
        self.assertEqual(csi.handler, meta._handler)
        self.assertEqual(meta._handler_kwargs, _data)

    def test_contained_miss(self):
        from zope.configuration.exceptions import ConfigurationError
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        csi = self._makeOne()
        with self.assertRaises(ConfigurationError):
            csi.contained((NS, NAME), {}, 'INFO')

    def test_contained_hit(self):
        from zope.interface import Interface
        from zope.configuration.config import GroupingContextDecorator
        from zope.configuration.config import SimpleStackItem
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        class ISubSchema(Interface):
            pass
        class WithName(object):
            def testing(self, *args):
                raise AssertionError("should not be called")
        meta = self._makeMeta()
        wn = meta._handler = WithName()
        meta[NAME] = (ISubSchema, 'SUBINFO')
        context = FauxContext()
        _data = {'name': 'NAME'}
        csi = self._makeOne(meta, context, _data, 'INFO')
        ssi = csi.contained((NS, NAME), {}, 'SUBINFO')
        self.assertIsInstance(ssi, SimpleStackItem)
        self.assertIsInstance(ssi.context, GroupingContextDecorator)
        self.assertTrue(ssi.context.context is csi.context)
        self.assertEqual(ssi.context.info, 'SUBINFO')
        self.assertEqual(ssi.handler, wn.testing)
        self.assertEqual(ssi.argdata, (ISubSchema, {}))

    def test_finish_handler_is_noncallable(self):
        meta = self._makeMeta()
        context = FauxContext()
        _data = {'name': 'NAME'}
        csi = self._makeOne(meta, context, _data, 'INFO')
        csi.finish() #noraise
        self.assertEqual(len(context.actions), 0)

    def test_finish_handler_raises_AE_for___call__(self):
        def _handler():
            raise AttributeError('__call__')
        meta = self._makeMeta()
        meta._handler = _handler
        context = FauxContext()
        _data = {'name': 'NAME'}
        csi = self._makeOne(meta, context, _data, 'INFO')
        csi.finish() #noraise
        self.assertEqual(len(context.actions), 0)

    def test_finish_handler_raises_AE_for_other(self):
        def _handler():
            raise AttributeError('other')
        meta = self._makeMeta()
        meta._handler = _handler
        context = FauxContext()
        _data = {'name': 'NAME'}
        csi = self._makeOne(meta, context, _data, 'INFO')
        with self.assertRaises(AttributeError):
            csi.finish()

    def test_finish_handler_returns_oldstyle_actions(self):
        def _action():
            raise AssertionError("should not be called")
        def _handler():
            return [(None, _action)]
        meta = self._makeMeta()
        meta._handler = _handler
        context = FauxContext()
        _data = {'name': 'NAME'}
        csi = self._makeOne(meta, context, _data, 'INFO')
        csi.finish()
        self.assertEqual(len(context.actions), 1)
        self.assertEqual(context.actions[0],
                         {'discriminator': None,
                          'callable': _action,
                          'args': (),
                          'kw': {},
                          'includepath': (),
                          'info': 'INFO',
                          'order': 0,
                         })

    def test_finish_handler_returns_newstyle_actions(self):
        def _action():
            raise AssertionError("should not be called")
        def _handler():
            return [{'discriminator': None, 'callable': _action}]
        meta = self._makeMeta()
        meta._handler = _handler
        context = FauxContext()
        _data = {'name': 'NAME'}
        csi = self._makeOne(meta, context, _data, 'INFO')
        csi.finish()
        self.assertEqual(len(context.actions), 1)
        self.assertEqual(context.actions[0],
                         {'discriminator': None,
                          'callable': _action,
                          'args': (),
                          'kw': {},
                          'includepath': (),
                          'info': 'INFO',
                          'order': 0,
                         })


class _ConformsToIGroupingContext(object):

    def _getTargetClass(self):
        raise NotImplementedError

    def _makeOne(self, *args, **kwargs):
        raise NotImplementedError

    def test_class_conforms_to_IGroupingContext(self):
        from zope.interface.verify import verifyClass
        from zope.configuration.interfaces import IGroupingContext
        verifyClass(IGroupingContext, self._getTargetClass())

    def test_instance_conforms_to_IGroupingContext(self):
        from zope.interface.verify import verifyObject
        from zope.configuration.interfaces import IGroupingContext
        verifyObject(IGroupingContext, self._makeOne())


class GroupingContextDecoratorTests(_ConformsToIConfigurationContext,
                                    _ConformsToIGroupingContext,
                                    unittest.TestCase,
                                   ):

    def _getTargetClass(self):
        from zope.configuration.config import GroupingContextDecorator
        return GroupingContextDecorator

    def _makeOne(self, context=None, **kw):
        if context is None:
            context = FauxContext()
            context.package = None #appease IConfigurationContext
        instance = self._getTargetClass()(context, **kw)
        return instance

    def test_ctor_no_kwargs(self):
        context = FauxContext()
        gcd = self._makeOne(context)
        self.assertTrue(gcd.context is context)

    def test_ctor_w_kwargs(self):
        context = FauxContext()
        gcd = self._makeOne(context, foo='bar', baz=42)
        self.assertTrue(gcd.context is context)
        self.assertEqual(gcd.foo, 'bar')
        self.assertEqual(gcd.baz, 42)

    def test_getattr_fetches_from_context_and_caches(self):
        context = FauxContext()
        gcd = self._makeOne(context)
        context.foo = 'bar'
        self.assertEqual(gcd.foo, 'bar')
        self.assertIn('foo', gcd.__dict__)

    def test_before(self):
        gcd = self._makeOne()
        gcd.before() #noraise

    def test_after(self):
        gcd = self._makeOne()
        gcd.after() #noraise


class _ConformsToIDirectivesContext(object):

    def _getTargetClass(self):
        raise NotImplementedError

    def _makeOne(self, *args, **kwargs):
        raise NotImplementedError

    def test_class_conforms_to_IDirectivesContext(self):
        from zope.interface.verify import verifyClass
        from zope.configuration.config import IDirectivesContext
        verifyClass(IDirectivesContext, self._getTargetClass())

    def test_instance_conforms_to_IDirectivesContext(self):
        from zope.interface.verify import verifyObject
        from zope.configuration.config import IDirectivesContext
        verifyObject(IDirectivesContext, self._makeOne())


class DirectivesHandlerTests(_ConformsToIDirectivesContext,
                             unittest.TestCase,
                            ):

    def _getTargetClass(self):
        from zope.configuration.config import DirectivesHandler
        return DirectivesHandler

    def _makeOne(self, context=None):
        if context is None:
            context = FauxContext()
            context.package = None #appease IConfigurationContext
            context.namespace = None #appease IDirectivesInfo
        instance = self._getTargetClass()(context)
        return instance


class Test_defineSimpleDirective(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.config import defineSimpleDirective
        return defineSimpleDirective(*args, **kw)

    def _makeContext(self):
        class _Context(FauxContext):
            def __init__(self):
                FauxContext.__init__(self)
                self._registered = []
                self._documented = []
            def register(self, usedIn, name, factory):
                self._registered.append((usedIn, name, factory))
            def document(self, name, schema, usedIn, handler, info):
                self._documented.append((name, schema, usedIn, handler, info))
        return _Context()

    def test_defaults(self):
        from zope.interface import Interface
        from zope.configuration.interfaces import IConfigurationContext as ICC
        class ISchema(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = self._makeContext()
        context.namespace = NS
        context.info = 'INFO'
        def _handler():
            raise AssertionError("should not be called")

        self._callFUT(context, NAME, ISchema, _handler)

        self.assertEqual(len(context._registered), 1)
        usedIn, name, factory = context._registered[0]
        self.assertEqual(usedIn, ICC)
        self.assertEqual(name, (NS, NAME))
        sub = object()
        ssi = factory(sub, {'a': 1}, 'SUBINFO')
        self.assertTrue(ssi.context.context is sub)
        self.assertEqual(ssi.context.info, 'SUBINFO')
        self.assertEqual(ssi.handler, _handler)

        self.assertEqual(len(context._documented), 1)
        self.assertEqual(context._documented[0],
                         ((NS, NAME), ISchema, ICC, _handler, 'INFO'))

    def test_explicit_w_star_namespace(self):
        from zope.interface import Interface
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = self._makeContext()
        context.namespace = NS
        context.info = 'INFO'
        def _handler():
            raise AssertionError("should not be called")

        self._callFUT(context, NAME, ISchema, _handler,
                      namespace='*', usedIn=IUsedIn)

        self.assertEqual(len(context._registered), 1)
        usedIn, name, factory = context._registered[0]
        self.assertEqual(usedIn, IUsedIn)
        self.assertEqual(name, NAME)
        sub = object()
        ssi = factory(sub, {'a': 1}, 'SUBINFO')
        self.assertTrue(ssi.context.context is sub)
        self.assertEqual(ssi.context.info, 'SUBINFO')
        self.assertEqual(ssi.handler, _handler)

        self.assertEqual(len(context._documented), 1)
        self.assertEqual(context._documented[0],
                         (NAME, ISchema, IUsedIn, _handler, 'INFO'))


class Test_defineGroupingDirective(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.config import defineGroupingDirective
        return defineGroupingDirective(*args, **kw)

    def _makeContext(self):
        class _Context(FauxContext):
            def __init__(self):
                FauxContext.__init__(self)
                self._registered = []
                self._documented = []
            def register(self, usedIn, name, factory):
                self._registered.append((usedIn, name, factory))
            def document(self, name, schema, usedIn, handler, info):
                self._documented.append((name, schema, usedIn, handler, info))
        return _Context()

    def test_defaults(self):
        from zope.interface import Interface
        from zope.schema import Text
        from zope.configuration.interfaces import IConfigurationContext as ICC
        class ISchema(Interface):
            arg = Text()
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = self._makeContext()
        context.namespace = NS
        context.info = 'INFO'
        newcontext = FauxContext()
        _called_with = []
        def _handler(context, **kw):
            _called_with.append((context, kw))
            return newcontext

        self._callFUT(context, NAME, ISchema, _handler)

        self.assertEqual(len(context._registered), 1)
        usedIn, name, factory = context._registered[0]
        self.assertEqual(usedIn, ICC)
        self.assertEqual(name, (NS, NAME))
        sub = object()
        gsi = factory(sub, {'arg': 'val'}, 'SUBINFO')
        self.assertTrue(gsi.context is newcontext)
        self.assertEqual(newcontext.info, 'SUBINFO')
        self.assertEqual(_called_with, [(sub, {'arg': 'val'})])

        self.assertEqual(len(context._documented), 1)
        self.assertEqual(context._documented[0],
                         ((NS, NAME), ISchema, ICC, _handler, 'INFO'))

    def test_explicit_w_star_namespace(self):
        from zope.interface import Interface
        from zope.schema import Text
        class ISchema(Interface):
            arg = Text()
        class IUsedIn(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = self._makeContext()
        context.namespace = NS
        context.info = 'INFO'
        newcontext = FauxContext()
        _called_with = []
        def _handler(context, **kw):
            _called_with.append((context, kw))
            return newcontext

        self._callFUT(context, NAME, ISchema, _handler,
                      namespace='*', usedIn=IUsedIn)

        self.assertEqual(len(context._registered), 1)
        usedIn, name, factory = context._registered[0]
        self.assertEqual(usedIn, IUsedIn)
        self.assertEqual(name, NAME)
        sub = object()
        gsi = factory(sub, {'arg': 'val'}, 'SUBINFO')
        self.assertTrue(gsi.context is newcontext)
        self.assertEqual(newcontext.info, 'SUBINFO')
        self.assertEqual(_called_with, [(sub, {'arg': 'val'})])

        self.assertEqual(len(context._documented), 1)
        self.assertEqual(context._documented[0],
                         (NAME, ISchema, IUsedIn, _handler, 'INFO'))


class _ConformsToIComplexDirectiveContext(object):

    def _getTargetClass(self):
        raise NotImplementedError

    def _makeOne(self, *args, **kwargs):
        raise NotImplementedError

    def test_class_conforms_to_IComplexDirectiveContext(self):
        from zope.interface.verify import verifyClass
        from zope.configuration.config import IComplexDirectiveContext
        verifyClass(IComplexDirectiveContext, self._getTargetClass())

    def test_instance_conforms_to_IComplexDirectiveContext(self):
        from zope.interface.verify import verifyObject
        from zope.configuration.config import IComplexDirectiveContext
        verifyObject(IComplexDirectiveContext, self._makeOne())


class ComplexDirectiveDefinitionTests(_ConformsToIComplexDirectiveContext,
                                      unittest.TestCase,
                                     ):

    def _getTargetClass(self):
        from zope.configuration.config import ComplexDirectiveDefinition
        return ComplexDirectiveDefinition

    def _makeOne(self, context=None):
        if context is None:
            context = self._makeContext()
        instance = self._getTargetClass()(context)
        return instance

    def _makeContext(self, package=None, namespace=None, name=None,
                     schema=None, handler=None, usedIn=None):
        context = FauxContext()
        context.package = package
        context.namespace = namespace
        context.name = name
        context.schema = schema
        context.handler = handler
        context.usedIn = usedIn
        return context

    def test_before(self):
        from zope.interface import Interface
        from zope.schema import Text
        class ISchema(Interface):
            arg = Text()
        class IUsedIn(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        _handled = []
        _csi_handler = object()
        def _handler(context, **kw):
            _handled.append((context, kw))
            return _csi_handler
        context = self._makeContext(namespace=NS, name=NAME, schema=ISchema,
                                    handler=_handler, usedIn=IUsedIn)
        context.info = 'INFO'
        _registered = []
        def _register(*args):
            _registered.append(args)
        context.register = _register
        _documented = []
        def _document(*args):
            _documented.append(args)
        context.document = _document
        cdd = self._makeOne(context)

        cdd.before()

        self.assertEqual(len(_registered), 1)
        usedIn, fqn, factory = _registered[0]
        self.assertEqual(usedIn, IUsedIn)
        self.assertEqual(fqn, (NS, NAME))
        sub = FauxContext()
        csi = factory(sub, {'arg': 'val'}, 'SUBINFO')
        self.assertEqual(csi.meta, cdd)
        self.assertEqual(csi.context.context, sub)
        self.assertEqual(csi.context.info, 'SUBINFO')
        self.assertEqual(csi.handler, _csi_handler)
        self.assertEqual(_handled, [(csi.context, {'arg': 'val'})])

        self.assertEqual(_documented,
                         [((NS, NAME), ISchema, IUsedIn, _handler, 'INFO')])


class Test_subdirective(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.config import subdirective
        return subdirective(*args, **kw)

    def _makeContext(self, package=None, namespace=None, name=None,
                     schema=None, handler=None, usedIn=None):
        class _Context(object):
            def __init__(self):
                self.context = {}
                self._documented = []
            def document(self, *args):
                self._documented.append(args)
        context = _Context()
        context.package = package
        context.namespace = namespace
        context.name = name
        context.schema = schema
        context.handler = handler
        context.usedIn = usedIn
        return context

    def test_wo_handler_attribute(self):
        from zope.interface import Interface
        from zope.schema import Text
        class ISubSchema(Interface):
            arg = Text()
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        SUBNAME = 'sub'
        _handler = object()
        context = self._makeContext(
            None, NS, NAME, ISchema, _handler, IUsedIn)
        context.info = 'INFO'
        self._callFUT(context, SUBNAME, ISubSchema)
        self.assertEqual(len(context._documented), 1)
        fqn, schema, usedIn, handler, info, ctx = context._documented[0]
        self.assertEqual(fqn, (NS, SUBNAME))
        self.assertEqual(schema, ISubSchema)
        self.assertEqual(usedIn, IUsedIn)
        self.assertEqual(handler, _handler)
        self.assertEqual(info, 'INFO')
        self.assertEqual(ctx, context.context)
        self.assertEqual(context.context[SUBNAME], (ISubSchema, 'INFO'))

    def test_w_handler_attribute(self):
        from zope.interface import Interface
        from zope.schema import Text
        class ISubSchema(Interface):
            arg = Text()
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        class Handler(object):
            sub = object()
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        SUBNAME = 'sub'
        handler = Handler()
        context = self._makeContext(None, NS, NAME, ISchema, handler, IUsedIn)
        context.info = 'INFO'
        self._callFUT(context, SUBNAME, ISubSchema)
        self.assertEqual(len(context._documented), 1)
        fqn, schema, usedIn, handler, info, ctx = context._documented[0]
        self.assertEqual(fqn, (NS, SUBNAME))
        self.assertEqual(schema, ISubSchema)
        self.assertEqual(usedIn, IUsedIn)
        self.assertEqual(handler, Handler.sub)
        self.assertEqual(info, 'INFO')
        self.assertEqual(ctx, context.context)
        self.assertEqual(context.context[SUBNAME], (ISubSchema, 'INFO'))


class Test_provides(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.config import provides
        return provides(*args, **kw)

    def test_w_multiple(self):
        context = FauxContext()
        with self.assertRaises(ValueError):
            self._callFUT(context, 'one two')

    def test_w_single(self):
        _provided = []
        def _provideFeature(feature):
            _provided.append(feature)
        context = FauxContext()
        context.provideFeature = _provideFeature
        self._callFUT(context, 'one')
        self.assertEqual(_provided, ['one'])


class Test_toargs(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.config import toargs
        return toargs(*args, **kw)

    def test_w_empty_schema_no_data(self):
        from zope.interface import Interface
        class ISchema(Interface):
            pass
        context = FauxContext()
        self.assertEqual(self._callFUT(context, ISchema, {}), {})

    def test_w_empty_schema_w_data_no_kwargs_allowed(self):
        from zope.configuration.exceptions import ConfigurationError
        from zope.interface import Interface
        class ISchema(Interface):
            pass
        context = FauxContext()
        with self.assertRaises(ConfigurationError) as exc:
            self._callFUT(context, ISchema, {'a': 'b'})
        self.assertEqual(exc.exception.args,
                         ('Unrecognized parameters:', 'a'))

    def test_w_empty_schema_w_data_w_kwargs_allowed(self):
        from zope.interface import Interface
        class ISchema(Interface):
            pass
        ISchema.setTaggedValue('keyword_arguments', True)
        context = FauxContext()
        self.assertEqual(self._callFUT(context, ISchema, {'a': 'b'}),
                         {'a': 'b'})

    def test_w_keyword_sub(self):
        from zope.interface import Interface
        from zope.schema import Text
        class ISchema(Interface):
            for_ = Text()
        context = FauxContext()
        self.assertEqual(self._callFUT(context, ISchema, {'for': 'foo'}),
                         {'for_': 'foo'})

    def test_w_field_missing_no_default(self):
        from zope.interface import Interface
        from zope.schema import Text
        from zope.configuration.exceptions import ConfigurationError
        class ISchema(Interface):
            no_default = Text()
        context = FauxContext()
        with self.assertRaises(ConfigurationError) as exc:
            self._callFUT(context, ISchema, {})
        self.assertEqual(exc.exception.args,
                         ("Missing parameter: 'no_default'",))

        # It includes the details of any validation failure;
        # The rendering of the nested exception varies by Python version,
        # sadly.
        exception_str = str(exc.exception)
        self.assertTrue(exception_str.startswith(
            "Missing parameter: 'no_default'\n"
        ), exception_str)
        self.assertTrue(exception_str.endswith(
            "RequiredMissing: no_default"
        ), exception_str)

    def test_w_field_missing_but_default(self):
        from zope.interface import Interface
        from zope.schema import Text
        class ISchema(Interface):
            w_default = Text(default=u'default')
        context = FauxContext()
        self.assertEqual(self._callFUT(context, ISchema, {}),
                         {'w_default': 'default'})

    def test_w_invalid_value(self):
        from zope.interface import Interface
        from zope.schema import Int
        from zope.configuration.exceptions import ConfigurationError
        class ISchema(Interface):
            count = Int(min=0)
        context = FauxContext()
        with self.assertRaises(ConfigurationError) as exc:
            self._callFUT(context, ISchema, {'count': '-1'})
        self.assertEqual(exc.exception.args,
                         ("Invalid value for 'count'",))

        for meth in str, repr:
            exception_str = meth(exc.exception)
            self.assertIn(
                "Invalid value for",
                exception_str)
            self.assertIn(
                "TooSmall: (-1, 0)",
                exception_str)

class Test_expand_action(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.config import expand_action
        return expand_action(*args, **kw)

    def test_defaults(self):
        self.assertEqual(self._callFUT(('a', 1, None)),
                         {'discriminator': ('a', 1, None),
                          'callable': None,
                          'args': (),
                          'kw': {},
                          'includepath': (),
                          'info': None,
                          'order': 0,
                         })

    def test_explicit_no_extra(self):
        def _callable():
            raise AssertionError("should not be called")
        self.assertEqual(self._callFUT(('a', 1, None),
                                       _callable, ('b', 2), {'c': None},
                                       ('p', 'q/r'), 'INFO', 42,
                                      ),
                         {'discriminator': ('a', 1, None),
                          'callable': _callable,
                          'args': ('b', 2),
                          'kw': {'c': None},
                          'includepath': ('p', 'q/r'),
                          'info': 'INFO',
                          'order': 42,
                         })

    def test_explicit_w_extra(self):
        def _callable():
            raise AssertionError("should not be called")
        self.assertEqual(self._callFUT(('a', 1, None),
                                       _callable, ('b', 2), {'c': None},
                                       ('p', 'q/r'), 'INFO', 42,
                                       foo='bar', baz=None,
                                      ),
                         {'discriminator': ('a', 1, None),
                          'callable': _callable,
                          'args': ('b', 2),
                          'kw': {'c': None},
                          'includepath': ('p', 'q/r'),
                          'info': 'INFO',
                          'order': 42,
                          'foo': 'bar',
                          'baz': None,
                         })


class Test_resolveConflicts(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.configuration.config import resolveConflicts
        return resolveConflicts(*args, **kw)

    def test_empty(self):
        self.assertEqual(self._callFUT(()), [])

    def test_expands_oldstyle_actions(self):
        def _callable():
            raise AssertionError("should not be called")
        self.assertEqual(
            self._callFUT([(None, _callable)]),
            [
                {
                    'discriminator': None,
                    'callable': _callable,
                    'args': (),
                    'kw': {},
                    'includepath': (),
                    'info': None,
                    'order': 0,
                }
            ]
        )

    def test_wo_discriminator_clash(self):
        from zope.configuration.config import expand_action
        def _a():
            raise AssertionError("should not be called")
        def _b():
            raise AssertionError("should not be called")
        def _c():
            raise AssertionError("should not be called")
        def _d():
            raise AssertionError("should not be called")
        actions = [
            expand_action(('a', 1), _a, order=3),
            expand_action(('b', 2), _b, order=1),
            expand_action(('c', 3), _c, order=2),
            expand_action(('d', 4), _d, order=1),
        ]
        self.assertEqual([x['callable'] for x in self._callFUT(actions)],
                         [_b, _d, _c, _a])

    def test_w_resolvable_discriminator_clash(self):
        from zope.configuration.config import expand_action
        def _a():
            raise AssertionError("should not be called")
        def _b():
            raise AssertionError("should not be called")
        actions = [
            expand_action(('a', 1), _a, includepath=('a',)),
            expand_action(('a', 1), _b, includepath=('a', 'b')),
        ]
        self.assertEqual([x['callable'] for x in self._callFUT(actions)],
                         [_a])

    def test_w_non_resolvable_discriminator_clash_different_paths(self):
        from zope.configuration.config import ConfigurationConflictError
        from zope.configuration.config import expand_action
        def _a():
            raise AssertionError("should not be called")
        def _b():
            raise AssertionError("should not be called")
        actions = [
            expand_action(('a', 1), _a, includepath=('b', 'c'), info='X'),
            expand_action(('a', 1), _b, includepath=('a',), info='Y'),
        ]
        with self.assertRaises(ConfigurationConflictError) as exc:
            self._callFUT(actions)
        self.assertEqual(exc.exception._conflicts, {('a', 1): ['Y', 'X']})

    def test_w_non_resolvable_discriminator_clash_same_path(self):
        from zope.configuration.config import ConfigurationConflictError
        from zope.configuration.config import expand_action
        def _a():
            raise AssertionError("should not be called")
        def _b():
            raise AssertionError("should not be called")
        actions = [
            expand_action(('a', 1), _a, includepath=('a',), info='X'),
            expand_action(('a', 1), _b, includepath=('a',), info='Y'),
        ]
        with self.assertRaises(ConfigurationConflictError) as exc:
            self._callFUT(actions)
        self.assertEqual(exc.exception._conflicts, {('a', 1): ['X', 'Y']})

    def test_configuration_conflict_error_has_readable_exception(self):
        from zope.configuration.config import ConfigurationConflictError
        from zope.configuration.config import expand_action
        def _a():
            raise AssertionError("should not be called")
        def _b():
            raise AssertionError("should not be called")
        actions = [
            expand_action(('a', 1), _a, includepath=('a',), info='conflict!'),
            expand_action(
                ('a', 1), _b, includepath=('a',), info='conflict2!'),
        ]
        with self.assertRaises(ConfigurationConflictError) as exc:
            self._callFUT(actions)
        self.assertEqual(
            "Conflicting configuration actions\n  "
            "For: ('a', 1)\n    conflict!\n    conflict2!",
            str(exc.exception))

        exc.exception.add_details('a detail')

        self.assertEqual(
            "Conflicting configuration actions\n  "
            "For: ('a', 1)\n    conflict!\n    conflict2!\n"
            "    a detail",
            str(exc.exception))

    def test_wo_discriminators_final_sorting_order(self):
        from zope.configuration.config import expand_action
        def _a():
            raise AssertionError("should not be called")
        def _b():
            raise AssertionError("should not be called")
        def _c():
            raise AssertionError("should not be called")
        def _d():
            raise AssertionError("should not be called")
        actions = [
            expand_action(None, _a, order=3),
            expand_action(None, _b, order=1),
            expand_action(None, _c, order=2),
            expand_action(None, _d, order=1),
        ]
        self.assertEqual([x['callable'] for x in self._callFUT(actions)],
                         [_b, _d, _c, _a])


class FauxContext(object):
    def __init__(self):
        self.actions = []
    def action(self, **kw):
        self.actions.append(kw)
