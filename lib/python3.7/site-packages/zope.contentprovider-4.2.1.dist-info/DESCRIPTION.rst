======================
 zope.contentprovider
======================

.. image:: https://img.shields.io/pypi/v/zope.contentprovider.svg
        :target: https://pypi.python.org/pypi/zope.contentprovider/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/zope.contentprovider.svg
        :target: https://pypi.org/project/zope.contentprovider/
        :alt: Supported Python versions

.. image:: https://travis-ci.org/zopefoundation/zope.contentprovider.svg?branch=master
        :target: https://travis-ci.org/zopefoundation/zope.contentprovider

.. image:: https://coveralls.io/repos/github/zopefoundation/zope.contentprovider/badge.svg?branch=master
        :target: https://coveralls.io/github/zopefoundation/zope.contentprovider?branch=master

.. image:: https://readthedocs.org/projects/zopecontentprovider/badge/?version=latest
        :target: https://zopecontentprovider.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

This package provides a framework to develop componentized Web GUI
applications. Instead of describing the content of a page using a single
template or static system of templates and METAL macros, content provider
objects are dynamically looked up based on the setup/configuration of the
application.

Detailed documentation is available at https://zopecontentprovider.readthedocs.io


=========
 Changes
=========

4.2.1 (2018-11-08)
==================

- Fix deprecation warnings.


4.2 (2018-10-05)
================

- Add support for Python 3.7.

- Fixed UpdateNotCalled being an instance rather than an exception class
  (`#4 <https://github.com/zopefoundation/zope.contentprovider/issues/4>`_).

- Host documentation at https://zopecontentprovider.readthedocs.io

4.1.0 (2017-08-08)
==================

- Add support for Python 3.5 and 3.6.

- Drop support for Python 2.6 and 3.3.


4.0.0 (2014-12-24)
==================

- Add support for PyPy and PyPy3.

- Add support for Python 3.4.

- Add support for testing on Travis.


4.0.0a1 (2013-02-22)
====================

- Add Python 3.3 support.

- Replace deprecated ``zope.component.adapts`` usage with equivalent
  ``zope.component.adapter`` decorator.

- Replace deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Drop support for Python 2.4 and 2.5.


3.7.2 (2010-05-25)
==================

- Fix unit tests broken under Python 2.4 by the switch to the standard
  library ``doctest`` module.


3.7.1 (2010-04-30)
==================

- Prefer the standard library's ``doctest`` module to the one from
  ``zope.testing.``


3.7 (2010-04-27)
================

- Since ``tales:expressiontype`` is now in ``zope.browserpage``, update
  conditional ZCML accordingly so it doesn't depend on the presence of
  ``zope.app.pagetemplate`` anymore.


3.6.1 (2009-12-23)
==================

- Ensure that our ``configure.zcml`` can be loaded without requiring further
  dependencies. It uses a ``tales:expressiontype`` directive defined in
  ``zope.app.pagetemplate.`` We keep that dependency optional, as not all
  consumers of this package use ZCML to configure the expression type.


3.6.0 (2009-12-22)
==================

- Update test dependency to use ``zope.browserpage``.


3.5.0 (2009-03-18)
==================

- Add very simple, but useful base class for implementing content
  providers, see ``zope.contentprovider.provider.ContentProviderBase``.

- Remove unneeded testing dependencies. We only need ``zope.testing`` and
  ``zope.app.pagetemplate``.

- Remove zcml slug and old zpkg-related files.

- Add setuptools dependency to setup.py.

- Clean up package's description and documentation a bit. Remove
  duplicate text in README.

- Change mailing list address to zope-dev at zope.org instead of
  retired one.

- Change ``cheeseshop`` to ``pypi`` in the package url.


3.4.0 (2007-10-02)
==================

- Initial release independent of the main Zope tree.


