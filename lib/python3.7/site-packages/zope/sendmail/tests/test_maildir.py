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
"""Unit tests for zope.sendmail.maildir module
"""
from __future__ import print_function

import unittest
import stat
import os
import errno

from zope.interface.verify import verifyObject

from zope.sendmail.maildir import Maildir
from zope.sendmail.interfaces import IMaildirMessageWriter


class FakeSocketModule(object):

    def gethostname(self):
        return 'myhostname'


class FakeTimeModule(object):

    _timer = 1234500000

    def time(self):
        return self._timer

    def sleep(self, n):
        self._timer += n


class FakeOsPathModule(object):

    def __init__(self, files, dirs):
        self.files = files
        self.dirs = dirs
        mtimes = {}
        for t, f in enumerate(files):
            mtimes[f] = 9999 - t
        self._mtimes = mtimes

    def join(self, *args):
        return '/'.join(args)

    def isdir(self, dir):
        return dir in self.dirs

    def getmtime(self, f):
        return self._mtimes.get(f, 10000)


class FakeOsModule(object):

    F_OK = 0
    O_CREAT = os.O_CREAT
    O_EXCL = os.O_EXCL
    O_WRONLY = os.O_WRONLY

    _stat_mode = {
        '/path/to/maildir': stat.S_IFDIR,
        '/path/to/maildir/new': stat.S_IFDIR,
        '/path/to/maildir/new/1': stat.S_IFREG,
        '/path/to/maildir/new/2': stat.S_IFREG,
        '/path/to/maildir/cur': stat.S_IFDIR,
        '/path/to/maildir/cur/1': stat.S_IFREG,
        '/path/to/maildir/cur/2': stat.S_IFREG,
        '/path/to/maildir/tmp': stat.S_IFDIR,
        '/path/to/maildir/tmp/1': stat.S_IFREG,
        '/path/to/maildir/tmp/2': stat.S_IFREG,
        '/path/to/maildir/tmp/1234500000.4242.myhostname.*': stat.S_IFREG,
        '/path/to/maildir/tmp/1234500001.4242.myhostname.*': stat.S_IFREG,
        '/path/to/regularfile': stat.S_IFREG,
        '/path/to/emptydir': stat.S_IFDIR,
    }
    _listdir = {
        '/path/to/maildir/new': ['1', '2', '.svn'],
        '/path/to/maildir/cur': ['2', '1', '.tmp'],
        '/path/to/maildir/tmp': ['1', '2', '.ignore'],
    }

    path = FakeOsPathModule(_stat_mode, _listdir)

    _made_directories = ()
    _removed_files = ()
    _renamed_files = ()

    _all_files_exist = False

    def __init__(self):
        self._descriptors = {}

    def access(self, path, mode):
        if self._all_files_exist:
            return True
        if path in self._stat_mode:
            return True
        if path.rsplit('.', 1)[0] + '.*' in self._stat_mode:
            return True
        return False

    def stat(self, path):
        raise NotImplementedError()

    def listdir(self, path):
        return self._listdir.get(path, [])

    def mkdir(self, path):
        self._made_directories += (path, )

    def getpid(self):
        return 4242

    def unlink(self, path):
        self._removed_files += (path, )

    def rename(self, old, new):
        self._renamed_files += ((old, new), )

    def open(self, filename, flags, mode=0o777):
        if (flags & os.O_EXCL and flags & os.O_CREAT
                and self.access(filename, 0)):
            raise OSError(errno.EEXIST, 'file already exists')
        if not flags & os.O_CREAT and not self.access(filename, 0):
            raise OSError('file not found')  # pragma: no cover
        fd = max(list(self._descriptors.keys()) + [2]) + 1
        self._descriptors[fd] = filename, flags, mode
        return fd

    def fdopen(self, fd, mode='r'):
        try:
            filename, flags, _permissions = self._descriptors[fd]
        except KeyError:  # pragma: no cover
            raise AssertionError('os.fdopen() called with an unknown'
                                 ' file descriptor')
        assert mode == 'wb'
        assert flags & os.O_WRONLY
        assert not flags & os.O_RDWR
        return FakeFile(filename, mode)


class FakeFile(object):

    def __init__(self, filename, mode):
        self._filename = filename
        self._mode = mode
        self._written = b'' if 'b' in mode else ''
        self._closed = False

    def close(self):
        self._closed = True

    def write(self, data):
        self._written += data

    def writelines(self, lines):
        self._written += b''.join(lines)


