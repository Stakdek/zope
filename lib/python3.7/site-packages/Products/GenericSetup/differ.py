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
""" Diff utilities for comparing configurations.
"""

import difflib
import re
import six

from AccessControl.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo

from Products.GenericSetup.interfaces import SKIPPED_FILES

BLANKS_REGEX = re.compile(b'^\\s*$')


def unidiff(a, b, filename_a=b'original', timestamp_a=b'',
            filename_b=b'modified', timestamp_b=b'', ignore_blanks=False):
    r"""Compare two sequences of lines; generate the resulting delta.

    Each sequence must contain individual single-line strings
    ending with newlines. Such sequences can be obtained from the
    `readlines()` method of file-like objects.  The delta
    generated also consists of newline-terminated strings, ready
    to be printed as-is via the writeline() method of a file-like
    object.

    Note that the last line of a file may *not* have a newline;
    this is reported in the same way that GNU diff reports this.
    *This method only supports UNIX line ending conventions.*

        filename_a and filename_b are used to generate the header,
        allowing other tools to determine what 'files' were used
        to generate this output.

        timestamp_a and timestamp_b, when supplied, are expected
        to be last-modified timestamps to be inserted in the
        header, as floating point values since the epoch.

    """
    if isinstance(a, six.binary_type):
        a = a.splitlines()

    if isinstance(b, six.binary_type):
        b = b.splitlines()

    if isinstance(filename_a, six.text_type):
        filename_a = filename_a.encode('utf-8')

    if isinstance(filename_b, six.text_type):
        filename_b = filename_b.encode('utf-8')

    if not isinstance(timestamp_a, six.binary_type):
        timestamp_a = six.text_type(timestamp_a).encode('utf-8')

    if not isinstance(timestamp_b, six.binary_type):
        timestamp_b = six.text_type(timestamp_b).encode('utf-8')

    if ignore_blanks:
        a = [x for x in a if not BLANKS_REGEX.match(x)]
        b = [x for x in b if not BLANKS_REGEX.match(x)]

    if six.PY2:
        return difflib.unified_diff(a, b, filename_a, filename_b, timestamp_a,
                                    timestamp_b, lineterm=b"")
    else:
        return difflib.diff_bytes(difflib.unified_diff, a, b, filename_a,
                                  filename_b, timestamp_a, timestamp_b,
                                  lineterm=b"")


class ConfigDiff:

    security = ClassSecurityInfo()

    def __init__(self, lhs, rhs, missing_as_empty=False, ignore_blanks=False,
                 skip=SKIPPED_FILES):
        self._lhs = lhs
        self._rhs = rhs
        self._missing_as_empty = missing_as_empty
        self._ignore_blanks = ignore_blanks
        self._skip = skip

    @security.private
    def compareDirectories(self, subdir=None):

        lhs_files = self._lhs.listDirectory(subdir, self._skip)
        if lhs_files is None:
            lhs_files = []

        rhs_files = self._rhs.listDirectory(subdir, self._skip)
        if rhs_files is None:
            rhs_files = []

        added = [f for f in rhs_files if f not in lhs_files]
        removed = [f for f in lhs_files if f not in rhs_files]
        all_files = lhs_files + added
        all_files.sort()

        result = []

        for filename in all_files:

            if subdir is None:
                pathname = filename
            else:
                pathname = '%s/%s' % (subdir, filename)

            if filename not in added:
                isDirectory = self._lhs.isDirectory(pathname)
            else:
                isDirectory = self._rhs.isDirectory(pathname)

            if not self._missing_as_empty and filename in removed:

                if isDirectory:
                    result.append(b'** Directory %s removed\n' %
                                  pathname.encode('utf-8'))
                    result.extend(self.compareDirectories(pathname))
                else:
                    result.append(b'** File %s removed\n' %
                                  pathname.encode('utf-8'))

            elif not self._missing_as_empty and filename in added:

                if isDirectory:
                    result.append(b'** Directory %s added\n' %
                                  pathname.encode('utf-8'))
                    result.extend(self.compareDirectories(pathname))
                else:
                    result.append(b'** File %s added\n' %
                                  pathname.encode('utf-8'))

            elif isDirectory:

                result.extend(self.compareDirectories(pathname))

                if (filename not in added + removed and
                        not self._rhs.isDirectory(pathname)):

                    result.append(b'** Directory %s replaced with a file of '
                                  b'the same name\n' % pathname)

                    if self._missing_as_empty:
                        result.extend(self.compareFiles(filename, subdir))
            else:
                if (filename not in added + removed and
                        self._rhs.isDirectory(pathname)):

                    result.append(b'** File %s replaced with a directory of '
                                  b'the same name\n' % pathname)

                    if self._missing_as_empty:
                        result.extend(self.compareFiles(filename, subdir))

                    result.extend(self.compareDirectories(pathname))
                else:
                    result.extend(self.compareFiles(filename, subdir))

        return result

    @security.private
    def compareFiles(self, filename, subdir=None):

        if subdir is None:
            path = filename
        else:
            path = '%s/%s' % (subdir, filename)

        lhs_file = self._lhs.readDataFile(filename, subdir)
        lhs_time = self._lhs.getLastModified(path)

        if lhs_file is None:
            assert self._missing_as_empty
            lhs_file = b''
            lhs_time = b''

        rhs_file = self._rhs.readDataFile(filename, subdir)
        rhs_time = self._rhs.getLastModified(path)

        if rhs_file is None:
            assert self._missing_as_empty
            rhs_file = b''
            rhs_time = b''

        if lhs_file == rhs_file:
            diff_lines = []
        else:
            diff_lines = unidiff(lhs_file, rhs_file, filename_a=path,
                                 timestamp_a=lhs_time, filename_b=path,
                                 timestamp_b=rhs_time,
                                 ignore_blanks=self._ignore_blanks)
            diff_lines = list(diff_lines)  # generator

        if len(diff_lines) == 0:  # No *real* difference found
            return []

        diff_lines.insert(0, b'Index: %s' % path.encode('utf-8'))
        diff_lines.insert(1, b'=' * 67)

        return diff_lines

    @security.private
    def compare(self):
        return b'\n'.join(self.compareDirectories())


InitializeClass(ConfigDiff)
