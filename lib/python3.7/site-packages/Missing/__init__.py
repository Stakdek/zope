import sys

from ExtensionClass import Base

if sys.version_info >= (3, 5):
    PY3 = True
    PY35 = True
elif sys.version_info >= (3, ):
    PY3 = True
    PY35 = False
else:
    PY3 = False
    PY35 = False


class Missing(Base):

    _valid = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    __hash__ = None

    def __call__(self):
        return self

    def __repr__(self):
        return 'Missing.Value'

    def __bytes__(self):
        return b''

    def __str__(self):
        return ''

    def __reduce__(self):
        if self is V:
            return 'V'
        return (type(self), ())

    def __bool__(self):
        return False

    if not PY3:
        __nonzero__ = __bool__

        def __coerce__(self, other):
            return (self, notMissing)

        def __cmp__(self, other):
            if self is notMissing:
                return -1
            return other is notMissing

    def __eq__(self, other):
        if self is notMissing:
            return True if other is notMissing else False
        return other is self

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return False

    def __le__(self, other):
        if self is other:
            return True
        return False

    def __gt__(self, other):
        if self is other:
            return False
        return True

    def __ge__(self, other):
        return True

    def _calc(self, other):
        if self is notMissing:
            return other
        return self

    __add__ = __radd__ = __sub__ = __rsub__ = _calc
    __mul__ = __rmul__ = __div__ = __rdiv__ = _calc
    __floordiv__ = __rfloordiv__ = __truediv__ = __rtruediv__ = _calc
    __pow__ = __rpow__ = _calc
    __mod__ = __rmod__ = __divmod__ = __rdivmod__ = _calc
    __lshift__ = __rshift__ = __rlshift__ = __rrshift__ = _calc
    __and__ = __rand__ = __or__ = __ror__ = __xor__ = __rxor__ = _calc

    if PY35:
        __matmul__ = __rmatmul__ = _calc

    def _change(self):
        return self

    __neg__ = __pos__ = __abs__ = __invert__ = _change

    def __setattr__(self, key, value):
        raise AttributeError(key)

    def __getattr__(self, key):
        if not key:
            raise AttributeError(key)
        _valid = self._valid
        if key[0] in _valid:
            if len(key) == 1:
                return self
        else:
            raise AttributeError(key)
        _valid2 = _valid + '_'
        for k in key:
            if k not in _valid2:
                raise AttributeError(key)
        return self


V = MV = Value = Missing()
notMissing = Missing()
