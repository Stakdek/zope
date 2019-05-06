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
"""Generic Expat-based XML parser base class.

This creates a parser with namespace processing enabled.
"""
import logging

try:
    # Python 2.x
    from urllib import urlopen
except ImportError:
    # Python 3.x
    from urllib.request import urlopen


try:
    unicode
except NameError:
    unicode = str # Python 3.x


class XMLParser(object):
    """
    Parse XML using :mod:`xml.parsers.expat`.
    """

    ordered_attributes = 0

    handler_names = [
        "StartElementHandler",
        "EndElementHandler",
        "ProcessingInstructionHandler",
        "CharacterDataHandler",
        "UnparsedEntityDeclHandler",
        "NotationDeclHandler",
        "StartNamespaceDeclHandler",
        "EndNamespaceDeclHandler",
        "CommentHandler",
        "StartCdataSectionHandler",
        "EndCdataSectionHandler",
        "DefaultHandler",
        "DefaultHandlerExpand",
        "NotStandaloneHandler",
        "ExternalEntityRefHandler",
        "XmlDeclHandler",
        "StartDoctypeDeclHandler",
        "EndDoctypeDeclHandler",
        "ElementDeclHandler",
        "AttlistDeclHandler"
        ]

    def __init__(self, encoding=None):
        self.parser = p = self.createParser(encoding)
        if self.ordered_attributes:
            try:
                self.parser.ordered_attributes = self.ordered_attributes
            except AttributeError:
                logging.warn("TAL.XMLParser: Can't set ordered_attributes")
                self.ordered_attributes = 0
        for name in self.handler_names:
            method = getattr(self, name, None)
            if method is not None:
                try:
                    setattr(p, name, method)
                except AttributeError:
                    logging.error("TAL.XMLParser: Can't set "
                                  "expat handler %s" % name)

    def createParser(self, encoding=None):
        global XMLParseError
        from xml.parsers import expat
        XMLParseError = expat.ExpatError
        return expat.ParserCreate(encoding, ' ')

    def parseFile(self, filename):
        """Parse from the given filename."""
        with open(filename, 'rb') as f:
            self.parseStream(f)

    def parseString(self, s):
        """Parse the given string."""
        if isinstance(s, unicode):
            # Expat cannot deal with unicode strings, only with
            # encoded ones.  Also, its range of encodings is rather
            # limited, UTF-8 is the safest bet here.
            s = s.encode('utf-8')
        self.parser.Parse(s, 1)

    def parseURL(self, url):
        """Parse the given URL."""
        self.parseStream(urlopen(url))

    def parseStream(self, stream):
        """Parse the given stream (open file)."""
        self.parser.ParseFile(stream)

    def parseFragment(self, s, end=0):
        self.parser.Parse(s, end)

    def getpos(self):
        # Apparently ErrorLineNumber and ErrorLineNumber contain the current
        # position even when there was no error.  This contradicts the official
        # documentation[1], but expat.h[2] contains the following definition:
        #
        #   /* For backwards compatibility with previous versions. */
        #   #define XML_GetErrorLineNumber   XML_GetCurrentLineNumber
        #
        # [1] http://python.org/doc/current/lib/xmlparser-objects.html
        # [2] http://cvs.sourceforge.net/viewcvs.py/expat/expat/lib/expat.h
        return (self.parser.ErrorLineNumber, self.parser.ErrorColumnNumber)
