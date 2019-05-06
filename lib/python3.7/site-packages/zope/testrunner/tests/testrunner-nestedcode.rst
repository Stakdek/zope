This testrunner_ex subdirectory contains a number of sample packages
with tests.  Let's run the tests found here.
We simulate here, that you use nested locations for your different source
packages and that within your source, you checked out other source
directories

    >>> import os.path
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> defaults = [
    ...     '--path', this_directory,
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     ]
    >>> from zope import testrunner
    >>> import sys
    >>> sys.argv = ['test']
    >>> testrunner.run_internal(defaults)
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Ran 156 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running samplelayers.Layer1 tests:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
      Set up samplelayers.Layer1 in N.NNN seconds.
      Ran 9 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running samplelayers.Layer11 tests:
      Set up samplelayers.Layer11 in N.NNN seconds.
      Ran 26 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running samplelayers.Layer111 tests:
      Set up samplelayers.Layerx in N.NNN seconds.
      Set up samplelayers.Layer111 in N.NNN seconds.
      Ran 26 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running samplelayers.Layer112 tests:
      Tear down samplelayers.Layer111 in N.NNN seconds.
      Set up samplelayers.Layer112 in N.NNN seconds.
      Ran 26 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running samplelayers.Layer12 tests:
      Tear down samplelayers.Layer112 in N.NNN seconds.
      Tear down samplelayers.Layerx in N.NNN seconds.
      Tear down samplelayers.Layer11 in N.NNN seconds.
      Set up samplelayers.Layer12 in N.NNN seconds.
      Ran 26 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running samplelayers.Layer121 tests:
      Set up samplelayers.Layer121 in N.NNN seconds.
      Ran 26 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running samplelayers.Layer122 tests:
      Tear down samplelayers.Layer121 in N.NNN seconds.
      Set up samplelayers.Layer122 in N.NNN seconds.
      Ran 26 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer122 in N.NNN seconds.
      Tear down samplelayers.Layer12 in N.NNN seconds.
      Tear down samplelayers.Layer1 in N.NNN seconds.
    Total: 321 tests, 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    False
