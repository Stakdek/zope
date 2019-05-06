Regression test for https://github.com/zopefoundation/zope.testrunner/issues/6:
when the test suite changes the current working directory, subprocess
invocation might fail.

    >>> import os.path, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex-6')
    >>> defaults = [
    ...     '--path', os.path.relpath(directory_with_tests),
    ...     '--tests-pattern', '^cwdtests?$',
    ...     ]

    >>> orig_cwd = os.getcwd()

    >>> sys.argv = [os.path.relpath(testrunner_script), '-j2']
    >>> from zope import testrunner
    >>> testrunner.run_internal(defaults)
    Running .EmptyLayer tests:
      Set up .EmptyLayer in N.NNN seconds.
      Ran 0 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running cwdtests.Layer1 tests:
      Running in a subprocess.
      Set up cwdtests.Layer1 in 0.000 seconds.
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in 0.000 seconds.
      Tear down cwdtests.Layer1 in 0.000 seconds.
    Running cwdtests.Layer2 tests:
      Running in a subprocess.
      Set up cwdtests.Layer2 in 0.000 seconds.
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in 0.000 seconds.
      Tear down cwdtests.Layer2 in 0.000 seconds.
    Tearing down left over layers:
      Tear down .EmptyLayer in N.NNN seconds.
    Total: 2 tests, 0 failures, 0 errors and 0 skipped in 0.162 seconds.
    False

    >>> os.chdir(orig_cwd)
