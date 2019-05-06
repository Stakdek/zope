##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Component registry for local site manager.
"""

import six

import Acquisition
import persistent
import zope.event
import zope.interface.interfaces
from Acquisition.interfaces import IAcquirer
from OFS.ObjectManager import ObjectManager
from zope.component.hooks import getSite
from zope.component.interfaces import ISite
from zope.component.persistentregistry import PersistentComponents
from zope.interface.adapter import _lookup
from zope.interface.adapter import _lookupAll
from zope.interface.adapter import _subscriptions
from zope.interface.adapter import VerifyingAdapterLookup
from zope.interface.registry import UtilityRegistration
from zope.interface.registry import _getUtilityProvided
from ZPublisher.BaseRequest import RequestContainer

from five.localsitemanager.utils import get_parent

_marker = object()


class FiveVerifyingAdapterLookup(VerifyingAdapterLookup):

    # override some AdapterLookupBase methods for acquisition wrapping

    def _uncached_lookup(self, required, provided, name=u''):
        result = None
        order = len(required)
        for registry in self._registry.ro:
            byorder = registry._adapters
            if order >= len(byorder):
                continue

            extendors = registry._v_lookup._extendors.get(provided)
            if not extendors:
                continue

            components = byorder[order]
            result = _lookup(components, required, extendors, name, 0,
                             order)
            if result is not None:
                result = _wrap(result, registry)
                break

        self._subscribe(*required)

        return result

    def _uncached_lookupAll(self, required, provided):
        order = len(required)
        result = {}
        for registry in reversed(self._registry.ro):
            byorder = registry._adapters
            if order >= len(byorder):
                continue
            extendors = registry._v_lookup._extendors.get(provided)
            if not extendors:
                continue
            components = byorder[order]
            tmp_result = {}
            _lookupAll(components, required, extendors, tmp_result, 0, order)
            for k, v in six.iteritems(tmp_result):
                tmp_result[k] = _wrap(v, registry)
            result.update(tmp_result)

        self._subscribe(*required)

        return tuple(six.iteritems(result))

    def _uncached_subscriptions(self, required, provided):
        order = len(required)
        result = []
        for registry in reversed(self._registry.ro):
            byorder = registry._subscribers
            if order >= len(byorder):
                continue

            if provided is None:
                extendors = (provided,)
            else:
                extendors = registry._v_lookup._extendors.get(provided)
                if extendors is None:
                    continue

            _subscriptions(byorder[order], required, extendors, u'',
                           result, 0, order)
            result = [_wrap(r, registry) for r in result]

        self._subscribe(*required)

        return result


def _recurse_to_site(current, wanted):
    if not Acquisition.aq_base(current) == wanted:
        current = _recurse_to_site(get_parent(current), wanted)
    return current


def _wrap(comp, registry):
    """Return an aq wrapped component with the site as the parent but
    only if the comp has an aq wrapper to begin with.
    """

    # If component is stored as a ComponentPathWrapper, we traverse to
    # the component using the stored path:
    if isinstance(comp, ComponentPathWrapper):
        comp = getSite().unrestrictedTraverse(comp.path)
        if IAcquirer.providedBy(comp):
            return _rewrap(comp)
        else:
            return comp

    # BBB: The primary reason for doing this sort of wrapping of
    # returned utilities is to support CMF tool-like functionality where
    # a tool expects its aq_parent to be the portal object. New code
    # (ie new utilities) should not rely on this predictability to
    # get the portal object and should search out an alternate means
    # (possibly retrieve the ISiteRoot utility). Although in most
    # cases getting at the portal object shouldn't be the required pattern
    # but instead looking up required functionality via other (possibly
    # local) components.

    if registry.__bases__ and IAcquirer.providedBy(comp):
        current_site = getSite()
        registry_site = Acquisition.aq_base(registry.__parent__)
        if not ISite.providedBy(registry_site):
            registry_site = registry_site.__parent__

        if current_site is None:
            # If no current site can be found, return utilities wrapped in
            # the site they where registered in. We loose the whole aq chain
            # here though
            current_site = Acquisition.aq_base(registry_site)

        parent = None

        if current_site == registry_site:
            parent = current_site
        else:
            parent = _recurse_to_site(current_site, registry_site)

        if parent is None:
            raise ValueError('Not enough context to acquire parent')

        base = Acquisition.aq_base(comp)
        # clean up aq_chain, removing REQUEST objects
        parent = _rewrap(parent)

        if base is not Acquisition.aq_base(parent):
            # If the component is not the component registry container,
            # wrap it in the parent
            comp = base.__of__(parent)
        else:
            # If the component happens to be the component registry
            # container we are looking up a ISiteRoot.
            # We are not wrapping it in itself but in its own parent
            site_parent = Acquisition.aq_parent(parent)
            if site_parent is not None:
                comp = base.__of__(site_parent)
            else:
                comp = base

    return comp


def _rewrap(obj):
    """This functions relies on the passed in obj to provide the IAcquirer
    interface.
    """
    obj = Acquisition.aq_inner(obj)
    base = Acquisition.aq_base(obj)
    parent = Acquisition.aq_parent(obj)
    if parent is None or isinstance(parent, RequestContainer):
        return base
    return base.__of__(_rewrap(parent))


class ComponentPathWrapper(persistent.Persistent):

    def __init__(self, component, path):
        self.component = component
        self.path = path

    def __eq__(self, other):
        return self.component == other

    def __ne__(self, other):
        return self.component != other


class PersistentComponents(PersistentComponents, ObjectManager):

    """An implementation of a component registry that can be persisted
    and looks like a standard ObjectManager.  It also ensures that all
    utilities have the the parent of this site manager (which should be
    the ISite) as their acquired parent.
    """

    def _init_registries(self):
        super(PersistentComponents, self)._init_registries()
        utilities = Acquisition.aq_base(self.utilities)
        utilities.LookupClass = FiveVerifyingAdapterLookup
        utilities._createLookup()
        utilities.__parent__ = self

    def __repr__(self):
        url = 'five'
        site = Acquisition.aq_base(self.__parent__)
        try:
            site = _wrap(site, self)
        except (ValueError, TypeError):
            pass
        path = getattr(site, 'getPhysicalPath', None)
        if path is not None and callable(path):
            url = '/'.join(path())
        return "<%s %s>" % (self.__class__.__name__, url)

    def registeredUtilities(self):
        for reg in super(PersistentComponents, self).registeredUtilities():
            reg.component = _wrap(reg.component, self)
            yield reg

    def registerUtility(self, component=None, provided=None, name=u'',
                        info=u'', event=True, factory=None):
        if factory:
            if component:
                raise TypeError("Can't specify factory and component.")
            component = factory()

        if provided is None:
            provided = _getUtilityProvided(component)

        reg = self._utility_registrations.get((provided, name))
        if reg is not None:
            if reg[:2] == (component, info):
                # already registered
                if isinstance(reg[0], ComponentPathWrapper):
                    # update path
                    self.utilities.unsubscribe((), provided, reg[0])
                    reg[0].path = component.getPhysicalPath()
                    self.utilities.subscribe((), provided, reg[0])
                return
            self.unregisterUtility(reg[0], provided, name)

        subscribed = False
        for ((p, _), data) in six.iteritems(self._utility_registrations):
            if p == provided and data[0] == component:
                subscribed = True
                break

        wrapped_component = component
        if getattr(component, 'aq_parent', None) is not None:
            # component is acquisition wrapped, so try to store path
            if getattr(component, 'getPhysicalPath', None) is None:
                raise AttributeError(
                    'Component %r does not implement getPhysicalPath, '
                    'so register it unwrapped or implement this method.' %
                    component)
            path = component.getPhysicalPath()
            # If the path is relative we can't store it because we
            # have nearly no chance to use the path for traversal in
            # getUtility.
            if path[0] == '':
                # We have an absolute path, so we can store it.
                wrapped_component = ComponentPathWrapper(
                    Acquisition.aq_base(component), path)

        self._utility_registrations[(provided, name)] = (
            wrapped_component, info, factory)
        self.utilities.register((), provided, name, wrapped_component)

        if not subscribed:
            self.utilities.subscribe((), provided, wrapped_component)

        if event:
            zope.event.notify(zope.interface.interfaces.Registered(
                UtilityRegistration(
                    self, provided, name, component, info, factory)
            ))

    def unregisterUtility(self, component=None, provided=None, name=u'',
                          factory=None):
        if factory:
            if component:
                raise TypeError("Can't specify factory and component.")
            component = factory()

        if provided is None:
            if component is None:
                raise TypeError("Must specify one of component, factory and "
                                "provided")
            provided = _getUtilityProvided(component)

        # If the existing registration is a ComponentPathWrapper, we
        # convert the component that is to be unregistered to a wrapper.
        # This ensures that our custom comparision methods are called.
        if component is not None:
            old = self._utility_registrations.get((provided, name))
            if old is not None:
                if isinstance(old[0], ComponentPathWrapper):
                    unwrapped_component = Acquisition.aq_base(component)
                    component = ComponentPathWrapper(unwrapped_component, '')
        # Unwrap the utility before continuing to super to allow zope.interface
        # to cache the component root
        component_root = Acquisition.aq_base(self)
        return super(PersistentComponents, component_root).unregisterUtility(
            component=component, provided=provided, name=name)
