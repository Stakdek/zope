##############################################################################
#
# Copyright (c) 2004-2008 Zope Foundation and Contributors.
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
"""Layer definitions
"""
import unittest


class UnitTests(object):
    """A layer for gathering all unit tests."""


class EmptyLayer(object):
    """An empty layer to start spreading out subprocesses."""

    __bases__ = ()
    __module__ = ''


def EmptySuite():
    suite = unittest.TestSuite()
    suite.layer = EmptyLayer()
    return suite
