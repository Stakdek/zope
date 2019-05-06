=============
Browser Menus
=============

Browser menus are used to categorize browser actions, such as the views of a
content component or the addable components of a container. In essence they
provide the same functionality as menu bars in desktop application.

  >>> from zope.browsermenu import menu, metaconfigure

Menus are simple components that have an id, title and description. They also
must provide a method called ``getMenuItems(object, request)`` that returns a
TAL-friendly list of information dictionaries. We will see this in detail
later. The default menu implementation, however, makes the menu be very
transparent by identifying the menu through an interface. So let's define and
register a simple edit menu:

  >>> import zope.interface
  >>> class EditMenu(zope.interface.Interface):
  ...     """This is an edit menu."""

  >>> from zope.browsermenu.interfaces import IMenuItemType
  >>> zope.interface.directlyProvides(EditMenu, IMenuItemType)

  >>> from zope.component import provideUtility
  >>> provideUtility(EditMenu, IMenuItemType, 'edit')

Now we have to create and register the menu itself:

  >>> from zope.browsermenu.interfaces import IBrowserMenu
  >>> provideUtility(
  ...     menu.BrowserMenu('edit', 'Edit', 'Edit Menu'), IBrowserMenu, 'edit')

Note that these steps seem like a lot of boilerplate, but all this work is
commonly done for you via ZCML. An item in a menu is simply an adapter that
provides. In the following section we will have a closer look at the browser
menu item:

``BrowserMenuItem`` class
-------------------------

The browser menu item represents an entry in the menu. Essentially, the menu
item is a browser view of a content component. Thus we have to create a
content component first:

  >>> class IContent(zope.interface.Interface):
  ...     pass

  >>> from zope.publisher.interfaces.browser import IBrowserPublisher
  >>> from zope.security.interfaces import Unauthorized, Forbidden

  >>> @zope.interface.implementer(IContent, IBrowserPublisher)
  ... class Content(object):
  ...
  ...     def foo(self):
  ...         pass
  ...
  ...     def browserDefault(self, r):
  ...         return self, ()
  ...
  ...     def publishTraverse(self, request, name):
  ...         if name.startswith('fb'):
  ...             raise Forbidden(name)
  ...         if name.startswith('ua'):
  ...             raise Unauthorized(name)
  ...         if name.startswith('le'):
  ...             raise LookupError(name)
  ...         return self.foo

We also implemented the ``IBrowserPublisher`` interface, because we want to
make the object traversable, so that we can make availability checks later.

Since the ``BrowserMenuItem`` is just a view, we can initiate it with an
object and a request.

  >>> from zope.publisher.browser import TestRequest
  >>> item = menu.BrowserMenuItem(Content(), TestRequest())

Note that the menu item knows *nothing* about the menu itself. It purely
depends on the adapter registration to determine in which menu it will
appear. The advantage is that a menu item can be reused in several menus.

Now we add a title, description, order and icon and see whether we can then
access the value. Note that these assignments are always automatically done by
the framework.

  >>> item.title = 'Item 1'
  >>> item.title
  'Item 1'

  >>> item.description = 'This is Item 1.'
  >>> item.description
  'This is Item 1.'

  >>> item.order
  0
  >>> item.order = 1
  >>> item.order
  1

  >>> item.icon is None
  True
  >>> item.icon = '/@@/icon.png'
  >>> item.icon
  '/@@/icon.png'

Since there is no permission or view specified yet, the menu item should
be available and not selected.

  >>> item.available()
  True
  >>> item.selected()
  False

There are two ways to deny availability of a menu item: (1) the current
user does not have the correct permission to access the action or the menu
item itself, or (2) the filter returns ``False``, in which case the menu
item should also not be shown.

  >>> from zope.security.interfaces import IPermission
  >>> from zope.security.permission import Permission
  >>> perm = Permission('perm', 'Permission')
  >>> provideUtility(perm, IPermission, 'perm')

  >>> class ParticipationStub(object):
  ...     principal = 'principal'
  ...     interaction = None


In the first case, the permission of the menu item was explicitly
specified. Make sure that the user needs this permission to make the menu
item available.

  >>> item.permission = perm

Now, we are not setting any user. This means that the menu item should be
available.

  >>> from zope.security.management import newInteraction, endInteraction
  >>> endInteraction()
  >>> newInteraction()
  >>> item.available()
  True

Now we specify a principal that does not have the specified permission.

  >>> endInteraction()
  >>> newInteraction(ParticipationStub())
  >>> item.available()
  False

In the second case, the permission is not explicitly defined and the
availability is determined by the permission required to access the
action.

  >>> item.permission = None

All views starting with 'fb' are forbidden, the ones with 'ua' are
unauthorized and all others are allowed.

  >>> item.action = 'fb'
  >>> item.available()
  False
  >>> item.action = 'ua'
  >>> item.available()
  False
  >>> item.action = 'a'
  >>> item.available()
  True

