# -*- coding: utf-8 -*-
__filename = 'manage_main'
__tokens = {31: ('here/manage_page_header', 1, 31), 89: ('here/manage_tabs', 3, 29), 229: ("python:getattr(here.aq_explicit, 'has_order_support', 0)", 8, 38), 309: (' modules/AccessControl/SecurityManagement/getSecurityManage', 9, 22), 402: ("t python: 'position' if has_order_support else 'i", 10, 31), 477: ("ey python:request.get('skey',default_so", 11, 22), 542: ("key python:request.get('rkey','a", 12, 21), 604: ("_alt python:'desc' if rkey=='asc' else ", 13, 24), 668: ('  obs python: here.manage_get_sortedObjects(sortkey = skey, revkey =', 14, 18), 796: ('string:${request/URL1}/', 16, 31), 805: ('request/URL1', 16, 40), 853: ('obs', 18, 30), 948: ('obs', 19, 89), 1011: ("python:'thead-light sorted_%s'%(request.get('rkey',''))", 20, 57), 1441: ("python:'Sort %s by Meta-Type'%( rkey_alt.upper() )", 28, 39), 1530: (" python:'?skey=meta_type&rkey=%s'%( rkey_alt ", 29, 37), 1615: ("s python:request.get('skey',None)=='meta_type' and 'zmi-sort_key' or No", 30, 37), 1985: ("python:'Sort %s by Name'%( rkey_alt.upper() )", 38, 39), 2069: (" python:'?skey=id&rkey=%s'%( rkey_alt ", 39, 37), 2147: ("s python:request.get('skey',None)=='id' and 'zmi-sort_key' or No", 40, 37), 2826: ("python:'Sort %s by File-Size'%( rkey_alt.upper() )", 51, 39), 2915: (" python:'?skey=get_size&rkey=%s'%( rkey_alt ", 52, 37), 2999: ("s python:request.get('skey',None)=='get_size' and 'zmi-sort_key' or No", 53, 37), 3431: ("python:'Sort %s by Modification Date'%( rkey_alt.upper() )", 62, 39), 3528: (" python:'?skey=_p_mtime&rkey=%s'%( rkey_alt ", 63, 37), 3612: ("s python:request.get('skey',None)=='_p_mtime' and 'zmi-sort_key' or No", 64, 37), 3914: ('obs', 73, 34), 3952: ('nocall:ob_dict/obj', 74, 32), 4186: ('ob_dict/id', 76, 104), 4530: (' ob/meta_type | defaul', 79, 122), 4502: ('ob/zmi_icon | default', 79, 94), 4609: ('ob/meta_type | default', 80, 53), 4776: ("python:'%s/manage_workspace'%(ob_dict['quoted_id'])", 84, 40), 4867: ('ob_dict/id', 85, 37), 5000: ('ob/wl_isLocked | nothing', 86, 111), 5174: ('ob/title|nothing', 89, 74), 5239: ('ob/title', 90, 46), 5401: ('python:here.compute_size(ob)', 94, 76), 5533: ('python:here.last_modified(ob)', 96, 81), 5734: ("python:sm.checkPermission('Delete objects', context)", 104, 21), 5803: ('obs', 104, 90), 5844: ('not:context/dontAllowCopyAndPaste|nothing', 105, 35), 5848: ('context/dontAllowCopyAndPaste|nothing', 105, 39), 6107: ('delete_allowed', 107, 114), 6348: ('here/cb_dataValid', 109, 118), 6511: ('delete_allowed', 111, 115), 6658: ("python:sm.checkPermission('Import/Export objects', context)", 112, 128), 6835: ("python: has_order_support and sm.checkPermission('Manage properties', context)", 115, 64), 7387: ('python:range(1,min(5,len(obs)))', 122, 38), 7433: ('val', 122, 84), 7479: ('python:range(5,len(obs),5)', 123, 38), 7520: ('val', 123, 79), 7960: ('not:obs', 132, 26), 7964: ('obs', 132, 30), 8074: ('here/title_or_id', 134, 57), 8178: ('not:context/dontAllowCopyAndPaste|nothing', 137, 35), 8182: ('context/dontAllowCopyAndPaste|nothing', 137, 39), 8340: ('here/cb_dataValid', 138, 118), 8516: ("python:sm.checkPermission('Import/Export objects', context)", 140, 128), 11448: ('here/manage_page_footer', 237, 31)}

from Products.PageTemplates.expression import BoboAwareZopeTraverse as _BoboAwareZopeTraverse
from sys import exc_info as _exc_info
from AccessControl.ZopeGuards import guarded_getitem as _guarded_getitem
from zope.location.interfaces import LocationError as _LocationError
from zExceptions.unauthorized import Unauthorized as _Unauthorized
from zExceptions import NotFound as _NotFound
from AccessControl.cAccessControl import guarded_getattr as _guarded_getattr

