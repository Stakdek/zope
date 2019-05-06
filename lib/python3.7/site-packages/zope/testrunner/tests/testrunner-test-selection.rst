===============================================
 Selecting Tests By Package, Module, and Level
===============================================

We've :doc:`already seen <testrunner-layers>` that we can select tests
by layer. There are three other ways we can select tests: by package,
by module and test, and by level.

Packages
========

We can select tests by package:

    >>> import os.path, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     ]

    >>> sys.argv = 'test --layer 122 -ssample1 -vv'.split()
    >>> from zope import testrunner
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running samplelayers.Layer122 tests:
      Set up samplelayers.Layer1 in 0.000 seconds.
      Set up samplelayers.Layer12 in 0.000 seconds.
      Set up samplelayers.Layer122 in 0.000 seconds.
      Running:
        test_x1 (sample1.sampletests.test122.TestA)
        test_y0 (sample1.sampletests.test122.TestA)
        test_z0 (sample1.sampletests.test122.TestA)
        test_x0 (sample1.sampletests.test122.TestB)
        test_y1 (sample1.sampletests.test122.TestB)
        test_z0 (sample1.sampletests.test122.TestB)
        test_1 (sample1.sampletests.test122.TestNotMuch)
        test_2 (sample1.sampletests.test122.TestNotMuch)
        test_3 (sample1.sampletests.test122.TestNotMuch)
        test_x0 (sample1.sampletests.test122)
        test_y0 (sample1.sampletests.test122)
        test_z1 (sample1.sampletests.test122)
        testrunner-ex/sample1/sampletests/../../sampletestsl.rst
      Ran 13 tests with 0 failures, 0 errors and 0 skipped in 0.005 seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer122 in 0.000 seconds.
      Tear down samplelayers.Layer12 in 0.000 seconds.
      Tear down samplelayers.Layer1 in 0.000 seconds.
    False

