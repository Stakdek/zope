Subunit v2 Output
=================

Subunit supports two protocols: v1 is largely a text protocol while v2 is
binary.  v2 is generally more robust, but tools that consume the output of
zope.testrunner may not expect to receive it, so we support emitting either
protocol.

First we set up some defaults:

    >>> import os.path, sys

    >>> defaults = [
    ...     '--subunit-v2',
    ...     '--path', os.path.join(this_directory, 'testrunner-ex'),
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     ]

    >>> from zope import testrunner

For easier doctesting, we use a helper that summarizes the output.

    >>> from subunit import ByteStreamToStreamResult
    >>> from testtools import StreamResult

    >>> class SummarizeResult(StreamResult):
    ...     def __init__(self, stream):
    ...         self.stream = stream
    ...         self._last_file = None
    ...     def status(self, test_id=None, test_status=None, test_tags=None,
    ...                runnable=True, file_name=None, file_bytes=None,
    ...                eof=False, mime_type=None, route_code=None,
    ...                timestamp=None):
    ...         if (test_id, file_name) == self._last_file:
    ...             self.stream.write(file_bytes.decode('utf-8', 'replace'))
    ...             return
    ...         elif self._last_file is not None:
    ...             self.stream.write('\n')
    ...             self._last_file = None
    ...         if test_id is not None:
    ...             self.stream.write('id=%s ' % (test_id,))
    ...             if test_status is not None:
    ...                 self.stream.write('status=%s ' % (test_status,))
    ...             if test_tags is not None:
    ...                 self.stream.write(
    ...                     'tags=(%s) ' % ' '.join(sorted(test_tags)))
    ...             if not runnable:
    ...                 self.stream.write('!runnable ')
    ...             self.stream.write('\n')
    ...         if file_name is not None:
    ...             self.stream.write('%s (%s)\n' % (file_name, mime_type))
    ...             self.stream.write(file_bytes.decode('utf-8', 'replace'))
    ...             self._last_file = (test_id, file_name)
    ...         self.stream.flush()

    >>> def subunit_summarize(func, *args, **kwargs):
    ...     orig_stdout = sys.stdout
    ...     try:
    ...         if sys.version_info[0] >= 3:
    ...             import io
    ...             sys.stdout = io.TextIOWrapper(
    ...                 io.BytesIO(), encoding='utf-8')
    ...         else:
    ...             import StringIO
    ...             sys.stdout = StringIO.StringIO()
    ...         ret = func(*args, **kwargs)
    ...         sys.stdout.flush()
    ...         buf = sys.stdout
    ...         if sys.version_info[0] >= 3:
    ...             buf = buf.detach()
    ...         buf.seek(0)
    ...     finally:
    ...         sys.stdout = orig_stdout
    ...     case = ByteStreamToStreamResult(buf, non_subunit_name='stdout')
    ...     case.run(SummarizeResult(sys.stdout))
    ...     return ret


Basic output
------------

There is an 'inprogress' status event for the start of each test and a
'success' status event for each successful test.

Zope layer setup and teardown events are represented as tests tagged with
'zope:layer'. This allows them to be distinguished from actual tests, provides
a place for the layer timing information in the subunit stream and allows us
to include error information if necessary.

