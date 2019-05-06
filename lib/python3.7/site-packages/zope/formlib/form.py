##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Forms.

This module provides the `zope.formlib.interfaces.IFormAPI` interface.
"""
import binascii
import datetime
import os
import re
import sys
import pytz
try:
    from html import escape
except ImportError:     # pragma: NO COVER
    from cgi import escape

import zope.browser.interfaces
import zope.event
import zope.i18n
import zope.i18nmessageid
import zope.security
import zope.interface.interfaces
import zope.publisher.browser
import zope.publisher.interfaces.browser
from zope import component, interface, schema
from zope.browserpage import ViewPageTemplateFile
from zope.interface.common import idatetime
from zope.interface.interface import InterfaceClass
from zope.publisher.interfaces.http import MethodNotAllowed
from zope.schema.interfaces import IField
from zope.schema.interfaces import ValidationError
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.lifecycleevent import Attributes
from zope.browserpage import namedtemplate

from zope.formlib._compat import basestring, unicode
from zope.formlib.interfaces import IWidgetInputErrorView
from zope.formlib.interfaces import IInputWidget, IDisplayWidget
from zope.formlib.interfaces import WidgetsError, MissingInputError
from zope.formlib.interfaces import InputErrors, WidgetInputError
from zope.formlib.interfaces import InvalidFormError, InvalidCSRFTokenError

from zope.formlib import interfaces
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("zope")


interface.moduleProvides(interfaces.IFormAPI)


def expandPrefix(prefix):
    """Expand prefix string by adding a trailing period if needed.

    expandPrefix(p) should be used instead of p+'.' in most contexts.
    """
    if prefix and not prefix.endswith('.'):
        return prefix + '.'
    return prefix

@interface.implementer(interfaces.IFormField)
class FormField(object):
    """Implementation of `zope.formlib.interfaces.IFormField`. """

    def __init__(self, field, name=None, prefix='',
                 for_display=None, for_input=None, custom_widget=None,
                 render_context=False, get_rendered=None, interface=None
                 ):
        self.field = field
        if name is None:
            name = field.__name__
        assert name
        self.__name__ = expandPrefix(prefix) + name
        self.prefix = prefix
        if interface is None:
            interface = field.interface
        self.interface = interface
        self.for_display = for_display
        self.for_input = for_input
        self.custom_widget = custom_widget
        self.render_context = render_context
        self.get_rendered = get_rendered

Field = FormField


def _initkw(keep_readonly=(), omit_readonly=False, **defaults):
    return keep_readonly, omit_readonly, defaults


@interface.implementer(interfaces.IFormFields)
class FormFields(object):
    """Implementation of `zope.formlib.interfaces.IFormFields`."""

    def __init__(self, *args, **kw):
        keep_readonly, omit_readonly, defaults = _initkw(**kw)

        fields = []
        for arg in args:
            if isinstance(arg, InterfaceClass):
                for name, field in schema.getFieldsInOrder(arg):
                    fields.append((name, field, arg))
            elif IField.providedBy(arg):
                name = arg.__name__
                if not name:
                    raise ValueError(
                            "Field has no name")

                fields.append((name, arg, arg.interface))
            elif isinstance(arg, FormFields):
                for form_field in arg:
                    fields.append(
                        (form_field.__name__,
                         form_field,
                         form_field.interface)
                        )
            elif isinstance(arg, FormField):
                fields.append((arg.__name__, arg, arg.interface))
            else:
                raise TypeError("Unrecognized argument type", arg)


        seq = []
        byname = {}
        for name, field, iface in fields:
            if isinstance(field, FormField):
                form_field = field
            else:
                if field.readonly:
                    if omit_readonly and (name not in keep_readonly):
                        continue
                form_field = FormField(field, interface=iface, **defaults)
                name = form_field.__name__

            if name in byname:
                raise ValueError("Duplicate name", name)
            seq.append(form_field)
            byname[name] = form_field

        self.__FormFields_seq__ = seq
        self.__FormFields_byname__ = byname

    def __len__(self):
        return len(self.__FormFields_seq__)

    def __iter__(self):
        return iter(self.__FormFields_seq__)

    def __getitem__(self, name):
        return self.__FormFields_byname__[name]

    def get(self, name, default=None):
        return self.__FormFields_byname__.get(name, default)

    def __add__(self, other):
        if not isinstance(other, FormFields):
            return NotImplemented
        return self.__class__(self, other)

    def select(self, *names):
        """Return a modified instance with an ordered subset of fields."""
        return self.__class__(*[self[name] for name in names])

    def omit(self, *names):
        """Return a modified instance omitting given fields."""
        return self.__class__(*[ff for ff in self if ff.__name__ not in names])

Fields = FormFields


def fields_initkw(keep_all_readonly=False, **other):
    return keep_all_readonly, other

# Backward compat
def fields(*args, **kw):
    keep_all_readonly, other = fields_initkw(**kw)
    other['omit_readonly'] = not keep_all_readonly
    return FormFields(*args, **other)


@interface.implementer(interfaces.IWidgets)
class Widgets(object):
    """Implementation of `zope.formlib.interfaces.IWidgets`."""

    def __init__(self, widgets, prefix_length=None, prefix=None):
        self.__Widgets_widgets_items__ = widgets
        self.__Widgets_widgets_list__ = [w for (i, w) in widgets]
        if prefix is None:
            # BBB Allow old code using the prefix_length argument.
            if prefix_length is None:
                raise TypeError(
                    "One of 'prefix_length' and 'prefix' is required."
                    )
            self.__Widgets_widgets_dict__ = dict(
                [(w.name[prefix_length:], w) for (i, w) in widgets]
                )
        else:
            prefix = expandPrefix(prefix)
            self.__Widgets_widgets_dict__ = dict(
                [(_widgetKey(w, prefix), w) for (i, w) in widgets]
                )

    def __iter__(self):
        return iter(self.__Widgets_widgets_list__)

    def __getitem__(self, name):
        return self.__Widgets_widgets_dict__[name]

    # TODO need test
    def get(self, name):
        return self.__Widgets_widgets_dict__.get(name)

    def __iter_input_and_widget__(self):
        return iter(self.__Widgets_widgets_items__)


    # TODO need test
    def __add__(self, other):
        widgets = self.__class__([], 0)
        widgets.__Widgets_widgets_items__ = (
            self.__Widgets_widgets_items__ + other.__Widgets_widgets_items__)
        widgets.__Widgets_widgets_list__ = (
            self.__Widgets_widgets_list__ + other.__Widgets_widgets_list__)
        widgets.__Widgets_widgets_dict__ = self.__Widgets_widgets_dict__.copy()
        widgets.__Widgets_widgets_dict__.update(other.__Widgets_widgets_dict__)
        return widgets

def canWrite(context, field):
    writer = getattr(field, 'writer', None)
    if writer is not None:
        return zope.security.canAccess(context, writer.__name__)
    return zope.security.canWrite(context, field.__name__)

def setUpWidgets(form_fields,
                 form_prefix=None, context=None, request=None, form=None,
                 data=(), adapters=None, ignore_request=False):
    """Sets up widgets."""
    if request is None:
        request = form.request
    if context is None and form is not None:
        context = form.context
    if form_prefix is None:
        form_prefix = form.prefix

    widgets = []
    adapter = None
    for form_field in form_fields:
        field = form_field.field
        if form_field.render_context:
            if adapters is None:
                adapters = {}

            # Adapt context, if necessary
            interface = form_field.interface
            adapter = adapters.get(interface)
            if adapter is None:
                if interface is None:
                    adapter = context
                else:
                    adapter = interface(context)
                adapters[interface] = adapter
                if interface is not None:
                    adapters[interface.__name__] = adapter
            field = field.bind(adapter)
        else:
            field = field.bind(context)

        readonly = form_field.for_display
        readonly = readonly or (field.readonly and not form_field.for_input)
        readonly = readonly or (
            (form_field.render_context & interfaces.DISPLAY_UNWRITEABLE)
            and not canWrite(adapter, field)
            )

        if form_field.custom_widget is not None:
            widget = form_field.custom_widget(field, request)
        else:
            if readonly:
                widget = component.getMultiAdapter((field, request),
                                                   IDisplayWidget)
            else:
                widget = component.getMultiAdapter((field, request),
                                                   IInputWidget)

        prefix = form_prefix
        if form_field.prefix:
            prefix = expandPrefix(prefix) + form_field.prefix

        widget.setPrefix(prefix)

        if ignore_request or readonly or not widget.hasInput():
            # Get the value to render
            if form_field.__name__ in data:
                widget.setRenderedValue(data[form_field.__name__])
            elif form_field.get_rendered is not None:
                widget.setRenderedValue(form_field.get_rendered(form))
            elif form_field.render_context:
                widget.setRenderedValue(field.get(adapter))
            else:
                widget.setRenderedValue(field.default)

        widgets.append((not readonly, widget))

    return Widgets(widgets, prefix=form_prefix)

def setUpInputWidgets(form_fields, form_prefix, context, request,
                      form=None, ignore_request=False):
    widgets = []
    for form_field in form_fields:
        field = form_field.field.bind(context)
        widget = _createWidget(form_field, field, request, IInputWidget)

        prefix = form_prefix
        if form_field.prefix:
            prefix = expandPrefix(prefix) + form_field.prefix

        widget.setPrefix(prefix)

        if ignore_request:
            if form_field.get_rendered is not None:
                value = form_field.get_rendered(form)
            else:
                value = field.default
            widget.setRenderedValue(value)

        widgets.append((True, widget))
    return Widgets(widgets, prefix=form_prefix)


def _createWidget(form_field, field, request, iface):
    if form_field.custom_widget is None:
        return component.getMultiAdapter((field, request), iface)
    else:
        return form_field.custom_widget(field, request)


def getWidgetsData(widgets, form_prefix, data):
    """See `zope.formlib.interfaces.IFormAPI.getWidgetsData`"""
    errors = []
    form_prefix = expandPrefix(form_prefix)

    for input, widget in widgets.__iter_input_and_widget__():
        if input and IInputWidget.providedBy(widget):
            name = _widgetKey(widget, form_prefix)

            if not widget.hasInput():
                continue

            try:
                data[name] = widget.getInputValue()
            except ValidationError as error:
                # convert field ValidationError to WidgetInputError
                error = WidgetInputError(widget.name, widget.label, error)
                errors.append(error)
            except InputErrors as error:
                errors.append(error)

    return errors

def _widgetKey(widget, form_prefix):
    name = widget.name
    if name.startswith(form_prefix):
        name = name[len(form_prefix):]
    else:
        raise ValueError("Name does not match prefix", name, form_prefix)
    return name

def setUpEditWidgets(form_fields, form_prefix, context, request,
                     adapters=None, for_display=False,
                     ignore_request=False):
    if adapters is None:
        adapters = {}

    widgets = []
    for form_field in form_fields:
        field = form_field.field
        # Adapt context, if necessary
        interface = form_field.interface
        adapter = adapters.get(interface)
        if adapter is None:
            if interface is None:
                adapter = context
            else:
                adapter = interface(context)
            adapters[interface] = adapter
            if interface is not None:
                adapters[interface.__name__] = adapter

        field = field.bind(adapter)

        readonly = form_field.for_display
        readonly = readonly or (field.readonly and not form_field.for_input)
        readonly = readonly or (
            (form_field.render_context & interfaces.DISPLAY_UNWRITEABLE)
            and not canWrite(adapter, field)
            )
        readonly = readonly or for_display

        if readonly:
            iface = IDisplayWidget
        else:
            iface = IInputWidget
        widget = _createWidget(form_field, field, request, iface)

        prefix = form_prefix
        if form_field.prefix:
            prefix = expandPrefix(prefix) + form_field.prefix

        widget.setPrefix(prefix)

        if ignore_request or readonly or not widget.hasInput():
            # Get the value to render
            value = field.get(adapter)
            widget.setRenderedValue(value)

        widgets.append((not readonly, widget))

    return Widgets(widgets, prefix=form_prefix)

def setUpDataWidgets(form_fields, form_prefix, context, request, data=(),
                     for_display=False, ignore_request=False):
    widgets = []
    for form_field in form_fields:
        field = form_field.field.bind(context)
        readonly = for_display or field.readonly or form_field.for_display
        if readonly:
            iface = IDisplayWidget
        else:
            iface = IInputWidget
        widget = _createWidget(form_field, field, request, iface)

        prefix = form_prefix
        if form_field.prefix:
            prefix = expandPrefix(prefix) + form_field.prefix

        widget.setPrefix(prefix)

        if ((form_field.__name__ in data)
            and (ignore_request or readonly or not widget.hasInput())
            ):
            widget.setRenderedValue(data[form_field.__name__])

        widgets.append((not readonly, widget))

    return Widgets(widgets, prefix=form_prefix)


class NoInputData(interface.Invalid):
    """There was no input data because:

    - It wasn't asked for

    - It wasn't entered by the user

    - It was entered by the user, but the value entered was invalid

    This exception is part of the internal implementation of checkInvariants.

    """

class FormData:

    def __init__(self, schema, data, context):
        self._FormData_data___ = data
        self._FormData_schema___ = schema
        self._FormData_context___ = context

    def __getattr__(self, name):
        schema = self._FormData_schema___
        data = self._FormData_data___
        context = self._FormData_context___
        try:
            field = schema[name]
        except KeyError:
            raise AttributeError(name)
        else:
            value = data.get(name, data)
            if value is data:
                if context is None:
                    raise NoInputData(name)
                # The value is not in the form look it up on the context:
                field = schema[name]
                adapted_context = schema(context)
                if IField.providedBy(field):
                    value = field.get(adapted_context)
                elif (zope.interface.interfaces.IAttribute.providedBy(field)
                      and
                      not zope.interface.interfaces.IMethod.providedBy(field)):
                    # Fallback for non-field schema contents:
                    value = getattr(adapted_context, name)
                else:
                    # Don't know how to extract value
                    raise NoInputData(name)
            if zope.interface.interfaces.IMethod.providedBy(field):
                if not IField.providedBy(field):
                    raise RuntimeError(
                        "Data value is not a schema field", name)
                v = lambda: value
            else:
                v = value
            setattr(self, name, v)
            return v
        raise AttributeError(name)


def checkInvariants(form_fields, form_data, context):
    """See `zope.formlib.interfaces.IFormAPI.checkInvariants`"""

    # First, collect the data for the various schemas
    schema_data = {}
    for form_field in form_fields:
        schema = form_field.interface
        if schema is None:
            continue

        data = schema_data.get(schema)
        if data is None:
            data = schema_data[schema] = {}

        if form_field.__name__ in form_data:
            data[form_field.field.__name__] = form_data[form_field.__name__]

    # Now validate the individual schemas
    errors = []
    for schema, data in schema_data.items():
        try:
            schema.validateInvariants(FormData(schema, data, context), errors)
        except interface.Invalid:
            pass # Just collect the errors

    return [error for error in errors if not isinstance(error, NoInputData)]

def applyData(context, form_fields, data, adapters=None):
    if adapters is None:
        adapters = {}

    descriptions = {}

    for form_field in form_fields:
        field = form_field.field
        # Adapt context, if necessary
        interface = form_field.interface
        adapter = adapters.get(interface)
        if adapter is None:
            if interface is None:
                adapter = context
            else:
                adapter = interface(context)
            adapters[interface] = adapter

        name = form_field.__name__
        newvalue = data.get(name, form_field) # using form_field as marker
        if (newvalue is not form_field) \
        and (field.get(adapter) != newvalue):
            descriptions.setdefault(interface, []).append(field.__name__)
            field.set(adapter, newvalue)

    return descriptions

def applyChanges(context, form_fields, data, adapters=None):
    """See `zope.formlib.interfaces.IFormAPI.applyChanges`"""
    return bool(applyData(context, form_fields, data, adapters))


def _callify(meth):
    """Return method if it is callable,
       otherwise return the form's method of the name"""
    if callable(meth):
        return meth
    elif isinstance(meth, str):
        return lambda form, *args: getattr(form, meth)(*args)


