##############################################################################
#
# Copyright (c) 2001-2004 Zope Foundation and Contributors.
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
"""Browser Widget Definitions
"""
__docformat__ = 'restructuredtext'

from xml.sax.saxutils import quoteattr, escape

from zope.component import getMultiAdapter, provideAdapter
from zope.interface import implementer
from zope.schema.interfaces import ValidationError
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.formlib.interfaces import ConversionError
from zope.formlib.interfaces import WidgetInputError, MissingInputError
from zope.formlib.interfaces import IBrowserWidget
from zope.formlib.interfaces import ISimpleInputWidget
from zope.formlib.interfaces import IWidgetInputErrorView
from zope.formlib.interfaces import IWidget, InputErrors, IWidgetFactory
from zope.formlib._compat import toUnicode

from zope.i18n import translate
from zope.schema.interfaces import IChoice, ICollection

import warnings


if quoteattr("\r") != '"&13;"':
    _quoteattr = quoteattr

    def quoteattr(data):
        return _quoteattr(
            data, {'\n': '&#10;', '\r': '&#13;', '\t':'&#9;'})


@implementer(IWidget)
class Widget(object):
    """Mixin class providing functionality common across widget types."""

    _prefix = 'field.'
    _data_marker = object()
    _data = _data_marker

    visible = True

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.name = self._prefix + context.__name__
        self.label = self.context.title
        self.hint = self.context.description

    def _translate(self, text):
        return translate(text, context=self.request, default=text)

    def _renderedValueSet(self):
        """Returns ``True`` if the the widget's rendered value has been set.

        This is a convenience method that widgets can use to check whether
        or not `setRenderedValue` was called.
        """
        return self._data is not self._data_marker

    def setPrefix(self, prefix):
        if prefix and not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
        self.name = prefix + self.context.__name__

    def setRenderedValue(self, value):
        self._data = value


class InputWidget(Widget):
    """Mixin class providing some default input widget methods."""

    def hasValidInput(self):
        try:
            self.getInputValue()
            return True
        except InputErrors:
            return False

    def applyChanges(self, content):
        field = self.context
        value = self.getInputValue()
        if field.query(content, self) != value:
            field.set(content, value)
            return True
        else:
            return False


@implementer(IWidgetFactory)
class CustomWidgetFactory(object):
    """Custom Widget Factory."""

    def __init__(self, widget_factory, *args, **kw):
        self._widget_factory = widget_factory
        self.args = args
        self.kw = kw

    def _create(self, args):
        instance = self._widget_factory(*args)
        for name, value in self.kw.items():
            setattr(instance, name, value)
        return instance

    def __call__(self, context, request):
        # Sequence widget factory
        if ICollection.providedBy(context):
            args = (context, context.value_type, request) + self.args

        # Vocabulary widget factory
        elif IChoice.providedBy(context):
            args = (context, context.vocabulary, request) + self.args

        # Regular widget factory
        else:
            args = (context, request) + self.args

        return self._create(args)

@implementer(IBrowserWidget)
class BrowserWidget(Widget, BrowserView):
    """Base class for browser widgets.

    >>> setUp()

    The class provides some basic functionality common to all browser widgets.

    Browser widgets have a `required` attribute, which indicates whether or
    not the underlying field requires input. By default, the widget's required
    attribute is equal to the field's required attribute:

        >>> from zope.schema import Field
        >>> from zope.publisher.browser import TestRequest
        >>> field = Field(required=True)
        >>> widget = BrowserWidget(field, TestRequest())
        >>> widget.required
        True
        >>> field.required = False
        >>> widget = BrowserWidget(field, TestRequest())
        >>> widget.required
        False

    However, the two `required` values are independent of one another:

        >>> field.required = True
        >>> widget.required
        False

    Browser widgets have an error state, which can be rendered in a form using
    the `error()` method. The error method delegates the error rendering to a
    view that is registered as providing `IWidgetInputErrorView`. To
    illustrate, we can create and register a simple error display view:

        >>> from zope.formlib.interfaces import IWidgetInputError
        >>> @implementer(IWidgetInputErrorView)
        ... class SnippetErrorView:
        ...     def __init__(self, context, request):
        ...         self.context = context
        ...     def snippet(self):
        ...         return "The error: " + str(self.context.errors)
        >>> provideAdapter(SnippetErrorView,
        ...                (IWidgetInputError, IDefaultBrowserLayer),
        ...                IWidgetInputErrorView, '')

    Whever an error occurs, widgets should set _error:

        >>> widget._error = WidgetInputError('foo', 'Foo', ('Err1', 'Err2'))

    so that it can be displayed using the error() method:

        >>> widget.error()
        "The error: ('Err1', 'Err2')"

    >>> tearDown()

    """

    _error = None

    def __init__(self, context, request):
        super(BrowserWidget, self).__init__(context, request)
        self.required = context.required

    def error(self):
        if self._error:
            return getMultiAdapter((self._error, self.request),
                                   IWidgetInputErrorView).snippet()
        return ""

    def hidden(self):
        return ""


