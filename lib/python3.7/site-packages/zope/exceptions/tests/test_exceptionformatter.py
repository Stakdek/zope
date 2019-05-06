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
"""ExceptionFormatter tests.
"""
import unittest
import sys


class TextExceptionFormatterTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.exceptions.exceptionformatter import TextExceptionFormatter
        return TextExceptionFormatter

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.line_sep, '\n')
        self.assertEqual(fmt.limit, None)
        self.assertEqual(fmt.with_filenames, False)

    def test_ctor_explicit(self):
        fmt = self._makeOne(limit=20, with_filenames=True)
        self.assertEqual(fmt.line_sep, '\n')
        self.assertEqual(fmt.limit, 20)
        self.assertEqual(fmt.with_filenames, True)

    def test_escape(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.escape('XXX'), 'XXX')

    def test_getPrefix(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.getPrefix(),
                         'Traceback (most recent call last):')

    def test_getLimit_default(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.getLimit(), 200)

    def test_getLimit_sys_has_limit(self):
        fmt = self._makeOne()
        with _Monkey(sys, tracebacklimit=15):
            self.assertEqual(fmt.getLimit(), 15)

    def test_getLimit_explicit(self):
        fmt = self._makeOne(limit=10)
        self.assertEqual(fmt.getLimit(), 10)

    def test_formatSupplementLine(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatSupplementLine('XXX'), '   - XXX')

    def test_formatSourceURL(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatSourceURL('http://example.com/'),
                         ['   - http://example.com/'])

    def test_formatSupplement_no_info(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        self.assertEqual(fmt.formatSupplement(supplement, tb=None), [])

    def test_formatSupplement_w_source_url(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.source_url = 'http://example.com/'
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - http://example.com/'])

    def test_formatSupplement_w_line_as_marker(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.line = -1
        tb = DummyTB()
        self.assertEqual(fmt.formatSupplement(supplement, tb=tb),
                         ['   - Line 14'])

    def test_formatSupplement_w_line_no_column(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.line = 23
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - Line 23'])

    def test_formatSupplement_w_column_no_line(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.column = 47
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - Column 47'])

    def test_formatSupplement_w_line_and_column(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.line = 23
        supplement.column = 47
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - Line 23, Column 47'])

    def test_formatSupplement_w_expression(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.expression = 'a*x^2 + b*x + c'
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - Expression: a*x^2 + b*x + c'])

    def test_formatSupplement_w_warnings(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.warnings = ['Beware the ides of March!',
                               'You\'re gonna get wasted.',
                              ]
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - Warning: Beware the ides of March!',
                          '   - Warning: You\'re gonna get wasted.',
                         ])

    def test_formatSupplement_w_getInfo_empty(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        self.assertEqual(fmt.formatSupplement(supplement, tb=None), [])

    def test_formatSupplement_w_getInfo_text(self):
        INFO = 'Some days\nI wish I had stayed in bed.'
        fmt = self._makeOne()
        supplement = DummySupplement(INFO)
        self.assertEqual(fmt.formatSupplement(supplement, tb=None), [INFO])

    def test_formatSupplementInfo(self):
        INFO = 'Some days\nI wish I had stayed in bed.'
        fmt = self._makeOne()
        self.assertEqual(fmt.formatSupplementInfo(INFO), INFO)

    def test_formatTracebackInfo(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatTracebackInfo('XYZZY'),
                         '   - __traceback_info__: XYZZY')

    def test_formatTracebackInfo_unicode(self):
        __traceback_info__ = u"Have a Snowman: \u2603"
        fmt = self._makeOne()

        result = fmt.formatTracebackInfo(__traceback_info__)
        expected = '   - __traceback_info__: Have a Snowman: '
        # utf-8 encoded on Python 2, unicode on Python 3
        expected += '\xe2\x98\x83' if bytes is str else u'\u2603'
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)

    def test_formatLine_no_tb_no_f(self):
        fmt = self._makeOne()
        self.assertRaises(ValueError, fmt.formatLine, None, None)

    def test_formatLine_w_tb_and_f(self):
        fmt = self._makeOne()
        tb = DummyTB()
        f = DummyFrame()
        self.assertRaises(ValueError, fmt.formatLine, tb, f)

    def test_formatLine_w_tb_bogus_linecache_w_filenames(self):
        fmt = self._makeOne(with_filenames=True)
        tb = DummyTB()
        tb.tb_frame = f = DummyFrame()
        lines = fmt.formatLine(tb).splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(
            lines[0],
            '  File "%s", line %d, in %s'
            % (f.f_code.co_filename,
               tb.tb_lineno,
               f.f_code.co_name,)
        )

    def test_formatLine_w_f_bogus_linecache_w_filenames(self):
        fmt = self._makeOne(with_filenames=True)
        f = DummyFrame()
        lines = fmt.formatLine(f=f).splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(
            lines[0],
            '  File "%s", line %d, in %s'
            % (f.f_code.co_filename,
               f.f_lineno,
               f.f_code.co_name,)
        )

    def test_formatLine_w_tb_bogus_linecache_wo_filenames(self):
        fmt = self._makeOne(with_filenames=False)
        tb = DummyTB()
        tb.tb_frame = f = DummyFrame()
        f.f_globals['__name__'] = 'dummy.filename'
        lines = fmt.formatLine(tb).splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(
            lines[0],
            '  Module dummy.filename, line %d, in %s'
            % (tb.tb_lineno,
               f.f_code.co_name,)
        )

    def test_formatLine_w_f_real_linecache_w_filenames(self):
        fmt = self._makeOne(with_filenames=True)
        f = sys._getframe()
        lineno = f.f_lineno
        result = fmt.formatLine(f=f)
        lines = result.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(
            lines[0],
            '  File "%s", line %d, in %s'
            % (f.f_code.co_filename,
               lineno + 1,
               f.f_code.co_name,)
        )
        self.assertEqual(lines[1],
                         '    result = fmt.formatLine(f=f)')

    def test_formatLine_w_supplement_in_locals(self):
        INFO_L = 'I wish I had stayed in bed.'
        INFO_G = 'I would rather soak my head.'
        fmt = self._makeOne(with_filenames=False)
        tb = DummyTB()
        tb.tb_frame = f = DummyFrame()
        f.f_globals['__name__'] = 'dummy.filename'
        f.f_locals['__traceback_supplement__'] = (DummySupplement, INFO_L)
        f.f_globals['__traceback_supplement__'] = (DummySupplement, INFO_G)
        lines = fmt.formatLine(tb).splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[1], INFO_L)

    def test_formatLine_w_supplement_in_globals(self):
        INFO_G = 'I would rather soak my head.'
        fmt = self._makeOne(with_filenames=False)
        tb = DummyTB()
        tb.tb_frame = f = DummyFrame()
        f.f_globals['__name__'] = 'dummy.filename'
        f.f_globals['__traceback_supplement__'] = (DummySupplement, INFO_G)
        lines = fmt.formatLine(tb).splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[1], INFO_G)

    def test_formatLine_w_traceback_info(self):
        INFO_T = 'I would rather soak my head.'
        fmt = self._makeOne(with_filenames=False)
        tb = DummyTB()
        tb.tb_frame = f = DummyFrame()
        f.f_globals['__name__'] = 'dummy.filename'
        f.f_locals['__traceback_info__'] = INFO_T
        lines = fmt.formatLine(tb).splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[1], '   - __traceback_info__: %s' % INFO_T)

    def test_formatExceptionOnly(self):
        import traceback
        fmt = self._makeOne()
        err = ValueError('testing')
        self.assertEqual(fmt.formatExceptionOnly(ValueError, err),
                         ''.join(
                             traceback.format_exception_only(ValueError, err)))

    def test_formatLastLine(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatLastLine('XXX'), 'XXX')

    def test_formatException_empty_tb_stack(self):
        import traceback
        fmt = self._makeOne()
        err = ValueError('testing')
        lines = fmt.formatException(ValueError, err, None)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], 'Traceback (most recent call last):\n')
        self.assertEqual(lines[1],
                         ''.join(
                             traceback.format_exception_only(ValueError, err)))

    def test_formatException_non_empty_tb_stack(self):
        import traceback
        fmt = self._makeOne()
        err = ValueError('testing')
        tb = DummyTB()
        tb.tb_frame = DummyFrame()
        lines = fmt.formatException(ValueError, err, tb)
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 'Traceback (most recent call last):\n')
        self.assertEqual(lines[1], '  Module dummy/filename.py, line 14, '
                                   'in dummy_function\n')
        self.assertEqual(lines[2],
                         ''.join(
                             traceback.format_exception_only(ValueError, err)))

    def test_formatException_deep_tb_stack_with_limit(self):
        import traceback
        fmt = self._makeOne(limit=4)
        err = ValueError('testing')
        tb = self._makeTBs(10)
        lines = fmt.formatException(ValueError, err, tb)

        self.assertEqual(len(lines), 7)

        expected = [
            'Traceback (most recent call last):\n',
            '  Module dummy/filename.py, line 4345, in dummy_function\n',
            '  Module dummy/filename.py, line 2287, in dummy_function\n',
            ('...\n'
             '6 entries omitted, because limit is 4.\n'
             'Set sys.tracebacklimit or TextExceptionFormatter.limit to'
             ' a higher value to see omitted entries\n'
             '...'),
            '  Module dummy/filename.py, line 26, in dummy_function\n',
            '  Module dummy/filename.py, line 14, in dummy_function\n',
            ''.join(traceback.format_exception_only(ValueError, err))
            ]
        self.assertEqual(lines, expected)

    def test_formatException_recursion_in_tb_stack(self):
        import traceback
        fmt = self._makeOne()
        err = ValueError('testing')
        tb_recurse = DummyTB()
        tb_recurse.tb_lineno = 27
        r_f = tb_recurse.tb_frame = DummyFrame()
        r_f.f_lineno = 27
        r_f.f_locals['__exception_formatter__'] = 1
        tb = DummyTB()
        tb.tb_frame = DummyFrame()
        tb.tb_next = tb_recurse
        lines = fmt.formatException(ValueError, err, tb)
        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[0], 'Traceback (most recent call last):\n')
        self.assertEqual(lines[1], '  Module dummy/filename.py, line 14, '
                                   'in dummy_function\n')
        self.assertEqual(lines[2], '(Recursive formatException() stopped, '
                                   'trying traceback.format_tb)\n')
        self.assertEqual(lines[3], '  File "dummy/filename.py", line 27, '
                                   'in dummy_function\n')
        self.assertEqual(lines[4],
                         ''.join(
                             traceback.format_exception_only(ValueError, err)))

    def test_extractStack_wo_frame(self):
        fmt = self._makeOne()
        f = sys._getframe()
        lineno = f.f_lineno
        lines = fmt.extractStack()
        # rather don't assert this here
        # self.assertEqual(len(lines), 10)
        self.assertEqual(lines[-1], '  Module '
                         'zope.exceptions.tests.test_exceptionformatter, '
                         'line %d, in test_extractStack_wo_frame\n'
                         '    lines = fmt.extractStack()\n' % (lineno + 1))

    def test_extractStack_wo_frame_w_limit(self):
        fmt = self._makeOne(limit=2)
        f = sys._getframe()
        lineno = f.f_lineno
        lines = fmt.extractStack()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[-1], '  Module '
                         'zope.exceptions.tests.test_exceptionformatter, '
                         'line %d, in test_extractStack_wo_frame_w_limit\n'
                         '    lines = fmt.extractStack()\n' % (lineno + 1))

    def test_extractStack_w_single_frame(self):
        fmt = self._makeOne()
        f = DummyFrame()
        lines = fmt.extractStack(f)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], '  Module dummy/filename.py, line 137, '
                                   'in dummy_function\n')

    def test_extractStack_w_multiple_frames_and_limit(self):
        fmt = self._makeOne(limit=2)
        f = self._makeFrames(10)
        lines = fmt.extractStack(f)

        self.assertEqual(len(lines), 3)

        expected = [
            '  Module dummy/filename.py, line 17, in dummy_function\n',
            '...8 entries omitted, because limit is 2...\n',
            '  Module dummy/filename.py, line 1126, in dummy_function\n',
            ]

        self.assertEqual(expected, lines)

    def test_extractStack_w_recursive_frames(self):
        fmt = self._makeOne()
        f = self._makeFrames(3)
        f.f_back.f_locals['__exception_formatter__'] = 1
        lines = fmt.extractStack(f)
        self.assertEqual(len(lines), 4)

        expected = [
            '  File "dummy/filename.py", line 17, in dummy_function\n',
            '  File "dummy/filename.py", line 27, in dummy_function\n',
            '(Recursive extractStack() stopped, trying traceback.format_stack)\n',
            '  Module dummy/filename.py, line 43, in dummy_function\n',
            ]

        self.assertEqual(expected, lines)

    def test_extractStack_w_recursive_frames_and_limit(self):
        fmt = self._makeOne(limit=2)
        f = self._makeFrames(3)
        f.f_back.f_locals['__exception_formatter__'] = 1
        lines = fmt.extractStack(f)
        self.assertEqual(len(lines), 3)

        expected = [
            '  File "dummy/filename.py", line 17, in dummy_function\n',
            '...2 entries omitted, because limit is 2...\n',
            '  Module dummy/filename.py, line 43, in dummy_function\n',
            ]

        self.assertEqual(expected, lines)

    def _makeTBs(self, count):
        prev = None
        for _i in range(count):
            tb = DummyTB()
            tb.tb_lineno = 14
            tb.tb_frame = DummyFrame()
            if prev is not None:
                tb.tb_lineno = int(prev.tb_lineno * 1.9)
                tb.tb_next = prev
            prev = tb
        return tb

    def _makeFrames(self, count):
        prev = None
        for _i in range(count):
            f = DummyFrame()
            f.f_lineno = 17
            if prev is not None:
                f.f_lineno = int(prev.f_lineno * 1.6)
                f.f_back = prev
            prev = f
        return f


class HTMLExceptionFormatterTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.exceptions.exceptionformatter import HTMLExceptionFormatter
        return HTMLExceptionFormatter

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.line_sep, '<br />\r\n')
        self.assertEqual(fmt.limit, None)
        self.assertEqual(fmt.with_filenames, False)

    def test_ctor_explicit(self):
        fmt = self._makeOne(limit=20, with_filenames=True)
        self.assertEqual(fmt.line_sep, '<br />\r\n')
        self.assertEqual(fmt.limit, 20)
        self.assertEqual(fmt.with_filenames, True)

    def test_escape_simple(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.escape('XXX'), 'XXX')

    def test_escape_w_markup(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.escape('<span>XXX & YYY<span>'),
                         '&lt;span&gt;XXX &amp; YYY&lt;span&gt;')

    def test_getPrefix(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.getPrefix(),
                         '<p>Traceback (most recent call last):</p>\r\n<ul>')

    def test_formatSupplementLine(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatSupplementLine('XXX'), '<b>XXX</b>')

    def test_formatSupplementLine_w_markup(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatSupplementLine('XXX & YYY'),
                         '<b>XXX &amp; YYY</b>')

    def test_formatSupplementInfo_simple(self):
        INFO = 'Some days\nI wonder.'
        fmt = self._makeOne()
        self.assertEqual(fmt.formatSupplementInfo(INFO),
                         'Some&nbsp;days<br />\r\nI&nbsp;wonder.')

    def test_formatSupplementInfo_w_markup(self):
        INFO = 'Some days\nI wonder, <b>Why?</b>.'
        fmt = self._makeOne()
        self.assertEqual(fmt.formatSupplementInfo(INFO),
                         'Some&nbsp;days<br />\r\nI&nbsp;wonder,&nbsp;'
                         '&lt;b&gt;Why?&lt;/b&gt;.')

    def test_formatTracebackInfo(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatTracebackInfo('XXX & YYY\nZZZ'),
                         '__traceback_info__: XXX &amp; YYY<br />\r\nZZZ')

    def test_formatLine_simple(self):
        fmt = self._makeOne(with_filenames=True)
        tb = DummyTB()
        tb.tb_frame = f = DummyFrame()
        result = fmt.formatLine(tb)
        self.assertEqual(
            result,
            '<li>  File "%s", line %d, in %s</li>'
            % (f.f_code.co_filename,
               tb.tb_lineno,
               f.f_code.co_name,)
        )

    def test_formatLastLine(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatLastLine('XXX'), '</ul><p>XXX</p>')


