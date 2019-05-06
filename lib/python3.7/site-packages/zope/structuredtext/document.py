##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Structured text document parser
"""
import re

from zope.structuredtext.stletters import letters
from zope.structuredtext.stletters import literal_punc
from zope.structuredtext.stletters import under_punc
from zope.structuredtext.stletters import strongem_punc
from zope.structuredtext.stletters import phrase_delimiters
from zope.structuredtext.stletters import dbl_quoted_punc
from zope.structuredtext.stng import StructuredTextBullet
from zope.structuredtext.stng import StructuredTextDescription
from zope.structuredtext.stng import StructuredTextDocument
from zope.structuredtext.stng import StructuredTextEmphasis
from zope.structuredtext.stng import StructuredTextExample
from zope.structuredtext.stng import StructuredTextImage
from zope.structuredtext.stng import StructuredTextInnerLink
from zope.structuredtext.stng import StructuredTextLink
from zope.structuredtext.stng import StructuredTextNamedLink
from zope.structuredtext.stng import StructuredTextNumbered
from zope.structuredtext.stng import StructuredTextLiteral
from zope.structuredtext.stng import StructuredTextParagraph
from zope.structuredtext.stng import StructuredTextSGML
from zope.structuredtext.stng import StructuredTextSection
from zope.structuredtext.stng import StructuredTextStrong
from zope.structuredtext.stng import StructuredTextTable
from zope.structuredtext.stng import StructuredTextUnderline
from zope.structuredtext.stng import StructuredTextXref
from zope.structuredtext.stng import structurize

string_types = (str,) if bytes is not str else (unicode, str)

__metaclass__ = type


class Document(object):
    """
    Class instance calls [ex.=> x()] require a structured text
    structure. Doc will then parse each paragraph in the structure
    and will find the special structures within each paragraph.
    Each special structure will be stored as an instance. Special
    structures within another special structure are stored within
    the 'top' structure
    EX : '-underline this-' => would be turned into an underline
    instance. '-underline **this**' would be stored as an underline
    instance with a strong instance stored in its string
    """

    paragraph_types = [
        'doc_bullet',
        'doc_numbered',
        'doc_description',
        'doc_header',
        'doc_table',
    ]

    #'doc_inner_link',
    #'doc_named_link',
    #'doc_underline'
    text_types = [
        'doc_literal',
        'doc_sgml',
        'doc_inner_link',
        'doc_named_link',
        'doc_href1',
        'doc_href2',
        'doc_strong',
        'doc_emphasize',
        'doc_underline',
        'doc_sgml',
        'doc_xref',
    ]

    def __call__(self, doc):
        if isinstance(doc, string_types):
            doc = structurize(doc)
            doc.setSubparagraphs(self.color_paragraphs(
                doc.getSubparagraphs()))
        else:
            doc = StructuredTextDocument(self.color_paragraphs(
                doc.getSubparagraphs()))
        return doc

    def parse(self, raw_string, text_type, type=type):

        """
        Parse accepts a raw_string, an expr to test the raw_string,
        and the raw_string's subparagraphs.

        Parse will continue to search through raw_string until
        all instances of expr in raw_string are found.

        If no instances of expr are found, raw_string is returned.
        Otherwise a list of substrings and instances is returned
        """

        tmp = []    # the list to be returned if raw_string is split

        if isinstance(text_type, string_types):
            text_type = getattr(self, text_type)

        while True:
            t = text_type(raw_string)
            if not t:
                break
            #an instance of expr was found
            t, start, end = t

            if start:
                tmp.append(raw_string[:start])

            if isinstance(t, string_types):
                # if we get a string back, add it to text to be parsed
                raw_string = t + raw_string[end:len(raw_string)]
            else:
                if isinstance(t, list):
                    # is we get a list, append it's elements
                    tmp.extend(t)
                else:
                    # normal case, an object
                    tmp.append(t)
                raw_string = raw_string[end:len(raw_string)]

        if not tmp:
            return raw_string # nothing found

        if raw_string:
            tmp.append(raw_string)
        elif len(tmp) == 1:
            return tmp[0]

        return tmp

    def color_text(self, text, types=None):
        """Search the paragraph for each special structure
        """
        if types is None:
            types = self.text_types

        for text_type in types:

            if isinstance(text, string_types):
                text = self.parse(text, text_type)
            elif isinstance(text, list):  #Waaaa
                result = []

                for s in text:
                    if isinstance(s, string_types):
                        s = self.parse(s, text_type)
                        if isinstance(s, list):
                            result.extend(s)
                        else:
                            result.append(s)
                    else:
                        s.setColorizableTexts(
                            [self.color_text(t) for t in s.getColorizableTexts()])
                        result.append(s)
                text = result
            else:
                result = []
                color = self.color_text
                for s in text.getColorizableTexts():
                    color(s, (text_type, ))
                    result.append(s)
                text.setColorizableTexts(result)

        return text

    def color_paragraphs(self, raw_paragraphs,
                         type=type,
                         sequence_types=(tuple, list),
                         sts=string_types):
        result = []
        for paragraph in raw_paragraphs:
            if paragraph.getNodeName() != 'StructuredTextParagraph':
                result.append(paragraph)
                continue

            for pt in self.paragraph_types:
                if isinstance(pt, sts):
                    # grab the corresponding function
                    pt = getattr(self, pt)
                # evaluate the paragraph
                new_paragraphs = pt(paragraph)
                if new_paragraphs:
                    if not isinstance(new_paragraphs, sequence_types):
                        new_paragraphs = (new_paragraphs, )

                    for paragraph in new_paragraphs:
                        subs = self.color_paragraphs(
                            paragraph.getSubparagraphs()
                        )
                        paragraph.setSubparagraphs(subs)
                    break
            else:
                # copy, retain attributes
                atts = getattr(paragraph, '_attributes', [])
                kw = dict([(att, getattr(paragraph, att))
                           for att in atts])
                subs = self.color_paragraphs(paragraph.getSubparagraphs())
                new_paragraphs = StructuredTextParagraph(
                    paragraph.getColorizableTexts()[0], subs, **kw),

            # color the inline StructuredText types
            # for each StructuredTextParagraph
            for paragraph in new_paragraphs:

                if paragraph.getNodeName() == "StructuredTextTable":
#                cells = paragraph.getColumns()
                    text = paragraph.getColorizableTexts()
                    text = [structurize(t) for t in text]
                    text = [self(t) for t in text]
                    text = [t.getSubparagraphs() for t in text]
                    paragraph.setColorizableTexts(text)

                paragraph.setColorizableTexts(
                    [self.color_text(t) for t in paragraph.getColorizableTexts()])
                result.append(paragraph)

        return result

    def doc_table(self, paragraph, expr=re.compile(r'\s*\|[-]+\|').match):
        text = paragraph.getColorizableTexts()[0]
        m = expr(text)

        subs = paragraph.getSubparagraphs()

        if not m:
            return None
        rows = []

        spans = []
        ROWS = []
        COLS = []
        indexes = []
        ignore = []

        TDdivider = re.compile(r"[\-]+").match
        THdivider = re.compile(r"[\=]+").match
        col = re.compile(r'\|').search
        innertable = re.compile(r'\|([-]+|[=]+)\|').search

        text = text.strip()
        rows = text.split('\n')
        foo = ""

        rows = [x.strip() for x in rows]

        # have indexes store if a row is a divider
        # or a cell part
        for index in range(len(rows)):
            tmpstr = rows[index][1:len(rows[index])-1]
            if TDdivider(tmpstr):
                indexes.append("TDdivider")
            elif THdivider(tmpstr):
                indexes.append("THdivider")
            else:
                indexes.append("cell")

        for index in range(len(indexes)):
            if indexes[index] in ("TDdivider", "THdivider"):
                ignore = [] # reset ignore
                #continue    # skip dividers

            tmp = rows[index].strip()    # clean the row up
            tmp = tmp[1:-1]     # remove leading + trailing |
            offset = 0

            # find the start and end of inner
            # tables. ignore everything between
            if innertable(tmp):
                tmpstr = tmp.strip()
                while innertable(tmpstr):
                    start, end = innertable(tmpstr).span()
                    if not (start, end - 1) in ignore:
                        ignore.append((start, end - 1))
                    tmpstr = " " + tmpstr[end:]

            # find the location of column dividers
            # NOTE: |'s in inner tables do not count
            #   as column dividers
            if col(tmp):
                while col(tmp):
                    bar = 1   # true if start is not in ignore
                    start, end = col(tmp).span()

                    if not start + offset in spans:
                        for s, e in ignore:
                            if start + offset >= s or start + offset <= e:
                                bar = None
                                break
                        if bar:   # start is clean
                            spans.append(start + offset)
                    if not bar:
                        foo += tmp[:end]
                        tmp = tmp[end:]
                        offset += end
                    else:
                        COLS.append((foo + tmp[:start], start + offset))
                        foo = ""
                        tmp = " " + tmp[end:]
                        offset = offset + start
            if not offset + len(tmp) in spans:
                spans.append(offset + len(tmp))
            COLS.append((foo + tmp, offset + len(tmp)))
            foo = ""
            ROWS.append(COLS)
            COLS = []

        spans.sort()
        ROWS = ROWS[1:]

        # find each column span
        cols = []
        tmp = []

        for row in ROWS:
            for c in row:
                tmp.append(c[1])
            cols.append(tmp)
            tmp = []

        cur = 1
        tmp = []
        C = []
        for col in cols:
            for span in spans:
                if not span in col:
                    cur += 1
                else:
                    tmp.append(cur)
                    cur = 1
            C.append(tmp)
            tmp = []

        for index in range(len(C)):
            for i in range(len(C[index])):
                ROWS[index][i] = (ROWS[index][i][0], C[index][i])
        rows = ROWS

        # label things as either TableData or
        # Table header
        TD = []
        TH = []
        all = []
        for index in range(len(indexes)):
            if indexes[index] == "TDdivider":
                TD.append(index)
                all.append(index)
            if indexes[index] == "THdivider":
                TH.append(index)
                all.append(index)
        TD = TD[1:]
        dividers = all[1:]
        #print "TD  => ", TD
        #print "TH  => ", TH
        #print "all => ", all, "\n"

        for div in dividers:
            if div in TD:
                index = all.index(div)
                for rowindex in range(all[index - 1], all[index]):
                    for i in range(len(rows[rowindex])):
                        rows[rowindex][i] = (rows[rowindex][i][0],
                                             rows[rowindex][i][1],
                                             "td")
            else:
                index = all.index(div)
                for rowindex in range(all[index - 1], all[index]):
                    for i in range(len(rows[rowindex])):
                        rows[rowindex][i] = (rows[rowindex][i][0],
                                             rows[rowindex][i][1],
                                             "th")

        # now munge the multi-line cells together
        # as paragraphs
        ROWS = []
        COLS = []
        for row in rows:
            for index in range(len(row)):
                if not COLS:
                    COLS = list(range(len(row)))
                    COLS = [["", 1, ""] for _ in COLS]
                    #for i in range(len(COLS)):
                    #    COLS[i] = ["", 1 ,""]
                if TDdivider(row[index][0]) or THdivider(row[index][0]):
                    ROWS.append(COLS)
                    COLS = []
                else:
                    COLS[index][0] = COLS[index][0] + (row[index][0]) + "\n"
                    COLS[index][1] = row[index][1]
                    COLS[index][2] = row[index][2]

        # now that each cell has been munged together,
        # determine the cell's alignment.
        # Default is to center. Also determine the cell's
        # vertical alignment, top, middle, bottom. Default is
        # to middle
        rows = []
        cols = []
        for row in ROWS:
            for index in range(len(row)):
                topindent = 0
                bottomindent = 0
                leftindent = 0
                rightindent = 0
                left = []
                right = []
                text = row[index][0]
                text = text.split('\n')
                text = text[:-1]
                align = ""
                valign = ""
                for t in text:
                    t = t.strip()
                    if not t:
                        topindent += 1
                    else:
                        break
                text.reverse()
                for t in text:
                    t = t.strip()
                    if not t:
                        bottomindent += 1
                    else:
                        break
                text.reverse()
                tmp = '\n'.join(text[topindent:len(text)-bottomindent])
                pars = re.compile(r"\n\s*\n").split(tmp)
                for par in pars:
                    if index > 0:
                        par = par[1:]
                    par = par.split(' ')
                    for p in par:
                        if not p:
                            leftindent += 1
                        else:
                            break
                    left.append(leftindent)
                    leftindent = 0
                    par.reverse()
                    for p in par:
                        if not p:
                            rightindent += 1
                        else:
                            break
                    right.append(rightindent)
                    rightindent = 0
                left.sort()
                right.sort()

                valign = "middle"
                if topindent == bottomindent:
                    valign = "middle"
                elif topindent < 1:
                    valign = "top"
                elif bottomindent < 1:
                    valign = "bottom"


                if left[0] < 1:
                    align = "left"
                elif right[0] < 1:
                    align = "right"
                elif left[0] > 1 and right[0] > 1:
                    align = "center"
                else:
                    align = "left"

                cols.append(
                    (row[index][0], row[index][1],
                     align, valign, row[index][2])
                )
            rows.append(cols)
            cols = []
        return StructuredTextTable(rows,
                                   text, subs, indent=paragraph.indent)

    def doc_bullet(self, paragraph, expr=re.compile(r'\s*[-*o]\s+').match):
        top = paragraph.getColorizableTexts()[0]
        m = expr(top)

        if not m:
            return None

        subs = paragraph.getSubparagraphs()
        if top[-2:] == '::':
            subs = [StructuredTextExample(subs)]
            top = top[:-1]
        return StructuredTextBullet(top[m.span()[1]:], subs,
                                    indent=paragraph.indent,
                                    bullet=top[:m.span()[1]])

    def doc_numbered(self,
                     paragraph,
                     expr=re.compile(
                         r'(\s*[%s]\.)|(\s*[0-9]+\.)|(\s*[0-9]+\s+)' % letters).match):

        # This is the old expression. It had a nasty habit
        # of grabbing paragraphs that began with a single
        # letter word even if there was no following period.

        #expr = re.compile('\s*'
        #                   '(([a-zA-Z]|[0-9]+|[ivxlcdmIVXLCDM]+)\.)*'
        #                   '([a-zA-Z]|[0-9]+|[ivxlcdmIVXLCDM]+)\.?'
        #                   '\s+').match):

        top = paragraph.getColorizableTexts()[0]
        m = expr(top)
        if not m:
            return None

        subs = paragraph.getSubparagraphs()
        if top[-2:] == '::':
            subs = [StructuredTextExample(subs)]
            top = top[:-1]
        return StructuredTextNumbered(top[m.span()[1]:], subs,
                                      indent=paragraph.indent,
                                      number=top[:m.span()[1]])

    def doc_description(self, paragraph,
                        delim=re.compile(r'\s+--\s+').search,
                        nb=re.compile(r'[^\000- ]').search):

        top = paragraph.getColorizableTexts()[0]
        d = delim(top)
        if not d:
            return None
        start, end = d.span()
        title = top[:start]
        if title.find('\n') >= 0:
            return None
        if not nb(title):
            return None
        d = top[start:end]
        top = top[end:]

        subs = paragraph.getSubparagraphs()
        if top[-2:] == '::':
            subs = [StructuredTextExample(subs)]
            top = top[:-1]

        return StructuredTextDescription(
            title, top, subs,
            indent=paragraph.indent,
            delim=d)

    def doc_header(self, paragraph):
        subs = paragraph.getSubparagraphs()
        if not subs:
            return None

        top = paragraph.getColorizableTexts()[0]
        if not top.strip():
            return None

        if top[-2:] == '::':
            subs = StructuredTextExample(subs)
            if top.strip() == '::':
                return subs
            # copy attrs when returning a paragraph
            kw = {}
            atts = getattr(paragraph, '_attributes', [])
            for att in atts:
                kw[att] = getattr(paragraph, att)
            return StructuredTextParagraph(top[:-1], [subs], **kw)

        if top.find('\n') >= 0:
            return None
        return StructuredTextSection(top, subs, indent=paragraph.indent)

    def doc_literal(self,
                    s,
                    expr=re.compile(
                        r"(\W+|^)'([\w%s\s]+)'([%s]+|$)"\
                        % (literal_punc, phrase_delimiters),
                        re.UNICODE).search):
        r = expr(s)
        if r:
            start, end = r.span(2)
            return (StructuredTextLiteral(s[start:end]), start-1, end+1)

    def doc_emphasize(self,
                      s,
                      expr=re.compile(r'\*([\w%s\s]+?)\*' \
                                      % (strongem_punc), re.UNICODE).search):

        r = expr(s)
        if r:
            start, end = r.span(1)
            return (StructuredTextEmphasis(s[start:end]),
                    start-1, end+1)

    def doc_inner_link(self,
                       s,
                       expr1=re.compile(r"\.\.\s*").search,
                       expr2=re.compile(r"\[[\w]+\]", re.UNICODE).search):

        # make sure we dont grab a named link
        if expr2(s) and expr1(s):
            start1, end1 = expr1(s).span()
            start2, end2 = expr2(s).span()
            if end1 == start2:
                # uh-oh, looks like a named link
                return None

            # the .. is somewhere else, ignore it
            return (StructuredTextInnerLink(s[start2 + 1:end2 - 1]),
                    start2, end2)
        elif expr2(s) and not expr1(s):
            start, end = expr2(s).span()
            return (StructuredTextInnerLink(s[start + 1:end - 1]),
                    start, end)

    def doc_named_link(self,
                       s,
                       expr=re.compile(r"(\.\.\s)(\[[\w]+\])",
                                       re.UNICODE).search):

        result = expr(s)
        if result:
            start, end = result.span(2)
            str = s[start + 1:end - 1]
            st, en = result.span()
            return (StructuredTextNamedLink(str), st, en)

    def doc_underline(self,
                      s,
                      expr=re.compile(r'_([\w%s\s]+)_([\s%s]|$)'\
                            % (under_punc, phrase_delimiters),
                                      re.UNICODE).search):

        result = expr(s)
        if result:
            if result.group(1)[:1] == '_':
                return None # no double unders
            start, end = result.span(1)
            st, e = result.span()
            return (StructuredTextUnderline(s[start:end]),
                    st, e-len(result.group(2)))

    def doc_strong(self,
                   s,
                   expr=re.compile(r'\*\*([\w%s\s]+?)\*\*' \
                                   % (strongem_punc), re.UNICODE).search):

        r = expr(s)
        if r:
            start, end = r.span(1)
            return (StructuredTextStrong(s[start:end]),
                    start-2, end+2)

    ## Some constants to make the doc_href() regex easier to read.
    # ## double quoted text
    _DQUOTEDTEXT = r'("[ \w\n\r%s]+")' % (dbl_quoted_punc)
    _ABSOLUTE_URL = r'((http|https|ftp|mailto|file|about)[:/]+?[\w\@\.\,\?\!\/\:\;\-\#\~\=\&\%%\+]+)'
    _ABS_AND_RELATIVE_URL = r'([\w\@\.\,\?\!\/\:\;\-\#\~\=\&\%%\+]+)'

    _SPACES = r'(\s*)'

    def doc_href1(self,
                  s,
                  expr=re.compile(_DQUOTEDTEXT \
                                  + "(:)" \
                                  + _ABS_AND_RELATIVE_URL \
                                  + _SPACES, re.UNICODE).search):
        return self.doc_href(s, expr)

    def doc_href2(self,
                  s,
                  expr=re.compile(_DQUOTEDTEXT\
                                 + r'(\,\s+)' \
                                 + _ABSOLUTE_URL \
                                 + _SPACES, re.UNICODE).search):
        return self.doc_href(s, expr)

    def doc_href(self,
                 s,
                 expr,
                 punctuation=re.compile(r"[\,\.\?\!\;]+", re.UNICODE).match):
        r = expr(s)

        if r:
            # need to grab the href part and the
            # beginning part
            start, e = r.span(1)
            name = s[start:e]
            name = name.replace('"', '', 2)
            #start   = start + 1
            st, end = r.span(3)
            if punctuation(s[end - 1:end]):
                end = end -1
            link = s[st:end]
            #end     = end - 1

            # name is the href title, link is the target
            # of the href
            return (StructuredTextLink(name, href=link),
                    start, end)

    def doc_sgml(self,
                 s,
                 expr=re.compile(r"\<[\w\.\=\'\"\:\/\-\#\+\s\*]+\>",
                                 re.UNICODE).search):
        """SGML text is ignored and outputed as-is
        """
        r = expr(s)
        if r:
            start, end = r.span()
            text = s[start:end]
            return (StructuredTextSGML(text),
                    start, end)

    def doc_xref(self,
                 s,
                 expr=re.compile(r'\[([\w\-.:/;,\n\r\~]+)\]',
                                 re.UNICODE).search):
        r = expr(s)
        if r:
            start, end = r.span(1)
            return (StructuredTextXref(s[start:end]),
                    start-1, end+1)

class DocumentWithImages(Document):
    """Document with images
    """

    text_types = [
        'doc_img',
    ] + Document.text_types


    def doc_img(self,
                s,
                expr=re.compile(Document._DQUOTEDTEXT \
                                + ":img:" \
                                + Document._ABS_AND_RELATIVE_URL,
                                re.UNICODE).search):

        r = expr(s)
        if r:
            startt, endt = r.span(1)
            starth, endh = r.span(2)
            start, end = r.span()
            return (StructuredTextImage(s[startt + 1:endt - 1],
                                        href=s[starth:endh]),
                    start, end)

        return None