@interface.implementer(interfaces.IAction)
class Action(object):
    """See `zope.formlib.interfaces.IAction`"""
    _identifier = re.compile('[A-Za-z][a-zA-Z0-9_]*$')

    def __init__(self, label, success=None, failure=None,
                condition=None, validator=None, prefix='actions',
                name=None, data=None):

        self.label = label
        self.setPrefix(prefix)
        self.setName(name)
        self.bindMethods(success_handler=success,
                        failure_handler=failure,
                        condition=condition,
                        validator=validator)

        if data is None:
            data = {}
        self.data = data

    def bindMethods(self, **methods):
        """Bind methods to the action"""
        for k, v in methods.items():
            setattr(self, k, _callify(v))

    def setName(self, name):
        """Make sure name is ASCIIfiable.
           Use action label if name is None
        """
        if name is None:
            name = self.label
            if self._identifier.match(name):
                name = name.lower()
            else:
                if isinstance(name, unicode):
                    name = name.encode("utf-8")
                name = binascii.hexlify(name).decode()
        self.name = name
        self.__name__ = self.prefix + name

    def setPrefix(self, prefix):
        """Set prefix"""
        self.prefix = expandPrefix(prefix)

    def __get__(self, form, class_=None):
        if form is None:
            return self
        result = self.__class__.__new__(self.__class__)
        result.__dict__.update(self.__dict__)
        result.form = form
        result.__name__ = expandPrefix(form.prefix) + result.__name__
        interface.alsoProvides(result, interfaces.IBoundAction)
        return result

    def available(self):
        condition = self.condition
        return (condition is None) or condition(self.form, self)

    def validate(self, data):
        if self.validator is not None:
            return self.validator(self.form, self, data)

    def success(self, data):
        if self.success_handler is not None:
            return self.success_handler(self.form, self, data)

    def failure(self, data, errors):
        if self.failure_handler is not None:
            return self.failure_handler(self.form, self, data, errors)

    def submitted(self):
        return (self.__name__ in self.form.request.form) and self.available()

    def update(self):
        pass

    render = namedtemplate.NamedTemplate('render')

