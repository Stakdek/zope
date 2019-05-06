============================================
 Layers To Organize and Share Test Fixtures
============================================

A *layer* is an object providing setup and teardown methods used to setup
and teardown the environment provided by the layer. It may also provide
setup and teardown methods used to reset the environment provided by the
layer between each test.

Layers are generally implemented as classes using class methods.

>>> class BaseLayer(object):
...     @classmethod
...     def setUp(cls):
...         log('BaseLayer.setUp')
...
...     @classmethod
...     def tearDown(cls):
...         log('BaseLayer.tearDown')
...
...     @classmethod
...     def testSetUp(cls):
...         log('BaseLayer.testSetUp')
...
...     @classmethod
...     def testTearDown(cls):
...         log('BaseLayer.testTearDown')


Layers can extend other layers.

.. important::

   Layers do not explicitly invoke the setup and teardown methods of
   other layers -- the test runner does this for us in order to
   minimize the number of invocations.

>>> class TopLayer(BaseLayer):
...     @classmethod
...     def setUp(cls):
...         log('TopLayer.setUp')
...
...     @classmethod
...     def tearDown(cls):
...         log('TopLayer.tearDown')
...
...     @classmethod
...     def testSetUp(cls):
...         log('TopLayer.testSetUp')
...
...     @classmethod
...     def testTearDown(cls):
...         log('TopLayer.testTearDown')
...

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

Before we can run the tests, we need to setup some helpers.

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

Now we run the tests. Note that the BaseLayer was not setup when
the TestSpecifyingNoLayer was run and setup/torn down around the
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
and run the tests again. This demonstrates the other method of specifying
a layer. This is generally how you specify what layer doctests need.

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

Now lets also specify a layer in the TestSpecifyingNoLayer class and rerun
the tests. This demonstrates that the most specific layer is used. It also
shows the behavior of nested layers - because TopLayer extends BaseLayer,
both the BaseLayer and TopLayer environments are setup when the
TestSpecifyingNoLayer tests are run.

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


If we inspect our trace of what methods got called in what order, we can
see that the layer setup and teardown methods only got called once. We can
also see that the layer's test setup and teardown methods got called for
each test using that layer in the right order.

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

Now lets stack a few more layers to ensure that our setUp and tearDown
methods are called in the correct order.

>>> from zope.testrunner.find import name_from_layer
>>> class A(object):
...     @classmethod
...     def setUp(cls):
...         log('%s.setUp' % name_from_layer(cls))
...
...     @classmethod
...     def tearDown(cls):
...         log('%s.tearDown' % name_from_layer(cls))
...
...     @classmethod
...     def testSetUp(cls):
...         log('%s.testSetUp' % name_from_layer(cls))
...
...     @classmethod
...     def testTearDown(cls):
...         log('%s.testTearDown' % name_from_layer(cls))
...
>>> class B(A): pass
>>> class C(B): pass
>>> class D(A): pass
>>> class E(D): pass
>>> class F(C,E): pass

>>> class DeepTest(unittest.TestCase):
...     layer = F
...     def test(self):
...         pass
>>> suite = unittest.makeSuite(DeepTest)
>>> log_handler.clear()
>>> runner = Runner(options=fresh_options(), args=[], found_suites=[suite])
>>> succeeded = runner.run() #doctest: +ELLIPSIS
Running ...F tests:
  Set up ...A in N.NNN seconds.
  Set up ...B in N.NNN seconds.
  Set up ...C in N.NNN seconds.
  Set up ...D in N.NNN seconds.
  Set up ...E in N.NNN seconds.
  Set up ...F in N.NNN seconds.
  Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
Tearing down left over layers:
  Tear down ...F in N.NNN seconds.
  Tear down ...E in N.NNN seconds.
  Tear down ...D in N.NNN seconds.
  Tear down ...C in N.NNN seconds.
  Tear down ...B in N.NNN seconds.
  Tear down ...A in N.NNN seconds.


>>> report() #doctest: +ELLIPSIS
Report:
...A.setUp
...B.setUp
...C.setUp
...D.setUp
...E.setUp
...F.setUp
...A.testSetUp
...B.testSetUp
...C.testSetUp
...D.testSetUp
...E.testSetUp
...F.testSetUp
...F.testTearDown
...E.testTearDown
...D.testTearDown
...C.testTearDown
...B.testTearDown
...A.testTearDown
...F.tearDown
...E.tearDown
...D.tearDown
...C.tearDown
...B.tearDown
...A.tearDown
