##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import unittest
import doctest

from .._compat import _u


class SamplePublication(object):

    def __init__(self, global_config, **options):
        self.args = global_config, options

    def beforeTraversal(self, request):
        pass

    def getApplication(self, request):
        return self

    def callTraversalHooks(self, request, ob):
        pass

    def traverseName(self, request, ob, name):
        return self

    def afterTraversal(self, request, ob):
        pass

    def callObject(self, request, ob):
        return (_u('<html><body>Thanks for your request:<br />\n'
                   '<h1>%s</h1>\n<pre>\n%s\n</pre>\n'
                   '<h1>Publication arguments:</h1>\n'
                   'Globals: %r<br />\nOptions: %r\n</body></html>')
                % (request.__class__.__name__, request,
                   self.args[0], self.args[1])
                )

    def afterCall(self, request, ob):
        pass

    def handleException(self, object, request, exc_info, retry_allowed=1):
        return 'Ouch!'

    def endRequest(self, request, ob):
        pass

    def getDefaultTraversal(self, request, ob):
        return self, ()

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            '../paste.txt',
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
