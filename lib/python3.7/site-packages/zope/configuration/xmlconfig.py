##############################################################################
#
# Copyright (c) 2001, 2002, 2003 Zope Foundation and Contributors.
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
"""Support for the XML configuration file format

Note, for a detailed description of the way that conflicting
configuration actions are resolved, see the detailed example in
test_includeOverrides in tests/test_xmlconfig.py
"""
__docformat__ = 'restructuredtext'

import errno
from glob import glob
import logging
import io
import os
import sys
from xml.sax import make_parser
from xml.sax.xmlreader import InputSource
from xml.sax.handler import ContentHandler, feature_namespaces
from xml.sax import SAXParseException

from zope.interface import Interface
from zope.schema import NativeStringLine

from zope.configuration.config import ConfigurationMachine
from zope.configuration.config import defineGroupingDirective
from zope.configuration.config import defineSimpleDirective
from zope.configuration.config import GroupingContextDecorator
from zope.configuration.config import GroupingStackItem
from zope.configuration.config import resolveConflicts
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.exceptions import ConfigurationWrapperError
from zope.configuration.fields import GlobalObject
from zope.configuration.zopeconfigure import IZopeConfigure
from zope.configuration.zopeconfigure import ZopeConfigure
from zope.configuration._compat import reraise

__all__ = [
    'ParserInfo',
    'ConfigurationHandler',
    'processxmlfile',
    'openInOrPlain',
    'IInclude',
    'include',
    'exclude',
    'includeOverrides',
    'registerCommonDirectives',
    'file',
    'string',
    'XMLConfig',
    'xmlconfig',
    'testxmlconfig',
]

logger = logging.getLogger("config")

ZCML_NAMESPACE = "http://namespaces.zope.org/zcml"
ZCML_CONDITION = (ZCML_NAMESPACE, u"condition")


class ZopeXMLConfigurationError(ConfigurationWrapperError):
    """
    Zope XML Configuration error

    These errors are wrappers for other errors. They include
    configuration info and the wrapped error type and value.

    Example

        >>> from zope.configuration.xmlconfig import ZopeXMLConfigurationError
        >>> v = ZopeXMLConfigurationError("blah", AttributeError("xxx"))
        >>> print(v)
        'blah'
            AttributeError: xxx
    """

    USE_INFO_REPR = True


class ZopeSAXParseException(ConfigurationWrapperError):
    """
    Sax Parser errors as a ConfigurationError.

    Example

        >>> from zope.configuration.xmlconfig import ZopeSAXParseException
        >>> v = ZopeSAXParseException("info", Exception("foo.xml:12:3:Not well formed"))
        >>> print(v)
        info
            Exception: foo.xml:12:3:Not well formed
    """


