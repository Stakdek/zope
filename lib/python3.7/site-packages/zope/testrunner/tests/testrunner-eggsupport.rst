====================
 Setuptools Support
====================


The ``ftest`` Setup Command
===========================

The `.ftest` class is a proper `distutils` command and
`zope.testrunner` exposes it as such via an entry point.

  >>> import pkg_resources
  >>> ws = pkg_resources.WorkingSet()
  >>> eps = dict([(ep.name, ep)
  ...             for ep in ws.iter_entry_points('distutils.commands')])
  >>> 'ftest' in eps
  True
  >>> eps['ftest']
  EntryPoint.parse('ftest = zope.testrunner.eggsupport:ftest')

Let's now run this command:

  >>> import zope.testrunner
  >>> org_run = zope.testrunner.run

  >>> def run(args):
  ...     print(' '.join(args))
  >>> zope.testrunner.run = run

  >>> import os, tempfile, shutil
  >>> tmpdir = tempfile.mkdtemp()
  >>> srcdir = os.path.join(tmpdir, 'src')
  >>> os.mkdir(srcdir)

  >>> import setuptools.dist
  >>> dist = setuptools.dist.Distribution(
  ...     {'package_dir': {'': srcdir},
  ...      'script_name': __file__})

  >>> from zope.testrunner.eggsupport import ftest
  >>> ftest(dist).run()
  IGNORE_ME --test-path .../src

Cleanup:

  >>> zope.testrunner.run = org_run
  >>> shutil.rmtree(tmpdir)


Skipping Tests with Layers
==========================

The `.SkipLayers` scanning test loader can replace the standard test loader,
so that any tests that require layers are skipped. This is necessary, since
the standard setuptools testing facility does not handle layers. It can be
used as follows::

      setup(
          ...
          setup_requires=[
              'eggtestinfo' # captures testing metadata in EGG-INFO
          ],
          tests_require=[
              'zope.testrunner',
          ],
          ...
          test_loader='zope.testrunner.eggsupport:SkipLayers',
          ...
      )

Let's now create some test suites to make sure that all tests with layers are
properly skipped.

  >>> import doctest
  >>> import unittest

  >>> all = unittest.TestSuite()
  >>> class T1(unittest.TestCase):
  ...     def test_t1(self):
  ...         pass
  >>> class T2(unittest.TestCase):
  ...     layer = 'layer'
  ...     def test_t2(self):
  ...         pass
  >>> T3 = doctest.DocTestSuite('zope.testrunner.find')
  >>> T4 = doctest.DocTestSuite('zope.testrunner.options')
  >>> T4.layer = 'layer'
  >>> T5 = doctest.DocFileSuite('testrunner.rst', package='zope.testrunner.tests')
  >>> T6 = doctest.DocFileSuite('testrunner-gc.rst', package='zope.testrunner.tests')
  >>> T6.layer = 'layer'

  >>> all = unittest.TestSuite((
  ...     unittest.makeSuite(T1), unittest.makeSuite(T2), T3, T4, T5, T6,
  ...     ))

Let's return those tests from the scan:

  >>> from setuptools.command.test import ScanningLoader
  >>> orig_loadTestsFromModule = ScanningLoader.loadTestsFromModule
  >>> ScanningLoader.loadTestsFromModule = lambda *args: all

Now we can retrieve the modules from the layer skipping loader:

  >>> from zope.testrunner.eggsupport import SkipLayers
  >>> filtered = SkipLayers().loadTestsFromModule('zope.testrunner')

  >>> len(filtered._tests)
  3
  >>> from pprint import pprint
  >>> pprint(filtered._tests)
  [<...T1 testMethod=test_t1>,
   StartUpFailure (zope.testrunner.find),
   .../zope/testrunner/tests/testrunner.rst]

Cleanup:

  >>> ScanningLoader.loadTestsFromModule = orig_loadTestsFromModule

When the distribution specified a ``test_suite``, another method is used to
load the tests.

  >>> orig_loadTestsFromNames = ScanningLoader.loadTestsFromNames
  >>> ScanningLoader.loadTestsFromNames = lambda *args: all

Now we can retrieve the modules from the layer skipping loader:

  >>> from zope.testrunner.eggsupport import SkipLayers
  >>> filtered = SkipLayers().loadTestsFromNames(
  ...     'zope.testrunner.tests.test_suite', 'zope.testrunner')

  >>> len(filtered._tests)
  3
  >>> from pprint import pprint
  >>> pprint(filtered._tests)
  [<...T1 testMethod=test_t1>,
   StartUpFailure (zope.testrunner.find),
   .../zope/testrunner/tests/testrunner.rst]

Cleanup:

  >>> ScanningLoader.loadTestsFromNames = orig_loadTestsFromNames
