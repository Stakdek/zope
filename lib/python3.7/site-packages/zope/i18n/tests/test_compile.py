##############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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

from zope.testing.loggingsupport import InstalledHandler

from zope.i18n import compile


@unittest.skipUnless(compile.HAS_PYTHON_GETTEXT,
                     "Need python-gettext")
class TestCompile(unittest.TestCase):

    def setUp(self):
        self.handler = InstalledHandler('zope.i18n')
        self.addCleanup(self.handler.uninstall)

    def test_non_existant_path(self):
        self.assertIsNone(compile.compile_mo_file('no_such_domain', ''))

    def test_po_exists_but_invalid(self):
        import tempfile
        import shutil
        import os.path

        td = tempfile.mkdtemp(suffix=".zopei18n_test_compile")
        self.addCleanup(shutil.rmtree, td)

        with open(os.path.join(td, "foo.po"), 'w') as f:
            f.write("this should not compile")

        compile.compile_mo_file('foo', td)

        self.assertIn("Syntax error while compiling",
                      str(self.handler))

    def test_po_exists_cannot_write_mo(self):
        import tempfile
        import shutil
        import os
        import os.path

        td = tempfile.mkdtemp(suffix=".zopei18n_test_compile")
        self.addCleanup(shutil.rmtree, td)

        mofile = os.path.join(td, 'foo.mo')
        with open(mofile, 'w') as f:
            f.write("Touching")

        # Put it in the past, make it not writable
        os.utime(mofile, (1000, 1000))
        os.chmod(mofile, 0)

        with open(os.path.join(td, "foo.po"), 'w') as f:
            f.write("# A comment")

        compile.compile_mo_file('foo', td)

        self.assertIn("Error while compiling",
                      str(self.handler))
