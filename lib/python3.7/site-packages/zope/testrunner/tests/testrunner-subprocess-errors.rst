This is a test for error handling when the test runner runs a test layer in a
subprocess.

Fake an IOError reading the output of the subprocess to exercise the
reporting of that error:

    >>> class FakeStdout(object):
    ...     raised = False
    ...     def __init__(self, msg):
    ...         self.msg = msg
    ...     def readline(self):
    ...         if not self.raised:
    ...             self.raised = True
    ...             raise IOError(self.msg)

    >>> class FakeStderr(object):
    ...     def __init__(self, msg):
    ...         self.msg = msg
    ...     def read(self):
    ...         return self.msg

    >>> class FakeProcess(object):
    ...     def __init__(self, out, err):
    ...         self.stdout = FakeStdout(out)
    ...         self.stderr = FakeStderr(err)
    ...     def kill(self):
    ...         pass
    ...     communicate = kill

    >>> class FakePopen(object):
    ...     def __init__(self, out, err):
    ...         self.out = out
    ...         self.err = err
    ...     def __call__(self, *args, **kw):
    ...         return FakeProcess(self.out, self.err)

    >>> import subprocess
    >>> Popen = subprocess.Popen
    >>> subprocess.Popen = FakePopen(
    ...      "Failure triggered to verify error reporting",
    ...      "0 0 0")

    >>> import os, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> from zope import testrunner
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     ]
    >>> argv = [sys.argv[0],
    ...         '-vv', '--tests-pattern', '^sampletests_buffering.*']

    >>> _ = testrunner.run_internal(defaults, argv)
    Running tests at level 1
    Running sampletests_buffering.Layer1 tests:
      Set up sampletests_buffering.Layer1 in N.NNN seconds.
      Running:
     test_something (sampletests_buffering.TestSomething1)
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running sampletests_buffering.Layer2 tests:
      Tear down sampletests_buffering.Layer1 ... not supported
    Error reading subprocess output for sampletests_buffering.Layer2
    Failure triggered to verify error reporting
    Total: 1 tests, 0 failures, 0 errors and 0 skipped in N.NNN seconds.

Now fake some unexpected stderr to test reporting a failure when
communicating with the subprocess:

    >>> subprocess.Popen = FakePopen(
    ...      "Failure triggered to verify error reporting",
    ...      b"segmentation fault (core dumped muahahaha)")

    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> from zope import testrunner
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     ]
    >>> argv = [sys.argv[0],
    ...         '-vv', '--tests-pattern', '^sampletests_buffering.*']

    >>> _ = testrunner.run_internal(defaults, argv) # doctest: +ELLIPSIS
    Running tests at level 1
    Running sampletests_buffering.Layer1 tests:
      Set up sampletests_buffering.Layer1 in N.NNN seconds.
      Running:
     test_something (sampletests_buffering.TestSomething1)
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running sampletests_buffering.Layer2 tests:
      Tear down sampletests_buffering.Layer1 ... not supported
    Error reading subprocess output for sampletests_buffering.Layer2
    Failure triggered to verify error reporting
    <BLANKLINE>
    **********************************************************************
    Could not communicate with subprocess!
    Child command line: ['...', '--resume-layer', 'sampletests_buffering.Layer2', '0', '--default', '--path', '--default', 'testrunner-ex', '-vv', '--tests-pattern', '^sampletests_buffering.*']
    Child stderr was:
      segmentation fault (core dumped muahahaha)
    **********************************************************************
    <BLANKLINE>
    <BLANKLINE>
    Tests with errors:
       subprocess for sampletests_buffering.Layer2
    Total: 1 tests, 0 failures, 1 errors and 0 skipped in N.NNN seconds.

Very large subprocess output is trimmed, unless you ask for extra verbosity

    >>> subprocess.Popen = FakePopen(
    ...      "Failure triggered to verify error reporting",
    ...      "\n".join(str(n) for n in range(1, 101)).encode())

    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> from zope import testrunner
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     ]
    >>> argv = [sys.argv[0],
    ...         '-v', '--tests-pattern', '^sampletests_buffering.*']

    >>> _ = testrunner.run_internal(defaults, argv) # doctest: +ELLIPSIS
    Running tests at level 1
    Running sampletests_buffering.Layer1 tests:
      Set up sampletests_buffering.Layer1 in N.NNN seconds.
      Running:
    .
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running sampletests_buffering.Layer2 tests:
      Tear down sampletests_buffering.Layer1 ... not supported
    Error reading subprocess output for sampletests_buffering.Layer2
    Failure triggered to verify error reporting
    <BLANKLINE>
    **********************************************************************
    Could not communicate with subprocess!
    Child command line: ['...', '--resume-layer', 'sampletests_buffering.Layer2', '0', '--default', '--path', '--default', 'testrunner-ex', '-v', '--tests-pattern', '^sampletests_buffering.*']
    Child stderr was:
      1
      2
      3
      4
      5
      6
      7
      8
      9
      10
    ...
      91
      92
      93
      94
      95
      96
      97
      98
      99
      100
    **********************************************************************
    <BLANKLINE>
    <BLANKLINE>
    Tests with errors:
       subprocess for sampletests_buffering.Layer2
    Total: 1 tests, 0 failures, 1 errors and 0 skipped in N.NNN seconds.

    >>> subprocess.Popen = Popen
