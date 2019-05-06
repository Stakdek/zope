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
"""An exception formatter that shows traceback supplements and traceback info,
optionally in HTML.
"""
import sys
try:
    from html import escape
except ImportError:
    from cgi import escape
import linecache
import traceback

DEBUG_EXCEPTION_FORMATTER = 1


class TextExceptionFormatter(object):

    line_sep = '\n'

    def __init__(self, limit=None, with_filenames=False):
        self.limit = limit
        self.with_filenames = with_filenames

    def escape(self, s):
        return s

    def getPrefix(self):
        return 'Traceback (most recent call last):'

    def getLimit(self):
        limit = self.limit
        if limit is None:
            limit = getattr(sys, 'tracebacklimit', 200)
        return limit

    def formatSupplementLine(self, line):
        result = '   - %s' % line
        if not isinstance(result, str):
            # Must be an Python 2, and must be a unicode `line`
            # and we upconverted the result to a unicode
            result = result.encode('utf-8')
        return result

    def formatSourceURL(self, url):
        return [self.formatSupplementLine(url)]

    def formatSupplement(self, supplement, tb):
        result = []
        fmtLine = self.formatSupplementLine

        url = getattr(supplement, 'source_url', None)
        if url is not None:
            result.extend(self.formatSourceURL(url))

        line = getattr(supplement, 'line', 0)
        if line == -1:
            line = tb.tb_lineno
        col = getattr(supplement, 'column', -1)
        if line:
            if col is not None and col >= 0:
                result.append(fmtLine('Line %s, Column %s' % (
                    line, col)))
            else:
                result.append(fmtLine('Line %s' % line))
        elif col is not None and col >= 0:
            result.append(fmtLine('Column %s' % col))

        expr = getattr(supplement, 'expression', None)
        if expr:
            result.append(fmtLine('Expression: %s' % expr))

        warnings = getattr(supplement, 'warnings', None)
        if warnings:
            for warning in warnings:
                result.append(fmtLine('Warning: %s' % warning))

        getInfo = getattr(supplement, 'getInfo', None)
        if getInfo is not None:
            try:
                extra = getInfo()
                if extra:
                    result.append(self.formatSupplementInfo(extra))
            except: #pragma: no cover
                if DEBUG_EXCEPTION_FORMATTER:
                    traceback.print_exc()
                # else just swallow the exception.
        return result

    def formatSupplementInfo(self, info):
        return self.escape(info)

    def formatTracebackInfo(self, tbi):
        return self.formatSupplementLine('__traceback_info__: %s' % (tbi, ))

    def formatLine(self, tb=None, f=None):
        if tb and not f:
            f = tb.tb_frame
            lineno = tb.tb_lineno
        elif not tb and f:
            lineno = f.f_lineno
        else:
            raise ValueError("Pass exactly one of tb or f")
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        f_locals = f.f_locals
        f_globals = f.f_globals

        if self.with_filenames:
            s = '  File "%s", line %d' % (filename, lineno)
        else:
            modname = f_globals.get('__name__', filename)
            s = '  Module %s, line %d' % (modname, lineno)

        s = s + ', in %s' % name

        result = []
        result.append(self.escape(s))

        # Append the source line, if available
        line = linecache.getline(filename, lineno)
        if line:
            result.append("    " + self.escape(line.strip()))

        # Output a traceback supplement, if any.
        if '__traceback_supplement__' in f_locals:
            # Use the supplement defined in the function.
            tbs = f_locals['__traceback_supplement__']
        elif '__traceback_supplement__' in f_globals:
            # Use the supplement defined in the module.
            # This is used by Scripts (Python).
            tbs = f_globals['__traceback_supplement__']
        else:
            tbs = None
        if tbs is not None:
            factory = tbs[0]
            args = tbs[1:]
            try:
                supp = factory(*args)
                result.extend(self.formatSupplement(supp, tb))
            except: #pragma: no cover
                if DEBUG_EXCEPTION_FORMATTER:
                    traceback.print_exc()
                # else just swallow the exception.

        try:
            tbi = f_locals.get('__traceback_info__', None)
            if tbi is not None:
                result.append(self.formatTracebackInfo(tbi))
        except: #pragma: no cover
            if DEBUG_EXCEPTION_FORMATTER:
                traceback.print_exc()
            # else just swallow the exception.

        return self.line_sep.join(result)

    def formatExceptionOnly(self, etype, value):
        result = ''.join(traceback.format_exception_only(etype, value))
        return result

    def formatLastLine(self, exc_line):
        return self.escape(exc_line)

    def formatException(self, etype, value, tb):
        # The next line provides a way to detect recursion.
        __exception_formatter__ = 1
        result = []
        while tb is not None:
            if tb.tb_frame.f_locals.get('__exception_formatter__'):
                # Stop recursion.
                result.append('(Recursive formatException() stopped, '
                              'trying traceback.format_tb)\n')
                result.extend(traceback.format_tb(tb))
                break
            line = self.formatLine(tb=tb)
            result.append(line + '\n')
            tb = tb.tb_next
        template = (
            '...\n'
            '{omitted} entries omitted, because limit is {limit}.\n'
            'Set sys.tracebacklimit or {klass}.limit to a higher'
            ' value to see omitted entries\n'
            '...')
        self._obeyLimit(result, template)
        result = [self.getPrefix() + '\n'] + result
        exc_line = self.formatExceptionOnly(etype, value)
        result.append(self.formatLastLine(exc_line))
        return result

    def extractStack(self, f=None):
        if f is None:
            try:
                raise ZeroDivisionError
            except ZeroDivisionError:
                f = sys.exc_info()[2].tb_frame.f_back

        # The next line provides a way to detect recursion.
        __exception_formatter__ = 1
        result = []
        while f is not None:
            if f.f_locals.get('__exception_formatter__'):
                # Stop recursion.
                result.append('(Recursive extractStack() stopped, '
                              'trying traceback.format_stack)\n')
                res = traceback.format_stack(f)
                res.reverse()
                result.extend(res)
                break
            line = self.formatLine(f=f)
            result.append(line + '\n')
            f = f.f_back

        self._obeyLimit(
            result,
            '...{omitted} entries omitted, because limit is {limit}...\n')
        result.reverse()
        return result

    def _obeyLimit(self, result, template):
        limit = self.getLimit()
        if limit is not None and len(result) > limit:
            # cut out the middle part of the TB
            tocut = len(result) - limit
            middle = len(result) // 2
            lower = middle - tocut // 2
            msg = template.format(
                omitted=tocut, limit=limit, klass=self.__class__.__name__)
            result[lower:lower + tocut] = [msg]