class TestMaildir(unittest.TestCase):

    def setUp(self):
        import zope.sendmail.maildir as maildir_module
        self.maildir_module = maildir_module
        self.old_os_module = maildir_module.os
        self.old_time_module = maildir_module.time
        self.old_socket_module = maildir_module.socket
        maildir_module.os = self.fake_os_module = FakeOsModule()
        maildir_module.time = FakeTimeModule()
        maildir_module.socket = FakeSocketModule()

    def tearDown(self):
        self.maildir_module.os = self.old_os_module
        self.maildir_module.time = self.old_time_module
        self.maildir_module.socket = self.old_socket_module
        self.fake_os_module._all_files_exist = False

    def test_factory(self):
        from zope.sendmail.interfaces import IMaildirFactory, IMaildir
        verifyObject(IMaildirFactory, Maildir)

        # Case 1: normal maildir
        m = Maildir('/path/to/maildir')
        verifyObject(IMaildir, m)

        # Case 2a: directory does not exist, create = False
        self.assertRaises(ValueError, Maildir, '/path/to/nosuchfolder', False)

        # Case 2b: directory does not exist, create = True
        m = Maildir('/path/to/nosuchfolder', True)
        verifyObject(IMaildir, m)
        dirs = sorted(self.fake_os_module._made_directories)
        self.assertEqual(dirs, ['/path/to/nosuchfolder',
                                '/path/to/nosuchfolder/cur',
                                '/path/to/nosuchfolder/new',
                                '/path/to/nosuchfolder/tmp'])

        # Case 3: it is a file, not a directory
        self.assertRaises(ValueError, Maildir, '/path/to/regularfile', False)
        self.assertRaises(ValueError, Maildir, '/path/to/regularfile', True)

        # Case 4: it is a directory, but not a maildir
        self.assertRaises(ValueError, Maildir, '/path/to/emptydir', False)
        self.assertRaises(ValueError, Maildir, '/path/to/emptydir', True)

    def test_iteration(self):
        m = Maildir('/path/to/maildir')
        messages = sorted(m)
        self.assertEqual(messages, ['/path/to/maildir/cur/1',
                                    '/path/to/maildir/cur/2',
                                    '/path/to/maildir/new/1',
                                    '/path/to/maildir/new/2'])

    def test_newMessage(self):
        m = Maildir('/path/to/maildir')
        fd = m.newMessage()
        verifyObject(IMaildirMessageWriter, fd)
        self.assertTrue(fd._filename.startswith(
            '/path/to/maildir/tmp/1234500002.4242.myhostname.'))

    def test_newMessage_error(self):
        m = Maildir('/path/to/maildir')

        def open(*args):
            raise OSError(errno.EADDRINUSE, "")
        self.fake_os_module.open = open

        with self.assertRaises(OSError) as exc:
            m.newMessage()

        self.assertEqual(exc.exception.errno, errno.EADDRINUSE)

    def test_newMessage_never_loops(self):
        self.fake_os_module._all_files_exist = True
        m = Maildir('/path/to/maildir')
        self.assertRaises(RuntimeError, m.newMessage)

    def test_message_writer_and_abort(self):
        from zope.sendmail.maildir import MaildirMessageWriter
        filename1 = '/path/to/maildir/tmp/1234500002.4242.myhostname'
        filename2 = '/path/to/maildir/new/1234500002.4242.myhostname'
        fd = FakeFile(filename1, 'wb')
        writer = MaildirMessageWriter(fd, filename1, filename2)
        self.assertEqual(writer._fd._filename, filename1)
        self.assertEqual(writer._fd._mode, 'wb')
        print('fee', end='', file=writer)
        writer.write(' fie')
        writer.writelines([' foe', ' foo'])
        self.assertEqual(writer._fd._written, b'fee fie foe foo')

        writer.abort()
        self.assertTrue(writer._fd._closed)
        self.assertTrue(filename1 in self.fake_os_module._removed_files)
        # Once aborted, abort does nothing
        self.fake_os_module._removed_files = ()
        writer.abort()
        writer.abort()
        self.assertEqual(self.fake_os_module._removed_files, ())
        # Once aborted, commit fails
        self.assertRaises(RuntimeError, writer.commit)

    def test_message_writer_commit(self):
        from zope.sendmail.maildir import MaildirMessageWriter
        filename1 = '/path/to/maildir/tmp/1234500002.4242.myhostname'
        filename2 = '/path/to/maildir/new/1234500002.4242.myhostname'
        fd = FakeFile(filename1, 'w')
        writer = MaildirMessageWriter(fd, filename1, filename2)
        writer.commit()
        self.assertTrue(writer._fd._closed)
        self.assertIn((filename1, filename2),
                      self.fake_os_module._renamed_files)
        # Once commited, commit does nothing
        self.fake_os_module._renamed_files = ()
        writer.commit()
        writer.commit()
        self.assertEqual(self.fake_os_module._renamed_files, ())
        # Once commited, abort does nothing
        writer.abort()
        writer.abort()
        self.assertEqual(self.fake_os_module._renamed_files, ())

    def test_message_writer_unicode(self):
        from zope.sendmail.maildir import MaildirMessageWriter
        filename1 = '/path/to/maildir/tmp/1234500002.4242.myhostname'
        filename2 = '/path/to/maildir/new/1234500002.4242.myhostname'
        fd = FakeFile(filename1, 'wb')
        writer = MaildirMessageWriter(fd, filename1, filename2)
        self.assertEqual(writer._fd._filename, filename1)
        self.assertEqual(writer._fd._mode, 'wb')
        print(u'fe\xe8', end='', file=writer)
        writer.write(u' fi\xe8')
        writer.writelines([u' fo\xe8', u' fo\xf2'])
        self.assertEqual(writer._fd._written,
                         b'fe\xc3\xa8 fi\xc3\xa8 fo\xc3\xa8 fo\xc3\xb2')
        writer.close()
        self.assertTrue(writer._fd._closed)
