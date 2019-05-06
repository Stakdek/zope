##############################################################################
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""File-system representation interfaces

The interfaces defined here are used for file-system and
file-system-like representations of objects, such as file-system
synchronization, FTP, PUT, and WebDAV.

There are three issues we need to deal with:

* File system representation

    Every object is either a directory or a file.

* Properties

    There are two kinds of properties:

    - Data properties

      Data properties are handled directly by the object implementation.

    - Meta-data properties

      Meta data properties are handled via annotations.

* Completeness

    We must have a complete lossless data representation for file-system
    synchronization. This is achieved through serialization of:

    - All annotations (not just properties), and

    - Extra data.

Strategies for common access mechanisms:

* FTP

    For getting directory info (statish) information:

        - Use Zope DublinCore to get modification times

        - Show as readable if we can access a read method.

        - Show as writable if we can access a write method.

* FTP and WebDAV

    - Treat as a directory if there is an adapter to :class:`IReadDirectory`.
      Treat as a file otherwise.

    - For creating objects:

        - Directories:

          Look for an :class:`IDirectoryFactory` adapter.

        - Files

          First look for a :class:`IFileFactory` adapter with a name that is
          the same as the extention (e.g. ".pt").

          Then look for an unnamed :class:`IFileFactory` adapter.


* File-system synchronization

      Because this must be lossless, we will use class-based adapters
      for this, but we want to make it as easy as possible to use other
      adapters as well.

      For reading, there must be a class adapter to :class:`IReadSync`.  We will
      then apply rules similar to those above.
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope import schema

from zope.interface.common.mapping import IEnumerableMapping
from zope.interface.common.mapping import IItemMapping
from zope.interface.common.mapping import IReadMapping


class IReadFile(Interface):
    """Provide read access to file data
    """

    def read():
        """Return the file data
        """

    def size():
        """Return the data length in bytes.
        """

class IWriteFile(Interface):
    """Provide write access to file data."""

    def write(data):
        """Update the file data
        """

class ICommonFileOperations(Interface):
    """Common file operations used by :class:`IRawReadFile` and :class:`IRawWriteFile`
    """

    mimeType = schema.ASCIILine(
        title=u"File MIME type",
        description=(u"Provided if it makes sense for this file data. "
                     u"May be set prior to writing data to a file that "
                     u"is writeable. It is an error to set this on a "
                     u"file that is not writable."),
        readonly=True,
    )

    encoding = schema.Bool(
        title=u"The encoding that this file uses",
        description=(u"Provided if it makes sense for this file data. "
                     u"May be set prior to writing data to a file that "
                     u"is writeable. It is an error to set this on a "
                     u"file that is not writable."),
        required=False,
    )

    closed = schema.Bool(
        title=u"Is the file closed?",
        required=True,
    )

    name = schema.TextLine(
        title=u"A representative file name",
        description=(u"Provided if it makes sense for this file data. "
                     u"May be set prior to writing data to a file that "
                     u"is writeable. It is an error to set this on a "
                     u"file that is not writable."),
        required=False,
    )

    def seek(offset, whence=None):
        """Seek the file. See Python documentation for :class:`io.IOBase` for
        details.
        """

    def tell():
        """Return the file's current position.
        """

    def close():
        """Close the file. See Python documentation for :class:`io.IOBase` for
        details.
        """

class IRawReadFile(IReadFile, ICommonFileOperations):
    """Specialisation of IReadFile to make it act more like a Python file
    object.
    """

    def read(size=None):
        """Read at most ``size`` bytes of file data. If ``size`` is None,
        return all the file data.
        """

    def readline(size=None):
        """Read one entire line from the file. See Python documentation for
        :class:`io.IOBase` for details.
        """

    def readlines(sizehint=None):
        """Read until EOF using readline() and return a list containing the
        lines thus read. See Python documentation for :class:`io.IOBase` for details.
        """

    def __iter__():
        """Return an iterator for the file.

        Note that unlike a Python standard :class:`file`, this does not necessarily
        have to return data line-by-line if doing so is inefficient.
        """

    def next():
        """Iterator protocol. See Python documentation for :class:`io.IOBase` for
        details.
        """

class IRawWriteFile(IWriteFile, ICommonFileOperations):
    """Specialisation of IWriteFile to make it act more like a Python file
    object.
    """

    def write(data):
        """Write a chunk of data to the file. See Python documentation for
        :class:`io.RawIOBase` for details.
        """

    def writelines(sequence):
        """Write a sequence of strings to the file. See Python documentation
        for :class:`io.IOBase` for details.
        """

    def truncate(size):
        """Truncate the file. See Python documentation for :class:`io.IOBase` for
        details.
        """

    def flush():
        """Flush the file. See Python documentation for :class:`io.IOBase` for details.
        """

class IReadDirectory(IEnumerableMapping, IItemMapping, IReadMapping):
    """Objects that should be treated as directories for reading
    """

class IWriteDirectory(Interface):
    """Objects that should be treated as directories for writing
    """

    def __setitem__(name, object):
        """Add the given `object` to the directory under the given name."""

    def __delitem__(name):
        """Delete the named object from the directory."""


class IDirectoryFactory(Interface):
    """Factory for :class:`IReadDirectory`/:class:`IWriteDirectory` objects."""

    def __call__(name):
        """Create a directory

        where a directory is an object with adapters to IReadDirectory
        and IWriteDirectory.

        """

class IFileFactory(Interface):
    """Factory for :class:`IReadFile`/:class:`IWriteFile` objects."""

    def __call__(name, content_type, data):
        """Create a file

        where a file is an object with adapters to `IReadFile`
        and `IWriteFile`.

        The file `name`, content `type`, and `data` are provided to help
        create the object.
        """

# TODO: we will add additional interfaces for WebDAV and File-system
# synchronization.
