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
"""Basic Page Template tests
"""
import unittest

from zope.pagetemplate.tests import util
import zope.pagetemplate.pagetemplate
import zope.component.testing

class BasicTemplateTests(unittest.TestCase):

    def setUp(self):
        zope.component.testing.setUp(self)
        self.t = zope.pagetemplate.pagetemplate.PageTemplate()

    def tearDown(self):
        zope.component.testing.tearDown(self)

    def test_if_in_var(self):
        # DTML test 1: if, in, and var:

        # %(comment)[ blah %(comment)]
        # <html><head><title>Test of documentation templates</title></head>
        # <body>
        # %(if args)[
        # <dl><dt>The arguments to this test program were:<p>
        # <dd>
        # <ul>
        # %(in args)[
        #   <li>Argument number %(num)d was %(arg)s
        # %(in args)]
        # </ul></dl><p>
        # %(if args)]
        # %(else args)[
        # No arguments were given.<p>
        # %(else args)]
        # And thats da trooth.
        # </body></html>

        tal = util.read_input('dtml1.html')
        self.t.write(tal)

        aa = util.argv(('one', 'two', 'three', 'cha', 'cha', 'cha'))
        o = self.t(content=aa)
        expect = util.read_output('dtml1a.html')

        util.check_xml(expect, o)

        aa = util.argv(())
        o = self.t(content=aa)
        expect = util.read_output('dtml1b.html')
        util.check_xml(expect, o)

    def test_pt_runtime_error(self):
        self.t.write("<tal:block define='a string:foo'>xyz")
        try:
            self.t.pt_render({})
        except zope.pagetemplate.pagetemplate.PTRuntimeError as e:
            self.assertEqual(
                str(e),
                "['Compilation failed', 'zope.tal.taldefs.TALError:"
                " TAL attributes on <tal:block> require explicit"
                " </tal:block>, at line 1, column 1']")
        else:
            self.fail("expected PTRuntimeError")

    def test_engine_utility_registration(self):
        self.t.write("foo")
        output = self.t.pt_render({})
        self.assertEqual(output, 'foo')

        from zope.pagetemplate.interfaces import IPageTemplateEngine
        from zope.component import provideUtility

        class DummyProgram(object):
            def __init__(self, *args):
                self.args = args

            def __call__(self, *args, **kwargs):
                return self.args, (self,) + args, kwargs

        class DummyEngine(object):
            @staticmethod
            def cook(*args):
                return DummyProgram(*args), "macros"

        provideUtility(DummyEngine, IPageTemplateEngine)
        self.t._cook()

        self.assertIsInstance(self.t._v_program, DummyProgram)
        self.assertEqual(self.t._v_macros, "macros")

        # "Render" and unpack arguments passed for verification
        ((source_file, text, _engine, content_type),
         (program, _context, macros),
         options) = self.t.pt_render({})

        self.assertEqual(source_file, None)
        self.assertEqual(text, 'foo')
        self.assertEqual(content_type, 'text/html')
        self.assertEqual(macros, 'macros')
        self.assertIsInstance(program, DummyProgram)
        self.assertEqual(options, {
            'tal': True,
            'showtal': False,
            'sourceAnnotations': False,
            'strictinsert': 0,
            })

    def test_batches_and_formatting(self):
        # DTML test 3: batches and formatting:

        #   <html><head><title>Test of documentation templates</title></head>
        #   <body>
        #   <!--#if args-->
        #     The arguments were:
        #     <!--#in args size=size end=end-->
        #         <!--#if previous-sequence-->
        #            (<!--#var previous-sequence-start-arg-->-
        #             <!--#var previous-sequence-end-arg-->)
        #         <!--#/if previous-sequence-->
        #         <!--#if sequence-start-->
        #            <dl>
        #         <!--#/if sequence-start-->
        #         <dt><!--#var sequence-arg-->.</dt>
        #         <dd>Argument <!--#var num fmt=d--> was <!--#var arg--></dd>
        #         <!--#if next-sequence-->
        #            (<!--#var next-sequence-start-arg-->-
        #             <!--#var next-sequence-end-arg-->)
        #         <!--#/if next-sequence-->
        #     <!--#/in args-->
        #     </dl>
        #   <!--#else args-->
        #     No arguments were given.<p>
        #   <!--#/if args-->
        #   And I\'m 100% sure!
        #   </body></html>

        tal = util.read_input('dtml3.html')
        self.t.write(tal)

        aa = util.argv((
            'one', 'two', 'three', 'four', 'five',
            'six', 'seven', 'eight', 'nine', 'ten',
            'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
            'sixteen', 'seventeen', 'eighteen', 'nineteen',
            'twenty',
        ))
        from zope.pagetemplate.tests import batch
        o = self.t(content=aa, batch=batch.batch(aa.args, 5))

        expect = util.read_output('dtml3.html')
        util.check_xml(expect, o)

    def test_on_error_in_slot_filler(self):
        # The `here` isn't defined, so the macro definition is
        # expected to catch the error that gets raised.
        text = '''\
            <div metal:define-macro="foo">
               <div tal:on-error="string:eek">
                  <div metal:define-slot="slot" />
                  cool
               </div>
            </div>

            <div metal:use-macro="template/macros/foo">
               <div metal:fill-slot="slot">
                  <p tal:content="here/xxx" />
               </div>
            </div>
            '''
        self.t.write(text)
        self.t()

    def test_on_error_in_slot_default(self):
        # The `here` isn't defined, so the macro definition is
        # expected to catch the error that gets raised.
        text = '''\
            <div metal:define-macro="foo">
               <div tal:on-error="string:eek">
                  <div metal:define-slot="slot">
                    <div tal:content="here/xxx" />
                  </div>
               </div>
            </div>

            <div metal:use-macro="template/macros/foo">
            </div>
            '''
        self.t.write(text)
        self.t()

    def test_unicode_html(self):
        text = u'<p>\xe4\xf6\xfc\xdf</p>'

        # test with HTML parser
        self.t.pt_edit(text, 'text/html')
        self.assertEqual(self.t().strip(), text)

        # test with XML parser
        self.t.pt_edit(text, 'text/xml')
        self.assertEqual(self.t().strip(), text)

    def test_edit_with_read(self):
        from io import BytesIO
        self.t.pt_edit(BytesIO(b"<html/>"), None)
        self.assertEqual(self.t._text, b'<html/>')

    def test_errors(self):
        self.t._v_cooked = True
        self.t._v_errors = 1
        e = self.t.pt_errors(None)
        self.assertEqual(e, 1)

        self.t._v_errors = ()
        e = self.t.pt_errors(None)
        self.assertEqual(e[0], 'Macro expansion failed')

    def test_convert(self):
        string = u'binary'
        text = b'binary'
        self.assertEqual(text, self.t._convert(string, text))

    def test_write_error(self):
        self.t.write(self.t._error_start + 'stuff' + self.t._error_end + self.t._newline)
        self.assertEqual(self.t._text, '')

    def test_read_no_expand(self):
        self.t.expand = False
        self.t._text = self
        self.t._v_cooked = True

        self.assertIs(self.t.read(), self)

    def test_read_error_expand(self):
        self.t.expand = True
        self.t._text = ''
        self.t._v_cooked = True
        text = self.t.read()
        self.assertIn(self.t._error_start, text)
        self.assertIn("Macro expansion failed", text)

    def test_macros(self):
        self.assertEqual(self.t.macros, {})


class TestPageTemplateTracebackSupplement(unittest.TestCase):

    def test_errors_old_style(self):
        class PT(object):
            def pt_errors(self, ns):
                return (ns,)

        pts = zope.pagetemplate.pagetemplate.PageTemplateTracebackSupplement(PT(), 'ns')

        self.assertEqual(pts.warnings, ['ns'])

    def test_errors_none(self):
        class PT(object):
            def pt_errors(self, ns, check_macro_expansion=False):
                return None

        pts = zope.pagetemplate.pagetemplate.PageTemplateTracebackSupplement(PT(), 'ns')
        self.assertEqual(pts.warnings, [])