@namedtemplate.implementation(interfaces.IAction)
def render_submit_button(self):
    if not self.available():
        return ''
    label = self.label
    if isinstance(label, zope.i18nmessageid.Message):
        label = zope.i18n.translate(self.label, context=self.form.request)
    return ('<input type="submit" id="%s" name="%s" value="%s"'
            ' class="button" />' %
            (self.__name__, self.__name__, escape(label, quote=True))
            )

class action(object):
    """See `zope.formlib.interfaces.IFormAPI.action`"""
    def __init__(self, label, actions=None, **options):
        caller_locals = sys._getframe(1).f_locals
        if actions is None:
            actions = caller_locals.get('actions')
        if actions is None:
            actions = caller_locals['actions'] = Actions()
        self.actions = actions
        self.label = label
        self.options = options

    def __call__(self, success):
        action = Action(self.label, success=success, **self.options)
        self.actions.append(action)
        return action


@interface.implementer(interfaces.IActions)
class Actions(object):

    def __init__(self, *actions):
        self.actions = actions
        self.byname = dict([(a.__name__, a) for a in actions])

    def __iter__(self):
        return iter(self.actions)

    def __getitem__(self, name):
        try:
            return self.byname[name]
        except TypeError:
            if isinstance(name, slice):
                return self.__class__(
                    *self.actions[name.start:name.stop:name.step]
                    )

    def append(self, action):
        self.actions += (action, )
        self.byname[action.__name__] = action

    # TODO need test
    def __add__(self, other):
        return self.__class__(*(self.actions + other.actions))

    def copy(self):
        return self.__class__(*self.actions)

    def __get__(self, inst, class_):
        if inst is None:
            return self
        return self.__class__(*[a.__get__(inst) for a in self.actions])

