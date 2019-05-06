===============
 ``zope.size``
===============

.. image:: https://img.shields.io/pypi/v/zope.size.svg
        :target: https://pypi.python.org/pypi/zope.size/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/zope.size.svg
        :target: https://pypi.org/project/zope.size/
        :alt: Supported Python versions

.. image:: https://travis-ci.org/zopefoundation/zope.size.svg?branch=master
        :target: https://travis-ci.org/zopefoundation/zope.size

.. image:: https://readthedocs.org/projects/zopesize/badge/?version=latest
        :target: https://zopesize.readthedocs.io/en/latest/
        :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/zopefoundation/zope.size/badge.svg?branch=master
        :target: https://coveralls.io/github/zopefoundation/zope.size?branch=master

This package provides a definition of simple interface that allows
applications to retrieve the size of the object for displaying and for sorting.

The default adapter is also provided. It expects objects to have the ``getSize``
method that returns size in bytes.  However, the adapter won't crash if an
object doesn't have one and will show size as "not available" instead.

Development is hosted at https://github.com/zopefoundation/zope.size

Documentation is hosted at https://zopesize.readthedocs.io


Changes
=======

4.3 (2018-10-05)
----------------

- Add support for Python 3.7.


4.2.0 (2017-07-27)
------------------

- Add support for Python 3.5 and 3.6.

- Drop support for Python 2.6, 3.2 and 3.3.


4.1.0 (2014-12-29)
------------------

- Add support for PyPy3.

- Add support for Python 3.4.

- Add support for testing on Travis.


4.0.1 (2013-03-08)
------------------

- Add Trove classifiers indicating CPython and PyPy support.


4.0.0 (2013-02-13)
------------------

- Replace deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Drop support for Python 2.4 and 2.5.

- Add support for Python 3.2 and 3.3.

- Conditionally disable tests that require ``zope.configuration`` and
  ``zope.security``.


3.5.0 (2011-11-29)
------------------

- Include zcml dependencies in configure.zcml, require the necessary packages
  via a zcml extra, added tests for zcml.

3.4.1 (2009-09-10)
------------------

- Add support for bootstrapping on Jython.

- Add docstrings.

- Beautify package's README and include CHANGES into the description.

- Change package's url to PyPI instead of Subversion.

3.4.0 (2006-09-29)
------------------

- First release as a separate egg