You can specify multiple packages:

    >>> sys.argv = 'test -u  -vv -ssample1 -ssample2'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_x1 (sample1.sampletestsf.TestA)
     test_y0 (sample1.sampletestsf.TestA)
     test_z0 (sample1.sampletestsf.TestA)
     test_x0 (sample1.sampletestsf.TestB)
     test_y1 (sample1.sampletestsf.TestB)
     test_z0 (sample1.sampletestsf.TestB)
     test_1 (sample1.sampletestsf.TestNotMuch)
     test_2 (sample1.sampletestsf.TestNotMuch)
     test_3 (sample1.sampletestsf.TestNotMuch)
     test_x0 (sample1.sampletestsf)
     test_y0 (sample1.sampletestsf)
     test_z1 (sample1.sampletestsf)
     testrunner-ex/sample1/../sampletests.rst
     test_x1 (sample1.sample11.sampletests.TestA)
     test_y0 (sample1.sample11.sampletests.TestA)
     test_z0 (sample1.sample11.sampletests.TestA)
     test_x0 (sample1.sample11.sampletests.TestB)
     test_y1 (sample1.sample11.sampletests.TestB)
     test_z0 (sample1.sample11.sampletests.TestB)
     test_1 (sample1.sample11.sampletests.TestNotMuch)
     test_2 (sample1.sample11.sampletests.TestNotMuch)
     test_3 (sample1.sample11.sampletests.TestNotMuch)
     test_x0 (sample1.sample11.sampletests)
     test_y0 (sample1.sample11.sampletests)
     test_z1 (sample1.sample11.sampletests)
     testrunner-ex/sample1/sample11/../../sampletests.rst
     test_x1 (sample1.sample13.sampletests.TestA)
     test_y0 (sample1.sample13.sampletests.TestA)
     test_z0 (sample1.sample13.sampletests.TestA)
     test_x0 (sample1.sample13.sampletests.TestB)
     test_y1 (sample1.sample13.sampletests.TestB)
     test_z0 (sample1.sample13.sampletests.TestB)
     test_1 (sample1.sample13.sampletests.TestNotMuch)
     test_2 (sample1.sample13.sampletests.TestNotMuch)
     test_3 (sample1.sample13.sampletests.TestNotMuch)
     test_x0 (sample1.sample13.sampletests)
     test_y0 (sample1.sample13.sampletests)
     test_z1 (sample1.sample13.sampletests)
     testrunner-ex/sample1/sample13/../../sampletests.rst
     test_x1 (sample1.sampletests.test1.TestA)
     test_y0 (sample1.sampletests.test1.TestA)
     test_z0 (sample1.sampletests.test1.TestA)
     test_x0 (sample1.sampletests.test1.TestB)
     test_y1 (sample1.sampletests.test1.TestB)
     test_z0 (sample1.sampletests.test1.TestB)
     test_1 (sample1.sampletests.test1.TestNotMuch)
     test_2 (sample1.sampletests.test1.TestNotMuch)
     test_3 (sample1.sampletests.test1.TestNotMuch)
     test_x0 (sample1.sampletests.test1)
     test_y0 (sample1.sampletests.test1)
     test_z1 (sample1.sampletests.test1)
     testrunner-ex/sample1/sampletests/../../sampletests.rst
     test_x1 (sample1.sampletests.test_one.TestA)
     test_y0 (sample1.sampletests.test_one.TestA)
     test_z0 (sample1.sampletests.test_one.TestA)
     test_x0 (sample1.sampletests.test_one.TestB)
     test_y1 (sample1.sampletests.test_one.TestB)
     test_z0 (sample1.sampletests.test_one.TestB)
     test_1 (sample1.sampletests.test_one.TestNotMuch)
     test_2 (sample1.sampletests.test_one.TestNotMuch)
     test_3 (sample1.sampletests.test_one.TestNotMuch)
     test_x0 (sample1.sampletests.test_one)
     test_y0 (sample1.sampletests.test_one)
     test_z1 (sample1.sampletests.test_one)
     testrunner-ex/sample1/sampletests/../../sampletests.rst
     test_x1 (sample2.sample21.sampletests.TestA)
     test_y0 (sample2.sample21.sampletests.TestA)
     test_z0 (sample2.sample21.sampletests.TestA)
     test_x0 (sample2.sample21.sampletests.TestB)
     test_y1 (sample2.sample21.sampletests.TestB)
     test_z0 (sample2.sample21.sampletests.TestB)
     test_1 (sample2.sample21.sampletests.TestNotMuch)
     test_2 (sample2.sample21.sampletests.TestNotMuch)
     test_3 (sample2.sample21.sampletests.TestNotMuch)
     test_x0 (sample2.sample21.sampletests)
     test_y0 (sample2.sample21.sampletests)
     test_z1 (sample2.sample21.sampletests)
     testrunner-ex/sample2/sample21/../../sampletests.rst
     test_x1 (sample2.sampletests.test_1.TestA)
     test_y0 (sample2.sampletests.test_1.TestA)
     test_z0 (sample2.sampletests.test_1.TestA)
     test_x0 (sample2.sampletests.test_1.TestB)
     test_y1 (sample2.sampletests.test_1.TestB)
     test_z0 (sample2.sampletests.test_1.TestB)
     test_1 (sample2.sampletests.test_1.TestNotMuch)
     test_2 (sample2.sampletests.test_1.TestNotMuch)
     test_3 (sample2.sampletests.test_1.TestNotMuch)
     test_x0 (sample2.sampletests.test_1)
     test_y0 (sample2.sampletests.test_1)
     test_z1 (sample2.sampletests.test_1)
     testrunner-ex/sample2/sampletests/../../sampletests.rst
     test_x1 (sample2.sampletests.testone.TestA)
     test_y0 (sample2.sampletests.testone.TestA)
     test_z0 (sample2.sampletests.testone.TestA)
     test_x0 (sample2.sampletests.testone.TestB)
     test_y1 (sample2.sampletests.testone.TestB)
     test_z0 (sample2.sampletests.testone.TestB)
     test_1 (sample2.sampletests.testone.TestNotMuch)
     test_2 (sample2.sampletests.testone.TestNotMuch)
     test_3 (sample2.sampletests.testone.TestNotMuch)
     test_x0 (sample2.sampletests.testone)
     test_y0 (sample2.sampletests.testone)
     test_z1 (sample2.sampletests.testone)
     testrunner-ex/sample2/sampletests/../../sampletests.rst
      Ran 104 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Directory Names
