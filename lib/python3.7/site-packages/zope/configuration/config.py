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
"""Configuration processor
"""
from keyword import iskeyword
import operator
import os.path
import sys

from zope.interface.adapter import AdapterRegistry
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import providedBy
from zope.schema import TextLine
from zope.schema import URI
from zope.schema import ValidationError

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.exceptions import ConfigurationWrapperError
from zope.configuration.interfaces import IConfigurationContext
from zope.configuration.interfaces import IGroupingContext
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import PathProcessor
from zope.configuration._compat import builtins
from zope.configuration._compat import reraise
from zope.configuration._compat import string_types
from zope.configuration._compat import text_type

__all__ = [
    'ConfigurationContext',
    'ConfigurationAdapterRegistry',
    'ConfigurationMachine',
    'IStackItem',
    'SimpleStackItem',
    'RootStackItem',
    'GroupingStackItem',
    'ComplexStackItem',
    'GroupingContextDecorator',
    'DirectiveSchema',
    'IDirectivesInfo',
    'IDirectivesContext',
    'DirectivesHandler',
    'IDirectiveInfo',
    'IFullInfo',
    'IStandaloneDirectiveInfo',
    'defineSimpleDirective',
    'defineGroupingDirective',
    'IComplexDirectiveContext',
    'ComplexDirectiveDefinition',
    'subdirective',
    'IProvidesDirectiveInfo',
    'provides',
    'toargs',
    'expand_action',
    'resolveConflicts',
    'ConfigurationConflictError',
]

zopens = 'http://namespaces.zope.org/zope'
metans = 'http://namespaces.zope.org/meta'
testns = 'http://namespaces.zope.org/test'


