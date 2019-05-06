from zope.location.interfaces import IRoot

from Acquisition import aq_parent, aq_inner

_marker = object()


def get_parent(obj, default=_marker):
    """Returns the container the object was traversed via.

    Returns None if the object is a containment root.
    Raises TypeError if the object doesn't have enough context to get the
    parent.
    """
    if IRoot.providedBy(obj):
        return None

    parent = aq_parent(aq_inner(obj))
    if parent is not None:
        return parent

    if default != _marker:
        return default

    raise TypeError("Not enough context information to get parent", obj)