@implementer(ISimpleInputWidget)
class SimpleInputWidget(BrowserWidget, InputWidget):
    """A baseclass for simple HTML form widgets.

    >>> setUp()

    Simple input widgets read input from a browser form. To illustrate, we
    will use a test request with two form values:

        >>> from zope.publisher.browser import TestRequest
        >>> request = TestRequest(form={
        ...     'field.foo': u'hello\\r\\nworld',
        ...     'baz.foo': u'bye world'})

    Like all widgets, simple input widgets are a view to a field context:

        >>> from zope.schema import Field
        >>> field = Field(__name__='foo', title=u'Foo')
        >>> widget = SimpleInputWidget(field, request)

    Widgets are named using their field's name:

        >>> widget.name
        'field.foo'

    The default implementation for the widget label is to use the field title:

        >>> widget.label
        u'Foo'

    According the request, the widget has input because 'field.foo' is
    present:

        >>> widget.hasInput()
        True
        >>> widget.getInputValue()
        u'hello\\r\\nworld'

    Widgets maintain an error state, which is used to communicate invalid
    input or other errors:

        >>> widget._error is None
        True
        >>> widget.error()
        ''

    `setRenderedValue` is used to specify the value displayed by the widget to
    the user. This value, however, is not the same as the input value, which
    is read from the request:

        >>> widget.setRenderedValue('Hey\\nfolks')
        >>> widget.getInputValue()
        u'hello\\r\\nworld'
        >>> widget._error is None
        True
        >>> widget.error()
        ''

    You can use 'setPrefix' to remove or modify the prefix used to create the
    widget name as follows:

        >>> widget.setPrefix('')
        >>> widget.name
        'foo'
        >>> widget.setPrefix('baz')
        >>> widget.name
        'baz.foo'

    `getInputValue` always returns a value that can legally be assigned to
    the widget field. To illustrate widget validation, we can add a constraint
    to its field:

        >>> import re
        >>> field.constraint = re.compile('.*hello.*').match

    Because we modified the widget's name, the widget will now read different
    form input:

        >>> request.form[widget.name]
        u'bye world'

    This input violates the new field constraint and therefore causes an
    error when `getInputValue` is called:

        >>> widget.getInputValue() #doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        WidgetInputError: ('foo', u'Foo', ConstraintNotSatisfied(u'bye world'))

    Simple input widgets require that input be available in the form request.
    If input is not present, a ``MissingInputError`` is raised:

        >>> del request.form[widget.name]
        >>> widget.getInputValue() #doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        MissingInputError: ('baz.foo', u'Foo', None)

    A ``MissingInputError`` indicates that input is missing from the form
    altogether. It does not indicate that the user failed to provide a value
    for a required field. The ``MissingInputError`` above was caused by the
    fact that the form does have any input for the widget:

        >>> request.form[widget.name] #doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        KeyError: 'baz.foo'

    If a user fails to provide input for a field, the form will contain the
    input provided by the user, namely an empty string:

        >>> request.form[widget.name] = ''

    In such a case, if the field is required, a ``WidgetInputError`` will be
    raised on a call to `getInputValue`:

        >>> field.required = True
        >>> widget.getInputValue() #doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        WidgetInputError: ('foo', u'Foo', RequiredMissing('foo'))

    However, if the field is not required, the empty string will be converted
    by the widget into the field's `missing_value` and read as a legal field
    value:

        >>> field.required = False
        >>> widget.getInputValue() is field.missing_value
        True

    Another type of exception is a conversion error. It is raised when a value
    cannot be converted to the desired Python object. Here is an example of a
    floating point.

        >>> from zope.schema import Float
        >>> field = Float(__name__='price', title=u'Price')

        >>> from zope.formlib.interfaces import ConversionError
        >>> class FloatWidget(SimpleInputWidget):
        ...     def _toFieldValue(self, input):
        ...         try:
        ...             return float(input)
        ...         except ValueError as v:
        ...             raise ConversionError('Invalid floating point data', v)
        ...
        ...     def _toFormValue(self, value):
        ...         value = super(FloatWidget, self)._toFormValue(value)
        ...         return '%.2f' % value

        >>> request = TestRequest(form={'field.price': u'32.0'})
        >>> widget = FloatWidget(field, request)
        >>> widget.getInputValue()
        32.0
        >>> widget()
        u'<input class="textType" id="field.price" name="field.price" required="True" type="text" value="32.00"  />'

        >>> request = TestRequest(form={'field.price': u'<p>foo</p>'})
        >>> widget = FloatWidget(field, request)
        >>> try:
        ...     widget.getInputValue()
        ... except ConversionError as error:
        ...     print(error.doc())
        Invalid floating point data
        >>> widget()
        u'<input class="textType" id="field.price" name="field.price" required="True" type="text" value="&lt;p&gt;foo&lt;/p&gt;"  />'


    >>> tearDown()
    """

    tag = u'input'
    type = u'text'
    cssClass = u''
    extra = u''
    _missing = u''

    def hasInput(self):
        """See IWidget.hasInput.

        Returns ``True`` if the submitted request form contains a value for
        the widget, otherwise returns False.

        Some browser widgets may need to implement a more sophisticated test
        for input. E.g. checkbox values are not supplied in submitted
        forms when their value is 'off' -- in this case the widget will
        need to add a hidden element to signal its presence in the form.
        """
        return self.name in self.request.form

    def getInputValue(self):
        self._error = None
        field = self.context

        # form input is required, otherwise raise an error
        if not self.hasInput():
            raise MissingInputError(self.name, self.label, None)

        # convert input to suitable value - may raise conversion error
        try:
            value = self._toFieldValue(self._getFormInput())
        except ConversionError as error:
            # ConversionError is already a WidgetInputError
            self._error = error
            raise self._error

        # allow missing values only for non-required fields
        if value == field.missing_value and not field.required:
            return value

        # value must be valid per the field constraints
        try:
            field.validate(value)
        except ValidationError as v:
            self._error = WidgetInputError(
                self.context.__name__, self.label, v)
            raise self._error
        return value

    def _getFormInput(self):
        """Returns current form input.

        The value returned must be in a format that can be used as the 'input'
        argument to `_toFieldValue`.

        The default implementation returns the form value that corresponds to
        the widget's name. Subclasses may override this method if their form
        input consists of more than one form element or use an alternative
        naming convention.
        """
        return self.request.get(self.name)

    def _toFieldValue(self, input):
        """Converts input to a value appropriate for the field type.

        Widgets for non-string fields should override this method to
        perform an appropriate conversion.

        This method is used by getInputValue to perform the conversion
        of form input (provided by `_getFormInput`) to an appropriate field
        value.
        """
        if input == self._missing:
            return self.context.missing_value
        else:
            return input

    def _toFormValue(self, value):
        """Converts a field value to a string used as an HTML form value.

        This method is used in the default rendering of widgets that can
        represent their values in a single HTML form value. Widgets whose
        fields have more complex data structures should disregard this
        method and override the default rendering method (__call__).
        """
        if value == self.context.missing_value:
            return self._missing
        else:
            return value

    def _getCurrentValueHelper(self):
        """Helper to get the current input value.

        Raises InputErrors if the data could not be validated/converted.
        """
        input_value = None
        if self._renderedValueSet():
            input_value = self._data
        else:
            if self.hasInput():
                # It's insane to use getInputValue this way. It can
                # cause _error to get set spuriously.  We'll work
                # around this by saving and restoring _error if
                # necessary.
                error = self._error
                try:
                    input_value = self.getInputValue()
                finally:
                    self._error = error
            else:
                input_value = self._getDefault()
        return input_value

    def _getCurrentValue(self):
        """Returns the current input value.

        Returns None if the data could not be validated/converted.
        """
        try:
            input_value = self._getCurrentValueHelper()
        except InputErrors:
            input_value = None
        return input_value

    def _getFormValue(self):
        """Returns a value suitable for use in an HTML form.

        Detects the status of the widget and selects either the input value
        that came from the request, the value from the _data attribute or the
        default value.
        """
        try:
            input_value = self._getCurrentValueHelper()
        except InputErrors:
            form_value = self.request.form.get(self.name, self._missing)
        else:
            form_value = self._toFormValue(input_value)
        return form_value

    def _getDefault(self):
        """Returns the default value for this widget."""
        return self.context.default

    def __call__(self):
        return renderElement(self.tag,
                             type=self.type,
                             name=self.name,
                             id=self.name,
                             value=self._getFormValue(),
                             cssClass=self.cssClass,
                             required=self.required,
                             extra=self.extra)

    def hidden(self):
        return renderElement(self.tag,
                             type='hidden',
                             name=self.name,
                             id=self.name,
                             value=self._getFormValue(),
                             cssClass=self.cssClass,
                             extra=self.extra)

