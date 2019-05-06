# -*- coding: utf-8 -*-
from zope.globalrequest.interfaces import IGlobalRequest
from zope.globalrequest.local import getLocal
from zope.globalrequest.local import setLocal
from zope.globalrequest.local import marker
from zope.interface.declarations import moduleProvides

moduleProvides(IGlobalRequest)


def getRequest():
    """ return the currently active request object """
    return getLocal('request')


def setRequest(request):
    """ set the request object to be returned by `getRequest` """
    setLocal('request', request)


def clearRequest():
    """ clear the stored request object """
    setRequest(marker)
