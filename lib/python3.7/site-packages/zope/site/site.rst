Sites and Local Site Managers
=============================

This is an introduction of location-based component architecture.

Creating and Accessing Sites
----------------------------

*Sites* are used to provide custom component setups for parts of your
application or web site. Every folder:

  >>> from zope.site import folder
  >>> myfolder = folder.rootFolder()

has the potential to become a site:

  >>> from zope.component.interfaces import ISite, IPossibleSite
  >>> IPossibleSite.providedBy(myfolder)
  True

but is not yet one:

  >>> ISite.providedBy(myfolder)
  False

If you would like your custom content component to be able to become a site,
you can use the `SiteManagerContainer` mix-in class:

  >>> from zope import site
  >>> class MyContentComponent(site.SiteManagerContainer):
  ...     pass

  >>> myContent = MyContentComponent()
  >>> IPossibleSite.providedBy(myContent)
  True
  >>> ISite.providedBy(myContent)
  False

To convert a possible site to a real site, we have to provide a site manager:

  >>> sm = site.LocalSiteManager(myfolder)
  >>> myfolder.setSiteManager(sm)
  >>> ISite.providedBy(myfolder)
  True
  >>> myfolder.getSiteManager() is sm
  True

Note that an event is generated when a local site manager is created:

  >>> from zope.component.eventtesting import getEvents
  >>> from zope.site.interfaces import INewLocalSite
  >>> [event] = getEvents(INewLocalSite)
  >>> event.manager is sm
  True

If one tries to set a bogus site manager, a `ValueError` will be raised:

   >>> myfolder2 = folder.Folder()
   >>> myfolder2.setSiteManager(object)
   Traceback (most recent call last):
   ...
   ValueError: setSiteManager requires an IComponentLookup

If the possible site has been changed to a site already, a `TypeError`
is raised when one attempts to add a new site manager:

  >>> myfolder.setSiteManager(site.LocalSiteManager(myfolder))
  Traceback (most recent call last):
  ...
  TypeError: Already a site

There is also an adapter you can use to get the next site manager from any
location:

  >>> myfolder['mysubfolder'] = folder.Folder()
  >>> import zope.interface.interfaces
  >>> zope.interface.interfaces.IComponentLookup(myfolder['mysubfolder']) is sm
  True

If the location passed is a site, the site manager of that site is returned:

  >>> zope.interface.interfaces.IComponentLookup(myfolder) is sm
  True


Using the Site Manager
----------------------

A site manager contains several *site management folders*, which are used to
logically organize the software. When a site manager is initialized, a default
site management folder is created:

  >>> sm = myfolder.getSiteManager()
  >>> default = sm['default']
  >>> default.__class__
  <class 'zope.site.site.SiteManagementFolder'>

However, you can tell not to create the default site manager folder on
LocalSiteManager creation:

  >>> nodefault = site.LocalSiteManager(myfolder, default_folder=False)
  >>> 'default' in nodefault
  False

Also, note that when creating LocalSiteManager, its __parent__ is set to
site that was passed to constructor and the __name__ is set to ++etc++site.

  >>> nodefault.__parent__ is myfolder
  True
  >>> nodefault.__name__ == '++etc++site'
  True

You can easily create a new site management folder:

  >>> sm['mySMF'] = site.SiteManagementFolder()
  >>> sm['mySMF'].__class__
  <class 'zope.site.site.SiteManagementFolder'>

Once you have your site management folder -- let's use the default one -- we
can register some components. Let's start with a utility:

  >>> import zope.interface
  >>> class IMyUtility(zope.interface.Interface):
  ...     pass

  >>> import persistent
  >>> from zope.container.contained import Contained
  >>> @zope.interface.implementer(IMyUtility)
  ... class MyUtility(persistent.Persistent, Contained):
  ...     def __init__(self, title):
  ...         self.title = title
  ...     def __repr__(self):
  ...         return "%s('%s')" %(self.__class__.__name__, self.title)

Now we can create an instance of our utility and put it in the site
management folder and register it:

  >>> myutil = MyUtility('My custom utility')
  >>> default['myutil'] = myutil
  >>> sm.registerUtility(myutil, IMyUtility, 'u1')

Now we can ask the site manager for the utility:

  >>> sm.queryUtility(IMyUtility, 'u1')
  MyUtility('My custom utility')

Of course, the local site manager has also access to the global component
registrations:

  >>> gutil = MyUtility('Global Utility')
  >>> from zope.component import getGlobalSiteManager
  >>> gsm = getGlobalSiteManager()
  >>> gsm.registerUtility(gutil, IMyUtility, 'gutil')

  >>> sm.queryUtility(IMyUtility, 'gutil')
  MyUtility('Global Utility')

Next let's see whether we can also successfully register an adapter as
well. Here the adapter will provide the size of a file:

  >>> class IFile(zope.interface.Interface):
  ...     pass

  >>> class ISized(zope.interface.Interface):
  ...     pass

  >>> @zope.interface.implementer(IFile)
  ... class File(object):
  ...     pass

  >>> @zope.interface.implementer(ISized)
  ... class FileSize(object):
  ...     def __init__(self, context):
  ...         self.context = context

Now that we have the adapter we need to register it:

  >>> sm.registerAdapter(FileSize, [IFile])

