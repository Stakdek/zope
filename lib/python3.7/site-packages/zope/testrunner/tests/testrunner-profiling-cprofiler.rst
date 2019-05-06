Profiling
=========

The testrunner includes the ability to profile the test execution with cProfile
via the `--profile=cProfile` option::

    >>> import os, sys, tempfile
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> sys.path.append(directory_with_tests)

    >>> tempdir = tempfile.mkdtemp(prefix='zope.testrunner-')

    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     '--profile-directory', tempdir,
    ...     ]

    >>> sys.argv = [testrunner_script, '--profile=cProfile']

When the tests are run, we get profiling output::

    >>> from zope import testrunner
    >>> testrunner.run_internal(defaults)
    Running...
    ...
       ncalls  tottime  percall  cumtime  percall filename:lineno(function)...
    ...

Profiling also works across layers::

    >>> sys.argv = [testrunner_script, '-ssample2', '--profile=cProfile',
    ...             '--tests-pattern', 'sampletests_ntd']
    >>> testrunner.run_internal(defaults)
    Running...
      Tear down ... not supported...
       ncalls  tottime  percall  cumtime  percall filename:lineno(function)...

The testrunner creates temnporary files containing cProfiler profiler
data::

    >>> os.listdir(tempdir)
    ['tests_profile.cZj2jt.prof', 'tests_profile.yHD-so.prof']

It deletes these when rerun.  We'll delete these ourselves::

    >>> import shutil
    >>> shutil.rmtree(tempdir)
