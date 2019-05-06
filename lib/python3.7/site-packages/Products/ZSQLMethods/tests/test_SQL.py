import unittest


class SQLMethodTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.ZSQLMethods.SQL import SQL
        return SQL

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_class_conforms_to_IWriteLock(self):
        from zope.interface.verify import verifyClass
        try:
            from OFS.interfaces import IWriteLock
        except ImportError:
            from webdav.interfaces import IWriteLock
        verifyClass(IWriteLock, self._getTargetClass())


class SQLConnectionIdsTests(unittest.TestCase):

    def setUp(self):
        from OFS.Folder import Folder
        from Products.ZSQLMethods.tests.dummy import DummySQLConnection
        super(SQLConnectionIdsTests, self).setUp()

        self.root = Folder('root')
        conn1 = DummySQLConnection('conn1', 'Title1')
        self.root._setObject('conn1', conn1)
        self.root._setObject('child1', Folder('child1'))
        conn2 = DummySQLConnection('conn2', 'Title2')
        self.root.child1._setObject('conn2', conn2)
        self.root._setObject('child2', Folder('child2'))
        conn3 = DummySQLConnection('conn3')
        self.root.child2._setObject('conn3', conn3)
        self.root.child1._setObject('grandchild1', Folder('grandchild1'))
        conn4 = DummySQLConnection('conn4')
        self.root.child1.grandchild1._setObject('conn4', conn4)

    def test_SQLConnectionIDs(self):
        from Products.ZSQLMethods.SQL import SQLConnectionIDs

        self.assertEqual(SQLConnectionIDs(self.root),
                         [('Title1 (conn1)', 'conn1')])
        self.assertEqual(SQLConnectionIDs(self.root.child1),
                         [('Title1 (conn1)', 'conn1'),
                          ('Title2 (conn2)', 'conn2')])
        self.assertEqual(SQLConnectionIDs(self.root.child1.grandchild1),
                         [('Title1 (conn1)', 'conn1'),
                          ('Title2 (conn2)', 'conn2'),
                          ('conn4', 'conn4')])
        self.assertEqual(SQLConnectionIDs(self.root.child2),
                         [('Title1 (conn1)', 'conn1'),
                          ('conn3', 'conn3')])


def test_suite():
    return unittest.TestSuite((unittest.makeSuite(SQLMethodTests),
                               unittest.makeSuite(SQLConnectionIdsTests)))