---------------

You can specify directory names instead of packages (useful for
tab-completion):

    >>> subdir = os.path.join(directory_with_tests, 'sample1')
    >>> sys.argv = ['test', '--layer', '122', '-s', subdir, '-vv']
    >>> from zope import testrunner
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running samplelayers.Layer122 tests:
      Set up samplelayers.Layer1 in 0.000 seconds.
      Set up samplelayers.Layer12 in 0.000 seconds.
      Set up samplelayers.Layer122 in 0.000 seconds.
      Running:
        test_x1 (sample1.sampletests.test122.TestA)
        test_y0 (sample1.sampletests.test122.TestA)
        test_z0 (sample1.sampletests.test122.TestA)
        test_x0 (sample1.sampletests.test122.TestB)
        test_y1 (sample1.sampletests.test122.TestB)
        test_z0 (sample1.sampletests.test122.TestB)
        test_1 (sample1.sampletests.test122.TestNotMuch)
        test_2 (sample1.sampletests.test122.TestNotMuch)
        test_3 (sample1.sampletests.test122.TestNotMuch)
        test_x0 (sample1.sampletests.test122)
        test_y0 (sample1.sampletests.test122)
        test_z1 (sample1.sampletests.test122)
        testrunner-ex/sample1/sampletests/../../sampletestsl.rst
      Ran 13 tests with 0 failures, 0 errors and 0 skipped in 0.005 seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer122 in 0.000 seconds.
      Tear down samplelayers.Layer12 in 0.000 seconds.
      Tear down samplelayers.Layer1 in 0.000 seconds.
    False

Modules And Tests
=================

We can select by test module name using the --module (-m) option:

    >>> sys.argv = 'test -u  -vv -ssample1 -m_one -mtest1'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_x1 (sample1.sampletests.test1.TestA)
     test_y0 (sample1.sampletests.test1.TestA)
     test_z0 (sample1.sampletests.test1.TestA)
     test_x0 (sample1.sampletests.test1.TestB)
     test_y1 (sample1.sampletests.test1.TestB)
     test_z0 (sample1.sampletests.test1.TestB)
     test_1 (sample1.sampletests.test1.TestNotMuch)
     test_2 (sample1.sampletests.test1.TestNotMuch)
     test_3 (sample1.sampletests.test1.TestNotMuch)
     test_x0 (sample1.sampletests.test1)
     test_y0 (sample1.sampletests.test1)
     test_z1 (sample1.sampletests.test1)
     testrunner-ex/sample1/sampletests/../../sampletests.rst
     test_x1 (sample1.sampletests.test_one.TestA)
     test_y0 (sample1.sampletests.test_one.TestA)
     test_z0 (sample1.sampletests.test_one.TestA)
     test_x0 (sample1.sampletests.test_one.TestB)
     test_y1 (sample1.sampletests.test_one.TestB)
     test_z0 (sample1.sampletests.test_one.TestB)
     test_1 (sample1.sampletests.test_one.TestNotMuch)
     test_2 (sample1.sampletests.test_one.TestNotMuch)
     test_3 (sample1.sampletests.test_one.TestNotMuch)
     test_x0 (sample1.sampletests.test_one)
     test_y0 (sample1.sampletests.test_one)
     test_z1 (sample1.sampletests.test_one)
     testrunner-ex/sample1/sampletests/../../sampletests.rst
      Ran 26 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


