Failure to find layers should not pass silently
===============================================

This is a regression test for the following bug: you try to run several
test layers using subprocesses (e.g. because you used bin/test -j99),
and the child process somehow is unable to find the layer it was supposed
to be running.  This is a serious problem that should not pass silently.

Instead of setting up the conditions for this problem to actually occur
in practice we'll simulate the subprocess invocation using --resume-layer.

    >>> import os.path, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     ]

The test runner does some funky stuff in this case, specifically, it
closes sys.stdout, which makes doctest unhappy, so we stub the close
method out.

    >>> sys.stdout.close = lambda: None

    >>> from six import StringIO
    >>> orig_stderr = sys.stderr
    >>> sys.stderr = fake_stderr = StringIO()

    >>> sys.argv = 'test --resume-layer NoSuchLayer 0'.split()
    >>> from zope import testrunner
    >>> testrunner.run_internal(defaults)
    <BLANKLINE>
    **********************************************************************
    Cannot find layer NoSuchLayer
    **********************************************************************
    <BLANKLINE>
    Total: 0 tests, 0 failures, 1 errors and 0 skipped in 0.000 seconds.
    True

It also prints to stderr to communicate with the parent process

    >>> print(fake_stderr.getvalue(), end='')
    0 0 1
    subprocess failed for NoSuchLayer

Cleanup

    >>> del sys.stdout.close
    >>> sys.stderr = orig_stderr

