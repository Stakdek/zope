# -*- coding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" GenericSetup.utils unit tests
"""

try:
    from html import escape  # noqa
    HTML_ESCAPE = True
except ImportError:
    HTML_ESCAPE = False
import six
import unittest

from DateTime.DateTime import DateTime
from Testing.ZopeTestCase import installProduct
from Testing.ZopeTestCase import ZopeTestCase

installProduct('GenericSetup')

_TESTED_PROPERTIES = (
    {'id': 'foo_boolean', 'type': 'boolean', 'mode': 'wd'},
    {'id': 'foo_date', 'type': 'date', 'mode': 'wd'},
    {'id': 'foo_float', 'type': 'float', 'mode': 'wd'},
    {'id': 'foo_int', 'type': 'int', 'mode': 'wd'},
    {'id': 'foo_lines', 'type': 'lines', 'mode': 'wd'},
    {'id': 'foo_long', 'type': 'long', 'mode': 'wd'},
    {'id': 'foo_string', 'type': 'string', 'mode': 'wd'},
    {'id': 'foo_text', 'type': 'text', 'mode': 'wd'},
    {'id': 'foo_tokens', 'type': 'tokens', 'mode': 'wd'},
    {'id': 'foo_selection', 'type': 'selection',
           'select_variable': 'foobarbaz', 'mode': 'wd'},
    {'id': 'foo_mselection', 'type': 'multiple selection',
           'select_variable': 'foobarbaz', 'mode': 'wd'},
    {'id': 'foo_boolean0', 'type': 'boolean', 'mode': 'wd'},
    {'id': 'foo_date_naive', 'type': 'date', 'mode': 'wd'},
    {'id': 'foo_ro', 'type': 'string', 'mode': ''},
    {'id': 'foo_boolean_nodel', 'type': 'boolean', 'mode': 'w'},
    {'id': 'foo_date_nodel', 'type': 'date', 'mode': 'w'},
    {'id': 'foo_float_nodel', 'type': 'float', 'mode': 'w'},
    {'id': 'foo_int_nodel', 'type': 'int', 'mode': 'w'},
)

_EMPTY_PROPERTY_EXPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <property name="foo_boolean" type="boolean">False</property>
 <property name="foo_date" type="date">1970/01/01 00:00:00 UTC</property>
 <property name="foo_float" type="float">0.0</property>
 <property name="foo_int" type="int">0</property>
 <property name="foo_lines" type="lines"/>
 <property name="foo_long" type="long">0</property>
 <property name="foo_string" type="string"></property>
 <property name="foo_text" type="text"></property>
 <property name="foo_tokens" type="tokens"/>
 <property name="foo_selection" select_variable="foobarbaz"
    type="selection"></property>
 <property name="foo_mselection" select_variable="foobarbaz"
    type="multiple selection"/>
 <property name="foo_boolean0" type="boolean">False</property>
 <property name="foo_date_naive" type="date">1970/01/01 00:00:00</property>
 <property name="foo_boolean_nodel">False</property>
 <property name="foo_date_nodel">1970/01/01 00:00:00 UTC</property>
 <property name="foo_float_nodel">0.0</property>
 <property name="foo_int_nodel">0</property>
</dummy>
""".encode('utf-8')

_NONE_PROPERTY_EXPORT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <property name="foo_boolean" type="boolean">False</property>
 <property name="foo_date" type="date">1970/01/01 00:00:00 UTC</property>
 <property name="foo_float" type="float">0.0</property>
 <property name="foo_int" type="int">0</property>
 <property name="foo_lines" type="lines"/>
 <property name="foo_long" type="long">0</property>
 <property name="foo_string" type="string"></property>
 <property name="foo_tokens" type="tokens"/>
 <property name="foo_selection" select_variable="foobarbaz"
    type="selection"></property>
 <property name="foo_mselection" select_variable="foobarbaz"
    type="multiple selection"/>
 <property name="foo_boolean0" type="boolean">False</property>
 <property name="foo_date_naive" type="date">1970/01/01 00:00:00</property>
 <property name="foo_boolean_nodel">False</property>
 <property name="foo_date_nodel">1970/01/01 00:00:00 UTC</property>
 <property name="foo_float_nodel">0.0</property>
 <property name="foo_int_nodel">0</property>
