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
"""Advanced sort support

e.g .Sort(sequence, (("akey", "nocase"), ("anotherkey", "cmp", "desc")))
"""

from functools import cmp_to_key
from locale import strcoll

try:
    cmp = cmp # always put in our namespace; tests import it from here
except NameError:
    def cmp(lhs, rhs): # pylint:disable=redefined-builtin
        return int(rhs < lhs) - int(lhs < rhs)

class _Smallest(object):
    """ Singleton:  sorts below any other value.
    """
    __slots__ = ()
    def __lt__(self, other):
        return True
    def __eq__(self, other):
        return other is self
    def __gt__(self, other):
        return False
_Smallest = _Smallest()



def sort(sequence, sort=(), _=None, mapping=0):
    """Return a sorted copy of 'sequence'.

    :param sequence: is a sequence of objects to be sorted
    :param sort: is a sequence of tuples (key,func,direction)
      that define the sort order:

      - *key* is the name of an attribute to sort the objects by

      - *func* is the name of a comparison function. This parameter is
        optional

        allowed values:

        - "cmp" -- the standard comparison function (default)

        - "nocase" -- case-insensitive comparison

        - "strcoll" or "locale" -- locale-aware string comparison

        - "strcoll_nocase" or "locale_nocase" -- locale-aware case-insensitive
           string comparison

        - "xxx" -- a user-defined comparison function

      - *direction* defines the sort direction for the key (optional).
        (allowed values: "asc" (default) , "desc")
    """
    need_sortfunc = 0

    if sort:
        for s in sort:
            if len(s) > 1: # extended sort if there is reference to...
                # ...comparison function or sort order, even if they are
                # "cmp" and "asc"
                need_sortfunc = 1
                break

    sortfields = sort # multi sort = key1,key2
    multsort = len(sortfields) > 1 # flag: is multiple sort

    if need_sortfunc:
        # prepare the list of functions and sort order multipliers
        sf_list = make_sortfunctions(sortfields, _)

        # clean the mess a bit
        if multsort: # More than one sort key.
            sortfields = [x[0] for x in sf_list]
        else:
            sort = sf_list[0][0]

    elif sort:
        if multsort: # More than one sort key.
            sortfields = [x[0] for x in sort]
        else:
            sort = sort[0][0]

    isort = not sort

    s = []
    for client in sequence:
        k = _Smallest
        if isinstance(client, tuple) and len(client) == 2:
            if isort:
                k = client[0]
            v = client[1]
        else:
            if isort:
                k = client
            v = client

        if sort:
            if multsort: # More than one sort key.
                k = []
                for sk in sortfields:
                    try:
                        if mapping:
                            akey = v[sk]
                        else:
                            akey = getattr(v, sk)
                    except (AttributeError, KeyError):
                        akey = _Smallest
                    else:
                        if not isinstance(akey, BASIC_TYPES):
                            try:
                                akey = akey()
                            except: # pylint:disable=bare-except
                                pass
                    k.append(akey)
            else: # One sort key.
                try:
                    if mapping:
                        k = v[sort]
                    else:
                        k = getattr(v, sort)
                except (AttributeError, KeyError):
                    k = _Smallest
                if not isinstance(k, BASIC_TYPES):
                    try:
                        k = k()
                    except: # pylint:disable=bare-except
                        pass

        s.append((k, client))

    if need_sortfunc:
        by = SortBy(multsort, sf_list)
        s.sort(key=cmp_to_key(by))
    else:
        s.sort()

    return [x[1] for x in s]


SortEx = sort

BASIC_TYPES = (
    type(u''),
    type(b''),
    type(0),
    type(0.0),
    type(()),
    type([]),
    type(None)
)


def nocase(str1, str2):
    return cmp(str1.lower(), str2.lower())


def strcoll_nocase(str1, str2):
    return strcoll(str1.lower(), str2.lower())

_SORT_FUNCTIONS = {
    "cmp": cmp, # builtin
    "nocase": nocase,
    "locale": strcoll,
    "strcoll": strcoll,
    "locale_nocase": strcoll_nocase,
    "strcoll_nocase": strcoll_nocase,
}

def make_sortfunctions(sortfields, _):
    """Accepts a list of sort fields; splits every field, finds comparison
    function. Returns a list of 3-tuples (field, cmp_function, asc_multplier)"""
    # pylint:disable=too-many-branches
    sf_list = []
    for field in sortfields:
        info = list(field)
        i_len = len(info)

        if i_len == 1:
            info.append("cmp")
            info.append("asc")
        elif i_len == 2:
            info.append("asc")
        elif i_len == 3:
            pass
        else:
            raise SyntaxError(
                "sort option: (Key [,sorter_name [,direction]])")

        f_name = info[1]

        # predefined function?
        func = _SORT_FUNCTIONS.get(f_name)
        # no - look it up in the namespace
        if func is None:
            if hasattr(_, 'getitem'):
                # support for zope.documenttemplate.dt_util.TemplateDict
                func = _.getitem(f_name, 0)
            else:
                func = _[f_name]

        sort_order = info[2].lower()

        if sort_order == "asc":
            multiplier = +1
        elif sort_order == "desc":
            multiplier = -1
        else:
            raise SyntaxError(
                "sort direction must be either ASC or DESC")

        sf_list.append((info[0], func, multiplier))

    return sf_list


class SortBy(object):
    def __init__(self, multsort, sf_list):
        self.multsort = multsort
        self.sf_list = sf_list

    def __call__(self, o1, o2):
        n_fields = len(self.sf_list)
        if self.multsort:
            o1 = o1[0] # if multsort - take the first element (key list)
            o2 = o2[0]
            req_len = n_fields
        else:
            req_len = n_fields + 1

        # assert that o1 and o2 are tuples of apropriate length
        if len(o1) != req_len:
            raise ValueError("%s, %d" % (o1, req_len))
        if len(o2) != req_len:
            raise ValueError("%s, %d" % (o2, req_len))

        # now run through the list of functions in sf_list and
        # compare every object in o1 and o2
        for i in range(n_fields):
            # if multsort - we already extracted the key list
            # if not multsort - i is 0, and the 0th element is the key
            c1, c2 = o1[i], o2[i]
            func, multiplier = self.sf_list[i][1:3]
            if c1 is _Smallest and c2 is _Smallest:
                return 0
            if c1 is _Smallest:
                return -1
            elif c2 is _Smallest:
                return 1
            n = func(c1, c2)
            if n:
                return n * multiplier

        # all functions returned 0 - identical sequences
        return 0
