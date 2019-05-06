===================
 zope.sequencesort
===================

.. image:: https://img.shields.io/pypi/v/zope.sequencesort.svg
   :target: https://pypi.org/project/zope.sequencesort/
   :alt: Latest Version

.. image:: https://travis-ci.org/zopefoundation/zope.sequencesort.svg?branch=master
   :target: https://travis-ci.org/zopefoundation/zope.sequencesort

.. image:: https://readthedocs.org/projects/zopesequencesort/badge/?version=latest
   :target: https://zopesequencesort.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/zopefoundation/zope.sequencesort/badge.svg
   :target: https://coveralls.io/github/zopefoundation/zope.sequencesort



This package provides support for sorting sequences based on multiple
keys, including locale-based comparisons and per-key directions.


===========
 Changelog
===========

4.1.2 (2018-10-10)
==================

- Fix regression introduced in 4.1.1 where two `_Smallest` objects are no
  longer considered to be equal.


4.1.1 (2018-10-05)
==================

- Handle sorting of broken objects more gracefully.
  (`#4 <https://github.com/zopefoundation/zope.sequencesort/pull/4>`_)


4.1.0 (2018-08-13)
==================

- Updated ``boostrap.py`` to version 2.2.

- Drop support for Python 2.6, 3.2 and 3.3.

- Add support for Python 3.4, 3.5, 3.6 and 3.7.

- The locale comparison functions, ``strcoll`` and ``strcoll_nocase``
  are always available, not only if the ``locale`` module had been
  imported before this module.

4.0.1 (2013-03-04)
==================

- Fix omitted tests under Py3k.

4.0.0 (2013-02-28)
==================

- Added ``setup.py docs`` alias (installs ``Sphinx`` and dependencies).

- Added ``setup.py dev`` alias (runs ``setup.py develop`` plus installs
  ``nose`` and ``coverage``).

- Dropped spurious ``test`` extra requirement on ``zope.testing``.

- 100% unit test coverage.

- Added support for PyPy, Python 3.2 / 3.2.

- Dropped support for Python 2.4 / 2.5.

3.4.0 (2007-10-03)
==================

- Initial release independent of the main Zope3 tree.