class ParserInfo(object):
    r"""
    Information about a directive based on parser data

    This includes the directive location, as well as text data
    contained in the directive.

    Example

        >>> from zope.configuration.xmlconfig import ParserInfo
        >>> info = ParserInfo('tests//sample.zcml', 1, 0)
        >>> info
        File "tests//sample.zcml", line 1.0

        >>> print(info)
        File "tests//sample.zcml", line 1.0

        >>> info.characters("blah\n")
        >>> info.characters("blah")
        >>> info.text
        'blah\nblah'

        >>> info.end(7, 0)
        >>> info
        File "tests//sample.zcml", line 1.0-7.0

        >>> print(info)
        File "tests//sample.zcml", line 1.0-7.0
          <configure xmlns='http://namespaces.zope.org/zope'>
            <!-- zope.configure -->
            <directives namespace="http://namespaces.zope.org/zope">
              <directive name="hook" attributes="name implementation module"
                 handler="zope.configuration.metaconfigure.hook" />
            </directives>
          </configure>
    """
    text = u''

    def __init__(self, file, line, column):
        self.file, self.line, self.column = file, line, column
        self.eline, self.ecolumn = line, column

    def end(self, line, column):
        self.eline, self.ecolumn = line, column

    def __repr__(self):
        if (self.line, self.column) == (self.eline, self.ecolumn):
            return 'File "%s", line %s.%s' % (
                self.file, self.line, self.column)

        return 'File "%s", line %s.%s-%s.%s' % (
            self.file, self.line, self.column, self.eline, self.ecolumn)

    def __str__(self):
        if (self.line, self.column) == (self.eline, self.ecolumn):
            return 'File "%s", line %s.%s' % (
                self.file, self.line, self.column)

        file = self.file
        if file == 'tests//sample.zcml':
            # special case for testing
            file = os.path.join(os.path.dirname(__file__),
                                'tests', 'sample.zcml')

        try:
            with open(file) as f:
                lines = f.readlines()[self.line-1:self.eline]
        except IOError:
            src = "  Could not read source."
        else:
            ecolumn = self.ecolumn
            if lines[-1][ecolumn:ecolumn+2] == '</': # pragma: no cover
                # We're pointing to the start of an end tag. Try to find
                # the end
                l = lines[-1].find('>', ecolumn)
                if l >= 0:
                    lines[-1] = lines[-1][:l+1]
            else: # pragma: no cover
                lines[-1] = lines[-1][:ecolumn+1]

            column = self.column
            if lines[0][:column].strip(): # pragma: no cover
                # Remove text before start if it's noy whitespace
                lines[0] = lines[0][self.column:]

            pad = u'  '
            blank = u''
            try:
                src = blank.join([pad + l for l in lines])
            except UnicodeDecodeError: # pragma: no cover
                # XXX:
                # I hope so most internation zcml will use UTF-8 as encoding
                # otherwise this code must be made more clever
                src = blank.join([pad + l.decode('utf-8') for l in lines])
                # unicode won't be printable, at least on my console
                src = src.encode('ascii', 'replace')

        return "%s\n%s" % (repr(self), src)

    def characters(self, characters):
        self.text += characters


