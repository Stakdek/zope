==============
 zope.browser
==============

.. image:: https://img.shields.io/pypi/v/zope.browser.svg
        :target: https://pypi.python.org/pypi/zope.browser/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/zope.browser.svg
        :target: https://pypi.org/project/zope.browser/
        :alt: Supported Python versions

.. image:: https://travis-ci.org/zopefoundation/zope.browser.svg?branch=master
        :target: https://travis-ci.org/zopefoundation/zope.browser

.. image:: https://coveralls.io/repos/github/zopefoundation/zope.browser/badge.svg?branch=master
        :target: https://coveralls.io/github/zopefoundation/zope.browser?branch=master

.. image:: https://readthedocs.org/projects/zopebrowser/badge/?version=latest
        :target: https://zopebrowser.readthedocs.io/en/latest/
        :alt: Documentation Status


This package provides shared browser components for the Zope Toolkit.
These components consist of a set of interfaces defining common
concepts, including:

- ``IView``
- ``IBrowserView``
- ``IAdding``
- ``ITerms``
- ``ISystemErrorView``

Documentation is hosted at https://zopebrowser.readthedocs.io


===========
 Changelog
===========

2.3 (2018-10-05)
================

- Add support for Python 3.7.


2.2.0 (2017-08-10)
==================

- Add support for Python 3.5 and 3.6.

- Drop support for Python 2.6, 3.2 and 3.3.

- Host documentation at https://zopebrowser.readthedocs.io

2.1.0 (2014-12-26)
==================

- Add support for Python 3.4.

- Add support for testing on Travis.

2.0.2 (2013-03-08)
==================

- Add Trove classifiers indicating CPython, 3.2 and PyPy support.

2.0.1 (2013-02-11)
==================

- Add support for testing with tox.

2.0.0 (2013-02-11)
==================

- Test coverage of 100% verified.

- Add support for Python 3.3 and PyPy.

- Drop support for Python 2.4 and 2.5.

1.3 (2010-04-30)
================

- Remove ``test`` extra and ``zope.testing`` dependency.

1.2 (2009-05-18)
================

- Move ``ISystemErrorView`` interface here from
  ``zope.app.exception`` to break undesirable dependencies.

- Fix home page and author's e-mail address.

- Add doctests to ``long_description``.

1.1 (2009-05-13)
================

- Move ``IAdding`` interface here from ``zope.app.container.interfaces``
  to break undesirable dependencies.

1.0 (2009-05-13)
================

- Move ``IView`` and ``IBrowserView`` interfaces here from
  ``zope.publisher.interfaces`` to break undesirable dependencies.

0.5.0 (2008-12-11)
==================

- Move ``ITerms`` interface here from ``zope.app.form.browser.interfaces``
  to break undesirable dependencies.


