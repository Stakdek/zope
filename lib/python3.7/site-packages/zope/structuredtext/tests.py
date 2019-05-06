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
from __future__ import print_function
import doctest
import unittest
import glob
import os

from zope.structuredtext import stng
from zope.structuredtext import stdom
from zope.structuredtext.document import DocumentWithImages
from zope.structuredtext.html import HTMLWithImages
from zope.structuredtext.docbook import DocBook
from zope.structuredtext.docbook import DocBookChapterWithFigures

here = os.path.dirname(__file__)
regressions = os.path.join(here, 'regressions')

files = glob.glob(regressions + '/*stx')


def readFile(dirname, fname):
    with open(os.path.join(dirname, fname), "r") as myfile:
        lines = myfile.readlines()
    return ''.join(lines)

def structurizedFile(f):
    raw_text = readFile(regressions, f)
    text = stng.structurize(raw_text)
    return text

def structurizedFiles():
    for f in files:
        yield structurizedFile(f)

class MockParagraph(object):

    co_texts = ()
    sub_paragraphs = ()
    indent = 0
    node_type = stdom.TEXT_NODE
    node_value = ''
    node_name = None
    child_nodes = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def getColorizableTexts(self):
        return self.co_texts

    def getSubparagraphs(self):
        return self.sub_paragraphs

    def getNodeType(self):
        return self.node_type

    def getNodeValue(self):
        return self.node_value

    def getNodeName(self):
        return self.node_name

    def getChildNodes(self):
        return self.child_nodes

class TestFiles(unittest.TestCase):

    maxDiff = None

    def _compare(self, filename, output, expected_extension=".ref"):
        expected_filename = filename.replace('.stx', expected_extension)
        try:
            expected = readFile(regressions, expected_filename)
        except IOError: # pragma: no cover
            full_expected_fname = os.path.join(regressions, expected_filename)
            if not os.path.exists(full_expected_fname):
                with open(full_expected_fname, 'w') as f:
                    f.write(output)
        else:
            self.assertEqual(expected.strip(), output.strip())

    def _check_html(self, f):
        # HTML regression test
        __traceback_info__ = f

        stext = structurizedFile(f)
        doc = DocumentWithImages()(stext)
        html = HTMLWithImages()(doc)

        self._compare(f, html)

        # The same thing should work if we feed it the bare text
        text = readFile(regressions, f)
        doc = DocumentWithImages()(text)
        html = HTMLWithImages()(doc)
        self._compare(f, html)

    def _check_docbook(self, f):
        __traceback_info__ = f

        fails_to_docbook = {
            # Doesn't support StructuredTextTable
            'table.stx',
        }

        requires_images = {
            'images.stx'
        }

        if f in fails_to_docbook:
            raise unittest.SkipTest()

        text = structurizedFile(f)
        doc = DocumentWithImages()(text)

        factory = DocBook if f not in requires_images else DocBookChapterWithFigures

        docbook = factory()(doc)
        self._compare(f, docbook, '.xml')



    for f in files:
        f = os.path.basename(f)
        html = lambda self, f=f: self._check_html(f)
        xml = lambda self, f=f: self._check_docbook(f)

        bn = os.path.basename(f).replace('.', '_')
        locals()['test_html_' + bn] = html
        locals()['test_xml_' + bn] = xml


