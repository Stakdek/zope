##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""MIME Content-Type parsing helper functions.

This supports parsing `RFC 1341`_ Content-Type values, including
quoted-string values as defined in `RFC 822`_.

.. _RFC 1341: https://tools.ietf.org/html/rfc1341
.. _RFC 822: https://tools.ietf.org/html/rfc822

"""
__docformat__ = "reStructuredText"

import re


# TODO: This still needs to support comments in structured fields as
# specified in RFC 2822.


def parse(string):
    """
    Parse the given string as a MIME type.

    This uses :func:`parseOrdered` and can raise the same
    exceptions it does.

    :return: A tuple ``(major, minor, params)`` where ``major``
      and ``minor`` are the two parts of the type, and ``params``
      is a dictionary containing any parameters by name.
    :param str string: The string to parse.
    """
    major, minor, params = parseOrdered(string)
    d = {}
    for (name, value) in params:
        d[name] = value
    return major, minor, d

def parseOrdered(string):
    """
    Parse the given string as a MIME type.

    :return: A tuple ``(major, minor, params)``  where ``major``
      and ``minor`` are the two parts of the type, and ``params`` is a
      sequence of the parameters in order.
    :raises ValueError: If the *string* is malformed.
    :param str string: The string to parse.
    """
    if ";" in string:
        type, params = string.split(";", 1)
        params = _parse_params(params)
    else:
        type = string
        params = []
    if "/" not in type:
        raise ValueError("content type missing major/minor parts: %r" % type)
    type = type.strip()

    major, minor = type.lower().split("/", 1)
    return _check_token(major.strip()), _check_token(minor.strip()), params

def _parse_params(string):
    result = []
    string = string.strip()
    while string:
        if not "=" in string:
            raise ValueError("parameter values are not optional")
        name, rest = string.split("=", 1)
        name = _check_token(name.strip().lower())
        rest = rest.strip()

        # rest is: value *[";" parameter]

        if rest[:1] == '"':
            # quoted-string, defined in RFC 822.
            m = _quoted_string_match(rest)
            if m is None:
                raise ValueError("invalid quoted-string in %r" % rest)
            value = m.group()
            rest = rest[m.end():].strip()
            #import pdb; pdb.set_trace()
            if rest[:1] not in ("", ";"):
                raise ValueError(
                    "invalid token following quoted-string: %r" % rest)
            rest = rest[1:]
            value = _unescape(value)

        elif ";" in rest:
            value, rest = rest.split(";")
            value = _check_token(value.strip())

        else:
            value = _check_token(rest.strip())
            rest = ""

        result.append((name, value))
        string = rest.strip()
    return result


_quoted_string_match = re.compile('"(?:\\\\.|[^"\n\r\\\\])*"', re.DOTALL).match
_token_match = re.compile("[^][ \t\n\r()<>@,;:\"/?=\\\\]+$").match

def _check_token(string):
    if _token_match(string) is None:
        raise ValueError('"%s" is not a valid token' % string)
    return string


def _unescape(string):
    assert string[0] == '"'
    assert string[-1] == '"'
    string = string[1:-1]
    if "\\" in string:
        string = re.sub(r"\\(.)", r"\1", string)
    return string


def join(spec):
    """
    Given a three-part tuple as produced by :func:`parse` or :func:`parseOrdered`,
    return the string representation.

    :returns: The string representation. For example, given ``('text',
      'plain', [('encoding','utf-8')])``, this will produce ``'text/plain;encoding=utf-8'``.
    :rtype: str
    """
    (major, minor, params) = spec
    pstr = ""
    try:
        params.items
    except AttributeError:
        pass
    else:
        params = params.items()
        # ensure a predictable order:
        params = sorted(params)
    for name, value in params:
        pstr += ";%s=%s" % (name, _escape(value))
    return "%s/%s%s" % (major, minor, pstr)

def _escape(string):
    try:
        return _check_token(string)
    except ValueError:
        # '\\' must be first
        for c in '\\"\n\r':
            string = string.replace(c, "\\" + c)
        return '"%s"' % string
