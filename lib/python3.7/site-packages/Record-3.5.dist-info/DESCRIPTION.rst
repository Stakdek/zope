Overview
========

Record provides special objects used in some Zope2 internals like ZRDB.

Records are used to provide compact storage for catalog query results.

They don't use instance dictionaries. Rather, they store they data in
a compact array internally. They use a record schema to map names to
positions within the array.

Changelog
=========

3.5 (2018-10-05)
----------------

- Add support for Python 3.7.

3.4 (2017-05-15)
----------------

- Add `__hash__` method to Record.

3.3 (2017-05-06)
----------------

- Set `__allow_access_to_unprotected_subobjects__` on the Record class.

- Remove the C extension.

3.2 (2017-04-26)
----------------

- Use `ExtensionClass.Base.__new__`.

- Add support for Python 3.6, drop support for Python 3.3.

3.1 (2016-04-03)
----------------

- Add support for Python 3.4 and 3.5.

- Drop support for Python 2.6 and 3.2.

3.0 (2013-05-04)
----------------

- Add support for Python 3.2, 3.3 and PyPy using the Python reference
  implementation.

- Add support for `__contains__`.

- Provide an Python reference implementation using `__slots__`.

- Rewrite tests as unit tests.

2.13.0 (2010-03-30)
-------------------

- Released as separate package.


