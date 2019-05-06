# -*- coding: utf-8 -*-
__filename = '/index_html'
__tokens = {56: ('template/title', 4, 24), 170: ('context/title_or_id', 9, 27), 247: ('template/title', 10, 29), 290: ('template/title', 11, 27), 386: ('template/id', 13, 43)}

from Products.PageTemplates.expression import BoboAwareZopeTraverse as _BoboAwareZopeTraverse
from sys import exc_info as _exc_info

_static_140317213873208 = {'charset': 'utf-8', }
_static_140317251270640 = _BoboAwareZopeTraverse()
_static_140317334114712 = {}

import re
import functools
from itertools import chain as __chain
__marker = object()
g_re_amp = re.compile('&(?!([A-Za-z]+|#[0-9]+);)')
g_re_needs_escape = re.compile('[&<>\\"\\\']').search
__re_whitespace = functools.partial(re.compile('\\s+').sub, ' ')

def initialize(modules, nothing, tales):

    def render(__stream, econtext, rcontext, __i18n_domain=None, __i18n_context=None):
        __append = __stream.append
        __re_amp = g_re_amp
        __token = None
        __re_needs_escape = g_re_needs_escape

        def __convert(target):
            if (target is None):
                return
            __tt = type(target)
            if ((__tt is int) or (__tt is float) or (__tt is int)):
                target = str(target)
            else:
                if (__tt is bytes):
                    target = decode(target)
                else:
                    if (__tt is not str):
                        try:
                            target = target.__html__
                        except AttributeError:
                            __converted = convert(target)
                            target = (str(target) if (target is __converted) else __converted)
                        else:
                            target = target()
            return target

        def __quote(target, quote, quote_entity, default, default_marker):
            if (target is None):
                return
            if (target is default_marker):
                return default
            __tt = type(target)
            if ((__tt is int) or (__tt is float) or (__tt is int)):
                target = str(target)
            else:
                if (__tt is bytes):
                    target = decode(target)
                else:
                    if (__tt is not str):
                        try:
                            target = target.__html__
                        except:
                            __converted = convert(target)
                            target = (str(target) if (target is __converted) else __converted)
                        else:
                            return target()
                if (target is not None):
                    try:
                        escape = (__re_needs_escape(target) is not None)
                    except TypeError:
                        pass
                    else:
                        if escape:
                            if ('&' in target):
                                target = target.replace('&', '&amp;')
                            if ('<' in target):
                                target = target.replace('<', '&lt;')
                            if ('>' in target):
                                target = target.replace('>', '&gt;')
                            if ((quote is not None) and (quote in target)):
                                target = target.replace(quote, quote_entity)
            return target
        translate = econtext['__translate']
        decode = econtext['__decode']
        convert = econtext['__convert']
        on_error_handler = econtext['__on_error_handler']
        try:
            getitem = econtext.__getitem__
            get = econtext.get
            __append('<!DOCTYPE html>')
            __append('\n')

            # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213837856
            __attrs_140317213837856 = _static_140317334114712

            # <html ... (0:0)
            # --------------------------------------------------------
            __append('<html')
            __append('>')
            __append('\n  ')

            # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213875952
            __attrs_140317213875952 = _static_140317334114712

            # <head ... (0:0)
            # --------------------------------------------------------
            __append('<head')
            __append('>')
            __append('\n    ')

            # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213874552
            __attrs_140317213874552 = _static_140317334114712

            # <title ... (0:0)
            # --------------------------------------------------------
            __append('<title')
            __append('>')
            __default_140317213875336 = '__default'

            # <Value 'template/title' (4:24)> -> __cache_140317213875616
            __token = 56
            __cache_140317213875616 = _static_140317251270640(getitem('template'), econtext, True, ('title', ))

            # <Identity expression=<Value 'template/title' (4:24)> value=<_ast.Str object at 0x7f9e25b05d30> at 7f9e25b05cf8> -> __condition
            __expression = __cache_140317213875616
            __value = '__default'
            __condition = (__expression is __value)
            if __condition:
                __append('The title')
            else:
                __content = __cache_140317213875616
                __content = __quote(__content, None, '\xad', None, None)
                if (__content is not None):
                    __append(__content)
            __append('</title>')
            __append('\n    ')

            # <Static value=<_ast.Dict object at 0x7f9e25b05438> name=None at 7f9e25b05198> -> __attrs_140317213873768
            __attrs_140317213873768 = _static_140317213873208

            # <meta ... (0:0)
            # --------------------------------------------------------
            __append('<meta')
            __append(' charset="utf-8"')
            __append(' />')
            __append('\n  ')
            __append('</head>')
            __append('\n  ')

            # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317214055000
            __attrs_140317214055000 = _static_140317334114712

            # <body ... (0:0)
            # --------------------------------------------------------
            __append('<body')
            __append('>')
            __append('\n    \n    ')

            # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317214052816
            __attrs_140317214052816 = _static_140317334114712

            # <h2 ... (0:0)
            # --------------------------------------------------------
            __append('<h2')
            __append('>')
            __default_140317214056008 = '__default'

            # <Value 'context/title_or_id' (9:27)> -> __cache_140317214056400
            __token = 170
            __cache_140317214056400 = _static_140317251270640(getitem('context'), econtext, True, ('title_or_id', ))

            # <Identity expression=<Value 'context/title_or_id' (9:27)> value=<_ast.Str object at 0x7f9e25b31f28> at 7f9e25b31d68> -> __condition
            __expression = __cache_140317214056400
            __value = '__default'
            __condition = (__expression is __value)
            if __condition:

                # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317214054496
                __attrs_140317214054496 = _static_140317334114712

                # <span ... (0:0)
                # --------------------------------------------------------
                __append('<span')
                __append('>')
                __append('content title or id')
                __append('</span>')
            else:
                __content = __cache_140317214056400
                __content = __quote(__content, None, '\xad', None, None)
                if (__content is not None):
                    __append(__content)
            __append('\n        ')

            # <Value 'template/title' (10:29)> -> __condition
            __token = 247
            __condition = _static_140317251270640(getitem('template'), econtext, True, ('title', ))
            if __condition:
                __default_140317214055616 = '__default'

                # <Value 'template/title' (11:27)> -> __cache_140317214055448
                __token = 290
                __cache_140317214055448 = _static_140317251270640(getitem('template'), econtext, True, ('title', ))

                # <Identity expression=<Value 'template/title' (11:27)> value=<_ast.Str object at 0x7f9e25b31908> at 7f9e25b31978> -> __condition
                __expression = __cache_140317214055448
                __value = '__default'
                __condition = (__expression is __value)
                if __condition:

                    # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317214055112
                    __attrs_140317214055112 = _static_140317334114712

                    # <span ... (0:0)
                    # --------------------------------------------------------
                    __append('<span')
                    __append('>')
                    __append('optional template title')
                    __append('</span>')
                else:
                    __content = __cache_140317214055448
                    __content = __quote(__content, None, '\xad', None, None)
                    if (__content is not None):
                        __append(__content)
            __append('</h2>')
            __append('\n\n    This is Page Template ')

            # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317214130696
            __attrs_140317214130696 = _static_140317334114712

            # <em ... (0:0)
            # --------------------------------------------------------
            __append('<em')
            __append('>')
            __default_140317214131424 = '__default'

            # <Value 'template/id' (13:43)> -> __cache_140317214054384
            __token = 386
            __cache_140317214054384 = _static_140317251270640(getitem('template'), econtext, True, ('id', ))

            # <Identity expression=<Value 'template/id' (13:43)> value=<_ast.Str object at 0x7f9e25b31710> at 7f9e25b316d8> -> __condition
            __expression = __cache_140317214054384
            __value = '__default'
            __condition = (__expression is __value)
            if __condition:
                __append('template id')
            else:
                __content = __cache_140317214054384
                __content = __quote(__content, None, '\xad', None, None)
                if (__content is not None):
                    __append(__content)
            __append('</em>')
            __append('.\n  ')
            __append('</body>')
            __append('\n')
            __append('</html>')
        except:
            if (__token is not None):
                rcontext.setdefault('__error__', []).append((__tokens[__token] + (__filename, _exc_info()[1], )))
            raise

    return {'render': render, }