</dummy>
""".encode('utf-8')

_NORMAL_PROPERTY_EXPORT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <property name="foo_boolean" type="boolean">True</property>
 <property name="foo_date" type="date">2000/01/01 00:00:00 UTC</property>
 <property name="foo_float" type="float">1.1</property>
 <property name="foo_int" type="int">1</property>
 <property name="foo_lines" type="lines">
  <element value="Foo"/>
  <element value="Lines"/>
  <element value="\xfcbrigens"/>
 </property>
 <property name="foo_long" type="long">1</property>
 <property name="foo_string" type="string">Foo String</property>
 <property name="foo_text" type="text">Foo
  Text</property>
 <property name="foo_tokens" type="tokens">
  <element value="Foo"/>
  <element value="Tokens"/>
 </property>
 <property name="foo_selection" select_variable="foobarbaz"
    type="selection">Foo</property>
 <property name="foo_mselection" select_variable="foobarbaz"
    type="multiple selection">
  <element value="Foo"/>
  <element value="Baz"/>
 </property>
 <property name="foo_boolean0" type="boolean">False</property>
 <property name="foo_date_naive" type="date">2000/01/01 00:00:00</property>
 <property name="foo_boolean_nodel">True</property>
 <property name="foo_date_nodel">2000/01/01 00:00:00 UTC</property>
 <property name="foo_float_nodel">3.1415</property>
 <property name="foo_int_nodel">1789</property>
</dummy>
""".encode('utf-8')

_NORMAL_PROPERTY_EXPORT_ISO_8859_1 = u"""\
<?xml version="1.0" encoding="iso-8859-1"?>
<dummy>
 <property name="foo_boolean" type="boolean">True</property>
 <property name="foo_date" type="date">2000/01/01 00:00:00 UTC</property>
 <property name="foo_float" type="float">1.1</property>
 <property name="foo_int" type="int">1</property>
 <property name="foo_lines" type="lines">
  <element value="Foo"/>
  <element value="Lines"/>
  <element value="\xfcbrigens"/>
 </property>
 <property name="foo_long" type="long">1</property>
 <property name="foo_string" type="string">Foo String</property>
 <property name="foo_text" type="text">Foo
  Text</property>
 <property name="foo_tokens" type="tokens">
  <element value="Foo"/>
  <element value="Tokens"/>
 </property>
 <property name="foo_selection" select_variable="foobarbaz"
    type="selection">Foo</property>
 <property name="foo_mselection" select_variable="foobarbaz"
    type="multiple selection">
  <element value="Foo"/>
  <element value="Baz"/>
 </property>
 <property name="foo_boolean0" type="boolean">False</property>
 <property name="foo_date_naive" type="date">2000/01/01 00:00:00</property>
 <property name="foo_boolean_nodel">True</property>
 <property name="foo_date_nodel">2000/01/01 00:00:00 UTC</property>
 <property name="foo_float_nodel">3.1415</property>
 <property name="foo_int_nodel">1789</property>
</dummy>
""".encode('iso-8859-1')

_NORMAL_PROPERTY_EXPORT_OLD = b"""\
<?xml version="1.0"?>
<dummy>
 <property name="foo_boolean" type="boolean">True</property>
 <property name="foo_date" type="date">2000/01/01 00:00:00 UTC</property>
 <property name="foo_float" type="float">1.1</property>
 <property name="foo_int" type="int">1</property>
 <property name="foo_lines" type="lines">
  <element value="Foo"/>
  <element value="Lines"/>
  <element value="\xc3\xbcbrigens"/>
 </property>
 <property name="foo_long" type="long">1</property>
 <property name="foo_string" type="string">Foo String</property>
 <property name="foo_text" type="text">Foo
  Text</property>
 <property name="foo_tokens" type="tokens">
  <element value="Foo"/>
  <element value="Tokens"/>
 </property>
 <property name="foo_selection" select_variable="foobarbaz"
    type="selection">Foo</property>
 <property name="foo_mselection" select_variable="foobarbaz"
    type="multiple selection">
  <element value="Foo"/>
  <element value="Baz"/>
 </property>
 <property name="foo_boolean0" type="boolean">False</property>
 <property name="foo_date_naive" type="date">2000/01/01 00:00:00</property>
 <property name="foo_boolean_nodel">True</property>
 <property name="foo_date_nodel">2000/01/01 00:00:00 UTC</property>
 <property name="foo_float_nodel">3.1415</property>
 <property name="foo_int_nodel">1789</property>
</dummy>
"""

