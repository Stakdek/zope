# Dummy implementations for unit tests

from Acquisition import Implicit
from ExtensionClass import Base


class DummySQLConnection(Base, Implicit):

    _isAnSQLConnection = True
    meta_type = 'Dummy ZSQLConnection'

    def __init__(self, id, title=''):
        self._id = id
        self.title = title

    def id(self):
        return self._id

    def title_and_id(self):
        if not self.title:
            return self._id
        return '%s (%s)' % (self.title, self._id)