Also, sometimes a menu item might be registered for a view that does not
exist. In those cases the traversal mechanism raises a ``TraversalError``, which
is a special type of ``LookupError``. All actions starting with 'le' should
raise this error:

  >>> item.action = 'le'
  >>> item.available()
  False

Now let's test filtering. If the filter is specified, it is assumed to be
a TALES object.

  >>> from zope.pagetemplate.engine import Engine
  >>> item.action = 'a'
  >>> item.filter = Engine.compile('not:context')
  >>> item.available()
  False
  >>> item.filter = Engine.compile('context')
  >>> item.available()
  True

Finally, make sure that the menu item can be selected.

  >>> item.request = TestRequest(SERVER_URL='http://127.0.0.1/@@view.html',
  ...                            PATH_INFO='/@@view.html')

  >>> item.selected()
  False
  >>> item.action = 'view.html'
  >>> item.selected()
  True
  >>> item.action = '@@view.html'
  >>> item.selected()
  True
  >>> item.request = TestRequest(
  ...     SERVER_URL='http://127.0.0.1/++view++view.html',
  ...     PATH_INFO='/++view++view.html')
  >>> item.selected()
  True
  >>> item.action = 'otherview.html'
  >>> item.selected()
  False


``BrowserSubMenuItem`` class
----------------------------

The menu framework also allows for submenus. Submenus can be inserted by
creating a special menu item that simply points to another menu to be
inserted:

  >>> item = menu.BrowserSubMenuItem(Content(), TestRequest())

The framework will always set the sub-menu automatically (we do it
manually here):

  >>> class SaveOptions(zope.interface.Interface):
  ...     "A sub-menu that describes available save options for the content."

  >>> zope.interface.directlyProvides(SaveOptions, IMenuItemType)

  >>> provideUtility(SaveOptions, IMenuItemType, 'save')
  >>> provideUtility(menu.BrowserMenu('save', 'Save', 'Save Menu'),
  ...                IBrowserMenu, 'save')

Now we can assign the sub-menu id to the menu item:

  >>> item.submenuId = 'save'

Also, the ``action`` attribute for the browser sub-menu item is optional,
because you often do not want the item itself to represent something. The rest
of the class is identical to the ``BrowserMenuItem`` class.


Getting a Menu
--------------

Now that we know how the single menu item works, let's have a look at how menu
items get put together to a menu. But let's first create some menu items and
register them as adapters with the component architecture.

Register the edit menu entries first. We use the menu item factory to create
the items:

  >>> from zope.component import provideAdapter
  >>> from zope.publisher.interfaces.browser import IBrowserRequest

  >>> undo = metaconfigure.MenuItemFactory(menu.BrowserMenuItem, title="Undo",
  ...                                 action="undo.html")
  >>> provideAdapter(undo, (IContent, IBrowserRequest), EditMenu, 'undo')

  >>> redo = metaconfigure.MenuItemFactory(menu.BrowserMenuItem, title="Redo",
  ...                                 action="redo.html", icon="/@@/redo.png")
  >>> provideAdapter(redo, (IContent, IBrowserRequest), EditMenu, 'redo')

  >>> save = metaconfigure.MenuItemFactory(menu.BrowserSubMenuItem, title="Save",
  ...                                 submenuId='save', order=2)
  >>> provideAdapter(save, (IContent, IBrowserRequest), EditMenu, 'save')

And now the save options:

  >>> saveas = metaconfigure.MenuItemFactory(menu.BrowserMenuItem, title="Save as",
  ...                                   action="saveas.html")
  >>> provideAdapter(saveas, (IContent, IBrowserRequest),
  ...                SaveOptions, 'saveas')

  >>> saveall = metaconfigure.MenuItemFactory(menu.BrowserMenuItem, title="Save all",
  ...                                    action="saveall.html")
  >>> provideAdapter(saveall, (IContent, IBrowserRequest),
  ...                SaveOptions, 'saveall')

Note that we can also register menu items for classes:


  >>> new = metaconfigure.MenuItemFactory(menu.BrowserMenuItem, title="New",
  ...                                 action="new.html", _for=Content)
  >>> provideAdapter(new, (Content, IBrowserRequest), EditMenu, 'new')


The utility that is used to generate the menu into a TAL-friendly
data-structure is ``getMenu()``::

  getMenu(menuId, object, request)