class Test_format_exception(unittest.TestCase):

    def _callFUT(self, as_html=False):
        from zope.exceptions.exceptionformatter import format_exception
        t, v, b = sys.exc_info()
        try:
            return ''.join(format_exception(t, v, b, as_html=as_html))
        finally:
            del b

    def test_basic_names_text(self):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        # The traceback should include the name of this function.
        self.assertTrue(s.find('test_basic_names_text') >= 0)
        # The traceback should include the name of the exception.
        self.assertTrue(s.find('ExceptionForTesting') >= 0)

    def test_basic_names_html(self):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # The traceback should include the name of this function.
        self.assertTrue(s.find('test_basic_names_html') >= 0)
        # The traceback should include the name of the exception.
        self.assertTrue(s.find('ExceptionForTesting') >= 0)

    def test_traceback_info_text(self):
        try:
            __traceback_info__ = "Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        self.assertTrue(s.find('Adam & Eve') >= 0, s)

    def test_traceback_info_html(self):
        try:
            __traceback_info__ = "Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # Be sure quoting is happening.
        self.assertTrue(s.find('Adam &amp; Eve') >= 0, s)

    def test_traceback_info_is_tuple(self):
        try:
            __traceback_info__ = ("Adam", "Eve")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        self.assertTrue(s.find('Adam') >= 0, s)
        self.assertTrue(s.find('Eve') >= 0, s)

    def test_supplement_text(self, as_html=0):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        "You're one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(as_html)
        # The source URL
        self.assertTrue(s.find('/somepath') >= 0, s)
        # The line number
        self.assertTrue(s.find('634') >= 0, s)
        # The column number
        self.assertTrue(s.find('57') >= 0, s)
        # The expression
        self.assertTrue(s.find("You're one in a million") >= 0, s)
        # The warning
        self.assertTrue(s.find("Repent, for the end is nigh") >= 0, s)

    def test_supplement_html(self):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        "You're one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # The source URL
        self.assertTrue(s.find('/somepath') >= 0, s)
        # The line number
        self.assertTrue(s.find('634') >= 0, s)
        # The column number
        self.assertTrue(s.find('57') >= 0, s)
        # The expression
        self.assertTrue(s.find("You're one in a million") >= 0, s)
        # The warning
        self.assertTrue(s.find("Repent, for the end is nigh") >= 0, s)

    def test_multiple_levels(self):
        # Ensure many levels are shown in a traceback.
        HOW_MANY = 10
        def f(n):
            """Produces a (n + 1)-level traceback."""
            __traceback_info__ = 'level%d' % n
            if n > 0:
                f(n - 1)
            else:
                raise ExceptionForTesting
        try:
            f(HOW_MANY)
        except ExceptionForTesting:
            s = self._callFUT(False)
        for n in range(HOW_MANY+1):
            self.assertTrue(s.find('level%d' % n) >= 0, s)

    def test_quote_last_line(self):
        class C(object):
            pass
        try:
            raise TypeError(C())
        except TypeError:
            s = self._callFUT(True)
        self.assertIn('&lt;', s)
        self.assertIn('&gt;', s)

    def test_multiline_exception(self):
        try:
            exec('syntax error\n')
        except SyntaxError:
            s = self._callFUT(False)
        lines = s.splitlines()[-3:]
        self.assertEqual(lines[0], '    syntax error')
        self.assertTrue(lines[1].endswith('    ^')) #PyPy has a shorter prefix
        self.assertEqual(lines[2], 'SyntaxError: invalid syntax')

    def test_traceback_info_non_ascii(self):
        __traceback_info__ = u"Have a Snowman: \u2603"
        try:
            raise TypeError()
        except TypeError:
            s = self._callFUT(True)

        self.assertIsInstance(s, str)
        self.assertIn('Have a Snowman', s)


    def test_recursion_failure(self):
        from zope.exceptions.exceptionformatter import TextExceptionFormatter

        class FormatterException(Exception):
            pass

        class FailingFormatter(TextExceptionFormatter):
            def formatLine(self, tb=None, f=None):
                raise FormatterException("Formatter failed")

        fmt = FailingFormatter()
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            try:
                fmt.formatException(*sys.exc_info())
            except FormatterException:
                s = self._callFUT(False)
        # Recursion was detected
        self.assertTrue('(Recursive formatException() stopped, '
                        'trying traceback.format_tb)' in s, s)
        # and we fellback to the stdlib rather than hid the real error
        self.assertEqual(s.splitlines()[-2],
                         '    raise FormatterException("Formatter failed")')
        self.assertTrue('FormatterException: Formatter failed'
                        in s.splitlines()[-1])

    def test_format_exception_as_html(self):
        # Test for format_exception (as_html=True)
        from zope.exceptions.exceptionformatter import format_exception
        from textwrap import dedent
        import re
        try:
            exec('import')
        except SyntaxError:
            result = ''.join(format_exception(*sys.exc_info(), as_html=True))
        expected = dedent("""\
            <p>Traceback (most recent call last):</p>
            <ul>
            <li>  Module zope.exceptions.tests.test_exceptionformatter, line ABC, in test_format_exception_as_html<br />
                exec('import')</li>
            </ul><p>  File "&lt;string&gt;", line 1<br />
                import<br />
                     ^<br />
            SyntaxError: invalid syntax<br />
            </p>""")
        # HTML formatter uses Windows line endings for some reason.
        result = result.replace('\r\n', '\n')
        result = re.sub(r'line \d\d\d,', 'line ABC,', result)
        self.maxDiff = None
        self.assertEqual(expected, result)