def handleSubmit(actions, data, default_validate=None):
    """Handle a submit."""
    for action in actions:
        if action.submitted():
            errors = action.validate(data)
            if errors is None and default_validate is not None:
                errors = default_validate(action, data)
            return errors, action

    return None, None

# TODO need test for this
def availableActions(form, actions):
    result = []
    for action in actions:
        condition = action.condition
        if (condition is None) or condition(form, action):
            result.append(action)
    return result


@interface.implementer(interfaces.IForm)
class FormBase(zope.publisher.browser.BrowserPage):

    label = u''

    prefix = 'form'

    status = ''

    errors = ()

    ignoreContext = False

    method = None

    protected = False

    csrftoken = None

    def setPrefix(self, prefix):
        self.prefix = prefix

    def setUpToken(self):
        self.csrftoken = self.request.getCookies().get('__csrftoken__')
        if self.csrftoken is None:
            # It is possible another form, that is rendered as part of
            # this request, already set a csrftoken. In that case we
            # should find it in the response cookie and use that.
            setcookie = self.request.response.getCookie('__csrftoken__')
            if setcookie is not None:
                self.csrftoken = setcookie['value']
            else:
                # Ok, nothing found, we should generate one and set
                # it in the cookie ourselves. Note how we ``str()``
                # the hex value of the ``os.urandom`` call here, as
                # Python-3 will return bytes and the cookie roundtrip
                # of a bytes values gets messed up.
                self.csrftoken = str(binascii.hexlify(os.urandom(32)))
                self.request.response.setCookie(
                    '__csrftoken__',
                    self.csrftoken,
                    path='/',
                    expires=None,  # equivalent to "remove on browser quit"
                    httpOnly=True,  # no javascript access please.
                    )

    def checkToken(self):
        cookietoken = self.request.getCookies().get('__csrftoken__')
        if cookietoken is None:
            # CSRF is enabled, so we really should get a token from the
            # cookie. We didn't get it, so this submit is invalid!
            raise InvalidCSRFTokenError(_('Invalid CSRF token'))
        if cookietoken != self.request.form.get('__csrftoken__', None):
            # The token in the cookie is different from the one in the
            # form data. This submit is invalid!
            raise InvalidCSRFTokenError(_('Invalid CSRF token'))

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            form=self, adapters=self.adapters, ignore_request=ignore_request)

    def validate(self, action, data):
        if self.method is not None:
            # Verify the correct request method was used.
            if self.method.upper() != self.request.method.upper():
                raise MethodNotAllowed(self.context, self.request)
        if self.protected:
            self.checkToken()  # This form has CSRF protection enabled.
        if self.ignoreContext:
            context = None
        else:
            context = self.context
        return (getWidgetsData(self.widgets, self.prefix, data)
                + checkInvariants(self.form_fields, data, context))

    template = namedtemplate.NamedTemplate('default')

    # TODO also need to be able to show disabled actions
    def availableActions(self):
        return availableActions(self, self.actions)

    def resetForm(self):
        self.setUpWidgets(ignore_request=True)

    form_result = None
    form_reset = True

    def update(self):
        if self.protected:
            self.setUpToken()  # This form has CSRF protection enabled.
        self.setUpWidgets()
        self.form_reset = False

        data = {}
        errors, action = handleSubmit(self.actions, data, self.validate)
        # the following part will make sure that previous error not
        # get overriden by new errors. This is usefull for subforms. (ri)
        if self.errors is None:
            self.errors = errors
        else:
            if errors is not None:
                self.errors += tuple(errors)

        if errors:
            self.status = _('There were errors')
            result = action.failure(data, errors)
        elif errors is not None:
            self.form_reset = True
            result = action.success(data)
        else:
            result = None

        self.form_result = result

    def render(self):
        # if the form has been updated, it will already have a result
        if self.form_result is None:
            if self.form_reset:
                # we reset, in case data has changed in a way that
                # causes the widgets to have different data
                self.resetForm()
                self.form_reset = False
            self.form_result = self.template()

        return self.form_result

    def __call__(self):
        self.update()
        if self.request.response.getStatus() in [301, 302, 303, 307]:
            # Avoid rendering if the action caused a redirect.
            result = self.form_result or ''
        else:
            result = self.render()
        return result

    def error_views(self):
        for error in self.errors:
            if isinstance(error, basestring):
                yield error
            else:
                view = component.getMultiAdapter(
                    (error, self.request),
                    IWidgetInputErrorView)
                title = getattr(error, 'widget_title', None) # duck typing
                if title:
                    if isinstance(title, zope.i18n.Message):
                        title = zope.i18n.translate(title, context=self.request)
                    yield '%s: %s' % (title, view.snippet())
                else:
                    yield view.snippet()


