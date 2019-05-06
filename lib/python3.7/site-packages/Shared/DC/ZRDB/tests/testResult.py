from six import StringIO
from unittest import TestCase, TestSuite, makeSuite
from ExtensionClass import Base
from Shared.DC.ZRDB.Results import Results
from Shared.DC.ZRDB import RDB


class Brain(Base):
    def __init__(self, *args):
        pass


Parent = Base()


class TestResults(TestCase):

    def test_results(self):
        r = Results(([{'name': 'foo', 'type': 'integer'},
                      {'name': 'bar', 'type': 'integer'}],
                     ((1, 2), (3, 4))),
                    brains=Brain,
                    parent=Parent)
        self.assertEqual(len(r), 2)
        row = r[0]
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], 2)
        self.assertEqual(row.foo, 1)
        self.assertEqual(row.bar, 2)
        self.assertEqual(row.FOO, 1)
        self.assertEqual(row.BAR, 2)
        row = r[1]
        self.assertEqual(row[0], 3)
        self.assertEqual(row[1], 4)
        self.assertEqual(row.foo, 3)
        self.assertEqual(row.bar, 4)
        self.assertEqual(row.FOO, 3)
        self.assertEqual(row.BAR, 4)
        self.assertTrue(isinstance(row, Brain))

    def test_rdb_file(self):
        infile = StringIO("""\
        foo\tbar
        2i\t2i
        1\t2
        3\t4\
        """)
        r = RDB.File(infile,
                     brains=Brain,
                     parent=Parent)
        self.assertEqual(len(r), 2)
        row = r[0]
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], 2)
        self.assertEqual(row.foo, 1)
        self.assertEqual(row.bar, 2)
        self.assertEqual(row.FOO, 1)
        self.assertEqual(row.BAR, 2)
        row = r[1]
        self.assertEqual(row[0], 3)
        self.assertEqual(row[1], 4)
        self.assertEqual(row.foo, 3)
        self.assertEqual(row.bar, 4)
        self.assertEqual(row.FOO, 3)
        self.assertEqual(row.BAR, 4)
        self.assertTrue(isinstance(row, Brain))


def test_suite():
    return TestSuite((makeSuite(TestResults),))
