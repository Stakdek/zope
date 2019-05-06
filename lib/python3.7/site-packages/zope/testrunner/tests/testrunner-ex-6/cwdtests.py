import unittest
import os

class Layer1:
    pass

class Layer2:
    pass


class Test1(unittest.TestCase):
    layer = Layer1

    def test_that_chdirs(self):
        os.chdir(os.path.dirname(__file__))


class Test2(unittest.TestCase):
    layer = Layer2

    def test(self):
        pass
