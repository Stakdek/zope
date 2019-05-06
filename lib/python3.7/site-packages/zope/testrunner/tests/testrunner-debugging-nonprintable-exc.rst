Regression tests for https://github.com/zopefoundation/zope.testrunner/issues/8

Post-mortem debugging also works when the exception cannot be printed

    >>> import os, shutil, sys, tempfile
    >>> tdir = tempfile.mkdtemp()
    >>> dir = os.path.join(tdir, 'TESTS-DIR')
    >>> os.mkdir(dir)
    >>> def write_file(filename, body):
    ...     with open(os.path.join(dir, filename), 'w') as f:
    ...         f.write(body)
    ...     try:
    ...         # Need to do this on Python 3.3 after creating new modules
    ...         import importlib; importlib.invalidate_caches()
    ...     except (ImportError, AttributeError):
    ...         pass

    >>> write_file('tests.py',
    ... r'''
    ... import unittest
    ... import six
    ...
    ... class MyTest(unittest.TestCase):
    ...     def test(self):
    ...         self.assertEqual(six.u('a'), six.b('\xc4\x85').decode('UTF-8'))
    ... ''')

    >>> class Input:
    ...     def __init__(self, src):
    ...         self.lines = src.split('\n')
    ...     def readline(self):
    ...         line = self.lines.pop(0)
    ...         print(line)
    ...         return line+'\n'

    >>> real_stdin = sys.stdin
    >>> sys.stdin = Input('c')

    >>> sys.argv = [testrunner_script]
    >>> import zope.testrunner
    >>> try:
    ...     zope.testrunner.run_internal(['--path', dir, '-D'])
    ... except zope.testrunner.interfaces.EndRun: print('EndRun raised')
    ... finally: sys.stdin = real_stdin
    ... # doctest: +ELLIPSIS +REPORT_NDIFF
    Running zope.testrunner.layer.UnitTests tests:
    ...
    AssertionError: ...'a' != ...'...'
    ...
    (Pdb) c
    Tearing down left over layers:
    ...
    False

    >>> shutil.rmtree(tdir)