and by test within the module using the --test (-t) option:

    >>> sys.argv = 'test -u  -vv -ssample1 -m_one -mtest1 -t_x0 -t_y0'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_y0 (sample1.sampletests.test1.TestA)
     test_x0 (sample1.sampletests.test1.TestB)
     test_x0 (sample1.sampletests.test1)
     test_y0 (sample1.sampletests.test1)
     test_y0 (sample1.sampletests.test_one.TestA)
     test_x0 (sample1.sampletests.test_one.TestB)
     test_x0 (sample1.sampletests.test_one)
     test_y0 (sample1.sampletests.test_one)
      Ran 8 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


    >>> sys.argv = 'test -u  -vv -ssample1 -trst'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     testrunner-ex/sample1/../sampletests.rst
     testrunner-ex/sample1/sample11/../../sampletests.rst
     testrunner-ex/sample1/sample13/../../sampletests.rst
     testrunner-ex/sample1/sampletests/../../sampletests.rst
     testrunner-ex/sample1/sampletests/../../sampletests.rst
      Ran 5 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Regular Expressions
-------------------

The ``--module`` and ``--test`` options take regular expressions.  If the
regular expressions specified begin with ``!``, then tests that don't
match the regular expression are selected:

    >>> sys.argv = 'test -u  -vv -ssample1 -m!sample1[.]sample1'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_x1 (sample1.sampletestsf.TestA)
     test_y0 (sample1.sampletestsf.TestA)
     test_z0 (sample1.sampletestsf.TestA)
     test_x0 (sample1.sampletestsf.TestB)
     test_y1 (sample1.sampletestsf.TestB)
     test_z0 (sample1.sampletestsf.TestB)
     test_1 (sample1.sampletestsf.TestNotMuch)
     test_2 (sample1.sampletestsf.TestNotMuch)
     test_3 (sample1.sampletestsf.TestNotMuch)
     test_x0 (sample1.sampletestsf)
     test_y0 (sample1.sampletestsf)
     test_z1 (sample1.sampletestsf)
     testrunner-ex/sample1/../sampletests.rst
     test_x1 (sample1.sampletests.test1.TestA)
     test_y0 (sample1.sampletests.test1.TestA)
     test_z0 (sample1.sampletests.test1.TestA)
     test_x0 (sample1.sampletests.test1.TestB)
     test_y1 (sample1.sampletests.test1.TestB)
     test_z0 (sample1.sampletests.test1.TestB)
     test_1 (sample1.sampletests.test1.TestNotMuch)
     test_2 (sample1.sampletests.test1.TestNotMuch)
     test_3 (sample1.sampletests.test1.TestNotMuch)
     test_x0 (sample1.sampletests.test1)
     test_y0 (sample1.sampletests.test1)
     test_z1 (sample1.sampletests.test1)
     testrunner-ex/sample1/sampletests/../../sampletests.rst
     test_x1 (sample1.sampletests.test_one.TestA)
     test_y0 (sample1.sampletests.test_one.TestA)
     test_z0 (sample1.sampletests.test_one.TestA)
     test_x0 (sample1.sampletests.test_one.TestB)
     test_y1 (sample1.sampletests.test_one.TestB)
     test_z0 (sample1.sampletests.test_one.TestB)
     test_1 (sample1.sampletests.test_one.TestNotMuch)
     test_2 (sample1.sampletests.test_one.TestNotMuch)
     test_3 (sample1.sampletests.test_one.TestNotMuch)
     test_x0 (sample1.sampletests.test_one)
     test_y0 (sample1.sampletests.test_one)
     test_z1 (sample1.sampletests.test_one)
     testrunner-ex/sample1/sampletests/../../sampletests.rst
      Ran 39 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Positional Arguments
--------------------

