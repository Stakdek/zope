""" Add unit and functional testing support to setuptools-driven eggs.
"""
from __future__ import print_function
from setuptools.command.test import ScanningLoader
from setuptools.command.test import test as BaseCommand

def skipLayers(suite, _result=None):
    """ Walk the suite returned by setuptools' testloader.

    o Skip any tests which have a 'layer' defined.
    """
    from unittest import TestSuite
    if _result is None:
        _result = TestSuite()
    # Sometimes test suites do not have tests, like DocFileSuite.
    if not suite._tests:
        _result.addTest(suite)
        return _result
    for test in suite._tests:
        layer = getattr(test, 'layer', None)
        if layer is not None:
            continue
        if isinstance(test, TestSuite):
            skipLayers(test, _result)
        else:
            _result.addTest(test)
    return _result

class SkipLayers(ScanningLoader):
    """
    Load only unit tests (those which have no layer associated with
    them).

    * Running the tests using 'setup.py test' cannot, by default,
      drive the full testrunner, with its support for layers (in
      functional tests).  This loader allows the command to work, by
      running only those tests which don't need the layer support.

    * To run layer-dependent tests, use 'setup.py ftest' (see below
      for adding the command to your setup.py).

    * To use this loader your package add the following your 'setup()'
      call::

        setup(
            ...
            setup_requires=[
                'eggtestinfo' # captures testing metadata in EGG-INFO
            ],
            tests_require=['zope.testrunner', ],
            ...
            test_loader='zope.testrunner.eggsupport:SkipLayers',
            ...
        )
    """
    def loadTestsFromModule(self, module):
        return skipLayers(
            ScanningLoader.loadTestsFromModule(self, module))

    def loadTestsFromNames(self, testNames, module):
        return skipLayers(
            ScanningLoader.loadTestsFromNames(self, testNames, module))


def print_usage():
    print('python setup.py ftest')
    print()
    print(ftest.__doc__)

class ftest(BaseCommand):
    """
    Run unit and functional tests after an in-place build.

    * Note that this command runs *all* tests (unit *and* functional).

    * This command does not provide any of the configuration options which
      the usual testrunner provided by 'zope.testrunner' offers:  it is intended
      to allow easy verification that a package has been installed correctly
      via setuptools, but is not likely to be useful for developers working
      on the package.

    * Developers working on the package will likely prefer to work with
      the stock testrunner, e.g., by using buildout with a recipe which
      configures the testrunner as a standalone script.

    * To use this in your pacakge add the following to the 'entry_points'
      section::

          setup(
              ...
              setup_requires=[
                  'zope.testrunner',
                  'eggtestinfo' # captures testing metadata in EGG-INFO
              ],
              ...
          )
    """
    description = "Run all functional and unit tests after in-place build"
    user_options = []
    help_options = [('usage', '?', 'Show usage', print_usage)]

    def initialize_options(self):
        pass # suppress normal handling

    def finalize_options(self):
        pass # suppress normal handling

    def run(self):
        from zope.testrunner import run
        args = ['IGNORE_ME']

        dist = self.distribution
        for src_loc in (dist.package_dir.values() or ['.']):
            args += ['--test-path', src_loc]

        if dist.install_requires:
            dist.fetch_build_eggs(dist.install_requires)

        if dist.tests_require:
            dist.fetch_build_eggs(dist.tests_require)

        def _run():
            run(args=args)

        self.with_project_on_sys_path(_run)