_FIXED_PROPERTY_EXPORT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <property name="foo_boolean">True</property>
 <property name="foo_date">2000/01/01 00:00:00 UTC</property>
 <property name="foo_float">1.1</property>
 <property name="foo_int">1</property>
 <property name="foo_lines">
  <element value="Foo"/>
  <element value="Lines"/>
 <element value="\xfcbrigens"/>
 </property>
 <property name="foo_long">1</property>
 <property name="foo_string">Foo String</property>
 <property name="foo_text">Foo
  Text</property>
 <property name="foo_tokens">
  <element value="Foo"/>
  <element value="Tokens"/></property>
 <property name="foo_selection" type="selection"
    select_variable="foobarbaz">Foo</property>
 <property name="foo_mselection">
  <element value="Foo"/>
  <element value="Baz"/>
 </property>
 <property name="foo_boolean0">False</property>
 <property name="foo_date_naive">2000/01/01 00:00:00</property>
 <property name="foo_boolean_nodel">True</property>
 <property name="foo_date_nodel">2000/01/01 00:00:00 UTC</property>
 <property name="foo_float_nodel">3.1415</property>
 <property name="foo_int_nodel">1789</property>
</dummy>
""".encode('utf-8')

_SPECIAL_IMPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <!-- ignore comment, import 0 as False -->
 <property name="foo_boolean0" type="boolean">0</property>
</dummy>
""".encode('utf-8')

_I18N_IMPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<dummy xmlns:i18n="http://xml.zope.org/namespaces/i18n"
   i18n:domain="dummy_domain">
 <property name="foo_string" i18n:translate="">Foo String</property>
</dummy>
""".encode('utf-8')

_NOPURGE_IMPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <property name="lines1">
  <element value="Foo"/>
  <element value="Bar"/>
 </property>
 <property name="lines2" purge="True">
  <element value="Foo"/>
  <element value="Bar"/>
 </property>
 <property name="lines3" purge="False">
  <element value="Foo"/>
  <element value="Bar"/>
 </property>
</dummy>
""".encode('utf-8')

_REMOVE_ELEMENT_IMPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <property name="lines1" purge="False">
   <element value="Foo" remove="True" />
   <element value="Bar" remove="False" />
  </property>
 <property name="lines2" purge="False">
   <element value="Foo" remove="True" />
  </property>
</dummy>
""".encode('utf-8')

_NORMAL_MARKER_EXPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <marker name="Products.GenericSetup.testing.IDummyMarker"/>
</dummy>
""".encode('utf-8')

_ADD_IMPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <object name="history" meta_type="Generic Setup Tool"/>
 <object name="future" meta_type="Generic Setup Tool"/>
</dummy>
""".encode('utf-8')

_REMOVE_IMPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <object name="history" remove="True"/>
 <object name="future" remove="False"/>
</dummy>
""".encode('utf-8')

_ADD_PROPERTY_IMPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <property name="line1" type="string">Line 1</property>
 <property name="line2" type="string">Line 2</property>
</dummy>
""".encode('utf-8')

_REMOVE_PROPERTY_IMPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<dummy>
 <property name="line1" remove="True"/>
 <property name="line2" type="string" remove="False"/>
</dummy>
""".encode('utf-8')


def _getDocumentElement(text):
    from xml.dom.minidom import parseString
    return parseString(text).documentElement


def _testFunc(*args, **kw):
    """ This is a test.

    This is only a test.
    """


_TEST_FUNC_NAME = 'Products.GenericSetup.tests.test_utils._testFunc'


class Whatever:
    pass


_WHATEVER_NAME = 'Products.GenericSetup.tests.test_utils.Whatever'

whatever_inst = Whatever()
whatever_inst.__name__ = 'whatever_inst'

_WHATEVER_INST_NAME = 'Products.GenericSetup.tests.test_utils.whatever_inst'


