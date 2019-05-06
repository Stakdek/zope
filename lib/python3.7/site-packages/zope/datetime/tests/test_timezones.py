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

class TestTimezones(unittest.TestCase):

    def test_dumpTimezoneInfo(self):
        from zope.datetime.timezones import dumpTimezoneInfo
        from zope.datetime.timezones import historical_zone_info

        import io

        output = io.StringIO() if bytes is not str else io.BytesIO()

        dumpTimezoneInfo(historical_zone_info, out=output)

        value = output.getvalue()

        self.assertTrue(value.endswith('\n}\n'))
