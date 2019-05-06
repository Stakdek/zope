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

import pkg_resources
import zope.publisher.browser
import zope.publisher.http
import zope.publisher.publish

browser_methods = set(('GET', 'HEAD', 'POST'))

class Application:

    def __init__(self, global_config, publication, **options):
        if not publication.startswith('egg:'):
            raise ValueError(
                'Invalid publication: .\n'
                'The publication specification must start with "egg:".\n'
                'The publication must name a publication entry point.'
                % publication)

        pub_class = get_egg(publication[4:],
                            'zope.publisher.publication_factory')
        self.publication = pub_class(global_config, **options)

    def __call__(self, environ, start_response):
        request = self.request(environ)
        request.setPublication(self.publication)

        # Let's support post-mortem debugging
        handle_errors = environ.get('wsgi.handleErrors', True)

        request = zope.publisher.publish.publish(
            request, handle_errors=handle_errors)
        response = request.response

        # Start the WSGI server response
        start_response(response.getStatusString(), response.getHeaders())

        # Return the result body iterable.
        return response.consumeBodyIter()

    def request(self, environ):
        method = environ.get('REQUEST_METHOD', 'GET').upper()
        if method in browser_methods:
            rc = zope.publisher.browser.BrowserRequest
        else:
            rc = zope.publisher.http.HTTPRequest
        return rc(environ['wsgi.input'], environ)

def get_egg(name, group):
    if '#' in name:
        egg, entry_point = name.split('#', 1)
    else:
        egg, entry_point = name, 'default'

    return pkg_resources.load_entry_point(egg, group, entry_point)
