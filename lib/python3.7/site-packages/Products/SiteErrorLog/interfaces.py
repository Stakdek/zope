# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.interface import Interface


class IErrorRaisedEvent(Interface):
    """
    An event that contains an error
    """


@implementer(IErrorRaisedEvent)
class ErrorRaisedEvent(dict):
    pass
