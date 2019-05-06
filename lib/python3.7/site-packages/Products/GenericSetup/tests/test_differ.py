##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for differ module.
"""

import six
import unittest
from Testing.ZopeTestCase import ZopeTestCase

from DateTime.DateTime import DateTime
from OFS.Folder import Folder
from OFS.Image import File


class DummySite(Folder):

    pass


class Test_unidiff(unittest.TestCase):

    def test_unidiff_both_text(self):

        from Products.GenericSetup.differ import unidiff

        diff_lines = unidiff(ONE_FOUR, ZERO_FOUR)
        diff_text = b'\n'.join(diff_lines)
        self.assertEqual(diff_text, DIFF_TEXT)

    def test_unidiff_both_lines(self):

        from Products.GenericSetup.differ import unidiff

        diff_lines = unidiff(ONE_FOUR.splitlines(), ZERO_FOUR.splitlines())
        diff_text = b'\n'.join(diff_lines)
        self.assertEqual(diff_text, DIFF_TEXT)

    def test_unidiff_mixed(self):

        from Products.GenericSetup.differ import unidiff

        diff_lines = unidiff(ONE_FOUR, ZERO_FOUR.splitlines())
        diff_text = b'\n'.join(diff_lines)
        self.assertEqual(diff_text, DIFF_TEXT)

    def test_unidiff_ignore_blanks(self):

        from Products.GenericSetup.differ import unidiff

        double_spaced = ONE_FOUR.replace(b'\n', b'\n\n')
        diff_lines = unidiff(double_spaced, ZERO_FOUR.splitlines(),
                             ignore_blanks=True)

        diff_text = b'\n'.join(diff_lines)
        self.assertEqual(diff_text, DIFF_TEXT)


ZERO_FOUR = b"""\
zero
one
tree
four
"""

ONE_FOUR = b"""\
one
two
three
four
"""

DIFF_TEXT = b"""\
--- original
+++ modified
@@ -1,4 +1,4 @@
+zero
 one
-two
-three
+tree
 four\
