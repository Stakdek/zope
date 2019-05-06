##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""A utility module for content-type handling.
"""
from __future__ import print_function
import re
import os.path
import mimetypes

find_binary = re.compile(b'[\0-\7]').search


def text_type(s):
    """
    Given an unnamed piece of data, try to guess its content type.

    Detects HTML, XML, and plain text.

    :return: A MIME type string such as 'text/html'.
    :rtype: str

    :param bytes s: The binary data to examine.
    """
    # at least the maximum length of any tags we look for
    max_tags = 14
    s2 = s.strip()[:max_tags].lower()

    if len(s2) == max_tags:
        if s2.startswith(b'<html>'):
            return 'text/html'

        if s2.startswith(b'<!doctype html'):
            return 'text/html'

        # what about encodings??
        if s2.startswith(b'<?xml'):
            return 'text/xml'

    # we also recognize small snippets of HTML - the closing tag might be
    # anywhere, even at the end of
    if b'</' in s:
        return 'text/html'

    return 'text/plain'


def guess_content_type(name='', body=b'', default=None):
    """
    Given a named piece of content, try to guess its content type.

    The implementation relies on the :mod:`mimetypes` standard Python module,
    the :func:`text_type` function also defined in this module, and a simple
    heuristic for detecting binary data.

    :return: A tuple of ``(type, encoding)`` like :func:`mimetypes.guess_type`.

    :keyword str name: The file name for the content. This is given priority
       when guessing the type.
    :keyword bytes body: The binary data of the content.
    :keyword str default: If given, and no content type can be guessed, this
       will be returned as the ``type`` portion.
    """
    # Attempt to determine the content type (and possibly
    # content-encoding) based on an an object's name and
    # entity body.
    type, enc = mimetypes.guess_type(name)
    if type is None:
        if body:
            if find_binary(body) is not None:
                type = default or 'application/octet-stream'
            else:
                type = (default or text_type(body)
                        or 'text/x-unknown-content-type')
        else:
            type = default or 'text/x-unknown-content-type'

    return type.lower(), enc.lower() if enc else None


def add_files(filenames):
    """
    Add the names of MIME type map files to the standard :mod:`mimetypes` module.

    MIME type map files are used for detecting the MIME type of some content
    based on the content's filename extension.

    The files should be formatted similarly to the 'mime.types' file
    included in this package.  Each line specifies a MIME type and the
    file extensions that imply that MIME type.  Here are some sample lines::

      text/css                        css
      text/plain                      bat c h pl ksh
      text/x-vcard                    vcf
    """
    # Make sure the additional files are either loaded or scheduled to
    # be loaded:
    if mimetypes.inited:
        # Re-initialize the mimetypes module, loading additional files
        mimetypes.init(filenames)
    else:
        # Tell the mimetypes module about the additional files so
        # when it is initialized, it will pick up all of them, in
        # the right order.
        mimetypes.knownfiles.extend(filenames)


# Provide definitions shipped as part of Zope:
here = os.path.dirname(os.path.abspath(__file__))
add_files([os.path.join(here, "mime.types")])


def main():
    items = mimetypes.types_map.items()
    items = sorted(items)
    for item in items:
        print("%s:\t%s" % item)
