import unittest
import textwrap
from zope.testing.renormalizing import strip_dottedname_from_traceback


class Exception2To3(unittest.TestCase):

    def test_strip_dottedname(self):
        string = textwrap.dedent("""\
            Traceback (most recent call last):
            foo.bar.FooBarError: requires at least one argument.""")
        expected = textwrap.dedent("""\
            Traceback (most recent call last):
            FooBarError: requires at least one argument.""")
        self.assertEqual(expected, strip_dottedname_from_traceback(string))

    def test_no_dots_in_name(self):
        string = textwrap.dedent("""\
            Traceback (most recent call last):
            FooBarError: requires at least one argument.""")
        expected = textwrap.dedent("""\
            Traceback (most recent call last):
            FooBarError: requires at least one argument.""")
        self.assertEqual(expected, strip_dottedname_from_traceback(string))

    def test_no_colon_in_first_word(self):
        string = textwrap.dedent("""\
            Traceback (most recent call last):
            foo.bar.FooBarError requires at least one argument.""")
        expected = textwrap.dedent("""\
            Traceback (most recent call last):
            foo.bar.FooBarError requires at least one argument.""")
        self.assertEqual(expected, strip_dottedname_from_traceback(string))

    def test_input_empty(self):
        string = ''
        expected = ''
        self.assertEqual(expected, strip_dottedname_from_traceback(string))

    def test_input_spaces(self):
        string = '   '
        expected = '   '
        self.assertEqual(expected, strip_dottedname_from_traceback(string))

    def test_last_line_empty(self):
        string = textwrap.dedent("""\
            Traceback (most recent call last):

            """)
        expected = textwrap.dedent("""\
            Traceback (most recent call last):

            """)
        self.assertEqual(expected, strip_dottedname_from_traceback(string))
