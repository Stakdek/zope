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
"""Page Template HTML Tests
"""
import unittest

from zope.pagetemplate.tests import util
from zope.pagetemplate.pagetemplate import PageTemplate


class Folder(object):
    context = property(lambda self: self)

class HTMLTests(unittest.TestCase):

    def setUp(self):
        self.folder = f = Folder()
        f.laf = PageTemplate()
        f.t = PageTemplate()

    def getProducts(self):
        return [
            {
                'description': ('This is the tee for those who LOVE Zope. '
                                'Show your heart on your tee.'),
                'price': 12.99, 'image': 'smlatee.jpg'
            },
            {
                'description': ('This is the tee for Jim Fulton. '
                                'He\'s the Zope Pope!'),
                'price': 11.99, 'image': 'smpztee.jpg'
            },
        ]

    def test_1(self):
        laf = self.folder.laf
        laf.write(util.read_input('teeshoplaf.html'))
        expect = util.read_output('teeshoplaf.html')
        util.check_html(expect, laf())

    def test_2(self):
        self.folder.laf.write(util.read_input('teeshoplaf.html'))

        t = self.folder.t
        t.write(util.read_input('teeshop2.html'))
        expect = util.read_output('teeshop2.html')
        out = t(laf=self.folder.laf, getProducts=self.getProducts)
        util.check_html(expect, out)


    def test_3(self):
        self.folder.laf.write(util.read_input('teeshoplaf.html'))

        t = self.folder.t
        t.write(util.read_input('teeshop1.html'))
        expect = util.read_output('teeshop1.html')
        out = t(laf=self.folder.laf, getProducts=self.getProducts)
        util.check_html(expect, out)

    def test_SimpleLoop(self):
        t = self.folder.t
        t.write(util.read_input('loop1.html'))
        expect = util.read_output('loop1.html')
        out = t()
        util.check_html(expect, out)

    def test_GlobalsShadowLocals(self):
        t = self.folder.t
        t.write(util.read_input('globalsshadowlocals.html'))
        expect = util.read_output('globalsshadowlocals.html')
        out = t()
        util.check_html(expect, out)

    def test_StringExpressions(self):
        t = self.folder.t
        t.write(util.read_input('stringexpression.html'))
        expect = util.read_output('stringexpression.html')
        out = t()
        util.check_html(expect, out)

    def test_ReplaceWithNothing(self):
        t = self.folder.t
        t.write(util.read_input('checknothing.html'))
        expect = util.read_output('checknothing.html')
        out = t()
        util.check_html(expect, out)

    def test_WithXMLHeader(self):
        t = self.folder.t
        t.write(util.read_input('checkwithxmlheader.html'))
        expect = util.read_output('checkwithxmlheader.html')
        out = t()
        util.check_html(expect, out)

    def test_NotExpression(self):
        t = self.folder.t
        t.write(util.read_input('checknotexpression.html'))
        expect = util.read_output('checknotexpression.html')
        out = t()
        util.check_html(expect, out)

    def test_PathNothing(self):
        t = self.folder.t
        t.write(util.read_input('checkpathnothing.html'))
        expect = util.read_output('checkpathnothing.html')
        out = t()
        util.check_html(expect, out)

    def test_PathAlt(self):
        t = self.folder.t
        t.write(util.read_input('checkpathalt.html'))
        expect = util.read_output('checkpathalt.html')
        out = t()
        util.check_html(expect, out)

    def test_translation(self):
        from zope.i18nmessageid import MessageFactory
        _ = MessageFactory('pttest')
        msg = _("Translate this!")

        t = self.folder.t
        t.write(util.read_input('translation.html'))
        expect = util.read_output('translation.html')
        out = t(msg=msg)
        util.check_html(expect, out)

    def test_recursion(self):
        t = self.folder.t
        t.write(util.read_input('recursive.html'))
        expect = util.read_output('recursive.html')
        context = dict(name='root',
                       children=[dict(name='first', children=[]),
                                 dict(name='second', children=[])])
        namespace = dict(template=t, options={}, args=(),
                         nothing=None, context=context)
        out = t.pt_render(namespace)
        # crude way of normalizing whitespace
        expect = expect.replace(' ', '').replace('\n\n', '\n')
        out = out.replace(' ', '').replace('\n\n', '\n')
        util.check_html(expect, out)
        # https://bugs.launchpad.net/zope.pagetemplate/+bug/732972
        errors = t.pt_errors(namespace, check_macro_expansion=False)
        self.assertFalse(errors)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
