# -*- coding: utf-8 -*-
"""
Tests for namespaces.py.

"""

import unittest

from z3c.pt import namespaces


class TestAdapterNamespaces(unittest.TestCase):
    def test_registered_name(self):
        nss = namespaces.AdapterNamespaces()
        func = lambda ctx: ctx  # noqa: E731
        nss.registerFunctionNamespace("ns", func)
        self.assertIs(func, nss["ns"])
        self.assertIs(func, nss.getFunctionNamespace("ns"))

    def test_unregistered_name(self):
        nss = namespaces.AdapterNamespaces()
        with self.assertRaises(KeyError):
            nss.getFunctionNamespace("ns")

        # but __getitem__ makes one up
        self.assertIsNotNone(nss["ns"])

    def test_using_pagetemplate_version(self):
        from zope.pagetemplate import engine

        self.assertNotIsInstance(
            namespaces.function_namespaces, namespaces.AdapterNamespaces
        )
        self.assertIsInstance(
            namespaces.function_namespaces, engine.AdapterNamespaces
        )