class UtilsTests(unittest.TestCase):

    def test__getDottedName_simple(self):

        from Products.GenericSetup.utils import _getDottedName

        self.assertEqual(_getDottedName(_testFunc), _TEST_FUNC_NAME)

    def test__getDottedName_string(self):

        from Products.GenericSetup.utils import _getDottedName

        self.assertEqual(_getDottedName(_TEST_FUNC_NAME), _TEST_FUNC_NAME)

    def test__getDottedName_unicode(self):

        from Products.GenericSetup.utils import _getDottedName

        dotted = u'%s' % _TEST_FUNC_NAME
        self.assertEqual(_getDottedName(dotted), _TEST_FUNC_NAME)
        self.assertEqual(type(_getDottedName(dotted)), str)

    def test__getDottedName_class(self):

        from Products.GenericSetup.utils import _getDottedName

        self.assertEqual(_getDottedName(Whatever), _WHATEVER_NAME)

    def test__getDottedName_inst(self):

        from Products.GenericSetup.utils import _getDottedName

        self.assertEqual(_getDottedName(whatever_inst), _WHATEVER_INST_NAME)

    def test__getDottedName_noname(self):

        from Products.GenericSetup.utils import _getDottedName

        class Doh:
            pass

        doh = Doh()
        self.assertRaises(ValueError, _getDottedName, doh)


class PropertyManagerHelpersTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.GenericSetup.utils import PropertyManagerHelpers

        return PropertyManagerHelpers

    def _makeOne(self, context=None, environ=None):
        from Products.GenericSetup.utils import NodeAdapterBase
        from Products.GenericSetup.testing import DummySetupEnviron

        class Foo(self._getTargetClass(), NodeAdapterBase):
            pass

        if context is None:
            context = self._makeContext()

        if environ is None:
            environ = DummySetupEnviron()

        return Foo(context, environ)

    def _getContextClass(self):
        from OFS.PropertyManager import PropertyManager

        class DummyContext(PropertyManager):
            _properties = _TESTED_PROPERTIES
        return DummyContext

    def _makeContext(self):
        obj = self._getContextClass()()
        obj.foobarbaz = ('Foo', 'Bar', 'Baz')
        obj.foo_boolean = False
        obj.foo_date = DateTime('1970/01/01 00:00:00 UTC')
        obj.foo_float = 0.0
        obj.foo_int = 0
        obj.foo_lines = []
        obj.foo_long = 0
        obj.foo_string = ''
        obj.foo_text = ''
        obj.foo_tokens = ()
        obj.foo_selection = ''
        obj.foo_mselection = ()
        obj.foo_boolean0 = 0
        obj.foo_date_naive = DateTime('1970/01/01 00:00:00')
        obj.foo_ro = ''
        obj.foo_boolean_nodel = False
        obj.foo_date_nodel = DateTime('1970/01/01 00:00:00 UTC')
        obj.foo_float_nodel = 0.0
        obj.foo_int_nodel = 0
        return obj

    def _getReal(self, obj):
        return obj

    def _populate(self, obj):
        obj._updateProperty('foo_boolean', 'True')
        obj._updateProperty('foo_date', '2000/01/01 00:00:00 UTC')
        obj._updateProperty('foo_float', '1.1')
        obj._updateProperty('foo_int', '1')
        if six.PY2:
            obj._updateProperty('foo_lines',
                                u'Foo\nLines\n\xfcbrigens'.encode('utf-8'))
        else:
            obj._updateProperty('foo_lines',
                                'Foo\nLines\nübrigens')
        obj._updateProperty('foo_long', '1')
        obj._updateProperty('foo_string', 'Foo String')
        obj._updateProperty('foo_text', 'Foo\nText')
        obj._updateProperty('foo_tokens', ('Foo', 'Tokens'))
        obj._updateProperty('foo_selection', 'Foo')
        obj._updateProperty('foo_mselection', ('Foo', 'Baz'))
        obj.foo_boolean0 = 0
        obj._updateProperty('foo_date_naive', '2000/01/01 00:00:00')
        obj._updateProperty('foo_ro', 'RO')
        obj._updateProperty('foo_boolean_nodel', 'True')
        obj._updateProperty('foo_date_nodel', '2000/01/01 00:00:00 UTC')
        obj._updateProperty('foo_float_nodel', '3.1415')
        obj._updateProperty('foo_int_nodel', '1789')

    def test__extractProperties_empty(self):
        from Products.GenericSetup.utils import PrettyDocument
        helpers = self._makeOne()
        doc = helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _EMPTY_PROPERTY_EXPORT)

    def test__extractProperties_none(self):
        from Products.GenericSetup.utils import PrettyDocument
        context = self._makeContext()
        # When a text property is None, in 1.10.0 you get an AttributeError:
        # 'NoneType' object has no attribute 'decode'
        context.foo_text = None
        helpers = self._makeOne(context=context)
        doc = helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NONE_PROPERTY_EXPORT)

    def test__extractProperties_normal(self):
        from Products.GenericSetup.utils import PrettyDocument
        helpers = self._makeOne()
        obj = self._getReal(helpers.context)
        self._populate(obj)
        doc = helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')

        # The extraction process wants to decode text properties
        # to unicode using the default ZPublisher encoding, which
        # defaults to iso-8859-15. We force UTF-8 here because we
        # forced our properties to be UTF-8 encoded.
        helpers._encoding = 'utf-8'
        node.appendChild(helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NORMAL_PROPERTY_EXPORT)

    def test__purgeProperties(self):
        helpers = self._makeOne()
        obj = self._getReal(helpers.context)
        self._populate(obj)
        helpers._purgeProperties()

        self.assertEqual(getattr(obj, 'foo_boolean', None), None)
        self.assertEqual(getattr(obj, 'foo_date', None), None)
        self.assertEqual(getattr(obj, 'foo_float', None), None)
        self.assertEqual(getattr(obj, 'foo_int', None), None)
        self.assertEqual(getattr(obj, 'foo_lines', None), None)
        self.assertEqual(getattr(obj, 'foo_long', None), None)
        self.assertEqual(getattr(obj, 'foo_string', None), None)
        self.assertEqual(getattr(obj, 'foo_text', None), None)
        self.assertEqual(getattr(obj, 'foo_tokens', None), None)
        self.assertEqual(getattr(obj, 'foo_selection', None), None)
        self.assertEqual(getattr(obj, 'foo_mselection', None), None)
        self.assertEqual(getattr(obj, 'foo_boolean0', None), None)
        self.assertEqual(getattr(obj, 'foo_date_naive', None), None)
        self.assertEqual(obj.foo_ro, 'RO')
        self.assertEqual(obj.foo_boolean_nodel, False)
        self.assertEqual(obj.foo_date_nodel,
                         DateTime('1970/01/01 00:00:00 UTC'))
        self.assertEqual(obj.foo_float_nodel, 0.0)
        self.assertEqual(obj.foo_int_nodel, 0)

    def test__initProperties_normal(self):
        from Products.GenericSetup.utils import PrettyDocument
        helpers = self._makeOne()
        obj = self._getReal(helpers.context)
        node = _getDocumentElement(_NORMAL_PROPERTY_EXPORT)
        helpers._initProperties(node)
        self.assertEqual(type(obj.foo_int), int)
        self.assertEqual(type(obj.foo_string), str)
        self.assertEqual(type(obj.foo_tokens), tuple)
        self.assertEqual(type(obj.foo_tokens[0]), six.binary_type)

        doc = helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NORMAL_PROPERTY_EXPORT)

    def test__initProperties_normal_oldxml(self):
        from Products.GenericSetup.utils import PrettyDocument
        helpers = self._makeOne()
        obj = self._getReal(helpers.context)
        node = _getDocumentElement(_NORMAL_PROPERTY_EXPORT_OLD)
        helpers._initProperties(node)
        self.assertEqual(type(obj.foo_int), int)
        self.assertEqual(type(obj.foo_string), str)
        self.assertEqual(type(obj.foo_tokens), tuple)
        self.assertEqual(type(obj.foo_tokens[0]), six.binary_type)

        doc = helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NORMAL_PROPERTY_EXPORT)

    def test__initProperties_normal_iso_8859_1(self):
        from Products.GenericSetup.utils import PrettyDocument
        helpers = self._makeOne()
        obj = self._getReal(helpers.context)
        node = _getDocumentElement(_NORMAL_PROPERTY_EXPORT_ISO_8859_1)
        # *sigh* The base class does not respect the encoding specified in the
        # xml, so we have to be explicit here. In the real world it is in
        # responsibility of the subclass.
        helpers._encoding = 'iso-8859-1'
        helpers._initProperties(node)
        self.assertEqual(type(obj.foo_int), int)
        self.assertEqual(type(obj.foo_string), str)
        self.assertEqual(type(obj.foo_tokens), tuple)
        self.assertEqual(type(obj.foo_tokens[0]), six.binary_type)

        doc = helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NORMAL_PROPERTY_EXPORT)

    def test__initProperties_fixed(self):
        from Products.GenericSetup.utils import PrettyDocument
        helpers = self._makeOne()
        node = _getDocumentElement(_FIXED_PROPERTY_EXPORT)
        helpers._initProperties(node)

        doc = helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NORMAL_PROPERTY_EXPORT)

    def test__initProperties_special(self):
        from Products.GenericSetup.utils import PrettyDocument
        helpers = self._makeOne()
        node = _getDocumentElement(_SPECIAL_IMPORT)
        helpers._initProperties(node)

        doc = helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _EMPTY_PROPERTY_EXPORT)

    def test__initProperties_i18n(self):
        helpers = self._makeOne()
        helpers.context.manage_addProperty('i18n_domain', '', 'string')
        node = _getDocumentElement(_I18N_IMPORT)
        helpers._initProperties(node)

        self.assertEqual(helpers.context.getProperty('i18n_domain'),
                         'dummy_domain')

    def test__initProperties_nopurge_base(self):
        helpers = self._makeOne()
        node = _getDocumentElement(_NOPURGE_IMPORT)
        helpers.environ._should_purge = True  # base profile
        obj = helpers.context
        obj._properties = ()
        obj.manage_addProperty('lines1', ('Foo', 'Gee'), 'lines')
        obj.manage_addProperty('lines2', ('Foo', 'Gee'), 'lines')
        obj.manage_addProperty('lines3', ('Foo', 'Gee'), 'lines')
        helpers._initProperties(node)

        self.assertEqual(obj.getProperty('lines1'), (b'Foo', b'Bar'))
        self.assertEqual(obj.getProperty('lines2'), (b'Foo', b'Bar'))
        self.assertEqual(obj.getProperty('lines3'), (b'Gee', b'Foo', b'Bar'))

    def test__initProperties_nopurge_extension(self):
        helpers = self._makeOne()
        node = _getDocumentElement(_NOPURGE_IMPORT)
        helpers.environ._should_purge = False  # extension profile
        obj = helpers.context
        obj._properties = ()
        obj.manage_addProperty('lines1', ('Foo', 'Gee'), 'lines')
        obj.manage_addProperty('lines2', ('Foo', 'Gee'), 'lines')
        obj.manage_addProperty('lines3', ('Foo', 'Gee'), 'lines')
        helpers._initProperties(node)

        self.assertEqual(obj.getProperty('lines1'), (b'Foo', b'Bar'))
        self.assertEqual(obj.getProperty('lines2'), (b'Foo', b'Bar'))
        self.assertEqual(obj.getProperty('lines3'), (b'Gee', b'Foo', b'Bar'))

    def test_initProperties_remove_elements(self):
        helpers = self._makeOne()
        node = _getDocumentElement(_REMOVE_ELEMENT_IMPORT)
        helpers.environ._should_purge = False  # extension profile
        obj = helpers.context
        obj._properties = ()
        obj.manage_addProperty('lines1', ('Foo', 'Gee'), 'lines')
        obj.manage_addProperty('lines2', ('Foo', 'Gee'), 'lines')
        helpers._initProperties(node)

        self.assertEqual(obj.getProperty('lines1'), (b'Gee', b'Bar'))
        self.assertEqual(obj.getProperty('lines2'), (b'Gee',))

    def test_initProperties_remove_properties(self):
        helpers = self._makeOne()
        helpers.environ._should_purge = False  # extension profile
        obj = helpers.context
        obj._properties = ()

        # Add two properties
        node = _getDocumentElement(_ADD_PROPERTY_IMPORT)
        helpers._initProperties(node)
        self.assertTrue(obj.hasProperty('line1'))
        self.assertEqual(obj.getProperty('line1'), 'Line 1')
        self.assertTrue(obj.hasProperty('line2'))

        # Remove one.
        node = _getDocumentElement(_REMOVE_PROPERTY_IMPORT)
        helpers._initProperties(node)
        self.assertFalse(obj.hasProperty('line1'))
        self.assertTrue(obj.hasProperty('line2'))

        # Removing it a second time should not throw an
        # AttributeError.
        node = _getDocumentElement(_REMOVE_PROPERTY_IMPORT)
        helpers._initProperties(node)
        self.assertFalse(obj.hasProperty('line1'))
        self.assertTrue(obj.hasProperty('line2'))


