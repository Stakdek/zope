r"""Doctests in TestCase classes

The original ``doctest`` unittest integration was based on
``unittest`` test suites, which have fallen out of favor. This module
provides a way to define doctests inside of unittest ``TestCase``
classes. It also provides better integration with unittest test
fixtures, because doctests use setup provided by the containing test
case class.  It also provides access to unittest assertion
methods.

You can define doctests in 4 ways:

- references to named files

- strings

- decorated functions with docstrings

- reference to named files decorating test-specific setup functions

.. some setup

   >>> __name__ = 'tests'

Here are some examples::

    from zope.testing import doctestcase
    import doctest
    import unittest

    g = 'global'
    class MyTest(unittest.TestCase):

        def setUp(self):
            self.a = 1
            self.globs = dict(c=9)

        test1 = doctestcase.file('test1.txt', optionflags=doctest.ELLIPSIS)

        test2 = doctestcase.docteststring('''
          >>> self.a, g, c
          (1, 'global', 9)
        ''')

        @doctestcase.doctestmethod(optionflags=doctest.ELLIPSIS)
        def test3(self):
            '''
            >>> self.a, self.x, g, c
            (1, 3, 'global', 9)
            '''
            self.x = 3

        @doctestcase.doctestfile('test4.txt')
        def test4(self):
            self.x = 5

In this example, 3 constructors were used:

doctestfile (alias: file)
  doctestfile makes a file-based test case.

  This can be used as a decorator, in which case, the decorated
  function is called before the test is run, to provide test-specific
  setup.

docteststring (alias string)
  docteststring constructs a doctest from a string.

doctestmethod (alias method)
  doctestmethod constructs a doctest from a method.

  The method's docstring provides the test. The method's body provides
  optional test-specific setup.

Note that short aliases are provided, which may be useful in certain
import styles.

Tests have access to the following data:

- Tests created with the ``docteststring`` and ``doctestmethod``
  constructors have access to the module globals of the defining
  module.

- In tests created with the ``docteststring`` and ``doctestmethod``
  constructors, the test case instance is available as the ``self``
  variable.

- In tests created with the ``doctestfile`` constructor, the test case
  instance is available as the ``test`` variable.

- If a test case defines a globs attribute, it must be a dictionary
  and its contents are added to the test globals.

The constructors accept standard doctest ``optionflags`` and
``checker`` arguments.

Note that the doctest IGNORE_EXCEPTION_DETAIL option flag is
added to optionflags.
"""
import doctest
import inspect
import os
import re
import sys
import types

__all__ = ['doctestmethod', 'docteststring', 'doctestfile']

_parser = doctest.DocTestParser()

def _testify(name):
    if not name.startswith('test'):
        name = 'test_' + name
    return name

def doctestmethod(test=None, optionflags=0, checker=None):
    """Define a doctest from a method within a unittest.TestCase.

    The method's doc string provides the test source. Its body is
    called before the test and may perform test-specific setup.

    You can pass doctest option flags and a custon checker.

    Variables defined in the enclosing module are available in the test.

    If a test case defines a globs attribute, it must be a dictionary
    and its contents are added to the test globals.

    The test object is available as the variable ``self`` in the test.
    """
    if test is None:
        return lambda test: _doctestmethod(test, optionflags, checker)

    return _doctestmethod(test, optionflags, checker)

method = doctestmethod

def _doctestmethod(test, optionflags, checker):
    doc = test.__doc__
    if not doc:
        raise ValueError(test, "has no docstring")
    setup = test
    name = test.__name__
    path = inspect.getsourcefile(test)
    lineno = inspect.getsourcelines(test)[1]

    fglobs = sys._getframe(3).f_globals

    def test_method(self):
        setup(self)
        _run_test(self, doc, fglobs.copy(), name, path,
                  optionflags, checker, lineno=lineno)

    test_method.__name__ = _testify(name)

    return test_method

def docteststring(test, optionflags=0, checker=None, name=None):
    """Define a doctest from a string within a unittest.TestCase.

    You can pass doctest option flags and a custon checker.

    Variables defined in the enclosing module are available in the test.

    If a test case defines a globs attribute, it must be a dictionary
    and its contents are added to the test globals.

    The test object is available as the variable ``self`` in the test.
    """
    fglobs = sys._getframe(2).f_globals

    def test_string(self):
        _run_test(self, test, fglobs.copy(), '<string>', '<string>',
                  optionflags, checker)
    if name:
        test_string.__name__ = _testify(name)

    return test_string

string = docteststring

_not_word = re.compile(r'\W')
def doctestfile(path, optionflags=0, checker=None):
    """Define a doctest from a test file within a unittest.TestCase.

    The file path may be relative or absolute. If its relative (the
    common case), it will be interpreted relative to the directory
    containing the referencing module.

    You can pass doctest option flags and a custon checker.

    If a test case defines a globs attribute, it must be a dictionary
    and its contents are added to the test globals.

    The test object is available as the variable ``test`` in the test.

    The resulting object can be used as a function decorator. The
    decorated method is called before the test and may perform
    test-specific setup. (The decorated method's doc string is ignored.)
    """
    base = os.path.dirname(os.path.abspath(
        sys._getframe(2).f_globals['__file__']
        ))
    path = os.path.join(base, path)
    with open(path) as f:
        test = f.read()
    name = os.path.basename(path)

    def test_file(self):
        if isinstance(self, types.FunctionType):
            setup = self
            def test_file_w_setup(self):
                setup(self)
                _run_test(self, test, {}, name, path, optionflags, checker,
                          'test')
            test_file_w_setup.__name__ = _testify(setup.__name__)
            test_file_w_setup.filepath = path
            test_file_w_setup.filename = os.path.basename(path)
            return test_file_w_setup

        _run_test(self, test, {}, name, path, optionflags, checker, 'test')

    test_file.__name__ = name_from_path(path)
    test_file.filepath = path
    test_file.filename = os.path.basename(path)

    return test_file

file = doctestfile

def doctestfiles(*paths, **kw):
    """Define doctests from test files in a decorated class.

    Multiple files can be specified. A member is added to the
    decorated class for each file.

    The file paths may be relative or absolute. If relative (the
    common case), they will be interpreted relative to the directory
    containing the referencing module.

    You can pass doctest option flags and a custon checker.

    If a test case defines a globs attribute, it must be a dictionary
    and its contents are added to the test globals.

    The test object is available as the variable ``test`` in the test.

    The resulting object must be used as a class decorator.
    """
    def doctestfiles_(class_):
        for path in paths:
            name = name_from_path(path)
            test = doctestfile(path, **kw)
            test.__name__ = name
            setattr(class_, name, test)

        return class_

    return doctestfiles_

files = doctestfiles

def name_from_path(path):
    return _testify(
        _not_word.sub('_', os.path.splitext(os.path.basename(path))[0])
        )

def _run_test(self, test, globs, name, path,
              optionflags, checker, testname='self', lineno=0):
    globs.update(getattr(self, 'globs', ()))
    globs[testname] = self
    optionflags |= doctest.IGNORE_EXCEPTION_DETAIL
    doctest.DocTestCase(
        _parser.get_doctest(test, globs, name, path, lineno),
        optionflags=optionflags,
        checker=checker,
        ).runTest()
