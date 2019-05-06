from types import MethodType

from ExtensionClass import Base
from ExtensionClass import C_EXTENSION


class Method(Base):
    """Base class for objects that want to be treated as methods

    The method class provides a method, __of__, that
    binds an object to an instance.  If a method is a subobject
    of an extension-class instance, the the method will be bound
    to the instance and when the resulting object is called, it
    will call the method and pass the instance in addition to
    other arguments.  It is the responsibility of Method objects
    to implement (or inherit) a __call__ method.
    """

    def __of__(self, inst):
        return MethodType(self, inst)


if C_EXTENSION:  # pragma no cover
    from ._MethodObject import *  # NOQA
