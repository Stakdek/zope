===================
 Threads Reporting
===================

For each test zope.testrunner checks if new threads are left behind.

    >>> import time
    >>> import os
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> defaults = ['--path', directory_with_tests]

    >>> from zope import testrunner
    >>> args = ['test', '--tests-pattern', '^new_threads$']
    >>> _ = testrunner.run_internal(defaults, args)
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    The following test left new threads behind:
    test_leave_thread_behind (new_threads.TestNewThreadsReporting)
    New thread(s): [<Thread(t1)>]
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    >>> time.sleep(1)


It is possible to ignore this reporting for known threads.

    >>> import time
    >>> import os
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> defaults = ['--path', directory_with_tests]

    >>> from zope import testrunner
    >>> args = ['test', '--tests-pattern', '^new_threads$', '--ignore-new-thread=t1']
    >>> _ = testrunner.run_internal(defaults, args)
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    >>> time.sleep(1)