where ``menuId`` is the id originally specified for the menu. Let's look up the
menu now:

  >>> pprint(menu.getMenu('edit', Content(), TestRequest()))
  [{'action': 'new.html',
    'description': '',
    'extra': None,
    'icon': None,
    'selected': '',
    'submenu': None,
    'title': 'New'},
   {'action': 'redo.html',
    'description': '',
    'extra': None,
    'icon': '/@@/redo.png',
    'selected': '',
    'submenu': None,
    'title': 'Redo'},
   {'action': 'undo.html',
    'description': '',
    'extra': None,
    'icon': None,
    'selected': '',
    'submenu': None,
    'title': 'Undo'},
   {'action': '',
    'description': '',
    'extra': None,
    'icon': None,
    'selected': '',
    'submen': [{'action': 'saveall.html',
                 'description': '',
                 'extra': None,
                 'icon': None,
                 'selected': '',
                 'submenu': None,
                 'title': 'Save all'},
                {'action': 'saveas.html',
                 'description': '',
                 'extra': None,
                 'icon': None,
                 'selected': '',
                 'submenu': None,
                 'title': 'Save as'}],
    'title': 'Save'}]


Custom ``IBrowserMenu`` Implementations
---------------------------------------

Until now we have only seen how to use the default menu implementation. Much
of the above boilerplate was necessary just to support custom menus. But what
could custom menus do? Sometimes menu items are dynamically generated based on
a certain state of the object the menu is for. For example, you might want to
show all items in a folder-like component. So first let's create this
folder-like component:

  >>> class Folderish(Content):
  ...     names = ['README.txt', 'logo.png', 'script.py']

Now we create a menu using the names to create a menu:

  >>> from zope.browsermenu.interfaces import IBrowserMenu

  >>> @zope.interface.implementer(IBrowserMenu)
  ... class Items(object):
  ...
  ...     def __init__(self, id, title='', description=''):
  ...         self.id = id
  ...         self.title = title
  ...         self.description = description
  ...
  ...     def getMenuItems(self, object, request):
  ...         return [{'title': name,
  ...                  'description': None,
  ...                  'action': name + '/manage',
  ...                  'selected': '',
  ...                  'icon': None,
  ...                  'extra': {},
  ...                  'submenu': None}
  ...                 for name in object.names]

and register it:

  >>> provideUtility(Items('items', 'Items', 'Items Men'),
  ...                IBrowserMenu, 'items')

We can now get the menu items using the previously introduced API:

  >>> pprint(menu.getMenu('items', Folderish(), TestRequest()))
  [{'action': 'README.txt/manage',
    'description': None,
    'extra': {},
    'icon': None,
    'selected': '',
    'submenu': None,
    'title': 'README.txt'},
   {'action': 'logo.png/manage',
    'description': None,
    'extra': {},
    'icon': None,
    'selected': '',
    'submenu': None,
    'title': 'logo.png'},
   {'action': 'script.py/manage',
    'description': None,
    'extra': {},
    'icon': None,
    'selected': '',
    'submenu': None,
    'title': 'script.py'}]


``MenuItemFactory`` class
-------------------------

As you have seen above already, we have used the menu item factory to generate
adapter factories for menu items. The factory needs a particular
``IBrowserMenuItem`` class to instantiate. Here is an example using a dummy
menu item class:

  >>> class DummyBrowserMenuItem(object):
  ...     "a dummy factory for menu items"
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request

To instantiate this class, pass the factory and the other arguments as keyword
arguments (every key in the arguments should map to an attribute of the menu
item class). We use dummy values for this example.

  >>> factory = metaconfigure.MenuItemFactory(
  ...     DummyBrowserMenuItem, title='Title', description='Description',
  ...     icon='Icon', action='Action', filter='Filter',
  ...     permission='zope.Public', extra='Extra', order='Order', _for='For')
  >>> factory.factory is DummyBrowserMenuItem
  True

The "zope.Public" permission needs to be translated to ``CheckerPublic``.

  >>> from zope.security.checker import CheckerPublic
  >>> factory.kwargs['permission'] is CheckerPublic
  True

Call the factory with context and request to return the instance.  We continue
to use dummy values.

  >>> item = factory('Context', 'Request')

The returned value should be an instance of the ``DummyBrowserMenuItem``, and
have all of the values we initially set on the factory.

  >>> isinstance(item, DummyBrowserMenuItem)
  True
  >>> item.context
  'Context'
  >>> item.request
  'Request'
  >>> item.title
  'Title'
  >>> item.description
  'Description'
  >>> item.icon
  'Icon'
  >>> item.action
  'Action'
  >>> item.filter
  'Filter'
  >>> item.permission is CheckerPublic
  True
  >>> item.extra
  'Extra'
  >>> item.order
  'Order'
  >>> item._for
  'For'

If you pass a permission other than ``zope.Public`` to the
``MenuItemFactory``, it should pass through unmodified.

  >>> factory = metaconfigure.MenuItemFactory(
  ...     DummyBrowserMenuItem, title='Title', description='Description',
  ...     icon='Icon', action='Action', filter='Filter',
  ...     permission='another.Permission', extra='Extra', order='Order',
  ...     _for='For_')
  >>> factory.kwargs['permission']
  'another.Permission'


