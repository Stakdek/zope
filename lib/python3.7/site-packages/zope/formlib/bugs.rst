Functional tests to verify bugs are gone
========================================


`setupWidgets` and `DISPLAY_UNWRITEABLE`
++++++++++++++++++++++++++++++++++++++++

This is to verify that bug #219948 is gone: setupWidgets doesn't check for
write access on the adapter.

Create a form containg two interfaces:

>>> import zope.formlib.tests
>>> class MyFormBase(object):
...     form_fields = zope.formlib.form.FormFields(
...         zope.formlib.tests.IOrder, zope.formlib.tests.IDescriptive,
...         render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).omit(
...             'now')
>>> class MyEditForm(MyFormBase, zope.formlib.form.EditForm):
...     pass

Instanciate the context objects and the form:

>>> import zope.publisher.browser
>>> request = zope.publisher.browser.TestRequest()
>>> order = zope.formlib.tests.Order()
>>> form = MyEditForm(order, request)

When we render the form, the fields of IDescriptive are read only because we
have no write access (this is configured in ftesting.zcml), the others are
writable[#needsinteraction]_:

>>> form.setUpWidgets()
>>> form.widgets['title']
<zope.formlib.widget.DisplayWidget object at 0x...>
>>> form.widgets['name']
<zope.formlib.textwidgets.TextWidget object at 0x...>


Make sure we have the same behaviour for non-edit forms:

>>> class MyForm(MyFormBase, zope.formlib.form.Form):
...     pass
>>> import zope.publisher.browser
>>> request = zope.publisher.browser.TestRequest()
>>> order = zope.formlib.tests.Order()
>>> form = MyForm(order, request)
>>> form.setUpWidgets()
>>> form.widgets['title']
<zope.formlib.widget.DisplayWidget object at 0x...>
>>> form.widgets['name']
<zope.formlib.textwidgets.TextWidget object at 0x...>



Clean up:

>>> zope.security.management.endInteraction()

.. [#needsinteraction]

    >>> import zope.security.management
    >>> import zope.security.testing
    >>> request.setPrincipal(zope.security.management.system_user)
    >>> zope.security.management.newInteraction(request)