Module and test filters can also be given as positional arguments:


    >>> sys.argv = 'test -u  -vv -ssample1 !sample1[.]sample1'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_x1 (sample1.sampletestsf.TestA)
     test_y0 (sample1.sampletestsf.TestA)
     test_z0 (sample1.sampletestsf.TestA)
     test_x0 (sample1.sampletestsf.TestB)
     test_y1 (sample1.sampletestsf.TestB)
     test_z0 (sample1.sampletestsf.TestB)
     test_1 (sample1.sampletestsf.TestNotMuch)
     test_2 (sample1.sampletestsf.TestNotMuch)
     test_3 (sample1.sampletestsf.TestNotMuch)
     test_x0 (sample1.sampletestsf)
     test_y0 (sample1.sampletestsf)
     test_z1 (sample1.sampletestsf)
     testrunner-ex/sample1/../sampletests.rst
     test_x1 (sample1.sampletests.test1.TestA)
     test_y0 (sample1.sampletests.test1.TestA)
     test_z0 (sample1.sampletests.test1.TestA)
     test_x0 (sample1.sampletests.test1.TestB)
     test_y1 (sample1.sampletests.test1.TestB)
     test_z0 (sample1.sampletests.test1.TestB)
     test_1 (sample1.sampletests.test1.TestNotMuch)
     test_2 (sample1.sampletests.test1.TestNotMuch)
     test_3 (sample1.sampletests.test1.TestNotMuch)
     test_x0 (sample1.sampletests.test1)
     test_y0 (sample1.sampletests.test1)
     test_z1 (sample1.sampletests.test1)
     testrunner-ex/sample1/sampletests/../../sampletests.rst
     test_x1 (sample1.sampletests.test_one.TestA)
     test_y0 (sample1.sampletests.test_one.TestA)
     test_z0 (sample1.sampletests.test_one.TestA)
     test_x0 (sample1.sampletests.test_one.TestB)
     test_y1 (sample1.sampletests.test_one.TestB)
     test_z0 (sample1.sampletests.test_one.TestB)
     test_1 (sample1.sampletests.test_one.TestNotMuch)
     test_2 (sample1.sampletests.test_one.TestNotMuch)
     test_3 (sample1.sampletests.test_one.TestNotMuch)
     test_x0 (sample1.sampletests.test_one)
     test_y0 (sample1.sampletests.test_one)
     test_z1 (sample1.sampletests.test_one)
     testrunner-ex/sample1/sampletests/../../sampletests.rst
      Ran 39 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


    >>> sys.argv = 'test -u  -vv -ssample1 . rst'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     testrunner-ex/sample1/../sampletests.rst
     testrunner-ex/sample1/sample11/../../sampletests.rst
     testrunner-ex/sample1/sample13/../../sampletests.rst
     testrunner-ex/sample1/sampletests/../../sampletests.rst
     testrunner-ex/sample1/sampletests/../../sampletests.rst
      Ran 5 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Levels
======

