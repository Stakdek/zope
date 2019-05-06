==============
 zope.viewlet
==============

.. image:: https://img.shields.io/pypi/v/zope.viewlet.svg
        :target: https://pypi.python.org/pypi/zope.viewlet/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/zope.viewlet.svg
        :target: https://pypi.org/project/zope.viewlet/
        :alt: Supported Python versions

.. image:: https://travis-ci.org/zopefoundation/zope.viewlet.svg?branch=master
        :target: https://travis-ci.org/zopefoundation/zope.viewlet

.. image:: https://coveralls.io/repos/github/zopefoundation/zope.viewlet/badge.svg?branch=master
        :target: https://coveralls.io/github/zopefoundation/zope.viewlet?branch=master

.. image:: https://readthedocs.org/projects/zopeviewlet/badge/?version=latest
        :target: https://zopeviewlet.readthedocs.io/en/latest/
        :alt: Documentation Status


Viewlets provide a generic framework for building pluggable user
interfaces. Viewlets are a special type of `content provider
<https://pypi.python.org/pypi/zope.contentprovider>`_ that allows a
template to define a region (a "viewlet manager"") into which content
("viewlets") can be plugged.

Documentation is hosted at https://zopeviewlet.readthedocs.io/


=========
 Changes
=========

4.2.1 (2018-12-17)
==================

- Fix deprecation warnings.
  (`#11 <https://github.com/zopefoundation/zope.viewlet/pull/11>`_)


4.2 (2018-10-09)
================

- Add support for Python 3.7.

- Host documentation at https://zopeviewlet.readthedocs.io

4.1.0 (2017-09-23)
==================

- Add support for Python 3.5 and 3.6.

- Drop support for Python 2.6 and 3.3.


4.0.0 (2014-12-24)
==================

- Add support for PyPy and PyPy3.

- Add support for Python 3.4.

- Add support for testing on Travis.


4.0.0a1 (2013-02-24)
====================

- Add support for Python 3.3.

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

- Remove use of 'zope.testing.doctest' in favor of stdlib's 'doctest.

- Fix dubious quoting in metadirectives.py. Closes
  https://bugs.launchpad.net/zope2/+bug/143774.


3.7.0 (2009-12-22)
==================

- Depend on ``zope.browserpage`` in favor of ``zope.app.pagetemplate``.


3.6.1 (2009-08-29)
==================

- Fix unit tests in README.txt.


3.6.0 (2009-08-02)
==================

- Optimize the the script tag for the JS viewlet. This makes YSlow happy.

- Remove ZCML slugs and old zpkg-related files.

- Drop all testing dependncies except ``zope.testing``.


3.5.0 (2009-01-26)
==================

- Remove the dependency on ``zope.app.publisher`` by moving four simple helper
  functions into this package and making the interface for describing the
  ZCML content provider directive explicit.

- Typo fix in CSSViewlet docstring.


3.4.2 (2008-01-24)
==================

- Re-release of 3.4.1 because of brown bag release.


3.4.1 (2008-01-21)
==================

- Implement missing ``__contains__`` method in IViewletManager

- Implement additional viewlet managers offering weight ordered sorting

- Implement additional viewlet managers offering conditional filtering


3.4.1a (2007-4-22)
==================

- Add a missing ',' behind ``zope.i18nmessageid``.

- Recreate the ``README.txt`` removing everything except for the overview.


3.4.0 (2007-10-10)
==================

- Initial release independent of the main Zope tree.


