##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
import unittest
import sys

# we have a lot of "foo" and "bar"
# pylint:disable=blacklisted-name
# pylint:disable=protected-access

# for sorting objects that are sortable but do not have any other attributes
# or string-like behavior
class _Broken(object):
    def __lt__(self, other):
        return True
    def __eq__(self, other):
        return other is self

class _OK(object):
    def __init__(self, _id):
        self.id = _id

class Test_sort(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.sequencesort.ssort import sort
        return sort(*args, **kw)

    def test_w_2_tuples(self):
        TUPLES = [('b', 'Bharney'), ('a', 'Phred')]
        self.assertEqual(self._callFUT(TUPLES), sorted(TUPLES))

    def test_w_attributes(self):
        class Foo(object):
            def __init__(self, bar):
                self.bar = bar
        TO_SORT = [Foo('b'), Foo('a'), Foo('c')]
        result = self._callFUT(TO_SORT, (('bar',),))
        self.assertEqual([x.bar for x in result], ['a', 'b', 'c'])

    def test_w_attributes_nocase(self):
        class Foo(object):
            def __init__(self, bar):
                self.bar = bar
        TO_SORT = [Foo('b'), Foo('A'), Foo('C')]
        result = self._callFUT(TO_SORT, (('bar', 'nocase'),))
        self.assertEqual([x.bar for x in result], ['A', 'b', 'C'])

    def test_w_attributes_strcoll_nocase(self):
        class Foo(object):
            def __init__(self, bar):
                self.bar = bar
        TO_SORT = [Foo('b'), Foo('A'), Foo('C')]
        result = self._callFUT(TO_SORT, (('bar', 'strcoll_nocase'),))
        self.assertEqual([x.bar for x in result], ['A', 'b', 'C'])

    def test_w_attributes_missing(self):
        class Foo(object):
            def __init__(self, bar):
                self.bar = bar
        TO_SORT = [Foo('b'), Foo('a'), Foo('c'), object()]
        result = self._callFUT(TO_SORT, (('bar',),))
        self.assertEqual([getattr(x, 'bar', 'ZZZ') for x in result],
                         ['ZZZ', 'a', 'b', 'c'])

    def test_w_multi_attributes(self):
        class Foo(object):
            def __init__(self, bar, baz):
                self.bar = bar
                self.baz = baz
        TO_SORT = [Foo('b', 'q'), Foo('a', 'r'), Foo('c', 's'), Foo('a', 'p')]
        result = self._callFUT(TO_SORT, (('bar',), ('baz',)))
        self.assertEqual([(x.bar, x.baz) for x in result],
                         [('a', 'p'), ('a', 'r'), ('b', 'q'), ('c', 's')])

    def test_w_multi_attributes_nocase(self):
        class Foo(object):
            def __init__(self, bar, baz):
                self.bar = bar
                self.baz = baz
        TO_SORT = [Foo('b', 'q'), Foo('a', 'R'), Foo('c', 's'), Foo('a', 'p')]
        result = self._callFUT(TO_SORT, (('bar',), ('baz', 'nocase'),))
        self.assertEqual([(x.bar, x.baz) for x in result],
                         [('a', 'p'), ('a', 'R'), ('b', 'q'), ('c', 's')])

    def test_w_multi_attributes_missing(self):
        class Foo(object):
            def __init__(self, bar, baz):
                self.bar = bar
                self.baz = baz
        TO_SORT = [Foo('b', 'q'), Foo('a', 'r'), object(), Foo('a', 'p')]
        result = self._callFUT(TO_SORT, (('bar',), ('baz',)))
        self.assertEqual([(getattr(x, 'bar', 'ZZZ'), getattr(x, 'baz', 'YYY'))
                          for x in result],
                         [('ZZZ', 'YYY'), ('a', 'p'), ('a', 'r'), ('b', 'q')])

    def test_w_non_basictype_key(self):
        from zope.sequencesort.ssort import cmp as compare
        class Qux(object):
            def __init__(self, spam):
                self._spam = spam
            def __lt__(self, other):
                return compare(self._spam, other._spam) < 0
        class Foo(object):
            def __init__(self, bar):
                self.bar = Qux(bar)
        TO_SORT = [Foo('b'), Foo('a'), Foo('c')]
        result = self._callFUT(TO_SORT, (('bar',),))
        self.assertEqual([x.bar._spam for x in result], ['a', 'b', 'c'])

    def test_w_methods(self):
        class Foo(object):
            def __init__(self, bar):
                self._bar = bar
            def bar(self):
                return self._bar
        TO_SORT = [Foo('b'), Foo('a'), Foo('c')]
        result = self._callFUT(TO_SORT, (('bar',),))
        self.assertEqual([x.bar() for x in result], ['a', 'b', 'c'])

    def test_w_attribute_and_methods(self):
        class Foo(object):
            def __init__(self, bar, baz):
                self._bar = bar
                self.baz = baz
            def bar(self):
                return self._bar
        TO_SORT = [Foo('b', 'Q'), Foo('b', 'p'), Foo('c', 'r')]
        result = self._callFUT(TO_SORT, (('bar',), ('baz', 'nocase')))
        self.assertEqual([(x.bar(), x.baz) for x in result],
                         [('b', 'p'), ('b', 'Q'), ('c', 'r')])

    def test_w_multi_and_non_basictype_key(self):
        from zope.sequencesort.ssort import cmp as compare
        class Qux(object):
            def __init__(self, spam):
                self._spam = spam
            def __lt__(self, other):
                return compare(self._spam, other._spam) < 0
        class Foo(object):
            def __init__(self, bar, baz):
                self.bar = bar
                self.baz = Qux(baz)
        TO_SORT = [Foo('b', 'q'), Foo('b', 'p'), Foo('c', 'r')]
        result = self._callFUT(TO_SORT, (('bar',), ('baz',)))
        self.assertEqual([(x.bar, x.baz._spam) for x in result],
                         [('b', 'p'), ('b', 'q'), ('c', 'r')])


    def test_wo_args(self):
        if sys.version_info[0] < 3: # pragma: no cover
            self.assertEqual(self._callFUT(WORDLIST), RES_WO_ARGS)
        else:
            with self.assertRaises(TypeError):
                self._callFUT(WORDLIST)

    def test_w_only_key(self):
        self.assertEqual(self._callFUT(WORDLIST, (("key",),), mapping=1),
                         RES_W_ONLY_KEY)

    def test_w_key_and_cmp(self):
        self.assertEqual(self._callFUT(WORDLIST, (("key", "cmp"),), mapping=1),
                         RES_W_KEY_AND_CMP)

    def test_w_key_and_cmp_desc(self):
        self.assertEqual(self._callFUT(WORDLIST, (("key", "cmp", "desc"),),
                                       mapping=1), RES_W_KEY_AND_CMP_DESC)

    def test_w_multi_key(self):
        self.assertEqual(self._callFUT(WORDLIST, (("weight",), ("key",)),
                                       mapping=1), RES_W_MULTI_KEY)

    def test_w_multi_key_nocase_desc(self):
        self.assertEqual(
            self._callFUT(WORDLIST, (("weight",),
                                     ("key", "nocase", "desc")), mapping=1),
            RES_W_MULTI_KEY_NOCASE_DESC)

    def test_w_custom_comparator(self):
        from zope.sequencesort.ssort import cmp as compare
        def myCmp(s1, s2):
            return -compare(s1, s2)

        md = {"myCmp" : myCmp}
        self.assertEqual(
            self._callFUT(
                WORDLIST,
                (("weight",), ("key", "myCmp", "desc")),
                md,
                mapping=1
            ),
            RES_W_CUSTOM_COMPARATOR)

    def test_w_custom_comparator_dtml_namespace(self):
        from zope.sequencesort.ssort import cmp as compare
        class Namespace(object):
            def __init__(self, **kw):
                self.__dict__.update(kw)
            def getitem(self, name, default):
                return getattr(self, name, default)

        def myCmp(s1, s2):
            return -compare(s1, s2)

        ns = Namespace(myCmp=myCmp)

        self.assertEqual(
            self._callFUT(
                WORDLIST,
                (("weight",), ("key", "myCmp", "desc")),
                ns,
                mapping=1
            ),
            RES_W_CUSTOM_COMPARATOR)

    def test_w_sort_broken(self):
        _broken = _Broken()
        _ok = _OK('test')
        self.assertEqual(
                self._callFUT([_ok, _broken]),
                [_broken, _ok]
                )

    def test_w_sort_broken_with_key(self):
        _broken = _Broken()
        _ok = _OK('test')
        self.assertEqual(
                self._callFUT([_ok, _broken], [('id',),]),
                [_broken, _ok]
                )
    
    def test_w_sort_broken_with_key_locale(self):
        # testing actual unicode literals to be sorted correctly has the
        # problem that one can not assume that there is any locale actually
        # installed on the system. But we can test if a broken object can be
        # compared with a correct one even for a sorting that assumes stringy
        # behavior
        _broken = _Broken()
        v1 = _OK(u'test')
        self.assertEqual(
                self._callFUT([v1,_broken], [('id','locale',),]),
                [_broken, v1]
                )
        self.assertEqual(
                self._callFUT([_broken,v1], [('id','locale',),]),
                [_broken, v1]
                )

    def test_w_sort_broken_with_key_locale_nocase(self):
        _broken = _Broken()
        v1 = _OK(u'test')
        self.assertEqual(
                self._callFUT([v1,_broken], [('id','locale_nocase',),]),
                [_broken, v1]
                )
        self.assertEqual(
                self._callFUT([_broken,v1], [('id','locale_nocase',),]),
                [_broken, v1]
                )


class Test_make_sortfunctions(unittest.TestCase):

    def _callFUT(self, sortfields, _):
        from zope.sequencesort.ssort import make_sortfunctions
        return make_sortfunctions(sortfields, _)

    def test_w_too_many_values(self):
        self.assertRaises(SyntaxError, self._callFUT,
                          (('bar', 'cmp', 'asc', 'bogus'),), None)

    def test_w_bogus_direction(self):
        self.assertRaises(SyntaxError, self._callFUT,
                          (('bar', 'cmp', 'bogus'),), None)


class SortByTests(unittest.TestCase):
    """Test zope.sequencesort.sort()
    """
    def _getTargetClass(self):
        from zope.sequencesort.ssort import SortBy
        return SortBy

    def _makeOne(self, multisort, sf_list):
        return self._getTargetClass()(multisort, sf_list)

    def _makeField(self, name, _cmp=None, multiplier=1):
        if _cmp is None:
            try:
                _cmp = cmp
            except NameError: #pragma NO COVER Py3k
                def _cmp(lhs, rhs):
                    return int(rhs < lhs) - int(lhs < rhs)
        return (name, _cmp, multiplier)

    def test_invalid_length_single(self):
        sb = self._makeOne(False, [self._makeField('bar')])
        self.assertRaises(ValueError, sb, [], ['b'])
        self.assertRaises(ValueError, sb, ['a'], [])
        self.assertRaises(ValueError, sb, ['a', 'c'], ['b'])
        self.assertRaises(ValueError, sb, ['a'], ['b', 'c'])

    def test_single(self):
        sb = self._makeOne(False, [self._makeField('bar')])
        self.assertEqual(sb(['a', 'q'], ['b', 'p']), -1)
        self.assertEqual(sb(['a', 'q'], ['a', 'r']), 0)
        self.assertEqual(sb(['b', 'p'], ['a', 'q']), 1)

    def test_invalid_length_multiple(self):
        sb = self._makeOne(True, [self._makeField('bar'),
                                  self._makeField('baz', multiplier=-1)])
        self.assertRaises(ValueError, sb,
                          ([], None), (['b', 'c'], None))
        self.assertRaises(ValueError, sb,
                          (['a'], None), (['b', 'c'], None))
        self.assertRaises(ValueError, sb,
                          (['a', 'b', 'c'], None), (['b', 'c'], None))
        self.assertRaises(ValueError, sb,
                          (['a', 'c'], None), ([], None))
        self.assertRaises(ValueError, sb,
                          (['a', 'c'], None), (['b'], None))
        self.assertRaises(ValueError, sb,
                          (['a', 'c'], None), (['b', 'd', 'e'], None))

    def test_multiple(self):
        sb = self._makeOne(True, [self._makeField('bar'),
                                  self._makeField('baz', multiplier=-1)])
        self.assertEqual(sb((['a', 'q'], None), (['b', 'p'], None)), -1)
        self.assertEqual(sb((['a', 'r'], None), (['a', 'q'], None)), -1)
        self.assertEqual(sb((['a', 'q'], None), (['a', 'q'], None)), 0)
        self.assertEqual(sb((['a', 'q'], None), (['a', 'r'], None)), 1)
        self.assertEqual(sb((['b', 'p'], None), (['a', 'q'], None)), 1)

    def test_smallest(self):
        from zope.sequencesort.ssort import _Smallest
        sb = self._makeOne(False, [self._makeField('bar')])
        self.assertEqual(sb(('a', None), (_Smallest, None)), 1)
        self.assertEqual(sb((_Smallest, None), ('a', None)), -1)
        self.assertEqual(sb((_Smallest, None), (_Smallest, None)), 0)

WORDLIST = [
    {"key": "aaa", "word": "AAA", "weight": 1},
    {"key": "bbb", "word": "BBB", "weight": 0},
    {"key": "ccc", "word": "CCC", "weight": 0},
    {"key": "ddd", "word": "DDD", "weight": 0},
    {"key": "eee", "word": "EEE", "weight": 1},
    {"key": "fff", "word": "FFF", "weight": 0},
    {"key": "ggg", "word": "GGG", "weight": 0},
    {"key": "hhh", "word": "HHH", "weight": 0},
    {"key": "iii", "word": "III", "weight": 1},
    {"key": "jjj", "word": "JJJ", "weight": -1},
    {"key": "kkk", "word": "KKK", "weight": 0},
    {"key": "lll", "word": "LLL", "weight": 0},
    {"key": "mmm", "word": "MMM", "weight": 0},
    {"key": "nnn", "word": "NNN", "weight": 0},
    {"key": "ooo", "word": "OOO", "weight": 1},
    {"key": "ppp", "word": "PPP", "weight": 0},
    {"key": "qqq", "word": "QQQ", "weight": -1},
    {"key": "rrr", "word": "RRR", "weight": 0},
    {"key": "sss", "word": "SSS", "weight": 0},
    {"key": "ttt", "word": "TTT", "weight": 0},
    {"key": "uuu", "word": "UUU", "weight": 1},
    {"key": "vvv", "word": "VVV", "weight": 0},
    {"key": "www", "word": "WWW", "weight": 0},
    {"key": "xxx", "word": "XXX", "weight": 0},
    {"key": "yyy", "word": "YYY", "weight": -1},
    {"key": "zzz", "word": "ZZZ", "weight": 0}
]

RES_WO_ARGS = [
    {'weight': 1, 'word': 'AAA', 'key': 'aaa'},
    {'weight': 0, 'word': 'BBB', 'key': 'bbb'},
    {'weight': 0, 'word': 'CCC', 'key': 'ccc'},
    {'weight': 0, 'word': 'DDD', 'key': 'ddd'},
    {'weight': 1, 'word': 'EEE', 'key': 'eee'},
    {'weight': 0, 'word': 'FFF', 'key': 'fff'},
    {'weight': 0, 'word': 'GGG', 'key': 'ggg'},
    {'weight': 0, 'word': 'HHH', 'key': 'hhh'},
    {'weight': 1, 'word': 'III', 'key': 'iii'},
    {'weight': -1, 'word': 'JJJ', 'key': 'jjj'},
    {'weight': 0, 'word': 'KKK', 'key': 'kkk'},
    {'weight': 0, 'word': 'LLL', 'key': 'lll'},
    {'weight': 0, 'word': 'MMM', 'key': 'mmm'},
    {'weight': 0, 'word': 'NNN', 'key': 'nnn'},
    {'weight': 1, 'word': 'OOO', 'key': 'ooo'},
    {'weight': 0, 'word': 'PPP', 'key': 'ppp'},
    {'weight': -1, 'word': 'QQQ', 'key': 'qqq'},
    {'weight': 0, 'word': 'RRR', 'key': 'rrr'},
    {'weight': 0, 'word': 'SSS', 'key': 'sss'},
    {'weight': 0, 'word': 'TTT', 'key': 'ttt'},
    {'weight': 1, 'word': 'UUU', 'key': 'uuu'},
    {'weight': 0, 'word': 'VVV', 'key': 'vvv'},
    {'weight': 0, 'word': 'WWW', 'key': 'www'},
    {'weight': 0, 'word': 'XXX', 'key': 'xxx'},
    {'weight': -1, 'word': 'YYY', 'key': 'yyy'},
    {'weight': 0, 'word': 'ZZZ', 'key': 'zzz'},
]

RES_W_ONLY_KEY = [
    {'weight': 1, 'word': 'AAA', 'key': 'aaa'},
    {'weight': 0, 'word': 'BBB', 'key': 'bbb'},
    {'weight': 0, 'word': 'CCC', 'key': 'ccc'},
    {'weight': 0, 'word': 'DDD', 'key': 'ddd'},
    {'weight': 1, 'word': 'EEE', 'key': 'eee'},
    {'weight': 0, 'word': 'FFF', 'key': 'fff'},
    {'weight': 0, 'word': 'GGG', 'key': 'ggg'},
    {'weight': 0, 'word': 'HHH', 'key': 'hhh'},
    {'weight': 1, 'word': 'III', 'key': 'iii'},
    {'weight': -1, 'word': 'JJJ', 'key': 'jjj'},
    {'weight': 0, 'word': 'KKK', 'key': 'kkk'},
    {'weight': 0, 'word': 'LLL', 'key': 'lll'},
    {'weight': 0, 'word': 'MMM', 'key': 'mmm'},
    {'weight': 0, 'word': 'NNN', 'key': 'nnn'},
    {'weight': 1, 'word': 'OOO', 'key': 'ooo'},
    {'weight': 0, 'word': 'PPP', 'key': 'ppp'},
    {'weight': -1, 'word': 'QQQ', 'key': 'qqq'},
    {'weight': 0, 'word': 'RRR', 'key': 'rrr'},
    {'weight': 0, 'word': 'SSS', 'key': 'sss'},
    {'weight': 0, 'word': 'TTT', 'key': 'ttt'},
    {'weight': 1, 'word': 'UUU', 'key': 'uuu'},
    {'weight': 0, 'word': 'VVV', 'key': 'vvv'},
    {'weight': 0, 'word': 'WWW', 'key': 'www'},
    {'weight': 0, 'word': 'XXX', 'key': 'xxx'},
    {'weight': -1, 'word': 'YYY', 'key': 'yyy'},
    {'weight': 0, 'word': 'ZZZ', 'key': 'zzz'},
]

RES_W_KEY_AND_CMP = [
    {'weight': 1, 'word': 'AAA', 'key': 'aaa'},
    {'weight': 0, 'word': 'BBB', 'key': 'bbb'},
    {'weight': 0, 'word': 'CCC', 'key': 'ccc'},
    {'weight': 0, 'word': 'DDD', 'key': 'ddd'},
    {'weight': 1, 'word': 'EEE', 'key': 'eee'},
    {'weight': 0, 'word': 'FFF', 'key': 'fff'},
    {'weight': 0, 'word': 'GGG', 'key': 'ggg'},
    {'weight': 0, 'word': 'HHH', 'key': 'hhh'},
    {'weight': 1, 'word': 'III', 'key': 'iii'},
    {'weight': -1, 'word': 'JJJ', 'key': 'jjj'},
    {'weight': 0, 'word': 'KKK', 'key': 'kkk'},
    {'weight': 0, 'word': 'LLL', 'key': 'lll'},
    {'weight': 0, 'word': 'MMM', 'key': 'mmm'},
    {'weight': 0, 'word': 'NNN', 'key': 'nnn'},
    {'weight': 1, 'word': 'OOO', 'key': 'ooo'},
    {'weight': 0, 'word': 'PPP', 'key': 'ppp'},
    {'weight': -1, 'word': 'QQQ', 'key': 'qqq'},
    {'weight': 0, 'word': 'RRR', 'key': 'rrr'},
    {'weight': 0, 'word': 'SSS', 'key': 'sss'},
    {'weight': 0, 'word': 'TTT', 'key': 'ttt'},
    {'weight': 1, 'word': 'UUU', 'key': 'uuu'},
    {'weight': 0, 'word': 'VVV', 'key': 'vvv'},
    {'weight': 0, 'word': 'WWW', 'key': 'www'},
    {'weight': 0, 'word': 'XXX', 'key': 'xxx'},
    {'weight': -1, 'word': 'YYY', 'key': 'yyy'},
    {'weight': 0, 'word': 'ZZZ', 'key': 'zzz'},
]

RES_W_KEY_AND_CMP_DESC = [
    {'weight': 0, 'word': 'ZZZ', 'key': 'zzz'},
    {'weight': -1, 'word': 'YYY', 'key': 'yyy'},
    {'weight': 0, 'word': 'XXX', 'key': 'xxx'},
    {'weight': 0, 'word': 'WWW', 'key': 'www'},
    {'weight': 0, 'word': 'VVV', 'key': 'vvv'},
    {'weight': 1, 'word': 'UUU', 'key': 'uuu'},
    {'weight': 0, 'word': 'TTT', 'key': 'ttt'},
    {'weight': 0, 'word': 'SSS', 'key': 'sss'},
    {'weight': 0, 'word': 'RRR', 'key': 'rrr'},
    {'weight': -1, 'word': 'QQQ', 'key': 'qqq'},
    {'weight': 0, 'word': 'PPP', 'key': 'ppp'},
    {'weight': 1, 'word': 'OOO', 'key': 'ooo'},
    {'weight': 0, 'word': 'NNN', 'key': 'nnn'},
    {'weight': 0, 'word': 'MMM', 'key': 'mmm'},
    {'weight': 0, 'word': 'LLL', 'key': 'lll'},
    {'weight': 0, 'word': 'KKK', 'key': 'kkk'},
    {'weight': -1, 'word': 'JJJ', 'key': 'jjj'},
    {'weight': 1, 'word': 'III', 'key': 'iii'},
    {'weight': 0, 'word': 'HHH', 'key': 'hhh'},
    {'weight': 0, 'word': 'GGG', 'key': 'ggg'},
    {'weight': 0, 'word': 'FFF', 'key': 'fff'},
    {'weight': 1, 'word': 'EEE', 'key': 'eee'},
    {'weight': 0, 'word': 'DDD', 'key': 'ddd'},
    {'weight': 0, 'word': 'CCC', 'key': 'ccc'},
    {'weight': 0, 'word': 'BBB', 'key': 'bbb'},
    {'weight': 1, 'word': 'AAA', 'key': 'aaa'},
]

RES_W_MULTI_KEY = [
    {'weight': -1, 'word': 'JJJ', 'key': 'jjj'},
    {'weight': -1, 'word': 'QQQ', 'key': 'qqq'},
    {'weight': -1, 'word': 'YYY', 'key': 'yyy'},
    {'weight': 0, 'word': 'BBB', 'key': 'bbb'},
    {'weight': 0, 'word': 'CCC', 'key': 'ccc'},
    {'weight': 0, 'word': 'DDD', 'key': 'ddd'},
    {'weight': 0, 'word': 'FFF', 'key': 'fff'},
    {'weight': 0, 'word': 'GGG', 'key': 'ggg'},
    {'weight': 0, 'word': 'HHH', 'key': 'hhh'},
    {'weight': 0, 'word': 'KKK', 'key': 'kkk'},
    {'weight': 0, 'word': 'LLL', 'key': 'lll'},
    {'weight': 0, 'word': 'MMM', 'key': 'mmm'},
    {'weight': 0, 'word': 'NNN', 'key': 'nnn'},
    {'weight': 0, 'word': 'PPP', 'key': 'ppp'},
    {'weight': 0, 'word': 'RRR', 'key': 'rrr'},
    {'weight': 0, 'word': 'SSS', 'key': 'sss'},
    {'weight': 0, 'word': 'TTT', 'key': 'ttt'},
    {'weight': 0, 'word': 'VVV', 'key': 'vvv'},
    {'weight': 0, 'word': 'WWW', 'key': 'www'},
    {'weight': 0, 'word': 'XXX', 'key': 'xxx'},
    {'weight': 0, 'word': 'ZZZ', 'key': 'zzz'},
    {'weight': 1, 'word': 'AAA', 'key': 'aaa'},
    {'weight': 1, 'word': 'EEE', 'key': 'eee'},
    {'weight': 1, 'word': 'III', 'key': 'iii'},
    {'weight': 1, 'word': 'OOO', 'key': 'ooo'},
    {'weight': 1, 'word': 'UUU', 'key': 'uuu'},
]

RES_W_MULTI_KEY_NOCASE_DESC = [
    {'weight': -1, 'word': 'YYY', 'key': 'yyy'},
    {'weight': -1, 'word': 'QQQ', 'key': 'qqq'},
    {'weight': -1, 'word': 'JJJ', 'key': 'jjj'},
    {'weight': 0, 'word': 'ZZZ', 'key': 'zzz'},
    {'weight': 0, 'word': 'XXX', 'key': 'xxx'},
    {'weight': 0, 'word': 'WWW', 'key': 'www'},
    {'weight': 0, 'word': 'VVV', 'key': 'vvv'},
    {'weight': 0, 'word': 'TTT', 'key': 'ttt'},
    {'weight': 0, 'word': 'SSS', 'key': 'sss'},
    {'weight': 0, 'word': 'RRR', 'key': 'rrr'},
    {'weight': 0, 'word': 'PPP', 'key': 'ppp'},
    {'weight': 0, 'word': 'NNN', 'key': 'nnn'},
    {'weight': 0, 'word': 'MMM', 'key': 'mmm'},
    {'weight': 0, 'word': 'LLL', 'key': 'lll'},
    {'weight': 0, 'word': 'KKK', 'key': 'kkk'},
    {'weight': 0, 'word': 'HHH', 'key': 'hhh'},
    {'weight': 0, 'word': 'GGG', 'key': 'ggg'},
    {'weight': 0, 'word': 'FFF', 'key': 'fff'},
    {'weight': 0, 'word': 'DDD', 'key': 'ddd'},
    {'weight': 0, 'word': 'CCC', 'key': 'ccc'},
    {'weight': 0, 'word': 'BBB', 'key': 'bbb'},
    {'weight': 1, 'word': 'UUU', 'key': 'uuu'},
    {'weight': 1, 'word': 'OOO', 'key': 'ooo'},
    {'weight': 1, 'word': 'III', 'key': 'iii'},
    {'weight': 1, 'word': 'EEE', 'key': 'eee'},
    {'weight': 1, 'word': 'AAA', 'key': 'aaa'},
]

RES_W_CUSTOM_COMPARATOR = [
    {'weight': -1, 'word': 'JJJ', 'key': 'jjj'},
    {'weight': -1, 'word': 'QQQ', 'key': 'qqq'},
    {'weight': -1, 'word': 'YYY', 'key': 'yyy'},
    {'weight': 0, 'word': 'BBB', 'key': 'bbb'},
    {'weight': 0, 'word': 'CCC', 'key': 'ccc'},
    {'weight': 0, 'word': 'DDD', 'key': 'ddd'},
    {'weight': 0, 'word': 'FFF', 'key': 'fff'},
    {'weight': 0, 'word': 'GGG', 'key': 'ggg'},
    {'weight': 0, 'word': 'HHH', 'key': 'hhh'},
    {'weight': 0, 'word': 'KKK', 'key': 'kkk'},
    {'weight': 0, 'word': 'LLL', 'key': 'lll'},
    {'weight': 0, 'word': 'MMM', 'key': 'mmm'},
    {'weight': 0, 'word': 'NNN', 'key': 'nnn'},
    {'weight': 0, 'word': 'PPP', 'key': 'ppp'},
    {'weight': 0, 'word': 'RRR', 'key': 'rrr'},
    {'weight': 0, 'word': 'SSS', 'key': 'sss'},
    {'weight': 0, 'word': 'TTT', 'key': 'ttt'},
    {'weight': 0, 'word': 'VVV', 'key': 'vvv'},
    {'weight': 0, 'word': 'WWW', 'key': 'www'},
    {'weight': 0, 'word': 'XXX', 'key': 'xxx'},
    {'weight': 0, 'word': 'ZZZ', 'key': 'zzz'},
    {'weight': 1, 'word': 'AAA', 'key': 'aaa'},
    {'weight': 1, 'word': 'EEE', 'key': 'eee'},
    {'weight': 1, 'word': 'III', 'key': 'iii'},
    {'weight': 1, 'word': 'OOO', 'key': 'ooo'},
    {'weight': 1, 'word': 'UUU', 'key': 'uuu'},
]


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
