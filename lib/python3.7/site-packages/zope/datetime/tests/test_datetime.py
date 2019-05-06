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
# pylint:disable=protected-access
import unittest

import time
from zope import datetime

class TestCache(unittest.TestCase):

    def test_error(self):
        with self.assertRaisesRegexp(datetime.DateTimeError,
                                     "Unrecognized timezone"):
            datetime._cache().__getitem__('foo')


class TestFuncs(unittest.TestCase):

    def test_correctYear(self):
        self.assertEqual(2069, datetime._correctYear(69))
        self.assertEqual(1998, datetime._correctYear(98))


    def test_safegmtime_safelocaltime_overflow(self):
        # Use values that are practically guaranteed to overflow on all
        # platforms
        v = 2**64 + 1
        fv = float(v)
        for func in (datetime.safegmtime, datetime.safelocaltime):
            for x in (v, fv):
                with self.assertRaises(datetime.TimeError):
                    func(x)

    def test_safegmtime(self):
        self.assertIsNotNone(datetime.safegmtime(6000))


    def test_safelocaltime(self):
        self.assertIsNotNone(datetime.safelocaltime(6000))

    def test_calcSD(self):
        s, d = datetime._calcSD(9)
        self.assertAlmostEqual(s, 0, places=1)
        self.assertGreater(d, 0)

    def test_calcDependentSecond(self):
        s = datetime._calcDependentSecond('000', 0)
        self.assertGreater(s, 0)

    def test_julianday(self):
        self.assertEqual(datetime._julianday(2000, 13, 1), 2451910)
        self.assertEqual(datetime._julianday(2000, -1, 1), 2451483)
        self.assertEqual(datetime._julianday(0, 1, 1), 1721057)

    def test_findLocalTimeZoneName(self):
        zmap = datetime._cache._zmap
        try:
            datetime._cache._zmap = {}
            name = datetime._findLocalTimeZoneName(True)
            self.assertEqual('', name)
        finally:
            datetime._cache._zmap = zmap


class TestTimezone(unittest.TestCase):

    def _makeOne(self, name='name', timect=1, typect=0,
                 ttrans=(), tindex=1, tinfo=(), az=0):
        return datetime._timezone((name, timect, typect, ttrans, tindex, tinfo, az))

    def test_default_index(self):
        tz = self._makeOne(timect=0)
        self.assertEqual(0, tz.default_index())

        tz = self._makeOne(timect=1, typect=2, tinfo=((0, 1), (0, 0)))
        self.assertEqual(1, tz.default_index())

        tz = self._makeOne(timect=1, typect=2, tinfo=((0, 1), (0, 1)))
        self.assertEqual(0, tz.default_index())

    def test_index(self):
        tz = self._makeOne(ttrans=(1,), tindex='a')
        self.assertEqual((0, 97, 0),
                         tz.index(0))

        self.assertEqual((97, 97, 0),
                         tz.index(1))

        tz.timect = 2
        tz.tindex = 'ab'
        self.assertEqual((98, 98, 97),
                         tz.index(1))