Once the layer is set up, all future tests are tagged with
'zope:layer:LAYER_NAME'.

    >>> sys.argv = 'test --layer 122 -t TestNotMuch'.split()
    >>> subunit_summarize(testrunner.run_internal, defaults)
    id=samplelayers.Layer1:setUp status=inprogress !runnable
    id=samplelayers.Layer1:setUp status=success tags=(zope:layer) !runnable
    id=samplelayers.Layer12:setUp status=inprogress !runnable
    id=samplelayers.Layer12:setUp status=success
      tags=(zope:layer zope:layer:samplelayers.Layer1) !runnable
    id=samplelayers.Layer122:setUp status=inprogress !runnable
    id=samplelayers.Layer122:setUp status=success
      tags=(zope:layer zope:layer:samplelayers.Layer1
            zope:layer:samplelayers.Layer12) !runnable
    id=sample1.sampletests.test122.TestNotMuch.test_1 status=inprogress
    id=sample1.sampletests.test122.TestNotMuch.test_1 status=success
      tags=(zope:layer:samplelayers.Layer1 zope:layer:samplelayers.Layer12
            zope:layer:samplelayers.Layer122)
    id=sample1.sampletests.test122.TestNotMuch.test_2 status=inprogress
    id=sample1.sampletests.test122.TestNotMuch.test_2 status=success
      tags=(zope:layer:samplelayers.Layer1 zope:layer:samplelayers.Layer12
            zope:layer:samplelayers.Layer122)
    id=sample1.sampletests.test122.TestNotMuch.test_3 status=inprogress
    id=sample1.sampletests.test122.TestNotMuch.test_3 status=success
      tags=(zope:layer:samplelayers.Layer1 zope:layer:samplelayers.Layer12
            zope:layer:samplelayers.Layer122)
    id=sampletests.test122.TestNotMuch.test_1 status=inprogress
    id=sampletests.test122.TestNotMuch.test_1 status=success
      tags=(zope:layer:samplelayers.Layer1 zope:layer:samplelayers.Layer12
            zope:layer:samplelayers.Layer122)
    id=sampletests.test122.TestNotMuch.test_2 status=inprogress
    id=sampletests.test122.TestNotMuch.test_2 status=success
      tags=(zope:layer:samplelayers.Layer1 zope:layer:samplelayers.Layer12
            zope:layer:samplelayers.Layer122)
    id=sampletests.test122.TestNotMuch.test_3 status=inprogress
    id=sampletests.test122.TestNotMuch.test_3 status=success
      tags=(zope:layer:samplelayers.Layer1 zope:layer:samplelayers.Layer12
            zope:layer:samplelayers.Layer122)
    id=samplelayers.Layer122:tearDown status=inprogress !runnable
    id=samplelayers.Layer122:tearDown status=success
      tags=(zope:layer zope:layer:samplelayers.Layer1
            zope:layer:samplelayers.Layer12) !runnable
    id=samplelayers.Layer12:tearDown status=inprogress !runnable
    id=samplelayers.Layer12:tearDown status=success
      tags=(zope:layer zope:layer:samplelayers.Layer1) !runnable
    id=samplelayers.Layer1:tearDown status=inprogress !runnable
    id=samplelayers.Layer1:tearDown status=success tags=(zope:layer) !runnable
    False


Listing tests
-------------

To list tests in subunit v2, we emit a stream of test results using the
'exists' status without actually running the tests.

Note that in this stream, we don't emit fake tests for the layer set up and
tear down, because it simply doesn't happen.

We also don't include the dependent layers in the stream (in this case Layer1
and Layer12), since they are not provided to the reporter.

    >>> sys.argv = 'test --layer 122 --list-tests -t TestNotMuch'.split()
    >>> subunit_summarize(testrunner.run_internal, defaults)
    id=sample1.sampletests.test122.TestNotMuch.test_1 status=inprogress
    id=sample1.sampletests.test122.TestNotMuch.test_1 status=exists
      tags=(zope:layer:samplelayers.Layer122)
    id=sample1.sampletests.test122.TestNotMuch.test_2 status=inprogress
    id=sample1.sampletests.test122.TestNotMuch.test_2 status=exists
      tags=(zope:layer:samplelayers.Layer122)
    id=sample1.sampletests.test122.TestNotMuch.test_3 status=inprogress
    id=sample1.sampletests.test122.TestNotMuch.test_3 status=exists
      tags=(zope:layer:samplelayers.Layer122)
    id=sampletests.test122.TestNotMuch.test_1 status=inprogress
    id=sampletests.test122.TestNotMuch.test_1 status=exists
      tags=(zope:layer:samplelayers.Layer122)
    id=sampletests.test122.TestNotMuch.test_2 status=inprogress
    id=sampletests.test122.TestNotMuch.test_2 status=exists
      tags=(zope:layer:samplelayers.Layer122)
    id=sampletests.test122.TestNotMuch.test_3 status=inprogress
    id=sampletests.test122.TestNotMuch.test_3 status=exists
      tags=(zope:layer:samplelayers.Layer122)
    False


Profiling tests
---------------

