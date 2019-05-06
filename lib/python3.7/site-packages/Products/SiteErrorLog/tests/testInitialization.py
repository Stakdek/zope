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

import os
import shutil
import tempfile
import unittest

import Products
from App.config import getConfiguration, setConfiguration
from OFS.Application import Application, AppInitializer
from Zope2.Startup.options import ZopeWSGIOptions

test_cfg = """
instancehome {instance_home}

<zodb_db main>
    mount-point /
    <mappingstorage>
        name mappingstorage
    </mappingstorage>
</zodb_db>
"""

def getApp():
    from App.ZApplication import ZApplicationWrapper
    DB = getConfiguration().dbtab.getDatabase('/')
    return ZApplicationWrapper(DB, 'Application', Application)()


class TestInitialization(unittest.TestCase):
    """Test the application initialization"""

    def setUp(self):
        self.original_config = getConfiguration()
        self.TEMPDIR = tempfile.mkdtemp()

    def tearDown(self):
        setConfiguration(self.original_config)
        shutil.rmtree(self.TEMPDIR)
        Products.__path__ = [d
                             for d in Products.__path__
                             if os.path.exists(d)]

    def configure(self, config):
        # We have to create a directory of our own since the existence
        # of the directory is checked.  This handles this in a
        # platform-independent way.
        config_path = os.path.join(self.TEMPDIR, 'zope.conf')
        with open(config_path, 'w') as fd:
            fd.write(config.format(instance_home=self.TEMPDIR))

        options = ZopeWSGIOptions(config_path)()
        config = options.configroot
        self.assertEqual(config.instancehome, self.TEMPDIR)
        setConfiguration(config)

    def getInitializer(self):
        app = getApp()
        return AppInitializer(app)

    def test_install_session_data_manager(self):
        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        self.configure(test_cfg)
        initializer = self.getInitializer()
        app = initializer.getApp()
        initializer.install_products()
        self.assertIsInstance(app.error_log, SiteErrorLog)
        self.assertEqual(app.error_log.meta_type, 'Site Error Log')