class ConfigurationContext(object):
    """
    Mix-in for implementing.
    :class:`zope.configuration.interfaces.IConfigurationContext`.

    Note that this class itself does not actually declare that it
    implements that interface; the subclass must do that. In addition,
    subclasses must provide a ``package`` attribute and a ``basepath``
    attribute. If the base path is not None, relative paths are
    converted to absolute paths using the the base path. If the
    package is not none, relative imports are performed relative to
    the package.

    In general, the basepath and package attributes should be
    consistent. When a package is provided, the base path should be
    set to the path of the package directory.

    Subclasses also provide an ``actions`` attribute, which is a list
    of actions, an ``includepath`` attribute, and an ``info``
    attribute.

    The include path is appended to each action and is used when
    resolving conflicts among actions. Normally, only the a
    ConfigurationMachine provides the actions attribute. Decorators
    simply use the actions of the context they decorate. The
    ``includepath`` attribute is a tuple of names. Each name is
    typically the name of an included configuration file.

    The ``info`` attribute contains descriptive information helpful
    when reporting errors. If not set, it defaults to an empty string.

    The actions attribute is a sequence of dictionaries where each
    dictionary has the following keys:

        - ``discriminator``, a value that identifies the action. Two
          actions that have the same (non None) discriminator
          conflict.

        - ``callable``, an object that is called to execute the
          action,

        - ``args``, positional arguments for the action

        - ``kw``, keyword arguments for the action

        - ``includepath``, a tuple of include file names (defaults to
          ())

        - ``info``, an object that has descriptive information about
          the action (defaults to '')
    """

    # pylint:disable=no-member

    def __init__(self):
        super(ConfigurationContext, self).__init__()
        self._seen_files = set()
        self._features = set()

    def resolve(self, dottedname):
        """
        Resolve a dotted name to an object.

        Examples:

             >>> from zope.configuration.config import ConfigurationContext
             >>> from zope.configuration.config import ConfigurationError
             >>> c = ConfigurationContext()
             >>> import zope, zope.interface
             >>> c.resolve('zope') is zope
             True
             >>> c.resolve('zope.interface') is zope.interface
             True
             >>> c.resolve('zope.configuration.eek') #doctest: +NORMALIZE_WHITESPACE
             Traceback (most recent call last):
             ...
             ConfigurationError:
             ImportError: Module zope.configuration has no global eek

             >>> c.resolve('.config.ConfigurationContext')
             Traceback (most recent call last):
             ...
             AttributeError: 'ConfigurationContext' object has no attribute 'package'
             >>> import zope.configuration
             >>> c.package = zope.configuration
             >>> c.resolve('.') is zope.configuration
             True
             >>> c.resolve('.config.ConfigurationContext') is ConfigurationContext
             True
             >>> c.resolve('..interface') is zope.interface
             True
             >>> c.resolve('str') is str
             True
        """
        name = dottedname.strip()

        if not name:
            raise ValueError("The given name is blank")

        if name == '.':
            return self.package

        names = name.split('.')

        if not names[-1]:
            raise ValueError(
                "Trailing dots are no longer supported in dotted names")

        if len(names) == 1:
            # Check for built-in objects
            marker = object()
            obj = getattr(builtins, names[0], marker)
            if obj is not marker:
                return obj

        if not names[0]:
            # Got a relative name. Convert it to abs using package info
            if self.package is None:
                raise ConfigurationError(
                    "Can't use leading dots in dotted names, "
                    "no package has been set.")
            pnames = self.package.__name__.split(".")
            pnames.append('')
            while names and not names[0]:
                names.pop(0)
                try:
                    pnames.pop()
                except IndexError:
                    raise ConfigurationError("Invalid global name", name)
            names[0:0] = pnames

        # Now we should have an absolute dotted name

        # Split off object name:
        oname, mname = names[-1], '.'.join(names[:-1])

        # Import the module
        if not mname:
            # Just got a single name. Must me a module
            mname = oname
            oname = ''

        try:
            # Without a fromlist, this returns the package rather than the
            # module if the name contains a dot.  Using a fromlist requires
            # star imports to work, which may not be true if there are
            # unicode items in __all__ due to unicode_literals on Python 2.
            # Getting the module from sys.modules instead avoids both
            # problems.
            __import__(mname)
            mod = sys.modules[mname]
        except ImportError as v:
            if sys.exc_info()[2].tb_next is not None:
                # ImportError was caused deeper
                raise
            raise ConfigurationError(
                "ImportError: Couldn't import %s, %s" % (mname, v))

        if not oname:
            # see not mname case above
            return mod


        try:
            obj = getattr(mod, oname)
            return obj
        except AttributeError:
            # No such name, maybe it's a module that we still need to import
            try:
                moname = mname + '.' + oname
                __import__(moname)
                return sys.modules[moname]
            except ImportError:
                if sys.exc_info()[2].tb_next is not None:
                    # ImportError was caused deeper
                    raise
                raise ConfigurationError(
                    "ImportError: Module %s has no global %s" % (mname, oname))

    def path(self, filename):
        """
        Compute package-relative paths.

        Examples:

             >>> import os
             >>> from zope.configuration.config import ConfigurationContext
             >>> c = ConfigurationContext()
             >>> c.path("/x/y/z") == os.path.normpath("/x/y/z")
             True
             >>> c.path("y/z")
             Traceback (most recent call last):
             ...
             AttributeError: 'ConfigurationContext' object has no attribute 'package'
             >>> import zope.configuration
             >>> c.package = zope.configuration
             >>> import os
             >>> d = os.path.dirname(zope.configuration.__file__)
             >>> c.path("y/z") == d + os.path.normpath("/y/z")
             True
             >>> c.path("y/./z") == d + os.path.normpath("/y/z")
             True
             >>> c.path("y/../z") == d + os.path.normpath("/z")
             True

        """
        filename, needs_processing = PathProcessor.expand(filename)

        if not needs_processing:
            return filename

        # Got a relative path, combine with base path.
        # If we have no basepath, compute the base path from the package
        # path.
        basepath = getattr(self, 'basepath', '')

        if not basepath:
            if self.package is None:
                basepath = os.getcwd()
            else:
                if hasattr(self.package, '__path__'):
                    basepath = self.package.__path__[0]
                else:
                    basepath = os.path.dirname(self.package.__file__)
                basepath = os.path.abspath(os.path.normpath(basepath))
            self.basepath = basepath

        return os.path.normpath(os.path.join(basepath, filename))

    def checkDuplicate(self, filename):
        """
        Check for duplicate imports of the same file.

        Raises an exception if this file had been processed before.
        This is better than an unlimited number of conflict errors.

        Examples:

             >>> from zope.configuration.config import ConfigurationContext
             >>> from zope.configuration.config import ConfigurationError
             >>> c = ConfigurationContext()
             >>> c.checkDuplicate('/foo.zcml')
             >>> try:
             ...     c.checkDuplicate('/foo.zcml')
             ... except ConfigurationError as e:
             ...     # On Linux the exact msg has /foo, on Windows \\foo.
             ...     str(e).endswith("foo.zcml' included more than once")
             True

        You may use different ways to refer to the same file:

             >>> import zope.configuration
             >>> c.package = zope.configuration
             >>> import os
             >>> d = os.path.dirname(zope.configuration.__file__)
             >>> c.checkDuplicate('bar.zcml')
             >>> try:
             ...   c.checkDuplicate(d + os.path.normpath('/bar.zcml'))
             ... except ConfigurationError as e:
             ...   str(e).endswith("bar.zcml' included more than once")
             ...
             True

        """
        path = self.path(filename)
        if path in self._seen_files:
            raise ConfigurationError('%r included more than once' % path)
        self._seen_files.add(path)

    def processFile(self, filename):
        """
        Check whether a file needs to be processed.

        Return True if processing is needed and False otherwise. If
        the file needs to be processed, it will be marked as
        processed, assuming that the caller will procces the file if
        it needs to be procssed.

        Examples:

             >>> from zope.configuration.config import ConfigurationContext
             >>> c = ConfigurationContext()
             >>> c.processFile('/foo.zcml')
             True
             >>> c.processFile('/foo.zcml')
             False

        You may use different ways to refer to the same file:

             >>> import zope.configuration
             >>> c.package = zope.configuration
             >>> import os
             >>> d = os.path.dirname(zope.configuration.__file__)
             >>> c.processFile('bar.zcml')
             True
             >>> c.processFile(os.path.join(d, 'bar.zcml'))
             False
        """
        path = self.path(filename)
        if path in self._seen_files:
            return False
        self._seen_files.add(path)
        return True

    def action(self, discriminator, callable=None, args=(), kw=None, order=0,
               includepath=None, info=None, **extra):
        """
        Add an action with the given discriminator, callable and
        arguments.

        For testing purposes, the callable and arguments may be
        omitted. In that case, a default noop callable is used.

        The discriminator must be given, but it can be None, to
        indicate that the action never conflicts.


        Examples:

             >>> from zope.configuration.config import ConfigurationContext
             >>> c = ConfigurationContext()

        Normally, the context gets actions from subclasses. We'll provide
        an actions attribute ourselves:

             >>> c.actions = []

        We'll use a test callable that has a convenient string representation

             >>> from zope.configuration.tests.directives import f
             >>> c.action(1, f, (1, ), {'x': 1})
             >>> from pprint import PrettyPrinter
             >>> pprint = PrettyPrinter(width=60).pprint
             >>> pprint(c.actions)
             [{'args': (1,),
               'callable': f,
               'discriminator': 1,
               'includepath': (),
               'info': '',
               'kw': {'x': 1},
               'order': 0}]

             >>> c.action(None)
             >>> pprint(c.actions)
             [{'args': (1,),
               'callable': f,
               'discriminator': 1,
               'includepath': (),
               'info': '',
               'kw': {'x': 1},
               'order': 0},
              {'args': (),
               'callable': None,
               'discriminator': None,
               'includepath': (),
               'info': '',
               'kw': {},
               'order': 0}]

        Now set the include path and info:

             >>> c.includepath = ('foo.zcml',)
             >>> c.info = "?"
             >>> c.action(None)
             >>> pprint(c.actions[-1])
             {'args': (),
              'callable': None,
              'discriminator': None,
              'includepath': ('foo.zcml',),
              'info': '?',
              'kw': {},
              'order': 0}

        We can add an order argument to crudely control the order
        of execution:

             >>> c.action(None, order=99999)
             >>> pprint(c.actions[-1])
             {'args': (),
              'callable': None,
              'discriminator': None,
              'includepath': ('foo.zcml',),
              'info': '?',
              'kw': {},
              'order': 99999}

        We can also pass an includepath argument, which will be used as the the
        includepath for the action.  (if includepath is None, self.includepath
        will be used):

             >>> c.action(None, includepath=('abc',))
             >>> pprint(c.actions[-1])
             {'args': (),
              'callable': None,
              'discriminator': None,
              'includepath': ('abc',),
              'info': '?',
              'kw': {},
              'order': 0}

        We can also pass an info argument, which will be used as the the
        source line info for the action.  (if info is None, self.info will be
        used):

             >>> c.action(None, info='abc')
             >>> pprint(c.actions[-1])
             {'args': (),
              'callable': None,
              'discriminator': None,
              'includepath': ('foo.zcml',),
              'info': 'abc',
              'kw': {},
              'order': 0}

        """
        if kw is None:
            kw = {}

        action = extra

        if info is None:
            info = getattr(self, 'info', '')

        if includepath is None:
            includepath = getattr(self, 'includepath', ())

        action.update(
            dict(
                discriminator=discriminator,
                callable=callable,
                args=args,
                kw=kw,
                includepath=includepath,
                info=info,
                order=order,
                )
            )

        self.actions.append(action)

    def hasFeature(self, feature):
        """
        Check whether a named feature has been provided.

        Initially no features are provided.

        Examples:

            >>> from zope.configuration.config import ConfigurationContext
            >>> c = ConfigurationContext()
            >>> c.hasFeature('onlinehelp')
            False

        You can declare that a feature is provided

            >>> c.provideFeature('onlinehelp')

        and it becomes available

            >>> c.hasFeature('onlinehelp')
            True
        """
        return feature in self._features

    def provideFeature(self, feature):
        """
        Declare that a named feature has been provided.

        See :meth:`hasFeature` for examples.
        """
        self._features.add(feature)


