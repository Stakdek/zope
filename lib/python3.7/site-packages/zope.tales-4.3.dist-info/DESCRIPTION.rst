============
 zope.tales
============

.. image:: https://img.shields.io/pypi/v/zope.tales.svg
        :target: https://pypi.python.org/pypi/zope.tales/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/zope.tales.svg
        :target: https://pypi.org/project/zope.tales/
        :alt: Supported Python versions

.. image:: https://travis-ci.org/zopefoundation/zope.tales.svg?branch=master
        :target: https://travis-ci.org/zopefoundation/zope.tales

.. image:: https://coveralls.io/repos/github/zopefoundation/zope.tales/badge.svg?branch=master
        :target: https://coveralls.io/github/zopefoundation/zope.tales?branch=master

.. image:: https://readthedocs.org/projects/zopetales/badge/?version=latest
        :target: https://zopetales.readthedocs.io/en/latest/
        :alt: Documentation Status


``zope.tales`` (Template Attribute Language - Expression Syntax) is an
expression language designed to work with `zope.tal
<https://zopetal.readthedocs.io>`_ (although it can be used
independently). The two are integrated to produce page templates in
`zope.pagetemplate <https://zopepagetemplate.readthedocs.io/>`_.

The specification for TAL and TALES can be found at
https://pagetemplates.readthedocs.io/en/latest/

Documentation on this implementation and its API can be found at
https://zopetales.readthedocs.io/


=========
 Changes
=========

4.3 (2018-10-05)
================

- Add support for Python 3.7.

- Host documentation at https://zopetales.readthedocs.io

4.2.0 (2017-09-22)
==================

- Add support for Python 3.5 and 3.6.

- Drop support for Python 2.6, 3.2 and 3.3.

- Drop support for ``python setup.py test``.

- Reach 100% test coverage and maintain it via tox.ini and Travis CI.

4.1.1 (2015-06-06)
==================

- Add support for Python 3.2 and PyPy3.


4.1.0 (2014-12-29)
==================

.. note::

   Support for PyPy3 is pending release of a fix for:
   https://bitbucket.org/pypy/pypy/issue/1946

- Add support for Python 3.4.

- Add support for testing on Travis.


4.0.2 (2013-11-12)
==================

- Add missing ``six`` dependency


4.0.1 (2013-02-22)
==================

- Fix a previously untested Python 3.3 compatibility problem.


4.0.0 (2013-02-14)
==================

- Remove hard dependency on ``zope.tal``, which was already conditionalized
  but required via ``setup.py``.

- Add support for Python 3.3 and PyPy.

- Replace deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Drop support for Python 2.4 and 2.5.

- Fix documentation link in README.txt


3.5.2 (2012-05-23)
==================

- Subexpressions of a 'string:' expression can be only path expressions.
  https://bugs.launchpad.net/zope.tales/+bug/1002242


3.5.1 (2010-04-30)
==================

- Remove use of ``zope.testing.doctestunit`` in favor of stdlib's 'doctest.


3.5.0 (2010-01-01)
==================

- Port the lazy expression from ``Products.PageTemplates``.


3.4.0 (2007-10-03)
==================

- Update package setup.

- Initial release outside the Zope 3 trunk.


3.2.0 (2006-01-05)
==================

- Corresponds to the verison of the zope.tales package shipped as part of
  the Zope 3.2.0 release.

- Documentation / test fixes.


3.0.0 (2004-11-07)
==================

- Corresponds to the verison of the zope.tales package shipped as part of
  the Zope X3.0.0 release.