class DisplayWidget(BrowserWidget):

    def __init__(self, context, request):
        super(DisplayWidget, self).__init__(context, request)
        self.required = False


    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return ""
        return escape(value)


class UnicodeDisplayWidget(DisplayWidget):
    """Display widget that converts the value to unicode before display."""

    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return ""
        return escape(toUnicode(value))


def renderTag(tag, **kw):
    """Render the tag. Well, not all of it, as we may want to / it."""
    attr_list = []

    # special case handling for cssClass
    cssClass = kw.pop('cssClass', u'')

    # If the 'type' attribute is given, append this plus 'Type' as a
    # css class. This allows us to do subselector stuff in css without
    # necessarily having a browser that supports css subselectors.
    # This is important if you want to style radio inputs differently than
    # text inputs.
    cssWidgetType = kw.get('type', u'')
    if cssWidgetType:
        cssWidgetType += u'Type'
    names = [c for c in (cssClass, cssWidgetType) if c]
    if names:
        attr_list.append(u'class="%s"' % u' '.join(names))

    style = kw.pop('style', u'')
    if style:
        attr_list.append(u'style=%s' % quoteattr(style))

    # special case handling for extra 'raw' code
    if 'extra' in kw:
        # could be empty string but we don't care
        extra = u" " + kw.pop('extra')
    else:
        extra = u''

    # handle other attributes
    if kw:
        items = sorted(kw.items())
        for key, value in items:
            if value is None:
                warnings.warn(
                    "None was passed for attribute %r.  Passing None "
                    "as attribute values to renderTag is deprecated. "
                    "Passing None as an attribute value will be disallowed "
                    "starting in Zope 3.3."
                    % key,
                    DeprecationWarning, stacklevel=2)
                value = key
            attr_list.append(u'%s=%s' % (key, quoteattr(toUnicode(value))))

    if attr_list:
        attr_str = u" ".join(attr_list)
        return u"<%s %s%s" % (tag, attr_str, extra)
    else:
        return u"<%s%s" % (tag, extra)


def renderElement(tag, **kw):
    contents = kw.pop('contents', None)
    if contents is not None:
        # Do not quote contents, since it often contains generated HTML.
        return u"%s>%s</%s>" % (renderTag(tag, **kw), contents, tag)
    else:
        return renderTag(tag, **kw) + " />"


def setUp():
    import zope.component.testing
    global setUp
    setUp = zope.component.testing.setUp
    setUp()


def tearDown():
    import zope.component.testing
    global tearDown
    tearDown = zope.component.testing.tearDown
    tearDown()
