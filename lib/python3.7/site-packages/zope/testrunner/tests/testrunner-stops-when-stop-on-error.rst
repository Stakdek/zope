testrunner stops test run when --stop-on-error is used and there's an error
===========================================================================
Issue/bug #37 on Github: the test runner stops running tests *for the current
layer only* when started with -x/--stop-on-error and a test fails. We want the
test runner to stop running all tests.

::

    >>> import os, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex-37')
    >>> from zope import testrunner
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^stop_on_error',
    ...  ]
    >>> sys.argv = ['test']

When we don't pass the flag, we see two layers are tested
---------------------------------------------------------

    >>> testrunner.run_internal(defaults)
    Running layers.LayerA tests:
      Set up layers.LayerA in N.NNN seconds.
    Failure in test test (stop_on_error.ErrorTestCase1)
    Traceback (most recent call last):
     testrunner-ex-37/stop_on_error.py", Line NNN, in test
        self.assertTrue(False)
    AssertionError: False is not true
      Ran 1 tests with 1 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running layers.LayerB tests:
      Tear down layers.LayerA in N.NNN seconds.
      Set up layers.LayerB in N.NNN seconds.
    Failure in test test (stop_on_error.ErrorTestCase2)
    Traceback (most recent call last):
     testrunner-ex-37/stop_on_error.py", Line NNN, in test
        self.assertTrue(False)
    AssertionError: False is not true
      Ran 1 tests with 2 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down layers.LayerB in N.NNN seconds.
    Total: 2 tests, 2 failures, 0 errors and 0 skipped in N.NNN seconds.
    True

When we do pass the flag we see only one layer is tested
--------------------------------------------------------

    >>> testrunner.run_internal(defaults + ["--stop-on-error"])
    Running layers.LayerA tests:
      Set up layers.LayerA in N.NNN seconds.
    Failure in test test (stop_on_error.ErrorTestCase1)
    Traceback (most recent call last):
     testrunner-ex-37/stop_on_error.py", Line NNN, in test
        self.assertTrue(False)
    AssertionError: False is not true
      Ran 1 tests with 1 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down layers.LayerA in N.NNN seconds.
    True

Same for failures, without the flag, we see two layers
------------------------------------------------------

    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^stop_on_failure',
    ...  ]
    >>> testrunner.run_internal(defaults)
    Running layers.LayerA tests:
      Set up layers.LayerA in N.NNN seconds.
    Error in test test (stop_on_failure.FailureTestCase1)
    Traceback (most recent call last):
     testrunner-ex-37/stop_on_failure.py", Line NNN, in test
        raise Exception
    Exception
      Ran 1 tests with 0 failures, 1 errors and 0 skipped in N.NNN seconds.
    Running layers.LayerB tests:
      Tear down layers.LayerA in N.NNN seconds.
      Set up layers.LayerB in N.NNN seconds.
    Error in test test (stop_on_failure.FailureTestCase2)
    Traceback (most recent call last):
     testrunner-ex-37/stop_on_failure.py", Line NNN, in test
        raise Exception
    Exception
      Ran 1 tests with 0 failures, 1 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down layers.LayerB in N.NNN seconds.
    Total: 2 tests, 0 failures, 2 errors and 0 skipped in N.NNN seconds.
    True

When we do pass the flag we see only one layer is tested
--------------------------------------------------------

    >>> testrunner.run_internal(defaults + ["--stop-on-error"])
    Running layers.LayerA tests:
      Set up layers.LayerA in N.NNN seconds.
    Error in test test (stop_on_failure.FailureTestCase1)
    Traceback (most recent call last):
     testrunner-ex-37/stop_on_failure.py", Line NNN, in test
        raise Exception
    Exception
      Ran 1 tests with 0 failures, 1 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down layers.LayerA in N.NNN seconds.
    True