class Test_print_exception(unittest.TestCase):

    def _callFUT(self, as_html=False):
        import io
        buf = io.StringIO() if bytes is not str else io.BytesIO()

        from zope.exceptions.exceptionformatter import print_exception
        t, v, b = sys.exc_info()
        try:
            print_exception(t, v, b, file=buf, as_html=as_html)
            return buf.getvalue()
        finally:
            del b

    def test_basic_names_text(self):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        # The traceback should include the name of this function.
        self.assertTrue(s.find('test_basic_names_text') >= 0)
        # The traceback should include the name of the exception.
        self.assertTrue(s.find('ExceptionForTesting') >= 0)

    def test_basic_names_html(self):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # The traceback should include the name of this function.
        self.assertTrue(s.find('test_basic_names_html') >= 0)
        # The traceback should include the name of the exception.
        self.assertTrue(s.find('ExceptionForTesting') >= 0)


class Test_extract_stack(unittest.TestCase):

    def _callFUT(self, as_html=False):
        from zope.exceptions.exceptionformatter import extract_stack
        f = sys.exc_info()[2].tb_frame
        try:
            return ''.join(extract_stack(f, as_html=as_html))
        finally:
            del f

    def test_basic_names_as_text(self, as_html=0):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        # The stack trace should include the name of this function.
        self.assertTrue(s.find('test_basic_names_as_text') >= 0)

    def test_basic_names_as_html(self):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # The stack trace should include the name of this function.
        self.assertTrue(s.find('test_basic_names_as_html') >= 0)

    def test_traceback_info_text(self):
        try:
            __traceback_info__ = "Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        self.assertTrue(s.find('Adam & Eve') >= 0, s)

    def test_traceback_info_html(self):
        try:
            __traceback_info__ = u"Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        self.assertTrue(s.find('Adam &amp; Eve') >= 0, s)

    def test_traceback_supplement_text(self):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        u"You're one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        # The source URL
        self.assertTrue(s.find('/somepath') >= 0, s)
        # The line number
        self.assertTrue(s.find('634') >= 0, s)
        # The column number
        self.assertTrue(s.find('57') >= 0, s)
        # The expression
        self.assertTrue(s.find("You're one in a million") >= 0, s)
        # The warning
        self.assertTrue(s.find("Repent, for the end is nigh") >= 0, s)

    def test_traceback_supplement_html(self):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        "You're one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # The source URL
        self.assertTrue(s.find('/somepath') >= 0, s)
        # The line number
        self.assertTrue(s.find('634') >= 0, s)
        # The column number
        self.assertTrue(s.find('57') >= 0, s)
        # The expression
        self.assertTrue(s.find("You're one in a million") >= 0, s)
        # The warning
        self.assertTrue(s.find("Repent, for the end is nigh") >= 0, s)

    def test_noinput(self):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            from zope.exceptions.exceptionformatter import extract_stack
            s = ''.join(extract_stack())
            self.assertTrue(s.find('test_noinput') >= 0)


class ExceptionForTesting(Exception):
    pass


class TestingTracebackSupplement(object):
    source_url = '/somepath'
    line = 634
    column = 57
    warnings = ['Repent, for the end is nigh']
    def __init__(self, expression):
        self.expression = expression


class DummySupplement(object):
    def __init__(self, info=''):
        self._info = info
    def getInfo(self):
        return self._info


class DummyTB(object):
    tb_lineno = 14
    tb_next = None


class DummyFrame(object):
    f_lineno = 137
    f_back = None
    def __init__(self):
        self.f_locals = {}
        self.f_globals = {}
        self.f_code = DummyCode()

class DummyCode(object):
    co_filename = 'dummy/filename.py'
    co_name = 'dummy_function'

class _Monkey(object):
    # context-manager for replacing module names in the scope of a test.
    def __init__(self, module, **kw):
        self.module = module
        self.to_restore = {key: getattr(module, key, self)
                           for key in kw}
        for key, value in kw.items():
            setattr(module, key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key, value in self.to_restore.items():
            if value is not self: # pragma: no cover
                setattr(self.module, key, value)
            else:
                delattr(self.module, key)




def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
