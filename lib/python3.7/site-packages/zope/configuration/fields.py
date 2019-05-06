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
"""Configuration-specific schema fields
"""
import os
import sys
import warnings

from zope.interface import implementer
from zope.schema import Bool as schema_Bool
from zope.schema import DottedName
from zope.schema import Field
from zope.schema import InterfaceField
from zope.schema import List
from zope.schema import PythonIdentifier as schema_PythonIdentifier
from zope.schema import Text
from zope.schema import ValidationError
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import InvalidValue

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.interfaces import InvalidToken

__all__ = [
    'Bool',
    'GlobalObject',
    'GlobalInterface',
    'MessageID',
    'Path',
    'PythonIdentifier',
    'Tokens',
]


class PythonIdentifier(schema_PythonIdentifier):
    r"""
    This class is like `zope.schema.PythonIdentifier`.


    Let's look at an example:

      >>> from zope.configuration.fields import PythonIdentifier
      >>> class FauxContext(object):
      ...     pass
      >>> context = FauxContext()
      >>> field = PythonIdentifier().bind(context)

    Let's test the fromUnicode method:

      >>> field.fromUnicode(u'foo')
      'foo'
      >>> field.fromUnicode(u'foo3')
      'foo3'
      >>> field.fromUnicode(u'_foo3')
      '_foo3'

    Now let's see whether validation works alright

      >>> for value in (u'foo', u'foo3', u'foo_', u'_foo3', u'foo_3', u'foo3_'):
      ...     _ = field.fromUnicode(value)
      >>> from zope.schema import ValidationError
      >>> for value in (u'3foo', u'foo:', u'\\', u''):
      ...     try:
      ...         field.fromUnicode(value)
      ...     except ValidationError:
      ...         print('Validation Error ' + repr(value))
      Validation Error '3foo'
      Validation Error 'foo:'
      Validation Error '\\'
      Validation Error ''

    .. versionchanged:: 4.2.0
       Extend `zope.schema.PythonIdentifier`, which implies that `fromUnicode`
       validates the strings.
    """

    def _validate(self, value):
        super(PythonIdentifier, self)._validate(value)
        if not value:
            raise ValidationError(value).with_field_and_value(self, value)


@implementer(IFromUnicode)
class GlobalObject(Field):
    """
    An object that can be accessed as a module global.

    The special value ``*`` indicates a value of `None`; this is
    not validated against the *value_type*.
    """

    _DOT_VALIDATOR = DottedName()

    def __init__(self, value_type=None, **kw):
        self.value_type = value_type
        super(GlobalObject, self).__init__(**kw)

    def _validate(self, value):
        super(GlobalObject, self)._validate(value)
        if self.value_type is not None:
            self.value_type.validate(value)

    def fromUnicode(self, value):
        r"""
        Find and return the module global at the path *value*.

          >>> d = {'x': 1, 'y': 42, 'z': 'zope'}
          >>> class fakeresolver(dict):
          ...     def resolve(self, n):
          ...         return self[n]
          >>> fake = fakeresolver(d)

          >>> from zope.schema import Int
          >>> from zope.configuration.fields import GlobalObject
          >>> g = GlobalObject(value_type=Int())
          >>> gg = g.bind(fake)
          >>> gg.fromUnicode("x")
          1
          >>> gg.fromUnicode("   x  \n  ")
          1
          >>> gg.fromUnicode("y")
          42
          >>> gg.fromUnicode("z")
          Traceback (most recent call last):
          ...
          WrongType: ('zope', (<type 'int'>, <type 'long'>), '')

          >>> g = GlobalObject(constraint=lambda x: x%2 == 0)
          >>> gg = g.bind(fake)
          >>> gg.fromUnicode("x")
          Traceback (most recent call last):
          ...
          ConstraintNotSatisfied: 1
          >>> gg.fromUnicode("y")
          42
          >>> g = GlobalObject()
          >>> gg = g.bind(fake)
          >>> print(gg.fromUnicode('*'))
          None
        """
        name = str(value.strip())

        # special case, mostly for interfaces
        if name == '*':
            return None

        try:
            # Leading dots are allowed here to indicate current
            # package, but not accepted by DottedName. Take care,
            # though, because a single dot is valid to resolve, but
            # not valid to pass to DottedName (as an empty string)
            to_validate = name.lstrip('.')
            if to_validate:
                self._DOT_VALIDATOR.validate(to_validate)
        except ValidationError as v:
            v.with_field_and_value(self, name)
            raise

        try:
            value = self.context.resolve(name)
        except ConfigurationError as v:
            raise ValidationError(v).with_field_and_value(self, name)

        self.validate(value)
        return value


