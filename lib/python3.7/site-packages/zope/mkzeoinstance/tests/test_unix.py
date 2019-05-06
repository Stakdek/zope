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

import unittest



class Test_print_(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.mkzeoinstance import print_
        print_(*args, **kw)

    def test_print__no_args_no_kw(self):
        with TempStdout() as out:
            self._callFUT('Foo')
            self.assertEqual(out.getvalue(), 'Foo\n')

    def test_print__w_args(self):
        with TempStdout() as out:
            self._callFUT('Foo: %s %d', 'bar', 123)
            self.assertEqual(out.getvalue(), 'Foo: bar 123\n')

    def test_print__w_kw(self):
        with TempStdout() as out:
            self._callFUT('Foo: %(bar)s', bar='Bar')
            self.assertEqual(out.getvalue(), 'Foo: Bar\n')


class Test_usage(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.mkzeoinstance import usage
        usage(*args, **kw)

    def test_defaults(self):
        from zope.mkzeoinstance import __doc__ as doc, PROGRAM
        _exited = []
        def _exit(rc):
            _exited.append(rc)
        with TempStdout() as out:
            self._callFUT(exit=_exit)
            self.assertEqual(out.getvalue(),
                             ("%s\n" % doc) % {'program': PROGRAM})
        self.assertEqual(_exited, [1])

    def test_explicit(self):
        from zope.mkzeoinstance import __doc__ as doc, PROGRAM
        _exited = []
        def _exit(rc):
            _exited.append(rc)
        with TempStdout() as out:
            self._callFUT('MSG', 2, exit=_exit)
            self.assertEqual(out.getvalue(),
                             ("%s\nMSG\n" % doc) % {'program': PROGRAM})
        self.assertEqual(_exited, [2])

    def test_w_non_str_message(self):
        from zope.mkzeoinstance import __doc__ as doc, PROGRAM
        msg = Exception('Foo')
        def _exit(rc):
            pass
        with TempStdout() as out:
            self._callFUT(msg, exit=_exit)
            self.assertEqual(out.getvalue(),
                             ("%s\nFoo\n" % doc) % {'program': PROGRAM})


class _WithTempdir(object):

    _temp_dir = None

    def tearDown(self):
        super(_WithTempdir, self).tearDown()
        if self._temp_dir is not None:
            import shutil
            shutil.rmtree(self._temp_dir)

    def _makeTempDir(self):
        if self._temp_dir is None:
            import tempfile
            self._temp_dir = tempfile.mkdtemp()
        return self._temp_dir


class ZEOInstanceBuilderTests(_WithTempdir, unittest.TestCase):

    def _getTargetClass(self):
        from zope.mkzeoinstance import ZEOInstanceBuilder
        return ZEOInstanceBuilder

    def _makeOne(self):
        return self._getTargetClass()()

    def _makeParams(self, instance_home=None):
        import os
        import sys
        import ZODB
        import zdaemon

        if instance_home is None:
            temp_dir = self._makeTempDir()
            instance_home = os.path.join(temp_dir, 'instance')
        zdaemon_home = os.path.split(zdaemon.__path__[0])[0]
        zodb_home = os.path.split(ZODB.__path__[0])[0]

        return {'PACKAGE': 'ZEO',
                'python': sys.executable,
                'executable': sys.executable,
                'package': 'zeo',
                'zdaemon_home': zdaemon_home,
                'instance_home': instance_home,
                'address': '99999',
                'zodb_home': zodb_home,
               }

    def test_get_params(self):
        import sys

        expected_params = {'PACKAGE': 'ZEO',
                           'python': sys.executable,
                           'package': 'zeo',
                           'zdaemon_home': '',
                           'instance_home': '',
                           'address': '',
                           'zodb_home': ''}

        builder = self._makeOne()
        params = builder.get_params(zodb_home='',
                                    zdaemon_home='',
                                    instance_home='',
                                    address='')

        self.assertEqual(params, expected_params)

    def test_create_folders_and_files(self):
        import os

        params = self._makeParams()
        instance_home = params['instance_home']

        expected_out = "\n".join([
            "Created directory %(instance_home)s",
            "Created directory %(instance_home)s/etc",
            "Created directory %(instance_home)s/var",
            "Created directory %(instance_home)s/log",
            "Created directory %(instance_home)s/bin",
            "Wrote file %(instance_home)s/etc/zeo.conf",
            "Wrote file %(instance_home)s/bin/zeoctl",
            "Changed mode for %(instance_home)s/bin/zeoctl to 755",
            "Wrote file %(instance_home)s/bin/runzeo",
            "Changed mode for %(instance_home)s/bin/runzeo to 755",
            "",
            ]) % params

        builder = self._makeOne()
        with TempStdout() as temp_out_file:

            with TempUmask(0o022):
                builder.create(instance_home, params)

            self.assertEqual(temp_out_file.getvalue(), expected_out)

        self.assertTrue(os.path.exists(os.path.join(instance_home, 'etc')))
        self.assertTrue(os.path.exists(os.path.join(instance_home, 'var')))
        self.assertTrue(os.path.exists(os.path.join(instance_home, 'log')))
        self.assertTrue(os.path.exists(os.path.join(instance_home, 'bin')))
        self.assertTrue(
            os.path.exists(os.path.join(instance_home, 'etc', 'zeo.conf')))
        self.assertTrue(
            os.path.exists(os.path.join(instance_home, 'bin', 'zeoctl')))
        self.assertTrue(
            os.path.exists(os.path.join(instance_home, 'bin', 'runzeo')))

    def test_zeo_conf_content(self):
        import os

        params = self._makeParams()
        instance_home = params['instance_home']
        zeo_conf_path = os.path.join(instance_home, 'etc', 'zeo.conf')
        expected_out = "\n".join([
            "# ZEO configuration file",
            "",
            "%%define INSTANCE %(instance_home)s",
            "",
            "<zeo>",
            "  address 99999",
            "  read-only false",
            "  invalidation-queue-size 100",
            "  # pid-filename $INSTANCE/var/ZEO.pid",
            "  # monitor-address PORT",
            "  # transaction-timeout SECONDS",
            "</zeo>",
            "",
            "<filestorage 1>",
            "  path $INSTANCE/var/Data.fs",
            "</filestorage>",
            "",
            "<eventlog>",
            "  level info",
            "  <logfile>",
            "    path $INSTANCE/log/zeo.log",
            "  </logfile>",
            "</eventlog>",
            "",
            "<runner>",
            "  program $INSTANCE/bin/runzeo",
            "  socket-name $INSTANCE/var/zeo.zdsock",
            "  daemon true",
            "  forever false",
            "  backoff-limit 10",
            "  exit-codes 0, 2",
            "  directory $INSTANCE",
            "  default-to-interactive true",
            "  # user zope",
            "  python %(executable)s",
            "  zdrun %(zdaemon_home)s/zdaemon/zdrun.py",
            "",
            "  # This logfile should match the one in the zeo.conf file.",
            "  # It is used by zdctl's logtail command, "
                        "zdrun/zdctl doesn't write it.",
            "  logfile $INSTANCE/log/zeo.log",
            "</runner>",
            '',
            ]) % params

        builder = self._makeOne()
        with TempStdout() as temp_out_file:
            builder.create(instance_home, params)

        with open(zeo_conf_path) as f:
            self.assertEqual(f.read(), expected_out)

    def test_zeoctl_content(self):
        import os
        params = self._makeParams()
        instance_home = params['instance_home']
        zeoctl_path = os.path.join(instance_home, 'bin', 'zeoctl')

        expected_out = "\n".join([
            '#!/bin/sh',
            '# ZEO instance control script',
            '',
            '# The following two lines are for chkconfig.  '
                            'On Red Hat Linux (and',
            '# some other systems), you can copy or symlink this script into',
            '# /etc/rc.d/init.d/ and then use chkconfig(8) to '
                            'automatically start',
            '# ZEO at boot time.',
            '',
            '# chkconfig: 345 90 10',
            '# description: start a ZEO server',
            '',
            'PYTHON="%(executable)s"',
            'INSTANCE_HOME="%(instance_home)s"',
            'ZODB3_HOME="%(zodb_home)s"',
            '',
            'CONFIG_FILE="%(instance_home)s/etc/zeo.conf"',
            '',
            'PYTHONPATH="$ZODB3_HOME"',
            'export PYTHONPATH INSTANCE_HOME',
            '',
            'exec "$PYTHON" -m ZEO.zeoctl -C "$CONFIG_FILE" ${1+"$@"}',
            '',
            ]) % params

        builder = self._makeOne()
        with TempStdout() as temp_out_file:
            builder.create(instance_home, params)

        with open(zeoctl_path) as f:
            self.assertEqual(f.read(), expected_out)

    def test_run_w_invalid_opt(self):
        builder = self._makeOne()
        usage = UsageStub()
        self.assertRaises(UsageExit, builder.run, ['--nonesuch'], usage=usage)
        self.assertEqual(usage._called_with,
                         ('option --nonesuch not recognized', 1))

    def test_run_w_help(self):
        builder = self._makeOne()
        usage = UsageStub()
        self.assertRaises(UsageExit, builder.run, ['--help'], usage=usage)
        self.assertEqual(usage._called_with, ('NO MESSAGE', 2))

    def test_run_wo_arguments(self):
        builder = self._makeOne()
        usage = UsageStub()
        self.assertRaises(UsageExit, builder.run, [], usage=usage)
        self.assertEqual(usage._called_with, ('NO MESSAGE', 1))

    def test_run_w_too_many_arguments(self):
        builder = self._makeOne()
        usage = UsageStub()
        self.assertRaises(UsageExit, builder.run, ['a', 'b', 'c'], usage=usage)
        self.assertEqual(usage._called_with, ('NO MESSAGE', 1))

    def test_run_wo_single_arg_non_absolute(self):
        import os

        builder = self._makeOne()
        tempdir = self._makeTempDir()
        where = os.path.join(tempdir, 'foo', '..', 'bar')
        abswhere = os.path.abspath(where)

        params = self._makeParams()
        params['instance_home'] = abswhere
        expected_out = "\n".join([
            "Created directory %(instance_home)s",
            "Created directory %(instance_home)s/etc",
            "Created directory %(instance_home)s/var",
            "Created directory %(instance_home)s/log",
            "Created directory %(instance_home)s/bin",
            "Wrote file %(instance_home)s/etc/zeo.conf",
            "Wrote file %(instance_home)s/bin/zeoctl",
            "Changed mode for %(instance_home)s/bin/zeoctl to 755",
            "Wrote file %(instance_home)s/bin/runzeo",
            "Changed mode for %(instance_home)s/bin/runzeo to 755",
            "",
            ]) % params

        with TempStdout() as temp_out_file:
            with TempUmask(0o022):
                builder.run([where])

            self.assertEqual(temp_out_file.getvalue(), expected_out)

        self.assertTrue(os.path.exists(os.path.join(abswhere, 'etc')))
        self.assertTrue(os.path.exists(os.path.join(abswhere, 'var')))
        self.assertTrue(os.path.exists(os.path.join(abswhere, 'log')))
        self.assertTrue(os.path.exists(os.path.join(abswhere, 'bin')))
        self.assertTrue(
            os.path.exists(os.path.join(abswhere, 'etc', 'zeo.conf')))
        self.assertTrue(
            os.path.exists(os.path.join(abswhere, 'bin', 'zeoctl')))
        self.assertTrue(
            os.path.exists(os.path.join(abswhere, 'bin', 'runzeo')))

    def test_run_wo_two_args_no_host(self):
        import os

        builder = self._makeOne()
        params = self._makeParams()
        instance_home = params['instance_home']

        with TempStdout() as temp_out_file:
            with TempUmask(0o022):
                builder.run([instance_home, '8888'])

        with open(os.path.join(instance_home, 'etc', 'zeo.conf')) as f:
            conf = f.read()
        self.assertTrue(
            'address 8888' in [x.strip() for x in conf.splitlines()])

    def test_run_wo_two_args_w_host(self):
        import os

        builder = self._makeOne()
        params = self._makeParams()
        instance_home = params['instance_home']

        with TempStdout() as temp_out_file:
            with TempUmask(0o022):
                builder.run([instance_home, 'localhost:8888'])

        with open(os.path.join(instance_home, 'etc', 'zeo.conf')) as f:
            conf = f.read()
        self.assertTrue(
            'address localhost:8888' in [x.strip() for x in conf.splitlines()])


class UtilityFunctionsTest(_WithTempdir, unittest.TestCase):

    def test_mkdirs(self):
        import os
        from zope.mkzeoinstance import mkdirs
        temp_dir = self._makeTempDir()
        path = os.path.join(temp_dir, 'test')

        with TempStdout() as temp_out_file:
            mkdirs(path)
            self.assertEqual('Created directory %s\n' % path,
                            temp_out_file.getvalue())
        self.assertTrue(os.path.exists(path))

    def test_mkdirs_nested(self):
        import os
        from zope.mkzeoinstance import mkdirs
        temp_dir = self._makeTempDir()
        parent_path = os.path.join(temp_dir, 'parent')
        child_path = os.path.join(parent_path, 'child')

        with TempStdout() as temp_out_file:
            mkdirs(child_path)
            self.assertEqual('Created directory %s\n'
                             'Created directory %s\n'
                                % (parent_path, child_path),
                            temp_out_file.getvalue())
        self.assertTrue(os.path.isdir(child_path))

    def test_makedir(self):
        import os
        from zope.mkzeoinstance import makedir
        temp_dir = self._makeTempDir()
        path = os.path.join(temp_dir, 'test')

        with TempStdout() as temp_out_file:
            makedir(temp_dir, 'test')
            self.assertEqual('Created directory %s\n' % path,
                             temp_out_file.getvalue())
        self.assertTrue(os.path.exists(path))

    def test_makefile(self):
        import os
        from zope.mkzeoinstance import makefile
        template = "KEY=%(key)s"
        params = {'key': 'value'}
        temp_dir = self._makeTempDir()
        path = os.path.join(temp_dir, 'test.txt')

        with TempStdout() as temp_out_file:
            makefile(template, temp_dir, 'test.txt', **params)
            self.assertEqual('Wrote file %s\n' % path,
                            temp_out_file.getvalue())

        with open(path) as f:
            self.assertEqual('KEY=value', f.read())

    def test_makefile_existing_same_content(self):
        import os
        from zope.mkzeoinstance import makefile
        template = "KEY=%(key)s"
        params = {'key': 'value'}
        temp_dir = self._makeTempDir()
        path = os.path.join(temp_dir, 'test.txt')

        with open(path, 'w') as f:
            f.write(template % params)

        with TempStdout() as temp_out_file:
            makefile(template, temp_dir, 'test.txt', **params)
            self.assertEqual('', temp_out_file.getvalue())

        with open(path) as f:
            self.assertEqual('KEY=value', f.read())

    def test_makefile_existing_different_content(self):
        import os
        from zope.mkzeoinstance import makefile
        template = "KEY=%(key)s"
        params = {'key': 'value'}
        temp_dir = self._makeTempDir()
        path = os.path.join(temp_dir, 'test.txt')

        with open(path, 'w') as f:
            f.write('NOT THE SAME CONTENT')

        with TempStdout() as temp_out_file:
            makefile(template, temp_dir, 'test.txt', **params)

        self.assertEqual('Warning: not overwriting existing file %s\n' % path,
                          temp_out_file.getvalue())

        with open(path) as f:
            self.assertEqual('NOT THE SAME CONTENT', f.read())

    def test_makexfile(self):
        import os
        from zope.mkzeoinstance import makexfile
        params = {}
        temp_dir = self._makeTempDir()
        path = os.path.join(temp_dir, 'test.txt')
        expected_out = ("Wrote file %(path)s\n"
                        "Changed mode for %(path)s to 755\n"
                       ) % {'path': path}

        with TempStdout() as temp_out_file:

            with TempUmask(0o022):
                makexfile('', temp_dir, 'test.txt', **params)

            self.assertEqual(expected_out,
                            temp_out_file.getvalue())


class TempStdout(object):

    def __enter__(self):
        import io
        import sys
        self._old_stdout = sys.stdout
        tmpfile = sys.stdout = io.StringIO()
        return tmpfile

    def __exit__(self, *err):
        import sys
        sys.stdout = self._old_stdout


class TempUmask(object):

    def __init__(self, target_umask):
        self._target_umask = target_umask

    def __enter__(self):
        import os
        self._old_umask = os.umask(self._target_umask)
        return self

    def __exit__(self, *err):
        import os
        os.umask(self._old_umask)


class UsageExit(Exception):
    pass


class UsageStub(object):

    _called_with = None

    def __call__(self, msg='NO MESSAGE', rc=None):
        self._called_with = (str(msg), rc)
        raise UsageExit()
