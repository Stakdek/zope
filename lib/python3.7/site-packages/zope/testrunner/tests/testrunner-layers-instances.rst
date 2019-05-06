=========================================
 Layers Implemented via Object Instances
=========================================

Layers are generally implemented as classes using class methods, but
regular objects can be used as well. They need to provide ``__module__``,
``__name__``, and ``__bases__`` attributes.

>>> class TestLayer(object):
...     def __init__(self, name, *bases):
...         self.__name__ = name
...         self.__bases__ = bases
...
...     def setUp(self):
...         log('%s.setUp' % self.__name__)
...
...     def tearDown(self):
...         log('%s.tearDown' % self.__name__)
...
...     def testSetUp(self):
...         log('%s.testSetUp' % self.__name__)
...
...     def testTearDown(self):
...         log('%s.testTearDown' % self.__name__)

>>> BaseLayer = TestLayer('BaseLayer')
>>> TopLayer = TestLayer('TopLayer', BaseLayer)

Tests or test suites specify what layer they need by storing a reference
in the ``layer`` attribute.

>>> import unittest
>>> class TestSpecifyingBaseLayer(unittest.TestCase):
...     'This TestCase explicitly specifies its layer'
...     layer = BaseLayer
...     name = 'TestSpecifyingBaseLayer' # For testing only
...
...     def setUp(self):
...         log('TestSpecifyingBaseLayer.setUp')
...
...     def tearDown(self):
...         log('TestSpecifyingBaseLayer.tearDown')
...
...     def test1(self):
...         log('TestSpecifyingBaseLayer.test1')
...
...     def test2(self):
...         log('TestSpecifyingBaseLayer.test2')
...
>>> class TestSpecifyingNoLayer(unittest.TestCase):
...     'This TestCase specifies no layer'
...     name = 'TestSpecifyingNoLayer' # For testing only
...     def setUp(self):
...         log('TestSpecifyingNoLayer.setUp')
...
...     def tearDown(self):
...         log('TestSpecifyingNoLayer.tearDown')
...
...     def test1(self):
...         log('TestSpecifyingNoLayer.test')
...
...     def test2(self):
...         log('TestSpecifyingNoLayer.test')
...

Create a TestSuite containing two test suites, one for each of
TestSpecifyingBaseLayer and TestSpecifyingNoLayer.

>>> umbrella_suite = unittest.TestSuite()
>>> umbrella_suite.addTest(unittest.makeSuite(TestSpecifyingBaseLayer))
>>> no_layer_suite = unittest.makeSuite(TestSpecifyingNoLayer)
>>> umbrella_suite.addTest(no_layer_suite)

Before we can run the tests, we need to set up some helpers.

>>> from zope.testrunner import options
>>> from zope.testing.loggingsupport import InstalledHandler
>>> import logging
>>> log_handler = InstalledHandler('zope.testrunner.tests')
>>> def log(msg):
...     logging.getLogger('zope.testrunner.tests').info(msg)
>>> def fresh_options():
...     opts = options.get_options(['--test-filter', '.*'])
...     opts.resume_layer = None
...     opts.resume_number = 0
...     return opts

Now we run the tests. Note that the BaseLayer was not set up when the
TestSpecifyingNoLayer was run and set up/torn down around the
TestSpecifyingBaseLayer tests.

>>> from zope.testrunner.runner import Runner
>>> runner = Runner(options=fresh_options(), args=[], found_suites=[umbrella_suite])
>>> succeeded = runner.run()
Running zope.testrunner.layer.UnitTests tests:
  Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
  Ran 2 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
Running ...BaseLayer tests:
  Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
  Set up ...BaseLayer in N.NNN seconds.
  Ran 2 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
Tearing down left over layers:
  Tear down ...BaseLayer in N.NNN seconds.
Total: 4 tests, 0 failures, 0 errors and 0 skipped in N.NNN seconds.


Now lets specify a layer in the suite containing TestSpecifyingNoLayer
and run the tests again. This demonstrates the other method of
specifying a layer. This is generally how you specify what layer
doctests need.

>>> no_layer_suite.layer = BaseLayer
>>> runner = Runner(options=fresh_options(), args=[], found_suites=[umbrella_suite])
>>> succeeded = runner.run()
Running ...BaseLayer tests:
  Set up ...BaseLayer in N.NNN seconds.
  Ran 4 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
Tearing down left over layers:
  Tear down ...BaseLayer in N.NNN seconds.

Clear our logged output, as we want to inspect it shortly.

>>> log_handler.clear()

Now lets also specify a layer in the TestSpecifyingNoLayer class and
rerun the tests. This demonstrates that the most specific layer is
used. It also shows the behavior of nested layers - because TopLayer
extends BaseLayer, both the BaseLayer and TopLayer environments are
set up when the TestSpecifyingNoLayer tests are run.

>>> TestSpecifyingNoLayer.layer = TopLayer
>>> runner = Runner(options=fresh_options(), args=[], found_suites=[umbrella_suite])
>>> succeeded = runner.run()
Running ...BaseLayer tests:
  Set up ...BaseLayer in N.NNN seconds.
  Ran 2 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
Running ...TopLayer tests:
  Set up ...TopLayer in N.NNN seconds.
  Ran 2 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
Tearing down left over layers:
  Tear down ...TopLayer in N.NNN seconds.
  Tear down ...BaseLayer in N.NNN seconds.
Total: 4 tests, 0 failures, 0 errors and 0 skipped in N.NNN seconds.


If we inspect our trace of what methods got called in what order, we
can see that the layer setUp and tearDown methods only got called
once. We can also see that the layer's test setUp and tearDown methods
got called for each test using that layer in the right order.

>>> def report():
...     print("Report:")
...     for record in log_handler.records:
...         print(record.getMessage())
>>> report()
Report:
BaseLayer.setUp
BaseLayer.testSetUp
TestSpecifyingBaseLayer.setUp
TestSpecifyingBaseLayer.test1
TestSpecifyingBaseLayer.tearDown
BaseLayer.testTearDown
BaseLayer.testSetUp
TestSpecifyingBaseLayer.setUp
TestSpecifyingBaseLayer.test2
TestSpecifyingBaseLayer.tearDown
BaseLayer.testTearDown
TopLayer.setUp
BaseLayer.testSetUp
TopLayer.testSetUp
TestSpecifyingNoLayer.setUp
TestSpecifyingNoLayer.test
TestSpecifyingNoLayer.tearDown
TopLayer.testTearDown
BaseLayer.testTearDown
BaseLayer.testSetUp
TopLayer.testSetUp
TestSpecifyingNoLayer.setUp
TestSpecifyingNoLayer.test
TestSpecifyingNoLayer.tearDown
TopLayer.testTearDown
BaseLayer.testTearDown
TopLayer.tearDown
BaseLayer.tearDown