Finally, we can get the adapter for a file:

  >>> file = File()
  >>> size = sm.queryAdapter(file, ISized, name='')
  >>> size.__class__
  <class 'FileSize'>
  >>> size.context is file
  True

By the way, once you set a site

  >>> from zope.component import hooks
  >>> hooks.setSite(myfolder)

you can simply use the zope.component's `getSiteManager()` method to get
the nearest site manager:

  >>> from zope.component import getSiteManager
  >>> getSiteManager() is sm
  True

This also means that you can simply use zope.component to look up your utility

  >>> from zope.component import getUtility
  >>> getUtility(IMyUtility, 'gutil')
  MyUtility('Global Utility')

or the adapter via the interface's `__call__` method:

  >>> size = ISized(file)
  >>> size.__class__
  <class 'FileSize'>
  >>> size.context is file
  True


Multiple Sites
--------------

Until now we have only dealt with one local and the global site. But things
really become interesting, once we have multiple sites. We can override other
local configuration.

This behaviour uses the notion of location, therefore we need to configure the
zope.location package first:

  >>> import zope.configuration.xmlconfig
  >>> _  = zope.configuration.xmlconfig.string("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ...   <include package="zope.component" file="meta.zcml"/>
  ...   <include package="zope.location" />
  ... </configure>
  ... """)

Let's now create a new folder called `folder11`, add it to `myfolder` and make
it a site:

  >>> myfolder11 = folder.Folder()
  >>> myfolder['myfolder11'] = myfolder11
  >>> myfolder11.setSiteManager(site.LocalSiteManager(myfolder11))
  >>> sm11 = myfolder11.getSiteManager()

If we ask the second site manager for its next, we get

  >>> sm11.__bases__ == (sm, )
  True

and the first site manager should have the folling sub manager:

  >>> sm.subs == (sm11,)
  True

If we now register a second utility with the same name and interface with the
new site manager folder,

  >>> default11 = sm11['default']
  >>> myutil11 = MyUtility('Utility, uno & uno')
  >>> default11['myutil'] = myutil11

  >>> sm11.registerUtility(myutil11, IMyUtility, 'u1')

then it will will be available in the second site manager

  >>> sm11.queryUtility(IMyUtility, 'u1')
  MyUtility('Utility, uno & uno')

but not in the first one:

  >>> sm.queryUtility(IMyUtility, 'u1')
  MyUtility('My custom utility')

It is also interesting to look at the use cases of moving and copying a
site. To do that we create a second root folder and make it a site, so that
site hierarchy is as follows:

::

           _____ global site _____
          /                       \
      myfolder1                myfolder2
          |
      myfolder11


  >>> myfolder2 = folder.rootFolder()
  >>> myfolder2.setSiteManager(site.LocalSiteManager(myfolder2))

Before we can move or copy sites, we need to register two event subscribers
that manage the wiring of site managers after moving or copying:

  >>> from zope import container
  >>> gsm.registerHandler(
  ...    site.changeSiteConfigurationAfterMove,
  ...    (ISite, container.interfaces.IObjectMovedEvent),
  ...    )

We only have to register one event listener, since the copy action causes an
`IObjectAddedEvent` to be created, which is just a special type of
`IObjectMovedEvent`.

First, make sure that everything is setup correctly in the first place:

  >>> myfolder11.getSiteManager().__bases__ == (myfolder.getSiteManager(), )
  True
  >>> myfolder.getSiteManager().subs[0] is myfolder11.getSiteManager()
  True
  >>> myfolder2.getSiteManager().subs
  ()

Let's now move `myfolder11` from `myfolder` to `myfolder2`:

  >>> myfolder2['myfolder21'] = myfolder11
  >>> del myfolder['myfolder11']

Now the next site manager for `myfolder11`'s site manager should have changed:

  >>> myfolder21 = myfolder11
  >>> myfolder21.getSiteManager().__bases__ == (myfolder2.getSiteManager(), )
  True
  >>> myfolder2.getSiteManager().subs[0] is myfolder21.getSiteManager()
  True
  >>> myfolder.getSiteManager().subs
  ()

Make sure that our interfaces and classes are picklable:

  >>> import sys
  >>> sys.modules['zope.site.tests'].IMyUtility = IMyUtility
  >>> IMyUtility.__module__ = 'zope.site.tests'
  >>> sys.modules['zope.site.tests'].MyUtility = MyUtility
  >>> MyUtility.__module__ = 'zope.site.tests'

  >>> from pickle import dumps, loads
  >>> data = dumps(myfolder2['myfolder21'])
  >>> myfolder['myfolder11'] = loads(data)

  >>> myfolder11 = myfolder['myfolder11']
  >>> myfolder11.getSiteManager().__bases__ == (myfolder.getSiteManager(), )
  True
  >>> myfolder.getSiteManager().subs[0] is myfolder11.getSiteManager()
  True
  >>> myfolder2.getSiteManager().subs[0] is myfolder21.getSiteManager()
  True

Finally, let's check that everything works fine when our folder is moved
to the folder that doesn't contain any site manager. Our folder's
sitemanager's bases should be set to global site manager.

  >>> myfolder11.getSiteManager().__bases__ == (myfolder.getSiteManager(), )
  True

  >>> nosm = folder.Folder()
  >>> nosm['root'] = myfolder11
  >>> myfolder11.getSiteManager().__bases__ == (gsm, )
  True
