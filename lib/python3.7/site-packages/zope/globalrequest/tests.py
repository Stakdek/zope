# -*- coding: utf-8 -*-
import unittest


class TestGlobalrequest(unittest.TestCase):

    def tearDown(self):
        # reset the threading local context
        from threading import local
        import zope.globalrequest.local
        zope.globalrequest.local.localData = local()

    def test_unset_local(self):
        # test with unset values
        import zope.globalrequest.local
        self.assertIs(zope.globalrequest.local.getLocal('unsetkey'), None)

    def test_set_get_local(self):
        # test with simple values
        import zope.globalrequest.local
        zope.globalrequest.local.setLocal('testkey', 'testvalue')
        self.assertIs(
            zope.globalrequest.local.getLocal('testkey'),
            'testvalue'
        )

    def test_unset_local_with_factory(self):
        # test with a factory given and marker set/not set
        dummy_default = 'dummy_test_default_value'

        def dummy_default_factory():
            return dummy_default

        import zope.globalrequest.local

        self.assertEqual(
            zope.globalrequest.local.getLocal(
                'testdefaultkey',
                factory=dummy_default_factory
            ),
            dummy_default
        )

    def test_unset_global_request(self):
        # get w/o any value set returns None
        import zope.globalrequest
        self.assertIs(zope.globalrequest.getRequest(), None)

    def test_set_get_globalrequest(self):
        # set a value and get it back
        import zope.globalrequest
        test_request = dict(value='I am a dummy request')
        zope.globalrequest.setRequest(test_request)
        self.assertIs(zope.globalrequest.getRequest(), test_request)

    def test_clear_global_request(self):
        # set a value and get it back
        import zope.globalrequest
        test_request = dict(value='I am a dummy request')
        zope.globalrequest.setRequest(test_request)
        zope.globalrequest.clearRequest()
        self.assertIs(zope.globalrequest.getRequest(), None)

    def test_set_subscriber(self):
        import zope.globalrequest.subscribers
        test_request = dict(value='I am a dummy request')

        class DummyEvent(object):
            request = test_request

        dummy_event = DummyEvent()

        # test set
        zope.globalrequest.subscribers.set(None, dummy_event)
        self.assertIs(zope.globalrequest.getRequest(), test_request)

    def test_clear_subscriber(self):
        import zope.globalrequest.subscribers
        test_request = dict(value='I am a dummy request')

        class DummyEvent(object):
            request = test_request

        dummy_event = DummyEvent()

        # test clear
        zope.globalrequest.subscribers.set(None, dummy_event)
        zope.globalrequest.subscribers.clearRequest()
        self.assertIs(zope.globalrequest.getRequest(), None)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
