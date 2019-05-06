##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
'''Inserting values with the 'sqlvar' tag

    The 'sqlvar' tag is used to type-safely insert values into SQL
    text.  The 'sqlvar' tag is similar to the 'var' tag, except that
    it replaces text formatting parameters with SQL type information.

    The sqlvar tag has the following attributes:

      name -- The name of the variable to insert. As with other
              DTML tags, the 'name=' prefix may be, and usually is,
              ommitted.

      type -- The data type of the value to be inserted.  This
              attribute is required and may be one of 'string',
              'int', 'float', or 'nb'.  The 'nb' data type indicates a
              string that must have a length that is greater than 0.

      optional -- A flag indicating that a value is optional.  If a
                  value is optional and is not provided (or is blank
                  when a non-blank value is expected), then the string
                  'null' is inserted.

    For example, given the tag::

      <dtml-sqlvar x type=nb optional>

    if the value of 'x' is::

      Let\'s do it

    then the text inserted is:

      'Let''s do it'

    however, if x is ommitted or an empty string, then the value
    inserted is 'null'.
'''

import six

from DocumentTemplate.DT_Util import ParseError, parse_params, name_param

StringType = str


class SQLVar:
    name = 'sqlvar'

    def __init__(self, args):
        args = parse_params(args, name='', expr='', type=None, optional=1)

        name, expr = name_param(args, 'sqlvar', 1)
        if expr is None:
            expr = name
        else:
            expr = expr.eval
        self.__name__, self.expr = name, expr

        self.args = args
        if 'type' not in args:
            raise ParseError('the type attribute is required', 'dtvar')
        t = args['type']
        if t not in valid_types:
            raise ParseError('invalid type, %s' % t, 'dtvar')

    def render(self, md):
        name = self.__name__
        args = self.args
        t = args['type']
        try:
            expr = self.expr
            if isinstance(expr, type('')):
                v = md[expr]
            else:
                v = expr(md)
        except Exception:
            if 'optional' in args and args['optional']:
                return 'null'
            if not isinstance(expr, type('')):
                raise
            raise ValueError('Missing input variable, <em>%s</em>' % name)

        if v is None:
            return 'null'

        if t == 'int':
            try:
                if isinstance(v, str):
                    if v[-1:] == 'L':
                        v = v[:-1]
                    int(v)
                else:
                    v = str(int(v))
            except Exception:
                if not v and 'optional' in args and args['optional']:
                    return 'null'
                err = 'Invalid integer value for <em>%s</em>' % name
                raise ValueError(err)
        elif t == 'float':
            try:
                if isinstance(v, str):
                    if v[-1:] == 'L':
                        v = v[:-1]
                    float(v)
                else:
                    v = str(float(v))
            except Exception:
                if not v and 'optional' in args and args['optional']:
                    return 'null'
                err = 'Invalid floating-point value for <em>%s</em>' % name
                raise ValueError(err)
        else:
            if not isinstance(v, (str, six.text_type)):
                v = str(v)
            if not v and t == 'nb':
                if 'optional' in args and args['optional']:
                    return 'null'
                else:
                    err = 'Invalid empty string value for <em>%s</em>' % name
                    raise ValueError(err)

            v = md.getitem('sql_quote__', 0)(v)
            # if v.find("\'") >= 0: v="''".join(v.split("\'"))
            # v="'%s'" % v

        return v

    __call__ = render


valid_types = {'int': 1, 'float': 1, 'string': 1, 'nb': 1}