class ConfigurationAdapterRegistry(object):
    """
    Simple adapter registry that manages directives as adapters.

    Examples:

        >>> from zope.configuration.interfaces import IConfigurationContext
        >>> from zope.configuration.config import ConfigurationAdapterRegistry
        >>> from zope.configuration.config import ConfigurationError
        >>> from zope.configuration.config import ConfigurationMachine
        >>> r = ConfigurationAdapterRegistry()
        >>> c = ConfigurationMachine()
        >>> r.factory(c, ('http://www.zope.com', 'xxx'))
        Traceback (most recent call last):
        ...
        ConfigurationError: ('Unknown directive', 'http://www.zope.com', 'xxx')
        >>> def f():
        ...     pass

        >>> r.register(IConfigurationContext, ('http://www.zope.com', 'xxx'), f)
        >>> r.factory(c, ('http://www.zope.com', 'xxx')) is f
        True
        >>> r.factory(c, ('http://www.zope.com', 'yyy')) is f
        Traceback (most recent call last):
        ...
        ConfigurationError: ('Unknown directive', 'http://www.zope.com', 'yyy')
        >>> r.register(IConfigurationContext, 'yyy', f)
        >>> r.factory(c, ('http://www.zope.com', 'yyy')) is f
        True

    Test the documentation feature:

        >>> from zope.configuration.config import IFullInfo
        >>> r._docRegistry
        []
        >>> r.document(('ns', 'dir'), IFullInfo, IConfigurationContext, None,
        ...            'inf', None)
        >>> r._docRegistry[0][0] == ('ns', 'dir')
        True
        >>> r._docRegistry[0][1] is IFullInfo
        True
        >>> r._docRegistry[0][2] is IConfigurationContext
        True
        >>> r._docRegistry[0][3] is None
        True
        >>> r._docRegistry[0][4] == 'inf'
        True
        >>> r._docRegistry[0][5] is None
        True
        >>> r.document('all-dir', None, None, None, None)
        >>> r._docRegistry[1][0]
        ('', 'all-dir')
    """

    def __init__(self):
        super(ConfigurationAdapterRegistry, self).__init__()
        self._registry = {}
        # Stores tuples of form:
        #   (namespace, name), schema, usedIn, info, parent
        self._docRegistry = []

    def register(self, interface, name, factory):
        r = self._registry.get(name)
        if r is None:
            r = AdapterRegistry()
            self._registry[name] = r

        r.register([interface], Interface, '', factory)

    def document(self, name, schema, usedIn, handler, info, parent=None):
        if isinstance(name, string_types):
            name = ('', name)
        self._docRegistry.append((name, schema, usedIn, handler, info, parent))

    def factory(self, context, name):
        r = self._registry.get(name)
        if r is None:
            # Try namespace-independent name
            ns, n = name
            r = self._registry.get(n)
            if r is None:
                raise ConfigurationError("Unknown directive", ns, n)

        f = r.lookup1(providedBy(context), Interface)
        if f is None:
            raise ConfigurationError(
                "The directive %s cannot be used in this context" % (name, ))
        return f

@implementer(IConfigurationContext)
class ConfigurationMachine(ConfigurationAdapterRegistry, ConfigurationContext):
    """
    Configuration machine.

    Example:

      >>> from zope.configuration.config import ConfigurationMachine
      >>> machine = ConfigurationMachine()
      >>> ns = "http://www.zope.org/testing"

    Register a directive:

      >>> from zope.configuration.config import metans
      >>> machine((metans, "directive"),
      ...         namespace=ns, name="simple",
      ...         schema="zope.configuration.tests.directives.ISimple",
      ...         handler="zope.configuration.tests.directives.simple")

    and try it out:

      >>> machine((ns, "simple"), a=u"aa", c=u"cc")
      >>> from pprint import PrettyPrinter
      >>> pprint = PrettyPrinter(width=60).pprint
      >>> pprint(machine.actions)
      [{'args': ('aa', 'xxx', 'cc'),
        'callable': f,
        'discriminator': ('simple', 'aa', 'xxx', 'cc'),
        'includepath': (),
        'info': None,
        'kw': {},
        'order': 0}]
    """
    package = None
    basepath = None
    includepath = ()
    info = ''

    #: These `Exception` subclasses are allowed to be raised from `execute_actions`
    #: without being re-wrapped into a `~.ConfigurationError`. (`BaseException`
    #: and other `~.ConfigurationError` instances are never wrapped.)
    #:
    #: Users of instances of this class may modify this before calling `execute_actions`
    #: if they need to propagate specific exceptions.
    #:
    #: .. versionadded:: 4.2.0
    pass_through_exceptions = ()

    def __init__(self):
        super(ConfigurationMachine, self).__init__()
        self.actions = []
        self.stack = [RootStackItem(self)]
        self.i18n_strings = {}
        _bootstrap(self)

    def begin(self, __name, __data=None, __info=None, **kw):
        if __data:
            if kw:
                raise TypeError("Can't provide a mapping object and keyword "
                                "arguments")
        else:
            __data = kw
        self.stack.append(self.stack[-1].contained(__name, __data, __info))

    def end(self):
        self.stack.pop().finish()

    def __call__(self, __name, __info=None, **__kw):
        self.begin(__name, __kw, __info)
        self.end()

    def getInfo(self):
        return self.stack[-1].context.info

    def setInfo(self, info):
        self.stack[-1].context.info = info

    def execute_actions(self, clear=True, testing=False):
        """
        Execute the configuration actions.

        This calls the action callables after resolving conflicts.

        For example:

            >>> from zope.configuration.config import ConfigurationMachine
            >>> output = []
            >>> def f(*a, **k):
            ...    output.append(('f', a, k))
            >>> context = ConfigurationMachine()
            >>> context.actions = [
            ...   (1, f, (1,)),
            ...   (1, f, (11,), {}, ('x', )),
            ...   (2, f, (2,)),
            ...   ]
            >>> context.execute_actions()
            >>> output
            [('f', (1,), {}), ('f', (2,), {})]

        If the action raises an error, we convert it to a
        `~.ConfigurationError`.

            >>> output = []
            >>> def bad():
            ...    bad.xxx
            >>> context.actions = [
            ...   (1, f, (1,)),
            ...   (1, f, (11,), {}, ('x', )),
            ...   (2, f, (2,)),
            ...   (3, bad, (), {}, (), 'oops')
            ...   ]

            >>> context.execute_actions()
            Traceback (most recent call last):
            ...
            zope.configuration.config.ConfigurationExecutionError: oops
                AttributeError: 'function' object has no attribute 'xxx'

        Note that actions executed before the error still have an effect:

            >>> output
            [('f', (1,), {}), ('f', (2,), {})]

        If the exception was already a `~.ConfigurationError`, it is raised
        as-is with the action's ``info`` added.

            >>> def bad():
            ...     raise ConfigurationError("I'm bad")
            >>> context.actions = [
            ...   (1, f, (1,)),
            ...   (1, f, (11,), {}, ('x', )),
            ...   (2, f, (2,)),
            ...   (3, bad, (), {}, (), 'oops')
            ...   ]
            >>> context.execute_actions()
            Traceback (most recent call last):
            ...
            zope.configuration.exceptions.ConfigurationError: I'm bad
                oops

        """
        pass_through_exceptions = self.pass_through_exceptions
        if testing:
            pass_through_exceptions = BaseException
        try:
            for action in resolveConflicts(self.actions):
                callable = action['callable']
                if callable is None:
                    continue
                args = action['args']
                kw = action['kw']
                info = action['info']
                try:
                    callable(*args, **kw)
                except ConfigurationError as ex:
                    ex.add_details(info)
                    raise
                except pass_through_exceptions:
                    raise
                except Exception:
                    # Wrap it up and raise.
                    reraise(ConfigurationExecutionError(info, sys.exc_info()[1]),
                            None, sys.exc_info()[2])
        finally:
            if clear:
                del self.actions[:]

