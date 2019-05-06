##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
"""Test Browser Widget
"""
import unittest


class FormBaseTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.formlib.form import FormBase
        return FormBase

    def _makeContext(self, **kw):
        class _Context(object):
            pass
        context = _Context()
        for k, v in kw.items():
            setattr(context, k, v)
        return context

    def _makeRequest(self, **kw):
        from zope.publisher.browser import TestRequest
        return TestRequest(**kw)

    def _makeOne(self, context=None, request=None):
        if context is None:
            context = self._makeContext()
        if request is None:
            request = self._makeRequest()
        return self._getTargetClass()(context, request)

    def test___call___does_not_render_on_redirects(self):
        for status in (301, 302, 303, 307):
            request = self._makeRequest()
            request.response.setStatus(status)
            def _raise(*args, **kw):
                self.fail("DON'T GO HERE")
            form = self._makeOne(request=request)
            form.form_fields = form.actions = ()
            form.template = _raise
            self.assertEqual(form(), '')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FormBaseTests),
    ))