class PropertyManagerHelpersNonPMContextTests(PropertyManagerHelpersTests):

    def _makeOne(self, context=None, environ=None):
        from Products.GenericSetup.utils import NodeAdapterBase
        from Products.GenericSetup.testing import DummySetupEnviron

        class Foo(self._getTargetClass(), NodeAdapterBase):
            _PROPERTIES = _TESTED_PROPERTIES

        if context is None:
            context = self._makeContext()

        if environ is None:
            environ = DummySetupEnviron()

        return Foo(context, environ)

    def _getContextClass(self):
        class NonPropertyManager:
            pass
        return NonPropertyManager

    def _getReal(self, obj):
        return obj._real

    def _populate(self, obj):
        obj.foo_boolean = True
        obj.foo_date = DateTime('2000/01/01 00:00:00 UTC')
        obj.foo_float = 1.1
        obj.foo_int = 1
        obj.foo_lines = ['Foo', 'Lines', u'\xfcbrigens'.encode('utf-8')]
        obj.foo_long = 1
        obj.foo_string = 'Foo String'
        obj.foo_text = 'Foo\nText'
        obj.foo_tokens = ('Foo', 'Tokens')
        obj.foo_selection = 'Foo'
        obj.foo_mselection = ('Foo', 'Baz')
        obj.foo_boolean0 = 0
        obj.foo_date_naive = DateTime('2000/01/01 00:00:00')
        obj.foo_ro = 'RO'
        obj.foo_boolean_nodel = True
        obj.foo_date_nodel = DateTime('2000/01/01 00:00:00 UTC')
        obj.foo_float_nodel = 3.1415
        obj.foo_int_nodel = 1789


class MarkerInterfaceHelpersTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.GenericSetup.utils import MarkerInterfaceHelpers

        return MarkerInterfaceHelpers

    def _makeOne(self, context=None, environ=None):
        from Products.GenericSetup.utils import NodeAdapterBase
        from Products.GenericSetup.testing import DummySetupEnviron

        class Foo(self._getTargetClass(), NodeAdapterBase):
            pass

        if context is None:
            context = self._makeContext()

        if environ is None:
            environ = DummySetupEnviron()

        return Foo(context, environ)

    def _makeContext(self):
        from OFS.SimpleItem import Item
        return Item('obj')

    def _populate(self, obj):
        from zope.interface import directlyProvides
        from Products.GenericSetup.testing import IDummyMarker
        directlyProvides(obj, IDummyMarker)

    def setUp(self):
        from zope.component import provideAdapter
        from zope.component.interface import provideInterface
        from OFS.interfaces import IItem
        from Products.Five.utilities.marker import MarkerInterfacesAdapter
        from Products.GenericSetup.testing import IDummyMarker
        provideAdapter(MarkerInterfacesAdapter, (IItem,))
        provideInterface('', IDummyMarker)

    def tearDown(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def test__extractMarkers(self):
        from Products.GenericSetup.utils import PrettyDocument
        helpers = self._makeOne()
        self._populate(helpers.context)
        doc = helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(helpers._extractMarkers())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NORMAL_MARKER_EXPORT)

    def test__purgeMarkers(self):
        from Products.GenericSetup.testing import IDummyMarker
        helpers = self._makeOne()
        obj = helpers.context
        self._populate(obj)
        self.assertTrue(IDummyMarker.providedBy(obj))

        helpers._purgeMarkers()
        self.assertFalse(IDummyMarker.providedBy(obj))

    def test__initMarkers(self):
        from Products.GenericSetup.utils import PrettyDocument
        from Products.GenericSetup.testing import IDummyMarker
        helpers = self._makeOne()
        node = _getDocumentElement(_NORMAL_MARKER_EXPORT)
        helpers._initMarkers(node)
        self.assertTrue(IDummyMarker.providedBy(helpers.context))

        doc = helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(helpers._extractMarkers())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NORMAL_MARKER_EXPORT)


