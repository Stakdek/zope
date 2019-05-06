#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2001, 2002, 2013 Zope Foundation and Contributors.
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
"""Driver program to test METAL and TAL implementation:
interprets a file, prints results to stdout.
"""

from __future__ import print_function

import os
import optparse
import sys

# Import local classes
import zope.tal.taldefs
from zope.tal.dummyengine import DummyEngine
from zope.tal.dummyengine import DummyTranslationDomain


class TestTranslations(DummyTranslationDomain):
    def translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        if msgid == 'timefmt':
            return '%(minutes)s minutes after %(hours)s %(ampm)s' % mapping
        elif msgid == 'jobnum':
            return '%(jobnum)s is the JOB NUMBER' % mapping
        elif msgid == 'verify':
            s = 'Your contact email address is recorded as %(email)s'
            return s % mapping
        elif msgid == 'mailto:${request/submitter}':
            return 'mailto:bperson@dom.ain'
        elif msgid == 'origin':
            return '%(name)s was born in %(country)s' % mapping
        return DummyTranslationDomain.translate(
            self, msgid, mapping, context,
            target_language, default=default)


class TestEngine(DummyEngine):
    def __init__(self, macros=None):
        DummyEngine.__init__(self, macros)
        self.translationDomain = TestTranslations()

    def evaluatePathOrVar(self, expr):
        if expr == 'here/currentTime':
            return {'hours'  : 6,
                    'minutes': 59,
                    'ampm'   : 'PM',
                    }
        elif expr == 'context/@@object_name':
            return '7'
        elif expr == 'request/submitter':
            return 'aperson@dom.ain'
        return DummyEngine.evaluatePathOrVar(self, expr)


# This is a disgusting hack so that we can use engines that actually know
# something about certain object paths.
ENGINES = {'test23.html': TestEngine,
           'test24.html': TestEngine,
           'test26.html': TestEngine,
           'test27.html': TestEngine,
           'test28.html': TestEngine,
           'test29.html': TestEngine,
           'test30.html': TestEngine,
           'test31.html': TestEngine,
           'test32.html': TestEngine,
           }


OPTIONS = [
    optparse.make_option('-H', '--html',
            action='store_const', const='html', dest='mode',
            help='explicitly choose HTML input (default: use file extension)'),
    optparse.make_option('-x', '--xml',
            action='store_const', const='xml', dest='mode',
            help='explicitly choose XML input (default: use file extension)'),
    optparse.make_option('-l', '--lenient', action='store_true',
            help='lenient structure insertion'),
            # aka don't validate HTML/XML inserted by
            # tal:content="structure expr"
    optparse.make_option('-m', '--macro-only', action='store_true',
            help='macro expansion only'),
    optparse.make_option('-s', '--show-code', action='store_true',
            help='print intermediate opcodes only'),
    optparse.make_option('-t', '--show-tal', action='store_true',
            help='leave TAL/METAL attributes in output'),
    optparse.make_option('-i', '--show-i18n', action='store_true',
            help='leave I18N substitution string un-interpolated'),
    optparse.make_option('-a', '--annotate', action='store_true',
            help='enable source annotations'),
]

def main(values=None):
    parser = optparse.OptionParser('usage: %prog [options] testfile',
                                   description=__doc__,
                                   option_list=OPTIONS)
    opts, args = parser.parse_args(values=values)
    if not args:
        parser.print_help()
        sys.exit(1)
    if len(args) > 1:
        parser.error('Too many arguments')
    file = args[0]

    it = compilefile(file, opts.mode)
    if opts.show_code:
        showit(it)
    else:
        # See if we need a special engine for this test
        engine = None
        engineClass = ENGINES.get(os.path.basename(file))
        if engineClass is not None:
            engine = engineClass(opts.macro_only)
        interpretit(it, engine=engine,
                    tal=not opts.macro_only,
                    showtal=1 if opts.show_tal else -1,
                    strictinsert=not opts.lenient,
                    i18nInterpolate=not opts.show_i18n,
                    sourceAnnotations=opts.annotate)

def interpretit(it, engine=None, stream=None, tal=1, showtal=-1,
                strictinsert=1, i18nInterpolate=1, sourceAnnotations=0):
    from zope.tal.talinterpreter import TALInterpreter
    program, macros = it
    assert zope.tal.taldefs.isCurrentVersion(program)
    if engine is None:
        engine = DummyEngine(macros)
    TALInterpreter(program, macros, engine, stream, wrap=0,
                   tal=tal, showtal=showtal, strictinsert=strictinsert,
                   i18nInterpolate=i18nInterpolate,
                   sourceAnnotations=sourceAnnotations)()

def compilefile(file, mode=None):
    assert mode in ("html", "xml", None)
    if mode is None:
        ext = os.path.splitext(file)[1]
        if ext.lower() in (".html", ".htm"):
            mode = "html"
        else:
            mode = "xml"
    # make sure we can find the file
    prefix = os.path.dirname(os.path.abspath(__file__)) + os.path.sep
    if (not os.path.exists(file)
        and os.path.exists(os.path.join(prefix, file))):
        file = os.path.join(prefix, file)
    # normalize filenames for test output
    filename = os.path.abspath(file)
    if filename.startswith(prefix):
        filename = filename[len(prefix):]
    filename = filename.replace(os.sep, '/') # test files expect slashes
    # parse
    from zope.tal.talgenerator import TALGenerator
    if mode == "html":
        from zope.tal.htmltalparser import HTMLTALParser
        p = HTMLTALParser(gen=TALGenerator(source_file=filename, xml=0))
    else:
        from zope.tal.talparser import TALParser
        p = TALParser(gen=TALGenerator(source_file=filename))
    p.parseFile(file)
    return p.getCode()

def showit(it):
    from pprint import pprint
    pprint(it)

if __name__ == "__main__":
    main()