class TestDocument(unittest.TestCase):

    def testDocumentClass(self):
        # testing Document
        # *cough* *cough* this can't be enough...

        for text in structurizedFiles():
            doc = DocumentWithImages()
            self.assertTrue(doc(text))

            def reprs(x): # coverage
                self.assertTrue(repr(x))
                if not hasattr(x, 'getChildren'):
                    return
                stng.print = lambda *args, **kwargs: None
                try:
                    stng.display(x)
                    stng.display2(x)
                finally:
                    del stng.print
                for i in x.getChildren():
                    self.assertTrue(repr(i))
                    reprs(i)
            reprs(text)

    def test_description_newline(self):
        doc = DocumentWithImages()
        with_newline = MockParagraph(co_texts=['\nD  -- '])
        result = doc.doc_description(with_newline)
        self.assertIsNone(result)

    def test_description_nb(self):
        doc = DocumentWithImages()
        with_nb = MockParagraph(co_texts=[' -- '])
        result = doc.doc_description(with_nb)
        self.assertIsNone(result)

    def test_description_example(self):
        doc = DocumentWithImages()
        with_example = MockParagraph(co_texts=['Desc:: -- ::'])

        result = doc.doc_description(with_example)
        self.assertIsInstance(result, stng.StructuredTextDescription)
        self.assertIsInstance(result.getSubparagraphs()[0], stng.StructuredTextExample)
        self.assertEqual(result._src, ':')

    def test_parse_returns_string(self):
        doc = DocumentWithImages()
        returns = ['', ('a string', 0, 0)]
        def text_type(arg):
            return returns.pop()

        result = doc.parse('raw_string', text_type)
        self.assertEqual('a stringraw_string', result)

    def test_parse_returns_list(self):
        doc = DocumentWithImages()
        returns = ['', ([1], 0, 0)]

        def text_type(arg):
            return returns.pop()

        result = doc.parse('raw_string', text_type)
        self.assertEqual([1, 'raw_string'], result)

    def test_header_empty(self):
        doc = DocumentWithImages()
        header = MockParagraph(sub_paragraphs=self, co_texts=[''])

        result = doc.doc_header(header)
        self.assertIsNone(result)

    def test_header_example(self):
        doc = DocumentWithImages()
        header = MockParagraph(sub_paragraphs=[MockParagraph()], co_texts=["::"])
        result = doc.doc_header(header)
        self.assertIsInstance(result, stng.StructuredTextExample)

    def test_inner_link_is_not_named_link(self):
        doc = DocumentWithImages()
        result = doc.doc_inner_link('...[abc]')
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], stng.StructuredTextInnerLink)