class TestDateTimeParser(unittest.TestCase):

    def _makeOne(self):
        return datetime.DateTimeParser()

    def _callParse(self, input_data):
        return self._makeOne().parse(input_data)

    def _call_parse(self, input_data):
        return self._makeOne()._parse(input_data)

    def test_parse_bad_input(self):
        with self.assertRaises(TypeError):
            self._callParse(None)

        with self.assertRaises(datetime.SyntaxError):
            self._callParse('')

    def test_parse_bad_year(self):
        with self.assertRaises(datetime.DateError):
            self._callParse("2000-01-32")

        with self.assertRaises(datetime.SyntaxError):
            self._call_parse("995-01-20")

    def test_parse_bad_time(self):
        with self.assertRaises(datetime.TimeError):
            self._callParse("2000-01-01T25:63")

    def test_parse_produces_invalid(self):
        dtp = self._makeOne()
        dtp._validDate = lambda *args: False

        with self.assertRaises(datetime.DateError):
            dtp.parse("2000-01-01")

    def test_time_bad_tz(self):
        # Have to mock the time() method here to get
        # the desired return value for TZ, I couldn't find
        # input that would get is there naturally
        def t(*args):
            return (2000, 1, 1, 0, 0, 0, '+FOO')
        dtp = self._makeOne()
        dtp.parse = t
        with self.assertRaisesRegexp(datetime.DateTimeError,
                                     "Unknown time zone"):
            dtp.time("foo")

    def test_time_no_tz(self):
        # See test_time_bad_tz
        def t(*args):
            return (2000, 1, 1, 0, 0, 0, '')
        dtp = self._makeOne()
        dtp.parse = t
        x = dtp.time("foo")
        self.assertGreaterEqual(x, 946000000.0)

    def test_localZone_non_multiple(self):
        dtp = self._makeOne()
        dtp._localzone0 = 0
        dtp._localzone1 = 1

        dtp._multipleZones = False
        self.assertEqual(0, dtp.localZone())

    def test_calcTimezoneName_non_multiple(self):
        dtp = self._makeOne()
        dtp._localzone0 = 0
        dtp._localzone1 = 1

        dtp._multipleZones = False
        self.assertEqual(0, dtp._calcTimezoneName(None, None))

    def test_calcTimezoneName_safelocaltime_fail(self):

        dtp = self._makeOne()
        dtp._multipleZones = True
        dtp._localzone0 = '0'
        dtp._localzone1 = '1'

        class MyException(Exception):
            pass

        def i(_):
            raise MyException()

        orig_safelocaltime = datetime.safelocaltime
        try:
            datetime.safelocaltime = i
            self.assertRaises(MyException,
                              dtp._calcTimezoneName, 9467061400, 0)
        finally:
            datetime.safelocaltime = orig_safelocaltime

    def test_calcTimezoneName_multiple_non_fail(self):
        dtp = self._makeOne()
        dtp._multipleZones = True
        self.assertIsNotNone(dtp._calcTimezoneName(100, 1))

    def test_parse_noniso_bad_month(self):
        with self.assertRaises(datetime.SyntaxError):
            self._callParse("2000--31 +1")

    def test_parse_noniso_tz(self):
        x = self._call_parse("2000-01-01 22:13+05:00")
        self.assertEqual((2000, 1, 1, 22, 13, 0, '+0500'), x)

    def test_parse_bad_month(self):
        with self.assertRaises(datetime.SyntaxError):
            self._call_parse("January January")

    def test_parse_bad_tm(self):
        with self.assertRaises(datetime.SyntaxError):
            self._call_parse("pm pm")

    def test_parse_multiple_ints(self):
        result = self._call_parse("1 24 2000")
        self.assertEqual(result[:-1],
                         (2000, 1, 24, 0, 0, 0))

        with self.assertRaises(datetime.DateTimeError):
            result = self._call_parse("January 24 2000 61")

        result = self._call_parse("January 2000 10")
        self.assertEqual(result[:-1],
                         (2000, 1, 10, 0, 0, 0))

        # This one takes "32" as the year, and has nothing for day or month.
        # Therefore it overrides day, month, and year with the current values
        result = self._call_parse("10 32 12")
        self.assertEqual(result[:-1],
                         time.localtime()[:3] + (0, 0, 0))

        result = self._call_parse("13 32 12")
        self.assertEqual(result[:-1],
                         (2032, 12, 13, 0, 0, 0))

        result = self._call_parse("12 32 13")
        self.assertEqual(result[:-1],
                         (2032, 12, 13, 0, 0, 0))

        with self.assertRaises(datetime.DateError):
            result = self._call_parse("13 31 32")

        result = self._call_parse("10 31 32")
        self.assertEqual(result[:-1],
                         (2032, 10, 31, 0, 0, 0))

        result = self._call_parse("10 30 30")
        self.assertEqual(result[:-1],
                         (2030, 10, 30, 0, 0, 0))

        with self.assertRaises(datetime.DateTimeError):
            self._call_parse("10 30 30 19:61")

        with self.assertRaises(datetime.SyntaxError):
            self._call_parse("10 30 30 20 20 20 20")

    def test_parse_iso_index_error(self):
        dtp = self._makeOne()
        with self.assertRaisesRegexp(datetime.DateError,
                                     "Not an ISO 8601 compliant"):
            dtp._parse_iso8601('')

    def test_parse_with_dot(self):
        result = self._call_parse("Jan.1.2000")
        self.assertEqual(result[:-1],
                         (2000, 1, 1, 0, 0, 0))

    def test_parse_am_pm(self):
        result = self._call_parse("2000-01-01 12 am")
        self.assertEqual(result[:-1],
                         (2000, 1, 1, 0, 0, 0))

        result = self._call_parse("2000-01-01 1 pm")
        self.assertEqual(result[:-1],
                         (2000, 1, 1, 13, 0, 0))

    def test_valid_date(self):
        self.assertFalse(self._makeOne()._validDate(2000, 0, 12))

    def test_localZone_multiple(self):
        p = self._makeOne()
        p._multipleZones = True
        self.assertIsNotNone(p.localZone())
