##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Locale and LocaleProvider Implementation.
"""
__docformat__ = 'restructuredtext'

import os
from datetime import date

from zope.interface import implementer
from zope.i18n.interfaces.locales import ILocale
from zope.i18n.interfaces.locales import ILocaleDisplayNames, ILocaleDates
from zope.i18n.interfaces.locales import ILocaleVersion, ILocaleIdentity
from zope.i18n.interfaces.locales import ILocaleTimeZone, ILocaleCalendar
from zope.i18n.interfaces.locales import ILocaleCurrency, ILocaleNumbers
from zope.i18n.interfaces.locales import ILocaleFormat, ILocaleFormatLength
from zope.i18n.interfaces.locales import ILocaleOrientation
from zope.i18n.interfaces.locales import ILocaleDayContext, ILocaleMonthContext
from zope.i18n.format import NumberFormat, DateTimeFormat
from zope.i18n.locales.inheritance import \
     AttributeInheritance, InheritingDictionary, NoParentException
from zope.i18n.locales.provider import LocaleProvider, LoadLocaleError


# Setup the locale directory
from zope import i18n
LOCALEDIR = os.path.join(os.path.dirname(i18n.__file__), "locales", "data")

# Global LocaleProvider. We really just need this single one.
locales = LocaleProvider(LOCALEDIR)

# Define some constants that can be used

JANUARY = 1
FEBRUARY = 2
MARCH = 3
APRIL = 4
MAY = 5
JUNE = 6
JULY = 7
AUGUST = 8
SEPTEMBER = 9
OCTOBER = 10
NOVEMBER = 11
DECEMBER = 12

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THURSDAY = 4
FRIDAY = 5
SATURDAY = 6
SUNDAY = 7

dayMapping = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4,
              'fri': 5, 'sat': 6, 'sun': 7}

BC = 1
AD = 2

calendarAliases = {'islamic': ('arabic',),
                   'islamic-civil': ('civil-arabic',),
                   'buddhist': ('thai-buddhist', )}

@implementer(ILocaleIdentity)
class LocaleIdentity(object):
    """Represents a unique identification of the locale

    This class does not have to deal with inheritance.

    Examples::

      >>> id = LocaleIdentity('en')
      >>> id
      <LocaleIdentity (en, None, None, None)>

      >>> id = LocaleIdentity('en', 'latin')
      >>> id
      <LocaleIdentity (en, latin, None, None)>

      >>> id = LocaleIdentity('en', 'latin', 'US')
      >>> id
      <LocaleIdentity (en, latin, US, None)>

      >>> id = LocaleIdentity('en', 'latin', 'US', 'POSIX')
      >>> id
      <LocaleIdentity (en, latin, US, POSIX)>

      >>> id = LocaleIdentity('en', None, 'US', 'POSIX')
      >>> id
      <LocaleIdentity (en, None, US, POSIX)>
    """

    def __init__(self, language=None, script=None, territory=None, variant=None):
        """Initialize object."""
        self.language = language
        self.script = script
        self.territory = territory
        self.variant = variant

    def __repr__(self):
        """See zope.i18n.interfaces.ILocaleIdentity
        """
        return "<LocaleIdentity (%s, %s, %s, %s)>" %(
            self.language, self.script, self.territory, self.variant)


@implementer(ILocaleVersion)
class LocaleVersion(object):
    """Represents a particular version of a locale

    This class does not have to deal with inheritance.

    Examples::

      >>> from datetime import datetime
      >>> (LocaleVersion('1.0', datetime(2004, 1, 1), 'no notes') ==
      ...     LocaleVersion('1.0', datetime(2004, 1, 1), 'no notes again'))
      True

      >>> (LocaleVersion('1.0', datetime(2004, 1, 1), 'no notes') <
      ...     LocaleVersion('1.0', datetime(2004, 1, 2), 'no notes again'))
      True

      >>> (LocaleVersion('1.0', datetime(2004, 1, 1), 'no notes') <
      ...     LocaleVersion('0.9', datetime(2004, 1, 2), 'no notes again'))
      True

      >>> (LocaleVersion('1.0', datetime(2004, 1, 1), 'no notes') >
      ...     LocaleVersion('0.9', datetime(2004, 1, 1), 'no notes again'))
      True

    """

    def __init__(self, number, generationDate, notes):
        """Initialize object."""
        self.number = number
        assert isinstance(generationDate, (date, type(None)))
        self.generationDate = generationDate
        self.notes = notes

    def __lt__(self, other):
        return ((self.generationDate, self.number) <
                (other.generationDate, other.number))

    def __eq__(self, other):
        return ((self.generationDate, self.number) ==
                (other.generationDate, other.number))

@implementer(ILocaleDisplayNames)
class LocaleDisplayNames(AttributeInheritance):
    """Locale display names with inheritable data.

    Examples::

      >>> from zope.i18n.locales.tests.test_docstrings import \\
      ...     LocaleInheritanceStub
      >>> root = LocaleInheritanceStub()
      >>> root.displayNames = LocaleDisplayNames()
      >>> root.displayNames.languages = ['en', 'de']
      >>> root.displayNames.keys = ['foo', 'bar']

      >>> locale = LocaleInheritanceStub(nextLocale=root)
      >>> locale.displayNames = LocaleDisplayNames()
      >>> locale.displayNames.keys = ['fu', 'bahr']

    Here you can see the inheritance in action::

      >>> locale.displayNames.languages
      ['en', 'de']
      >>> locale.displayNames.keys
      ['fu', 'bahr']
    """


@implementer(ILocaleTimeZone)
class LocaleTimeZone(object):
    """Specifies one of the timezones of a specific locale.

    The attributes of this class are not inherited, since all timezone
    information is always provided together.

    Example::

      >>> tz = LocaleTimeZone('Europe/Berlin')
      >>> tz.cities = ['Berlin']
      >>> tz.names = {'standard': ('Mitteleuropaeische Zeit', 'MEZ'),
      ...             'daylight': ('Mitteleuropaeische Sommerzeit', 'MESZ')}

      >>> tz.type
      'Europe/Berlin'
      >>> tz.cities
      ['Berlin']
    """

    def __init__(self, type):
        """Initialize the object."""
        self.type = type
        self.cities = []
        self.names = {}


@implementer(ILocaleFormat)
class LocaleFormat(object):
    """Specifies one of the format of a specific format length.

    The attributes of this class are not inherited, since all format
    information is always provided together. Note that this information by
    itself is often not useful, since other calendar data is required to use
    the specified pattern for formatting and parsing.
    """

    def __init__(self, type=None):
        """Initialize the object."""
        self.type = type
        self.displayName = u""
        self.pattern = u""


@implementer(ILocaleFormatLength)
class LocaleFormatLength(AttributeInheritance):
    """Specifies one of the format lengths of a specific quantity, like
    numbers, dates, times and datetimes."""


    def __init__(self, type=None):
        """Initialize the object."""
        self.type = type
        self.default = None


@implementer(ILocaleMonthContext)
class LocaleMonthContext(AttributeInheritance):

    def __init__(self, type=None):
        """Initialize the object."""
        self.type = type
        self.default = u"wide"


@implementer(ILocaleDayContext)
class LocaleDayContext(AttributeInheritance):

    def __init__(self, type=None):
        """Initialize the object."""
        self.type = type
        self.default = u"wide"


@implementer(ILocaleCalendar)
class LocaleCalendar(AttributeInheritance):
    """Represents locale data for a calendar, like 'gregorian'.

    This object is particular tricky, since the calendar not only inherits
    from higher-up locales, but also from the specified gregorian calendar
    available for this locale. This was done, since most other calendars have
    different year and era data, but everything else remains the same.

    Example:

    Even though the 'Locale' object has no 'calendar' attribute for real, it
    helps us here to make the example simpler.

      >>> from zope.i18n.locales.tests.test_docstrings import \\
      ...     LocaleInheritanceStub
      >>> root = LocaleInheritanceStub()
      >>> root.calendar = LocaleCalendar('gregorian')
      >>> locale = LocaleInheritanceStub(nextLocale=root)
      >>> locale.calendar = LocaleCalendar('gregorian')

      >>> root.calendar.months = InheritingDictionary(
      ...     {1: (u"January", u"Jan"), 2: (u"February", u"Feb")})
      >>> locale.calendar.months = InheritingDictionary(
      ...     {2: (u"Februar", u"Feb"), 3: (u"Maerz", u"Mrz")})
      >>> locale.calendar.getMonthNames()[:4]
      [u'January', u'Februar', u'Maerz', None]
      >>> locale.calendar.getMonthTypeFromName(u"January")
      1
      >>> locale.calendar.getMonthTypeFromName(u"Februar")
      2
      >>> locale.calendar.getMonthAbbreviations()[:4]
      [u'Jan', u'Feb', u'Mrz', None]
      >>> locale.calendar.getMonthTypeFromAbbreviation(u"Jan")
      1
      >>> locale.calendar.getMonthTypeFromAbbreviation(u"Mrz")
      3

      >>> root.calendar.days = InheritingDictionary(
      ...     {1: (u"Monday", u"Mon"), 2: (u"Tuesday", u"Tue")})
      >>> locale.calendar.days = InheritingDictionary(
      ...     {2: (u"Dienstag", u"Die"), 3: (u"Mittwoch", u"Mit")})
      >>> locale.calendar.getDayNames()[:4]
      [u'Monday', u'Dienstag', u'Mittwoch', None]
      >>> locale.calendar.getDayTypeFromName(u"Monday")
      1
      >>> locale.calendar.getDayTypeFromName(u"Dienstag")
      2
      >>> locale.calendar.getDayAbbreviations()[:4]
      [u'Mon', u'Die', u'Mit', None]
      >>> locale.calendar.getDayTypeFromAbbreviation(u"Mon")
      1
      >>> locale.calendar.getDayTypeFromAbbreviation(u"Die")
      2

      >>> root.calendar.week = {'firstDay': 1}
      >>> locale.calendar.getFirstWeekDayName()
      u'Monday'

    Let's test the direct attribute access as well.

      >>> root.am = u"AM"
      >>> root.pm = u"PM"
      >>> locale.pm = u"nachm."
      >>> locale.pm
      u'nachm.'
      >>> locale.am
      u'AM'

    Note that ``isWeekend`` is not implemented:

      >>> locale.calendar.isWeekend(object())
      False
      >>> locale.calendar.isWeekend(None)
      False
      >>> locale.calendar.isWeekend('anything')
      False
    """

    def __init__(self, type):
        """Initialize the object."""
        self.type = type

    def getMonthNames(self):
        """See zope.i18n.interfaces.ILocaleCalendar"""
        return [self.months.get(type, (None, None))[0] for type in range(1, 13)]

    def getMonthTypeFromName(self, name):
        """See zope.i18n.interfaces.ILocaleCalendar"""
        for item in self.months.items():
            if item[1][0] == name:
                return item[0]

    def getMonthAbbreviations(self):
        """See zope.i18n.interfaces.ILocaleCalendar"""
        return [self.months.get(type, (None, None))[1] for type in range(1, 13)]

    def getMonthTypeFromAbbreviation(self, abbr):
        """See zope.i18n.interfaces.ILocaleCalendar"""
        for item in self.months.items():
            if item[1][1] == abbr:
                return item[0]

    def getDayNames(self):
        """See zope.i18n.interfaces.ILocaleCalendar"""
        return [self.days.get(type, (None, None))[0] for type in range(1, 8)]

    def getDayTypeFromName(self, name):
        """See zope.i18n.interfaces.ILocaleCalendar"""
        for item in self.days.items():
            if item[1][0] == name:
                return item[0]

    def getDayAbbreviations(self):
        """See zope.i18n.interfaces.ILocaleCalendar"""
        return [self.days.get(type, (None, None))[1] for type in range(1, 8)]

    def getDayTypeFromAbbreviation(self, abbr):
        """See zope.i18n.interfaces.ILocaleCalendar"""
        for item in self.days.items():
            if item[1][1] == abbr:
                return item[0]

    def isWeekend(self, datetime):
        """See zope.i18n.interfaces.ILocaleCalendar"""
        # TODO: Implement this method
        return False

    def getFirstWeekDayName(self):
        """See zope.i18n.interfaces.ILocaleCalendar"""
        firstDayNumber = self.week['firstDay']
        return self.days[firstDayNumber][0]


@implementer(ILocaleDates)
class LocaleDates(AttributeInheritance):
    """Simple ILocaleDates implementation that can inherit data from other
    locales.

    Examples::

      >>> from zope.i18n.tests.test_formats import LocaleCalendarStub as Stub
      >>> from datetime import datetime, date, time
      >>> dates = LocaleDates()
      >>> cal = LocaleCalendar('gregorian')
      >>> cal.months = Stub.months
      >>> cal.days = Stub.days
      >>> cal.am = Stub.am
      >>> cal.pm = Stub.pm
      >>> cal.eras = Stub.eras
      >>> cal.week = {'firstDay': 1, 'minDays': 1}
      >>> dates.calendars = {'gregorian': cal}

    Setting up and accessing date format through a specific length
    (very common scenario)::

      >>> fulllength = LocaleFormatLength()
      >>> format = LocaleFormat()
      >>> format.pattern = u"EEEE, d. MMMM yyyy"
      >>> fulllength.formats = {None: format}

      >>> mediumlength = LocaleFormatLength()
      >>> format = LocaleFormat()
      >>> format.pattern = u"dd.MM.yyyy"
      >>> mediumlength.formats = {None: format}

      >>> cal.dateFormats = {'full': fulllength, 'medium': mediumlength}
      >>> cal.defaultDateFormat = 'medium'

      >>> formatter = dates.getFormatter('date')
      >>> formatter.format(date(2004, 2, 4))
      u'04.02.2004'

      >>> formatter = dates.getFormatter('date', length='full')
      >>> formatter.format(date(2004, 2, 4))
      u'Mittwoch, 4. Februar 2004'

    Let's also test the time formatter::

      >>> fulllength = LocaleFormatLength()
      >>> format = LocaleFormat()
      >>> format.pattern = u"H:mm' Uhr 'z"
      >>> fulllength.formats = {None: format}

      >>> mediumlength = LocaleFormatLength()
      >>> format = LocaleFormat()
      >>> format.pattern = u"HH:mm:ss"
      >>> mediumlength.formats = {None: format}

      >>> cal.timeFormats = {'full': fulllength, 'medium': mediumlength}
      >>> cal.defaultTimeFormat = 'medium'

      >>> formatter = dates.getFormatter('time')
      >>> formatter.format(time(12, 15, 00))
      u'12:15:00'

      >>> formatter = dates.getFormatter('time', length='full')
      >>> formatter.format(time(12, 15, 00))
      u'12:15 Uhr +000'

    The datetime formatter is a bit special, since it is constructed from
    the other two::

      >>> length = LocaleFormatLength()
      >>> format = LocaleFormat()
      >>> format.pattern = u"{1} {0}"
      >>> length.formats = {None: format}
      >>> cal.dateTimeFormats = {None: length}

      >>> formatter = dates.getFormatter('dateTime')
      >>> formatter.format(datetime(2004, 2, 4, 12, 15, 00))
      u'04.02.2004 12:15:00'

      >>> formatter = dates.getFormatter('dateTime', length='full')
      >>> formatter.format(datetime(2004, 2, 4, 12, 15, 00))
      u'Mittwoch, 4. Februar 2004 12:15 Uhr +000'

    Finally, we'll test some invalid input::

      >>> dates.getFormatter('timeDate')
      Traceback (most recent call last):
      ValueError: Invalid category: timeDate

      >>> dates.getFormatter('date', length='superlong')
      Traceback (most recent call last):
      ValueError: Invalid format length: superlong

      >>> dates.getFormatter('date', calendar='irish-catholic')
      Traceback (most recent call last):
      ValueError: Invalid calendar: irish-catholic

    """

    def getFormatter(self, category, length=None, name=None,
                     calendar=u"gregorian"):
        """See zope.i18n.interfaces.locales.ILocaleDates"""
        if category not in (u"date", u"time", u"dateTime"):
            raise ValueError('Invalid category: %s' % category)
        if calendar not in (u"gregorian", u"arabic", u"chinese",
                            u"civil-arabic", u"hebrew", u"japanese",
                            u"thai-buddhist"):
            raise ValueError('Invalid calendar: %s' % calendar)
        if length not in (u"short", u"medium", u"long", u"full", None):
            raise ValueError('Invalid format length: %s' % length)

        cal = self.calendars[calendar]

        formats = getattr(cal, category+'Formats')
        if length is None:
            length = getattr(
                cal,
                'default'+category[0].upper()+category[1:]+'Format',
                list(formats.keys())[0])

        # 'datetime' is always a bit special; we often do not have a length
        # specification, but we need it for looking up the date and time
        # formatters
        if category == 'dateTime':
            formatLength = formats.get(length, formats[None])
        else:
            formatLength = formats[length]

        if name is None:
            name = formatLength.default

        format = formatLength.formats[name]
        pattern = format.pattern

        if category == 'dateTime':
            date_pat = self.getFormatter(
                'date', length, name, calendar).getPattern()
            time_pat = self.getFormatter(
                'time', length, name, calendar).getPattern()
            pattern = pattern.replace('{1}', date_pat)
            pattern = pattern.replace('{0}', time_pat)

        return DateTimeFormat(pattern, cal)


@implementer(ILocaleCurrency)
class LocaleCurrency(object):
    """Simple implementation of ILocaleCurrency without inheritance support,
    since it is not needed for a single currency."""

    def __init__(self, type):
        """Initialize object."""
        self.type = type
        self.symbol = None
        self.symbolChoice = False
        self.displayName = None


@implementer(ILocaleNumbers)
class LocaleNumbers(AttributeInheritance):
    """Implementation of ILocaleCurrency including inheritance support.

    Examples::

      >>> numbers = LocaleNumbers()
      >>> numbers.symbols = {
      ...     'decimal': ',', 'group': '.', 'list': ';', 'percentSign': '%',
      ...     'nativeZeroDigit': '0', 'patternDigit': '#', 'plusSign': '+',
      ...     'minusSign': '-', 'exponential': 'E', 'perMille': 'o/oo',
      ...     'infinity': 'oo', 'nan': 'N/A'}

    Setting up and accessing totally unnamed decimal format
    (very common scenario)::

      >>> length = LocaleFormatLength()
      >>> format = LocaleFormat()
      >>> format.pattern = u"#,##0.###;-#,##0.###"
      >>> length.formats = {None: format}
      >>> numbers.decimalFormats = {None: length}
      >>> formatter = numbers.getFormatter('decimal')
      >>> formatter.format(3.4)
      u'3,4'
      >>> formatter.format(-3.4567)
      u'-3,457'
      >>> formatter.format(3210.4)
      u'3.210,4'

    Setting up and accessing scientific formats with named format lengths::

      >>> longlength = LocaleFormatLength('long')
      >>> format = LocaleFormat()
      >>> format.pattern = u"0.000###E+00"
      >>> longlength.formats = {None: format}
      >>> mediumlength = LocaleFormatLength('long')
      >>> format = LocaleFormat()
      >>> format.pattern = u"0.00##E+00"
      >>> mediumlength.formats = {None: format}
      >>> numbers.scientificFormats = {'long': longlength,
      ...                              'medium': mediumlength}
      >>> numbers.defaultScientificFormat = 'long'
      >>> formatter = numbers.getFormatter('scientific')
      >>> formatter.format(1234.5678)
      u'1,234568E+03'
      >>> formatter = numbers.getFormatter('scientific', 'medium')
      >>> formatter.format(1234.5678)
      u'1,2346E+03'

    Setting up and accessing percent formats with named format lengths
    and format names::

      >>> longlength = LocaleFormatLength('long')
      >>> fooformat = LocaleFormat()
      >>> fooformat.pattern = u"0.##0%"
      >>> barformat = LocaleFormat()
      >>> barformat.pattern = u"0%"
      >>> longlength.formats = {None: fooformat, 'bar': barformat}
      >>> numbers.percentFormats = {'long': longlength}
      >>> numbers.defaultPercentFormat = 'long'
      >>> formatter = numbers.getFormatter('percent')
      >>> formatter.format(123.45678)
      u'123,457%'
      >>> formatter = numbers.getFormatter('percent', name='bar')
      >>> formatter.format(123.45678)
      u'123%'

    ...using a default name::

      >>> numbers.percentFormats['long'].default = 'bar'
      >>> formatter = numbers.getFormatter('percent')
      >>> formatter.format(123.45678)
      u'123%'

    """

    def getFormatter(self, category, length=None, name=None):
        """See zope.i18n.interfaces.locales.ILocaleNumbers"""
        assert category in (u"decimal", u"percent", u"scientific", u"currency")
        assert length in (u"short", u"medium", u"long", u"full", None)

        formats = getattr(self, category + 'Formats')
        if length is None:
            length = getattr(
                self,
                'default' + category[0].upper() + category[1:] + 'Format',
                list(formats.keys())[0])
        formatLength = formats[length]

        if name is None:
            name = formatLength.default

        format = formatLength.formats[name]

        return NumberFormat(format.pattern, self.symbols)


@implementer(ILocaleOrientation)
class LocaleOrientation(AttributeInheritance):
    """Implementation of ILocaleOrientation
    """

@implementer(ILocale)
class Locale(AttributeInheritance):
    """Implementation of the ILocale interface."""

    def __init__(self, id):
        self.id = id

    def getLocaleID(self):
        """
        Return the locale id.

        Example::

            >>> lid = LocaleIdentity('en', 'latin', 'US', 'POSIX')
            >>> locale = Locale(lid)
            >>> locale.getLocaleID()
            'en_latin_US_POSIX'

            >>> lid = LocaleIdentity('en', 'latin')
            >>> locale = Locale(lid)
            >>> locale.getLocaleID()
            'en_latin'

            >>> lid = LocaleIdentity()
            >>> locale = Locale(lid)
            >>> locale.getLocaleID()
            ''

        """
        id = self.id
        pieces = [x for x in
                  (id.language, id.script, id.territory, id.variant)
                  if x]
        id_string = '_'.join(pieces)
        # TODO: What about keys??? Where do I get this info from?
        # Notice that 'pieces' is always empty.
        pieces = [key + '=' + type for (key, type) in ()]
        assert not pieces
        if pieces: # pragma: no cover
            id_string += '@' + ','.join(pieces)
        return id_string

    def getInheritedSelf(self):
        """See zope.i18n.interfaces.locales.ILocaleInheritance

        This is the really interesting method that looks up the next (more
        general) Locale object. This is used in case this locale object does
        not have the required information.

        This method works closely with with LocaleProvider.
        """
        language = self.id.language
        territory = self.id.territory
        variant = self.id.variant
        if variant is not None:
            return locales.getLocale(language, territory, None)
        elif territory is not None:
            return locales.getLocale(language, None, None)
        elif language is not None:
            return locales.getLocale(None, None, None)
        else:
            # Well, this is bad; we are already at the root locale
            raise NoParentException('Cannot find a more general locale.')