"""


class ConfigDiffTests(ZopeTestCase):

    site = None
    tool = None

    def _getTargetClass(self):

        from Products.GenericSetup.differ import ConfigDiff
        return ConfigDiff

    def _makeOne(self, lhs, rhs, *args, **kw):

        return self._getTargetClass()(lhs, rhs, *args, **kw)

    def _makeSite(self):

        if self.site is not None:
            return

        site = self.site = DummySite('site').__of__(self.app)
        site._setObject('setup_tool', Folder('setup_tool'))
        self.tool = tool = site._getOb('setup_tool')

        tool._setObject('snapshots', Folder('snapshots'))

    def _makeContext(self, context_id):

        from Products.GenericSetup.context import SnapshotImportContext

        self._makeSite()

        if context_id not in self.tool.snapshots.objectIds():
            self.tool.snapshots._setObject(context_id, Folder(context_id))

        ctx = SnapshotImportContext(self.tool, context_id)

        return ctx.__of__(self.tool)

    def _makeDirectory(self, snapshot_id, subdir):

        self._makeSite()
        folder = self.tool.snapshots._getOb(snapshot_id)

        for element in subdir.split('/'):

            try:
                folder = folder._getOb(element)
            except AttributeError:
                folder._setObject(element, Folder(element))
                folder = folder._getOb(element)

        return folder

    def _makeFile(self, snapshot_id, filename, contents,
                  content_type='text/plain', mod_time=None, subdir=None):

        self._makeSite()
        snapshots = self.tool.snapshots
        snapshot = snapshots._getOb(snapshot_id)

        if subdir is not None:
            folder = self._makeDirectory(snapshot_id, subdir)
        else:
            folder = snapshot

        file = File(filename, '', contents, content_type)
        folder._setObject(filename, file)

        if mod_time is not None:
            folder._faux_mod_time = file._faux_mod_time = mod_time

        return folder._getOb(filename)

    def test_compare_empties(self):

        lhs = self._makeContext('lhs')
        rhs = self._makeContext('rhs')

        cd = self._makeOne(lhs, rhs)

        diffs = cd.compare()

        self.assertEqual(diffs, b'')

    def test_compare_identical(self):

        lhs = self._makeContext('lhs')
        rhs = self._makeContext('rhs')

        self._makeFile('lhs', 'test.txt', b'ABCDEF')
        self._makeFile('lhs', 'again.txt', b'GHIJKL', subdir='sub')
        self._makeFile('rhs', 'test.txt', b'ABCDEF')
        self._makeFile('rhs', 'again.txt', b'GHIJKL', subdir='sub')

        cd = self._makeOne(lhs, rhs)

        diffs = cd.compare()

        self.assertEqual(diffs, b'')

    def test_compare_changed_file(self):

        BEFORE = DateTime('2004-01-01T00:00:00Z')
        AFTER = DateTime('2004-02-29T23:59:59Z')

        lhs = self._makeContext('lhs')
        rhs = self._makeContext('rhs')

        self._makeFile('lhs', 'test.txt', b'ABCDEF\nWXYZ', mod_time=BEFORE)
        self._makeFile('lhs', 'again.txt', b'GHIJKL', subdir='sub')
        self._makeFile('rhs', 'test.txt', b'ABCDEF\nQRST', mod_time=AFTER)
        self._makeFile('rhs', 'again.txt', b'GHIJKL', subdir='sub')

        cd = self._makeOne(lhs, rhs)

        diffs = cd.compare()

        self.assertEqual(diffs, TEST_TXT_DIFFS % (
            _DateTime_as_bytes(BEFORE),
            _DateTime_as_bytes(AFTER),
        ))

    def test_compare_changed_file_ignore_blanks(self):

        BEFORE = DateTime('2004-01-01T00:00:00Z')
        AFTER = DateTime('2004-02-29T23:59:59Z')

        lhs = self._makeContext('lhs')
        rhs = self._makeContext('rhs')

        self._makeFile('lhs', 'test.txt', b'ABCDEF\nWXYZ', mod_time=BEFORE)
        self._makeFile('rhs', 'test.txt', b'ABCDEF\n\n\nWXYZ', mod_time=AFTER)

        cd = self._makeOne(lhs, rhs, ignore_blanks=True)

        diffs = cd.compare()

        self.assertEqual(diffs, b'')

    def test_compare_changed_file_explicit_skip(self):

        BEFORE = DateTime('2004-01-01T00:00:00Z')
        AFTER = DateTime('2004-02-29T23:59:59Z')

        lhs = self._makeContext('lhs')
        rhs = self._makeContext('rhs')

        self._makeFile('lhs', 'test.txt', b'ABCDEF\nWXYZ',
                       subdir='skipme', mod_time=BEFORE)
        self._makeFile('lhs', 'again.txt', b'GHIJKL', subdir='sub')
        self._makeFile('rhs', 'test.txt', b'ABCDEF\nQRST',
                       subdir='skipme', mod_time=AFTER)
        self._makeFile('rhs', 'again.txt', b'GHIJKL', subdir='sub')

        cd = self._makeOne(lhs, rhs, skip=['skipme'])

        diffs = cd.compare()

        self.assertEqual(diffs, b'')

    def test_compare_changed_file_implicit_skip(self):

        BEFORE = DateTime('2004-01-01T00:00:00Z')
        AFTER = DateTime('2004-02-29T23:59:59Z')

        lhs = self._makeContext('lhs')
        rhs = self._makeContext('rhs')

        self._makeFile('lhs', 'test.txt', b'ABCDEF\nWXYZ',
                       subdir='CVS', mod_time=BEFORE)
        self._makeFile('lhs', 'again.txt', b'GHIJKL',
                       subdir='.svn', mod_time=BEFORE)

        self._makeFile('rhs', 'test.txt', b'ABCDEF\nQRST',
                       subdir='CVS', mod_time=AFTER)
        self._makeFile('rhs', 'again.txt', b'MNOPQR',
                       subdir='.svn', mod_time=AFTER)

        cd = self._makeOne(lhs, rhs)

        diffs = cd.compare()

        self.assertEqual(diffs, b'')

    def test_compare_added_file_no_missing_as_empty(self):

        lhs = self._makeContext('lhs')
        rhs = self._makeContext('rhs')

        self._makeFile('lhs', 'test.txt', b'ABCDEF\nWXYZ')
        self._makeDirectory('lhs', subdir='sub')
        self._makeFile('rhs', 'test.txt', b'ABCDEF\nWXYZ')
        self._makeFile('rhs', 'again.txt', b'GHIJKL', subdir='sub')

        cd = self._makeOne(lhs, rhs)

        diffs = cd.compare()

        self.assertEqual(diffs, ADDED_FILE_DIFFS_NO_MAE)

    def test_compare_added_file_missing_as_empty(self):

        AFTER = DateTime('2004-02-29T23:59:59Z')
        lhs = self._makeContext('lhs')
        rhs = self._makeContext('rhs')

        self._makeFile('lhs', 'test.txt', b'ABCDEF\nWXYZ')
        self._makeDirectory('lhs', subdir='sub')
        self._makeFile('rhs', 'test.txt', b'ABCDEF\nWXYZ')
        self._makeFile('rhs', 'again.txt', b'GHIJKL',
                       subdir='sub', mod_time=AFTER)

        cd = self._makeOne(lhs, rhs, missing_as_empty=True)

        diffs = cd.compare()

        self.assertEqual(
            diffs, ADDED_FILE_DIFFS_MAE % _DateTime_as_bytes(AFTER))

    def test_compare_removed_file_no_missing_as_empty(self):

        lhs = self._makeContext('lhs')
        rhs = self._makeContext('rhs')

        self._makeFile('lhs', 'test.txt', b'ABCDEF\nWXYZ')
        self._makeFile('lhs', 'again.txt', b'GHIJKL', subdir='sub')
        self._makeFile('rhs', 'test.txt', b'ABCDEF\nWXYZ')
        self._makeDirectory('rhs', subdir='sub')

        cd = self._makeOne(lhs, rhs)

        diffs = cd.compare()

        self.assertEqual(diffs, REMOVED_FILE_DIFFS_NO_MAE)

    def test_compare_removed_file_missing_as_empty(self):

        BEFORE = DateTime('2004-01-01T00:00:00Z')
        lhs = self._makeContext('lhs')
        rhs = self._makeContext('rhs')

        self._makeFile('lhs', 'test.txt', b'ABCDEF\nWXYZ')
        self._makeFile('lhs', 'again.txt', b'GHIJKL',
                       subdir='sub', mod_time=BEFORE)
        self._makeFile('rhs', 'test.txt', b'ABCDEF\nWXYZ')
        self._makeDirectory('rhs', subdir='sub')

        cd = self._makeOne(lhs, rhs, missing_as_empty=True)

        diffs = cd.compare()

        self.assertEqual(
            diffs, REMOVED_FILE_DIFFS_MAE % _DateTime_as_bytes(BEFORE))


TEST_TXT_DIFFS = b"""\
Index: test.txt
===================================================================
--- test.txt\t%s
+++ test.txt\t%s
@@ -1,2 +1,2 @@
 ABCDEF
-WXYZ
+QRST\
"""

ADDED_FILE_DIFFS_NO_MAE = b"""\
** File sub/again.txt added
"""

ADDED_FILE_DIFFS_MAE = b"""\
Index: sub/again.txt
===================================================================
--- sub/again.txt
+++ sub/again.txt\t%s
@@ -0,0 +1 @@
+GHIJKL\
"""

REMOVED_FILE_DIFFS_NO_MAE = b"""\
** File sub/again.txt removed
"""

REMOVED_FILE_DIFFS_MAE = b"""\
Index: sub/again.txt
===================================================================
--- sub/again.txt\t%s
+++ sub/again.txt
@@ -1 +0,0 @@
-GHIJKL\
"""


def _DateTime_as_bytes(dt):
    return six.text_type(dt).encode('utf-8')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_unidiff),
        unittest.makeSuite(ConfigDiffTests),
    ))
