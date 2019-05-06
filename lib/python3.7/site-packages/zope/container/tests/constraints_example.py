from zope.interface import implementer
from zope.location.interfaces import IContained

from zope.container.interfaces import IContainer
from zope.container.constraints import containers
from zope.container.constraints import contains

class IBuddyFolder(IContainer):
    contains('.IBuddy')

class IBuddy(IContained):
    containers(IBuddyFolder)

@implementer(IBuddy)
class Buddy:
    pass

@implementer(IBuddyFolder)
class BuddyFolder:
    pass

class IContact(IContained):
    containers('.IContacts')

class IContacts(IContainer):
    contains(IContact)

@implementer(IContact)
class Contact:
    pass

@implementer(IContacts)
class Contacts:
    pass
