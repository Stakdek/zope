Overview
========

zExceptions contains common exceptions and helper functions related to
exceptions as used in Zope.

Changelog
=========

4.1 (2018-10-05)
----------------

- Add support for Python 3.7.


4.0 (2018-01-27)
----------------

- Drop support for string exceptions.

3.6.1 (2017-05-17)
------------------

- Increase Python 3 compatibility

3.6 (2017-02-05)
----------------

- Add realm as an argument to unauthorized exceptions, its presence
  causing a `WWW-Authenticate` header to be emitted.

- Set `location` header during `__init__` of redirect exceptions.

3.5 (2017-02-05)
----------------

- Drop support for Python 3.3, add support for Python 3.6.

- Use `str(self)` as detail if it is not set.

- Add a `setHeader` method to add a response header to an HTTPException.

- `upgradeException` now also supports finding an HTTPException class
  with the same name as a non-HTTPException class.

3.4 (2016-09-08)
----------------

- Use `HTTPException.body_template` when title and detail are set.

- Add new title and detail attributes to HTTPException.

3.3 (2016-08-06)
----------------

- Add exception classes for all HTTP status codes.

3.2 (2016-07-22)
----------------

- Implement basic subset of Response features in HTTPException class.

3.1 (2016-07-22)
----------------

- Mark exceptions with appropriate zope.publisher interfaces.

- Add a new common base class `zExceptions.HTTPException` to all exceptions.

3.0 (2016-04-03)
----------------

- Add compatibility with PyPy and Python 3.

- Arguments to the Unauthorized exception are assumed to be utf8-encoded
  if they are bytes.

2.13.0 (2010-06-05)
-------------------

- Released as separate package.


