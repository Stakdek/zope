import unittest

from Missing import PY3
from Missing import PY35

if PY3:
    def u(value):
        return str(value, 'utf-8')
    long = int
else:
    def u(value):
        return unicode(value, 'utf-8')  # NOQA: F821


class ValueTests(object):

    def test_cmp(self):
        value = self._make_one()
        self.assertNotEqual(value, 12)
        self.assertNotEqual(12, value)
        self.assertNotEqual(value, b'abc')
        self.assertNotEqual(b'abc', value)
        self.assertNotEqual(value, u(b'abc'))
        self.assertNotEqual(u(b'abc'), value)

    def test_lt(self):
        value = self._make_one()
        self.assertTrue(1 < value)
        self.assertFalse(value < 1)
        self.assertFalse(value < value)

    def test_le(self):
        value = self._make_one()
        self.assertTrue(1 <= value)
        self.assertFalse(value <= 1)
        self.assertTrue(value <= value)

    def test_eq(self):
        value = self._make_one()
        self.assertFalse(1 == value)
        self.assertFalse(value == 1)
        self.assertTrue(value == value)

    def test_ne(self):
        value = self._make_one()
        self.assertTrue(1 != value)
        self.assertTrue(value != 1)
        self.assertFalse(value != value)

    def test_gt(self):
        value = self._make_one()
        self.assertFalse(1 > value)
        self.assertTrue(value > 1)
        self.assertFalse(value > value)

    def test_ge(self):
        value = self._make_one()
        self.assertFalse(1 >= value)
        self.assertTrue(value >= 1)
        self.assertTrue(value >= value)

    def test_add(self):
        value = self._make_one()
        self.assertEqual(1 + value, value)
        self.assertEqual(value + 1, value)
        self.assertEqual(value, 1 + value)
        self.assertEqual(value, value + 1)

    def test_sub(self):
        value = self._make_one()
        self.assertEqual(1 - value, value)
        self.assertEqual(value - 1, value)
        self.assertEqual(value, 1 - value)
        self.assertEqual(value, value - 1)

    @unittest.skipUnless(PY35, 'Python 3.5+ syntax')
    def test_matmul(self):
        value = self._make_one()

        class Dummy(object):
            def __init__(self, value):
                self.value = value

            def __matmul__(self, other):
                return self.value * other

            def __rmatmul__(self, other):
                return self.value * other

        def matmul(a, b):
            # Don't use the @ operator to avoid SyntaxError's
            return a.__matmul__(b)

        dummy = Dummy(2)
        self.assertEqual(matmul(dummy, value), value)
        self.assertEqual(matmul(value, dummy), value)
        self.assertEqual(value, matmul(dummy, value))
        self.assertEqual(value, matmul(value, dummy))

    def test_mul(self):
        value = self._make_one()
        self.assertEqual(2 * value, value)
        self.assertEqual(value * 2, value)
        self.assertEqual(value, 2 * value)
        self.assertEqual(value, value * 2)

    def test_div(self):
        value = self._make_one()
        self.assertEqual(2 / value, value)
        self.assertEqual(value / 2, value)
        self.assertEqual(value, 2 / value)
        self.assertEqual(value, value / 2)

    def test_integer_div(self):
        value = self._make_one()
        self.assertEqual(2 // value, value)
        self.assertEqual(value // 2, value)
        self.assertEqual(value, 2 // value)
        self.assertEqual(value, value // 2)

    def test_mod(self):
        value = self._make_one()
        self.assertEqual(2 % value, value)
        self.assertEqual(value % 2, value)
        self.assertEqual(value, 2 % value)
        self.assertEqual(value, value % 2)

    def test_divmod(self):
        value = self._make_one()
        self.assertEqual(divmod(2, value), value)
        self.assertEqual(divmod(value, 2), value)
        self.assertEqual(value, divmod(2, value))
        self.assertEqual(value, divmod(value, 2))

    def test_pow(self):
        value = self._make_one()
        self.assertEqual(2 ** value, value)
        self.assertEqual(value ** 2, value)
        self.assertEqual(value, 2 ** value)
        self.assertEqual(value, value ** 2)

    def test_neg(self):
        value = self._make_one()
        self.assertEqual(-value, value)
        self.assertEqual(value, -value)

    def test_pos(self):
        value = self._make_one()
        self.assertEqual(+value, value)
        self.assertEqual(value, +value)

    def test_abs(self):
        value = self._make_one()
        self.assertEqual(abs(value), value)
        self.assertEqual(value, abs(value))

    def test_inv(self):
        value = self._make_one()
        self.assertEqual(~value, value)
        self.assertEqual(value, ~value)

    def test_nonzero(self):
        value = self._make_one()
        self.assertEqual(bool(value), False)
        self.assertEqual(False, bool(value))

    def test_lshift(self):
        value = self._make_one()
        self.assertEqual(2 << value, value)
        self.assertEqual(value << 2, value)
        self.assertEqual(value, 2 << value)
        self.assertEqual(value, value << 2)

    def test_rshift(self):
        value = self._make_one()
        self.assertEqual(2 >> value, value)
        self.assertEqual(value >> 2, value)
        self.assertEqual(value, 2 >> value)
        self.assertEqual(value, value >> 2)

    def test_and(self):
        value = self._make_one()
        self.assertEqual(2 & value, value)
        self.assertEqual(value & 2, value)
        self.assertEqual(value, 2 & value)
        self.assertEqual(value, value & 2)

    def test_or(self):
        value = self._make_one()
        self.assertEqual(2 | value, value)
        self.assertEqual(value | 2, value)
        self.assertEqual(value, 2 | value)
        self.assertEqual(value, value | 2)

    def test_xor(self):
        value = self._make_one()
        self.assertEqual(2 ^ value, value)
        self.assertEqual(value ^ 2, value)
        self.assertEqual(value, 2 ^ value)
        self.assertEqual(value, value ^ 2)

    @unittest.skipIf(PY3, 'Python 2 only.')
    def test_coerce(self):
        from Missing import notMissing
        value = self._make_one()
        self.assertEqual(coerce(value, 1), (value, notMissing))  # NOQA: F821
        self.assertEqual(coerce(1, value), (notMissing, value))  # NOQA: F821
        self.assertEqual(coerce(value, 1.0), (value, notMissing))  # NOQA: F821
        self.assertEqual(coerce(1.0, value), (notMissing, value))  # NOQA: F821
        self.assertEqual(coerce(value, 0x1), (value, notMissing))  # NOQA: F821
        self.assertEqual(coerce(0x1, value), (notMissing, value))  # NOQA: F821

    def test_number_conversion(self):
        value = self._make_one()
        self.assertRaises(TypeError, int, value)
        self.assertRaises(TypeError, long, value)
        self.assertRaises(TypeError, float, value)
        self.assertRaises(TypeError, oct, value)
        self.assertRaises(TypeError, hex, value)

    def test_getattr(self):
        value = self._make_one()
        valid = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for v in valid:
            self.assertEqual(getattr(value, v), value)
        self.assertEqual(getattr(value, 'abc'), value)
        self.assertEqual(getattr(value, 'a_b'), value)
        self.assertRaises(AttributeError, getattr, value, 'a1')
        self.assertRaises(AttributeError, getattr, value, '_a')
        self.assertRaises(AttributeError, getattr, value, 'a_b1')

    def test_setattr(self):
        value = self._make_one()
        self.assertRaises(AttributeError, setattr, value, 'a', 2)
        self.assertRaises(AttributeError, setattr, value, 'a1', 2)

    def test_call(self):
        value = self._make_one()
        self.assertEqual(value, value())
        self.assertEqual(value(), value)

    def test_hash(self):
        value = self._make_one()
        self.assertRaises(TypeError, hash, value)

    def test_repr(self):
        value = self._make_one()
        self.assertEqual(repr(value), 'Missing.Value')

    def test_bytes(self):
        value = self._make_one()
        self.assertEqual(bytes(value), b'')

    def test_str(self):
        value = self._make_one()
        self.assertEqual(str(value), '')

    def test_reduce(self):
        value = self._make_one()
        self.assertEqual(value.__reduce__(), 'V')

    def test_class(self):
        value = self._make_one()
        self.assertTrue('Missing.Missing' in repr(value.__class__))

    def test_type(self):
        value = self._make_one()
        self.assertTrue('Missing.Missing' in repr(type(value)))


class TestValue(ValueTests, unittest.TestCase):

    def _get_target(self):
        from Missing import Value
        return Value

    def _make_one(self):
        return self._get_target()


class TestMV(ValueTests, unittest.TestCase):

    def _get_target(self):
        from Missing import MV
        return MV

    def _make_one(self):
        return self._get_target()


class TestV(ValueTests, unittest.TestCase):

    def _get_target(self):
        from Missing import V
        return V

    def _make_one(self):
        return self._get_target()


class TestMissing(ValueTests, unittest.TestCase):

    def _get_target(self):
        from Missing import Missing
        return Missing

    def _make_one(self):
        return self._get_target()()

    def test_reduce(self):
        klass = self._get_target()
        value = self._make_one()
        self.assertEqual(value.__reduce__(), (klass, ()))