Sometimes there are tests that you don't want to run by default. For
example, you might have tests that take a long time. Tests can have a
level attribute. If no level is specified, a level of 1 is assumed
and, by default, only tests at level one are run. to run tests at a
higher level, use the ``--at-level`` (``-a``) option to specify a higher
level. For example, with the following options:


    >>> sys.argv = 'test -u  -vv -t test_y1 -t test_y0'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_y0 (sampletestsf.TestA)
     test_y1 (sampletestsf.TestB)
     test_y0 (sampletestsf)
     test_y0 (sample1.sampletestsf.TestA)
     test_y1 (sample1.sampletestsf.TestB)
     test_y0 (sample1.sampletestsf)
     test_y0 (sample1.sample11.sampletests.TestA)
     test_y1 (sample1.sample11.sampletests.TestB)
     test_y0 (sample1.sample11.sampletests)
     test_y0 (sample1.sample13.sampletests.TestA)
     test_y1 (sample1.sample13.sampletests.TestB)
     test_y0 (sample1.sample13.sampletests)
     test_y0 (sample1.sampletests.test1.TestA)
     test_y1 (sample1.sampletests.test1.TestB)
     test_y0 (sample1.sampletests.test1)
     test_y0 (sample1.sampletests.test_one.TestA)
     test_y1 (sample1.sampletests.test_one.TestB)
     test_y0 (sample1.sampletests.test_one)
     test_y0 (sample2.sample21.sampletests.TestA)
     test_y1 (sample2.sample21.sampletests.TestB)
     test_y0 (sample2.sample21.sampletests)
     test_y0 (sample2.sampletests.test_1.TestA)
     test_y1 (sample2.sampletests.test_1.TestB)
     test_y0 (sample2.sampletests.test_1)
     test_y0 (sample2.sampletests.testone.TestA)
     test_y1 (sample2.sampletests.testone.TestB)
     test_y0 (sample2.sampletests.testone)
     test_y0 (sample3.sampletests.TestA)
     test_y1 (sample3.sampletests.TestB)
     test_y0 (sample3.sampletests)
     test_y0 (sampletests.test1.TestA)
     test_y1 (sampletests.test1.TestB)
     test_y0 (sampletests.test1)
     test_y0 (sampletests.test_one.TestA)
     test_y1 (sampletests.test_one.TestB)
     test_y0 (sampletests.test_one)
      Ran 36 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


We get run 36 tests.  If we specify a level of 2, we get some
additional tests:

    >>> sys.argv = 'test -u  -vv -a 2 -t test_y1 -t test_y0'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 2
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_y0 (sampletestsf.TestA)
     test_y0 (sampletestsf.TestA2)
     test_y1 (sampletestsf.TestB)
     test_y0 (sampletestsf)
     test_y0 (sample1.sampletestsf.TestA)
     test_y1 (sample1.sampletestsf.TestB)
     test_y0 (sample1.sampletestsf)
     test_y0 (sample1.sample11.sampletests.TestA)
     test_y1 (sample1.sample11.sampletests.TestB)
     test_y1 (sample1.sample11.sampletests.TestB2)
     test_y0 (sample1.sample11.sampletests)
     test_y0 (sample1.sample13.sampletests.TestA)
     test_y1 (sample1.sample13.sampletests.TestB)
     test_y0 (sample1.sample13.sampletests)
     test_y0 (sample1.sampletests.test1.TestA)
     test_y1 (sample1.sampletests.test1.TestB)
     test_y0 (sample1.sampletests.test1)
     test_y0 (sample1.sampletests.test_one.TestA)
     test_y1 (sample1.sampletests.test_one.TestB)
     test_y0 (sample1.sampletests.test_one)
     test_y0 (sample2.sample21.sampletests.TestA)
     test_y1 (sample2.sample21.sampletests.TestB)
     test_y0 (sample2.sample21.sampletests)
     test_y0 (sample2.sampletests.test_1.TestA)
     test_y1 (sample2.sampletests.test_1.TestB)
     test_y0 (sample2.sampletests.test_1)
     test_y0 (sample2.sampletests.testone.TestA)
     test_y1 (sample2.sampletests.testone.TestB)
     test_y0 (sample2.sampletests.testone)
     test_y0 (sample3.sampletests.TestA)
     test_y1 (sample3.sampletests.TestB)
     test_y0 (sample3.sampletests)
     test_y0 (sampletests.test1.TestA)
     test_y1 (sampletests.test1.TestB)
     test_y0 (sampletests.test1)
     test_y0 (sampletests.test_one.TestA)
     test_y1 (sampletests.test_one.TestB)
     test_y0 (sampletests.test_one)
      Ran 38 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


