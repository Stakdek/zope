Post-mortem debugging also works when there is a failure in layer
setup.

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
    ... import doctest
    ...
    ... class Layer:
    ...     @classmethod
    ...     def setUp(self):
    ...         x = 1
    ...         raise ValueError
    ...
    ... def a_test():
    ...     """
    ...     >>> None
    ...     """
    ... def test_suite():
    ...     suite = doctest.DocTestSuite()
    ...     suite.layer = Layer
    ...     return suite
    ... 
    ... ''')

    >>> class Input:
    ...     def __init__(self, src):
    ...         self.lines = src.split('\n')
    ...     def readline(self):
    ...         line = self.lines.pop(0)
    ...         print(line)
    ...         return line+'\n'

    >>> real_stdin = sys.stdin
    >>> sys.stdin = Input('p x\nc')

    >>> sys.argv = [testrunner_script]
    >>> import zope.testrunner
    >>> try:
    ...     zope.testrunner.run_internal(['--path', dir, '-D'])
    ... except zope.testrunner.interfaces.EndRun: print("unexpected EndRun!")
    ... finally: sys.stdin = real_stdin
    ... # doctest: +ELLIPSIS
    Running tests.Layer tests:
      Set up tests.Layer ...ValueError
    <BLANKLINE>
    > ...tests.py(8)setUp()
    -> raise ValueError
    (Pdb) p x
    1
    (Pdb) c
    False

Note that post-mortem debugging doesn't work when the layer is run in
a subprocess:

    >>> sys.stdin = Input('p x\nc')

    >>> write_file('tests2.py',
    ... '''
    ... import doctest, unittest
    ...
    ... class Layer1:
    ...     @classmethod
    ...     def setUp(self):
    ...         pass
    ...
    ...     @classmethod
    ...     def tearDown(self):
    ...         raise NotImplementedError
    ...
    ... class Layer2:
    ...     @classmethod
    ...     def setUp(self):
    ...         x = 1
    ...         raise ValueError
    ...     
    ... def a_test():
    ...     """
    ...     >>> None
    ...     """
    ... def test_suite():
    ...     suite1 = doctest.DocTestSuite()
    ...     suite1.layer = Layer1
    ...     suite2 = doctest.DocTestSuite()
    ...     suite2.layer = Layer2
    ...     return unittest.TestSuite((suite1, suite2))
    ... 
    ... ''')

    >>> import sys
    >>> try:
    ...     zope.testrunner.run_internal(
    ...       ['--path', dir, '-Dvv', '--tests-pattern', 'tests2'])
    ... except zope.testrunner.interfaces.EndRun: print("unexpected EndRun!")
    ... finally: sys.stdin = real_stdin
    ... # doctest: +ELLIPSIS +REPORT_NDIFF
    Running tests at level 1
    Running tests2.Layer1 tests:
      Set up tests2.Layer1 in 0.000 seconds.
      Running:
     a_test (tests2)
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in 0.001 seconds.
    Running tests2.Layer2 tests:
      Tear down tests2.Layer1 ... not supported
      Running in a subprocess.
      Set up tests2.Layer2
    **********************************************************************
    <BLANKLINE>
    Can't post-mortem debug when running a layer as a subprocess!
    Try running layer 'tests2.Layer2' by itself.
    <BLANKLINE>
    **********************************************************************
    <BLANKLINE>
    Traceback (most recent call last):
    ...
        raise ValueError
    ValueError
    <BLANKLINE>
    <BLANKLINE>
    Tests with errors:
       Layer: tests2.Layer2
    Total: 1 tests, 0 failures, 1 errors and 0 skipped in 0.210 seconds.
    True

    >>> shutil.rmtree(tdir)


