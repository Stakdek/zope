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
""" GenericSetup product:  unit test utilities.
"""

import os
import shutil
import six
from tarfile import TarFile

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.users import UnrestrictedUser
from Testing.ZopeTestCase import ZopeTestCase
from zope.interface import implementer

from Products.GenericSetup.interfaces import IExportContext
from Products.GenericSetup.interfaces import IImportContext
from Products.GenericSetup.testing import DummyLogger


class DOMComparator:

    def _compareDOM(self, found_text, expected_text, debug=False):

        if six.PY3:
            if isinstance(found_text, bytes):
                found_text = found_text.decode('utf8')
            if isinstance(expected_text, bytes):
                expected_text = expected_text.decode('utf8')

        found_lines = [x.strip() for x in found_text.splitlines()]
        found_text = '\n'.join([i for i in found_lines if i])

        expected_text = '\n'.join([i for i in found_lines if i])

        from xml.dom.minidom import parseString
        found = parseString(found_text)
        expected = parseString(expected_text)
        fxml = found.toxml()
        exml = expected.toxml()

        if fxml != exml:

            if debug:
                zipped = zip(fxml, exml)
                diff = [(i, zipped[i][0], zipped[i][1])
                        for i in range(len(zipped))
                        if zipped[i][0] != zipped[i][1]
                        ]
                # Ugly, but it will do.
                print('Diff:')
                print(diff)
                print()

            print('Found:')
            print(fxml)
            print()
            print('Expected:')
            print(exml)
            print()

        self.assertEqual(found.toxml(), expected.toxml())


class BaseRegistryTests(ZopeTestCase, DOMComparator):

    def afterSetUp(self):
        self.root = self.app
        newSecurityManager(None, UnrestrictedUser('god', '', ['Manager'], ''))

    def _makeOne(self, *args, **kw):
        # Derived classes must implement _getTargetClass
        return self._getTargetClass()(*args, **kw)


def _clearTestDirectory(root_path):

    if os.path.exists(root_path):
        shutil.rmtree(root_path)


def _makeTestFile(filename, root_path, contents):

    if isinstance(contents, six.text_type):
        contents = contents.encode('utf-8')

    path, filename = os.path.split(filename)

    subdir = os.path.join(root_path, path)

    if not os.path.exists(subdir):
        os.makedirs(subdir)

    fqpath = os.path.join(subdir, filename)

    file = open(fqpath, 'wb')
    file.write(contents)
    file.close()
    return fqpath


class FilesystemTestBase(ZopeTestCase):

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def beforeTearDown(self):
        _clearTestDirectory(self._PROFILE_PATH)

    def _makeFile(self, filename, contents):
        return _makeTestFile(filename, self._PROFILE_PATH, contents)


class TarballTester(DOMComparator):

    def _verifyTarballContents(self, fileish, toc_list, when=None):

        fileish.seek(0)
        tarfile = TarFile.open('foo.tar.gz', fileobj=fileish, mode='r:gz')
        items = sorted(tarfile.getnames())
        toc_list.sort()

        self.assertEqual(len(items), len(toc_list))
        for i in range(len(items)):
            self.assertEqual(items[i].rstrip('/'), toc_list[i])

        if when is not None:
            for tarinfo in tarfile:
                self.assertFalse(tarinfo.mtime < when)

    def _verifyTarballEntry(self, fileish, entry_name, data):

        fileish.seek(0)
        tarfile = TarFile.open('foo.tar.gz', fileobj=fileish, mode='r:gz')
        extract = tarfile.extractfile(entry_name)
        found = extract.read()
        self.assertEqual(found, data)

    def _verifyTarballEntryXML(self, fileish, entry_name, data):

        fileish.seek(0)
        tarfile = TarFile.open('foo.tar.gz', fileobj=fileish, mode='r:gz')
        extract = tarfile.extractfile(entry_name)
        found = extract.read()
        self._compareDOM(found.decode('utf-8'), data)


@implementer(IExportContext)
class DummyExportContext:

    def __init__(self, site, tool=None):
        self._site = site
        self._tool = tool
        self._wrote = []
        self._notes = []

    def getSite(self):
        return self._site

    def getSetupTool(self):
        return self._tool

    def getLogger(self, name):
        return DummyLogger(name, self._notes)

    def writeDataFile(self, filename, text, content_type, subdir=None):
        if subdir is not None:
            filename = '%s/%s' % (subdir, filename)
        self._wrote.append((filename, text, content_type))


@implementer(IImportContext)
class DummyImportContext:

    def __init__(self, site, purge=True, encoding=None, tool=None):
        self._site = site
        self._tool = tool
        self._purge = purge
        self._encoding = encoding
        self._files = {}
        self._notes = []

    def getSite(self):
        return self._site

    def getSetupTool(self):
        return self._tool

    def getEncoding(self):
        return self._encoding

    def getLogger(self, name):
        return DummyLogger(name, self._notes)

    def readDataFile(self, filename, subdir=None):

        if subdir is not None:
            filename = '/'.join((subdir, filename))

        return self._files.get(filename)

    def shouldPurge(self):

        return self._purge


def dummy_handler(context):

    pass


# BBB: PAS tests use this
class SecurityRequestTest(ZopeTestCase):

    def setUp(self):
        ZopeTestCase.setUp(self)
        self.root = self.app