_static_140317213688776 = {'class': 'zmi-typename_show', }
_static_140317213674296 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_importExportForm:method', 'value': 'Import/Export', }
_static_140317213672560 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_pasteObjects:method', 'value': 'Paste', }
_static_140317213670368 = {'class': 'form-group', }
_static_140317213668016 = {'class': 'alert alert-info mt-4 mb-4', }
_static_140317213657352 = {'type': 'submit', 'name': 'manage_move_objects_to_bottom:method', 'value': 'Move to bottom', 'class': 'btn btn-primary', 'title': 'Move selected items to bottom', }
_static_140317213642648 = {'type': 'submit', 'name': 'manage_move_objects_to_top:method', 'value': 'Move to top', 'class': 'btn btn-primary', 'title': 'Move selected items to top', }
_static_140317213626320 = {'class': 'form-control', 'name': 'delta:int', }
_static_140317213625088 = {'class': 'col-xs-2', }
_static_140317213614032 = {'type': 'submit', 'name': 'manage_move_objects_down:method', 'value': 'Move down', 'title': 'Move selected items down', 'class': 'btn btn-primary', }
_static_140317213610952 = {'type': 'submit', 'name': 'manage_move_objects_up:method', 'value': 'Move up', 'title': 'Move selected items up', 'class': 'btn btn-primary', }
_static_140317213609264 = {'class': 'form-group row zmi-controls', }
_static_140317213608088 = {'class': 'container-fluid', }
_static_140317213606184 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_importExportForm:method', 'value': 'Import/Export', }
_static_140317213595800 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_delObjects:method', 'value': 'Delete', }
_static_140317213594008 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_pasteObjects:method', 'value': 'Paste', }
_static_140317213587776 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_copyObjects:method', 'value': 'Copy', }
_static_140317213585592 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_cutObjects:method', 'value': 'Cut', }
_static_140317213562976 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_renameForm:method', 'value': 'Rename', }
_static_140317213996984 = {'class': 'form-group zmi-controls', }
_static_140317213543224 = {'class': 'text-right zmi-object-date hidden-xs pl-3', }
_static_140317213541544 = {'class': 'text-right zmi-object-size hidden-xs', }
_static_140317214054664 = {'class': 'zmi-object-title hidden-xs', }
_static_140317214053544 = {'class': 'fa fa-lock', }
_static_140317214035472 = {'class': 'badge badge-warning', 'title': 'This item has been locked by WebDAV', }
_static_140317214032784 = {'href': "python:'%s/manage_workspace'%(ob_dict['quoted_id'])", }
_static_140317214023408 = {'class': 'zmi-object-id', }
_static_140317214022232 = {'class': 'sr-only', }
_static_140317214019712 = {'title': 'Broken object', 'class': 'fas fa-ban text-danger', }
_static_140317214006016 = {'class': 'zmi-object-type', 'onclick': "$(this).prev().children('input').trigger('click')", }
_static_140317214003832 = {'type': 'checkbox', 'class': 'checkbox-list-item', 'name': 'ids:list', 'onclick': "event.stopPropagation();$(this).parent().parent().toggleClass('checked');", 'value': 'ob_dict/id', }
_static_140317213997992 = {'class': 'zmi-object-check text-right', 'onclick': "$(this).children('input').trigger('click');", }
_static_140317213982056 = {'class': 'fa fa-sort', }
_static_140317213979928 = {'title': 'Sort Ascending by Modification Date', 'href': '?skey=_p_mtime&rkey=asc', 'class': "python:request.get('skey',None)=='_p_mtime' and 'zmi-sort_key' or None", }
_static_140317213970160 = {'scope': 'col', 'class': 'zmi-object-date text-right hidden-xs', }
_static_140317213968984 = {'class': 'fa fa-sort', }
_static_140317213966800 = {'title': 'Sort Ascending by File-Size', 'href': '?skey=get_size&rkey=asc', 'class': "python:request.get('skey',None)=='get_size' and 'zmi-sort_key' or None", }
_static_140317213956976 = {'scope': 'col', 'class': 'zmi-object-size text-right hidden-xs', }
_static_140317213955072 = {'id': 'tablefilter', 'name': 'obj_ids:tokens', 'type': 'text', 'title': 'Filter object list by entering a name. Pressing the Enter key starts recursive search.', }
_static_140317213949288 = {'class': 'fa fa-search tablefilter', 'onclick': "$('#tablefilter').focus()", }
_static_140317213948112 = {'class': 'fa fa-sort', }
_static_140317213945984 = {'title': 'Sort Ascending by Name', 'href': '?skey=id&rkey=asc', 'class': "python:request.get('skey',None)=='id' and 'zmi-sort_key' or None", }
_static_140317213919832 = {'scope': 'col', 'class': 'zmi-object-id', }
_static_140317213918656 = {'class': 'fa fa-sort', }
_static_140317213916408 = {'title': 'Sort Ascending by Meta-Type', 'href': '?skey=meta_type&rkey=asc', 'class': "python:request.get('skey',None)=='meta_type' and 'zmi-sort_key' or None", }
_static_140317213914840 = {'scope': 'col', 'class': 'zmi-object-type', }
_static_140317213913216 = {'type': 'checkbox', 'id': 'checkAll', 'onclick': 'checkbox_all();', }
_static_140317213899296 = {'scope': 'col', 'class': 'zmi-object-check text-right', }
_static_140317334114712 = {}
_static_140317213896888 = {'class': 'thead-light', }
_static_140317213875112 = {'class': 'table table-striped table-hover table-sm objectItems', }
_static_140317213838360 = {'name': 'objectItems', 'method': 'post', 'action': 'string:${request/URL1}/', }
_static_140317213836960 = {'class': 'container-fluid', }
_static_140317251270640 = _BoboAwareZopeTraverse()

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
            __default_140317213835560 = '__default'

            # <Value 'here/manage_page_header' (1:31)> -> __cache_140317213835896
            __token = 31
            __cache_140317213835896 = _static_140317251270640(getitem('here'), econtext, True, ('manage_page_header', ))

            # <Identity expression=<Value 'here/manage_page_header' (1:31)> value=<_ast.Str object at 0x7f9e25afc2e8> at 7f9e25afc320> -> __condition
            __expression = __cache_140317213835896
            __value = '__default'
            __condition = (__expression is __value)
            if __condition:
                pass
            else:
                __content = __cache_140317213835896
                __content = __convert(__content)
                if (__content is not None):
                    __append(__content)
            __append('\n\n')
            __default_140317213836848 = '__default'

            # <Value 'here/manage_tabs' (3:29)> -> __cache_140317213836456
            __token = 89
            __cache_140317213836456 = _static_140317251270640(getitem('here'), econtext, True, ('manage_tabs', ))

            # <Identity expression=<Value 'here/manage_tabs' (3:29)> value=<_ast.Str object at 0x7f9e25afc518> at 7f9e25afc550> -> __condition
            __expression = __cache_140317213836456
            __value = '__default'
            __condition = (__expression is __value)
            if __condition:
                pass
            else:
                __content = __cache_140317213836456
                __content = __convert(__content)
                if (__content is not None):
                    __append(__content)
            __append('\n\n')

            # <Static value=<_ast.Dict object at 0x7f9e25afc6a0> name=None at 7f9e25afc1d0> -> __attrs_140317213837744
            __attrs_140317213837744 = _static_140317213836960

            # <main ... (0:0)
            # --------------------------------------------------------
            __append('<main')
            __append(' class="container-fluid"')
            __append('>')
            __append('\n  ')
            __backup_has_order_support_140317213835504 = get('has_order_support', __marker)

            # <Value "python:getattr(here.aq_explicit, 'has_order_support', 0)" (8:38)> -> __value
            __token = 229
            __value = get('getattr', getattr)(_guarded_getattr(getitem('here'), 'aq_explicit'), 'has_order_support', 0)
            econtext['has_order_support'] = __value
            __backup_sm_140317213835336 = get('sm', __marker)

            # <Value 'modules/AccessControl/SecurityManagement/getSecurityManager' (9:22)> -> __value
            __token = 309
            __value = _static_140317251270640(get('modules', modules), econtext, True, ('AccessControl', 'SecurityManagement', 'getSecurityManager', ))
            econtext['sm'] = __value
            __backup_default_sort_140317213835616 = get('default_sort', __marker)

            # <Value "python: 'position' if has_order_support else 'id'" (10:31)> -> __value
            __token = 402
            __value = ('position' if getitem('has_order_support') else 'id')
            econtext['default_sort'] = __value
            __backup_skey_140317213872816 = get('skey', __marker)

            # <Value "python:request.get('skey',default_sort)" (11:22)> -> __value
            __token = 477
            __value = _guarded_getattr(getitem('request'), 'get')('skey', getitem('default_sort'))
            econtext['skey'] = __value
            __backup_rkey_140317213872760 = get('rkey', __marker)

            # <Value "python:request.get('rkey','asc')" (12:21)> -> __value
            __token = 542
            __value = _guarded_getattr(getitem('request'), 'get')('rkey', 'asc')
            econtext['rkey'] = __value
            __backup_rkey_alt_140317213872928 = get('rkey_alt', __marker)

            # <Value "python:'desc' if rkey=='asc' else 'asc'" (13:24)> -> __value
            __token = 604
            __value = ('desc' if (getitem('rkey') == 'asc') else 'asc')
            econtext['rkey_alt'] = __value
            __backup_obs_140317213872984 = get('obs', __marker)

            # <Value 'python: here.manage_get_sortedObjects(sortkey = skey, revkey = rkey)' (14:18)> -> __value
            __token = 668
            __value = _guarded_getattr(getitem('here'), 'manage_get_sortedObjects')(sortkey=getitem('skey'), revkey=getitem('rkey'))
            econtext['obs'] = __value

            # <Static value=<_ast.Dict object at 0x7f9e25afcc18> name=None at 7f9e25afcbe0> -> __attrs_140317213872536
            __attrs_140317213872536 = _static_140317213838360

            # <form ... (0:0)
            # --------------------------------------------------------
            __append('<form')
            __append(' name="objectItems"')
            __append(' method="post"')
            __default_140317213839200 = '__default__'

            # <Substitution 'string:${request/URL1}/' (16:31)> -> __attr_action
            __token = 796
            __token = 805
            __attr_action = _static_140317251270640(getitem('request'), econtext, True, ('URL1', ))
            if (__attr_action is None):
                pass
            else:
                if (__attr_action is '__default__'):
                    __attr_action = None
                else:
                    __tt = type(__attr_action)
                    if ((__tt is int) or (__tt is float) or (__tt is int)):
                        __attr_action = str(__attr_action)
                    else:
                        if (__tt is bytes):
                            __attr_action = decode(__attr_action)
                        else:
                            if (__tt is not str):
                                try:
                                    __attr_action = __attr_action.__html__
                                except get('AttributeError', AttributeError):
                                    __converted = convert(__attr_action)
                                    __attr_action = (str(__attr_action) if (__attr_action is __converted) else __converted)
                                else:
                                    __attr_action = __attr_action()
            __attr_action = ('%s%s' % ((__attr_action if (__attr_action is not None) else ''), '/', ))
            __attr_action = __quote(__attr_action, '"', '&quot;', None, '__default__')
            if (__attr_action is not None):
                __append((' action="%s"' % __attr_action))
            __append('>')
            __append('\n\n    ')

            # <Value 'obs' (18:30)> -> __condition
            __token = 853
            __condition = _static_140317251270640(getitem('obs'), econtext, True, ())
            if __condition:
                __append('\n      ')

                # <Value 'obs' (19:89)> -> __condition
                __token = 948
                __condition = _static_140317251270640(getitem('obs'), econtext, True, ())
                if __condition:

                    # <Static value=<_ast.Dict object at 0x7f9e25b05ba8> name=None at 7f9e25b05b38> -> __attrs_140317213875896
                    __attrs_140317213875896 = _static_140317213875112

                    # <table ... (0:0)
                    # --------------------------------------------------------
                    __append('<table')
                    __append(' class="table table-striped table-hover table-sm objectItems"')
                    __append('>')
                    __append('\n        ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b0b0b8> name=None at 7f9e25b0b0f0> -> __attrs_140317213898064
                    __attrs_140317213898064 = _static_140317213896888

                    # <thead ... (0:0)
                    # --------------------------------------------------------
                    __append('<thead')
                    __default_140317213897560 = 'thead-light'

                    # <Substitution "python:'thead-light sorted_%s'%(request.get('rkey',''))" (20:57)> -> __attr_class
                    __token = 1011
                    __attr_class = ('thead-light sorted_%s' % _guarded_getattr(getitem('request'), 'get')('rkey', ''))
                    __attr_class = __quote(__attr_class, '"', '&quot;', 'thead-light', '__default__')
                    if (__attr_class is not None):
                        __append((' class="%s"' % __attr_class))
                    __append('>')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213898792
                    __attrs_140317213898792 = _static_140317334114712

                    # <tr ... (0:0)
                    # --------------------------------------------------------
                    __append('<tr')
                    __append('>')
                    __append('\n            ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b0ba20> name=None at 7f9e25b0b9e8> -> __attrs_140317213900360
                    __attrs_140317213900360 = _static_140317213899296

                    # <th ... (0:0)
                    # --------------------------------------------------------
                    __append('<th')
                    __append(' scope="col"')
                    __append(' class="zmi-object-check text-right"')
                    __append('>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b0f080> name=None at 7f9e25b0f048> -> __attrs_140317213914392
                    __attrs_140317213914392 = _static_140317213913216

                    # <input ... (0:0)
                    # --------------------------------------------------------
                    __append('<input')
                    __append(' type="checkbox"')
                    __append(' id="checkAll"')
                    __append(' onclick="checkbox_all();"')
                    __append(' />')
                    __append('\n            ')
                    __append('</th>')
                    __append('\n            ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b0f6d8> name=None at 7f9e25b0f6a0> -> __attrs_140317213915904
                    __attrs_140317213915904 = _static_140317213914840

                    # <th ... (0:0)
                    # --------------------------------------------------------
                    __append('<th')
                    __append(' scope="col"')
                    __append(' class="zmi-object-type"')
                    __append('>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b0fcf8> name=None at 7f9e25b0fc18> -> __attrs_140317213918264
                    __attrs_140317213918264 = _static_140317213916408

                    # <a ... (0:0)
                    # --------------------------------------------------------
                    __append('<a')
                    __default_140317213917256 = 'Sort Ascending by Meta-Type'

                    # <Substitution "python:'Sort %s by Meta-Type'%( rkey_alt.upper() )" (28:39)> -> __attr_title
                    __token = 1441
                    __attr_title = ('Sort %s by Meta-Type' % _guarded_getattr(getitem('rkey_alt'), 'upper')())
                    __attr_title = __quote(__attr_title, '"', '&quot;', 'Sort Ascending by Meta-Type', '__default__')
                    if (__attr_title is not None):
                        __append((' title="%s"' % __attr_title))
                    __default_140317213917536 = '?skey=meta_type&rkey=asc'

                    # <Substitution "python:'?skey=meta_type&rkey=%s'%( rkey_alt )" (29:37)> -> __attr_href
                    __token = 1530
                    __attr_href = ('?skey=meta_type&rkey=%s' % getitem('rkey_alt'))
                    __attr_href = __quote(__attr_href, '"', '&quot;', '?skey=meta_type&rkey=asc', '__default__')
                    if (__attr_href is not None):
                        __append((' href="%s"' % __attr_href))
                    __default_140317213917760 = '__default__'

                    # <Substitution "python:request.get('skey',None)=='meta_type' and 'zmi-sort_key' or None" (30:37)> -> __attr_class
                    __token = 1615
                    __attr_class = (((_guarded_getattr(getitem('request'), 'get')('skey', None) == 'meta_type') and 'zmi-sort_key') or None)
                    __attr_class = __quote(__attr_class, '"', '&quot;', None, '__default__')
                    if (__attr_class is not None):
                        __append((' class="%s"' % __attr_class))
                    __append('>')
                    __append('\n                ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b105c0> name=None at 7f9e25b10588> -> __attrs_140317213919440
                    __attrs_140317213919440 = _static_140317213918656

                    # <i ... (0:0)
                    # --------------------------------------------------------
                    __append('<i')
                    __append(' class="fa fa-sort"')
                    __append('>')
                    __append('</i>')
                    __append('\n              ')
                    __append('</a>')
                    __append('\n            ')
                    __append('</th>')
                    __append('\n            ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b10a58> name=None at 7f9e25b10a20> -> __attrs_140317213920896
                    __attrs_140317213920896 = _static_140317213919832

                    # <th ... (0:0)
                    # --------------------------------------------------------
                    __append('<th')
                    __append(' scope="col"')
                    __append(' class="zmi-object-id"')
                    __append('>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b17080> name=None at 7f9e25b17048> -> __attrs_140317213947720
                    __attrs_140317213947720 = _static_140317213945984

                    # <a ... (0:0)
                    # --------------------------------------------------------
                    __append('<a')
                    __default_140317213946712 = 'Sort Ascending by Name'

                    # <Substitution "python:'Sort %s by Name'%( rkey_alt.upper() )" (38:39)> -> __attr_title
                    __token = 1985
                    __attr_title = ('Sort %s by Name' % _guarded_getattr(getitem('rkey_alt'), 'upper')())
                    __attr_title = __quote(__attr_title, '"', '&quot;', 'Sort Ascending by Name', '__default__')
                    if (__attr_title is not None):
                        __append((' title="%s"' % __attr_title))
                    __default_140317213946992 = '?skey=id&rkey=asc'

                    # <Substitution "python:'?skey=id&rkey=%s'%( rkey_alt )" (39:37)> -> __attr_href
                    __token = 2069
                    __attr_href = ('?skey=id&rkey=%s' % getitem('rkey_alt'))
                    __attr_href = __quote(__attr_href, '"', '&quot;', '?skey=id&rkey=asc', '__default__')
                    if (__attr_href is not None):
                        __append((' href="%s"' % __attr_href))
                    __default_140317213947216 = '__default__'

                    # <Substitution "python:request.get('skey',None)=='id' and 'zmi-sort_key' or None" (40:37)> -> __attr_class
                    __token = 2147
                    __attr_class = (((_guarded_getattr(getitem('request'), 'get')('skey', None) == 'id') and 'zmi-sort_key') or None)
                    __attr_class = __quote(__attr_class, '"', '&quot;', None, '__default__')
                    if (__attr_class is not None):
                        __append((' class="%s"' % __attr_class))
                    __append('>')
                    __append('\n                Name\n                ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b178d0> name=None at 7f9e25b17898> -> __attrs_140317213948896
                    __attrs_140317213948896 = _static_140317213948112

                    # <i ... (0:0)
                    # --------------------------------------------------------
                    __append('<i')
                    __append(' class="fa fa-sort"')
                    __append('>')
                    __append('</i>')
                    __append('\n              ')
                    __append('</a>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b17d68> name=None at 7f9e25b17cc0> -> __attrs_140317213954512
                    __attrs_140317213954512 = _static_140317213949288

                    # <i ... (0:0)
                    # --------------------------------------------------------
                    __append('<i')
                    __append(' class="fa fa-search tablefilter"')
                    __append(' onclick="$(\'#tablefilter\').focus()"')
                    __append('>')
                    __append('</i>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b19400> name=None at 7f9e25b193c8> -> __attrs_140317213956528
                    __attrs_140317213956528 = _static_140317213955072

                    # <input ... (0:0)
                    # --------------------------------------------------------
                    __append('<input')
                    __append(' id="tablefilter"')
                    __append(' name="obj_ids:tokens"')
                    __append(' type="text"')
                    __append(' title="Filter object list by entering a name. Pressing the Enter key starts recursive search."')
                    __append(' />')
                    __append('\n            ')
                    __append('</th>')
                    __append('\n            ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b19b70> name=None at 7f9e25b19b38> -> __attrs_140317213958040
                    __attrs_140317213958040 = _static_140317213956976

                    # <th ... (0:0)
                    # --------------------------------------------------------
                    __append('<th')
                    __append(' scope="col"')
                    __append(' class="zmi-object-size text-right hidden-xs"')
                    __append('>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b1c1d0> name=None at 7f9e25b1c0f0> -> __attrs_140317213968592
                    __attrs_140317213968592 = _static_140317213966800

                    # <a ... (0:0)
                    # --------------------------------------------------------
                    __append('<a')
                    __default_140317213967584 = 'Sort Ascending by File-Size'

                    # <Substitution "python:'Sort %s by File-Size'%( rkey_alt.upper() )" (51:39)> -> __attr_title
                    __token = 2826
                    __attr_title = ('Sort %s by File-Size' % _guarded_getattr(getitem('rkey_alt'), 'upper')())
                    __attr_title = __quote(__attr_title, '"', '&quot;', 'Sort Ascending by File-Size', '__default__')
                    if (__attr_title is not None):
                        __append((' title="%s"' % __attr_title))
                    __default_140317213967864 = '?skey=get_size&rkey=asc'

                    # <Substitution "python:'?skey=get_size&rkey=%s'%( rkey_alt )" (52:37)> -> __attr_href
                    __token = 2915
                    __attr_href = ('?skey=get_size&rkey=%s' % getitem('rkey_alt'))
                    __attr_href = __quote(__attr_href, '"', '&quot;', '?skey=get_size&rkey=asc', '__default__')
                    if (__attr_href is not None):
                        __append((' href="%s"' % __attr_href))
                    __default_140317213968088 = '__default__'

                    # <Substitution "python:request.get('skey',None)=='get_size' and 'zmi-sort_key' or None" (53:37)> -> __attr_class
                    __token = 2999
                    __attr_class = (((_guarded_getattr(getitem('request'), 'get')('skey', None) == 'get_size') and 'zmi-sort_key') or None)
                    __attr_class = __quote(__attr_class, '"', '&quot;', None, '__default__')
                    if (__attr_class is not None):
                        __append((' class="%s"' % __attr_class))
                    __append('>')
                    __append('\n                Size\n                ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b1ca58> name=None at 7f9e25b1ca20> -> __attrs_140317213969768
                    __attrs_140317213969768 = _static_140317213968984

                    # <i ... (0:0)
                    # --------------------------------------------------------
                    __append('<i')
                    __append(' class="fa fa-sort"')
                    __append('>')
                    __append('</i>')
                    __append('\n              ')
                    __append('</a>')
                    __append('\n            ')
                    __append('</th>')
                    __append('\n            ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b1cef0> name=None at 7f9e25b1ceb8> -> __attrs_140317213979480
                    __attrs_140317213979480 = _static_140317213970160

                    # <th ... (0:0)
                    # --------------------------------------------------------
                    __append('<th')
                    __append(' scope="col"')
                    __append(' class="zmi-object-date text-right hidden-xs"')
                    __append('>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b1f518> name=None at 7f9e25b1f470> -> __attrs_140317213981664
                    __attrs_140317213981664 = _static_140317213979928

                    # <a ... (0:0)
                    # --------------------------------------------------------
                    __append('<a')
                    __default_140317213980656 = 'Sort Ascending by Modification Date'

                    # <Substitution "python:'Sort %s by Modification Date'%( rkey_alt.upper() )" (62:39)> -> __attr_title
                    __token = 3431
                    __attr_title = ('Sort %s by Modification Date' % _guarded_getattr(getitem('rkey_alt'), 'upper')())
                    __attr_title = __quote(__attr_title, '"', '&quot;', 'Sort Ascending by Modification Date', '__default__')
                    if (__attr_title is not None):
                        __append((' title="%s"' % __attr_title))
                    __default_140317213980936 = '?skey=_p_mtime&rkey=asc'

                    # <Substitution "python:'?skey=_p_mtime&rkey=%s'%( rkey_alt )" (63:37)> -> __attr_href
                    __token = 3528
                    __attr_href = ('?skey=_p_mtime&rkey=%s' % getitem('rkey_alt'))
                    __attr_href = __quote(__attr_href, '"', '&quot;', '?skey=_p_mtime&rkey=asc', '__default__')
                    if (__attr_href is not None):
                        __append((' href="%s"' % __attr_href))
                    __default_140317213981160 = '__default__'

                    # <Substitution "python:request.get('skey',None)=='_p_mtime' and 'zmi-sort_key' or None" (64:37)> -> __attr_class
                    __token = 3612
                    __attr_class = (((_guarded_getattr(getitem('request'), 'get')('skey', None) == '_p_mtime') and 'zmi-sort_key') or None)
                    __attr_class = __quote(__attr_class, '"', '&quot;', None, '__default__')
                    if (__attr_class is not None):
                        __append((' class="%s"' % __attr_class))
                    __append('>')
                    __append('\n                Last Modified\n                ')

                    # <Static value=<_ast.Dict object at 0x7f9e25b1fd68> name=None at 7f9e25b1fd30> -> __attrs_140317213995192
                    __attrs_140317213995192 = _static_140317213982056

                    # <i ... (0:0)
                    # --------------------------------------------------------
                    __append('<i')
                    __append(' class="fa fa-sort"')
                    __append('>')
                    __append('</i>')
                    __append('\n              ')
                    __append('</a>')
                    __append('\n            ')
                    __append('</th>')
                    __append('\n          ')
                    __append('</tr>')
                    __append('\n        ')
                    __append('</thead>')
                    __append('\n        ')

                    # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213995808
                    __attrs_140317213995808 = _static_140317334114712

                    # <tbody ... (0:0)
                    # --------------------------------------------------------
                    __append('<tbody')
                    __append('>')
                    __append('\n          ')
                    __backup_ob_dict_140317213874832 = get('ob_dict', __marker)

                    # <Value 'obs' (73:34)> -> __iterator
                    __token = 3914
                    __iterator = _static_140317251270640(getitem('obs'), econtext, True, ())
                    (__iterator, ____index_140317213996704, ) = getitem('repeat')('ob_dict', __iterator)
                    econtext['ob_dict'] = None
                    for __item in __iterator:
                        econtext['ob_dict'] = __item

                        # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213996536
                        __attrs_140317213996536 = _static_140317334114712

                        # <tr ... (0:0)
                        # --------------------------------------------------------
                        __append('<tr')
                        __append('>')
                        __append('\n            ')
                        __backup_ob_140317213896776 = get('ob', __marker)

                        # <Value 'nocall:ob_dict/obj' (74:32)> -> __value
                        __token = 3952
                        __value = _static_140317251270640(getitem('ob_dict'), econtext, False, ('obj', ))
                        econtext['ob'] = __value
                        __append('\n              ')

                        # <Static value=<_ast.Dict object at 0x7f9e25b23ba8> name=None at 7f9e25b23b00> -> __attrs_140317213999056
                        __attrs_140317213999056 = _static_140317213997992

                        # <td ... (0:0)
                        # --------------------------------------------------------
                        __append('<td')
                        __append(' class="zmi-object-check text-right"')
                        __append(' onclick="$(this).children(\'input\').trigger(\'click\');"')
                        __append('>')
                        __append('\n                ')

                        # <Static value=<_ast.Dict object at 0x7f9e25b25278> name=None at 7f9e25b25128> -> __attrs_140317214005624
                        __attrs_140317214005624 = _static_140317214003832

                        # <input ... (0:0)
                        # --------------------------------------------------------
                        __append('<input')
                        __append(' type="checkbox"')
                        __append(' class="checkbox-list-item"')
                        __append(' name="ids:list"')
                        __append(' onclick="event.stopPropagation();$(this).parent().parent().toggleClass(\'checked\');"')
                        __default_140317214005288 = '__default__'

                        # <Substitution 'ob_dict/id' (76:104)> -> __attr_value
                        __token = 4186
                        __attr_value = _static_140317251270640(getitem('ob_dict'), econtext, True, ('id', ))
                        __attr_value = __quote(__attr_value, '"', '&quot;', None, '__default__')
                        if (__attr_value is not None):
                            __append((' value="%s"' % __attr_value))
                        __append(' />')
                        __append('\n              ')
                        __append('</td>')
                        __append('\n              ')

                        # <Static value=<_ast.Dict object at 0x7f9e25b25b00> name=None at 7f9e25b25ac8> -> __attrs_140317214007080
                        __attrs_140317214007080 = _static_140317214006016

                        # <td ... (0:0)
                        # --------------------------------------------------------
                        __append('<td')
                        __append(' class="zmi-object-type"')
                        __append(' onclick="$(this).prev().children(\'input\').trigger(\'click\')"')
                        __append('>')
                        __append('\n                ')

                        # <Static value=<_ast.Dict object at 0x7f9e25b29080> name=None at 7f9e25b290b8> -> __attrs_140317214021280
                        __attrs_140317214021280 = _static_140317214019712

                        # <i ... (0:0)
                        # --------------------------------------------------------
                        __append('<i')
                        __default_140317214020440 = 'Broken object'

                        # <Substitution 'ob/meta_type | default' (79:122)> -> __attr_title
                        __token = 4530
                        try:
                            __attr_title = _static_140317251270640(getitem('ob'), econtext, True, ('meta_type', ))
                        except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                            __attr_title = _static_140317251270640(__default_140317214020440, econtext, True, ())

                        __attr_title = __quote(__attr_title, '"', '&quot;', 'Broken object', '__default__')
                        if (__attr_title is not None):
                            __append((' title="%s"' % __attr_title))
                        __default_140317214020776 = 'fas fa-ban text-danger'

                        # <Substitution 'ob/zmi_icon | default' (79:94)> -> __attr_class
                        __token = 4502
                        try:
                            __attr_class = _static_140317251270640(getitem('ob'), econtext, True, ('zmi_icon', ))
                        except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                            __attr_class = _static_140317251270640(__default_140317214020776, econtext, True, ())

                        __attr_class = __quote(__attr_class, '"', '&quot;', 'fas fa-ban text-danger', '__default__')
                        if (__attr_class is not None):
                            __append((' class="%s"' % __attr_class))
                        __append('>')
                        __append('\n                  ')

                        # <Static value=<_ast.Dict object at 0x7f9e25b29a58> name=None at 7f9e25b29a20> -> __attrs_140317214023016
                        __attrs_140317214023016 = _static_140317214022232

                        # <span ... (0:0)
                        # --------------------------------------------------------
                        __append('<span')
                        __append(' class="sr-only"')
                        __append('>')
                        __default_140317214021952 = '__default'

                        # <Value 'ob/meta_type | default' (80:53)> -> __cache_140317214021560
                        __token = 4609
                        try:
                            __cache_140317214021560 = _static_140317251270640(getitem('ob'), econtext, True, ('meta_type', ))
                        except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                            __cache_140317214021560 = _static_140317251270640(__default_140317214021952, econtext, True, ())


                        # <Identity expression=<Value 'ob/meta_type | default' (80:53)> value=<_ast.Str object at 0x7f9e25b29828> at 7f9e25b29860> -> __condition
                        __expression = __cache_140317214021560
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:
                            __append('Broken object')
                        else:
                            __content = __cache_140317214021560
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('</span>')
                        __append('\n                ')
                        __append('</i>')
                        __append('\n              ')
                        __append('</td>')
                        __append('\n              ')

                        # <Static value=<_ast.Dict object at 0x7f9e25b29ef0> name=None at 7f9e25b29eb8> -> __attrs_140317214032448
                        __attrs_140317214032448 = _static_140317214023408

                        # <td ... (0:0)
                        # --------------------------------------------------------
                        __append('<td')
                        __append(' class="zmi-object-id"')
                        __append('>')
                        __append('\n                ')

                        # <Static value=<_ast.Dict object at 0x7f9e25b2c390> name=None at 7f9e25b2c358> -> __attrs_140317214033792
                        __attrs_140317214033792 = _static_140317214032784

                        # <a ... (0:0)
                        # --------------------------------------------------------
                        __append('<a')
                        __default_140317214033288 = '__default__'

                        # <Substitution "python:'%s/manage_workspace'%(ob_dict['quoted_id'])" (84:40)> -> __attr_href
                        __token = 4776
                        __attr_href = ('%s/manage_workspace' % _guarded_getitem(getitem('ob_dict'), 'quoted_id'))
                        __attr_href = __quote(__attr_href, '"', '&quot;', None, '__default__')
                        if (__attr_href is not None):
                            __append((' href="%s"' % __attr_href))
                        __append('>')
                        __append('\n                  ')
                        __default_140317214035024 = '__default'

                        # <Value 'ob_dict/id' (85:37)> -> __cache_140317214034632
                        __token = 4867
                        __cache_140317214034632 = _static_140317251270640(getitem('ob_dict'), econtext, True, ('id', ))

                        # <Identity expression=<Value 'ob_dict/id' (85:37)> value=<_ast.Str object at 0x7f9e25b2cb38> at 7f9e25b2cb70> -> __condition
                        __expression = __cache_140317214034632
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:

                            # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317214034520
                            __attrs_140317214034520 = _static_140317334114712

                            # <span ... (0:0)
                            # --------------------------------------------------------
                            __append('<span')
                            __append('>')
                            __append('Id')
                            __append('</span>')
                        else:
                            __content = __cache_140317214034632
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('\n                  ')

                        # <Value 'ob/wl_isLocked | nothing' (86:111)> -> __condition
                        __token = 5000
                        try:
                            __condition = _static_140317251270640(getitem('ob'), econtext, True, ('wl_isLocked', ))
                        except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                            __condition = _static_140317251270640(get('nothing', nothing), econtext, True, ())

                        if __condition:

                            # <Static value=<_ast.Dict object at 0x7f9e25b2ce10> name=None at 7f9e25b2cd68> -> __attrs_140317214052984
                            __attrs_140317214052984 = _static_140317214035472

                            # <span ... (0:0)
                            # --------------------------------------------------------
                            __append('<span')
                            __append(' class="badge badge-warning"')
                            __append(' title="This item has been locked by WebDAV"')
                            __append('>')
                            __append('\n                    ')

                            # <Static value=<_ast.Dict object at 0x7f9e25b314a8> name=None at 7f9e25b31470> -> __attrs_140317214054328
                            __attrs_140317214054328 = _static_140317214053544

                            # <i ... (0:0)
                            # --------------------------------------------------------
                            __append('<i')
                            __append(' class="fa fa-lock"')
                            __append('>')
                            __append('</i>')
                            __append('\n                  ')
                            __append('</span>')
                        __append('\n                  ')

                        # <Value 'ob/title|nothing' (89:74)> -> __condition
                        __token = 5174
                        try:
                            __condition = _static_140317251270640(getitem('ob'), econtext, True, ('title', ))
                        except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                            __condition = _static_140317251270640(get('nothing', nothing), econtext, True, ())

                        if __condition:

                            # <Static value=<_ast.Dict object at 0x7f9e25b31908> name=None at 7f9e25b318d0> -> __attrs_140317214055448
                            __attrs_140317214055448 = _static_140317214054664

                            # <span ... (0:0)
                            # --------------------------------------------------------
                            __append('<span')
                            __append(' class="zmi-object-title hidden-xs"')
                            __append('>')
                            __append('\n                    &nbsp;(')
                            __default_140317213540760 = '__default'

                            # <Value 'ob/title' (90:46)> -> __cache_140317214056400
                            __token = 5239
                            __cache_140317214056400 = _static_140317251270640(getitem('ob'), econtext, True, ('title', ))

                            # <Identity expression=<Value 'ob/title' (90:46)> value=<_ast.Str object at 0x7f9e25ab4080> at 7f9e25ab40b8> -> __condition
                            __expression = __cache_140317214056400
                            __value = '__default'
                            __condition = (__expression is __value)
                            if __condition:

                                # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317214056288
                                __attrs_140317214056288 = _static_140317334114712

                                # <span ... (0:0)
                                # --------------------------------------------------------
                                __append('<span')
                                __append('>')
                                __append('</span>')
                            else:
                                __content = __cache_140317214056400
                                __content = __quote(__content, None, '\xad', None, None)
                                if (__content is not None):
                                    __append(__content)
                            __append(')\n                  ')
                            __append('</span>')
                        __append('\n                ')
                        __append('</a>')
                        __append('\n              ')
                        __append('</td>')
                        __append('\n              ')

                        # <Static value=<_ast.Dict object at 0x7f9e25ab44a8> name=None at 7f9e25ab4470> -> __attrs_140317213542328
                        __attrs_140317213542328 = _static_140317213541544

                        # <td ... (0:0)
                        # --------------------------------------------------------
                        __append('<td')
                        __append(' class="text-right zmi-object-size hidden-xs"')
                        __append('>')
                        __default_140317213541320 = '__default'

                        # <Value 'python:here.compute_size(ob)' (94:76)> -> __cache_140317213540928
                        __token = 5401
                        __cache_140317213540928 = _guarded_getattr(getitem('here'), 'compute_size')(getitem('ob'))

                        # <Identity expression=<Value 'python:here.compute_size(ob)' (94:76)> value=<_ast.Str object at 0x7f9e25ab42b0> at 7f9e25ab42e8> -> __condition
                        __expression = __cache_140317213540928
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:
                            __append('\n              ')
                        else:
                            __content = __cache_140317213540928
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('</td>')
                        __append('\n              ')

                        # <Static value=<_ast.Dict object at 0x7f9e25ab4b38> name=None at 7f9e25ab4b00> -> __attrs_140317213544008
                        __attrs_140317213544008 = _static_140317213543224

                        # <td ... (0:0)
                        # --------------------------------------------------------
                        __append('<td')
                        __append(' class="text-right zmi-object-date hidden-xs pl-3"')
                        __append('>')
                        __default_140317213543000 = '__default'

                        # <Value 'python:here.last_modified(ob)' (96:81)> -> __cache_140317213542608
                        __token = 5533
                        __cache_140317213542608 = _guarded_getattr(getitem('here'), 'last_modified')(getitem('ob'))

                        # <Identity expression=<Value 'python:here.last_modified(ob)' (96:81)> value=<_ast.Str object at 0x7f9e25ab4940> at 7f9e25ab4978> -> __condition
                        __expression = __cache_140317213542608
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:
                            __append('\n              ')
                        else:
                            __content = __cache_140317213542608
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('</td>')
                        __append('\n            ')
                        if (__backup_ob_140317213896776 is __marker):
                            del econtext['ob']
                        else:
                            econtext['ob'] = __backup_ob_140317213896776
                        __append('\n          ')
                        __append('</tr>')
                        ____index_140317213996704 -= 1
                        if (____index_140317213996704 > 0):
                            __append('\n          ')
                    if (__backup_ob_dict_140317213874832 is __marker):
                        del econtext['ob_dict']
                    else:
                        econtext['ob_dict'] = __backup_ob_dict_140317213874832
                    __append('\n        ')
                    __append('</tbody>')
                    __append('\n      ')
                    __append('</table>')
                __append('\n\n      ')
                __backup_delete_allowed_140317213873096 = get('delete_allowed', __marker)

                # <Value "python:sm.checkPermission('Delete objects', context)" (104:21)> -> __value
                __token = 5734
                __value = _guarded_getattr(getitem('sm'), 'checkPermission')('Delete objects', getitem('context'))
                econtext['delete_allowed'] = __value

                # <Value 'obs' (104:90)> -> __condition
                __token = 5803
                __condition = _static_140317251270640(getitem('obs'), econtext, True, ())
                if __condition:

                    # <Static value=<_ast.Dict object at 0x7f9e25b237b8> name=None at 7f9e25b23860> -> __attrs_140317213561240
                    __attrs_140317213561240 = _static_140317213996984

                    # <div ... (0:0)
                    # --------------------------------------------------------
                    __append('<div')
                    __append(' class="form-group zmi-controls"')
                    __append('>')
                    __append('\n        ')

                    # <Value 'not:context/dontAllowCopyAndPaste|nothing' (105:35)> -> __condition
                    __token = 5844
                    __token = 5848
                    try:
                        __condition = _static_140317251270640(getitem('context'), econtext, True, ('dontAllowCopyAndPaste', ))
                    except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                        __condition = _static_140317251270640(get('nothing', nothing), econtext, True, ())

                    __condition = not __condition
                    if __condition:
                        __append('\n          ')

                        # <Static value=<_ast.Dict object at 0x7f9e25ab9860> name=None at 7f9e25ab9828> -> __attrs_140317213564432
                        __attrs_140317213564432 = _static_140317213562976

                        # <input ... (0:0)
                        # --------------------------------------------------------
                        __append('<input')
                        __append(' class="btn btn-primary"')
                        __append(' type="submit"')
                        __append(' name="manage_renameForm:method"')
                        __append(' value="Rename"')
                        __append(' />')
                        __append('\n          ')

                        # <Value 'delete_allowed' (107:114)> -> __condition
                        __token = 6107
                        __condition = _static_140317251270640(getitem('delete_allowed'), econtext, True, ())
                        if __condition:

                            # <Static value=<_ast.Dict object at 0x7f9e25abf0b8> name=None at 7f9e25abf080> -> __attrs_140317213587048
                            __attrs_140317213587048 = _static_140317213585592

                            # <input ... (0:0)
                            # --------------------------------------------------------
                            __append('<input')
                            __append(' class="btn btn-primary"')
                            __append(' type="submit"')
                            __append(' name="manage_cutObjects:method"')
                            __append(' value="Cut"')
                            __append(' />')
                        __append('\n          ')

                        # <Static value=<_ast.Dict object at 0x7f9e25abf940> name=None at 7f9e25abf908> -> __attrs_140317213589232
                        __attrs_140317213589232 = _static_140317213587776

                        # <input ... (0:0)
                        # --------------------------------------------------------
                        __append('<input')
                        __append(' class="btn btn-primary"')
                        __append(' type="submit"')
                        __append(' name="manage_copyObjects:method"')
                        __append(' value="Copy"')
                        __append(' />')
                        __append('\n          ')

                        # <Value 'here/cb_dataValid' (109:118)> -> __condition
                        __token = 6348
                        __condition = _static_140317251270640(getitem('here'), econtext, True, ('cb_dataValid', ))
                        if __condition:

                            # <Static value=<_ast.Dict object at 0x7f9e25ac1198> name=None at 7f9e25ac1160> -> __attrs_140317213595464
                            __attrs_140317213595464 = _static_140317213594008

                            # <input ... (0:0)
                            # --------------------------------------------------------
                            __append('<input')
                            __append(' class="btn btn-primary"')
                            __append(' type="submit"')
                            __append(' name="manage_pasteObjects:method"')
                            __append(' value="Paste"')
                            __append(' />')
                        __append('\n        ')
                    __append('\n        ')

                    # <Value 'delete_allowed' (111:115)> -> __condition
                    __token = 6511
                    __condition = _static_140317251270640(getitem('delete_allowed'), econtext, True, ())
                    if __condition:

                        # <Static value=<_ast.Dict object at 0x7f9e25ac1898> name=None at 7f9e25ac1860> -> __attrs_140317213597256
                        __attrs_140317213597256 = _static_140317213595800

                        # <input ... (0:0)
                        # --------------------------------------------------------
                        __append('<input')
                        __append(' class="btn btn-primary"')
                        __append(' type="submit"')
                        __append(' name="manage_delObjects:method"')
                        __append(' value="Delete"')
                        __append(' />')
                    __append('\n        ')

                    # <Value "python:sm.checkPermission('Import/Export objects', context)" (112:128)> -> __condition
                    __token = 6658
                    __condition = _guarded_getattr(getitem('sm'), 'checkPermission')('Import/Export objects', getitem('context'))
                    if __condition:

                        # <Static value=<_ast.Dict object at 0x7f9e25ac4128> name=None at 7f9e25ac40f0> -> __attrs_140317213607640
                        __attrs_140317213607640 = _static_140317213606184

                        # <input ... (0:0)
                        # --------------------------------------------------------
                        __append('<input')
                        __append(' class="btn btn-primary"')
                        __append(' type="submit"')
                        __append(' name="manage_importExportForm:method"')
                        __append(' value="Import/Export"')
                        __append(' />')
                    __append('\n      ')
                    __append('</div>')
                if (__backup_delete_allowed_140317213873096 is __marker):
                    del econtext['delete_allowed']
                else:
                    econtext['delete_allowed'] = __backup_delete_allowed_140317213873096
                __append('\n      ')

                # <Static value=<_ast.Dict object at 0x7f9e25ac4898> name=None at 7f9e25ac4860> -> __attrs_140317213608872
                __attrs_140317213608872 = _static_140317213608088

                # <div ... (0:0)
                # --------------------------------------------------------
                __append('<div')
                __append(' class="container-fluid"')
                __append('>')
                __append('\n        ')

                # <Value "python: has_order_support and sm.checkPermission('Manage properties', context)" (115:64)> -> __condition
                __token = 6835
                __condition = (getitem('has_order_support') and _guarded_getattr(getitem('sm'), 'checkPermission')('Manage properties', getitem('context')))
                if __condition:

                    # <Static value=<_ast.Dict object at 0x7f9e25ac4d30> name=None at 7f9e25ac4cf8> -> __attrs_140317213610112
                    __attrs_140317213610112 = _static_140317213609264

                    # <div ... (0:0)
                    # --------------------------------------------------------
                    __append('<div')
                    __append(' class="form-group row zmi-controls"')
                    __append('>')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f9e25ac53c8> name=None at 7f9e25ac5390> -> __attrs_140317213612688
                    __attrs_140317213612688 = _static_140317213610952

                    # <input ... (0:0)
                    # --------------------------------------------------------
                    __append('<input')
                    __append(' type="submit"')
                    __append(' name="manage_move_objects_up:method"')
                    __append(' value="Move up"')
                    __append(' title="Move selected items up"')
                    __append(' class="btn btn-primary"')
                    __append(' />')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213613360
                    __attrs_140317213613360 = _static_140317334114712

                    # <span ... (0:0)
                    # --------------------------------------------------------
                    __append('<span')
                    __append('>')
                    __append('/')
                    __append('</span>')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f9e25ac5fd0> name=None at 7f9e25ac5f98> -> __attrs_140317213624024
                    __attrs_140317213624024 = _static_140317213614032

                    # <input ... (0:0)
                    # --------------------------------------------------------
                    __append('<input')
                    __append(' type="submit"')
                    __append(' name="manage_move_objects_down:method"')
                    __append(' value="Move down"')
                    __append(' title="Move selected items down"')
                    __append(' class="btn btn-primary"')
                    __append(' />')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213624696
                    __attrs_140317213624696 = _static_140317334114712

                    # <span ... (0:0)
                    # --------------------------------------------------------
                    __append('<span')
                    __append('>')
                    __append('by')
                    __append('</span>')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f9e25ac8b00> name=None at 7f9e25ac8ac8> -> __attrs_140317213625872
                    __attrs_140317213625872 = _static_140317213625088

                    # <div ... (0:0)
                    # --------------------------------------------------------
                    __append('<div')
                    __append(' class="col-xs-2"')
                    __append('>')
                    __append('\n            ')

                    # <Static value=<_ast.Dict object at 0x7f9e25ac8fd0> name=None at 7f9e25ac8f28> -> __attrs_140317213639736
                    __attrs_140317213639736 = _static_140317213626320

                    # <select ... (0:0)
                    # --------------------------------------------------------
                    __append('<select')
                    __append(' class="form-control"')
                    __append(' name="delta:int"')
                    __append('>')
                    __append('\n              ')
                    __backup_val_140317213997712 = get('val', __marker)

                    # <Value 'python:range(1,min(5,len(obs)))' (122:38)> -> __iterator
                    __token = 7387
                    __iterator = get('range', range)(1, get('min', min)(5, len(getitem('obs'))))
                    (__iterator, ____index_140317213640968, ) = getitem('repeat')('val', __iterator)
                    econtext['val'] = None
                    for __item in __iterator:
                        econtext['val'] = __item

                        # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213640800
                        __attrs_140317213640800 = _static_140317334114712

                        # <option ... (0:0)
                        # --------------------------------------------------------
                        __append('<option')
                        __append('>')
                        __default_140317213640408 = '__default'

                        # <Value 'val' (122:84)> -> __cache_140317213640016
                        __token = 7433
                        __cache_140317213640016 = _static_140317251270640(getitem('val'), econtext, True, ())

                        # <Identity expression=<Value 'val' (122:84)> value=<_ast.Str object at 0x7f9e25acc5c0> at 7f9e25acc5f8> -> __condition
                        __expression = __cache_140317213640016
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:
                            pass
                        else:
                            __content = __cache_140317213640016
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('</option>')
                        ____index_140317213640968 -= 1
                        if (____index_140317213640968 > 0):
                            __append('\n              ')
                    if (__backup_val_140317213997712 is __marker):
                        del econtext['val']
                    else:
                        econtext['val'] = __backup_val_140317213997712
                    __append('\n              ')
                    __backup_val_140317213997432 = get('val', __marker)

                    # <Value 'python:range(5,len(obs),5)' (123:38)> -> __iterator
                    __token = 7479
                    __iterator = get('range', range)(5, len(getitem('obs')), 5)
                    (__iterator, ____index_140317213642088, ) = getitem('repeat')('val', __iterator)
                    econtext['val'] = None
                    for __item in __iterator:
                        econtext['val'] = __item

                        # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213641920
                        __attrs_140317213641920 = _static_140317334114712

                        # <option ... (0:0)
                        # --------------------------------------------------------
                        __append('<option')
                        __append('>')
                        __default_140317213641528 = '__default'

                        # <Value 'val' (123:79)> -> __cache_140317213641136
                        __token = 7520
                        __cache_140317213641136 = _static_140317251270640(getitem('val'), econtext, True, ())

                        # <Identity expression=<Value 'val' (123:79)> value=<_ast.Str object at 0x7f9e25acca20> at 7f9e25acca58> -> __condition
                        __expression = __cache_140317213641136
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:
                            pass
                        else:
                            __content = __cache_140317213641136
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('</option>')
                        ____index_140317213642088 -= 1
                        if (____index_140317213642088 > 0):
                            __append('\n              ')
                    if (__backup_val_140317213997432 is __marker):
                        del econtext['val']
                    else:
                        econtext['val'] = __backup_val_140317213997432
                    __append('\n            ')
                    __append('</select>')
                    __append('\n          ')
                    __append('</div>')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f9e25accf98> name=None at 7f9e25accf60> -> __attrs_140317213656736
                    __attrs_140317213656736 = _static_140317213642648

                    # <input ... (0:0)
                    # --------------------------------------------------------
                    __append('<input')
                    __append(' type="submit"')
                    __append(' name="manage_move_objects_to_top:method"')
                    __append(' value="Move to top"')
                    __append(' class="btn btn-primary"')
                    __append(' title="Move selected items to top"')
                    __append(' />')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f9e25ad0908> name=None at 7f9e25ad08d0> -> __attrs_140317213659088
                    __attrs_140317213659088 = _static_140317213657352

                    # <input ... (0:0)
                    # --------------------------------------------------------
                    __append('<input')
                    __append(' type="submit"')
                    __append(' name="manage_move_objects_to_bottom:method"')
                    __append(' value="Move to bottom"')
                    __append(' class="btn btn-primary"')
                    __append(' title="Move selected items to bottom"')
                    __append(' />')
                    __append('\n        ')
                    __append('</div>')
                __append('\n      ')
                __append('</div>')
                __append('\n    ')
            __append('\n\n    ')

            # <Value 'not:obs' (132:26)> -> __condition
            __token = 7960
            __token = 7964
            __condition = _static_140317251270640(getitem('obs'), econtext, True, ())
            __condition = not __condition
            if __condition:
                __append('\n      ')

                # <Static value=<_ast.Dict object at 0x7f9e25ad32b0> name=None at 7f9e25ad3278> -> __attrs_140317213668800
                __attrs_140317213668800 = _static_140317213668016

                # <div ... (0:0)
                # --------------------------------------------------------
                __append('<div')
                __append(' class="alert alert-info mt-4 mb-4"')
                __append('>')
                __append('\n        There are currently no items in ')

                # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213670032
                __attrs_140317213670032 = _static_140317334114712

                # <em ... (0:0)
                # --------------------------------------------------------
                __append('<em')
                __append('>')
                __default_140317213669472 = '__default'

                # <Value 'here/title_or_id' (134:57)> -> __cache_140317213669080
                __token = 8074
                __cache_140317213669080 = _static_140317251270640(getitem('here'), econtext, True, ('title_or_id', ))

                # <Identity expression=<Value 'here/title_or_id' (134:57)> value=<_ast.Str object at 0x7f9e25ad3748> at 7f9e25ad3780> -> __condition
                __expression = __cache_140317213669080
                __value = '__default'
                __condition = (__expression is __value)
                if __condition:
                    pass
                else:
                    __content = __cache_140317213669080
                    __content = __quote(__content, None, '\xad', None, None)
                    if (__content is not None):
                        __append(__content)
                __append('</em>')
                __append('.\n      ')
                __append('</div>')
                __append('\n      ')

                # <Static value=<_ast.Dict object at 0x7f9e25ad3be0> name=None at 7f9e25ad3ba8> -> __attrs_140317213671152
                __attrs_140317213671152 = _static_140317213670368

                # <div ... (0:0)
                # --------------------------------------------------------
                __append('<div')
                __append(' class="form-group"')
                __append('>')
                __append('\n        ')

                # <Value 'not:context/dontAllowCopyAndPaste|nothing' (137:35)> -> __condition
                __token = 8178
                __token = 8182
                try:
                    __condition = _static_140317251270640(getitem('context'), econtext, True, ('dontAllowCopyAndPaste', ))
                except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                    __condition = _static_140317251270640(get('nothing', nothing), econtext, True, ())

                __condition = not __condition
                if __condition:
                    __append('\n          ')

                    # <Value 'here/cb_dataValid' (138:118)> -> __condition
                    __token = 8340
                    __condition = _static_140317251270640(getitem('here'), econtext, True, ('cb_dataValid', ))
                    if __condition:

                        # <Static value=<_ast.Dict object at 0x7f9e25ad4470> name=None at 7f9e25ad4438> -> __attrs_140317213674016
                        __attrs_140317213674016 = _static_140317213672560

                        # <input ... (0:0)
                        # --------------------------------------------------------
                        __append('<input')
                        __append(' class="btn btn-primary"')
                        __append(' type="submit"')
                        __append(' name="manage_pasteObjects:method"')
                        __append(' value="Paste"')
                        __append(' />')
                    __append('\n        ')
                __append('\n        ')

                # <Value "python:sm.checkPermission('Import/Export objects', context)" (140:128)> -> __condition
                __token = 8516
                __condition = _guarded_getattr(getitem('sm'), 'checkPermission')('Import/Export objects', getitem('context'))
                if __condition:

                    # <Static value=<_ast.Dict object at 0x7f9e25ad4b38> name=None at 7f9e25ad4208> -> __attrs_140317213688104
                    __attrs_140317213688104 = _static_140317213674296

                    # <input ... (0:0)
                    # --------------------------------------------------------
                    __append('<input')
                    __append(' class="btn btn-primary"')
                    __append(' type="submit"')
                    __append(' name="manage_importExportForm:method"')
                    __append(' value="Import/Export"')
                    __append(' />')
                __append('\n      ')
                __append('</div>')
                __append('\n    ')
            __append('\n  ')
            __append('</form>')
            if (__backup_has_order_support_140317213835504 is __marker):
                del econtext['has_order_support']
            else:
                econtext['has_order_support'] = __backup_has_order_support_140317213835504
            if (__backup_sm_140317213835336 is __marker):
                del econtext['sm']
            else:
                econtext['sm'] = __backup_sm_140317213835336
            if (__backup_default_sort_140317213835616 is __marker):
                del econtext['default_sort']
            else:
                econtext['default_sort'] = __backup_default_sort_140317213835616
            if (__backup_skey_140317213872816 is __marker):
                del econtext['skey']
            else:
                econtext['skey'] = __backup_skey_140317213872816
            if (__backup_rkey_140317213872760 is __marker):
                del econtext['rkey']
            else:
                econtext['rkey'] = __backup_rkey_140317213872760
            if (__backup_rkey_alt_140317213872928 is __marker):
                del econtext['rkey_alt']
            else:
                econtext['rkey_alt'] = __backup_rkey_alt_140317213872928
            if (__backup_obs_140317213872984 is __marker):
                del econtext['obs']
            else:
                econtext['obs'] = __backup_obs_140317213872984
            __append('\n')
            __append('</main>')
            __append('\n\n\n')

            # <Static value=<_ast.Dict object at 0x7f9e2cdb1198> name=None at 7f9e2cdb14e0> -> __attrs_140317213667624
            __attrs_140317213667624 = _static_140317334114712

            # <script ... (0:0)
            # --------------------------------------------------------
            __append('<script')
            __append('>')
            __append("\n  // +++++++++++++++++++++++++++\n  // checkbox_all: Item  Selection\n  // +++++++++++++++++++++++++++\n  function checkbox_all() {\n    var checkboxes = document.getElementsByClassName('checkbox-list-item');\n    // Toggle Highlighting CSS-Class\n    if (document.getElementById('checkAll').checked) {\n      $('table.objectItems tbody tr').addClass('checked');\n    } else {\n      $('table.objectItems tbody tr').removeClass('checked');\n    };\n    // Set Checkbox like checkAll-Box\n    for (i = 0; i ")
            __append('<')
            __append(' checkboxes.length; i++) {\n      checkboxes[i].checked = document.getElementById(\'checkAll\').checked;\n    }\n  };\n\n\n  $(function () {\n\n    // +++++++++++++++++++++++++++\n    // Icon Tooltips\n    // +++++++++++++++++++++++++++\n    $(\'td.zmi-object-type i\').tooltip({\n      \'placement\': \'top\'\n    });\n\n    // +++++++++++++++++++++++++++\n    // Tablefilter/Search Element\n    // +++++++++++++++++++++++++++\n\n    function isModifierKeyPressed(event) {\n      return event.altKey ||\n        event.ctrlKey ||\n        event.metaKey;\n    }\n\n    $(document).keypress(function (event) {\n\n      if (isModifierKeyPressed(event)) {\n        return; // ignore\n      }\n\n      // Set Focus to Tablefilter only when Modal Dialog is not Shown\n      if (!$(\'#zmi-modal\').hasClass(\'show\')) {\n        $(\'#tablefilter\').focus();\n        // Prevent Submitting a form by hitting Enter\n        // https://stackoverflow.com/questions/895171/prevent-users-from-submitting-a-form-by-hitting-enter\n        if (event.which == 13) {\n          event.preventDefault();\n          return false;\n        };\n      };\n    })\n\n    $(\'#tablefilter\').keyup(function (event) {\n\n      if (isModifierKeyPressed(event)) {\n        return; // ignore\n      }\n\n      var tablefilter = $(this).val();\n      if (event.which == 13) {\n        if (1 === $(\'tbody tr:visible\').length) {\n          window.location.href = $(\'tbody tr:visible a\').attr(\'href\');\n        } else {\n          window.location.href = \'manage_findForm?btn_submit=Find&search_sub:int=1&obj_ids%3Atokens=\' + tablefilter;\n        }\n        event.preventDefault();\n      };\n      $(\'table.objectItems\').find("tbody tr").hide();\n      $(\'table.objectItems\').find("tbody tr td.zmi-object-id a:contains(" + tablefilter + ")").closest(\'tbody tr\').show();\n    });\n\n    // +++++++++++++++++++++++++++\n    // OBJECTIST SORTING: Show skey=meta_type\n    // +++++++++++++++++++++++++++\n    let searchParams = new URLSearchParams(window.location.search);\n    if (searchParams.get(\'skey\') == \'meta_type\') {\n      $(\'td.zmi-object-type i\').each(function () {\n        $(this).parent().parent().find(\'td.zmi-object-id\').prepend(\'')

            # <Static value=<_ast.Dict object at 0x7f9e25ad83c8> name=None at 7f9e25ad8390> -> __attrs_140317213689560
            __attrs_140317213689560 = _static_140317213688776

            # <span ... (0:0)
            # --------------------------------------------------------
            __append('<span')
            __append(' class="zmi-typename_show"')
            __append('>')
            __append("' + $(this).text() + '")
            __append('</span>')
            __append("')\n      });\n      $('th.zmi-object-id').addClass('zmi-typename_show');\n    }\n\n  });\n\n")
            __append('</script>')
            __append('\n\n')
            __default_140317213690456 = '__default'

            # <Value 'here/manage_page_footer' (237:31)> -> __cache_140317213690064
            __token = 11448
            __cache_140317213690064 = _static_140317251270640(getitem('here'), econtext, True, ('manage_page_footer', ))

            # <Identity expression=<Value 'here/manage_page_footer' (237:31)> value=<_ast.Str object at 0x7f9e25ad8940> at 7f9e25ad8978> -> __condition
            __expression = __cache_140317213690064
            __value = '__default'
            __condition = (__expression is __value)
            if __condition:
                pass
            else:
                __content = __cache_140317213690064
                __content = __convert(__content)
                if (__content is not None):
                    __append(__content)
            __append('\n')
        except:
            if (__token is not None):
                rcontext.setdefault('__error__', []).append((__tokens[__token] + (__filename, _exc_info()[1], )))
            raise

    return {'render': render, }