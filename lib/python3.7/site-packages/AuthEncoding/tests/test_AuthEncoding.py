# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002, 2015 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Test of AuthEncoding
"""

from AuthEncoding import AuthEncoding
from ..compat import b, u
import pytest


def testListSchemes():
    assert len(AuthEncoding.listSchemes()) > 0  # At least one must exist!


@pytest.mark.parametrize('schema_id', AuthEncoding.listSchemes())
@pytest.mark.parametrize('password', [u'good_pw', u'gööd_pw', b(u'gööd_pw')])
def testGoodPassword(schema_id, password):
    enc = AuthEncoding.pw_encrypt(password, schema_id)
    assert enc != password
    assert AuthEncoding.pw_validate(enc, password)
    assert AuthEncoding.pw_validate(u(enc), password)
    assert AuthEncoding.is_encrypted(enc)
    assert not AuthEncoding.is_encrypted(password)


@pytest.mark.parametrize('schema_id', AuthEncoding.listSchemes())
@pytest.mark.parametrize(
    'password', [u'OK_pa55w0rd \n', u'OK_pä55w0rd \n', b(u'OK_pä55w0rd \n')])
def testBadPassword(schema_id, password):
    enc = AuthEncoding.pw_encrypt(password, schema_id)
    assert enc != password
    assert not AuthEncoding.pw_validate(enc, u'xxx')
    assert not AuthEncoding.pw_validate(enc, b'xxx')
    assert not AuthEncoding.pw_validate(u(enc), u'xxx')
    assert not AuthEncoding.pw_validate(enc, enc)
    if schema_id != u'CRYPT':
        # crypt truncates passwords and would fail this test.
        assert not AuthEncoding.pw_validate(enc, password[:-1])
    assert not AuthEncoding.pw_validate(enc, password[1:])
    assert AuthEncoding.pw_validate(enc, password)


@pytest.mark.parametrize('schema_id', AuthEncoding.listSchemes())
def testShortPassword(schema_id):
    pw = u'1'
    enc = AuthEncoding.pw_encrypt(pw, schema_id)
    assert AuthEncoding.pw_validate(enc, pw)
    assert not AuthEncoding.pw_validate(enc, enc)
    assert not AuthEncoding.pw_validate(enc, u'xxx')


@pytest.mark.parametrize('schema_id', AuthEncoding.listSchemes())
def testLongPassword(schema_id):
    pw = u'Pw' * 2000
    enc = AuthEncoding.pw_encrypt(pw, schema_id)
    assert AuthEncoding.pw_validate(enc, pw)
    assert not AuthEncoding.pw_validate(enc, enc)
    assert not AuthEncoding.pw_validate(enc, u'xxx')
    if u'CRYPT' not in schema_id:
        # crypt and bcrypt truncates passwords and would fail these tests.
        assert not AuthEncoding.pw_validate(enc, pw[:-2])
        assert not AuthEncoding.pw_validate(enc, pw[2:])


@pytest.mark.parametrize('schema_id', AuthEncoding.listSchemes())
def testBlankPassword(schema_id):
    pw = u''
    enc = AuthEncoding.pw_encrypt(pw, schema_id)
    assert enc != pw
    assert AuthEncoding.pw_validate(enc, pw)
    assert not AuthEncoding.pw_validate(enc, enc)
    assert not AuthEncoding.pw_validate(enc, u'xxx')


def testUnencryptedPassword():
    # Sanity check
    pw = u'my-password'
    assert AuthEncoding.pw_validate(pw, pw)
    assert not AuthEncoding.pw_validate(pw, pw + u'asdf')


def testEncryptWithNotSupportedScheme():
    with pytest.raises(ValueError) as err:
        AuthEncoding.pw_encrypt(u'asdf', 'MD1')
    assert 'Not supported: MD1' == str(err.value)


def testEncryptAcceptsTextAndBinaryEncodingNames():
    assert (AuthEncoding.pw_encrypt(u'asdf', b'SHA') ==
            AuthEncoding.pw_encrypt(u'asdf', u'SHA'))


def testIsEncryptedAcceptsTextAndBinary():
    assert AuthEncoding.is_encrypted(b'{SHA}')
    assert AuthEncoding.is_encrypted(u'{SHA}')
    assert not AuthEncoding.is_encrypted(b'foo')
    assert not AuthEncoding.is_encrypted(u'foo')