class ConfigurationExecutionError(ConfigurationWrapperError):
    """
    An error occurred during execution of a configuration action
    """

##############################################################################
# Stack items

class IStackItem(Interface):
    """
    Configuration machine stack items

    Stack items are created when a directive is being processed.

    A stack item is created for each directive use.
    """

    def contained(name, data, info):
        """Begin processing a contained directive

        The data are a dictionary of attribute names mapped to unicode
        strings.

        The info argument is an object that can be converted to a
        string and that contains information about the directive.

        The begin method returns the next item to be placed on the stack.
        """

    def finish():
        """Finish processing a directive
        """

@implementer(IStackItem)
class SimpleStackItem(object):
    """
    Simple stack item

    A simple stack item can't have anything added after it.  It can
    only be removed.  It is used for simple directives and
    subdirectives, which can't contain other directives.

    It also defers any computation until the end of the directive
    has been reached.
    """
    #XXX why this *argdata hack instead of schema, data?
    def __init__(self, context, handler, info, *argdata):
        newcontext = GroupingContextDecorator(context)
        newcontext.info = info
        self.context = newcontext
        self.handler = handler
        self.argdata = argdata

    def contained(self, name, data, info):
        raise ConfigurationError("Invalid directive %s" % str(name))

    def finish(self):
        # We're going to use the context that was passed to us, which wasn't
        # created for the directive.  We want to set it's info to the one
        # passed to us while we make the call, so we'll save the old one
        # and restore it.
        context = self.context
        args = toargs(context, *self.argdata)
        actions = self.handler(context, **args)
        if actions:
            # we allow the handler to return nothing
            for action in actions:
                if not isinstance(action, dict):
                    action = expand_action(*action) # b/c
                context.action(**action)

@implementer(IStackItem)
class RootStackItem(object):
    """
    A root stack item.
    """

    def __init__(self, context):
        self.context = context

    def contained(self, name, data, info):
        """Handle a contained directive

        We have to compute a new stack item by getting a named adapter
        for the current context object.
        """
        factory = self.context.factory(self.context, name)
        if factory is None:
            raise ConfigurationError("Invalid directive", name)
        adapter = factory(self.context, data, info)
        return adapter

    def finish(self):
        pass

@implementer(IStackItem)
class GroupingStackItem(RootStackItem):
    """
    Stack item for a grouping directive

    A grouping stack item is in the stack when a grouping directive is
    being processed. Grouping directives group other directives.
    Often, they just manage common data, but they may also take
    actions, either before or after contained directives are executed.

    A grouping stack item is created with a grouping directive
    definition, a configuration context, and directive data.

    To see how this works, let's look at an example:

    We need a context. We'll just use a configuration machine

        >>> from zope.configuration.config import GroupingStackItem
        >>> from zope.configuration.config import ConfigurationMachine
        >>> context = ConfigurationMachine()

    We need a callable to use in configuration actions. We'll use a
    convenient one from the tests:

        >>> from zope.configuration.tests.directives import f

    We need a handler for the grouping directive. This is a class that
    implements a context decorator. The decorator must also provide
    ``before`` and ``after`` methods that are called before and after
    any contained directives are processed. We'll typically subclass
    ``GroupingContextDecorator``, which provides context decoration,
    and default ``before`` and ``after`` methods.

        >>> from zope.configuration.config import GroupingContextDecorator
        >>> class SampleGrouping(GroupingContextDecorator):
        ...    def before(self):
        ...       self.action(('before', self.x, self.y), f)
        ...    def after(self):
        ...       self.action(('after'), f)

    We'll use our decorator to decorate our initial context, providing
    keyword arguments x and y:

        >>> dec = SampleGrouping(context, x=1, y=2)

    Note that the keyword arguments are made attributes of the
    decorator.

    Now we'll create the stack item.

        >>> item = GroupingStackItem(dec)

    We still haven't called the before action yet, which we can verify
    by looking at the context actions:

        >>> context.actions
        []

    Subdirectives will get looked up as adapters of the context.

    We'll create a simple handler:

        >>> def simple(context, data, info):
        ...     context.action(("simple", context.x, context.y, data), f)
        ...     return info

    and register it with the context:

        >>> from zope.configuration.interfaces import IConfigurationContext
        >>> from zope.configuration.config import testns
        >>> context.register(IConfigurationContext, (testns, 'simple'), simple)

    This handler isn't really a propert handler, because it doesn't
    return a new context. It will do for this example.

    Now we'll call the contained method on the stack item:

        >>> item.contained((testns, 'simple'), {'z': 'zope'}, "someinfo")
        'someinfo'

    We can verify thet the simple method was called by looking at the
    context actions. Note that the before method was called before
    handling the contained directive.

        >>> from pprint import PrettyPrinter
        >>> pprint = PrettyPrinter(width=60).pprint

        >>> pprint(context.actions)
        [{'args': (),
          'callable': f,
          'discriminator': ('before', 1, 2),
          'includepath': (),
          'info': '',
          'kw': {},
          'order': 0},
         {'args': (),
          'callable': f,
          'discriminator': ('simple', 1, 2, {'z': 'zope'}),
          'includepath': (),
          'info': '',
          'kw': {},
          'order': 0}]

    Finally, we call finish, which calls the decorator after method:

        >>> item.finish()

        >>> pprint(context.actions)
        [{'args': (),
          'callable': f,
          'discriminator': ('before', 1, 2),
          'includepath': (),
          'info': '',
          'kw': {},
          'order': 0},
         {'args': (),
          'callable': f,
          'discriminator': ('simple', 1, 2, {'z': 'zope'}),
          'includepath': (),
          'info': '',
          'kw': {},
          'order': 0},
         {'args': (),
          'callable': f,
          'discriminator': 'after',
          'includepath': (),
          'info': '',
          'kw': {},
          'order': 0}]

    If there were no nested directives:

        >>> context = ConfigurationMachine()
        >>> dec = SampleGrouping(context, x=1, y=2)
        >>> item = GroupingStackItem(dec)
        >>> item.finish()

    Then before will be when we call finish:

        >>> pprint(context.actions)
        [{'args': (),
          'callable': f,
          'discriminator': ('before', 1, 2),
          'includepath': (),
          'info': '',
          'kw': {},
          'order': 0},
         {'args': (),
          'callable': f,
          'discriminator': 'after',
          'includepath': (),
          'info': '',
          'kw': {},
          'order': 0}]
    """

    def __init__(self, context):
        super(GroupingStackItem, self).__init__(context)

    def __callBefore(self):
        actions = self.context.before()
        if actions:
            for action in actions:
                if not isinstance(action, dict):
                    action = expand_action(*action)
                self.context.action(**action)
        self.__callBefore = noop

    def contained(self, name, data, info):
        self.__callBefore()
        return RootStackItem.contained(self, name, data, info)

    def finish(self):
        self.__callBefore()
        actions = self.context.after()
        if actions:
            for action in actions:
                if not isinstance(action, dict):
                    action = expand_action(*action)
                self.context.action(**action)