class HTMLDocumentTests(unittest.TestCase):

    def _test(self, stxtxt, expected, html=HTMLWithImages):
        doc = stng.structurize(stxtxt)
        doc = DocumentWithImages()(doc)
        output = html()(doc, level=1)

        msg = ("Text:      %s\n" % stxtxt
               + "Converted: %s\n" % output
               + "Expected:  %s\n" % expected)
        self.assertIn(expected, output, msg)

    def testUnderline(self):
        self._test("xx _this is html_ xx",
                   "xx <u>this is html</u> xx")

    def testUnderlineNonASCII(self):
        self._test("xx _D\xc3\xbcsseldorf underlined_ xx",
                   "xx <u>D\xc3\xbcsseldorf underlined</u> xx")

    def testUnderline1(self):
        self._test("xx _this is html_",
                   "<u>this is html</u>")


    def testUnderline1NonASCII(self):
        self._test("xx _D\xc3\xbcsseldorf underlined_",
                   "<u>D\xc3\xbcsseldorf underlined</u>")

    def testEmphasis(self):
        self._test("xx *this is html* xx",
                   "xx <em>this is html</em> xx")

    def testEmphasisNonASCII(self):
        self._test("xx *Emphasising D\xc3\xbcsseldorf* xx",
                   "xx <em>Emphasising D\xc3\xbcsseldorf</em> xx")

    def testStrong(self):
        self._test("xx **this is html** xx",
                   "xx <strong>this is html</strong> xx")

    def testStrongNonASCII(self):
        self._test("xx **Greetings from D\xc3\xbcsseldorf** xx",
                   "xx <strong>Greetings from D\xc3\xbcsseldorf</strong> xx")

    def testUnderlineThroughoutTags(self):
        self._test('<a href="index_html">index_html</a>',
                   '<a href="index_html">index_html</a>')

    def testUnderlineThroughoutTagsNonASCII(self):
        self._test('<a href="index_html">D\xc3\xbcsseldorf</a>',
                   '<a href="index_html">D\xc3\xbcsseldorf</a>')

    def testUnderscoresInLiteral1(self):
        self._test("def __init__(self)",
                   "def __init__(self)")

    def testUnderscoresInLiteral1NonASCII(self):
        self._test("def __init__(D\xc3\xbcsself)",
                   "def __init__(D\xc3\xbcsself)")

    def testUnderscoresInLiteral2(self):
        self._test("this is '__a_literal__' eh",
                   "<code>__a_literal__</code>")


    def testUnderscoresInLiteral2NonASCII(self):
        self._test("this is '__literally_D\xc3\xbcsseldorf__' eh",
                   "<code>__literally_D\xc3\xbcsseldorf__</code>")

    def testUnderlinesWithoutWithspaces(self):
        self._test("Zopes structured_text is sometimes a night_mare",
                   "Zopes structured_text is sometimes a night_mare")

    def testUnderlinesWithoutWithspacesNonASCII(self):
        self._test("D\xc3\xbcsseldorf by night is sometimes a night_mare",
                   "D\xc3\xbcsseldorf by night is sometimes a night_mare")

    def testAsterisksInLiteral(self):
        self._test("this is a '*literal*' eh",
                   "<code>*literal*</code>")

    def testAsterisksInLiteralNonASCII(self):
        self._test("this is a '*D\xc3\xbcsseldorf*' eh",
                   "<code>*D\xc3\xbcsseldorf*</code>")

    def testDoubleAsterisksInLiteral(self):
        self._test("this is a '**literal**' eh",
                   "<code>**literal**</code>")

    def testDoubleAsterisksInLiteralNonASCII(self):
        self._test("this is a '**D\xc3\xbcsseldorf**' eh",
                   "<code>**D\xc3\xbcsseldorf**</code>")

    def testLinkInLiteral(self):
        self._test("this is a '\"literal\":http://www.zope.org/.' eh",
                   '<code>"literal":http://www.zope.org/.</code>')

    def testLinkInLiteralNonASCII(self):
        self._test("this is a '\"D\xc3\xbcsseldorf\":http://www.zope.org/.' eh",
                   '<code>"D\xc3\xbcsseldorf":http://www.zope.org/.</code>')

    def testLink(self):
        self._test('"foo":http://www.zope.org/foo/bar',
                   '<p><a href="http://www.zope.org/foo/bar">foo</a></p>')

        self._test('"foo":http://www.zope.org/foo/bar/%20x',
                   '<p><a href="http://www.zope.org/foo/bar/%20x">foo</a></p>')

        self._test('"foo":http://www.zope.org/foo/bar?arg1=1&arg2=2',
                   '<p><a href="http://www.zope.org/foo/bar?arg1=1&arg2=2">foo</a></p>')

        self._test('"foo bar":http://www.zope.org/foo/bar',
                   '<p><a href="http://www.zope.org/foo/bar">foo bar</a></p>')

        self._test('"[link goes here]":http://www.zope.org/foo/bar',
                   '<p><a href="http://www.zope.org/foo/bar">[link goes here]</a></p>')

        self._test('"[Dad\'s car]":http://www.zope.org/foo/bar',
                   '<p><a href="http://www.zope.org/foo/bar">[Dad\'s car]</a></p>')

    def testLinkNonASCII(self):
        self._test('"D\xc3\xbcsseldorf":http://www.zope.org/foo/bar',
                   '<p><a href="http://www.zope.org/foo/bar">D\xc3\xbcsseldorf</a></p>')

        self._test('"D\xc3\xbcsseldorf":http://www.zope.org/foo/bar/%20x',
                   '<p><a href="http://www.zope.org/foo/bar/%20x">D\xc3\xbcsseldorf</a></p>')

        self._test(
            '"D\xc3\xbcsseldorf":http://www.zope.org/foo/bar?arg1=1&arg2=2',
            '<p><a href="http://www.zope.org/foo/bar?arg1=1&arg2=2">D\xc3\xbcsseldorf</a></p>')

        self._test('"D\xc3\xbcsseldorf am Rhein":http://www.zope.org/foo/bar',
                   '<p><a href="http://www.zope.org/foo/bar">D\xc3\xbcsseldorf am Rhein</a></p>')

        self._test('"[D\xc3\xbcsseldorf am Rhein]":http://www.zope.org/foo/bar',
                   '<p><a href="http://www.zope.org/foo/bar">[D\xc3\xbcsseldorf am Rhein]</a></p>')

        self._test(
            '"[D\xc3\xbcsseldorf\'s Homepage]":http://www.zope.org/foo/bar',
            '<p><a href="http://www.zope.org/foo/bar">[D\xc3\xbcsseldorf\'s Homepage]</a></p>')

    def testImgLink(self):
        self._test('"foo":img:http://www.zope.org/bar.gif',
                   '<img src="http://www.zope.org/bar.gif" alt="foo" />')

        self._test('"foo":img:http://www.zope.org:8080/bar.gif',
                   '<img src="http://www.zope.org:8080/bar.gif" alt="foo" />')

        self._test('"foo":img:http://www.zope.org:8080/foo/bar?arg=1',
                   '<img src="http://www.zope.org:8080/foo/bar?arg=1" alt="foo" />')

        self._test('"foo":img:http://www.zope.org:8080/foo/b%20ar?arg=1',
                   '<img src="http://www.zope.org:8080/foo/b%20ar?arg=1" alt="foo" />')

        self._test('"foo bar":img:http://www.zope.org:8080/foo/bar',
                   '<img src="http://www.zope.org:8080/foo/bar" alt="foo bar" />')

        self._test('"[link goes here]":img:http://www.zope.org:8080/foo/bar',
                   '<img src="http://www.zope.org:8080/foo/bar" alt="[link goes here]" />')

        self._test('"[Dad\'s new car]":img:http://www.zope.org:8080/foo/bar',
                   '<img src="http://www.zope.org:8080/foo/bar" alt="[Dad\'s new car]" />')

    def testImgLinkNonASCII(self):
        self._test(
            '"D\xc3\xbcsseldorf":img:http://www.zope.org/bar.gif',
            '<img src="http://www.zope.org/bar.gif" alt="D\xc3\xbcsseldorf" />')

        self._test(
            '"D\xc3\xbcsseldorf":img:http://www.zope.org:8080/bar.gif',
            '<img src="http://www.zope.org:8080/bar.gif" alt="D\xc3\xbcsseldorf" />')

        self._test(
            '"D\xc3\xbcsseldorf":img:http://www.zope.org:8080/foo/bar?arg=1',
            '<img src="http://www.zope.org:8080/foo/bar?arg=1" alt="D\xc3\xbcsseldorf" />')

        self._test(
            '"D\xc3\xbcsseldorf":img:http://www.zope.org:8080/foo/b%20ar?arg=1',
            '<img src="http://www.zope.org:8080/foo/b%20ar?arg=1" alt="D\xc3\xbcsseldorf" />')

        self._test(
            '"D\xc3\xbcsseldorf am Rhein":img:http://www.zope.org:8080/foo/bar',
            '<img src="http://www.zope.org:8080/foo/bar" alt="D\xc3\xbcsseldorf am Rhein" />')

        self._test(
            '"[D\xc3\xbcsseldorf am Rhein]":img:http://www.zope.org:8080/foo/bar',
            '<img src="http://www.zope.org:8080/foo/bar" alt="[D\xc3\xbcsseldorf am Rhein]" />')

        self._test(
            '"[D\xc3\xbcsseldorf\'s Homepage]":img:http://www.zope.org:8080/foo/bar',
            '<img src="http://www.zope.org:8080/foo/bar" alt="[D\xc3\xbcsseldorf\'s Homepage]" />')

    def testBulletList(self):
        self._test("* item in a list", "<ul>\n<li>item in a list</li>")

    def testOrderedList(self):
        self._test("1. First item", "<ol>\n<li> First item</li>")

    def testDefinitionList(self):
        self._test("Term -- Definition", "<dt>Term</dt>\n<dd>Definition</dd>")

    def testHeader1(self):
        self._test("Title\n\n    following paragraph",
                   ("<h1>Title</h1>\n<p>    following paragraph</p>"))

    def testHeader1_again(self):
        self._test(
            """Title

            first paragraph

            Subtitle

                second paragraph""",
            ("""<h1>Title</h1>
<p>            first paragraph</p>
<h2>            Subtitle</h2>
<p>                second paragraph</p>"""))

    def testUnicodeContent(self):
        # This fails because ST uses the default locale to get "letters"
        # whereas it should use \w+ and re.U if the string is Unicode.
        self._test(u"h\xe9 **y\xe9** xx",
                   u"h\xe9 <strong>y\xe9</strong> xx")

    def test_paragraph_not_nestable(self):
        first_child_not_nestable = MockParagraph(node_name='not nestable or known')
        second_child_nestable = MockParagraph(node_name="#text")
        third_child_not_nestable = MockParagraph(node_name='not nestable or known')
        doc = MockParagraph(child_nodes=[first_child_not_nestable,
                                         second_child_nestable,
                                         third_child_not_nestable])

        html = HTMLWithImages()
        html.dispatch = lambda *args: None
        l = []
        html.paragraph(doc, level=1, output=l.append)
        self.assertEqual(l, ['<p>', '</p>\n', '<p>', '</p>\n'])

    def test_image_with_key(self):
        doc = MockParagraph(key='abc', href='def', node_value='123')
        html = HTMLWithImages()
        l = []
        html.image(doc, 1, output=l.append)
        self.assertEqual(l,
                         ['<a name="abc"></a>\n',
                          '<img src="def" alt="123" />\n',
                          '<p><b>Figure abc</b> 123</p>\n'])


