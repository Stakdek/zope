# encoding: utf-8
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
""" Unit tests for import / export contexts.
"""
from __future__ import absolute_import
import unittest
from Testing.ZopeTestCase import ZopeTestCase

import logging
import os
from six import BytesIO
from string import digits
from string import printable
import six
import tempfile
import time
from tarfile import TarFile
from tarfile import TarInfo

from DateTime.DateTime import DateTime
from OFS.Folder import Folder
from OFS.Image import File

from .common import FilesystemTestBase
from .common import TarballTester
from .conformance import ConformsToISetupContext
from .conformance import ConformsToIImportContext
from .conformance import ConformsToIExportContext
from .conformance import ConformsToIChunkableExportContext
from .conformance import ConformsToIChunkableImportContext


printable_bytes = printable.encode('utf-8')
digits_bytes = digits.encode('utf-8')


class DummySite(Folder):

    pass


class DummyTool(Folder):

    pass


class DummyPdataStreamIterator:

    pass


class DirectoryImportContextTests(FilesystemTestBase, ConformsToISetupContext,
                                  ConformsToIImportContext,
                                  ConformsToIChunkableImportContext):

    _PROFILE_PATH = '/tmp/ICTTexts'

    def _getTargetClass(self):

        from Products.GenericSetup.context import DirectoryImportContext
        return DirectoryImportContext

    def test_getLogger(self):

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)
        self.assertEqual(len(ctx.listNotes()), 0)

        logger = ctx.getLogger('foo')
        logger.info('bar')

        self.assertEqual(len(ctx.listNotes()), 1)
        level, component, message = ctx.listNotes()[0]
        self.assertEqual(level, logging.INFO)
        self.assertEqual(component, 'foo')
        self.assertEqual(message, 'bar')

        ctx.clearNotes()
        self.assertEqual(len(ctx.listNotes()), 0)

    def test_readDataFile_nonesuch(self):

        FILENAME = 'nonesuch.txt'

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.readDataFile(FILENAME), None)

    def test_readDataFile_simple(self):

        FILENAME = 'simple.txt'
        self._makeFile(FILENAME, printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.readDataFile(FILENAME), printable_bytes)

    def test_readDataFile_subdir(self):

        FILENAME = 'subdir/nested.txt'
        self._makeFile(FILENAME, printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.readDataFile(FILENAME), printable_bytes)

    def test_getLastModified_nonesuch(self):
        FILENAME = 'nonesuch.txt'
        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.getLastModified(FILENAME), None)

    def test_getLastModified_simple(self):

        FILENAME = 'simple.txt'
        fqpath = self._makeFile(FILENAME, printable_bytes)
        WHEN = os.path.getmtime(fqpath)
        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        lm = ctx.getLastModified(FILENAME)
        self.assertTrue(isinstance(lm, DateTime))
        self.assertEqual(lm, DateTime(WHEN))

    def test_getLastModified_subdir(self):

        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'
        PATH = os.path.join(SUBDIR, FILENAME)
        fqpath = self._makeFile(PATH, printable_bytes)
        WHEN = os.path.getmtime(fqpath)
        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        lm = ctx.getLastModified(PATH)
        self.assertTrue(isinstance(lm, DateTime))
        self.assertEqual(lm, DateTime(WHEN))

    def test_getLastModified_directory(self):

        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'
        PATH = os.path.join(SUBDIR, FILENAME)
        fqpath = self._makeFile(PATH, printable_bytes)
        path, file = os.path.split(fqpath)
        WHEN = os.path.getmtime(path)
        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        lm = ctx.getLastModified(SUBDIR)
        self.assertTrue(isinstance(lm, DateTime))
        self.assertEqual(lm, DateTime(WHEN))

    def test_isDirectory_nonesuch(self):

        FILENAME = 'nonesuch.txt'

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.isDirectory(FILENAME), None)

    def test_isDirectory_simple(self):

        FILENAME = 'simple.txt'
        self._makeFile(FILENAME, printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.isDirectory(FILENAME), False)

    def test_isDirectory_nested(self):

        SUBDIR = 'subdir'
        FILENAME = os.path.join(SUBDIR, 'nested.txt')
        self._makeFile(FILENAME, printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.isDirectory(FILENAME), False)

    def test_isDirectory_directory(self):

        SUBDIR = 'subdir'
        FILENAME = os.path.join(SUBDIR, 'nested.txt')
        self._makeFile(FILENAME, printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.isDirectory(SUBDIR), True)

    def test_listDirectory_nonesuch(self):

        FILENAME = 'nonesuch.txt'

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.listDirectory(FILENAME), None)

    def test_listDirectory_root(self):

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        FILENAME = 'simple.txt'
        self._makeFile(FILENAME, printable_bytes)

        self.assertEqual(len(ctx.listDirectory(None)), 1)
        self.assertTrue(FILENAME in ctx.listDirectory(None))

    def test_listDirectory_simple(self):

        FILENAME = 'simple.txt'
        self._makeFile(FILENAME, printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.listDirectory(FILENAME), None)

    def test_listDirectory_nested(self):

        SUBDIR = 'subdir'
        FILENAME = os.path.join(SUBDIR, 'nested.txt')
        self._makeFile(FILENAME, printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        self.assertEqual(ctx.listDirectory(FILENAME), None)

    def test_listDirectory_single(self):

        SUBDIR = 'subdir'
        FILENAME = os.path.join(SUBDIR, 'nested.txt')
        self._makeFile(FILENAME, printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        names = ctx.listDirectory(SUBDIR)
        self.assertEqual(len(names), 1)
        self.assertTrue('nested.txt' in names)

    def test_listDirectory_multiple(self):

        SUBDIR = 'subdir'
        FILENAME = os.path.join(SUBDIR, 'nested.txt')
        self._makeFile(FILENAME, printable_bytes)
        self._makeFile(os.path.join(SUBDIR, 'another.txt'), b'ABC')

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        names = ctx.listDirectory(SUBDIR)
        self.assertEqual(len(names), 2)
        self.assertTrue('nested.txt' in names)
        self.assertTrue('another.txt' in names)

    def test_listDirectory_skip_implicit(self):

        SUBDIR = 'subdir'
        FILENAME = os.path.join(SUBDIR, 'nested.txt')
        self._makeFile(FILENAME, printable_bytes)
        self._makeFile(os.path.join(SUBDIR, 'another.txt'), b'ABC')
        self._makeFile(os.path.join(SUBDIR, 'another.txt~'), b'123')
        self._makeFile(os.path.join(SUBDIR, 'CVS/skip.txt'), b'DEF')
        self._makeFile(os.path.join(SUBDIR, '.svn/skip.txt'), b'GHI')

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        names = ctx.listDirectory(SUBDIR)
        self.assertEqual(len(names), 2)
        self.assertTrue('nested.txt' in names)
        self.assertTrue('another.txt' in names)
        self.assertFalse('another.txt~' in names)
        self.assertFalse('CVS' in names)
        self.assertFalse('.svn' in names)

    def test_listDirectory_skip_explicit(self):

        SUBDIR = 'subdir'
        FILENAME = os.path.join(SUBDIR, 'nested.txt')
        self._makeFile(FILENAME, printable_bytes)
        self._makeFile(os.path.join(SUBDIR, 'another.txt'), b'ABC')
        self._makeFile(os.path.join(SUBDIR, 'another.bak'), b'123')
        self._makeFile(os.path.join(SUBDIR, 'CVS/skip.txt'), b'DEF')
        self._makeFile(os.path.join(SUBDIR, '.svn/skip.txt'), b'GHI')

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        names = ctx.listDirectory(SUBDIR, skip=('nested.txt',),
                                  skip_suffixes=('.bak',))
        self.assertEqual(len(names), 3)
        self.assertFalse('nested.txt' in names)
        self.assertFalse('nested.bak' in names)
        self.assertTrue('another.txt' in names)
        self.assertTrue('CVS' in names)
        self.assertTrue('.svn' in names)


class DirectoryExportContextTests(FilesystemTestBase, ConformsToISetupContext,
                                  ConformsToIExportContext,
                                  ConformsToIChunkableExportContext):

    _PROFILE_PATH = '/tmp/ECTTexts'

    def _getTargetClass(self):

        from Products.GenericSetup.context import DirectoryExportContext
        return DirectoryExportContext

    def test_getLogger(self):

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)
        self.assertEqual(len(ctx.listNotes()), 0)

        logger = ctx.getLogger('foo')
        logger.info('bar')

        self.assertEqual(len(ctx.listNotes()), 1)
        level, component, message = ctx.listNotes()[0]
        self.assertEqual(level, logging.INFO)
        self.assertEqual(component, 'foo')
        self.assertEqual(message, 'bar')

        ctx.clearNotes()
        self.assertEqual(len(ctx.listNotes()), 0)

    def test_writeDataFile_simple(self):

        FILENAME = 'simple.txt'
        fqname = self._makeFile(FILENAME, printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        ctx.writeDataFile(FILENAME, digits_bytes, 'text/plain')

        with open(fqname, 'rb') as fp:
            self.assertEqual(fp.read(), digits_bytes)

    def test_writeDataFile_unicode(self):

        text = u'Kein Weltraum links vom Gerät'
        FILENAME = 'unicode.txt'
        fqname = self._makeFile(FILENAME, printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        ctx.writeDataFile(FILENAME, text, 'text/plain')

        with open(fqname, 'rb') as fp:
            self.assertEqual(fp.read(), text.encode('UTF-8'))

    def test_writeDataFile_new_subdir(self):

        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        fqname = os.path.join(self._PROFILE_PATH, SUBDIR, FILENAME)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        ctx.writeDataFile(FILENAME, digits_bytes, 'text/plain', SUBDIR)

        with open(fqname, 'rb') as fp:
            self.assertEqual(fp.read(), digits_bytes)

    def test_writeDataFile_overwrite(self):

        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        fqname = self._makeFile(os.path.join(SUBDIR, FILENAME),
                                printable_bytes)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        ctx.writeDataFile(FILENAME, digits_bytes, 'text/plain', SUBDIR)

        with open(fqname, 'rb') as fp:
            self.assertEqual(fp.read(), digits_bytes)

    def test_writeDataFile_existing_subdir(self):

        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        self._makeFile(os.path.join(SUBDIR, 'another.txt'), printable_bytes)
        fqname = os.path.join(self._PROFILE_PATH, SUBDIR, FILENAME)

        site = DummySite('site').__of__(self.app)
        ctx = self._makeOne(site, self._PROFILE_PATH)

        ctx.writeDataFile(FILENAME, digits_bytes, 'text/plain', SUBDIR)

        with open(fqname, 'rb') as fp:
            self.assertEqual(fp.read(), digits_bytes)


class TarballImportContextTests(ZopeTestCase, ConformsToISetupContext,
                                ConformsToIImportContext):

    def _getTargetClass(self):

        from Products.GenericSetup.context import TarballImportContext
        return TarballImportContext

    def _makeOne(self, file_dict={}, mod_time=None, *args, **kw):

        archive_stream = BytesIO()
        archive = TarFile.open('test.tar.gz', 'w:gz', archive_stream)

        def _addOneMember(path, data, modtime):
            stream = BytesIO(v)
            info = TarInfo(k)
            info.size = len(v)
            info.mtime = modtime
            archive.addfile(info, stream)

        def _addMember(filename, data, modtime):
            from tarfile import DIRTYPE
            parents = filename.split('/')[:-1]
            while parents:
                path = '/'.join(parents) + '/'
                if path not in archive.getnames():
                    info = TarInfo(path)
                    info.type = DIRTYPE
                    info.mtime = modtime
                    archive.addfile(info)
                parents.pop()
            _addOneMember(filename, data, modtime)

        file_items = file_dict.items() or [(
            'dummy', b'')]  # empty archive barfs

        if mod_time is None:
            mod_time = time.time()

        for k, v in file_items:
            if isinstance(v, str):
                v = v.encode('utf-8')
            _addMember(k, v, mod_time)

        archive.close()
        bits = archive_stream.getvalue()

        site = DummySite('site').__of__(self.app)
        site._setObject('setup_tool', Folder('setup_tool'))
        tool = site._getOb('setup_tool')

        ctx = self._getTargetClass()(tool, bits, *args, **kw)

        return site, tool, ctx.__of__(tool)

    def test_getLogger(self):

        site, tool, ctx = self._makeOne()
        self.assertEqual(len(ctx.listNotes()), 0)

        logger = ctx.getLogger('foo')
        logger.info('bar')

        self.assertEqual(len(ctx.listNotes()), 1)
        level, component, message = ctx.listNotes()[0]
        self.assertEqual(level, logging.INFO)
        self.assertEqual(component, 'foo')
        self.assertEqual(message, 'bar')

        ctx.clearNotes()
        self.assertEqual(len(ctx.listNotes()), 0)

    def test_ctorparms(self):

        ENCODING = 'latin-1'
        site, tool, ctx = self._makeOne(encoding=ENCODING, should_purge=True
                                        )

        self.assertEqual(ctx.getEncoding(), ENCODING)
        self.assertEqual(ctx.shouldPurge(), True)

    def test_empty(self):

        site, tool, ctx = self._makeOne()

        self.assertEqual(ctx.getSite(), site)
        self.assertEqual(ctx.getEncoding(), None)
        self.assertEqual(ctx.shouldPurge(), False)

        # These methods are all specified to return 'None' for non-existing
        # paths / entities
        self.assertEqual(ctx.isDirectory('nonesuch/path'), None)
        self.assertEqual(ctx.listDirectory('nonesuch/path'), None)

    def test_readDataFile_nonesuch(self):

        FILENAME = 'nonesuch.txt'

        site, tool, ctx = self._makeOne()

        self.assertEqual(ctx.readDataFile(FILENAME), None)
        self.assertEqual(ctx.readDataFile(FILENAME, 'subdir'), None)

    def test_readDataFile_simple(self):

        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne({FILENAME: printable_bytes})

        self.assertEqual(ctx.readDataFile(FILENAME), printable_bytes)

    def test_readDataFile_subdir(self):

        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'

        site, tool, ctx = self._makeOne({'%s/%s' % (SUBDIR, FILENAME):
                                         printable_bytes})

        self.assertEqual(ctx.readDataFile(FILENAME, SUBDIR), printable_bytes)

    def test_getLastModified_nonesuch(self):
        FILENAME = 'nonesuch.txt'
        ctx = self._makeOne()[2]

        self.assertEqual(ctx.getLastModified(FILENAME), None)

    def test_getLastModified_simple(self):

        FILENAME = 'simple.txt'
        WHEN = 999999999.0
        ctx = self._makeOne({FILENAME: printable_bytes}, mod_time=WHEN)[2]

        lm = ctx.getLastModified(FILENAME)
        self.assertTrue(isinstance(lm, DateTime))
        self.assertEqual(lm, DateTime(WHEN))

    def test_getLastModified_subdir(self):

        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'
        PATH = '%s/%s' % (SUBDIR, FILENAME)
        WHEN = 999999999.0
        ctx = self._makeOne({PATH: printable_bytes}, mod_time=WHEN)[2]

        lm = ctx.getLastModified(PATH)
        self.assertTrue(isinstance(lm, DateTime))
        self.assertEqual(lm, DateTime(WHEN))

    def test_getLastModified_directory(self):

        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'
        PATH = '%s/%s' % (SUBDIR, FILENAME)
        WHEN = 999999999.0
        ctx = self._makeOne({PATH: printable_bytes}, mod_time=WHEN)[2]

        lm = ctx.getLastModified(SUBDIR)
        self.assertTrue(isinstance(lm, DateTime))
        self.assertEqual(lm, DateTime(WHEN))

    def test_isDirectory_nonesuch(self):

        FILENAME = 'nonesuch.txt'

        site, tool, ctx = self._makeOne()

        self.assertEqual(ctx.isDirectory(FILENAME), None)

    def test_isDirectory_simple(self):

        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne({FILENAME: printable_bytes})

        self.assertEqual(ctx.isDirectory(FILENAME), False)

    def test_isDirectory_nested(self):

        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        PATH = '%s/%s' % (SUBDIR, FILENAME)

        site, tool, ctx = self._makeOne({PATH: printable_bytes})

        self.assertEqual(ctx.isDirectory(PATH), False)

    def test_isDirectory_subdir(self):

        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        PATH = '%s/%s' % (SUBDIR, FILENAME)

        site, tool, ctx = self._makeOne({PATH: printable_bytes})

        self.assertEqual(ctx.isDirectory(SUBDIR), True)

    def test_listDirectory_nonesuch(self):

        SUBDIR = 'nonesuch/path'

        site, tool, ctx = self._makeOne()

        self.assertEqual(ctx.listDirectory(SUBDIR), None)

    def test_listDirectory_root(self):

        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne({FILENAME: printable_bytes})

        self.assertEqual(len(ctx.listDirectory(None)), 1)
        self.assertTrue(FILENAME in ctx.listDirectory(None))

    def test_listDirectory_simple(self):

        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne({FILENAME: printable_bytes})

        self.assertEqual(ctx.listDirectory(FILENAME), None)

    def test_listDirectory_nested(self):

        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        PATH = '%s/%s' % (SUBDIR, FILENAME)

        site, tool, ctx = self._makeOne({PATH: printable_bytes})

        self.assertEqual(ctx.listDirectory(PATH), None)

    def test_listDirectory_single(self):

        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        PATH = '%s/%s' % (SUBDIR, FILENAME)

        site, tool, ctx = self._makeOne({PATH: printable_bytes})

        names = ctx.listDirectory(SUBDIR)
        self.assertEqual(len(names), 1)
        self.assertTrue(FILENAME in names)

    def test_listDirectory_multiple(self):

        from string import ascii_uppercase

        SUBDIR = 'subdir'
        FILENAME1 = 'nested.txt'
        PATH1 = '%s/%s' % (SUBDIR, FILENAME1)
        FILENAME2 = 'another.txt'
        PATH2 = '%s/%s' % (SUBDIR, FILENAME2)

        site, tool, ctx = self._makeOne({PATH1: printable_bytes,
                                         PATH2: ascii_uppercase})

        names = ctx.listDirectory(SUBDIR)
        self.assertEqual(len(names), 2)
        self.assertTrue(FILENAME1 in names)
        self.assertTrue(FILENAME2 in names)

    def test_listDirectory_skip(self):

        from string import ascii_uppercase

        SUBDIR = 'subdir'
        FILENAME1 = 'nested.txt'
        PATH1 = '%s/%s' % (SUBDIR, FILENAME1)
        FILENAME2 = 'another.txt'
        PATH2 = '%s/%s' % (SUBDIR, FILENAME2)
        FILENAME3 = 'another.bak'
        PATH3 = '%s/%s' % (SUBDIR, FILENAME3)

        site, tool, ctx = self._makeOne({PATH1: printable_bytes,
                                         PATH2: ascii_uppercase,
                                         PATH3: 'xyz'})

        names = ctx.listDirectory(SUBDIR, skip=(FILENAME1,),
                                  skip_suffixes=('.bak',))
        self.assertEqual(len(names), 1)
        self.assertFalse(FILENAME1 in names)
        self.assertTrue(FILENAME2 in names)
        self.assertFalse(FILENAME3 in names)


class TarballExportContextTests(ZopeTestCase, ConformsToISetupContext,
                                ConformsToIExportContext, TarballTester):

    def _getTargetClass(self):

        from Products.GenericSetup.context import TarballExportContext
        return TarballExportContext

    def test_getLogger(self):

        site = DummySite('site').__of__(self.app)
        ctx = self._getTargetClass()(site)

        self.assertEqual(len(ctx.listNotes()), 0)

        logger = ctx.getLogger('foo')
        logger.info('bar')

        self.assertEqual(len(ctx.listNotes()), 1)
        level, component, message = ctx.listNotes()[0]
        self.assertEqual(level, logging.INFO)
        self.assertEqual(component, 'foo')
        self.assertEqual(message, 'bar')

        ctx.clearNotes()
        self.assertEqual(len(ctx.listNotes()), 0)

    def test_writeDataFile_simple(self):

        now = int(time.time())

        site = DummySite('site').__of__(self.app)
        ctx = self._getTargetClass()(site)

        ctx.writeDataFile('foo.txt', printable_bytes, 'text/plain')

        fileish = BytesIO(ctx.getArchive())

        self._verifyTarballContents(fileish, ['foo.txt'], now)
        self._verifyTarballEntry(fileish, 'foo.txt', printable_bytes)

    def test_writeDataFile_umlauts(self):

        text = u'Kein Weltraum links vom Gerät'
        now = int(time.time())

        site = DummySite('site').__of__(self.app)
        ctx = self._getTargetClass()(site)

        ctx.writeDataFile('foo.txt', text, 'text/plain')

        fileish = BytesIO(ctx.getArchive())

        self._verifyTarballContents(fileish, ['foo.txt'], now)
        self._verifyTarballEntry(fileish, 'foo.txt', text.encode('UTF-8'))

    def test_writeDataFile_multiple(self):

        site = DummySite('site').__of__(self.app)
        ctx = self._getTargetClass()(site)

        ctx.writeDataFile('foo.txt', printable_bytes, 'text/plain')
        ctx.writeDataFile('bar.txt', digits_bytes, 'text/plain')

        fileish = BytesIO(ctx.getArchive())

        self._verifyTarballContents(fileish, ['foo.txt', 'bar.txt'])
        self._verifyTarballEntry(fileish, 'foo.txt', printable_bytes)
        self._verifyTarballEntry(fileish, 'bar.txt', digits_bytes)

    def test_writeDataFile_PdataStreamIterator(self):

        site = DummySite('site').__of__(self.app)
        ctx = self._getTargetClass()(site)

        fp = tempfile.TemporaryFile()
        fp.write(printable_bytes)
        fp.seek(0)
        pData = DummyPdataStreamIterator()
        pData.file = fp
        pData.size = len(printable_bytes)
        ctx.writeDataFile('foo.txt', pData, 'text/plain')

        fileish = BytesIO(ctx.getArchive())

        self._verifyTarballContents(fileish, ['foo.txt'])
        self._verifyTarballEntry(fileish, 'foo.txt', printable_bytes)

        fp.close()  # Prevent unclosed file warning

    def test_writeDataFile_subdir(self):

        site = DummySite('site').__of__(self.app)
        ctx = self._getTargetClass()(site)

        ctx.writeDataFile('foo.txt', printable_bytes, 'text/plain')
        ctx.writeDataFile('bar/baz.txt', digits_bytes, 'text/plain')

        fileish = BytesIO(ctx.getArchive())

        self._verifyTarballContents(fileish,
                                    ['foo.txt', 'bar', 'bar/baz.txt'])
        self._verifyTarballEntry(fileish, 'foo.txt', printable_bytes)
        self._verifyTarballEntry(fileish, 'bar/baz.txt', digits_bytes)


class SnapshotExportContextTests(ZopeTestCase, ConformsToISetupContext,
                                 ConformsToIExportContext):

    def _getTargetClass(self):

        from Products.GenericSetup.context import SnapshotExportContext
        return SnapshotExportContext

    def _makeOne(self, *args, **kw):

        return self._getTargetClass()(*args, **kw)

    def test_getLogger(self):

        site = DummySite('site').__of__(self.app)
        site.setup_tool = DummyTool('setup_tool')
        tool = site.setup_tool
        ctx = self._makeOne(tool, 'simple')

        self.assertEqual(len(ctx.listNotes()), 0)

        logger = ctx.getLogger('foo')
        logger.info('bar')

        self.assertEqual(len(ctx.listNotes()), 1)
        level, component, message = ctx.listNotes()[0]
        self.assertEqual(level, logging.INFO)
        self.assertEqual(component, 'foo')
        self.assertEqual(message, 'bar')

        ctx.clearNotes()
        self.assertEqual(len(ctx.listNotes()), 0)

    def test_writeDataFile_simple_image(self):

        from OFS.Image import Image
        FILENAME = 'simple.txt'
        CONTENT_TYPE = 'image/png'
        png_filename = os.path.join(os.path.split(__file__)[0], 'simple.png')
        png_file = open(png_filename, 'rb')
        png_data = png_file.read()
        png_file.close()

        site = DummySite('site').__of__(self.app)
        site.setup_tool = DummyTool('setup_tool')
        tool = site.setup_tool
        ctx = self._makeOne(tool, 'simple')

        ctx.writeDataFile(FILENAME, png_data, CONTENT_TYPE)

        snapshot = tool.snapshots._getOb('simple')

        self.assertEqual(len(snapshot.objectIds()), 1)
        self.assertTrue(FILENAME in snapshot.objectIds())

        fileobj = snapshot._getOb(FILENAME)

        self.assertEqual(fileobj.getId(), FILENAME)
        self.assertEqual(fileobj.meta_type, Image.meta_type)
        self.assertEqual(fileobj.getContentType(), CONTENT_TYPE)
        self.assertEqual(fileobj.data, png_data)

    def test_writeDataFile_simple_plain_text(self):

        FILENAME = 'simple.txt'
        CONTENT_TYPE = 'text/plain'

        site = DummySite('site').__of__(self.app)
        site.setup_tool = DummyTool('setup_tool')
        tool = site.setup_tool
        ctx = self._makeOne(tool, 'simple')

        ctx.writeDataFile(FILENAME, digits_bytes, CONTENT_TYPE)

        snapshot = tool.snapshots._getOb('simple')

        self.assertEqual(len(snapshot.objectIds()), 1)
        self.assertTrue(FILENAME in snapshot.objectIds())

        fileobj = snapshot._getOb(FILENAME)

        self.assertEqual(fileobj.getId(), FILENAME)
        self.assertEqual(fileobj.meta_type, File.meta_type)
        self.assertEqual(fileobj.getContentType(), CONTENT_TYPE)
        self.assertEqual(fileobj.data, digits_bytes)

    def test_writeDataFile_simple_plain_text_unicode(self):
        FILENAME = 'simple.txt'
        CONTENT_TYPE = 'text/plain'
        CONTENT = u'Unicode, with non-ASCII: %s.' % six.unichr(150)

        site = DummySite('site').__of__(self.app)
        site.setup_tool = DummyTool('setup_tool')
        tool = site.setup_tool
        ctx = self._makeOne(tool, 'simple', 'latin_1')
        ctx.writeDataFile(FILENAME, CONTENT, CONTENT_TYPE)

        snapshot = tool.snapshots._getOb('simple')

        self.assertEqual(len(snapshot.objectIds()), 1)
        self.assertTrue(FILENAME in snapshot.objectIds())

        fileobj = snapshot._getOb(FILENAME)

        self.assertEqual(fileobj.getId(), FILENAME)
        self.assertEqual(fileobj.meta_type, File.meta_type)
        self.assertEqual(fileobj.getContentType(), CONTENT_TYPE)
        self.assertEqual(fileobj.data, CONTENT.encode(ctx._encoding))

    def test_writeDataFile_simple_xml(self):

        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        FILENAME = 'simple.xml'
        CONTENT_TYPE = 'text/xml'
        _XML = """<?xml version="1.0"?><simple />"""

        site = DummySite('site').__of__(self.app)
        site.setup_tool = DummyTool('setup_tool')
        tool = site.setup_tool
        ctx = self._makeOne(tool, 'simple')

        ctx.writeDataFile(FILENAME, _XML, CONTENT_TYPE)

        snapshot = tool.snapshots._getOb('simple')

        self.assertEqual(len(snapshot.objectIds()), 1)
        self.assertTrue(FILENAME in snapshot.objectIds())

        template = snapshot._getOb(FILENAME)

        self.assertEqual(template.getId(), FILENAME)
        self.assertEqual(template.meta_type, ZopePageTemplate.meta_type)
        self.assertEqual(template.read(), _XML)
        self.assertFalse(template.html())

    def test_writeDataFile_subdir_dtml(self):

        from OFS.DTMLDocument import DTMLDocument
        FILENAME = 'simple.dtml'
        CONTENT_TYPE = 'text/html'
        _HTML = """<html><body><h1>HTML</h1></body></html>"""

        site = DummySite('site').__of__(self.app)
        site.setup_tool = DummyTool('setup_tool')
        tool = site.setup_tool
        ctx = self._makeOne(tool, 'simple')

        ctx.writeDataFile(FILENAME, _HTML, CONTENT_TYPE, 'sub1')

        snapshot = tool.snapshots._getOb('simple')
        sub1 = snapshot._getOb('sub1')

        self.assertEqual(len(sub1.objectIds()), 1)
        self.assertTrue(FILENAME in sub1.objectIds())

        template = sub1._getOb(FILENAME)

        self.assertEqual(template.getId(), FILENAME)
        self.assertEqual(template.meta_type, DTMLDocument.meta_type)
        self.assertEqual(template.read(), _HTML)

        ctx.writeDataFile('sub1/%s2' % FILENAME, _HTML, CONTENT_TYPE)
        self.assertEqual(len(sub1.objectIds()), 2)

    def test_writeDataFile_nested_subdirs_html(self):

        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        FILENAME = 'simple.html'
        CONTENT_TYPE = 'text/html'
        _HTML = """<html><body><h1>HTML</h1></body></html>"""

        site = DummySite('site').__of__(self.app)
        site.setup_tool = DummyTool('setup_tool')
        tool = site.setup_tool
        ctx = self._makeOne(tool, 'simple')

        ctx.writeDataFile(FILENAME, _HTML, CONTENT_TYPE, 'sub1/sub2')

        snapshot = tool.snapshots._getOb('simple')
        sub1 = snapshot._getOb('sub1')
        sub2 = sub1._getOb('sub2')

        self.assertEqual(len(sub2.objectIds()), 1)
        self.assertTrue(FILENAME in sub2.objectIds())

        template = sub2._getOb(FILENAME)

        self.assertEqual(template.getId(), FILENAME)
        self.assertEqual(template.meta_type, ZopePageTemplate.meta_type)
        self.assertEqual(template.read(), _HTML)
        self.assertTrue(template.html())

    def test_writeDataFile_multiple(self):

        site = DummySite('site').__of__(self.app)
        site.setup_tool = DummyTool('setup_tool')
        tool = site.setup_tool
        ctx = self._makeOne(tool, 'multiple')

        ctx.writeDataFile('foo.txt', printable_bytes, 'text/plain')
        ctx.writeDataFile('bar.txt', digits_bytes, 'text/plain')

        snapshot = tool.snapshots._getOb('multiple')

        self.assertEqual(len(snapshot.objectIds()), 2)

        for id in ['foo.txt', 'bar.txt']:
            self.assertTrue(id in snapshot.objectIds())


class SnapshotImportContextTests(ZopeTestCase, ConformsToISetupContext,
                                 ConformsToIImportContext):

    def _getTargetClass(self):

        from Products.GenericSetup.context import SnapshotImportContext
        return SnapshotImportContext

    def _makeOne(self, context_id, *args, **kw):

        site = DummySite('site').__of__(self.app)
        site._setObject('setup_tool', Folder('setup_tool'))
        tool = site._getOb('setup_tool')

        tool._setObject('snapshots', Folder('snapshots'))
        tool.snapshots._setObject(context_id, Folder(context_id))

        ctx = self._getTargetClass()(tool, context_id, *args, **kw)

        return site, tool, ctx.__of__(tool)

    def _makeFile(self, tool, snapshot_id, filename, contents,
                  content_type='text/plain', mod_time=None, subdir=None):

        snapshots = tool._getOb('snapshots')
        folder = snapshots._getOb(snapshot_id)

        if subdir is not None:

            for element in subdir.split('/'):

                try:
                    folder = folder._getOb(element)
                except AttributeError:
                    folder._setObject(element, Folder(element))
                    folder = folder._getOb(element)

        file = File(filename, '', contents, content_type)
        folder._setObject(filename, file)

        if mod_time is not None:
            mod_time = DateTime(mod_time).timeTime()
            folder._faux_mod_time = file._faux_mod_time = mod_time

        return folder._getOb(filename)

    def test_getLogger(self):

        SNAPSHOT_ID = 'note'
        site, tool, ctx = self._makeOne(SNAPSHOT_ID)

        self.assertEqual(len(ctx.listNotes()), 0)

        logger = ctx.getLogger('foo')
        logger.info('bar')

        self.assertEqual(len(ctx.listNotes()), 1)
        level, component, message = ctx.listNotes()[0]
        self.assertEqual(level, logging.INFO)
        self.assertEqual(component, 'foo')
        self.assertEqual(message, 'bar')

        ctx.clearNotes()
        self.assertEqual(len(ctx.listNotes()), 0)

    def test_ctorparms(self):

        SNAPSHOT_ID = 'ctorparms'
        ENCODING = 'latin-1'
        site, tool, ctx = self._makeOne(SNAPSHOT_ID, encoding=ENCODING,
                                        should_purge=True)

        self.assertEqual(ctx.getEncoding(), ENCODING)
        self.assertEqual(ctx.shouldPurge(), True)

    def test_empty(self):

        SNAPSHOT_ID = 'empty'
        site, tool, ctx = self._makeOne(SNAPSHOT_ID)

        self.assertEqual(ctx.getSite(), site)
        self.assertEqual(ctx.getEncoding(), None)
        self.assertEqual(ctx.shouldPurge(), False)

        # These methods are all specified to return 'None' for non-existing
        # paths / entities
        self.assertEqual(ctx.isDirectory('nonesuch/path'), None)
        self.assertEqual(ctx.listDirectory('nonesuch/path'), None)

    def test_readDataFile_nonesuch(self):

        SNAPSHOT_ID = 'readDataFile_nonesuch'
        FILENAME = 'nonesuch.txt'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)

        self.assertEqual(ctx.readDataFile(FILENAME), None)
        self.assertEqual(ctx.readDataFile(FILENAME, 'subdir'), None)

    def test_readDataFile_simple(self):

        SNAPSHOT_ID = 'readDataFile_simple'
        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes)

        self.assertEqual(ctx.readDataFile(FILENAME), printable_bytes)

    def test_readDataFile_Pdata(self):

        from OFS.Image import Pdata

        SNAPSHOT_ID = 'readDataFile_Pdata'
        FILENAME = 'pdata.txt'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, Pdata(printable_bytes))

        self.assertEqual(ctx.readDataFile(FILENAME), printable_bytes)

    def test_readDataFile_subdir(self):

        SNAPSHOT_ID = 'readDataFile_subdir'
        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes,
                       subdir=SUBDIR)

        self.assertEqual(ctx.readDataFile(FILENAME, SUBDIR), printable_bytes)
        self.assertEqual(ctx.readDataFile('%s/%s' % (SUBDIR, FILENAME)),
                         printable_bytes)

    def test_getLastModified_nonesuch(self):
        FILENAME = 'nonesuch.txt'
        SNAPSHOT_ID = 'getLastModified_nonesuch'
        ctx = self._makeOne(SNAPSHOT_ID)[2]

        self.assertEqual(ctx.getLastModified(FILENAME), None)

    def test_getLastModified_simple(self):

        FILENAME = 'simple.txt'
        WHEN = 999999999.0
        SNAPSHOT_ID = 'getLastModified_simple'
        tool, ctx = self._makeOne(SNAPSHOT_ID)[1:]
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes,
                       mod_time=WHEN)

        lm = ctx.getLastModified(FILENAME)
        self.assertTrue(isinstance(lm, DateTime))
        self.assertEqual(lm, DateTime(WHEN))

    def test_getLastModified_subdir(self):

        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'
        PATH = '%s/%s' % (SUBDIR, FILENAME)
        WHEN = 999999999.0
        SNAPSHOT_ID = 'getLastModified_subdir'
        tool, ctx = self._makeOne(SNAPSHOT_ID)[1:]
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes,
                       mod_time=WHEN, subdir=SUBDIR)

        lm = ctx.getLastModified(PATH)
        self.assertTrue(isinstance(lm, DateTime))
        self.assertEqual(lm, DateTime(WHEN))

    def test_getLastModified_directory(self):

        FILENAME = 'subdir.txt'
        SUBDIR = 'subdir'
        WHEN = 999999999.0
        SNAPSHOT_ID = 'getLastModified_directory'
        tool, ctx = self._makeOne(SNAPSHOT_ID)[1:]
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes,
                       mod_time=WHEN, subdir=SUBDIR)

        lm = ctx.getLastModified(SUBDIR)
        self.assertTrue(isinstance(lm, DateTime))
        self.assertEqual(lm, DateTime(WHEN))

    def test_isDirectory_nonesuch(self):

        SNAPSHOT_ID = 'isDirectory_nonesuch'
        FILENAME = 'nonesuch.txt'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)

        self.assertEqual(ctx.isDirectory(FILENAME), None)

    def test_isDirectory_simple(self):

        SNAPSHOT_ID = 'isDirectory_simple'
        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes)

        self.assertEqual(ctx.isDirectory(FILENAME), False)

    def test_isDirectory_nested(self):

        SNAPSHOT_ID = 'isDirectory_nested'
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        PATH = '%s/%s' % (SUBDIR, FILENAME)

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes,
                       subdir=SUBDIR)

        self.assertEqual(ctx.isDirectory(PATH), False)

    def test_isDirectory_subdir(self):

        SNAPSHOT_ID = 'isDirectory_subdir'
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes,
                       subdir=SUBDIR)

        self.assertEqual(ctx.isDirectory(SUBDIR), True)

    def test_listDirectory_nonesuch(self):

        SNAPSHOT_ID = 'listDirectory_nonesuch'
        SUBDIR = 'nonesuch/path'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)

        self.assertEqual(ctx.listDirectory(SUBDIR), None)

    def test_listDirectory_root(self):

        SNAPSHOT_ID = 'listDirectory_root'
        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes)

        self.assertEqual(len(ctx.listDirectory(None)), 1)
        self.assertTrue(FILENAME in ctx.listDirectory(None))

    def test_listDirectory_simple(self):

        SNAPSHOT_ID = 'listDirectory_simple'
        FILENAME = 'simple.txt'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes)

        self.assertEqual(ctx.listDirectory(FILENAME), None)

    def test_listDirectory_nested(self):

        SNAPSHOT_ID = 'listDirectory_nested'
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'
        PATH = '%s/%s' % (SUBDIR, FILENAME)

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes,
                       subdir=SUBDIR)

        self.assertEqual(ctx.listDirectory(PATH), None)

    def test_listDirectory_single(self):

        SNAPSHOT_ID = 'listDirectory_nested'
        SUBDIR = 'subdir'
        FILENAME = 'nested.txt'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME, printable_bytes,
                       subdir=SUBDIR)

        names = ctx.listDirectory(SUBDIR)
        self.assertEqual(len(names), 1)
        self.assertTrue(FILENAME in names)

    def test_listDirectory_multiple(self):

        from string import ascii_uppercase

        SNAPSHOT_ID = 'listDirectory_nested'
        SUBDIR = 'subdir'
        FILENAME1 = 'nested.txt'
        FILENAME2 = 'another.txt'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME1, printable_bytes,
                       subdir=SUBDIR)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME2,
                       ascii_uppercase.encode('utf-8'), subdir=SUBDIR)

        names = ctx.listDirectory(SUBDIR)
        self.assertEqual(len(names), 2)
        self.assertTrue(FILENAME1 in names)
        self.assertTrue(FILENAME2 in names)

    def test_listDirectory_skip(self):

        from string import ascii_uppercase

        SNAPSHOT_ID = 'listDirectory_nested'
        SUBDIR = 'subdir'
        FILENAME1 = 'nested.txt'
        FILENAME2 = 'another.txt'
        FILENAME3 = 'another.bak'

        site, tool, ctx = self._makeOne(SNAPSHOT_ID)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME1, printable_bytes,
                       subdir=SUBDIR)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME2,
                       ascii_uppercase.encode('utf-8'), subdir=SUBDIR)
        self._makeFile(tool, SNAPSHOT_ID, FILENAME3, b'abc', subdir=SUBDIR)

        names = ctx.listDirectory(SUBDIR, skip=(FILENAME1,),
                                  skip_suffixes=('.bak',))
        self.assertEqual(len(names), 1)
        self.assertFalse(FILENAME1 in names)
        self.assertTrue(FILENAME2 in names)
        self.assertFalse(FILENAME3 in names)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectoryImportContextTests),
        unittest.makeSuite(DirectoryExportContextTests),
        unittest.makeSuite(TarballImportContextTests),
        unittest.makeSuite(TarballExportContextTests),
        unittest.makeSuite(SnapshotExportContextTests),
        unittest.makeSuite(SnapshotImportContextTests),
    ))
