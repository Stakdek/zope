##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Form utility functions

This is an implementation only used by zope.formlib.objectwidget, not
by the rest of the widgets in zope.formlib. We would like to keep it
this way.

This module is not directly tested: zope.app.form does have tests to
test this, and the objectwidget implementation tests this indirectly.

At some point we would like to rewrite zope.formlib.objectwidget so it
uses the infrastructure provided by zope.formlib itself.
"""
__docformat__ = 'restructuredtext'

from zope import component
from zope.schema import getFieldsInOrder
from zope.formlib.interfaces import IWidget
from zope.formlib.interfaces import WidgetsError
from zope.formlib.interfaces import InputErrors
from zope.formlib.interfaces import IInputWidget
from zope.formlib.interfaces import IWidgetFactory

# A marker that indicates 'no value' for any of the utility functions that
# accept a 'value' argument.
no_value = object()

def _fieldlist(names, schema):
    if not names:
        fields = getFieldsInOrder(schema)
    else:
        fields = [ (name, schema[name]) for name in names ]
    return fields


def _createWidget(context, field, viewType, request):
    """Creates a widget given a `context`, `field`, and `viewType`."""
    field = field.bind(context)
    return component.getMultiAdapter((field, request), viewType)

def _widgetHasStickyValue(widget):
    """Returns ``True`` if the widget has a sticky value.

    A sticky value is input from the user that should not be overridden
    by an object's current field value. E.g. a user may enter an invalid
    postal code, submit the form, and receive a validation error - the postal
    code should be treated as 'sticky' until the user successfully updates
    the object.
    """
    return IInputWidget.providedBy(widget) and widget.hasInput()

def setUpWidget(view, name, field, viewType, value=no_value, prefix=None,
                ignoreStickyValues=False, context=None):
    """Sets up a single view widget.

    The widget will be an attribute of the `view`. If there is already
    an attribute of the given name, it must be a widget and it will be
    initialized with the given `value` if not ``no_value``.

    If there isn't already a `view` attribute of the given name, then a
    widget will be created and assigned to the attribute.
    """
    if context is None:
        context = view.context
    widgetName = name + '_widget'

    # check if widget already exists
    widget = getattr(view, widgetName, None)
    if widget is None:
        # does not exist - create it
        widget = _createWidget(context, field, viewType, view.request)
        setattr(view, widgetName, widget)
    elif IWidgetFactory.providedBy(widget):
        # exists, but is actually a factory - use it to create the widget
        widget = widget(field.bind(context), view.request)
        setattr(view, widgetName, widget)

    # widget must implement IWidget
    if not IWidget.providedBy(widget):
        raise TypeError(
            "Unable to configure a widget for %s - attribute %s does not "
            "implement IWidget" % (name, widgetName))

    if prefix:
        widget.setPrefix(prefix)

    if value is not no_value and (
        ignoreStickyValues or not _widgetHasStickyValue(widget)):
        widget.setRenderedValue(value)


def setUpWidgets(view, schema, viewType, prefix=None, ignoreStickyValues=False,
                 initial={}, names=None, context=None):
    """Sets up widgets for the fields defined by a `schema`.

    Appropriate for collecting input without a current object implementing
    the schema (such as an add form).

    `view` is the view that will be configured with widgets.

    `viewType` is the type of widgets to create (e.g. IInputWidget or
    IDisplayWidget).

    `schema` is an interface containing the fields that widgets will be
    created for.

    `prefix` is a string that is prepended to the widget names in the generated
    HTML. This can be used to differentiate widgets for different schemas.

    `ignoreStickyValues` is a flag that, when ``True``, will cause widget
    sticky values to be replaced with the context field value or a value
    specified in initial.

    `initial` is a mapping of field names to initial values.

    `names` is an optional iterable that provides an ordered list of field
    names to use. If names is ``None``, the list of fields will be defined by
    the schema.

    `context` provides an alternative context for acquisition.
    """
    for (name, field) in _fieldlist(names, schema):
        setUpWidget(view, name, field, viewType,
                    value=initial.get(name, no_value),
                    prefix=prefix,
                    ignoreStickyValues=ignoreStickyValues,
                    context=context)


def applyWidgetsChanges(view, schema, target=None, names=None):
    """Updates an object with values from a view's widgets.

    `view` contained the widgets that perform the update. By default, the
    widgets will update the view's context.

    `target` can be specified as an alternative object to update.

    `schema` contrains the values provided by the widgets.

    `names` can be specified to update a subset of the schema constrained
    values.
    """
    errors = []
    changed = False
    if target is None:
        target = view.context

    for name, field in _fieldlist(names, schema):
        widget = getattr(view, name + '_widget')
        if IInputWidget.providedBy(widget) and widget.hasInput():
            try:
                changed = widget.applyChanges(target) or changed
            except InputErrors as v:
                errors.append(v)
    if errors:
        raise WidgetsError(errors)

    return changed
