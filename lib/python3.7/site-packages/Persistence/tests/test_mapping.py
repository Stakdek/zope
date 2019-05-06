import unittest


class PersistentMappingTests(unittest.TestCase):

    def _getTargetClass(self):
        from Persistence import PersistentMapping
        return PersistentMapping

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test___setstate__(self):
        m = self._makeOne()
        m.__setstate__({'data': {'x': 1, 'y': 2}})
        self.assertEqual(sorted(m.items()), [('x', 1), ('y', 2)])

    def test___setstate___old_pickles(self):
        m = self._makeOne()
        m.__setstate__({'_container': {'x': 1, 'y': 2}})
        self.assertEqual(sorted(m.items()), [('x', 1), ('y', 2)])

    def test_subclass(self):
        klass = self._getTargetClass()

        class Dummy(klass):
            def __init__(self, *args, **kw):
                self._value = []
                klass.__init__(self, *args, **kw)

        self.assertTrue(issubclass(Dummy, klass))

        dummy = Dummy()
        self.assertTrue(isinstance(dummy, Dummy))
        self.assertTrue(isinstance(dummy, klass))