@implementer(IFromUnicode)
class GlobalInterface(GlobalObject):
    """
    An interface that can be accessed from a module.

    Example:

    First, we need to set up a stub name resolver:

      >>> from zope.interface import Interface
      >>> class IFoo(Interface):
      ...     pass
      >>> class Foo(object):
      ...     pass
      >>> d = {'Foo': Foo, 'IFoo': IFoo}
      >>> class fakeresolver(dict):
      ...     def resolve(self, n):
      ...         return self[n]
      >>> fake = fakeresolver(d)

    Now verify constraints are checked correctly:

      >>> from zope.configuration.fields import GlobalInterface
      >>> g = GlobalInterface()
      >>> gg = g.bind(fake)
      >>> gg.fromUnicode('IFoo') is IFoo
      True
      >>> gg.fromUnicode('  IFoo  ') is IFoo
      True
      >>> gg.fromUnicode('Foo')
      Traceback (most recent call last):
      ...
      NotAnInterface: (<class 'Foo'>, ...

    """
    def __init__(self, **kw):
        super(GlobalInterface, self).__init__(InterfaceField(), **kw)


@implementer(IFromUnicode)
class Tokens(List):
    """
    A list that can be read from a space-separated string.
    """

    def fromUnicode(self, value):
        r"""
        Split the input string and convert it to *value_type*.

        Consider GlobalObject tokens:

        First, we need to set up a stub name resolver:

          >>> d = {'x': 1, 'y': 42, 'z': 'zope', 'x.y.x': 'foo'}
          >>> class fakeresolver(dict):
          ...     def resolve(self, n):
          ...         return self[n]
          >>> fake = fakeresolver(d)

          >>> from zope.configuration.fields import Tokens
          >>> from zope.configuration.fields import GlobalObject
          >>> g = Tokens(value_type=GlobalObject())
          >>> gg = g.bind(fake)
          >>> gg.fromUnicode("  \n  x y z  \n")
          [1, 42, 'zope']

          >>> from zope.schema import Int
          >>> g = Tokens(value_type=
          ...            GlobalObject(value_type=
          ...                         Int(constraint=lambda x: x%2 == 0)))
          >>> gg = g.bind(fake)
          >>> gg.fromUnicode("x y")
          Traceback (most recent call last):
          ...
          InvalidToken: 1 in x y

          >>> gg.fromUnicode("z y")
          Traceback (most recent call last):
          ...
          InvalidToken: ('zope', (<type 'int'>, <type 'long'>), '') in z y
          >>> gg.fromUnicode("y y")
          [42, 42]
        """
        value = value.strip()
        if value:
            vt = self.value_type.bind(self.context)
            values = []
            for s in value.split():
                try:
                    v = vt.fromUnicode(s)
                except ValidationError as ex:
                    raise InvalidToken("%s in %r" % (ex, value)).with_field_and_value(self, s)
                else:
                    values.append(v)
        else:
            values = []

        self.validate(values)

        return values

