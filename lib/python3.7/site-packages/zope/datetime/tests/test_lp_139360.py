import unittest

# The separator character:
s = '-'

# The sets of single digit days and months:
D = [(d, repr(d)) for d in range(1, 10)]
M = [(m, repr(m)) for m in range(1, 10)]

# The sets of double digit days and months:
DD = [(d, dr.rjust(2, '0')) for d, dr in D] + [(d, repr(d)) for d in range(10, 31)]
MM = [(m, mr.rjust(2, '0')) for m, mr in M] + [(m, repr(m)) for m in range(10, 13)]

# The set of years:
YYYY = [(2001, '2001')]

# The sets of mixed-endian date strings (where each string is stored with its component values):
M_D_YYYY   = [((d, m, y), s.join([mr, dr, yr])) for d, dr in  D for m, mr in  M for y, yr in YYYY]
M_DD_YYYY  = [((d, m, y), s.join([mr, dr, yr])) for d, dr in DD for m, mr in  M for y, yr in YYYY]
MM_D_YYYY  = [((d, m, y), s.join([mr, dr, yr])) for d, dr in  D for m, mr in MM for y, yr in YYYY]
MM_DD_YYYY = [((d, m, y), s.join([mr, dr, yr])) for d, dr in DD for m, mr in MM for y, yr in YYYY]

# The sets of big-endian date strings (where each string is stored with its component values):
YYYY_M_D   = [((d, m, y), s.join([yr, mr, dr])) for d, dr in  D for m, mr in  M for y, yr in YYYY]
YYYY_M_DD  = [((d, m, y), s.join([yr, mr, dr])) for d, dr in DD for m, mr in  M for y, yr in YYYY]
YYYY_MM_D  = [((d, m, y), s.join([yr, mr, dr])) for d, dr in  D for m, mr in MM for y, yr in YYYY]
YYYY_MM_DD = [((d, m, y), s.join([yr, mr, dr])) for d, dr in DD for m, mr in MM for y, yr in YYYY]

# The combined sets of mixed- and big-endian date strings:
dates_ME = M_D_YYYY + M_DD_YYYY + MM_D_YYYY + MM_DD_YYYY
dates_BE = YYYY_M_D + YYYY_M_DD + YYYY_MM_D + YYYY_MM_DD

# The set of all date strings:
dates = dates_ME + dates_BE

class LP_139360(unittest.TestCase):

    def _callFUT(self, text):
        from zope.datetime import parse
        return parse(text)


# For each date string, compare the output of the
# parser with the component values of that date:
for i, ((d, m, y), string) in enumerate(dates):
    method_name = 'test_%09d' % i
    def _test(self):
        yp, mp, dp, _, _, _, _ = self._callFUT(string)
        self.assertEqual(y, yp)
        self.assertEqual(m, mp)
        self.assertEqual(d, dp)

    _test.__name__ = method_name
    setattr(LP_139360, method_name, _test)

# Hide the temporary from nose
del _test

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LP_139360),
    ))
