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
"""Batching support tests
"""

class batch(object):
    """Create a sequence batch"""

    def __init__(self, sequence, size, start=0, end=0,
                 orphan=3, overlap=0):

        start = start + 1

        start, end, sz = opt(start, end, size, orphan, sequence)

        self._last = end - 1
        self._first = start - 1

        self._sequence = sequence
        self._size = size
        self._start = start
        self._end = end
        self._orphan = orphan
        self._overlap = overlap

    def previous_sequence(self):
        return self._first

    def next_sequence_end_item(self):
        _start, end, _spam = opt(self._end+1-self._overlap, 0,
                                 self._size, self._orphan, self._sequence)
        return self._sequence[end-1]

    def next_sequence_start_item(self):
        start, _end, _spam = opt(self._end+1-self._overlap, 0,
                                 self._size, self._orphan, self._sequence)
        return self._sequence[start-1]

    def next_sequence(self):
        return self._end < len(self._sequence)
        # try: self._sequence[self._end]
        # except IndexError: return 0
        # else: return 1

    def __getitem__(self, index):
        if index > self._last:
            raise IndexError(index)
        return self._sequence[index + self._first]

def opt(start, end, size, orphan, sequence):
    assert size >= 1
    assert start > 0

    start = len(sequence) if start - 1 >= len(sequence) else start
    assert end <= 0
    end = start + size - 1

    assert end + orphan - 1 < len(sequence)

    return start, end, size