def haveInputWidgets(form, action):
    for input, widget in form.widgets.__iter_input_and_widget__():
        if input:
            return True
    else:
        return False

class EditFormBase(FormBase):

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )

    @action(_("Apply"), condition=haveInputWidgets)
    def handle_edit_action(self, action, data):
        descriptions = applyData(self.context, self.form_fields, data,
                                self.adapters)
        if descriptions:
            descriptions = [Attributes(interface, *tuple(keys))
                           for interface, keys in descriptions.items()]
            zope.event.notify(ObjectModifiedEvent(self.context, *descriptions))
            formatter = self.request.locale.dates.getFormatter(
                'dateTime', 'medium')

            try:
                time_zone = idatetime.ITZInfo(self.request)
            except TypeError:
                time_zone = pytz.UTC

            status = _("Updated on ${date_time}",
                       mapping={'date_time':
                                formatter.format(
                                   datetime.datetime.now(time_zone)
                                   )
                        }
                       )
            self.status = status
        else:
            self.status = _('No changes')

class DisplayFormBase(FormBase):

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, for_display=True,
            ignore_request=ignore_request
            )

    actions = ()


@interface.implementer(interfaces.IAddFormCustomization,
                       zope.component.interfaces.IFactory)
@component.adapter(zope.browser.interfaces.IAdding,
                   zope.publisher.interfaces.browser.IBrowserRequest)
