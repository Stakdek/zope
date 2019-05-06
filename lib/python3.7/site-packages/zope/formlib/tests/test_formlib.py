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
from __future__ import print_function
import unittest
import re
import pytz

from zope.component.testing import setUp, tearDown
from zope.component import adapter
from zope.component import provideAdapter, provideUtility

from zope.i18n.testing import setUp as i18nSetUp
import zope.interface.common.idatetime
import zope.publisher.interfaces
import zope.publisher.interfaces.browser
import zope.schema.interfaces
import zope.testing.renormalizing
import zope.traversing.adapters

from zope.formlib.widgets import (
    TextWidget, FloatWidget, UnicodeDisplayWidget, IntWidget,
    DatetimeDisplayWidget, DatetimeWidget)

from zope.formlib import exception
from zope.formlib.interfaces import IWidgetInputErrorView

import zope.formlib
import zope.formlib.form
import zope.formlib.interfaces
from zope.formlib.tests import support
from zope.browserpage.namedtemplate import NamedTemplateImplementation

from zope.configuration.xmlconfig import XMLConfig

@zope.interface.implementer(zope.interface.common.idatetime.ITZInfo)
@adapter(zope.publisher.interfaces.IRequest)
def requestToTZInfo(request):
    return pytz.timezone('US/Hawaii')

def pageSetUp(test):
    setUp(test)
    provideAdapter(
        zope.traversing.adapters.DefaultTraversable,
        [None],
        )

@adapter(zope.formlib.interfaces.IForm)
@NamedTemplateImplementation
def TestTemplate(self):
    # This "template" overrides the default page templates that is
    # registered for forms.
    status = self.status
    if status:
        status = zope.i18n.translate(status,
                                     context=self.request,
                                     default=self.status)
        if getattr(status, 'mapping', 0):
            status = zope.i18n.interpolate(status, status.mapping)
        print(status)

    result = []

    if self.errors:
        for error in self.errors:
            result.append("%s: %s" % (error.__class__.__name__, error))

    for w in self.widgets:
        result.append(w())
        error = w.error()
        if error:
            result.append(str(error))

    if self.protected:
        result.append(
            '<inut type="hidden" '
            'name="__csrftoken__" '
            'value="%s"' % self.csrftoken)

    for action in self.availableActions():
        result.append(action.render())

    return '\n'.join(result)

