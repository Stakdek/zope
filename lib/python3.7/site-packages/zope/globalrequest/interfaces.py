from zope.interface import Interface


class IGlobalRequest(Interface):
    """ interface to handle retrieval and setting of the currently
        used request object in a thread-local manner """

    def getRequest():
        """ return the currently active request object """

    def setRequest(request):
        """ set the request object to be returned by `getRequest` """

    def clearRequest():
        """ clear the stored request object """