class PathProcessor(object):
    # Internal helper for manipulations on paths

    @classmethod
    def expand(cls, filename):
        # Perform the expansions we want to have done. Returns a
        # tuple: (path, needs_processing) If the second value is true,
        # further processing should be done (the path isn't fully
        # resolved); if false, the path should be used as is

        filename = filename.strip()
        # expanding a ~ at the front should generally result
        # in an absolute path.
        filename = os.path.expanduser(filename)
        filename = os.path.expandvars(filename)
        if os.path.isabs(filename):
            return os.path.normpath(filename), False
        return filename, True


@implementer(IFromUnicode)
class Path(Text):
    """
    A file path name, which may be input as a relative path

    Input paths are converted to absolute paths and normalized.
    """

    def fromUnicode(self, value):
        r"""
        Convert the input path to a normalized, absolute path.

        Let's look at an example:

        First, we need a "context" for the field that has a path
        function for converting relative path to an absolute path.

        We'll be careful to do this in an operating system independent fashion.

          >>> from zope.configuration.fields import Path
          >>> class FauxContext(object):
          ...    def path(self, p):
          ...       return os.path.join(os.sep, 'faux', 'context', p)
          >>> context = FauxContext()
          >>> field = Path().bind(context)

        Lets try an absolute path first:

          >>> import os
          >>> p = os.path.join(os.sep, u'a', u'b')
          >>> n = field.fromUnicode(p)
          >>> n.split(os.sep)
          ['', 'a', 'b']

        This should also work with extra spaces around the path:

          >>> p = "   \n   %s   \n\n   " % p
          >>> n = field.fromUnicode(p)
          >>> n.split(os.sep)
          ['', 'a', 'b']

        Environment variables are expanded:

          >>> os.environ['path-test'] = '42'
          >>> with_env = os.path.join(os.sep, u'a', u'${path-test}')
          >>> n = field.fromUnicode(with_env)
          >>> n.split(os.sep)
          ['', 'a', '42']

        Now try a relative path:

          >>> p = os.path.join(u'a', u'b')
          >>> n = field.fromUnicode(p)
          >>> n.split(os.sep)
          ['', 'faux', 'context', 'a', 'b']

        The current user is expanded (these are implicitly relative paths):

          >>> old_home = os.environ.get('HOME')
          >>> os.environ['HOME'] = os.path.join(os.sep, 'HOME')
          >>> n = field.fromUnicode('~')
          >>> n.split(os.sep)
          ['', 'HOME']
          >>> if old_home:
          ...    os.environ['HOME'] = old_home
          ... else:
          ...    del os.environ['HOME']


        .. versionchanged:: 4.2.0
            Start expanding home directories and environment variables.
        """
        filename, needs_processing = PathProcessor.expand(value)
        if needs_processing:
            filename = self.context.path(filename)

        return filename


@implementer(IFromUnicode)
class Bool(schema_Bool):
    """
    A boolean value.

    Values may be input (in upper or lower case) as any of:

    - yes / no
    - y / n
    - true / false
    - t / f

    .. caution::

       Do not confuse this with :class:`zope.schema.Bool`.
       That class will only parse ``"True"`` and ``"true"`` as
       `True` values. Any other value will silently be accepted as
       `False`. This class raises a validation error for unrecognized
       input.

    """

    def fromUnicode(self, value):
        """
        Convert the input string to a boolean.

        Example:

            >>> from zope.configuration.fields import Bool
            >>> Bool().fromUnicode(u"yes")
            True
            >>> Bool().fromUnicode(u"y")
            True
            >>> Bool().fromUnicode(u"true")
            True
            >>> Bool().fromUnicode(u"no")
            False
            >>> Bool().fromUnicode(u"surprise")
            Traceback (most recent call last):
            ...
            zope.schema._bootstrapinterfaces.InvalidValue
        """
        value = value.lower()
        if value in ('1', 'true', 'yes', 't', 'y'):
            return True
        if value in ('0', 'false', 'no', 'f', 'n'):
            return False
        # Unlike the superclass, anything else is invalid.
        raise InvalidValue().with_field_and_value(self, value)



