##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""General test support.
"""
import re
from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    # Python 3 bytes adds the "b".
    (re.compile("b('.*?')"),
     r"\1"),
    (re.compile('b(".*?")'),
     r"\1"),
    # Python 3 changed the set representation.
    (re.compile("set\(\[(.*)\]\)"),
     r"{\1}"),
    # Python 3 renames builtins.
    (re.compile("__builtin__"),
     r"builtins"),
    # Python 3 adds module name to exceptions.
    (re.compile("zope.schema.interfaces.SchemaNotProvided"),
     r"SchemaNotProvided"),
    ])

class VerifyResults(object):
    """Mix-in for test classes with helpers for checking string data."""

    def verifyResult(self, result, check_list, inorder=False):
        start = 0
        for check in check_list:
            pos = result.find(check, start)
            self.assertTrue(pos >= 0,
                         "%r not found in %r" % (check, result[start:]))
            if inorder:
                start = pos + len(check)

    def verifyResultMissing(self, result, check_list):
        for check in check_list:
            self.assertTrue(result.find(check) < 0,
                         "%r unexpectedly found in %r" % (check, result))

def patternExists(pattern, source, flags=0):
    return re.search(pattern, source, flags) is not None

def validationErrorExists(field, error_msg, source):
    regex = re.compile(r'%s.*?name="form.(\w+)(?:\.[\w\.]+)?"' % (error_msg,),
                       re.DOTALL)
    # compile it first because Python 2.3 doesn't allow flags in findall
    return field in regex.findall(source)

def missingInputErrorExists(field, source):
    return validationErrorExists(field, 'Required input is missing.', source)
