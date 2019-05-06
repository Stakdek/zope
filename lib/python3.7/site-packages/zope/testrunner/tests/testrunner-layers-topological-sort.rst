Now lets stack a few more layers to ensure that our setUp and tearDown
methods are called in the correct order.

>>> from zope.testing.loggingsupport import InstalledHandler
>>> from zope.testrunner.find import name_from_layer
>>> from zope.testrunner import options
>>> from zope.testrunner.runner import Runner
>>> import logging
>>> import unittest

>>> def fresh_options():
...     opts = options.get_options(['--test-filter', '.*'])
...     opts.resume_layer = None
...     opts.resume_number = 0
...     return opts
>>> def log(msg):
...     logging.getLogger('zope.testrunner.tests').info(msg)
>>> log_handler = InstalledHandler('zope.testrunner.tests')

>>> class A(object):
...     def setUp(cls):
...         log('%s.setUp' % name_from_layer(cls))
...     setUp = classmethod(setUp)
...
...     def tearDown(cls):
...         log('%s.tearDown' % name_from_layer(cls))
...     tearDown = classmethod(tearDown)
...
...     def testSetUp(cls):
...         log('%s.testSetUp' % name_from_layer(cls))
...     testSetUp = classmethod(testSetUp)
...
...     def testTearDown(cls):
...         log('%s.testTearDown' % name_from_layer(cls))
...     testTearDown = classmethod(testTearDown)
...         
>>> class AB(A): pass
>>> class AC(A): pass
>>> class AAAABD(AB): pass
>>> class ZZZABE(AB): pass
>>> class MMMACF(AC): pass

>>> class DeepTest1(unittest.TestCase):
...     layer = AAAABD
...     def test(self):
...         pass
>>> class DeepTest2(unittest.TestCase):
...     layer = MMMACF
...     def test(self):
...         pass
>>> class DeepTest3(unittest.TestCase):
...     layer = ZZZABE
...     def test(self):
...         pass
>>> class QuickTests(unittest.TestCase):
...     def test(self):
...         pass
>>> suite = unittest.TestSuite()
>>> suite.addTest(unittest.makeSuite(DeepTest1))
>>> suite.addTest(unittest.makeSuite(DeepTest2))
>>> suite.addTest(unittest.makeSuite(DeepTest3))
>>> suite.addTest(unittest.makeSuite(QuickTests))
>>> log_handler.clear()
>>> runner = Runner(options=fresh_options(), args=[], found_suites=[suite])
>>> succeeded = runner.run() #doctest: +ELLIPSIS
Running zope.testrunner.layer.UnitTests tests:
  Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
  Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
Running ...AAAABD tests:
  Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
  Set up ...A in N.NNN seconds.
  Set up ...AB in N.NNN seconds.
  Set up ...AAAABD in N.NNN seconds.
  Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
Running ...ZZZABE tests:
  Tear down ...AAAABD in N.NNN seconds.
  Set up ...ZZZABE in N.NNN seconds.
  Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
Running ...MMMACF tests:
  Tear down ...ZZZABE in N.NNN seconds.
  Tear down ...AB in N.NNN seconds.
  Set up ...AC in N.NNN seconds.
  Set up ...MMMACF in N.NNN seconds.
  Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
Tearing down left over layers:
  Tear down ...MMMACF in N.NNN seconds.
  Tear down ...AC in N.NNN seconds.
  Tear down ...A in N.NNN seconds.
Total: 4 tests, 0 failures, 0 errors and 0 skipped in N.NNN seconds.