def noop():
    pass


@implementer(IStackItem)
class ComplexStackItem(object):
    """
    Complex stack item

    A complex stack item is in the stack when a complex directive is
    being processed. It only allows subdirectives to be used.

    A complex stack item is created with a complex directive
    definition (IComplexDirectiveContext), a configuration context,
    and directive data.

    To see how this works, let's look at an example:

    We need a context. We'll just use a configuration machine

        >>> from zope.configuration.config import ConfigurationMachine
        >>> context = ConfigurationMachine()

    We need a callable to use in configuration actions. We'll use a
    convenient one from the tests:

        >>> from zope.configuration.tests.directives import f

    We need a handler for the complex directive. This is a class with
    a method for each subdirective:

        >>> class Handler(object):
        ...   def __init__(self, context, x, y):
        ...      self.context, self.x, self.y = context, x, y
        ...      context.action('init', f)
        ...   def sub(self, context, a, b):
        ...      context.action(('sub', a, b), f)
        ...   def __call__(self):
        ...      self.context.action(('call', self.x, self.y), f)

    We need a complex directive definition:

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        >>> from zope.configuration.config import ComplexDirectiveDefinition
        >>> class Ixy(Interface):
        ...    x = TextLine()
        ...    y = TextLine()
        >>> definition = ComplexDirectiveDefinition(
        ...        context, name="test", schema=Ixy,
        ...        handler=Handler)
        >>> class Iab(Interface):
        ...    a = TextLine()
        ...    b = TextLine()
        >>> definition['sub'] = Iab, ''

    OK, now that we have the context, handler and definition, we're
    ready to use a stack item.

        >>> from zope.configuration.config import ComplexStackItem
        >>> item = ComplexStackItem(definition, context, {'x': u'xv', 'y': u'yv'},
        ...                         'foo')

    When we created the definition, the handler (factory) was called.

        >>> from pprint import PrettyPrinter
        >>> pprint = PrettyPrinter(width=60).pprint
        >>> pprint(context.actions)
        [{'args': (),
          'callable': f,
          'discriminator': 'init',
          'includepath': (),
          'info': 'foo',
          'kw': {},
          'order': 0}]

    If a subdirective is provided, the ``contained`` method of the
    stack item is called. It will lookup the subdirective schema and
    call the corresponding method on the handler instance:

        >>> simple = item.contained(('somenamespace', 'sub'),
        ...                         {'a': u'av', 'b': u'bv'}, 'baz')
        >>> simple.finish()

    Note that the name passed to ``contained`` is a 2-part name,
    consisting of a namespace and a name within the namespace.

        >>> pprint(context.actions)
        [{'args': (),
          'callable': f,
          'discriminator': 'init',
          'includepath': (),
          'info': 'foo',
          'kw': {},
          'order': 0},
         {'args': (),
          'callable': f,
          'discriminator': ('sub', 'av', 'bv'),
          'includepath': (),
          'info': 'baz',
          'kw': {},
          'order': 0}]

    The new stack item returned by contained is one that doesn't allow
    any more subdirectives,

    When all of the subdirectives have been provided, the ``finish``
    method is called:

        >>> item.finish()

    The stack item will call the handler if it is callable.

        >>> pprint(context.actions)
        [{'args': (),
          'callable': f,
          'discriminator': 'init',
          'includepath': (),
          'info': 'foo',
          'kw': {},
          'order': 0},
         {'args': (),
          'callable': f,
          'discriminator': ('sub', 'av', 'bv'),
          'includepath': (),
          'info': 'baz',
          'kw': {},
          'order': 0},
         {'args': (),
          'callable': f,
          'discriminator': ('call', 'xv', 'yv'),
          'includepath': (),
          'info': 'foo',
          'kw': {},
          'order': 0}]
    """
    def __init__(self, meta, context, data, info):
        newcontext = GroupingContextDecorator(context)
        newcontext.info = info
        self.context = newcontext
        self.meta = meta

        # Call the handler contructor
        args = toargs(newcontext, meta.schema, data)
        self.handler = self.meta.handler(newcontext, **args)

    def contained(self, name, data, info):
        """Handle a subdirective
        """
        # Look up the subdirective meta data on our meta object
        ns, name = name
        schema = self.meta.get(name)
        if schema is None:
            raise ConfigurationError("Invalid directive", name)
        schema = schema[0] # strip off info
        handler = getattr(self.handler, name)
        return SimpleStackItem(self.context, handler, info, schema, data)

    def finish(self):
        # when we're done, we call the handler, which might return more actions
        # Need to save and restore old info
        # XXX why not just use callable()?
        try:
            actions = self.handler()
        except AttributeError as v:
            if v.args[0] == '__call__':
                return # noncallable
            raise
        except TypeError:
            return # non callable

        if actions:
            # we allow the handler to return nothing
            for action in actions:
                if not isinstance(action, dict):
                    action = expand_action(*action)
                self.context.action(**action)


