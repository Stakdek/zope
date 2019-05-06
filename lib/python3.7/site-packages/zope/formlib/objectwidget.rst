=============
Object Widget
=============

The following example shows a ``Family`` with ``Mother`` and ``Father``.
First define the interface for a person:

  >>> from zope.interface import Interface, implementer
  >>> from zope.schema import TextLine

  >>> class IPerson(Interface):
  ...     """Interface for Persons."""
  ...
  ...     name = TextLine(title=u'Name', description=u'The first name')

Let's define the class:

  >>> @implementer(IPerson)
  ... class Person(object):
  ...     def __init__(self, name=''):
  ...         self.name = name

Let's define the interface family:

  >>> from zope.schema import Object

  >>> class IFamily(Interface):
  ...     """The familiy interface."""
  ...
  ...     mother = Object(title=u'Mother',
  ...                     required=False,
  ...                     schema=IPerson)
  ...
  ...     father = Object(title=u'Father',
  ...                     required=False,
  ...                     schema=IPerson)

Let's define the class ``Family`` using
`zope.schema.fieldproperty.FieldProperty` for ``mother`` and ``father``.
``FieldProperty`` instances validate the values if they get added:

  >>> from zope.schema.fieldproperty import FieldProperty

  >>> @implementer(IFamily)
  ... class Family(object):
  ...     """The familiy interface."""
  ...     mother = FieldProperty(IFamily['mother'])
  ...     father = FieldProperty(IFamily['father'])
  ...
  ...     def __init__(self, mother=None, father=None):
  ...         self.mother = mother
  ...         self.father = father

Let's make an instance of Family with `None` attributes:

  >>> family = Family()
  >>> bool(family.mother == None)
  True

  >>> bool(family.father == None)
  True

Let's make an instance of Family with None attributes:

  >>> mother = Person(u'Margrith')
  >>> father = Person(u'Joe')
  >>> family = Family(mother, father)
  >>> IPerson.providedBy(family.mother)
  True

  >>> IPerson.providedBy(family.father)
  True

Let's define a dummy class which doesn't implements IPerson:

  >>> class Dummy(object):
  ...     """Dummy class."""
  ...     def __init__(self, name=''):
  ...         self.name = name

Raise a `zope.schema.interfaces.SchemaNotProvided` exception if we add a Dummy instance to a Family
object:

  >>> foo = Dummy('foo')
  >>> bar = Dummy('bar')
  >>> family = Family(foo, bar)
  ... # doctest: +IGNORE_EXCEPTION_DETAIL
  Traceback (most recent call last):
  ...
  SchemaNotProvided

Now let's setup a enviroment for use the widget like in a real application:


  >>> from zope.publisher.browser import TestRequest
  >>> from zope.schema.interfaces import ITextLine
  >>> from zope.schema import TextLine
  >>> from zope.formlib.widgets import TextWidget
  >>> from zope.formlib.widgets import ObjectWidget
  >>> from zope.formlib.interfaces import IInputWidget

Register the `zope.schema.TextLine` widget used in the IPerson interface for the field 'name'.

  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope.component import provideAdapter
  >>> provideAdapter(TextWidget, (ITextLine, IDefaultBrowserLayer),
  ...                IInputWidget)

Let's define a request and provide input value for the mothers name used
in the family object:

  >>> request = TestRequest(HTTP_ACCEPT_LANGUAGE='pl')
  >>> request.form['field.mother.name'] = u'Margrith Ineichen'

Before we update the object let's check the value name of the mother
instance on the family object:

  >>> family.mother.name
  u'Margrith'

Now let's initialize a `.ObjectWidget` with the right attributes:

  >>> mother_field = IFamily['mother']
  >>> factory = Person
  >>> widget = ObjectWidget(mother_field, request, factory)

Now comes the magic. Apply changes means we force the `.ObjectWidget` to read
the request, extract the value and save it on the content. The `.ObjectWidget`
instance uses a real Person class (factory) for add the value. The value is
temporary stored in this factory class. The `.ObjectWidget` reads the value from
this factory and set it to the attribute 'name' of the instance mother
(The object mother is already there). If we don't have an instance mother
already stored in the family object, the factory instance will be stored
directly to the family attribute mother. For more information see the method
`zope.formlib.objectwidget.ObjectWidget.applyChanges`.

  >>> widget.applyChanges(family)
  True

Test the updated mother's name value on the object family:

  >>> family.mother.name
  u'Margrith Ineichen'

  >>> IPerson.providedBy(family.mother)
  True

So, now you know my mothers and fathers name. I hope it's also clear how to
use the `zope.schema.Object` field and the `.ObjectWidget`.