def formSetUp(test):
    setUp(test)
    i18nSetUp(test)
    provideAdapter(
        TextWidget,
        [zope.schema.interfaces.ITextLine,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.formlib.interfaces.IInputWidget,
        )
    provideAdapter(
        FloatWidget,
        [zope.schema.interfaces.IFloat,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.formlib.interfaces.IInputWidget,
        )
    provideAdapter(
        UnicodeDisplayWidget,
        [zope.schema.interfaces.IInt,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.formlib.interfaces.IDisplayWidget,
        )
    provideAdapter(
        IntWidget,
        [zope.schema.interfaces.IInt,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.formlib.interfaces.IInputWidget,
        )
    provideAdapter(
        UnicodeDisplayWidget,
        [zope.schema.interfaces.IFloat,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.formlib.interfaces.IDisplayWidget,
        )
    provideAdapter(
        UnicodeDisplayWidget,
        [zope.schema.interfaces.ITextLine,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.formlib.interfaces.IDisplayWidget,
        )
    provideAdapter(
        DatetimeDisplayWidget,
        [zope.schema.interfaces.IDatetime,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.formlib.interfaces.IDisplayWidget,
        )
    provideAdapter(
        DatetimeWidget,
        [zope.schema.interfaces.IDatetime,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.formlib.interfaces.IInputWidget,
        )
    provideAdapter(
        exception.WidgetInputErrorView,
        [zope.formlib.interfaces.IWidgetInputError,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        IWidgetInputErrorView,
        )
    provideAdapter(
        zope.formlib.errors.InvalidErrorView,
        [zope.interface.Invalid,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        IWidgetInputErrorView,
        )
    provideAdapter(TestTemplate, name='default')
    provideAdapter(requestToTZInfo)
    provideAdapter(
        zope.formlib.form.render_submit_button, name='render')

    XMLConfig('ftesting.zcml', zope.formlib)
    test.globs['print_function'] = print_function

# Classes used in tests

class IOrder(zope.interface.Interface):
    identifier = zope.schema.Int(title=u"Identifier", readonly=True)
    name = zope.schema.TextLine(title=u"Name")
    min_size = zope.schema.Float(title=u"Minimum size")
    max_size = zope.schema.Float(title=u"Maximum size")
    now = zope.schema.Datetime(title=u"Now", readonly=True)

class IDescriptive(zope.interface.Interface):
    title = zope.schema.TextLine(title=u"Title")
    description = zope.schema.TextLine(title=u"Description")


@zope.interface.implementer(IOrder)
class Order:
    identifier = 1
    name = 'unknown'
    min_size = 1.0
    max_size = 10.0


@adapter(IOrder)
@zope.interface.implementer(IDescriptive)
class Descriptive(object):
    def __init__(self, context):
        self.context = context

    def title():
        def get(self):
            try:
                return self.context.__title
            except AttributeError:
                return ''
        def set(self, v):
            self.context.__title = v
        return property(get, set)
    title = title()

    def description():
        def get(self):
            try:
                return self.context.__description
            except AttributeError:
                return ''
        def set(self, v):
            self.context.__description = v
        return property(get, set)
    description = description()


def makeSureRenderCanBeCalledWithoutCallingUpdate():
    """\

    >>> class MyForm(zope.formlib.form.EditForm):
    ...     form_fields = zope.formlib.form.fields(
    ...         IOrder, keep_readonly=['identifier'])

    >>> from zope.publisher.browser import TestRequest
    >>> myform = MyForm(Order(), TestRequest())
    >>> print(myform.render()) # doctest: +NORMALIZE_WHITESPACE
    1
    <input class="textType" id="form.name" name="form.name"
           size="20" type="text" value="unknown"  />
    <input class="textType" id="form.min_size" name="form.min_size"
           size="10" type="text" value="1.0"  />
    <input class="textType" id="form.max_size" name="form.max_size"
           size="10" type="text" value="10.0"  />
    <input type="submit" id="form.actions.apply" name="form.actions.apply"
           value="Apply" class="button" />

"""

def make_sure_i18n_is_called_correctly_for_actions():
    """\

We want to make sure that i18n is called correctly.  This is in
response to a bug that occurred because actions called i18n.translate
with incorrect positional arguments.

We'll start by setting up an action:

    >>> import zope.i18nmessageid
    >>> _ = zope.i18nmessageid.MessageFactory('my.domain')
    >>> action = zope.formlib.form.Action(_("MyAction"))

Actions get bound to forms.  We'll set up a test request, create a
form for it and bind the action to the form:

    >>> myform = zope.formlib.form.FormBase(None, 42)
    >>> action = action.__get__(myform)

Button labels are rendered by form.render_submit_button, passing the
bound action.  Before we call this however, we need to set up a dummy
translation domain.  We'll create one for our needs:

    >>> import zope.i18n.interfaces
    >>> @zope.interface.implementer(zope.i18n.interfaces.ITranslationDomain)
    ... class MyDomain:
    ...
    ...     def translate(self, msgid, mapping=None, context=None,
    ...                   target_language=None, default=None,
    ...                   msgid_plural=None, default_plural=None, number=None):
    ...         print(msgid)
    ...         print(mapping)
    ...         print(context)
    ...         print(target_language)
    ...         print(default)
    ...         return msgid

    >>> provideUtility(MyDomain(), name='my.domain')

Now, if we call render_submit_button, we should be able to verify the
data passed to translate:

    >>> print(zope.formlib.form.render_submit_button(action)())
    ...     # doctest: +NORMALIZE_WHITESPACE
    MyAction
    None
    42
    None
    MyAction
    <input type="submit" id="form.actions.myaction"
       name="form.actions.myaction" value="MyAction" class="button" />


"""

def test_error_handling():
    """\

Let's test the getWidgetsData method which is responsible for handling widget
erros raised by the widgets getInputValue method.

    >>> import zope.formlib.interfaces
    >>> @zope.interface.implementer(zope.formlib.interfaces.IInputWidget)
    ... class Widget(object):
    ...     def __init__(self):
    ...         self.name = 'form.summary'
    ...         self.label = 'Summary'
    ...     def hasInput(self):
    ...         return True
    ...     def getInputValue(self):
    ...         raise zope.formlib.interfaces.WidgetInputError(
    ...         field_name='summary',
    ...         widget_title=u'Summary')
    >>> widget = Widget()
    >>> inputs = [(True, widget)]
    >>> widgets = zope.formlib.form.Widgets(inputs, 5)
    >>> errors = zope.formlib.form.getWidgetsData(
    ...     widgets, 'form', {'summary':'value'})
    >>> print(errors[0].__class__.__name__, errors[0])
    WidgetInputError ('summary', 'Summary', None)

Let's see what happens if a widget doesn't convert a ValidationError
raised by a field to a WidgetInputError. This should not happen if a widget
converts ValidationErrors to WidgetInputErrors. But since I just fixed
yesterday the sequence input widget, I decided to catch ValidationError also
in the formlib as a fallback if some widget doen't handle errors correct. (ri)

    >>> @zope.interface.implementer(zope.formlib.interfaces.IInputWidget)
    ... class Widget(object):
    ...     def __init__(self):
    ...         self.name = 'form.summary'
    ...         self.label = 'summary'
    ...     def hasInput(self):
    ...         return True
    ...     def getInputValue(self):
    ...         raise zope.schema.interfaces.ValidationError('A error message')
    >>> widget = Widget()
    >>> inputs = [(True, widget)]
    >>> widgets = zope.formlib.form.Widgets(inputs, 5)
    >>> errors = zope.formlib.form.getWidgetsData(widgets, 'form', {'summary':'value'})
    >>> errors #doctest: +ELLIPSIS
    [<zope.formlib.interfaces.WidgetInputError instance at ...>]

"""

def test_form_template_i18n():
    """\
Let's try to check that the formlib templates handle i18n correctly.
We'll define a simple form:

    >>> from zope.browserpage import ViewPageTemplateFile
    >>> import zope.i18nmessageid
    >>> _ = zope.i18nmessageid.MessageFactory('my.domain')

    >>> class MyForm(zope.formlib.form.Form):
    ...     label = _('The label')
    ...     status = _('Success!')
    ...     form_fields = zope.formlib.form.Fields(
    ...         zope.schema.TextLine(__name__='name',
    ...                              title=_("Name"),
    ...                              description=_("Enter your name"),
    ...                             ),
    ...         )
    ...     @zope.formlib.form.action(_('Ok'))
    ...     def ok(self, action, data):
    ...         pass
    ...     page = ViewPageTemplateFile("../pageform.pt")
    ...     subpage = ViewPageTemplateFile("../subpageform.pt")

Now, we should be able to create a form instance:

    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> form = MyForm(object(), request)

Unfortunately, the "page" template uses a page macro. We need to
provide a template that it can get one from.  Here, we'll set up a
view that provides the necessary macros:

    >>> from zope.pagetemplate.pagetemplate import PageTemplate
    >>> macro_template = PageTemplate()
    >>> macro_template.write('''\
    ... <html metal:define-macro="view">
    ... <body metal:define-slot="body" />
    ... </html>
    ... ''')

We also need to provide a traversal adapter for the view namespace
that lets us look up the macros.

    >>> import zope.traversing.interfaces
    >>> @adapter(None, None)
    ... @zope.interface.implementer(zope.traversing.interfaces.ITraversable)
    ... class view:
    ...     def __init__(self, ob, r=None):
    ...         pass
    ...     def traverse(*args):
    ...         return macro_template.macros

    >>> provideAdapter(view, name='view')

And we have to register the default traversable adapter (I wish we had
push templates):

    >>> from zope.traversing.adapters import DefaultTraversable
    >>> provideAdapter(DefaultTraversable, [None])

We need to set up the translation framework. We'll just provide a
negotiator that always decides to use the test language:

    >>> import zope.i18n.interfaces
    >>> @zope.interface.implementer(zope.i18n.interfaces.INegotiator)
    ... class Negotiator:
    ...     def getLanguage(*ignored):
    ...         return 'test'

    >>> provideUtility(Negotiator())

And we'll set up the fallback-domain factory, which provides the test
language for all domains:

    >>> from zope.i18n.testmessagecatalog import TestMessageFallbackDomain
    >>> provideUtility(TestMessageFallbackDomain)

OK, so let's see what the page form looks like. First, we'll compute
the page:

    >>> form.update()
    >>> page = form.page()

We want to make sure that the page has the translations we expect and
that it doesn't double translate anything.  We'll write a generator
that extracts the translations, complaining if any are nested:

    >>> def find_translations(text):
    ...     l = 0
    ...     while 1:
    ...         lopen = text.find('[[', l)
    ...         lclose = text.find(']]', l)
    ...         if lclose >= 0 and lclose < lopen:
    ...             raise ValueError(lopen, lclose, text)
    ...         if lopen < 0:
    ...             break
    ...         l = lopen + 2
    ...         lopen = text.find('[[', l)
    ...         lclose = text.find(']]', l)
    ...         if lopen >= 0 and lopen < lclose:
    ...             raise ValueError(lopen, lclose, text)
    ...         if lclose < 0:
    ...             raise ValueError(l, text)
    ...         yield text[l-2:lclose+2]
    ...         l = lclose + 2

    >>> for t in find_translations(page):
    ...     print(t)
    [[my.domain][The label]]
    [[my.domain][Success!]]
    [[my.domain][Name]]
    [[my.domain][Enter your name]]
    [[my.domain][Ok]]

Now, let's try the same thing with the sub-page form:

    >>> for t in find_translations(form.subpage()):
    ...     print(t)
    [[my.domain][The label]]
    [[my.domain][Success!]]
    [[my.domain][Name]]
    [[my.domain][Enter your name]]
    [[my.domain][Ok]]

"""


def test_setUpWidgets_prefix():
    """This is a regression test for field prefix handling in setUp*Widgets.

    Let's set up fields with some interface and a prefix on fields:

        >>> from zope.formlib import form
        >>> from zope import interface, schema

        >>> class ITrivial(interface.Interface):
        ...     name = schema.TextLine(title=u"Name")

        >>> form_fields = form.Fields(ITrivial, prefix='one')
        >>> form_fields += form.Fields(ITrivial, prefix='two')
        >>> form_fields += form.Fields(ITrivial, prefix='three')

    Let's call setUpDataWidgets and see their names:

        >>> @interface.implementer(ITrivial)
        ... class Trivial(object):
        ...     name = 'foo'
        >>> context = Trivial()

        >>> from zope.publisher.browser import TestRequest
        >>> request = TestRequest()

        >>> widgets = form.setUpDataWidgets(form_fields, 'form', context,
        ...                                 request, {})
        >>> [w.name for w in widgets]
        ['form.one.name', 'form.two.name', 'form.three.name']

    Let's try the same with setUpEditWidgets:

        >>> widgets = form.setUpEditWidgets(form_fields, 'form', context,
        ...                                  request)
        >>> [w.name for w in widgets]
        ['form.one.name', 'form.two.name', 'form.three.name']

    And setUpInputWidgets:

        >>> widgets = form.setUpInputWidgets(form_fields, 'form', context,
        ...                                  request)
        >>> [w.name for w in widgets]
        ['form.one.name', 'form.two.name', 'form.three.name']

    And setUpWidgets:

        >>> widgets = form.setUpWidgets(form_fields, 'form', context, request)
        >>> [w.name for w in widgets]
        ['form.one.name', 'form.two.name', 'form.three.name']

    """

def check_action_name():
    """
We want to make sure that Action name setting adheres to the specification.

With just label, with increasing complexity:

    >>> action = zope.formlib.form.Action("MyAction")
    >>> action.name
    'myaction'

    >>> action = zope.formlib.form.Action("8 Balls")
    >>> action.name
    '382042616c6c73'

    >>> action = zope.formlib.form.Action(u"MyAction")
    >>> action.name
    u'myaction'

    >>> action = zope.formlib.form.Action(u"8 Balls")
    >>> action.name
    '382042616c6c73'

    >>> action = zope.formlib.form.Action(u'\u9001\u4fe1')
    >>> action.name
    'e98081e4bfa1'

    >>> import zope.i18nmessageid
    >>> _ = zope.i18nmessageid.MessageFactory('my.domain')

    >>> action = zope.formlib.form.Action(_(u"MyAction"))
    >>> action.name
    u'myaction'

    >>> action = zope.formlib.form.Action(_(u"8 Balls"))
    >>> action.name
    '382042616c6c73'

    >>> action = zope.formlib.form.Action(_(u'\u9001\u4fe1'))
    >>> action.name
    'e98081e4bfa1'

With all lowercase name:

    >>> action = zope.formlib.form.Action("MyAction", name='foobar')
    >>> action.name
    'foobar'

    >>> action = zope.formlib.form.Action("8 Balls", name='foobar')
    >>> action.name
    'foobar'

    >>> action = zope.formlib.form.Action(u"MyAction", name='foobar')
    >>> action.name
    'foobar'

    >>> action = zope.formlib.form.Action(u"8 Balls", name='foobar')
    >>> action.name
    'foobar'

    >>> action = zope.formlib.form.Action(u'\u9001\u4fe1', name='foobar')
    >>> action.name
    'foobar'

    >>> action = zope.formlib.form.Action(_(u"MyAction"), name='foobar')
    >>> action.name
    'foobar'

    >>> action = zope.formlib.form.Action(_(u"8 Balls"), name='foobar')
    >>> action.name
    'foobar'

    >>> action = zope.formlib.form.Action(_(u'\u9001\u4fe1'), name='foobar')
    >>> action.name
    'foobar'

With some uppercase name:

    >>> action = zope.formlib.form.Action("MyAction", name='FooBar')
    >>> action.name
    'FooBar'

    >>> action = zope.formlib.form.Action("8 Balls", name='FooBar')
    >>> action.name
    'FooBar'

    >>> action = zope.formlib.form.Action(u"MyAction", name='FooBar')
    >>> action.name
    'FooBar'

    >>> action = zope.formlib.form.Action(u"8 Balls", name='FooBar')
    >>> action.name
    'FooBar'

    >>> action = zope.formlib.form.Action(u'\u9001\u4fe1', name='FooBar')
    >>> action.name
    'FooBar'

    >>> action = zope.formlib.form.Action(_(u"MyAction"), name='FooBar')
    >>> action.name
    'FooBar'

    >>> action = zope.formlib.form.Action(_(u"8 Balls"), name='FooBar')
    >>> action.name
    'FooBar'

    >>> action = zope.formlib.form.Action(_(u'\u9001\u4fe1'), name='FooBar')
    >>> action.name
    'FooBar'

"""


def validate_respects_ignoreContext_setting_on_form_when_checking_invariants():
    """
The `validate` method of the form respects the value of
``self.ignoreContext`` when calling `checkInvariants`. `checkInvariants` is
able to access the values from the form and the context (if not ignored) to
make sure invariants are not violated:

    >>> class IFlexMaximum(zope.interface.Interface):
    ...     max = zope.schema.Int(title=u"Maximum")
    ...     value = zope.schema.Int(title=u"Value")
    ...
    ...     @zope.interface.invariant
    ...     def value_not_bigger_than_max(data):
    ...         if data.value > data.max:
    ...             raise zope.interface.Invalid('value bigger than max')

    >>> @zope.interface.implementer(IFlexMaximum)
    ... class Content(object):
    ...     max = 10
    ...     value = 7

    >>> class ValueForm(zope.formlib.form.FormBase):
    ...     ignoreContext = False
    ...     form_fields = zope.formlib.form.FormFields(
    ...         IFlexMaximum).omit('max')
    ...
    ...     @zope.formlib.form.action("Apply")
    ...     def handle_apply(self, action, data):
    ...         pass

`checkInvariants` is able to access the value on the context, so the
interface invariant triggers an error message:

    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest(
    ...     form={'form.value': 42, 'form.actions.apply': '1'})
    >>> form = ValueForm(Content(), request)
    >>> form.update()
    >>> form.errors
    (Invalid('value bigger than max',),)

`checkInvariants` if the entered value is small enough, the error message is
not triggered:

    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest(
    ...     form={'form.value': 8, 'form.actions.apply': '1'})
    >>> form = ValueForm(Content(), request)
    >>> form.update()
    >>> form.errors
    ()

The error is not triggered, too,  if ``ignoreContext`` is set to ``True`` as
`checkInvariants` does not access the context then:

    >>> request = TestRequest(
    ...     form={'form.value': 42, 'form.actions.apply': '1'})
    >>> form = ValueForm(Content(), request)
    >>> form.ignoreContext = True
    >>> form.update()
    >>> form.errors
    ()
"""



def FormData___getattr___handles_zope_interrface_attributes_correctly():
    """
`FormData.__getattr__` reads objects defined as zope.interface.Attribute in
interface correctly from context:

    >>> class IStaticMaximum(zope.interface.Interface):
    ...     max = zope.interface.Attribute("Predefined maximum")

    >>> @zope.interface.implementer(IStaticMaximum)
    ... class Content(object):
    ...     max = 10

    >>> formdata = zope.formlib.form.FormData(IStaticMaximum, {}, Content())
    >>> formdata.max
    10
"""


def FormData___getattr___raises_NoInputData_if_unknown_how_to_access_value():
    """
`FormData.__getattr__` raises an exception if it cannot determine how to
read the object from context:

    >>> class IStaticMaximum(zope.interface.Interface):
    ...     def max(): pass

    >>> @zope.interface.implementer(IStaticMaximum)
    ... class Content(object):
    ...     pass

    >>> formdata = zope.formlib.form.FormData(IStaticMaximum, {}, Content())
    >>> formdata.max #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    NoInputData: max
"""


def test_suite():
    import doctest
    checker = support.checker + zope.testing.renormalizing.RENormalizing([
      (re.compile(r"\[WidgetInputError\('form.summary', 'summary', ValidationError\('A error message'\)\)\]"),
                  r"[<zope.formlib.interfaces.WidgetInputError instance at ...>]"),
      (re.compile(r"\[WidgetInputError\('summary', u'Summary', None\)\]"),
                  r"[<zope.formlib.interfaces.WidgetInputError instance at ...>]"),
      (re.compile(r" ValueError\('invalid literal for float\(\): (bob'|10/0'),\)"),
                  r"\n <exceptions.ValueError instance at ...>"),
      (re.compile(r" ValueError\('could not convert string to float: bob',\)"),
                  r"\n <exceptions.ValueError instance at ...>"),
      (re.compile(r"\(Invalid\('value bigger than max',\),\)"),
       r"(Invalid('value bigger than max'),)"),
    ])
    return unittest.TestSuite((
        doctest.DocFileSuite(
            '../errors.rst',
            setUp=formSetUp, tearDown=tearDown, checker=checker,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        # The following test needs some zope.security test setup
        #doctest.DocFileSuite(
        #     'bugs.txt',
        #     setUp=formSetUp, tearDown=tearDown,
        #     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        #     ),
        doctest.DocFileSuite(
            '../form.rst',
            setUp=formSetUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker
            ),
        doctest.DocTestSuite(
            setUp=formSetUp, tearDown=tearDown,
            checker=checker
            ),
        doctest.DocTestSuite(
            'zope.formlib.errors', checker=checker),
        ))
