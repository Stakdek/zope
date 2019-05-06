Overview
========

AuthEncoding is a framework for handling LDAP style password hashes.

It is used in Zope but does not depend on any other Zope package.

Changelog
=========

4.1 (2018-10-30)
----------------

- Add support for Python 3.6, 3.7 and PyPy3.

- Drop support for Python 2.6, 3.3 and 3.4.

- Add ``BCRYPTHashingScheme``, optionally available if package is
  installed with the `bcrypt` extra.

- Accept bytes as input to ``AuthEncoding.is_encrypted``.


4.0.0 (2015-09-30)
------------------

- Supporting Python 3.3 up to 3.5 and PyPy2.

- Added ``SHA256DigestScheme``.


3.0.0 (2015-09-28)
------------------

- Extracted from ``AccessControl 3.0.11``