class ConfigurationHandler(ContentHandler):
    """
    Interface to the XML parser

    Translate parser events into calls into the configuration system.
    """
    locator = None

    def __init__(self, context, testing=False):
        self.context = context
        self.testing = testing
        self.ignore_depth = 0

    def setDocumentLocator(self, locator):
        self.locator = locator

    def characters(self, text):
        self.context.getInfo().characters(text)

    def _handle_exception(self, ex, info):
        if self.testing:
            raise
        if isinstance(ex, ConfigurationError):
            ex.add_details(repr(info))
            raise

        exc = ZopeXMLConfigurationError(info, ex)
        reraise(exc, None, sys.exc_info()[2])

    def startElementNS(self, name, qname, attrs):
        if self.ignore_depth:
            self.ignore_depth += 1
            return

        data = {}
        for (ns, aname), value in attrs.items():
            # NB: even though on CPython, 'ns' will be ``None`` always,
            # do not change the below to "if ns is None" because Jython's
            # sax parser generates attrs that have empty strings for
            # the namepace instead of ``None``.
            if not ns:
                aname = str(aname)
                data[aname] = value
            if (ns, aname) == ZCML_CONDITION:
                # need to process the expression to determine if we
                # use this element and it's descendents
                use = self.evaluateCondition(value)
                if not use:
                    self.ignore_depth = 1
                    return

        info = ParserInfo(
            self.locator.getSystemId(),
            self.locator.getLineNumber(),
            self.locator.getColumnNumber(),
            )

        try:
            self.context.begin(name, data, info)
        except Exception as ex:
            self._handle_exception(ex, info)

        self.context.setInfo(info)

    def evaluateCondition(self, expression):
        """
        Evaluate a ZCML condition.

        ``expression`` is a string of the form "verb arguments".

        Currently the supported verbs are ``have``, ``not-have``,
        ``installed`` and ``not-installed``.

        The ``have`` and ``not-have`` verbs each take one argument:
        the name of a feature:

            >>> from zope.configuration.config import ConfigurationContext
            >>> from zope.configuration.xmlconfig import ConfigurationHandler
            >>> context = ConfigurationContext()
            >>> context.provideFeature('apidoc')
            >>> c = ConfigurationHandler(context, testing=True)
            >>> c.evaluateCondition("have apidoc")
            True
            >>> c.evaluateCondition("not-have apidoc")
            False
            >>> c.evaluateCondition("have onlinehelp")
            False
            >>> c.evaluateCondition("not-have onlinehelp")
            True

        Ill-formed expressions raise an error:

            >>> c.evaluateCondition("want apidoc")
            Traceback (most recent call last):
              ...
            ValueError: Invalid ZCML condition: 'want apidoc'

            >>> c.evaluateCondition("have x y")
            Traceback (most recent call last):
              ...
            ValueError: Only one feature allowed: 'have x y'

            >>> c.evaluateCondition("have")
            Traceback (most recent call last):
              ...
            ValueError: Feature name missing: 'have'

        The ``installed`` and ``not-installed`` verbs each take one
        argument: the dotted name of a pacakge.

        If the pacakge is found, in other words, can be imported, then
        the condition will return true / false:

            >>> context = ConfigurationContext()
            >>> c = ConfigurationHandler(context, testing=True)
            >>> c.evaluateCondition('installed zope.interface')
            True
            >>> c.evaluateCondition('not-installed zope.interface')
            False
            >>> c.evaluateCondition('installed zope.foo')
            False
            >>> c.evaluateCondition('not-installed zope.foo')
            True

        Ill-formed expressions raise an error:

            >>> c.evaluateCondition("installed foo bar")
            Traceback (most recent call last):
              ...
            ValueError: Only one package allowed: 'installed foo bar'

            >>> c.evaluateCondition("installed")
            Traceback (most recent call last):
              ...
            ValueError: Package name missing: 'installed'
        """
        arguments = expression.split(None)
        verb = arguments.pop(0)

        if verb in ('have', 'not-have'):
            if not arguments:
                raise ValueError("Feature name missing: %r" % expression)
            if len(arguments) > 1:
                raise ValueError("Only one feature allowed: %r" % expression)

            if verb == 'have':
                return self.context.hasFeature(arguments[0])
            elif verb == 'not-have':
                return not self.context.hasFeature(arguments[0])

        elif verb in ('installed', 'not-installed'):
            if not arguments:
                raise ValueError("Package name missing: %r" % expression)
            if len(arguments) > 1:
                raise ValueError("Only one package allowed: %r" % expression)

            try:
                __import__(arguments[0])
                installed = True
            except ImportError:
                installed = False

            if verb == 'installed':
                return installed
            elif verb == 'not-installed':
                return not installed
        else:
            raise ValueError("Invalid ZCML condition: %r" % expression)

    def endElementNS(self, name, qname):
        # If ignore_depth is set, this element will be ignored, even
        # if this this decrements ignore_depth to 0.
        if self.ignore_depth:
            self.ignore_depth -= 1
            return

        info = self.context.getInfo()
        info.end(
            self.locator.getLineNumber(),
            self.locator.getColumnNumber(),
            )

        try:
            self.context.end()
        except Exception as ex:
            self._handle_exception(ex, info)


def processxmlfile(file, context, testing=False):
    """Process a configuration file

    See examples in tests/test_xmlconfig.py
    """
    src = InputSource(getattr(file, 'name', '<string>'))
    src.setByteStream(file)
    parser = make_parser()
    parser.setContentHandler(ConfigurationHandler(context, testing=testing))
    parser.setFeature(feature_namespaces, True)
    try:
        parser.parse(src)
    except SAXParseException:
        reraise(ZopeSAXParseException(file, sys.exc_info()[1]),
                None, sys.exc_info()[2])