@implementer(IFromUnicode)
class MessageID(Text):
    """
    Text string that should be translated.

    When a string is converted to a message ID, it is also recorded in
    the context.
    """

    __factories = {}

    def fromUnicode(self, u):
        """
        Translate a string to a MessageID.

          >>> from zope.configuration.fields import MessageID
          >>> class Info(object):
          ...     file = 'file location'
          ...     line = 8
          >>> class FauxContext(object):
          ...     i18n_strings = {}
          ...     info = Info()
          >>> context = FauxContext()
          >>> field = MessageID().bind(context)

        There is a fallback domain when no domain has been specified.

        Exchange the warn function so we can make test whether the warning
        has been issued

          >>> warned = None
          >>> def fakewarn(*args, **kw):
          ...     global warned
          ...     warned = args

          >>> import warnings
          >>> realwarn = warnings.warn
          >>> warnings.warn = fakewarn

          >>> i = field.fromUnicode(u"Hello world!")
          >>> i
          'Hello world!'
          >>> i.domain
          'untranslated'
          >>> warned
          ("You did not specify an i18n translation domain for the '' field in file location",)

          >>> warnings.warn = realwarn

        With the domain specified:

          >>> context.i18n_strings = {}
          >>> context.i18n_domain = 'testing'

        We can get a message id:

          >>> i = field.fromUnicode(u"Hello world!")
          >>> i
          'Hello world!'
          >>> i.domain
          'testing'

        In addition, the string has been registered with the context:

          >>> context.i18n_strings
          {'testing': {'Hello world!': [('file location', 8)]}}

          >>> i = field.fromUnicode(u"Foo Bar")
          >>> i = field.fromUnicode(u"Hello world!")
          >>> from pprint import PrettyPrinter
          >>> pprint=PrettyPrinter(width=70).pprint
          >>> pprint(context.i18n_strings)
          {'testing': {'Foo Bar': [('file location', 8)],
                       'Hello world!': [('file location', 8),
                                        ('file location', 8)]}}

          >>> from zope.i18nmessageid import Message
          >>> isinstance(list(context.i18n_strings['testing'].keys())[0], Message)
          True

        Explicit Message IDs

          >>> i = field.fromUnicode(u'[View-Permission] View')
          >>> i
          'View-Permission'
          >>> i.default
          'View'

          >>> i = field.fromUnicode(u'[] [Some] text')
          >>> i
          '[Some] text'
          >>> i.default is None
          True

        """
        context = self.context
        domain = getattr(context, 'i18n_domain', '')
        if not domain:
            domain = 'untranslated'
            warnings.warn(
                "You did not specify an i18n translation domain for the "\
                "'%s' field in %s" % (self.getName(), context.info.file)
                )
        if not isinstance(domain, str):
            # IZopeConfigure specifies i18n_domain as a BytesLine, but that's
            # wrong on Python 3, where the filesystem uses str, and hence
            # zope.i18n registers ITranslationDomain utilities with str names.
            # If we keep bytes, we can't find those utilities.
            enc = sys.getfilesystemencoding() or sys.getdefaultencoding()
            domain = domain.decode(enc)

        v = super(MessageID, self).fromUnicode(u)

        # Check whether there is an explicit message is specified
        default = None
        if v.startswith('[]'):
            v = v[2:].lstrip()
        elif v.startswith('['):
            end = v.find(']')
            default = v[end+2:]
            v = v[1:end]

        # Convert to a message id, importing the factory, if necessary
        factory = self.__factories.get(domain)
        if factory is None:
            import zope.i18nmessageid
            factory = zope.i18nmessageid.MessageFactory(domain)
            self.__factories[domain] = factory

        msgid = factory(v, default)

        # Record the string we got for the domain
        i18n_strings = context.i18n_strings
        strings = i18n_strings.get(domain)
        if strings is None:
            strings = i18n_strings[domain] = {}
        locations = strings.setdefault(msgid, [])
        locations.append((context.info.file, context.info.line))

        return msgid
