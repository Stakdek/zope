============
 Interfaces
============

This package defines several basic interfaces.

.. currentmodule:: zope.browser.interfaces

IView
=====

Views adapt both a context and a request.

There is not much we can test except that ``IView`` is importable
and an interface:

  >>> from zope.interface import Interface
  >>> from zope.browser.interfaces import IView
  >>> Interface.providedBy(IView)
  True

.. autointerface:: IView

IBrowserView
============

Browser views are views specialized for requests from a browser (e.g.,
as distinct from WebDAV, FTP, XML-RPC, etc.).

There is not much we can test except that ``IBrowserView`` is importable
and an interface derived from :class:`IView`:

  >>> from zope.interface import Interface
  >>> from zope.browser.interfaces import IBrowserView
  >>> Interface.providedBy(IBrowserView)
  True
  >>> IBrowserView.extends(IView)
  True

.. autointerface:: IBrowserView

IAdding
=======

Adding views manage how newly-created items get added to containers.

There is not much we can test except that ``IAdding`` is importable
and an interface derived from :class:`IBrowserView`:

  >>> from zope.interface import Interface
  >>> from zope.browser.interfaces import IAdding
  >>> Interface.providedBy(IBrowserView)
  True
  >>> IAdding.extends(IBrowserView)
  True

.. autointerface:: IAdding

ITerms
======

The ``ITerms`` interface is used as a base for ``ISource`` widget
implementations.  This interfaces get used by ``zope.app.form`` and was
initially defined in ``zope.app.form.browser.interfaces``, which made it
impossible to use for other packages like ``z3c.form`` wihtout depending on
``zope.app.form``.

Moving such base components / interfaces to ``zope.browser`` makes it
possible to share them without undesirable dependencies.

There is not much we can test except that ITerms is importable
and an interface:

  >>> from zope.interface import Interface
  >>> from zope.browser.interfaces import ITerms
  >>> Interface.providedBy(ITerms)
  True

.. autointerface:: ITerms

ISystemErrorView
================

Views providing this interface can classify their contexts as system
errors. These errors can be handled in a special way (e. g. more
detailed logging).

There is not much we can test except that ``ISystemErrorView`` is importable
and an interface:

  >>> from zope.interface import Interface
  >>> from zope.browser.interfaces import ISystemErrorView
  >>> Interface.providedBy(ISystemErrorView)
  True

.. autointerface:: ISystemErrorView
