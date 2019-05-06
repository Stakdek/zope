==========
 zope.tal
==========

.. image:: https://img.shields.io/pypi/v/zope.tal.svg
        :target: https://pypi.python.org/pypi/zope.tal/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/zope.tal.svg
        :target: https://pypi.org/project/zope.tal/
        :alt: Supported Python versions

.. image:: https://travis-ci.org/zopefoundation/zope.tal.svg?branch=master
        :target: https://travis-ci.org/zopefoundation/zope.tal

.. image:: https://coveralls.io/repos/github/zopefoundation/zope.tal/badge.svg?branch=master
        :target: https://coveralls.io/github/zopefoundation/zope.tal?branch=master

.. image:: https://readthedocs.org/projects/zopetal/badge/?version=latest
        :target: https://zopetal.readthedocs.io/en/latest/
        :alt: Documentation Status

The Zope3 Template Attribute Languate (TAL) specifies the custom namespace
and attributes which are used by the Zope Page Templates renderer to inject
dynamic markup into a page.  It also includes the Macro Expansion for TAL
(METAL) macro language used in page assembly.

The dynamic values themselves are specified using a companion language,
TALES (see the `zope.tales`_ package for more).

The reference documentation for the TAL language is available at https://pagetemplates.readthedocs.io/en/latest/tal.html

Detailed documentation for this implementation and its API is available at https://zopetal.readthedocs.io/


.. _`zope.tales` :  https://zopetales.readthedocs.io


=========
 Changes
=========

4.4 (2018-10-05)
================

- Add support for Python 3.7.

4.3.1 (2018-03-21)
==================

- Host documentation at https://zopetal.readthedocs.io

- Fix a ``NameError`` on Python 3 in talgettext.py affecting i18ndude.
  See https://github.com/zopefoundation/zope.tal/pull/11

4.3.0 (2017-08-08)
==================

- Drop support for Python 3.3.

- Add support for Python 3.6.

4.2.0 (2016-04-12)
==================

- Drop support for Python 2.6 and 3.2.

- Accept and ignore ``i18n:ignore`` and ``i18n:ignore-attributes`` attributes.
  For compatibility with other tools (such as ``i18ndude``).

- Add support for Python 3.5.

4.1.1 (2015-06-05)
==================

- Suppress deprecation under Python 3.4 for default ``convert_charrefs``
  argument (passed to ``HTMLParser``).  Also ensures that upcoming change
  to the default in Python 3.5 will not affect us.

- Add support for Python 3.2 and PyPy3.

4.1.0 (2014-12-19)
==================

.. note::

   Support for PyPy3 is pending release of a fix for:
   https://bitbucket.org/pypy/pypy/issue/1946

- Add support for Python 3.4.

- Add support for testing on Travis.


4.0.0 (2014-01-13)
==================

- Fix possible UnicodeDecodeError in warning when msgid already exists.


4.0.0a1 (2013-02-15)
====================

- Replace deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Add support for Python 3.3 and PyPy.

- Drop support for Python 2.4 and 2.5.

- Output attributes generate via ``tal:attributes`` and ``i18n:attributes``
  directives in alphabetical order.


3.6.1 (2012-03-09)
==================

- Avoid handling end tags within <script> tags in the HTML parser. This works
  around http://bugs.python.org/issue670664

- Fix documentation link in README.txt.

3.6.0 (2011-08-20)
==================

- Update `talinterpreter.FasterStringIO` to faster list-based implementation.

- Increase the default value of the `wrap` argument from 60 to 1023 characters,
  to avoid extra whitespace and line breaks.

- Fix printing of error messages for msgid conflict with non-ASCII texts.


3.5.2 (2009-10-31)
==================

- In ``talgettext.POEngine.translate``, print a warning if a msgid already
  exists in the domain with a different default.


3.5.1 (2009-03-08)
==================

- Update tests of "bad" entities for compatibility with the stricter
  HTMLParser module shipped with Python 2.6.x.


3.5.0 (2008-06-06)
==================

- Remove artificial addition of a trailing newline if the output doesn't end
  in one; this allows the template source to be the full specification of what
  should be included.
  (See https://bugs.launchpad.net/launchpad/+bug/218706.)


3.4.1 (2007-11-16)
==================

- Remove unnecessary ``dummyengine`` dependency on zope.i18n to
  simplify distribution.  The ``dummyengine.DummyTranslationDomain``
  class no longer implements
  ``zope.i18n.interfaces.ITranslationDomain`` as a result.  Installing
  zope.tal with easy_install or buildout no longer pulls in many
  unrelated distributions.

- Support running tests using ``setup.py test``.

- Stop pinning (no longer required) ``zope.traversing`` and
  ``zope.app.publisher`` versions in buildout.cfg.


3.4.0 (2007-10-03)
==================

- Update package meta-data.


3.4.0b1
=======

- Update dependency on ``zope.i18n`` to a verions requiring the correct
  version of ``zope.security``, avoiding a hidden dependency issue in
  ``zope.security``.

.. note::

   Changes before 3.4.0b1 where not tracked as an individual
   package and have been documented in the Zope 3 changelog.


