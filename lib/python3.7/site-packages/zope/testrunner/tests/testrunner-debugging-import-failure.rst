Regression tests for https://bugs.launchpad.net/zope.testrunner/+bug/1119363

Post-mortem debugging also works when there is an import failure.

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
    ... '''
    ... impot doctest
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
      File ".../TESTS-DIR/tests.py", line 2
        impot doctest
                    ^
    SyntaxError: invalid syntax
    > ...find.py(399)import_name()
    -> __import__(name)
    (Pdb) c
    EndRun raised

Post-mortem debugging also works when the test suite is invalid:

    >>> sys.stdin = Input('c')

    >>> write_file('tests2.py',
    ... '''
    ... def test_suite():
    ...     return None
    ... ''')

    >>> import sys
    >>> try:
    ...     zope.testrunner.run_internal(
    ...       ['--path', dir, '-Dvv', '--tests-pattern', 'tests2'])
    ... except zope.testrunner.interfaces.EndRun: print('EndRun raised')
    ... finally: sys.stdin = real_stdin
    ... # doctest: +ELLIPSIS +REPORT_NDIFF
    TypeError: Invalid test_suite, None, in tests2
    > ...find.py(217)find_suites()
    -> % (suite, module_name)
    (Pdb) c
    EndRun raised

    >>> shutil.rmtree(tdir)


