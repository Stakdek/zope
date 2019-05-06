Profiling
=========
The testrunner supports hotshot and cProfile profilers. Hotshot profiler
support does not work with python2.6

    >>> import os.path, sys, tempfile
    >>> profiler = '--profile=hotshot'
    >>> if sys.hexversion >= 0x02060000:
    ...     profiler = '--profile=cProfile'

The testrunner includes the ability to profile the test execution with hotshot
via the --profile option, if it a python <= 2.6

    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> sys.path.append(directory_with_tests)

    >>> tempdir = tempfile.mkdtemp(prefix='zope.testrunner-')

    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     '--profile-directory', tempdir,
    ...     ]

    >>> sys.argv = [testrunner_script, profiler]

When the tests are run, we get profiling output.

    >>> from zope import testrunner
    >>> testrunner.run_internal(defaults)
    Running zope.testrunner.layer.UnitTests tests:
    ...
    Running samplelayers.Layer1 tests:
    ...
    Running samplelayers.Layer11 tests:
    ...
       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    ...
    Total: ... tests, 0 failures, 0 errors and 0 skipped in ... seconds.
    False

Profiling also works across layers.

    >>> sys.argv = [testrunner_script, '-ssample2', profiler,
    ...             '--tests-pattern', 'sampletests_ntd']
    >>> testrunner.run_internal(defaults)
    Running...
      Tear down ... not supported...
       ncalls  tottime  percall  cumtime  percall filename:lineno(function)...

The testrunner creates temnporary files containing hotshot profiler
data:

    >>> os.listdir(tempdir)
    ['tests_profile.cZj2jt.prof', 'tests_profile.yHD-so.prof']

It deletes these when rerun.  We'll delete these ourselves:

    >>> import shutil
    >>> shutil.rmtree(tempdir)