class ObjectManagerHelpersTests(ZopeTestCase):

    def _getTargetClass(self):
        from Products.GenericSetup.utils import ObjectManagerHelpers

        return ObjectManagerHelpers

    def _makeOne(self, context=None, environ=None):
        from Products.GenericSetup.utils import NodeAdapterBase
        from Products.GenericSetup.testing import DummySetupEnviron

        class Foo(self._getTargetClass(), NodeAdapterBase):
            pass

        if context is None:
            context = self._makeContext()

        if environ is None:
            environ = DummySetupEnviron()

        return Foo(context, environ)

    def _makeContext(self):
        from OFS.ObjectManager import ObjectManager
        return ObjectManager('obj')

    def test__initObjects(self):
        helpers = self._makeOne()
        obj = helpers.context
        self.assertFalse('history' in obj.objectIds())

        # Add two objects
        node = _getDocumentElement(_ADD_IMPORT)
        helpers._initObjects(node)
        self.assertTrue('history' in obj.objectIds())
        self.assertTrue('future' in obj.objectIds())

        # Remove one
        node = _getDocumentElement(_REMOVE_IMPORT)
        helpers._initObjects(node)
        self.assertFalse('history' in obj.objectIds())
        self.assertTrue('future' in obj.objectIds())

        # Removing it a second time should not throw an
        # AttributeError.
        node = _getDocumentElement(_REMOVE_IMPORT)
        helpers._initObjects(node)
        self.assertFalse('history' in obj.objectIds())
        self.assertTrue('future' in obj.objectIds())


class PrettyDocumentTests(unittest.TestCase):

    def test_attr_quoting(self):
        from Products.GenericSetup.utils import PrettyDocument
        original = 'baz &nbsp;<bar>&"\''
        html_escaped = (b'<?xml version="1.0" encoding="utf-8"?>\n'
                        b'<doc bar="" foo="baz '
                        b'&amp;nbsp;&lt;bar&gt;&amp;&quot;&#x27;"/>\n')
        cgi_escaped = (b'<?xml version="1.0" encoding="utf-8"?>\n'
                       b'<doc bar="" foo="baz '
                       b'&amp;nbsp;&lt;bar&gt;&amp;&quot;\'"/>\n')

        doc = PrettyDocument()
        node = doc.createElement('doc')
        node.setAttribute('foo', original)
        node.setAttribute('bar', None)
        doc.appendChild(node)

        # Output depends on the presence of html.escape
        xml_output = doc.toprettyxml(' ')
        if HTML_ESCAPE:
            self.assertEqual(xml_output, html_escaped)
        else:
            self.assertEqual(xml_output, cgi_escaped)

        # Reparse from cgi.escape representation (Python 2 only)
        # should always work
        e = _getDocumentElement(cgi_escaped)
        self.assertEqual(e.getAttribute('foo'), original)

        # Reparse from html.escape representation (Python 3 only)
        # should always work, even without html.escape
        e = _getDocumentElement(html_escaped)
        self.assertEqual(e.getAttribute('foo'), original)

    def test_text_quoting(self):
        from Products.GenericSetup.utils import PrettyDocument
        original = 'goo &nbsp;<hmm>&"\''
        html_escaped = (b'<?xml version="1.0" encoding="utf-8"?>\n'
                        b'<doc>goo &amp;nbsp;&lt;hmm&gt;'
                        b'&amp;&quot;&#x27;</doc>\n')
        cgi_escaped = (b'<?xml version="1.0" encoding="utf-8"?>\n'
                       b'<doc>goo &amp;nbsp;&lt;hmm&gt;'
                       b'&amp;"\'</doc>\n')

        doc = PrettyDocument()
        node = doc.createElement('doc')
        child = doc.createTextNode(original)
        node.appendChild(child)
        doc.appendChild(node)

        # Output depends on the presence of html.escape
        xml_output = doc.toprettyxml(' ')
        if HTML_ESCAPE:
            self.assertEqual(xml_output, html_escaped)
        else:
            self.assertEqual(xml_output, cgi_escaped)

        # Reparse from cgi.escape representation (Python 2 only)
        # should always work
        e = _getDocumentElement(cgi_escaped)
        self.assertEqual(e.childNodes[0].nodeValue, original)

        # Reparse from html.escape representation (Python 3 only)
        # should always work, even without html.escape
        e = _getDocumentElement(html_escaped)
        self.assertEqual(e.childNodes[0].nodeValue, original)


def test_suite():
    # reimport to make sure tests are run from Products
    from Products.GenericSetup.tests.test_utils import UtilsTests

    return unittest.TestSuite((
        unittest.makeSuite(UtilsTests),
        unittest.makeSuite(PropertyManagerHelpersTests),
        unittest.makeSuite(PropertyManagerHelpersNonPMContextTests),
        unittest.makeSuite(MarkerInterfaceHelpersTests),
        unittest.makeSuite(ObjectManagerHelpersTests),
        unittest.makeSuite(PrettyDocumentTests),
    ))