Test suites often cover a lot of code, and the performance of test suites
themselves is often a critical part of the development process. Thus, it's
good to be able to profile a test run.

    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp(prefix='zope.testrunner-test-')

    >>> sys.argv = [
    ...     'test', '--layer=122', '--profile=cProfile',
    ...     '--profile-directory', tempdir,
    ...     '-t', 'TestNotMuch']
    >>> subunit_summarize(testrunner.run_internal, defaults)
    id=samplelayers.Layer1:setUp status=inprogress !runnable
    ...
    id=samplelayers.Layer1:tearDown status=success tags=(zope:layer) !runnable
    id=zope:profiler_stats status=inprogress !runnable
    id=zope:profiler_stats !runnable
    profiler-stats (application/x-binary-profile)
    ...\r
    <BLANKLINE>
    ...
    id=zope:profiler_stats status=success tags=(zope:profiler_stats) !runnable
    False

    >>> import shutil
    >>> shutil.rmtree(tempdir)


Errors
------

Errors are recorded in the subunit stream as MIME-encoded chunks of text.

(With subunit v2, errors and failures are unfortunately conflated: see
https://bugs.launchpad.net/subunit/+bug/1740158.)

    >>> sys.argv = ['test', '--tests-pattern', '^sampletests_e$']
    >>> subunit_summarize(testrunner.run_internal, defaults)
    id=zope.testrunner.layer.UnitTests:setUp status=inprogress !runnable
    id=zope.testrunner.layer.UnitTests:setUp status=success tags=(zope:layer)
      !runnable
    id=sample2.sampletests_e.eek status=inprogress
    id=sample2.sampletests_e.eek
    traceback (text/x-traceback...)
    Failed doctest test for sample2.sampletests_e.eek
     testrunner-ex/sample2/sampletests_e.py", Line NNN, in eek
    <BLANKLINE>
    ----------------------------------------------------------------------
    File testrunner-ex/sample2/sampletests_e.py", Line NNN, in sample2.sampletests_e.eek
    Failed example:
        f()
    Exception raised:
        Traceback (most recent call last):
          File "<doctest sample2.sampletests_e.eek[0]>", Line NNN, in ?
            f()
     testrunner-ex/sample2/sampletests_e.py", Line NNN, in f
            g()
     testrunner-ex/sample2/sampletests_e.py", Line NNN, in g
            x = y + 1
           - __traceback_info__: I don't know what Y should be.
        NameError: global name 'y' is not defined
    <BLANKLINE>
    id=sample2.sampletests_e.eek status=fail
      tags=(zope:layer:zope.testrunner.layer.UnitTests)
    id=sample2.sampletests_e.Test.test1 status=inprogress
    id=sample2.sampletests_e.Test.test1 status=success
      tags=(zope:layer:zope.testrunner.layer.UnitTests)
    id=sample2.sampletests_e.Test.test2 status=inprogress
    id=sample2.sampletests_e.Test.test2 status=success
      tags=(zope:layer:zope.testrunner.layer.UnitTests)
    id=sample2.sampletests_e.Test.test3 status=inprogress
    id=sample2.sampletests_e.Test.test3
    traceback (text/x-traceback...)
    Traceback (most recent call last):
     testrunner-ex/sample2/sampletests_e.py", Line NNN, in test3
        f()
     testrunner-ex/sample2/sampletests_e.py", Line NNN, in f
        g()
     testrunner-ex/sample2/sampletests_e.py", Line NNN, in g
        x = y + 1
       - __traceback_info__: I don't know what Y should be.
    NameError: global name 'y' is not defined
    <BLANKLINE>
    id=sample2.sampletests_e.Test.test3 status=fail
      tags=(zope:layer:zope.testrunner.layer.UnitTests)
    id=sample2.sampletests_e.Test.test4 status=inprogress
    id=sample2.sampletests_e.Test.test4 status=success
      tags=(zope:layer:zope.testrunner.layer.UnitTests)
    id=sample2.sampletests_e.Test.test5 status=inprogress
    id=sample2.sampletests_e.Test.test5 status=success
      tags=(zope:layer:zope.testrunner.layer.UnitTests)
    id=e_rst status=inprogress
    id=e_rst
    traceback (text/x-traceback...)
    Failed doctest test for e.rst
     testrunner-ex/sample2/e.rst", line 0
    <BLANKLINE>
    ----------------------------------------------------------------------
    File testrunner-ex/sample2/e.rst", Line NNN, in e.rst
    Failed example:
        f()
    Exception raised:
        Traceback (most recent call last):
          File "<doctest e.rst[1]>", Line NNN, in ?
            f()
          File "<doctest e.rst[0]>", Line NNN, in f
            return x
        NameError: global name 'x' is not defined
    <BLANKLINE>
    id=e_rst status=fail tags=(zope:layer:zope.testrunner.layer.UnitTests)
    id=zope.testrunner.layer.UnitTests:tearDown status=inprogress !runnable
    id=zope.testrunner.layer.UnitTests:tearDown status=success
      tags=(zope:layer) !runnable
    True


Layers that can't be torn down
------------------------------

A layer can have a tearDown method that raises NotImplementedError. If this is
the case, the subunit stream will say that the layer skipped its tearDown.

    >>> sys.argv = 'test -ssample2 --tests-pattern sampletests_ntd$'.split()
    >>> subunit_summarize(testrunner.run_internal, defaults)
    id=sample2.sampletests_ntd.Layer:setUp status=inprogress !runnable
    id=sample2.sampletests_ntd.Layer:setUp status=success tags=(zope:layer)
      !runnable
    id=sample2.sampletests_ntd.TestSomething.test_something status=inprogress
    id=sample2.sampletests_ntd.TestSomething.test_something status=success
      tags=(zope:layer:sample2.sampletests_ntd.Layer)
    id=sample2.sampletests_ntd.Layer:tearDown status=inprogress !runnable
    id=sample2.sampletests_ntd.Layer:tearDown !runnable
    reason (text/plain...)
    tearDown not supported
    id=sample2.sampletests_ntd.Layer:tearDown status=skip tags=(zope:layer)
      !runnable
    False


Module import errors
--------------------

We report module import errors too. They get encoded as tests with errors. The
name of the test is the module that could not be imported, the test's result
is an error containing the traceback. These "tests" are tagged with
zope:import_error.

Let's run tests including a module with some bad syntax:

    >>> sys.argv = [
    ...     'test', '--tests-pattern', '^(badsyntax|sampletests(f|_i)?)$',
    ...     '--layer', '1']
    >>> subunit_summarize(testrunner.run_internal, defaults)
    id=sample2.badsyntax status=inprogress
    id=sample2.badsyntax
    traceback (text/x-traceback...)
    Traceback (most recent call last):
      File "/home/benji/workspace/all-the-trunks/zope.testrunner/src/zope/testrunner/testrunner-ex/sample2/badsyntax.py", line 16
        importx unittest
                       ^
    SyntaxError: invalid syntax
    <BLANKLINE>
    id=sample2.badsyntax status=fail tags=(zope:import_error)
    id=sample2.sample21.sampletests_i status=inprogress
    id=sample2.sample21.sampletests_i
    traceback (text/x-traceback...)
    Traceback (most recent call last):
      File "/home/benji/workspace/all-the-trunks/zope.testrunner/src/zope/testrunner/testrunner-ex/sample2/sample21/sampletests_i.py", line 16, in <module>
        import zope.testrunner.huh
    ImportError: No module named huh
    <BLANKLINE>
    id=sample2.sample21.sampletests_i status=fail tags=(zope:import_error)
    id=sample2.sample23.sampletests_i status=inprogress
    id=sample2.sample23.sampletests_i
    traceback (text/x-traceback...)
    Traceback (most recent call last):
      File "/home/benji/workspace/all-the-trunks/zope.testrunner/src/zope/testrunner/testrunner-ex/sample2/sample23/sampletests_i.py", line 17, in <module>
        class Test(unittest.TestCase):
      File "/home/benji/workspace/all-the-trunks/zope.testrunner/src/zope/testrunner/testrunner-ex/sample2/sample23/sampletests_i.py", line 22, in Test
        raise TypeError('eek')
    TypeError: eek
    <BLANKLINE>
    id=sample2.sample23.sampletests_i status=fail tags=(zope:import_error)
    id=samplelayers.Layer1:setUp status=inprogress
    ...
    True


Tests in subprocesses
---------------------

If the tearDown method raises NotImplementedError and there are remaining
layers to run, the test runner will restart itself as a new process,
resuming tests where it left off:

    >>> sys.argv = [testrunner_script, '--tests-pattern', 'sampletests_ntd$']
    >>> subunit_summarize(testrunner.run_internal, defaults)
    id=sample1.sampletests_ntd.Layer:setUp status=inprogress !runnable
    id=sample1.sampletests_ntd.Layer:setUp status=success tags=(zope:layer)
      !runnable
    id=sample1.sampletests_ntd.TestSomething.test_something status=inprogress
    id=sample1.sampletests_ntd.TestSomething.test_something status=success
      tags=(zope:layer:sample1.sampletests_ntd.Layer)
    id=sample1.sampletests_ntd.Layer:tearDown status=inprogress !runnable
    id=sample1.sampletests_ntd.Layer:tearDown !runnable
    reason (text/plain...)
    tearDown not supported
    id=sample1.sampletests_ntd.Layer:tearDown status=skip tags=(zope:layer)
      !runnable
    id=Running in a subprocess. status=inprogress !runnable
    id=Running in a subprocess. status=success tags=(zope:info_suboptimal)
      !runnable
    id=sample2.sampletests_ntd.Layer:setUp status=inprogress !runnable
    id=sample2.sampletests_ntd.Layer:setUp status=success tags=(zope:layer)
      !runnable
    id=sample2.sampletests_ntd.TestSomething.test_something status=inprogress
    id=sample2.sampletests_ntd.TestSomething.test_something status=success
      tags=(zope:layer:sample2.sampletests_ntd.Layer)
    id=sample2.sampletests_ntd.Layer:tearDown status=inprogress !runnable
    id=sample2.sampletests_ntd.Layer:tearDown !runnable
    reason (text/plain...)
    tearDown not supported
    id=sample2.sampletests_ntd.Layer:tearDown status=skip tags=(zope:layer)
      !runnable
    id=Running in a subprocess. status=inprogress !runnable
    id=Running in a subprocess. status=success tags=(zope:info_suboptimal)
      !runnable
    id=sample3.sampletests_ntd.Layer:setUp status=inprogress !runnable
    id=sample3.sampletests_ntd.Layer:setUp status=success tags=(zope:layer)
      !runnable
    id=sample3.sampletests_ntd.TestSomething.test_error1 status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_error1
    traceback (text/x-traceback...)
    Traceback (most recent call last):
     testrunner-ex/sample3/sampletests_ntd.py", Line NNN, in test_error1
        raise TypeError("Can we see errors")
    TypeError: Can we see errors
    <BLANKLINE>
    id=sample3.sampletests_ntd.TestSomething.test_error1 status=fail
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=sample3.sampletests_ntd.TestSomething.test_error2 status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_error2
    traceback (text/x-traceback...)
    Traceback (most recent call last):
     testrunner-ex/sample3/sampletests_ntd.py", Line NNN, in test_error2
        raise TypeError("I hope so")
    TypeError: I hope so
    <BLANKLINE>
    id=sample3.sampletests_ntd.TestSomething.test_error2 status=fail
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=sample3.sampletests_ntd.TestSomething.test_fail1 status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_fail1
    traceback (text/x-traceback...)
    Traceback (most recent call last):
     testrunner-ex/sample3/sampletests_ntd.py", Line NNN, in test_fail1
        self.assertEqual(1, 2)
    AssertionError: 1 != 2
    <BLANKLINE>
    id=sample3.sampletests_ntd.TestSomething.test_fail1 status=fail
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=sample3.sampletests_ntd.TestSomething.test_fail2 status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_fail2
    traceback (text/x-traceback...)
    Traceback (most recent call last):
     testrunner-ex/sample3/sampletests_ntd.py", Line NNN, in test_fail2
        self.assertEqual(1, 3)
    AssertionError: 1 != 3
    <BLANKLINE>
    id=sample3.sampletests_ntd.TestSomething.test_fail2 status=fail
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=sample3.sampletests_ntd.TestSomething.test_something status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_something status=success
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=sample3.sampletests_ntd.TestSomething.test_something_else
      status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_something_else status=success
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=sample3.sampletests_ntd.Layer:tearDown status=inprogress !runnable
    id=sample3.sampletests_ntd.Layer:tearDown !runnable
    reason (text/plain...)
    tearDown not supported
    id=sample3.sampletests_ntd.Layer:tearDown status=skip tags=(zope:layer)
      !runnable
    True

Note that debugging doesn't work when running tests in a subprocess:

    >>> sys.argv = [testrunner_script, '--tests-pattern', 'sampletests_ntd$',
    ...             '-D', ]
    >>> subunit_summarize(testrunner.run_internal, defaults)
    id=sample1.sampletests_ntd.Layer:setUp status=inprogress !runnable
    id=sample1.sampletests_ntd.Layer:setUp status=success tags=(zope:layer)
      !runnable
    id=sample1.sampletests_ntd.TestSomething.test_something status=inprogress
    id=sample1.sampletests_ntd.TestSomething.test_something status=success
      tags=(zope:layer:sample1.sampletests_ntd.Layer)
    id=sample1.sampletests_ntd.Layer:tearDown status=inprogress !runnable
    id=sample1.sampletests_ntd.Layer:tearDown !runnable
    reason (text/plain...)
    tearDown not supported
    id=sample1.sampletests_ntd.Layer:tearDown status=skip tags=(zope:layer)
      !runnable
    id=Running in a subprocess. status=inprogress !runnable
    id=Running in a subprocess. status=success tags=(zope:info_suboptimal)
      !runnable
    id=sample2.sampletests_ntd.Layer:setUp status=inprogress !runnable
    id=sample2.sampletests_ntd.Layer:setUp status=success tags=(zope:layer)
      !runnable
    id=sample2.sampletests_ntd.TestSomething.test_something status=inprogress
    id=sample2.sampletests_ntd.TestSomething.test_something status=success
      tags=(zope:layer:sample2.sampletests_ntd.Layer)
    id=sample2.sampletests_ntd.Layer:tearDown status=inprogress !runnable
    id=sample2.sampletests_ntd.Layer:tearDown !runnable
    reason (text/plain...)
    tearDown not supported
    id=sample2.sampletests_ntd.Layer:tearDown status=skip tags=(zope:layer)
      !runnable
    id=Running in a subprocess. status=inprogress !runnable
    id=Running in a subprocess. status=success tags=(zope:info_suboptimal)
      !runnable
    id=sample3.sampletests_ntd.Layer:setUp status=inprogress !runnable
    id=sample3.sampletests_ntd.Layer:setUp status=success tags=(zope:layer)
      !runnable
    id=sample3.sampletests_ntd.TestSomething.test_error1 status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_error1
    traceback (text/x-traceback...)
    Traceback (most recent call last):
      File "/usr/lib/python2.6/unittest.py", line 305, in debug
        getattr(self, self._testMethodName)()
      File "/home/jml/src/zope.testrunner/subunit-output-formatter/src/zope/testing/testrunner/testrunner-ex/sample3/sampletests_ntd.py", line 42, in test_error1
        raise TypeError("Can we see errors")
    TypeError: Can we see errors
    <BLANKLINE>
    id=sample3.sampletests_ntd.TestSomething.test_error1 status=fail
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=Can't post-mortem debug when running a layer as a subprocess!
      status=inprogress !runnable
    id=Can't post-mortem debug when running a layer as a subprocess!
      status=success
      tags=(zope:error_with_banner zope:layer:sample3.sampletests_ntd.Layer)
      !runnable
    id=sample3.sampletests_ntd.TestSomething.test_error2 status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_error2
    traceback (text/x-traceback...)
    Traceback (most recent call last):
      File "/usr/lib/python2.6/unittest.py", line 305, in debug
        getattr(self, self._testMethodName)()
      File "/home/jml/src/zope.testrunner/subunit-output-formatter/src/zope/testing/testrunner/testrunner-ex/sample3/sampletests_ntd.py", line 45, in test_error2
        raise TypeError("I hope so")
    TypeError: I hope so
    <BLANKLINE>
    id=sample3.sampletests_ntd.TestSomething.test_error2 status=fail
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=Can't post-mortem debug when running a layer as a subprocess!
      status=inprogress !runnable
    id=Can't post-mortem debug when running a layer as a subprocess!
      status=success
      tags=(zope:error_with_banner zope:layer:sample3.sampletests_ntd.Layer)
      !runnable
    id=sample3.sampletests_ntd.TestSomething.test_fail1 status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_fail1
    traceback (text/x-traceback...)
    Traceback (most recent call last):
      File "/usr/lib/python2.6/unittest.py", line 305, in debug
        getattr(self, self._testMethodName)()
      File "/home/jml/src/zope.testrunner/subunit-output-formatter/src/zope/testing/testrunner/testrunner-ex/sample3/sampletests_ntd.py", line 48, in test_fail1
        self.assertEqual(1, 2)
      File "/usr/lib/python2.6/unittest.py", line 350, in failUnlessEqual
        (msg or '%r != %r' % (first, second))
    AssertionError: 1 != 2
    <BLANKLINE>
    id=sample3.sampletests_ntd.TestSomething.test_fail1 status=fail
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=Can't post-mortem debug when running a layer as a subprocess!
      status=inprogress !runnable
    id=Can't post-mortem debug when running a layer as a subprocess!
      status=success
      tags=(zope:error_with_banner zope:layer:sample3.sampletests_ntd.Layer)
      !runnable
    id=sample3.sampletests_ntd.TestSomething.test_fail2 status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_fail2
    traceback (text/x-traceback...)
    Traceback (most recent call last):
      File "/usr/lib/python2.6/unittest.py", line 305, in debug
        getattr(self, self._testMethodName)()
      File "/home/jml/src/zope.testrunner/subunit-output-formatter/src/zope/testing/testrunner/testrunner-ex/sample3/sampletests_ntd.py", line 51, in test_fail2
        self.assertEqual(1, 3)
      File "/usr/lib/python2.6/unittest.py", line 350, in failUnlessEqual
        (msg or '%r != %r' % (first, second))
    AssertionError: 1 != 3
    <BLANKLINE>
    id=sample3.sampletests_ntd.TestSomething.test_fail2 status=fail
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=Can't post-mortem debug when running a layer as a subprocess!
      status=inprogress !runnable
    id=Can't post-mortem debug when running a layer as a subprocess!
      status=success
      tags=(zope:error_with_banner zope:layer:sample3.sampletests_ntd.Layer)
      !runnable
    id=sample3.sampletests_ntd.TestSomething.test_something status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_something status=success
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=sample3.sampletests_ntd.TestSomething.test_something_else
      status=inprogress
    id=sample3.sampletests_ntd.TestSomething.test_something_else status=success
      tags=(zope:layer:sample3.sampletests_ntd.Layer)
    id=sample3.sampletests_ntd.Layer:tearDown status=inprogress !runnable
    id=sample3.sampletests_ntd.Layer:tearDown !runnable
    reason (text/plain...)
    tearDown not supported
    id=sample3.sampletests_ntd.Layer:tearDown status=skip tags=(zope:layer)
      !runnable
    True


Support skipped tests
---------------------

    >>> directory_with_skipped_tests = os.path.join(this_directory,
    ...                                             'testrunner-ex-skip')
    >>> skip_defaults = [
    ...     '--path', directory_with_skipped_tests,
    ...     '--tests-pattern', '^sample_skipped_tests$',
    ...  ]
    >>> sys.argv = ['test']
    >>> subunit_summarize(
    ...     testrunner.run_internal,
    ...     skip_defaults + ["--subunit-v2", "-t", "TestSkipppedNoLayer"])
    id=zope.testrunner.layer.UnitTests:setUp status=inprogress !runnable
    id=zope.testrunner.layer.UnitTests:setUp status=success tags=(zope:layer)
      !runnable
    id=sample_skipped_tests.TestSkipppedNoLayer.test_skipped status=inprogress
    id=sample_skipped_tests.TestSkipppedNoLayer.test_skipped
    reason (text/plain...)
    I'm a skipped test!
    id=sample_skipped_tests.TestSkipppedNoLayer.test_skipped status=skip
      tags=(zope:layer:zope.testrunner.layer.UnitTests)
    id=zope.testrunner.layer.UnitTests:tearDown status=inprogress !runnable
    id=zope.testrunner.layer.UnitTests:tearDown status=success
      tags=(zope:layer) !runnable
    False
