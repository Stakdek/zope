##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Resource interfaces
"""
from zope.interface import Interface, Attribute


class IResource(Interface):
    """
    A resource.

    Resources are static files and directories that are served to the
    browser directly from the filesystem. The most common example are
    images, CSS style sheets, or JavaScript files.

    Resources are be registered under a symbolic name and can later be
    referred to by that name, so their usage is independent from their
    physical location.

    .. seealso:: `zope.browserresource.resource.Resource`
    .. seealso:: `zope.browserresource.resource.AbsoluteURL`
    """

    request = Attribute('Request object that is requesting the resource')

    def __call__():
        """
        Return the absolute URL of this resource.
        """

class IFileResource(IResource):
    """
    A resource representing a single file.

    .. seealso:: `zope.browserresource.file.FileResource`
    """


class IResourceFactory(Interface):
    """
    A callable object to produce `IResource` objects.
    """

    def __call__(request):
        """Return an `IResource` object"""

class IResourceFactoryFactory(Interface):
    """
    A factory for `IResourceFactory` objects

    These factories are registered as named utilities that can be
    selected for creating resource factories in a pluggable way.

    `Resource directories <.DirectoryResource>` and the
    ``<browser:resource>`` `directive <.IResourceDirective>` use these
    utilities to choose what resource to create, depending on the file
    extension, so third-party packages could easily plug-in additional
    resource types.
    """

    def __call__(path, checker, name):
        """Return an IResourceFactory"""

class IETag(Interface):
    """
    An adapter for computing resource ETags.

    These should be registered as multi-adapters on the resource
    and the request.

    .. seealso:: `zope.browserresource.file.FileETag`
    """

    def __call__(mtime, content):
        """
        Compute an ETag for a resource.

        :param float mtime: The filesystem modification time
           of the resource (`os.path.getmtime`)
        :param bytes content: The contents of the resource.
        :return: A string representing the ETag, or `None` to
            disable the ETag header.
        """