class DocBookOutputTests(unittest.TestCase):

    def test_literal_text(self):
        doc = MockParagraph(node_name='StructuredTextLiteral', node_value='   ')
        docbook = DocBook()
        l = []
        docbook._text(doc, 1, output=l.append)
        self.assertEqual(l, ['   '])

class DocBookChapterWithFiguresOutputTests(unittest.TestCase):

    def test_image_with_key(self):
        doc = MockParagraph(key='abc', href='def', node_value='123')
        docbook = DocBookChapterWithFigures()
        l = []
        docbook.image(doc, 1, output=l.append)
        self.assertEqual(l,
                         ['<figure id="abc"><title>123</title>\n',
                          '<graphic fileref="def"></graphic>\n</figure>\n'])

class TestDocBookBook(unittest.TestCase):

    def test_output(self):
        from zope.structuredtext.docbook import DocBookBook

        book = DocBookBook('title')
        book.addChapter("\nchapter1\n")
        book.addChapter("\nchapter2\n")

        self.assertEqual(str(book),
                         '<!DOCTYPE book PUBLIC "-//OASIS//DTD DocBook V4.1//EN">\n<book>\n<title>title</title>\n\nchapter1\n\n\nchapter2\n\n\n</book>\n')

class TestSTNGFunctions(unittest.TestCase):

    def test_findlevel_empty(self):
        self.assertEqual(0, stng.findlevel({}, 42))

    def test_structurize_empty(self):
        paragraphs = ''
        result = stng.structurize(paragraphs)
        self.assertIsInstance(result, stng.StructuredTextDocument)

