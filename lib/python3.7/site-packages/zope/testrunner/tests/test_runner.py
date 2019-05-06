##############################################################################
#
# Copyright (c) 2015 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests for the testrunner's runner logic
"""
import sys
import unittest

from zope.testrunner import runner
from zope.testrunner.layer import UnitTests


class TestLayerOrdering(unittest.TestCase):

    def sort_key(self, layer):
        return ', '.join(qn.rpartition('.')[-1]
                         for qn in runner.layer_sort_key(layer))

    def order(self, *layers):
        return ', '.join(l.__name__ for l in runner.order_by_bases(layers))

    def test_order_by_bases(self):
        #    A      B
        #   /|\    /
        #  / | \  /
        # A1 A2 AB
        class A(object): pass
        class A1(A): pass
        class A2(A): pass
        class B(object): pass
        class AB(A, B): pass
        self.assertEqual(self.order(B, A1, A2, A1, AB, UnitTests),
                         'UnitTests, A1, A2, B, AB')
        self.assertEqual(self.sort_key(UnitTests), '')
        self.assertEqual(self.sort_key(A1), 'A, A1')
        self.assertEqual(self.sort_key(A2), 'A, A2')
        self.assertEqual(self.sort_key(B), 'B')
        self.assertEqual(self.sort_key(AB), 'B, A, AB')

    def test_order_by_bases_alphabetical_order(self):
        class X(object): pass
        class Y(object): pass
        class Z(object): pass
        class A(Y): pass
        class B(X): pass
        class C(Z): pass
        # It'd be nice to get A, B, C here, but that's not trivial.
        self.assertEqual(self.order(A, B, C), 'B, A, C')
        self.assertEqual(self.sort_key(B), 'X, B')
        self.assertEqual(self.sort_key(A), 'Y, A')
        self.assertEqual(self.sort_key(C), 'Z, C')

    def test_order_by_bases_diamond_hierarchy(self):
        #      A
        #     / \
        #    B   D
        #    |   |
        #    C   E
        #     \ /
        #      F
        class A(object): pass
        class B(A): pass
        class C(B): pass
        class D(A): pass
        class E(D): pass
        class F(C, E): pass
        self.assertEqual(self.order(A, B, C, D, E, F), 'A, B, C, D, E, F')
        self.assertEqual(self.sort_key(A), 'A')
        self.assertEqual(self.sort_key(B), 'A, B')
        self.assertEqual(self.sort_key(C), 'A, B, C')
        self.assertEqual(self.sort_key(D), 'A, D')
        self.assertEqual(self.sort_key(E), 'A, D, E')
        self.assertEqual(self.sort_key(F), 'A, D, E, B, C, F')
        # only those layers that were passed in are returned
        self.assertEqual(self.order(B, E), 'B, E')

    def test_order_by_bases_shared_setup_trumps_alphabetical_order(self):
        #       A
        #      / \
        #     AB AC
        #    /  \  \
        # AAAABD \ MMMACF
        #      ZZZABE
        class A(object): pass
        class AB(A): pass
        class AC(A): pass
        class AAAABD(AB): pass
        class ZZZABE(AB): pass
        class MMMACF(AC): pass
        self.assertEqual(self.order(AAAABD, MMMACF, ZZZABE),
                         'AAAABD, ZZZABE, MMMACF')
        self.assertEqual(self.sort_key(AAAABD), 'A, AB, AAAABD')
        self.assertEqual(self.sort_key(ZZZABE), 'A, AB, ZZZABE')
        self.assertEqual(self.sort_key(MMMACF), 'A, AC, MMMACF')

    def test_order_by_bases_multiple_inheritance(self):
        # Layerx      Layer1
        # |  \        /    \
        # |   \ Layer11    Layer12
        # |    \   | |      /    \
        # | Layer111 | Layer121  Layer122
        #  \        /
        #   \      /
        #   Layer112
        #
        class Layer1: pass
        class Layerx: pass
        class Layer11(Layer1): pass
        class Layer12(Layer1): pass
        class Layer111(Layerx, Layer11): pass
        class Layer121(Layer12): pass
        class Layer112(Layerx, Layer11): pass
        class Layer122(Layer12): pass
        self.assertEqual(
            self.order(Layer1, Layer11, Layer12, Layer111, Layer112, Layer121,
                       Layer122),
            'Layer1, Layer11, Layer111, Layer112, Layer12, Layer121, Layer122')
        self.assertEqual(self.order(Layer111, Layer12), 'Layer111, Layer12')
        self.assertEqual(self.order(Layerx, Layer1, Layer11, Layer112),
                         'Layer1, Layer11, Layerx, Layer112')
        self.assertEqual(self.sort_key(Layer111),
                         'Layer1, Layer11, Layerx, Layer111')
        self.assertEqual(self.sort_key(Layer12),
                         'Layer1, Layer12')

    def test_order_by_bases_reverse_tree(self):
        # E   D  F
        #  \ / \ /
        #   B   C
        #    \ /
        #     A
        class F(object): pass
        class E(object): pass
        class D(object): pass
        class C(D, F): pass
        class B(D, E): pass
        class A(B, C): pass
        self.assertEqual(self.order(A, B, C), 'B, C, A')
        self.assertEqual(self.order(A, B, C, D, E, F), 'D, E, B, F, C, A')

    def test_order_by_bases_mro_is_complicated(self):
        #  A  C  B  E  D
        # / \ | / \ | / \
        # \  K1     K2  /
        #  `---.    _--'
        #     \ \  / |
        #      \ K3 /
        #       \ |/
        #        ZZ
        class A(object): pass
        class B(object): pass
        class C(object): pass
        class D(object): pass
        class E(object): pass
        class K1(A, B, C): pass
        class K2(D, B, E): pass
        class K3(D, A): pass
        class ZZ(K1, K2, K3): pass
        self.assertEqual(self.order(K1, K2, K3, ZZ),
                         'K3, K2, K1, ZZ')
        # Sorting by reverse MRO, as computed by Python's MRO algorithm,
        # would put the layers in a different order: K3, K1, K2, ZZ.
        # Does that matter?  The class diagram is symmetric, so I think not.

    def test_FakeInputContinueGenerator_close(self):
        # multiprocessing (and likely other forkful frameworks) want to
        # close sys.stdin.  The test runner replaces sys.stdin with a
        # FakeInputContinueGenerator for some reason. It should be
        # closeable.

        f = runner.FakeInputContinueGenerator()
        f.close()

@unittest.skipIf(sys.warnoptions, "Only done if no user override")
class TestWarnings(unittest.TestCase):

    def test_warning_filter_default(self):
        # When we run tests, we run them with a 'default' simplefilter.
        # Note that this test will fail if PYTHONWARNINGS is set,
        # or a -W option was given, so we skip it
        import warnings
        # Save the current filters, ignoring the compiled regexes,
        # which can't be compared.
        old_filters = [(f[0], f[2], 4) for f in warnings.filters]
        with warnings.catch_warnings():
            # Set up just like the runner does
            warnings.simplefilter('default')
            warnings.filterwarnings('module',
                                    category=DeprecationWarning,
                                    message=r'Please use assert\w+ instead.')
            new_filters = [(f[0], f[2], 4) for f in warnings.filters]

        # For some reason, catch_warnings doesn't fully reset things,
        # and we wind up with some duplicate entries in new_filters
        self.assertEqual(set(old_filters), set(new_filters))


    def test_warnings_are_shown(self):
        import warnings
        import logging
        from zope.testing.loggingsupport import InstalledHandler

        handler = InstalledHandler("py.warnings", level=logging.WARNING)
        self.addCleanup(handler.uninstall)

        logging.captureWarnings(True)
        self.addCleanup(logging.captureWarnings, False)

        msg = "This should be visible by default"
        warnings.warn(msg, DeprecationWarning)

        self.assertEqual(1, len(handler.records))
        self.assertIn('DeprecationWarning', handler.records[0].getMessage())
        self.assertIn(msg, handler.records[0].getMessage())