We can use the --all option to run tests at all levels:

    >>> sys.argv = 'test -u  -vv --all -t test_y1 -t test_y0'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at all levels
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_y0 (sampletestsf.TestA)
     test_y0 (sampletestsf.TestA2)
     test_y1 (sampletestsf.TestB)
     test_y0 (sampletestsf)
     test_y0 (sample1.sampletestsf.TestA)
     test_y1 (sample1.sampletestsf.TestB)
     test_y0 (sample1.sampletestsf)
     test_y0 (sample1.sample11.sampletests.TestA)
     test_y0 (sample1.sample11.sampletests.TestA3)
     test_y1 (sample1.sample11.sampletests.TestB)
     test_y1 (sample1.sample11.sampletests.TestB2)
     test_y0 (sample1.sample11.sampletests)
     test_y0 (sample1.sample13.sampletests.TestA)
     test_y1 (sample1.sample13.sampletests.TestB)
     test_y0 (sample1.sample13.sampletests)
     test_y0 (sample1.sampletests.test1.TestA)
     test_y1 (sample1.sampletests.test1.TestB)
     test_y0 (sample1.sampletests.test1)
     test_y0 (sample1.sampletests.test_one.TestA)
     test_y1 (sample1.sampletests.test_one.TestB)
     test_y0 (sample1.sampletests.test_one)
     test_y0 (sample2.sample21.sampletests.TestA)
     test_y1 (sample2.sample21.sampletests.TestB)
     test_y0 (sample2.sample21.sampletests)
     test_y0 (sample2.sampletests.test_1.TestA)
     test_y1 (sample2.sampletests.test_1.TestB)
     test_y0 (sample2.sampletests.test_1)
     test_y0 (sample2.sampletests.testone.TestA)
     test_y1 (sample2.sampletests.testone.TestB)
     test_y0 (sample2.sampletests.testone)
     test_y0 (sample3.sampletests.TestA)
     test_y1 (sample3.sampletests.TestB)
     test_y0 (sample3.sampletests)
     test_y0 (sampletests.test1.TestA)
     test_y1 (sampletests.test1.TestB)
     test_y0 (sampletests.test1)
     test_y0 (sampletests.test_one.TestA)
     test_y1 (sampletests.test_one.TestB)
     test_y0 (sampletests.test_one)
      Ran 39 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Listing Selected Tests
======================

When you're trying to figure out why the test you want is not matched by the
pattern you specified, it is convenient to see which tests match your
specifications.

    >>> sys.argv = 'test --all -m sample1 -t test_y0 --list-tests'.split()
    >>> testrunner.run_internal(defaults)
    Listing zope.testrunner.layer.UnitTests tests:
      test_y0 (sample1.sampletestsf.TestA)
      test_y0 (sample1.sampletestsf)
      test_y0 (sample1.sample11.sampletests.TestA)
      test_y0 (sample1.sample11.sampletests.TestA3)
      test_y0 (sample1.sample11.sampletests)
      test_y0 (sample1.sample13.sampletests.TestA)
      test_y0 (sample1.sample13.sampletests)
      test_y0 (sample1.sampletests.test1.TestA)
      test_y0 (sample1.sampletests.test1)
      test_y0 (sample1.sampletests.test_one.TestA)
      test_y0 (sample1.sampletests.test_one)
    Listing samplelayers.Layer11 tests:
      test_y0 (sample1.sampletests.test11.TestA)
      test_y0 (sample1.sampletests.test11)
    Listing samplelayers.Layer111 tests:
      test_y0 (sample1.sampletests.test111.TestA)
      test_y0 (sample1.sampletests.test111)
    Listing samplelayers.Layer112 tests:
      test_y0 (sample1.sampletests.test112.TestA)
      test_y0 (sample1.sampletests.test112)
    Listing samplelayers.Layer12 tests:
      test_y0 (sample1.sampletests.test12.TestA)
      test_y0 (sample1.sampletests.test12)
    Listing samplelayers.Layer121 tests:
      test_y0 (sample1.sampletests.test121.TestA)
      test_y0 (sample1.sampletests.test121)
    Listing samplelayers.Layer122 tests:
      test_y0 (sample1.sampletests.test122.TestA)
      test_y0 (sample1.sampletests.test122)
    False