def openInOrPlain(filename):
    """
    Open a file, falling back to filename.in.

    If the requested file does not exist and filename.in does, fall
    back to filename.in. If opening the original filename fails for
    any other reason, allow the failure to propogate.

    For example, the tests/samplepackage dirextory has files:

        - configure.zcml

        - configure.zcml.in

        - foo.zcml.in

    If we open configure.zcml, we'll get that file:

        >>> import os
        >>> from zope.configuration.xmlconfig import __file__
        >>> from zope.configuration.xmlconfig import openInOrPlain
        >>> here = os.path.dirname(__file__)
        >>> path = os.path.join(here, 'tests', 'samplepackage', 'configure.zcml')
        >>> f = openInOrPlain(path)
        >>> f.name[-14:]
        'configure.zcml'
        >>> f.close()

    But if we open foo.zcml, we'll get foo.zcml.in, since there isn't
    a foo.zcml:

        >>> path = os.path.join(here, 'tests', 'samplepackage', 'foo.zcml')
        >>> f = openInOrPlain(path)
        >>> f.name[-11:]
        'foo.zcml.in'
        >>> f.close()

    Make sure other IOErrors are re-raised. We need to do this in a
    try-except block because different errors are raised on Windows
    and on Linux.

        >>> try:
        ...     f = openInOrPlain('.')
        ... except IOError:
        ...     print("passed")
        ... else:
        ...     print("failed")
        passed
    """
    try:
        return open(filename)
    except IOError as e:
        code, msg = e.args
        if code == errno.ENOENT:
            fn = filename + ".in"
            if os.path.exists(fn):
                return open(fn)
        raise


class IInclude(Interface):
    """The `include`, `includeOverrides` and `exclude`
    directives.

    These directives allows you to include or preserve including of
    another ZCML file in the configuration. This enables you to write
    configuration files in each package and then link them together.
    """

    file = NativeStringLine(
        title=u"Configuration file name",
        description=(
            u"The name of a configuration file to be included/"
            u"excluded, relative to the directive containing the "
            u"including configuration file."
        ),
        required=False,
    )

    files = NativeStringLine(
        title=u"Configuration file name pattern",
        description=u"""
        The names of multiple configuration files to be included/excluded,
        expressed as a file-name pattern, relative to the directive
        containing the including or excluding configuration file.
        The pattern can include:

        - ``*`` matches 0 or more characters

        - ``?`` matches a single character

        - ``[<seq>]`` matches any character in seq

        - ``[!<seq>]`` matches any character not in seq

        The file names are included in sorted order, where sorting is
        without regard to case.
        """,
        required=False,
    )

    package = GlobalObject(
        title=u"Include or exclude package",
        description=u"""
        Include or exclude the named file (or configure.zcml) from the
        directory of this package.
        """,
        required=False,
    )


def include(_context, file=None, package=None, files=None):
    """Include a zcml file
    """

    if files:
        if file:
            raise ValueError("Must specify only one of file or files")
    elif not file:
        file = 'configure.zcml'

    # This is a tad tricky. We want to behave as a grouping directive.

    context = GroupingContextDecorator(_context)
    if package is not None:
        context.package = package
        context.basepath = None

    if files:
        paths = glob(context.path(files))
        paths = sorted(zip([path.lower() for path in paths], paths))
        paths = [path for (l, path) in paths]
    else:
        paths = [context.path(file)]

    for path in paths:
        if context.processFile(path):
            with openInOrPlain(path) as f:
                logger.debug("include %s", f.name)

                context.basepath = os.path.dirname(path)
                context.includepath = _context.includepath + (f.name, )
                _context.stack.append(GroupingStackItem(context))

                processxmlfile(f, context)
            assert _context.stack[-1].context is context
            _context.stack.pop()

