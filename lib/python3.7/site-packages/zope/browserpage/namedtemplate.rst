===============
Named Templates
===============

We often want to be able to define view logic and view templates
independently.  We'd like to be able to change the template used by a
form without being forced to modify the form.

Named templates provide templates that are registered as named view
adapters.   To define a named template, use the `NamedTemplateImplementation`
constructor:

    >>> from zope.browserpage import ViewPageTemplateFile
    >>> from zope.browserpage.namedtemplate import (
    ...     NamedTemplateImplementation)
    >>> sample = ViewPageTemplateFile('tests/namedtemplate.pt')
    >>> sample = NamedTemplateImplementation(sample)

Let's define a view that uses the named template.  To use a named
template, use the NamedTemplate constructor, and give a template name:

    >>> from zope.browserpage.namedtemplate import NamedTemplate
    >>> class MyView:
    ...     def __init__(self, context, request):
    ...         self.context = context
    ...         self.request = request
    ...
    ...     __call__ = NamedTemplate('sample')

Normally, we'd register a named template for a view interface, to
allow it to be registered for multiple views.  We'll just register it
for our view class.

    >>> from zope import component
    >>> component.provideAdapter(sample, [MyView], name='sample')

Now, with this in place, we should be able to use our view:

    >>> class MyContent:
    ...     def __init__(self, name):
    ...         self.name = name

    >>> from zope.publisher.browser import TestRequest
    >>> view = MyView(MyContent('bob'), TestRequest())
    >>> print(view(x=42).replace('\r\n', '\n'))
    <html><body>
    Hello bob
    The URL is http://127.0.0.1
    The positional arguments were ()
    The keyword argument x is 42
    </body></html>
    <BLANKLINE>

The view type that a named template is to be used for can be supplied
when the named template is created:

    >>> class MyView:
    ...     def __init__(self, context, request):
    ...         self.context = context
    ...         self.request = request
    ...
    ...     __call__ = NamedTemplate('sample2')

    >>> sample = ViewPageTemplateFile('tests/namedtemplate.pt')
    >>> sample = NamedTemplateImplementation(sample, MyView)
    >>> component.provideAdapter(sample, name='sample2')
    >>> view = MyView(MyContent('bob'), TestRequest())
    >>> print(view(x=42).replace('\r\n', '\n'))
    <html><body>
    Hello bob
    The URL is http://127.0.0.1
    The positional arguments were ()
    The keyword argument x is 42
    </body></html>
    <BLANKLINE>
