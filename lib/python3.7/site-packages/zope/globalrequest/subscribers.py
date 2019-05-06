from zope.globalrequest import clearRequest
from zope.globalrequest import setRequest


def set(context, event):
    """ set the request object as provided by the event """
    setRequest(event.request)


def clear(event):
    """ clear the stored request object """
    clearRequest()