def exclude(_context, file=None, package=None, files=None):
    """Exclude a zcml file

    This directive should be used before any ZML that includes
    configuration you want to exclude.
    """

    if files:
        if file:
            raise ValueError("Must specify only one of file or files")
    elif not file:
        file = 'configure.zcml'


    context = GroupingContextDecorator(_context)
    if package is not None:
        context.package = package
        context.basepath = None

    if files:
        paths = glob(context.path(files))
        paths = sorted(zip([path.lower() for path in paths], paths))
        paths = [path for (l, path) in paths]
    else:
        paths = [context.path(file)]

    for path in paths:
        # processFile returns a boolean indicating if the file has been
        # processed or not, it *also* marks the file as having been processed,
        # here the side effect is used to keep the given file from being
        # processed in the future
        context.processFile(path)

def includeOverrides(_context, file=None, package=None, files=None):
    """Include zcml file containing overrides.

    The actions in the included file are added to the context as if
    they were in the including file directly. Conflicting actions
    added by the named *file* or *files* are resolved before this
    directive completes.

    .. caution::
        If you do not specify a *file*, then the default file
        of ``configure.zcml`` will be used. A common use is to set *file*
        to ``overrides.zcml``.
    """

    # We need to remember how many actions we had before
    nactions = len(_context.actions)

    # We'll give the new actions this include path
    includepath = _context.includepath

    # Now we'll include the file. We'll munge the actions after
    include(_context, file, package, files)

    # Now we'll grab the new actions, resolve conflicts,
    # and munge the includepath:
    newactions = []

    for action in resolveConflicts(_context.actions[nactions:]):
        action['includepath'] = includepath
        newactions.append(action)

    _context.actions[nactions:] = newactions

def registerCommonDirectives(context):
    # We have to use the direct definition functions to define
    # a directive for all namespaces.

    defineSimpleDirective(
        context, "include", IInclude, include, namespace="*")

    defineSimpleDirective(
        context, "exclude", IInclude, exclude, namespace="*")

    defineSimpleDirective(
        context, "includeOverrides", IInclude, includeOverrides, namespace="*")

    defineGroupingDirective(
        context,
        name="configure",
        namespace="*",
        schema=IZopeConfigure,
        handler=ZopeConfigure,
        )

def file(name, package=None, context=None, execute=True):
    """Execute a zcml file
    """

    if context is None:
        context = ConfigurationMachine()
        registerCommonDirectives(context)
        context.package = package

    include(context, name, package)
    if execute:
        context.execute_actions()

    return context

def string(s, context=None, name="<string>", execute=True):
    """Execute a zcml string
    """
    if context is None:
        context = ConfigurationMachine()
        registerCommonDirectives(context)

    f = io.BytesIO(s) if isinstance(s, bytes) else io.StringIO(s)
    f.name = name
    processxmlfile(f, context)

    if execute:
        context.execute_actions()

    return context


##############################################################################
# Backward compatability, mainly for tests


_context = None
def _clearContext():
    global _context
    _context = ConfigurationMachine()
    registerCommonDirectives(_context)

def _getContext():
    global _context
    if _context is None:
        _clearContext()
        try:
            from zope.testing.cleanup import addCleanUp
        except ImportError: # pragma: no cover
            pass
        else: # pragma: no cover
            addCleanUp(_clearContext)
            del addCleanUp
    return _context

class XMLConfig(object):
    """Provide high-level handling of configuration files.

    See examples in tests/text_xmlconfig.py
    """

    def __init__(self, file_name, module=None):
        context = _getContext()
        include(context, file_name, module)
        self.context = context

    def __call__(self):
        self.context.execute_actions()

def xmlconfig(file, testing=False):
    context = _getContext()
    processxmlfile(file, context, testing=testing)
    context.execute_actions(testing=testing)


def testxmlconfig(file):
    """xmlconfig that doesn't raise configuration errors

    This is useful for testing, as it doesn't mask exception types.
    """
    context = _getContext()
    processxmlfile(file, context, testing=True)
    context.execute_actions(testing=True)
