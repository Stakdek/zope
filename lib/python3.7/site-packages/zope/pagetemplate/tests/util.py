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
"""Utilities
"""
from __future__ import print_function
import os
import re
import sys
import unittest
import zope.pagetemplate.tests

class arg(object):
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, nn, aa):
        self.num, self.arg = nn, aa

    def __str__(self):
        return str(self.arg)

class argv(object):
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, argv=None):
        args = self.args = []
        argv = argv if argv is not None else sys.argv[1:]
        for aa in argv:
            args.append(arg(len(args) + 1, aa))

    context = property(lambda self: self)

class _Test(unittest.TestCase):

    def runTest(self): # pragma: no cover 2.7 compatibility
        return

_assertEqual = _Test().assertEqual
del _Test

def check_html(s1, s2):
    s1 = normalize_html(s1)
    s2 = normalize_html(s2)
    _assertEqual(s1, s2, "HTML Output Changed")

def check_xml(s1, s2):
    s1 = normalize_xml(s1)
    s2 = normalize_xml(s2)
    _assertEqual(s1, s2, 'XML Output Changed')

def normalize_html(s):
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"/>", ">", s)
    return s

def normalize_xml(s):
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"(?s)\s+<", "<", s)
    s = re.sub(r"(?s)>\s+", ">", s)
    return s




here = os.path.dirname(zope.pagetemplate.tests.__file__)
input_dir = os.path.join(here, 'input')
output_dir = os.path.join(here, 'output')

def read_input(filename):
    filename = os.path.join(input_dir, filename)
    with open(filename, 'r') as f:
        return f.read()

def read_output(filename):
    filename = os.path.join(output_dir, filename)
    with open(filename, 'r') as f:
        return f.read()
