Overview
========

Missing provides special objects used in some Zope internals like the ZCatalog.


Changelog
=========

4.1 (2018-10-05)
----------------

- Drop support for Python 3.4.

- Add support for Python 3.7.

4.0.1 (2017-08-25)
------------------

- Restore `Missing._Missing` module for pickle compatibility with the old
  C extension version. [https://github.com/zopefoundation/Missing/issues/3]

4.0 (2017-05-16)
----------------

- Add support for bytes and matrix multiplication.

- Remove the Python 2-only C extension.

3.2 (2017-04-26)
----------------

- Add support for Python 3.6, drop support for Python 3.3.

3.1 (2016-04-03)
----------------

- Add support for Python 3.4 and 3.5.

- Drop support for Python 2.6 and 3.2.

3.0 (2013-05-05)
----------------

- Added compatibility with Python 3.2, 3.3 and PyPy using the Python
  implementation.

- Added a Python reference implementation of the Missing class.

- Changed the type name of the Missing class to `Missing.Missing` to
  distinguish it from an instance of the type like `Missing.Value`.

2.13.1 (2010-06-16)
-------------------

- Added a ``__class__`` to Missing.Value objects.

2.13.0 (2010-03-30)
-------------------

- Released as separate package.


