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
"""Common definitions used by TAL and METAL compilation and transformation.
"""
import re
from zope.tal.interfaces import ITALExpressionErrorInfo
from zope.interface import implementer

#: Version of the specification we implement.
TAL_VERSION = "1.6"

#: URI for XML namespace
XML_NS = "http://www.w3.org/XML/1998/namespace"
#: URI for XML NS declarations
XMLNS_NS = "http://www.w3.org/2000/xmlns/"

#: TAL namespace URI
ZOPE_TAL_NS = "http://xml.zope.org/namespaces/tal"
#: METAL namespace URI
ZOPE_METAL_NS = "http://xml.zope.org/namespaces/metal"
#: I18N namespace URI
ZOPE_I18N_NS = "http://xml.zope.org/namespaces/i18n"

# This RE must exactly match the expression of the same name in the
# zope.i18n.simpletranslationservice module:
NAME_RE = "[a-zA-Z_][-a-zA-Z0-9_]*"

#: Known METAL attributes
KNOWN_METAL_ATTRIBUTES = frozenset([
    "define-macro",
    "extend-macro",
    "use-macro",
    "define-slot",
    "fill-slot",
    ])

#: Known TAL attributes
KNOWN_TAL_ATTRIBUTES = frozenset([
    "define",
    "condition",
    "content",
    "replace",
    "repeat",
    "attributes",
    "on-error",
    "omit-tag",
    "script",
    "tal tag",      # a pseudo attribute that holds the namespace of elements
                    # like <tal:x>, <metal:y>, <i18n:z>
    ])

#: Known I18N attributes
KNOWN_I18N_ATTRIBUTES = frozenset([
    "translate",
    "domain",
    "target",
    "source",
    "attributes",
    "data",
    "name",
    "ignore",
    "ignore-attributes",
    ])

class TALError(Exception):
    """
    A base exception for errors raised by this implementation.
    """

    def __init__(self, msg, position=(None, None)):
        Exception.__init__(self)
        assert msg != ""
        self.msg = msg
        self.lineno = position[0]
        self.offset = position[1]
        self.filename = None

    def setFile(self, filename):
        self.filename = filename

    def __str__(self):
        result = self.msg
        if self.lineno is not None:
            result = result + ", at line %d" % self.lineno
        if self.offset is not None:
            result = result + ", column %d" % (self.offset + 1)
        if self.filename is not None:
            result = result + ', in file %s' % self.filename
        return result

class METALError(TALError):
    """An error parsing on running METAL macros."""

class TALExpressionError(TALError):
    """An error parsing or running a TAL expression."""

class I18NError(TALError):
    """An error parsing a I18N expression."""


@implementer(ITALExpressionErrorInfo)
class ErrorInfo(object):
    """
    Default implementation of :class:`zope.tal.interfaces.ITALExpressionErrorInfo`.
    """

    def __init__(self, err, position=(None, None)):
        if isinstance(err, Exception):
            self.type = err.__class__
            self.value = err
        else:
            self.type = err
            self.value = None
        self.lineno = position[0]
        self.offset = position[1]


_attr_re = re.compile(r"\s*([^\s]+)\s+([^\s].*)\Z", re.S)
_subst_re = re.compile(r"\s*(?:(text|structure)\s+)?(.*)\Z", re.S)

def parseAttributeReplacements(arg, xml):
    attr_dict = {}
    for part in splitParts(arg):
        m = _attr_re.match(part)
        if not m:
            raise TALError("Bad syntax in attributes: %r" % part)
        name, expr = m.groups()
        if not xml:
            name = name.lower()
        if name in attr_dict:
            raise TALError("Duplicate attribute name in attributes: %r" % part)
        attr_dict[name] = expr
    return attr_dict

def parseSubstitution(arg, position=(None, None)):
    m = _subst_re.match(arg)
    if not m:
        raise TALError("Bad syntax in substitution text: %r" % arg, position)
    key, expr = m.groups()
    if not key:
        key = "text"
    return key, expr

def splitParts(arg):
    # Break in pieces at undoubled semicolons and
    # change double semicolons to singles:
    arg = arg.replace(";;", "\0")
    parts = arg.split(';')
    parts = [p.replace("\0", ";") for p in parts]
    if len(parts) > 1 and not parts[-1].strip():
        del parts[-1] # It ended in a semicolon
    return parts

def isCurrentVersion(program):
    version = getProgramVersion(program)
    return version == TAL_VERSION

def isinstance_(ob, kind):
    # Proxy-friendly and faster isinstance_ check for new-style objects
    try:
        return kind in ob.__class__.__mro__
    except AttributeError:
        return False


def getProgramMode(program):
    version = getProgramVersion(program)
    if (version == TAL_VERSION and isinstance_(program[1], tuple)
            and len(program[1]) == 2):
        opcode, mode = program[1]
        if opcode == "mode":
            return mode
    return None

def getProgramVersion(program):
    if (len(program) >= 2
            and isinstance_(program[0], tuple) and len(program[0]) == 2):
        opcode, version = program[0]
        if opcode == "version":
            return version
    return None

_ent1_re = re.compile('&(?![A-Z#])', re.I)
_entch_re = re.compile('&([A-Z][A-Z0-9]*)(?![A-Z0-9;])', re.I)
_entn1_re = re.compile('&#(?![0-9X])', re.I)
_entnx_re = re.compile('&(#X[A-F0-9]*)(?![A-F0-9;])', re.I)
_entnd_re = re.compile('&(#[0-9][0-9]*)(?![0-9;])')

def attrEscape(s):
    """Replace special characters '&<>' by character entities,
    except when '&' already begins a syntactically valid entity."""
    s = _ent1_re.sub('&amp;', s)
    s = _entch_re.sub(r'&amp;\1', s)
    s = _entn1_re.sub('&amp;#', s)
    s = _entnx_re.sub(r'&amp;\1', s)
    s = _entnd_re.sub(r'&amp;\1', s)
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace('"', '&quot;')
    return s

def quote(s):
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return '"%s"' % s