Directive Handlers
------------------

``menu`` Directive Handler
~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a new menu (item type).

  >>> class Context(object):
  ...     info = 'doc'
  ...     def __init__(self):
  ...         self.actions = []
  ...
  ...     def action(self, **kw):
  ...         self.actions.append(kw)

Possibility 1: The Old Way
++++++++++++++++++++++++++

  >>> context = Context()
  >>> metaconfigure.menuDirective(context, 'menu1', title='Menu 1')
  >>> iface = context.actions[0]['args'][1]
  >>> iface.getName()
  'menu1'

  >>> import sys
  >>> hasattr(sys.modules['zope.app.menus'], 'menu1')
  True

  >>> del sys.modules['zope.app.menus'].menu1

Possibility 2: Just specify an interface
++++++++++++++++++++++++++++++++++++++++

  >>> class menu1(zope.interface.Interface):
  ...     pass

  >>> context = Context()
  >>> metaconfigure.menuDirective(context, interface=menu1)
  >>> context.actions[0]['args'][1] is menu1
  True

Possibility 3: Specify an interface and an id
+++++++++++++++++++++++++++++++++++++++++++++

  >>> context = Context()
  >>> metaconfigure.menuDirective(context, id='menu1', interface=menu1)

  >>> pprint([action['discriminator'] for action in context.actions])
  [('browser', 'MenuItemType', '__builtin__.menu1'),
   ('interface', '__builtin__.menu1'),
   ('browser', 'MenuItemType', 'menu1'),
   ('utility',
    <InterfaceClass zope.browsermenu.interfaces.IBrowserMenu>,
    'menu1'),
   None]

Here are some disallowed configurations.

  >>> context = Context()
  >>> metaconfigure.menuDirective(context)
  Traceback (most recent call last):
  ...
  ConfigurationError: You must specify the 'id' or 'interface' attribute.

  >>> metaconfigure.menuDirective(context, title='Menu 1')
  Traceback (most recent call last):
  ...
  ConfigurationError: You must specify the 'id' or 'interface' attribute.


``menuItems`` Directive Handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register several menu items for a particular menu.

  >>> class TestMenuItemType(zope.interface.Interface):
  ...     pass

  >>> class ITest(zope.interface.Interface):
  ...     pass

  >>> context = Context()
  >>> items = metaconfigure.menuItemsDirective(context, TestMenuItemType, ITest)
  >>> context.actions
  []
  >>> items.menuItem(context, 'view.html', 'View')
  >>> items.subMenuItem(context, SaveOptions, 'Save')

  >>> disc = sorted([action['discriminator'] for action in context.actions
  ...                if action['discriminator'] is not None])
  >>> pprint(disc[-2:])
  [('adapter',
    (<InterfaceClass __builtin__.ITest>,
     <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
    <InterfaceClass __builtin__.TestMenuItemType>,
    'Save'),
   ('adapter',
    (<InterfaceClass __builtin__.ITest>,
     <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
    <InterfaceClass __builtin__.TestMenuItemType>,
    'View')]

Custom menu item classes
~~~~~~~~~~~~~~~~~~~~~~~~

We can register menu items and sub menu items with custom classes instead
of ones used by default. For that, we need to create an implementation
of ``IBrowserMenuItem`` or ``IBrowserSubMenuItem``.

  >>> context = Context()
  >>> items = metaconfigure.menuItemsDirective(context, TestMenuItemType, ITest)
  >>> context.actions
  []

Let's create a custom menu item class that inherits standard ``BrowserMenuItem``:

  >>> class MyMenuItem(menu.BrowserMenuItem):
  ...    pass

  >>> items.menuItem(context, 'view.html', 'View', item_class=MyMenuItem)

Also create a custom sub menu item class inheriting standard ``BrowserSubMenuItem``:

  >>> class MySubMenuItem(menu.BrowserSubMenuItem):
  ...    pass

  >>> items.subMenuItem(context, SaveOptions, 'Save', item_class=MySubMenuItem)

  >>> actions = sorted(context.actions, key=lambda a:a['discriminator'] or ())
  >>> factories = [action['args'][1] for action in actions][-2:]

  >>> factories[0].factory is MySubMenuItem
  True

  >>> factories[1].factory is MyMenuItem
  True

These directive will fail if you provide an item_class that does not
implement ``IBrowserMenuItem``/``IBrowserSubMenuItem``:

  >>> items.menuItem(context, 'fail', 'Failed', item_class=object)
  Traceback (most recent call last):
  ...
  ValueError: Item class (<type 'object'>) must implement IBrowserMenuItem

  >>> items.subMenuItem(context, SaveOptions, 'Failed', item_class=object)
  Traceback (most recent call last):
  ...
  ValueError: Item class (<type 'object'>) must implement IBrowserSubMenuItem
