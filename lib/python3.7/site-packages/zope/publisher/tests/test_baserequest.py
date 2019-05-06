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
"""baserequest tests
"""
from unittest import TestCase, main, makeSuite

from zope.publisher.tests.basetestipublicationrequest \
     import BaseTestIPublicationRequest

from zope.publisher.tests.basetestipublisherrequest \
     import BaseTestIPublisherRequest

from zope.publisher.tests.basetestiapplicationrequest \
     import BaseTestIApplicationRequest

from io import BytesIO
from zope.interface import Interface, providedBy, alsoProvides
from zope.component import provideAdapter

class TestBaseRequest(BaseTestIPublicationRequest,
                      BaseTestIApplicationRequest,
                      BaseTestIPublisherRequest,
                      TestCase):

    def _Test__new(self, **kw):
        from zope.publisher.base import BaseRequest
        return BaseRequest(BytesIO(), kw)

    def _Test__expectedViewType(self):
        return None # we don't expect

    def test_bool_empty(self):
        self.assertTrue(self._Test__new())

    def test_IApplicationRequest_bodyStream(self):
        from zope.publisher.base import BaseRequest

        request = BaseRequest(BytesIO(b'spam'), {})
        self.assertEqual(request.bodyStream.read(), b'spam')

    def test_IPublicationRequest_getPositionalArguments(self):
        self.assertEqual(self._Test__new().getPositionalArguments(), ())

    def test_IPublisherRequest_retry(self):
        self.assertEqual(self._Test__new().supportsRetry(), 0)

    def test_IPublisherRequest_traverse(self):
        from zope.publisher.tests.publication import TestPublication
        request = self._Test__new()
        request.setPublication(TestPublication())
        app = request.publication.getApplication(request)

        request.setTraversalStack([])
        self.assertEqual(request.traverse(app).name, '')
        self.assertEqual(request._last_obj_traversed, app)
        request.setTraversalStack(['ZopeCorp'])
        self.assertEqual(request.traverse(app).name, 'ZopeCorp')
        self.assertEqual(request._last_obj_traversed, app.ZopeCorp)
        request.setTraversalStack(['Engineering', 'ZopeCorp'])
        self.assertEqual(request.traverse(app).name, 'Engineering')
        self.assertEqual(request._last_obj_traversed, app.ZopeCorp.Engineering)

    def test_IPublisherRequest_processInputs(self):
        self._Test__new().processInputs()

    def test_AnnotationsExist(self):
        self.assertEqual(self._Test__new().annotations, {})

    # Needed by BaseTestIEnumerableMapping tests:
    def _IEnumerableMapping__stateDict(self):
        return {'id': 'ZopeOrg', 'title': 'Zope Community Web Site',
                'greet': 'Welcome to the Zope Community Web site'}

    def _IEnumerableMapping__sample(self):
        return self._Test__new(**(self._IEnumerableMapping__stateDict()))

    def _IEnumerableMapping__absentKeys(self):
        return 'foo', 'bar'

    def test_SetRequestInResponse(self):
        request = self._Test__new()
        self.assertEqual(request.response._request, request)

    def test_retry_keeps_everything(self):
        """lowlevel test for retry (see #98440)"""
        from zope.publisher.browser import TestRequest
        from zope.publisher.skinnable import setDefaultSkin
        from zope.publisher.interfaces import IDefaultSkin
        from zope.publisher.interfaces.browser import IBrowserRequest
        from zope.publisher.interfaces.browser import IBrowserSkinType
        # create a retryable request
        request = TestRequest()
        self.assertTrue(request.supportsRetry())
        # create a skin and register it as the default skin
        class ISomeSkin(Interface):
            pass
        alsoProvides(ISomeSkin, IBrowserSkinType)
        provideAdapter(ISomeSkin, (IBrowserRequest,), IDefaultSkin)
        # set the default skin for the request
        setDefaultSkin(request)

        # create a retried request
        retried = request.retry()

        # the requests are not the same
        self.assertTrue(request is not retried)
        # the requests both provide the default skin
        self.assertTrue(ISomeSkin.providedBy(request))
        self.assertTrue(ISomeSkin.providedBy(retried))


def test_suite():
    return makeSuite(TestBaseRequest)

if __name__=='__main__':
    main(defaultTest='test_suite')
