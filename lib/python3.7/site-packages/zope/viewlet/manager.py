##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Content Provider Manager implementation
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.security
import zope.event
from zope.browserpage import ViewPageTemplateFile

from zope.viewlet import interfaces
from zope.location.interfaces import ILocation
from zope.contentprovider.interfaces import BeforeUpdateEvent

@zope.interface.implementer(interfaces.IViewletManager)
class ViewletManagerBase(object):
    """The Viewlet Manager Base

    A generic manager class which can be instantiated.
    """

    #: A callable that will be used by `render`, if present,
    #: to produce the output. It will be passed the list of viewlets
    #: in the *viewlets* keyword argument.
    template = None

    #: A list of active viewlets for the current manager.
    #: Populated by `update`.
    viewlets = None

    def __init__(self, context, request, view):
        self.__updated = False
        self.__parent__ = view
        self.context = context
        self.request = request

    def __getitem__(self, name):
        """
        Return a viewlet for this object having the given
        name.

        This takes into account security.
        """
        # Find the viewlet
        viewlet = zope.component.queryMultiAdapter(
            (self.context, self.request, self.__parent__, self),
            interfaces.IViewlet, name=name)

        # If the viewlet was not found, then raise a lookup error
        if viewlet is None:
            raise zope.interface.interfaces.ComponentLookupError(
                'No provider with name `%s` found.' % name)

        # If the viewlet cannot be accessed, then raise an
        # unauthorized error
        if not zope.security.canAccess(viewlet, 'render'):
            raise zope.security.interfaces.Unauthorized(
                'You are not authorized to access the provider '
                'called `%s`.' % name)

        # Return the viewlet.
        return viewlet

    def get(self, name, default=None):
        """
        Return a viewlet registered for this object having
        the given name.

        This takes into account security.

        If no such viewlet can be found, returns *default*.
        """
        try:
            return self[name]
        except (zope.interface.interfaces.ComponentLookupError,
                zope.security.interfaces.Unauthorized):
            return default

    def __contains__(self, name):
        """See zope.interface.common.mapping.IReadMapping"""
        return bool(self.get(name, False))

    def filter(self, viewlets):
        """
        Filter *viewlets* down from all available viewlets to just the
        currently desired set.

        :param list viewlets: a list of tuples of the form ``(name,
            viewlet)``.

        :return: A list of the available viewlets in the form ``(name,
            viewlet)``.  By default, this method checks with
            `zope.security.checker.canAccess` to see if the
            ``render`` method of a viewlet can be used to
            determine availability.
        """
        # Only return viewlets accessible to the principal
        return [(name, viewlet) for name, viewlet in viewlets
                if zope.security.canAccess(viewlet, 'render')]

    def sort(self, viewlets):
        """Sort the viewlets.

        ``viewlets`` is a list of tuples of the form (name, viewlet).
        """
        # By default, we are not sorting by viewlet name.
        return sorted(viewlets, key=lambda x: x[0])

    def update(self):
        """
        Update the viewlet manager for rendering.

        This method is part of the protocol of a content provider, called before
        :meth:`render`. This implementation will use it to:

        1. Find the total set of available viewlets by querying for viewlet adapters.
        2. Filter the total set down to the active set by using :meth:`filter`.
        3. Sort the active set using :meth:`sort`.
        4. Provide viewlets that implement :class:`~zope.location.interfaces.ILocation`
           with a name.
        5. Set :attr:`viewlets` to the found set of active viewlets.
        6. Fire :class:`.BeforeUpdateEvent` for each active viewlet before calling ``update()``
           on it.

        ..  seealso:: :class:`zope.contentprovider.interfaces.IContentProvider`
        """
        self.__updated = True

        # Find all content providers for the region
        viewlets = zope.component.getAdapters(
            (self.context, self.request, self.__parent__, self),
            interfaces.IViewlet)

        viewlets = self.filter(viewlets)
        viewlets = self.sort(viewlets)
        # Just use the viewlets from now on
        self.viewlets = []
        for name, viewlet in viewlets:
            if ILocation.providedBy(viewlet):
                viewlet.__name__ = name
            self.viewlets.append(viewlet)
        self._updateViewlets()

    def _updateViewlets(self):
        """Calls update on all viewlets and fires events"""
        for viewlet in self.viewlets:
            zope.event.notify(BeforeUpdateEvent(viewlet, self.request))
            viewlet.update()

    def render(self):
        """
        Render the active viewlets.

        If a :attr:`template` has been provided, call the template to
        render. Otherwise, call each viewlet in order to render.

        .. note:: If a :attr:`template` is provided, it will be called
           even if there are no :attr:`viewlets`.

        ..  seealso:: :class:`zope.contentprovider.interfaces.IContentProvider`
        """
        # Now render the view
        if self.template:
            return self.template(viewlets=self.viewlets)
        return u'\n'.join([viewlet.render() for viewlet in self.viewlets])


def ViewletManager(name, interface, template=None, bases=()):
    """
    Create and return a new viewlet manager class that implements
    :class:`zope.viewlet.interfaces.IViewletManager`.

    :param str name: The name of the generated class.
    :param interface: The additional interface the class will implement.
    :keyword tuple bases: The base classes to extend.
    """

    attrDict = {'__name__' : name}
    if template is not None:
        attrDict['template'] = ViewPageTemplateFile(template)

    if ViewletManagerBase not in bases:
        # Make sure that we do not get a default viewlet manager mixin, if the
        # provided base is already a full viewlet manager implementation.
        if not (len(bases) == 1 and
                interfaces.IViewletManager.implementedBy(bases[0])):
            bases = bases + (ViewletManagerBase,)

    ViewletManagerCls = type(
        '<ViewletManager providing %s>' % interface.getName(), bases, attrDict)
    zope.interface.classImplements(ViewletManagerCls, interface)
    return ViewletManagerCls


def getWeight(item):
    _name, viewlet = item
    try:
        return int(viewlet.weight)
    except AttributeError:
        return 0


class WeightOrderedViewletManager(ViewletManagerBase):
    """Weight ordered viewlet managers."""

    def sort(self, viewlets):
        """
        Sort the viewlets based on their ``weight`` attribute (if present;
        viewlets without a ``weight`` are sorted at the beginning but are
        otherwise unordered).
        """
        return sorted(viewlets, key=getWeight)

    def render(self):
        """
        Just like :meth:`ViewletManagerBase`, except that if there are no
        active viewlets in :attr:`viewlets`, we will not attempt to render
        the template.
        """
        # do not render a manager template if no viewlets are avaiable
        if not self.viewlets:
            return u''
        return ViewletManagerBase.render(self)


def isAvailable(viewlet):
    try:
        return zope.security.canAccess(viewlet, 'render') and viewlet.available
    except AttributeError:
        return True


class ConditionalViewletManager(WeightOrderedViewletManager):
    """Conditional weight ordered viewlet managers."""

    def filter(self, viewlets):
        """
        Sort out all viewlets which are explicity not available
        based on the value of their ``available`` attribute (viewlets without
        this attribute are considered available).

        """
        return [(name, viewlet) for name, viewlet in viewlets
                if isAvailable(viewlet)]