##############################################################################
# Helper classes

@implementer(IConfigurationContext, IGroupingContext)
class GroupingContextDecorator(ConfigurationContext):
    """Helper mix-in class for building grouping directives

    See the discussion (and test) in GroupingStackItem.
    """

    def __init__(self, context, **kw):
        self.context = context
        for name, v in kw.items():
            setattr(self, name, v)

    def __getattr__(self, name):
        v = getattr(self.context, name)
        # cache result in self
        setattr(self, name, v)
        return v

    def before(self):
        pass

    def after(self):
        pass

##############################################################################
# Directive-definition

class DirectiveSchema(GlobalInterface):
    """A field that contains a global variable value that must be a schema
    """

class IDirectivesInfo(Interface):
    """Schema for the ``directives`` directive
    """

    namespace = URI(
        title=u"Namespace",
        description=(
            u"The namespace in which directives' names "
            u"will be defined"),
    )


class IDirectivesContext(IDirectivesInfo, IConfigurationContext):
    pass


@implementer(IDirectivesContext)
class DirectivesHandler(GroupingContextDecorator):
    """Handler for the directives directive

    This is just a grouping directive that adds a namespace attribute
    to the normal directive context.

    """


class IDirectiveInfo(Interface):
    """Information common to all directive definitions.
    """

    name = TextLine(
        title=u"Directive name",
        description=u"The name of the directive being defined",
    )

    schema = DirectiveSchema(
        title=u"Directive handler",
        description=u"The dotted name of the directive handler",
    )


class IFullInfo(IDirectiveInfo):
    """Information that all top-level directives (not subdirectives)
    have.
    """

    handler = GlobalObject(
        title=u"Directive handler",
        description=u"The dotted name of the directive handler",
    )

    usedIn = GlobalInterface(
        title=u"The directive types the directive can be used in",
        description=(
            u"The interface of the directives that can contain "
            u"the directive"
        ),
        default=IConfigurationContext,
    )


class IStandaloneDirectiveInfo(IDirectivesInfo, IFullInfo):
    """Info for full directives defined outside a directives directives
    """

def defineSimpleDirective(context, name, schema, handler,
                          namespace='', usedIn=IConfigurationContext):
    """
    Define a simple directive

    Define and register a factory that invokes the simple directive
    and returns a new stack item, which is always the same simple
    stack item.

    If the namespace is '*', the directive is registered for all
    namespaces.

    Example:

        >>> from zope.configuration.config import ConfigurationMachine
        >>> context = ConfigurationMachine()
        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        >>> from zope.configuration.tests.directives import f
        >>> class Ixy(Interface):
        ...    x = TextLine()
        ...    y = TextLine()
        >>> def s(context, x, y):
        ...    context.action(('s', x, y), f)

        >>> from zope.configuration.config import defineSimpleDirective
        >>> defineSimpleDirective(context, 's', Ixy, s, testns)

        >>> context((testns, "s"), x=u"vx", y=u"vy")
        >>> from pprint import PrettyPrinter
        >>> pprint = PrettyPrinter(width=60).pprint
        >>> pprint(context.actions)
        [{'args': (),
          'callable': f,
          'discriminator': ('s', 'vx', 'vy'),
          'includepath': (),
          'info': None,
          'kw': {},
          'order': 0}]

        >>> context(('http://www.zope.com/t1', "s"), x=u"vx", y=u"vy")
        Traceback (most recent call last):
        ...
        ConfigurationError: ('Unknown directive', 'http://www.zope.com/t1', 's')

        >>> context = ConfigurationMachine()
        >>> defineSimpleDirective(context, 's', Ixy, s, "*")

        >>> context(('http://www.zope.com/t1', "s"), x=u"vx", y=u"vy")
        >>> pprint(context.actions)
        [{'args': (),
          'callable': f,
          'discriminator': ('s', 'vx', 'vy'),
          'includepath': (),
          'info': None,
          'kw': {},
          'order': 0}]
    """
    namespace = namespace or context.namespace
    if namespace != '*':
        name = namespace, name

    def factory(context, data, info):
        return SimpleStackItem(context, handler, info, schema, data)
    factory.schema = schema

    context.register(usedIn, name, factory)
    context.document(name, schema, usedIn, handler, context.info)

def defineGroupingDirective(context, name, schema, handler,
                            namespace='', usedIn=IConfigurationContext):
    """
    Define a grouping directive

    Define and register a factory that sets up a grouping directive.

    If the namespace is '*', the directive is registered for all
    namespaces.

    Example:

        >>> from zope.configuration.config import ConfigurationMachine
        >>> context = ConfigurationMachine()
        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        >>> from zope.configuration.tests.directives import f
        >>> class Ixy(Interface):
        ...    x = TextLine()
        ...    y = TextLine()

    We won't bother creating a special grouping directive class. We'll
    just use :class:`GroupingContextDecorator`, which simply sets up a
    grouping context that has extra attributes defined by a schema:

        >>> from zope.configuration.config import defineGroupingDirective
        >>> from zope.configuration.config import GroupingContextDecorator
        >>> defineGroupingDirective(context, 'g', Ixy,
        ...                         GroupingContextDecorator, testns)

        >>> context.begin((testns, "g"), x=u"vx", y=u"vy")
        >>> context.stack[-1].context.x
        'vx'
        >>> context.stack[-1].context.y
        'vy'

        >>> context(('http://www.zope.com/t1', "g"), x=u"vx", y=u"vy")
        Traceback (most recent call last):
        ...
        ConfigurationError: ('Unknown directive', 'http://www.zope.com/t1', 'g')

        >>> context = ConfigurationMachine()
        >>> defineGroupingDirective(context, 'g', Ixy,
        ...                         GroupingContextDecorator, "*")

        >>> context.begin(('http://www.zope.com/t1', "g"), x=u"vx", y=u"vy")
        >>> context.stack[-1].context.x
        'vx'
        >>> context.stack[-1].context.y
        'vy'
    """
    namespace = namespace or context.namespace
    if namespace != '*':
        name = namespace, name

    def factory(context, data, info):
        args = toargs(context, schema, data)
        newcontext = handler(context, **args)
        newcontext.info = info
        return GroupingStackItem(newcontext)
    factory.schema = schema

    context.register(usedIn, name, factory)
    context.document(name, schema, usedIn, handler, context.info)


