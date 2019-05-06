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
'''Class for reading RDB files'''

import array
import re

from Acquisition import Implicit
from DateTime import DateTime
from ExtensionClass import Base
import six

from Missing import MV
from Record import Record


def parse_text(s):
    if s.find('\\') < 0 and s.find('\\t') < 0 and s.find('\\n') < 0:
        return s
    r = []
    for x in s.split('\\\\'):
        x = '\n'.join(x.split('\\n'))
        r.append('\t'.join(x.split('\\t')))
    return '\\'.join(r)


if six.PY3:
    long = int

Parsers = {'n': float,
           'i': int,
           'l': long,
           'd': DateTime,
           't': parse_text}


class SQLAlias(Base):

    def __init__(self, name):
        self._n = name

    def __of__(self, parent):
        return getattr(parent, self._n)


class NoBrains(Base):
    pass


class DatabaseResults(object):
    """Class for reading RDB files
    """
    _index = None

    # We need to allow access to not-explicitly-protected
    # individual record objects contained in the result.
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, file, brains=NoBrains, parent=None, zbrains=NoBrains):

        self._file = file
        readline = file.readline
        line = readline()
        self._parent = parent

        while line and line.find('#') != -1:
            line = readline()

        line = line[:-1]
        if line and line[-1:] in '\r\n':
            line = line[:-1]
        self._names = names = [name.strip() for name in line.split('\t')]
        if not names:
            raise ValueError('No column names')

        aliases = []
        self._schema = schema = {}
        i = 0
        for name in names:
            if not name:
                raise ValueError('Empty column name, %s' % name)

            if name in schema:
                raise ValueError('Duplicate column name, %s' % name)

            schema[name] = i
            i = i + 1

            n = name.lower()
            if n != name:
                aliases.append((n, SQLAlias(name)))

            n = name.upper()
            if n != name:
                aliases.append((n, SQLAlias(name)))

        self._nv = nv = len(names)
        line = readline()
        line = line[:-1]
        if line[-1:] in '\r\n':
            line = line[:-1]

        self._defs = defs = [_def.strip() for _def in line.split('\t')]

        if not defs:
            raise ValueError('No column definitions')

        if len(defs) != nv:
            raise ValueError(
                """The number of column names and the number of column
                definitions are different.""")

        i = 0
        self._parsers = parsers = []
        defre = re.compile(r'([0-9]*)([a-zA-Z])?')
        self._data_dictionary = dd = {}
        self.__items__ = items = []

        for _def in defs:
            if not _def:
                raise ValueError('Empty column definition for %s' % names[i])

            mo = defre.match(_def)
            if mo is None:
                err = 'Invalid column definition for, %s, for %s' % (
                      _def, names[i])
                raise ValueError(err)

            type = mo.group(2).lower()
            width = mo.group(1)

            if width:
                width = int(width)
            else:
                width = 8

            parser = Parsers.get(type, str)

            name = names[i]
            d = {'name': name, 'type': type, 'width': width, 'parser': parser}
            items.append(d)
            dd[name] = d

            parsers.append((i, parser))
            i += 1

        # Create a record class to hold the records.
        names = tuple(names)

        class r(Record, Implicit, brains, zbrains):
            'Result record class'

        for k, v in Record.__dict__.items():
            if k[:2] == '__':
                setattr(r, k, v)

        r.__record_schema__ = schema

        # Add SQL Aliases
        for k, v in aliases:
            if getattr(r, k, self) is self:
                setattr(r, k, v)

        self._class = r

        # OK, we've read meta data, now get line indexes

        pos = file.tell()
        save = self._lines = array.array('i')
        save = save.append
        line = readline()
        while line:
            save(pos)
            pos += len(line)
            line = readline()

    def _searchable_result_columns(self):
        return self.__items__

    def names(self):
        return self._names

    def data_dictionary(self):
        return self._data_dictionary

    def __len__(self):
        return len(self._lines)

    def __getitem__(self, index):
        if index == self._index:
            return self._row
        file = self._file
        file.seek(self._lines[index])
        line = file.readline()
        line = line[:-1]
        if line and line[-1:] in '\r\n':
            line = line[:-1]
        fields = [field.strip() for field in line.split('\t')]
        fields_len = len(fields)
        nv = self._nv
        if fields_len != nv:
            if fields_len < nv:
                fields = fields + [''] * (nv - fields_len)
            else:
                raise ValueError(
                    """The number of items in record %s is invalid
                    <pre>%s\n%s\n%s\n%s</pre>
                    """
                    % (index, ('=' * 40), line, ('=' * 40), fields))
        for i, parser in self._parsers:
            try:
                v = parser(fields[i])
            except Exception:
                if fields[i]:
                    raise ValueError(
                        """Invalid value, %s, for %s in record %s"""
                        % (fields[i], self._names[i], index))
                else:
                    v = MV
            fields[i] = v

        parent = self._parent
        record = self._class(fields, parent)
        self._index = index
        self._row = record
        if parent is None:
            return record
        return record.__of__(parent)


File = DatabaseResults
