This is a test for a fix in buffering of output from a layer in a subprocess.

Prior to the change that this tests, output from within a test layer in a
subprocess would be buffered.  This could wreak havoc on supervising processes
(or human) that would kill a test run if no output was seen for some period of
time.

First, we wrap stdout with an object that instruments it. It notes the time at
which a given line was written.

    >>> import os, sys, datetime
    >>> class RecordingStreamWrapper(object):
    ...     def __init__(self, wrapped):
    ...         self.record = []
    ...         self.wrapped = wrapped
    ...     @property
    ...     def buffer(self):
    ...         # runner._get_output_buffer attempts to write b''
    ...         # to us, and when that fails (see write()), accesses our .buffer directly.
    ...         # That object deals in bytes.
    ...         wrapper = self
    ...         class buffer(object):
    ...             def write(self, data):
    ...                  assert isinstance(data, bytes)
    ...                  wrapper.write(data.decode('utf-8'))
    ...             def writelines(self, lines):
    ...                  for line in lines:
    ...                      self.write(line)
    ...             def flush(self):
    ...                  wrapper.flush()
    ...         return buffer()
    ...     def write(self, out):
    ...         # sys.stdout deals with native strings;
    ...         # and raises TypeError for other things. We must do
    ...         # the same.
    ...         if not isinstance(out, str):
    ...              raise TypeError
    ...         self.record.append((out, datetime.datetime.now()))
    ...         self.wrapped.write(out)
    ...     def writelines(self, lines):
    ...         for line in lines:
    ...             self.write(line)
    ...     def flush(self):
    ...         self.wrapped.flush()
    ...
    >>> sys.stdout = RecordingStreamWrapper(sys.stdout)

Now we actually call our test.  If you open the file to which we are referring
here (zope/testrunner/tests/testrunner-ex/sampletests_buffering.py) you will
see two test suites, each with its own layer that does not know how to tear
down.  This forces the second suite to be run in a subprocess.

That second suite has two tests.  Both sleep for half a second each.

    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> from zope import testrunner
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     ]
    >>> argv = [sys.argv[0],
    ...         '-vv', '--tests-pattern', '^sampletests_buffering.*']

    >>> try:
    ...     testrunner.run_internal(defaults, argv)
    ...     record = sys.stdout.record
    ... finally:
    ...     sys.stdout = sys.stdout.wrapped
    ...
    Running tests at level 1
    Running sampletests_buffering.Layer1 tests:
      Set up sampletests_buffering.Layer1 in N.NNN seconds.
      Running:
     test_something (sampletests_buffering.TestSomething1)
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running sampletests_buffering.Layer2 tests:
      Tear down sampletests_buffering.Layer1 ... not supported
      Running in a subprocess.
      Set up sampletests_buffering.Layer2 in N.NNN seconds.
      Running:
     test_something (sampletests_buffering.TestSomething2)
     test_something2 (sampletests_buffering.TestSomething2)
      Ran 2 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
      Tear down sampletests_buffering.Layer2 ... not supported
    Total: 3 tests, 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    False

Now we actually check the results we care about.  We should see that there are
two pauses of about half a second, one around the first test and one around the
second.  Before the change that this test verifies, there was a single pause of
more than a second after the second suite ran.

    >>> def assert_progressive_output():
    ...     pause = datetime.timedelta(seconds=0.3)
    ...     last_line, last_time = record.pop(0)
    ...     print('---')
    ...     for line, time in record:
    ...         if time-last_time >= pause:
    ...             # We paused!
    ...             print('PAUSE FOUND BETWEEN THESE LINES:')
    ...             print(''.join([last_line, line, '-' * 70]))
    ...         last_line, last_time = line, time

    >>> assert_progressive_output() # doctest: +ELLIPSIS
    ---...
    PAUSE FOUND BETWEEN THESE LINES:...
      Running:
     test_something (sampletests_buffering.TestSomething2)
    ----------------------------------------------------------------------
    PAUSE FOUND BETWEEN THESE LINES:
     test_something (sampletests_buffering.TestSomething2)
     test_something2 (sampletests_buffering.TestSomething2)
    ---...

Because this is a test based on timing, it may be somewhat fragile.  However,
on a relatively slow machine, this timing works out fine; I'm hopeful that this
test will not be a source of spurious errors.  If it is, we will have to
readdress.

Now let's do the same thing, but with multiple processes at once.  We'll get
a different result that has similar characteristics.  Note that we don't have
to use a special layer that doesn't support teardown to force the layer we're
interested in to run in a subprocess: the test runner now does that when you
ask for parallel execution.  The other layer now just makes the test output
non-deterministic, so we'll skip it.

    >>> sys.stdout = RecordingStreamWrapper(sys.stdout)
    >>> argv.extend(['-j', '2', '--layer=sampletests_buffering.Layer2'])
    >>> try:
    ...     testrunner.run_internal(defaults, argv)
    ...     record = sys.stdout.record
    ... finally:
    ...     sys.stdout = sys.stdout.wrapped
    ...
    Running tests at level 1
    Running .EmptyLayer tests:
      Set up .EmptyLayer in N.NNN seconds.
      Running:
      Ran 0 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    [Parallel tests running in sampletests_buffering.Layer2:
      .. LAYER FINISHED]
    Running sampletests_buffering.Layer2 tests:
      Running in a subprocess.
      Set up sampletests_buffering.Layer2 in N.NNN seconds.
      Ran 2 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
      Tear down sampletests_buffering.Layer2 ... not supported
    Tearing down left over layers:
      Tear down .EmptyLayer in N.NNN seconds.
    Total: 2 tests, 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    False

Notice that, with a -vv (or greater) verbosity, the parallel test run includes
a progress report to keep track of tests run in the various layers.  Because
the actual results are saved to be displayed assembled in the original test
order, the progress report shows up before we are given the news that the
testrunner is starting Layer2.  This is counterintuitive, but lets us keep the
primary reporting information for the given layer in one location, while also
giving us progress reports that can be used for keepalive analysis by a human or
automated agent. In particular for the second point, notice below that, as
before, the progress output is not buffered.

    >>> def assert_progressive_output():
    ...     pause = datetime.timedelta(seconds=0.3)
    ...     last_line, last_time = record.pop(0)
    ...     print('---')
    ...     for line, time in record:
    ...         if time-last_time >= pause:
    ...             # We paused!
    ...             print('PAUSE FOUND BETWEEN THIS OUTPUT:')
    ...             print('\n'.join([last_line, line, '-'*70]))
    ...         last_line, last_time = line, time

    >>> assert_progressive_output() # doctest: +ELLIPSIS
    ---...
    PAUSE FOUND BETWEEN THIS OUTPUT:...
    .
    .
    ----------------------------------------------------------------------
    PAUSE FOUND BETWEEN THIS OUTPUT:
    .
     LAYER FINISHED
    ---...