class IComplexDirectiveContext(IFullInfo, IConfigurationContext):
    pass


@implementer(IComplexDirectiveContext)
class ComplexDirectiveDefinition(GroupingContextDecorator, dict):
    """Handler for defining complex directives

    See the description and tests for ComplexStackItem.
    """
    def before(self):

        def factory(context, data, info):
            return ComplexStackItem(self, context, data, info)
        factory.schema = self.schema

        self.register(self.usedIn, (self.namespace, self.name), factory)
        self.document((self.namespace, self.name), self.schema, self.usedIn,
                      self.handler, self.info)

def subdirective(context, name, schema):
    context.document((context.namespace, name), schema, context.usedIn,
                     getattr(context.handler, name, context.handler),
                     context.info, context.context)
    context.context[name] = schema, context.info

##############################################################################
# Features

class IProvidesDirectiveInfo(Interface):
    """Information for a <meta:provides> directive"""

    feature = TextLine(
        title=u"Feature name",
        description=u"""The name of the feature being provided

        You can test available features with zcml:condition="have featurename".
        """,
    )

def provides(context, feature):
    """
    Declare that a feature is provided in context.

    Example:

        >>> from zope.configuration.config import ConfigurationContext
        >>> from zope.configuration.config import provides
        >>> c = ConfigurationContext()
        >>> provides(c, 'apidoc')
        >>> c.hasFeature('apidoc')
        True

    Spaces are not allowed in feature names (this is reserved for
    providing many features with a single directive in the future).

        >>> provides(c, 'apidoc onlinehelp')
        Traceback (most recent call last):
          ...
        ValueError: Only one feature name allowed

        >>> c.hasFeature('apidoc onlinehelp')
        False
    """
    if len(feature.split()) > 1:
        raise ValueError("Only one feature name allowed")
    context.provideFeature(feature)


##############################################################################
# Argument conversion

def toargs(context, schema, data):
    """
    Marshal data to an argument dictionary using a schema

    Names that are python keywords have an underscore added as a
    suffix in the schema and in the argument list, but are used
    without the underscore in the data.

    The fields in the schema must all implement IFromUnicode.

    All of the items in the data must have corresponding fields in the
    schema unless the schema has a true tagged value named
    'keyword_arguments'.

    Example:

        >>> from zope.configuration.config import toargs
        >>> from zope.schema import BytesLine
        >>> from zope.schema import Float
        >>> from zope.schema import Int
        >>> from zope.schema import TextLine
        >>> from zope.schema import URI
        >>> class schema(Interface):
        ...     in_ = Int(constraint=lambda v: v > 0)
        ...     f = Float()
        ...     n = TextLine(min_length=1, default=u"rob")
        ...     x = BytesLine(required=False)
        ...     u = URI()

        >>> context = ConfigurationMachine()
        >>> from pprint import PrettyPrinter
        >>> pprint = PrettyPrinter(width=50).pprint

        >>> pprint(toargs(context, schema,
        ...        {'in': u'1', 'f': u'1.2', 'n': u'bob', 'x': u'x.y.z',
        ...          'u': u'http://www.zope.org' }))
        {'f': 1.2,
         'in_': 1,
         'n': 'bob',
         'u': 'http://www.zope.org',
         'x': b'x.y.z'}

    If we have extra data, we'll get an error:

        >>> toargs(context, schema,
        ...        {'in': u'1', 'f': u'1.2', 'n': u'bob', 'x': u'x.y.z',
        ...          'u': u'http://www.zope.org', 'a': u'1'})
        Traceback (most recent call last):
        ...
        ConfigurationError: ('Unrecognized parameters:', 'a')

    Unless we set a tagged value to say that extra arguments are ok:

        >>> schema.setTaggedValue('keyword_arguments', True)

        >>> pprint(toargs(context, schema,
        ...        {'in': u'1', 'f': u'1.2', 'n': u'bob', 'x': u'x.y.z',
        ...          'u': u'http://www.zope.org', 'a': u'1'}))
        {'a': '1',
         'f': 1.2,
         'in_': 1,
         'n': 'bob',
         'u': 'http://www.zope.org',
         'x': b'x.y.z'}

    If we omit required data we get an error telling us what was
    omitted:

        >>> pprint(toargs(context, schema,
        ...        {'in': u'1', 'f': u'1.2', 'n': u'bob', 'x': u'x.y.z'}))
        Traceback (most recent call last):
        ...
        ConfigurationError: ('Missing parameter:', 'u')

    Although we can omit not-required data:

        >>> pprint(toargs(context, schema,
        ...        {'in': u'1', 'f': u'1.2', 'n': u'bob',
        ...          'u': u'http://www.zope.org', 'a': u'1'}))
        {'a': '1',
         'f': 1.2,
         'in_': 1,
         'n': 'bob',
         'u': 'http://www.zope.org'}

    And we can omit required fields if they have valid defaults
    (defaults that are valid values):

        >>> pprint(toargs(context, schema,
        ...        {'in': u'1', 'f': u'1.2',
        ...          'u': u'http://www.zope.org', 'a': u'1'}))
        {'a': '1',
         'f': 1.2,
         'in_': 1,
         'n': 'rob',
         'u': 'http://www.zope.org'}

    We also get an error if any data was invalid:

        >>> pprint(toargs(context, schema,
        ...        {'in': u'0', 'f': u'1.2', 'n': u'bob', 'x': u'x.y.z',
        ...          'u': u'http://www.zope.org', 'a': u'1'}))
        Traceback (most recent call last):
        ...
        ConfigurationError: ('Invalid value for', 'in', '0')
    """
    data = dict(data)
    args = {}
    for name, field in schema.namesAndDescriptions(True):
        field = field.bind(context)
        n = name
        if n.endswith('_') and iskeyword(n[:-1]):
            n = n[:-1]

        s = data.get(n, data)
        if s is not data:
            s = text_type(s)
            del data[n]

            try:
                args[str(name)] = field.fromUnicode(s)
            except ValidationError as v:
                reraise(ConfigurationError("Invalid value for %r" % (n)).add_details(v),
                        None, sys.exc_info()[2])
        elif field.required:
            # if the default is valid, we can use that:
            default = field.default
            try:
                field.validate(default)
            except ValidationError as v:
                reraise(ConfigurationError("Missing parameter: %r" % (n,)).add_details(v),
                        None, sys.exc_info()[2])
            args[str(name)] = default

    if data:
        # we had data left over
        try:
            keyword_arguments = schema.getTaggedValue('keyword_arguments')
        except KeyError:
            keyword_arguments = False
        if not keyword_arguments:
            raise ConfigurationError("Unrecognized parameters:", *data)

        for name in data:
            args[str(name)] = data[name]

    return args

