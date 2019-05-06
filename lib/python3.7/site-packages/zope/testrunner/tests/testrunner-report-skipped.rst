testrunner handling of skipped tests
====================================

`unittest 2`_, which has been merged into Python 2.7 and Python 3.1, provides a
way to "skip" tests:
http://docs.python.org/2/library/unittest.html#skipping-tests-and-expected-failures

This feature is reported by the test runner.

::

    >>> import os, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex-skip')
    >>> from zope import testrunner
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sample_skipped_tests$',
    ...  ]
    >>> sys.argv = ['test']

Show how many skipped tests has been run
----------------------------------------

By default, the runner displays how many tests has been skipped, as part of the
result line::

    >>> testrunner.run_internal(defaults + ["-t", "TestSkipppedNoLayer"])
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Ran 1 tests with 0 failures, 0 errors and 1 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

If tests has been skipped in a layer, they are reported in the layer's status
line, and in the total status line::

    >>> testrunner.run_internal(defaults)
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in 0.000 seconds.
      Ran 1 tests with 0 failures, 0 errors and 1 skipped in 0.000 seconds.
    Running sample_skipped_tests.Layer tests:
      Tear down zope.testrunner.layer.UnitTests in 0.000 seconds.
      Set up sample_skipped_tests.Layer in 0.000 seconds.
      Ran 2 tests with 0 failures, 0 errors and 1 skipped in 0.000 seconds.
    Tearing down left over layers:
      Tear down sample_skipped_tests.Layer in 0.000 seconds.
    Total: 3 tests, 0 failures, 0 errors and 2 skipped in 0.034 seconds.
    False

Show the reason why tests have been skipped
-------------------------------------------

By changing the verbose level of the runner itself, you can get increasing
number of information::

    >>> testrunner.run_internal(defaults + ["-t", "TestSkipppedNoLayer"])
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Ran 1 tests with 0 failures, 0 errors and 1 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False
    >>> testrunner.run_internal(defaults + ["-t", "TestSkipppedNoLayer", "-vv"])
    Running tests at level 1
    ...
     test_skipped (sample_skipped_tests.TestSkipppedNoLayer) (skipped)
    ...
    >>> testrunner.run_internal(defaults + ["-t", "TestSkipppedNoLayer", "-vvv"])
    Running tests at level 1
    ...
     test_skipped (sample_skipped_tests.TestSkipppedNoLayer) (skipped: I'm a skipped test!)
    ...
