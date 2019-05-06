===============================
File representation for folders
===============================

Folders can be represented in file-system-like protocols (e.g. FTP). An
adapter abstracts some internals away and adds support for accessing the
'++etc++site' folder from those protocols.

  >>> from zope.container.folder import Folder
  >>> from zope.container.directory import ReadDirectory
  >>> folder = Folder()

The new folder isn't a site manager and doesn't have any entries:

  >>> fs_folder = ReadDirectory(folder)
  >>> list(fs_folder.keys())
  []
  >>> fs_folder.get('test', )
  >>> fs_folder['test']
  Traceback (most recent call last):
  KeyError: 'test'
  >>> list(fs_folder.__iter__())
  []
  >>> list(fs_folder.values())
  []
  >>> len(fs_folder)
  0
  >>> list(fs_folder.items())
  []
  >>> 'test' in fs_folder
  False

If we pretend that our folder is a site, we have that entry:

  >>> from zope.component.interfaces import ISite
  >>> from zope.interface import alsoProvides
  >>> alsoProvides(folder, ISite)
  >>> folder.getSiteManager = lambda: 42
  >>> list(fs_folder.keys())
  ['++etc++site']
  >>> fs_folder['++etc++site']
  42
  >>> len(fs_folder)
  1


This is a short regression test for #728: we get a KeyError when trying to
access non-existing entries:

  >>> from zope.security.proxy import ProxyFactory
  >>> from zope.security.checker import NamesChecker
  >>> proxied_folder = ProxyFactory(fs_folder, NamesChecker(('get',)))
  >>> proxied_fs_folder = ReadDirectory(proxied_folder)
  >>> print(proxied_fs_folder['i dont exist'])
  Traceback (most recent call last):
  KeyError: 'i dont exist'
