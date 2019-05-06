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

import binascii
import six
from binascii import b2a_base64, a2b_base64
from hashlib import sha1 as sha
from hashlib import sha256
from os import getpid
import time
from .compat import long, b, u


# Use the system PRNG if possible
import random
try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False


def _reseed():
    if not using_sysrandom:
        # This is ugly, and a hack, but it makes things better than
        # the alternative of predictability. This re-seeds the PRNG
        # using a value that is hard for an attacker to predict, every
        # time a random string is required. This may change the
        # properties of the chosen random sequence slightly, but this
        # is better than absolute predictability.
        random.seed(sha256(
            "%s%s%s" % (random.getstate(), time.time(), getpid())
        ).digest())


def _choice(c):
    _reseed()
    return random.choice(c)


def _randrange(r):
    _reseed()
    return random.randrange(r)


def constant_time_compare(val1, val2):
    """
    Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(six.iterbytes(val1), six.iterbytes(val2)):
        result |= x ^ y
    return result == 0


class PasswordEncryptionScheme:  # An Interface

    def encrypt(pw):
        """
        Encrypt the provided plain text password.
        """

    def validate(reference, attempt):
        """
        Validate the provided password string.  Reference is the
        correct password, which may be encrypted; attempt is clear text
        password attempt.
        """


_schemes = []


def registerScheme(id, s):
    '''
    Registers an LDAP password encoding scheme.
    '''
    _schemes.append((id, u'{%s}' % id, s))


def listSchemes():
    return [id for id, prefix, scheme in _schemes]


class SSHADigestScheme:
    '''
    SSHA is a modification of the SHA digest scheme with a salt
    starting at byte 20 of the base64-encoded string.
    '''
    # Source: http://developer.netscape.com/docs/technote/ldap/pass_sha.html

    def generate_salt(self):
        # Salt can be any length, but not more than about 37 characters
        # because of limitations of the binascii module.
        # 7 is what Netscape's example used and should be enough.
        # All 256 characters are available.
        salt = b''
        for n in range(7):
            salt += six.int2byte(_randrange(256))
        return salt

    def encrypt(self, pw):
        return self._encrypt_with_salt(pw, self.generate_salt())

    def validate(self, reference, attempt):
        try:
            ref = a2b_base64(reference)
        except binascii.Error:
            # Not valid base64.
            return 0
        salt = ref[20:]
        compare = self._encrypt_with_salt(attempt, salt)
        return constant_time_compare(compare, reference)

    def _encrypt_with_salt(self, pw, salt):
        pw = b(pw)
        return b2a_base64(sha(pw + salt).digest() + salt)[:-1]


registerScheme(u'SSHA', SSHADigestScheme())


class SHADigestScheme:

    def encrypt(self, pw):
        return self._encrypt(pw)

    def validate(self, reference, attempt):
        compare = self._encrypt(attempt)
        return constant_time_compare(compare, reference)

    def _encrypt(self, pw):
        pw = b(pw)
        return b2a_base64(sha(pw).digest())[:-1]


registerScheme(u'SHA', SHADigestScheme())


class SHA256DigestScheme:

    def encrypt(self, pw):
        return b(sha256(b(pw)).hexdigest())

    def validate(self, reference, attempt):
        a = self.encrypt(attempt)
        return constant_time_compare(a, reference)


registerScheme(u'SHA256', SHA256DigestScheme())


# Bcrypt support may not have been requested at installation time
# - installed via the 'bcrypt' extra
try:
    import bcrypt
except ImportError:
    bcrypt = None


class BCRYPTHashingScheme:
    """A BCRYPT hashing scheme."""

    @staticmethod
    def _ensure_bytes(pw, encoding='utf-8'):
        """Ensures the given password `pw` is returned as bytes."""
        if isinstance(pw, six.text_type):
            pw = pw.encode(encoding)
        return pw

    def encrypt(self, pw):
        return bcrypt.hashpw(self._ensure_bytes(pw), bcrypt.gensalt())

    def validate(self, reference, attempt):
        try:
            return bcrypt.checkpw(self._ensure_bytes(attempt), reference)
        except ValueError:
            # Usually due to an invalid salt
            return False


if bcrypt is not None:
    registerScheme(u'BCRYPT', BCRYPTHashingScheme())


# Bogosity on various platforms due to ITAR restrictions
try:
    from crypt import crypt
except ImportError:
    crypt = None

if crypt is not None:

    class CryptDigestScheme:

        def generate_salt(self):
            choices = (u"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                       u"abcdefghijklmnopqrstuvwxyz"
                       u"0123456789./")
            return _choice(choices) + _choice(choices)

        def encrypt(self, pw):
            return b(crypt(self._recode_password(pw), self.generate_salt()))

        def validate(self, reference, attempt):
            attempt = self._recode_password(attempt)
            a = b(crypt(attempt, reference[:2].decode('ascii')))
            return constant_time_compare(a, reference)

        def _recode_password(self, pw):
            # crypt always requires `str` which has a different meaning among
            # the Python versions:
            if six.PY3:
                return u(pw)
            return b(pw)

    registerScheme(u'CRYPT', CryptDigestScheme())


class MySQLDigestScheme:

    def encrypt(self, pw):
        pw = u(pw)
        nr = long(1345345333)
        add = 7
        nr2 = long(0x12345671)
        for i in pw:
            if i == ' ' or i == '\t':
                continue
            nr ^= (((nr & 63) + add) * ord(i)) + (nr << 8)
            nr2 += (nr2 << 8) ^ nr
            add += ord(i)
        r0 = nr & ((long(1) << 31) - long(1))
        r1 = nr2 & ((long(1) << 31) - long(1))
        return (u"%08lx%08lx" % (r0, r1)).encode('ascii')

    def validate(self, reference, attempt):
        a = self.encrypt(attempt)
        return constant_time_compare(a, reference)


registerScheme(u'MYSQL', MySQLDigestScheme())


def pw_validate(reference, attempt):
    """Validate the provided password string, which uses LDAP-style encoding
    notation.  Reference is the correct password, attempt is clear text
    password attempt."""
    reference = b(reference)
    for id, prefix, scheme in _schemes:
        lp = len(prefix)
        if reference[:lp] == b(prefix):
            return scheme.validate(reference[lp:], attempt)
    # Assume cleartext.
    return constant_time_compare(reference, b(attempt))


def is_encrypted(pw):
    pw = b(pw)
    for id, prefix, scheme in _schemes:
        lp = len(prefix)
        if pw[:lp] == b(prefix):
            return 1
    return 0


def pw_encrypt(pw, encoding=u'SSHA'):
    """Encrypt the provided plain text password using the encoding if provided
    and return it in an LDAP-style representation."""
    encoding = u(encoding)
    for id, prefix, scheme in _schemes:
        if encoding == id:
            return b(prefix) + scheme.encrypt(pw)
    raise ValueError('Not supported: %s' % encoding)


pw_encode = pw_encrypt  # backward compatibility
