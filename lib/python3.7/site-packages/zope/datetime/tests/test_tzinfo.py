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
"""Test for the 'tzinfo() function
"""

import unittest
import pickle
import datetime

from zope.datetime import tzinfo


class Test(unittest.TestCase):

    def test(self):

        for minutes in 1439, 600, 1, 0, -1, -600, -1439:
            info1 = tzinfo(minutes)
            info2 = tzinfo(minutes)

            self.assertEqual(info1, info2)
            self.assertIs(info1, info2)
            self.assertIs(pickle.loads(pickle.dumps(info1)), info1)


            self.assertEqual(info1.utcoffset(None),
                             datetime.timedelta(minutes=minutes))

            self.assertEqual(info1.dst(None), None)
            self.assertEqual(info1.tzname(None), None)

        for minutes in 900000, 1440*60, -1440*60, -900000:
            self.assertRaises(ValueError, tzinfo, minutes)



def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
