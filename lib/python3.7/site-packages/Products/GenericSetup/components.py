##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Local component registry export / import handler.
"""

import six

from operator import itemgetter

from Acquisition import aq_base
from Acquisition import aq_parent
from zope.component import adapts
from zope.component import getUtilitiesFor
from zope.component import queryMultiAdapter
from zope.interface.interfaces import ComponentLookupError
from zope.interface.interfaces import IComponentRegistry
from zope.component.interfaces import IPossibleSite

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import IComponentsHandlerBlacklist
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import _getDottedName
from Products.GenericSetup.utils import _resolveDottedName
from Products.GenericSetup.utils import XMLAdapterBase

BLACKLIST_SELF = _getDottedName(IComponentsHandlerBlacklist)


class ComponentRegistryXMLAdapter(XMLAdapterBase):

    """XML im- and exporter for a local component registry.
    """

    adapts(IComponentRegistry, ISetupEnviron)

    _LOGGER_ID = 'componentregistry'

    name = 'componentregistry'

    def _constructBlacklist(self):
        blacklist = set((BLACKLIST_SELF,))
        utils = getUtilitiesFor(IComponentsHandlerBlacklist)
        for _, util in utils:
            names = [_getDottedName(i) for i in util.getExcludedInterfaces()]
            blacklist.update(names)
        return blacklist

    def _exportNode(self):
        node = self._doc.createElement('componentregistry')
        fragment = self._doc.createDocumentFragment()

        child = self._doc.createElement('adapters')
        child.appendChild(self._extractAdapters())
        self._logger.info('Adapters exported.')
        fragment.appendChild(child)

        child = self._doc.createElement('subscribers')
        child.appendChild(self._extractSubscriptionAdapters())
        child.appendChild(self._extractHandlers())
        self._logger.info('Subscribers exported.')
        fragment.appendChild(child)

        child = self._doc.createElement('utilities')
        child.appendChild(self._extractUtilities())
        self._logger.info('Utilities exported.')
        fragment.appendChild(child)

        node.appendChild(fragment)

        return node

    def _importNode(self, node):
        if self.environ.shouldPurge():
            self._purgeAdapters()
            self._logger.info('Adapters purged.')
            self._purgeSubscriptionAdapters()
            self._purgeHandlers()
            self._logger.info('Subscribers purged.')
            self._purgeUtilities()
            self._logger.info('Utilities purged.')

        for child in node.childNodes:
            if child.nodeName == 'adapters':
                self._initAdapters(child)
                self._logger.info('Adapters registered.')
            if child.nodeName == 'subscribers':
                # These should have either a factory or a handler.  Not both.
                # Handle factory:
                self._initSubscriptionAdapters(child)
                # Handle handler:
                self._initHandlers(child)
                self._logger.info('Subscribers registered.')
            if child.nodeName == 'utilities':
                self._initUtilities(child)
                self._logger.info('Utilities registered.')

    def _purgeAdapters(self):
        registrations = tuple(self.context.registeredAdapters())
        blacklist = self._constructBlacklist()

        for registration in registrations:
            factory = registration.factory
            required = registration.required
            provided = registration.provided
            name = registration.name
            if _getDottedName(provided) in blacklist:
                continue

            self.context.unregisterAdapter(factory=factory,
                                           required=required,
                                           provided=provided,
                                           name=name)

    def _purgeSubscriptionAdapters(self):
        registrations = tuple(self.context.registeredSubscriptionAdapters())
        blacklist = self._constructBlacklist()

        for registration in registrations:
            factory = registration.factory
            required = registration.required
            provided = registration.provided
            if _getDottedName(provided) in blacklist:
                continue

            self.context.unregisterSubscriptionAdapter(factory=factory,
                                                       required=required,
                                                       provided=provided)

    def _purgeHandlers(self):
        registrations = tuple(self.context.registeredHandlers())

        for registration in registrations:
            factory = registration.factory
            required = registration.required

            self.context.unregisterHandler(factory=factory, required=required)

    def _purgeUtilities(self):
        registrations = tuple(self.context.registeredUtilities())
        blacklist = self._constructBlacklist()

        for registration in registrations:
            provided = registration.provided
            name = registration.name
            if _getDottedName(provided) in blacklist:
                continue
            self.context.unregisterUtility(provided=provided, name=name)

    def _initAdapters(self, node):
        blacklist = self._constructBlacklist()

        for child in node.childNodes:
            if child.nodeName != 'adapter':
                continue

            factory = _resolveDottedName(child.getAttribute('factory'))

            provided = child.getAttribute('provides')
            if provided in blacklist:
                continue

            provided = _resolveDottedName(provided)
            name = six.text_type(child.getAttribute('name'))

            # BBB
            for_ = child.getAttribute('for') or child.getAttribute('for_')
            required = []
            for interface in for_.split():
                required.append(_resolveDottedName(interface))

            if child.hasAttribute('remove'):
                self.context.unregisterAdapter(factory,
                                               required, provided, name)
                continue

            self.context.registerAdapter(factory,
                                         required=required,
                                         provided=provided,
                                         name=name)

    def _initSubscriptionAdapters(self, node):
        blacklist = self._constructBlacklist()

        for child in node.childNodes:
            if child.nodeName != 'subscriber':
                continue

            # We only handle subscribers with a factory attribute.
            # The handler attribute is handled by _initHandlers.
            # Only one of the two attributes is supported in a subscriber.
            factory = child.getAttribute('factory')
            if not factory:
                continue

            handler = child.getAttribute('handler')
            if handler:
                raise ValueError("Can not specify both a factory and a "
                                 "handler in a subscriber registration.")

            factory = _resolveDottedName(factory)

            provided = child.getAttribute('provides')
            if provided in blacklist:
                continue

            provided = _resolveDottedName(provided)

            # BBB
            for_ = child.getAttribute('for') or child.getAttribute('for_')
            required = []
            for interface in for_.split():
                required.append(_resolveDottedName(interface))

            # Uninstall to prevent duplicate registrations. While this is
            # allowed in ZCML, GS profiles can be run multiple times.
            self.context.unregisterSubscriptionAdapter(factory,
                                                       required=required,
                                                       provided=provided)

            if child.hasAttribute('remove'):
                continue

            self.context.registerSubscriptionAdapter(factory,
                                                     required=required,
                                                     provided=provided)

    def _initHandlers(self, node):
        for child in node.childNodes:
            if child.nodeName != 'subscriber':
                continue

            # We only handle subscribers with a handler attribute.
            # The factory attribute is handled by _initSubscriptionAdapters.
            # Only one of the two attributes is supported in a subscriber.
            handler = child.getAttribute('handler')
            if not handler:
                continue

            factory = child.getAttribute('factory')
            if factory:
                raise ValueError("Can not specify both a factory and a "
                                 "handler in a subscriber registration.")

            if child.hasAttribute('provides'):
                raise ValueError("Cannot use handler with provides in a "
                                 "subscriber registration.")

            handler = _resolveDottedName(handler)

            # BBB
            for_ = child.getAttribute('for') or child.getAttribute('for_')
            required = []

            for interface in for_.split():
                required.append(_resolveDottedName(interface))

            # Uninstall to prevent duplicate registrations. While this is
            # allowed in ZCML, GS profiles can be run multiple times.
            self.context.unregisterHandler(handler, required=required)

            if child.hasAttribute('remove'):
                continue

            self.context.registerHandler(handler, required=required)

    def _getSite(self):
        # Get the site by either __parent__ or Acquisition
        site = getattr(self.context, '__parent__', None)
        if site is None:
            site = aq_parent(self.context)
        return site

    def _initUtilities(self, node):
        site = self._getSite()
        blacklist = self._constructBlacklist()

        current_utilities = self.context.registeredUtilities()

        for child in node.childNodes:
            if child.nodeName != 'utility':
                continue

            provided = child.getAttribute('interface')
            if provided in blacklist:
                continue

            provided = _resolveDottedName(provided)
            name = six.text_type(child.getAttribute('name'))

            component = child.getAttribute('component')
            component = component and _resolveDottedName(component) or None

            factory = child.getAttribute('factory')
            factory = factory and _resolveDottedName(factory) or None

            if child.hasAttribute('remove'):
                if self.context.queryUtility(provided, name) is not None:
                    ofs_id = self._ofs_id(child)
                    if ofs_id in self.context.objectIds():
                        self.context._delObject(ofs_id, suppress_events=True)
                    self.context.unregisterUtility(provided=provided,
                                                   name=name)
                continue

            if component and factory:
                raise ValueError("Can not specify both a factory and a "
                                 "component in a utility registration.")

            obj_path = child.getAttribute('object')
            if not component and not factory and obj_path is not None:
                # Support for registering the site itself
                if obj_path in ('', '/'):
                    obj = site
                else:
                    # BBB: filter out path segments, we did claim to support
                    # nested paths once
                    id_ = [p for p in obj_path.split('/') if p][0]
                    obj = getattr(site, id_, None)

                if obj is not None:
                    self.context.registerUtility(aq_base(obj), provided, name)
                else:
                    # Log an error, object not found
                    self._logger.warning("The object %s was not found, while "
                                         "trying to register an utility. The "
                                         "provided object definition was %s. "
                                         "The site used was: %s"
                                         % (repr(obj), obj_path, repr(site)))
            elif component:
                self.context.registerUtility(component, provided, name)
            elif factory:
                current = [utility for utility in current_utilities
                           if utility.provided == provided and
                           utility.name == name]

                if current and getattr(current[0], "factory", None) == factory:
                    continue

                obj = factory()
                ofs_id = self._ofs_id(child)
                if ofs_id not in self.context.objectIds():
                    self.context._setObject(ofs_id, aq_base(obj),
                                            set_owner=False,
                                            suppress_events=True)
                obj = self.context.get(ofs_id)
                obj.__name__ = ofs_id
                obj.__parent__ = aq_base(self.context)
                self.context.registerUtility(aq_base(obj), provided, name)
            else:
                self._logger.warning("Invalid utility registration for "
                                     "interface %s" % provided)

    def _ofs_id(self, child):
        # We build a valid OFS id by using the interface's full
        # dotted path or using the specified id
        name = str(child.getAttribute('name'))
        ofs_id = str(child.getAttribute('id'))
        if not ofs_id:
            ofs_id = str(child.getAttribute('interface'))
            # In case of named utilities we append the name
            if name:
                ofs_id += '-' + str(name)
        return ofs_id

    def _extractAdapters(self):
        fragment = self._doc.createDocumentFragment()

        registrations = [{'factory': _getDottedName(reg.factory),
                          'provided': _getDottedName(reg.provided),
                          'required': reg.required,
                          'name': reg.name}
                         for reg in self.context.registeredAdapters()]
        registrations.sort(key=itemgetter('name'))
        registrations.sort(key=itemgetter('provided'))
        blacklist = self._constructBlacklist()

        for reg_info in registrations:
            if reg_info['provided'] in blacklist:
                continue

            child = self._doc.createElement('adapter')

            for_ = u''
            for interface in reg_info['required']:
                for_ = for_ + _getDottedName(interface) + u'\n           '

            child.setAttribute('factory', reg_info['factory'])
            child.setAttribute('provides', reg_info['provided'])
            child.setAttribute('for', for_.strip())
            if reg_info['name']:
                child.setAttribute('name', reg_info['name'])

            fragment.appendChild(child)

        return fragment

    def _extractSubscriptionAdapters(self):
        fragment = self._doc.createDocumentFragment()

        registrations = [{'factory': _getDottedName(reg.factory),
                          'provided': _getDottedName(reg.provided),
                          'required': reg.required} for reg
                         in self.context.registeredSubscriptionAdapters()]
        registrations.sort(key=itemgetter('factory'))
        registrations.sort(key=itemgetter('provided'))
        blacklist = self._constructBlacklist()

        for reg_info in registrations:
            if reg_info['provided'] in blacklist:
                continue

            child = self._doc.createElement('subscriber')

            for_ = u''
            for interface in reg_info['required']:
                for_ = for_ + _getDottedName(interface) + u'\n           '

            child.setAttribute('factory', reg_info['factory'])
            child.setAttribute('provides', reg_info['provided'])
            child.setAttribute('for', for_.strip())

            fragment.appendChild(child)

        return fragment

    def _extractHandlers(self):
        fragment = self._doc.createDocumentFragment()

        registrations = [{'factory': _getDottedName(reg.factory),
                          'required': reg.required}
                         for reg in self.context.registeredHandlers()]
        registrations.sort(key=itemgetter('factory'))
        registrations.sort(key=itemgetter('required'))

        for reg_info in registrations:
            child = self._doc.createElement('subscriber')

            for_ = u''
            for interface in reg_info['required']:
                for_ = for_ + _getDottedName(interface) + u'\n           '

            child.setAttribute('handler', reg_info['factory'])
            child.setAttribute('for', for_.strip())

            fragment.appendChild(child)

        return fragment

    def _extractUtilities(self):
        fragment = self._doc.createDocumentFragment()

        registrations = [{'component': reg.component,
                          'factory': getattr(reg, 'factory', None),
                          'provided': _getDottedName(reg.provided),
                          'name': reg.name}
                         for reg in self.context.registeredUtilities()]
        registrations.sort(key=itemgetter('name'))
        registrations.sort(key=itemgetter('provided'))
        site = aq_base(self._getSite())
        blacklist = self._constructBlacklist()

        for reg_info in registrations:
            if reg_info['provided'] in blacklist:
                continue

            child = self._doc.createElement('utility')
            child.setAttribute('interface', reg_info['provided'])

            if reg_info['name']:
                child.setAttribute('name', reg_info['name'])

            if reg_info['factory'] is not None:
                factory = _getDottedName(reg_info['factory'])
                child.setAttribute('factory', factory)
            else:
                factory = None
                comp = reg_info['component']
                # check if the component is acquisition wrapped. If it is,
                # export an object reference instead of a factory reference
                if getattr(comp, 'aq_base', None) is not None:
                    if aq_base(comp) is site:
                        child.setAttribute('object', '')
                    elif hasattr(aq_base(comp), 'getId'):
                        child.setAttribute('object', comp.getId())
                    else:
                        # This is a five.localsitemanager wrapped utility
                        factory = _getDottedName(type(aq_base(comp)))
                        child.setAttribute('factory', factory)
                else:
                    factory = _getDottedName(type(comp))
                    child.setAttribute('factory', factory)
                if factory is not None:
                    ofs_id = self._ofs_id(child)
                    name = getattr(comp, '__name__', None)
                    if ofs_id != name:
                        if name is not None:
                            child.setAttribute('id', name)
                        else:
                            child.setAttribute('id', ofs_id)

            fragment.appendChild(child)

        return fragment


def importComponentRegistry(context):
    """Import local components.
    """
    site = context.getSite()
    sm = None
    if IPossibleSite.providedBy(site):
        # All object managers are an IPossibleSite, but this
        # defines the getSiteManager method to be available
        try:
            sm = site.getSiteManager()
        except ComponentLookupError:
            sm = None

    if sm is None or not IComponentRegistry.providedBy(sm):
        logger = context.getLogger('componentregistry')
        logger.info("Can not register components, as no registry was found.")
        return

    importer = queryMultiAdapter((sm, context), IBody)
    if importer:
        body = context.readDataFile('componentregistry.xml')
        if body is not None:
            importer.body = body
        else:
            logger = context.getLogger('componentregistry')
            logger.debug("Nothing to import")


def exportComponentRegistry(context):
    """Export local components.
    """
    site = context.getSite()
    sm = None
    if IPossibleSite.providedBy(site):
        # All object managers are an IPossibleSite, but this
        # defines the getSiteManager method to be available
        try:
            sm = site.getSiteManager()
        except ComponentLookupError:
            sm = None

    if sm is None or not IComponentRegistry.providedBy(sm):
        logger = context.getLogger('componentregistry')
        logger.debug("Nothing to export.")
        return

    exporter = queryMultiAdapter((sm, context), IBody)
    if exporter:
        body = exporter.body
        if body is not None:
            context.writeDataFile('componentregistry.xml', body,
                                  exporter.mime_type)