class TestStructuredTextDocument(unittest.TestCase):

    def test_set_texts_noop(self):
        doc = stng.StructuredTextDocument()
        self.assertEqual((), doc.getColorizableTexts())
        doc.setColorizableTexts(self)
        self.assertEqual((), doc.getColorizableTexts())


class TestStructuredTextExample(unittest.TestCase):

    def test_set_texts_noop(self):
        doc = stng.StructuredTextExample(())
        self.assertEqual((), doc.getColorizableTexts())
        doc.setColorizableTexts(self)
        self.assertEqual((), doc.getColorizableTexts())


class TestStructuredTextParagraph(unittest.TestCase):

    def test_attributes(self):
        p = stng.StructuredTextParagraph(src='', k=42)
        self.assertEqual(p.getAttribute("k"), 42)
        self.assertIsNone(p.getAttribute('does not exist'))
        self.assertIsNone(p.getAttributeNode('does not exist'))
        self.assertIsInstance(p.getAttributeNode('k'), stdom.Attr)
        nnmap = p.getAttributes()
        self.assertIsInstance(nnmap, stdom.NamedNodeMap)

class TestStructuredTextRow(unittest.TestCase):

    def test_set_columns(self):
        # What we set gets wrapped in another list
        row = stng.StructuredTextRow((), {})
        row.setColumns(self)
        self.assertEqual([self], row.getColumns())


class TestStructuredTextMarkup(unittest.TestCase):

    def test_repr(self):
        m = stng.StructuredTextMarkup('value')
        self.assertEqual("StructuredTextMarkup('value')", repr(m))


class TestStructuredTextTable(unittest.TestCase):

    def test_get_columns(self):

        row = stng.StructuredTextRow((), {})
        table = stng.StructuredTextTable((), '', ())
        table._rows = [row]

        self.assertEqual([[[]]], table.getColumns())

        table.setColumns(table.getColumns())

def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTest(doctest.DocTestSuite(
        'zope.structuredtext',
        optionflags=doctest.ELLIPSIS,
    ))
    return suite
