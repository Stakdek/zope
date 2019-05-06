import sys


PY3 = sys.version_info >= (3, 0)
if PY3:
    import builtins
    class_types = type,
    string_types = (str, bytes)
    unicode = str
else:
    import __builtin__ as builtins  # noqa
    from types import ClassType
    class_types = (type, ClassType)
    string_types = basestring,
    unicode = unicode