class HTMLExceptionFormatter(TextExceptionFormatter):

    line_sep = '<br />\r\n'

    def escape(self, s):
        if not isinstance(s, str):
            try:
                s = str(s)
            except UnicodeError:
                if hasattr(s, 'encode'):
                    # We probably got a unicode string on
                    # Python 2.
                    s = s.encode('utf-8')
                else: # pragma: no cover
                    raise
        return escape(s, quote=False)

    def getPrefix(self):
        return '<p>Traceback (most recent call last):</p>\r\n<ul>'

    def formatSupplementLine(self, line):
        return '<b>%s</b>' % self.escape(line)

    def formatSupplementInfo(self, info):
        info = self.escape(info)
        info = info.replace(" ", "&nbsp;")
        info = info.replace("\n", self.line_sep)
        return info

    def formatTracebackInfo(self, tbi):
        s = self.escape(tbi)
        s = s.replace('\n', self.line_sep)
        return '__traceback_info__: %s' % (s, )

    def formatLine(self, tb=None, f=None):
        line = TextExceptionFormatter.formatLine(self, tb, f)
        return '<li>%s</li>' % line

    def formatLastLine(self, exc_line):
        line = '</ul><p>%s</p>' % self.escape(exc_line)
        return line.replace('\n', self.line_sep)


def format_exception(t, v, tb, limit=None, as_html=False,
                     with_filenames=False):
    """Format a stack trace and the exception information.

    Similar to 'traceback.format_exception', but adds supplemental
    information to the traceback and accepts two options, 'as_html'
    and 'with_filenames'.

    The result is a list of native strings; on Python 2 they are UTF-8
    encoded if need be.
    """
    if as_html:
        fmt = HTMLExceptionFormatter(limit, with_filenames)
    else:
        fmt = TextExceptionFormatter(limit, with_filenames)
    return fmt.formatException(t, v, tb)


def print_exception(t, v, tb, limit=None, file=None, as_html=False,
                    with_filenames=True):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    Similar to 'traceback.print_exception', but adds supplemental
    information to the traceback and accepts two options, 'as_html'
    and 'with_filenames'.
    """
    if file is None: # pragma: no cover
        file = sys.stderr
    lines = format_exception(t, v, tb, limit, as_html, with_filenames)
    for line in lines:
        file.write(line)


def extract_stack(f=None, limit=None, as_html=False,
                  with_filenames=True):
    """Format a stack trace and the exception information.

    Similar to 'traceback.extract_stack', but adds supplemental
    information to the traceback and accepts two options, 'as_html'
    and 'with_filenames'.
    """
    if as_html:
        fmt = HTMLExceptionFormatter(limit, with_filenames)
    else:
        fmt = TextExceptionFormatter(limit, with_filenames)
    return fmt.extractStack(f)