class AddFormBase(FormBase):

    ignoreContext = True


    def __init__(self, context, request):
        self.__parent__ = context
        super(AddFormBase, self).__init__(context, request)

    def setUpWidgets(self, ignore_request=False):
        self.widgets = setUpInputWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request,
            )

    @action(_("Add"), condition=haveInputWidgets)
    def handle_add(self, action, data):
        self.createAndAdd(data)

    # zope.formlib.interfaces.IAddFormCustomization

    def createAndAdd(self, data):
        ob = self.create(data)
        zope.event.notify(ObjectCreatedEvent(ob))
        return self.add(ob)

    def create(self, data):
        raise NotImplementedError(
            "concrete classes must implement create() or createAndAdd()")

    _finished_add = False

    def add(self, object):
        ob = self.context.add(object)
        self._finished_add = True
        return ob

    def render(self):
        if self._finished_add:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(AddFormBase, self).render()

    def nextURL(self):
        return self.context.nextURL()


default_page_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('pageform.pt'), interfaces.IPageForm)

default_subpage_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('subpageform.pt'), interfaces.ISubPageForm)

@interface.implementer(interfaces.IPageForm)
class PageForm(FormBase):
    pass

Form = PageForm

@interface.implementer(interfaces.IPageForm)
class PageEditForm(EditFormBase):
    pass

EditForm = PageEditForm

@interface.implementer(interfaces.IPageForm)
class PageDisplayForm(DisplayFormBase):
    pass

DisplayForm = PageDisplayForm

@interface.implementer(interfaces.IPageForm)
class PageAddForm(AddFormBase):
    pass

AddForm = PageAddForm

@interface.implementer(interfaces.ISubPageForm)
class SubPageForm(FormBase):
    pass

@interface.implementer(interfaces.ISubPageForm)
class SubPageEditForm(EditFormBase):
    pass

@interface.implementer(interfaces.ISubPageForm)
class SubPageDisplayForm(DisplayFormBase):
    pass