##############################################################################
# Conflict resolution

def expand_action(discriminator, callable=None, args=(), kw=None,
                  includepath=(), info=None, order=0, **extra):
    if kw is None:
        kw = {}
    action = extra
    action.update(
        dict(
            discriminator=discriminator,
            callable=callable,
            args=args,
            kw=kw,
            includepath=includepath,
            info=info,
            order=order,
            )
        )
    return action

def resolveConflicts(actions):
    """
    Resolve conflicting actions.

    Given an actions list, identify and try to resolve conflicting actions.
    Actions conflict if they have the same non-None discriminator.
    Conflicting actions can be resolved if the include path of one of
    the actions is a prefix of the includepaths of the other
    conflicting actions and is unequal to the include paths in the
    other conflicting actions.
    """

    # organize actions by discriminators
    unique = {}
    output = []
    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            # old-style tuple action
            action = expand_action(*action)

        # "order" is an integer grouping. Actions in a lower order will be
        # executed before actions in a higher order.  Within an order,
        # actions are executed sequentially based on original action ordering
        # ("i").
        order = action['order'] or 0
        discriminator = action['discriminator']

        # "ainfo" is a tuple of (order, i, action) where "order" is a
        # user-supplied grouping, "i" is an integer expressing the relative
        # position of this action in the action list being resolved, and
        # "action" is an action dictionary.  The purpose of an ainfo is to
        # associate an "order" and an "i" with a particular action; "order"
        # and "i" exist for sorting purposes after conflict resolution.
        ainfo = (order, i, action)

        if discriminator is None:
            # The discriminator is None, so this action can never conflict.
            # We can add it directly to the result.
            output.append(ainfo)
            continue

        L = unique.setdefault(discriminator, [])
        L.append(ainfo)

    # Check for conflicts
    conflicts = {}

    for discriminator, ainfos in unique.items():

        # We use (includepath, order, i) as a sort key because we need to
        # sort the actions by the paths so that the shortest path with a
        # given prefix comes first.  The "first" action is the one with the
        # shortest include path.  We break sorting ties using "order", then
        # "i".
        def bypath(ainfo):
            path, order, i = ainfo[2]['includepath'], ainfo[0], ainfo[1]
            return path, order, i

        ainfos.sort(key=bypath)
        ainfo, rest = ainfos[0], ainfos[1:]
        output.append(ainfo)
        _, _, action = ainfo
        basepath, baseinfo, discriminator = (action['includepath'],
                                             action['info'],
                                             action['discriminator'])

        for _, _, action in rest:
            includepath = action['includepath']
            # Test whether path is a prefix of opath
            if (includepath[:len(basepath)] != basepath # not a prefix
                or includepath == basepath):
                L = conflicts.setdefault(discriminator, [baseinfo])
                L.append(action['info'])

    if conflicts:
        raise ConfigurationConflictError(conflicts)

    # Sort conflict-resolved actions by (order, i) and return them.
    return [x[2] for x in sorted(output, key=operator.itemgetter(0, 1))]


class ConfigurationConflictError(ConfigurationError):

    def __init__(self, conflicts):
        super(ConfigurationConflictError, self).__init__()
        self._conflicts = conflicts

    def _with_details(self, opening, detail_formatter):
        r = ["Conflicting configuration actions"]
        for discriminator, infos in sorted(self._conflicts.items()):
            r.append("  For: %s" % (discriminator, ))
            for info in infos:
                for line in text_type(info).rstrip().split(u'\n'):
                    r.append(u"    " + line)

        opening = "\n".join(r)
        return super(ConfigurationConflictError, self)._with_details(opening, detail_formatter)


##############################################################################
# Bootstap code


def _bootstrap(context):

    # Set enough machinery to register other directives

    # Define the directive (simple directive) directive by calling it's
    # handler directly

    info = 'Manually registered in zope/configuration/config.py'

    context.info = info
    defineSimpleDirective(
        context,
        namespace=metans, name='directive',
        schema=IStandaloneDirectiveInfo,
        handler=defineSimpleDirective)
    context.info = ''

    # OK, now that we have that, we can use the machine to define the
    # other directives. This isn't the easiest way to proceed, but it lets
    # us eat our own dogfood. :)

    # Standalone groupingDirective
    context((metans, 'directive'),
            info,
            name='groupingDirective',
            namespace=metans,
            handler="zope.configuration.config.defineGroupingDirective",
            schema="zope.configuration.config.IStandaloneDirectiveInfo"
            )

    # Now we can use the grouping directive to define the directives directive
    context((metans, 'groupingDirective'),
            info,
            name='directives',
            namespace=metans,
            handler="zope.configuration.config.DirectivesHandler",
            schema="zope.configuration.config.IDirectivesInfo"
            )

    # directive and groupingDirective inside directives
    context((metans, 'directive'),
            info,
            name='directive',
            namespace=metans,
            usedIn="zope.configuration.config.IDirectivesContext",
            handler="zope.configuration.config.defineSimpleDirective",
            schema="zope.configuration.config.IFullInfo"
            )
    context((metans, 'directive'),
            info,
            name='groupingDirective',
            namespace=metans,
            usedIn="zope.configuration.config.IDirectivesContext",
            handler="zope.configuration.config.defineGroupingDirective",
            schema="zope.configuration.config.IFullInfo"
            )

    # Setup complex directive directive, both standalone, and in
    # directives directive
    context((metans, 'groupingDirective'),
            info,
            name='complexDirective',
            namespace=metans,
            handler="zope.configuration.config.ComplexDirectiveDefinition",
            schema="zope.configuration.config.IStandaloneDirectiveInfo"
            )
    context((metans, 'groupingDirective'),
            info,
            name='complexDirective',
            namespace=metans,
            usedIn="zope.configuration.config.IDirectivesContext",
            handler="zope.configuration.config.ComplexDirectiveDefinition",
            schema="zope.configuration.config.IFullInfo"
            )

    # Finally, setup subdirective directive
    context((metans, 'directive'),
            info,
            name='subdirective',
            namespace=metans,
            usedIn="zope.configuration.config.IComplexDirectiveContext",
            handler="zope.configuration.config.subdirective",
            schema="zope.configuration.config.IDirectiveInfo"
            )

    # meta:provides
    context((metans, 'directive'),
            info,
            name='provides',
            namespace=metans,
            handler="zope.configuration.config.provides",
            schema="zope.configuration.config.IProvidesDirectiveInfo"
            )
