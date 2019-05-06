##############################################################################
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
"""Tests for the testing framework.
"""
import doctest
import sys
import re
import unittest
from zope.testing import renormalizing
from zope.testing.test_renormalizing import Exception2To3

def print_(*args):
    sys.stdout.write(' '.join(map(str, args))+'\n')

def setUp(test):
    test.globs['print_'] = print_


def test_suite():
    suite = unittest.TestSuite((
        doctest.DocFileSuite(
            'module.txt',
            # Python 3.3 changed exception messaging:
            #   https://bugs.launchpad.net/zope.testing/+bug/1055720
            # and then Python 3.6 introduced ImportError subclasses
            checker=renormalizing.RENormalizing([
                (re.compile('ModuleNotFoundError:'), 'ImportError:'),
                (re.compile(
                    "No module named '?zope.testing.unlikelymodulename'?"),
                 'No module named unlikelymodulename'),
                (re.compile("No module named '?fake'?"),
                 'No module named fake')])),
        doctest.DocFileSuite('loggingsupport.txt', setUp=setUp),
        doctest.DocFileSuite('renormalizing.txt', setUp=setUp),
        doctest.DocFileSuite('setupstack.txt', setUp=setUp),
        doctest.DocFileSuite(
            'wait.txt', setUp=setUp,
            checker=renormalizing.RENormalizing([
                # For Python 3.4.
                (re.compile('zope.testing.wait.TimeOutWaitingFor: '),
                 'TimeOutWaitingFor: '),
                # For Python 3.5
                (re.compile('zope.testing.wait.Wait.TimeOutWaitingFor: '),
                 'TimeOutWaitingFor: '),
                ])
            ),
        ))

    if sys.version_info[:2] >= (2, 7):
        suite.addTests(doctest.DocFileSuite('doctestcase.txt'))
    if sys.version_info[0] < 3:
        suite.addTests(doctest.DocTestSuite('zope.testing.server'))
        suite.addTests(doctest.DocFileSuite('formparser.txt'))
    suite.addTest(
        unittest.makeSuite(Exception2To3))
    return suite
