"""Support code for functional widget tests.
"""

from zope.browserpage.namedtemplate import NamedTemplateImplementation
from zope.component import adapter
from zope.component import provideAdapter
from zope.component.testing import setUp, tearDown
from zope.formlib import form
from zope.formlib.errors import InvalidErrorView
from zope.formlib.exception import WidgetInputErrorView
from zope.formlib.interfaces import (
    IInputWidget, IForm,
    IWidgetInputError, IWidgetInputErrorView)
from zope.formlib.tests.test_formlib import requestToTZInfo
from zope.i18n.testing import setUp as i18nSetUp
from zope.interface import Invalid
from zope.publisher.interfaces.browser import IBrowserRequest
import unittest
import zope.i18n
import zope.schema.interfaces

@adapter(IForm)
@NamedTemplateImplementation
def TestTemplate(self):
    status = self.status
    if status:
        status = zope.i18n.translate(status,
                                     context=self.request,
                                     default=self.status)
        if getattr(status, 'mapping', 0):
            status = zope.i18n.interpolate(status, status.mapping)

    result = []

    for w in self.widgets:
        result.append(w())
        error = w.error()
        if error:
            result.append(str(error))

    for action in self.availableActions():
        result.append(action.render())

    return '\n'.join(result)

def formSetUp(test):
    setUp(test)
    i18nSetUp(test)

    for field, widget in test.widgets:
        if isinstance(field, tuple):
            field = field + (IBrowserRequest,)
        else:
            field = (field, IBrowserRequest)
        provideAdapter(
            widget,
            field,
            IInputWidget)
        
    provideAdapter(
       WidgetInputErrorView,
        (IWidgetInputError,
         IBrowserRequest),
        IWidgetInputErrorView,
        )
    provideAdapter(
        InvalidErrorView,
        (Invalid,
         IBrowserRequest),
        IWidgetInputErrorView,
        )

    provideAdapter(TestTemplate, name='default')
    provideAdapter(requestToTZInfo)
    provideAdapter(
        form.render_submit_button, name='render')

class FunctionalWidgetTestCase(unittest.TestCase):
    widgets = []
    
    def setUp(self):
        formSetUp(self)

    def tearDown(self):
        tearDown(self)


