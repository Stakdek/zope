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

_static_139817698922904 = {'class': 'zmi-typename_show', }
_static_139817698908424 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_importExportForm:method', 'value': 'Import/Export', }
_static_139817698906688 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_pasteObjects:method', 'value': 'Paste', }
_static_139817698900400 = {'class': 'form-group', }
_static_139817698898048 = {'class': 'alert alert-info mt-4 mb-4', }
_static_139817698887384 = {'type': 'submit', 'name': 'manage_move_objects_to_bottom:method', 'value': 'Move to bottom', 'class': 'btn btn-primary', 'title': 'Move selected items to bottom', }
_static_139817698872680 = {'type': 'submit', 'name': 'manage_move_objects_to_top:method', 'value': 'Move to top', 'class': 'btn btn-primary', 'title': 'Move selected items to top', }
_static_139817698856352 = {'class': 'form-control', 'name': 'delta:int', }
_static_139817698855120 = {'class': 'col-xs-2', }
_static_139817698864544 = {'type': 'submit', 'name': 'manage_move_objects_down:method', 'value': 'Move down', 'title': 'Move selected items down', 'class': 'btn btn-primary', }
_static_139817698861464 = {'type': 'submit', 'name': 'manage_move_objects_up:method', 'value': 'Move up', 'title': 'Move selected items up', 'class': 'btn btn-primary', }
_static_139817699347200 = {'class': 'form-group row zmi-controls', }
_static_139817699346024 = {'class': 'container-fluid', }
_static_139817699356344 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_importExportForm:method', 'value': 'Import/Export', }
_static_139817699354216 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_delObjects:method', 'value': 'Delete', }
_static_139817699344168 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_pasteObjects:method', 'value': 'Paste', }
_static_139817699342096 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_copyObjects:method', 'value': 'Copy', }
_static_139817699331656 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_cutObjects:method', 'value': 'Cut', }
_static_139817699329584 = {'class': 'btn btn-primary', 'type': 'submit', 'name': 'manage_renameForm:method', 'value': 'Rename', }
_static_139817699239304 = {'class': 'form-group zmi-controls', }
_static_139817699305736 = {'class': 'text-right zmi-object-date hidden-xs pl-3', }
_static_139817699304056 = {'class': 'text-right zmi-object-size hidden-xs', }
_static_139817699296984 = {'class': 'zmi-object-title hidden-xs', }
_static_139817699295864 = {'class': 'fa fa-lock', }
_static_139817699277792 = {'class': 'badge badge-warning', 'title': 'This item has been locked by WebDAV', }
_static_139817699275104 = {'href': "python:'%s/manage_workspace'%(ob_dict['quoted_id'])", }
_static_139817699261632 = {'class': 'zmi-object-id', }
_static_139817699260456 = {'class': 'sr-only', }
_static_139817699266064 = {'title': 'Broken object', 'class': 'fas fa-ban text-danger', }
_static_139817699264720 = {'class': 'zmi-object-type', 'onclick': "$(this).prev().children('input').trigger('click')", }
_static_139817699262536 = {'type': 'checkbox', 'class': 'checkbox-list-item', 'name': 'ids:list', 'onclick': "event.stopPropagation();$(this).parent().parent().toggleClass('checked');", 'value': 'ob_dict/id', }
_static_139817699240312 = {'class': 'zmi-object-check text-right', 'onclick': "$(this).children('input').trigger('click');", }
_static_139817699228472 = {'class': 'fa fa-sort', }
_static_139817699226344 = {'title': 'Sort Ascending by Modification Date', 'href': '?skey=_p_mtime&rkey=asc', 'class': "python:request.get('skey',None)=='_p_mtime' and 'zmi-sort_key' or None", }
_static_139817699220672 = {'scope': 'col', 'class': 'zmi-object-date text-right hidden-xs', }
_static_139817699219496 = {'class': 'fa fa-sort', }
_static_139817699364592 = {'title': 'Sort Ascending by File-Size', 'href': '?skey=get_size&rkey=asc', 'class': "python:request.get('skey',None)=='get_size' and 'zmi-sort_key' or None", }
_static_139817699363472 = {'scope': 'col', 'class': 'zmi-object-size text-right hidden-xs', }
_static_139817699361120 = {'id': 'tablefilter', 'name': 'obj_ids:tokens', 'type': 'text', 'title': 'Filter object list by entering a name. Pressing the Enter key starts recursive search.', }
_static_139817699842760 = {'class': 'fa fa-search tablefilter', 'onclick': "$('#tablefilter').focus()", }
_static_139817699841584 = {'class': 'fa fa-sort', }
_static_139817699818464 = {'title': 'Sort Ascending by Name', 'href': '?skey=id&rkey=asc', 'class': "python:request.get('skey',None)=='id' and 'zmi-sort_key' or None", }
_static_139817699816448 = {'scope': 'col', 'class': 'zmi-object-id', }
_static_139817699724704 = {'class': 'fa fa-sort', }
_static_139817699721792 = {'title': 'Sort Ascending by Meta-Type', 'href': '?skey=meta_type&rkey=asc', 'class': "python:request.get('skey',None)=='meta_type' and 'zmi-sort_key' or None", }
_static_139817699750744 = {'scope': 'col', 'class': 'zmi-object-type', }
_static_139817699750576 = {'type': 'checkbox', 'id': 'checkAll', 'onclick': 'checkbox_all();', }
_static_139817699693680 = {'scope': 'col', 'class': 'zmi-object-check text-right', }
_static_139817719828608 = {}
_static_139817699630328 = {'class': 'thead-light', }
_static_139817699629096 = {'class': 'table table-striped table-hover table-sm objectItems', }
_static_139817699637680 = {'name': 'objectItems', 'method': 'post', 'action': 'string:${request/URL1}/', }
_static_139817718999472 = {'class': 'container-fluid', }
_static_139817719409072 = _BoboAwareZopeTraverse()

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
            __default_139817718912112 = '__default'

            # <Value 'here/manage_page_header' (1:31)> -> __cache_139817718914128
            __token = 31
            __cache_139817718914128 = _static_139817719409072(getitem('here'), econtext, True, ('manage_page_header', ))

            # <Identity expression=<Value 'here/manage_page_header' (1:31)> value=<_ast.Str object at 0x7f29d97815f8> at 7f29d9781668> -> __condition
            __expression = __cache_139817718914128
            __value = '__default'
            __condition = (__expression is __value)
            if __condition:
                pass
            else:
                __content = __cache_139817718914128
                __content = __convert(__content)
                if (__content is not None):
                    __append(__content)
            __append('\n\n')
            __default_139817718998632 = '__default'

            # <Value 'here/manage_tabs' (3:29)> -> __cache_139817718912672
            __token = 89
            __cache_139817718912672 = _static_139817719409072(getitem('here'), econtext, True, ('manage_tabs', ))

            # <Identity expression=<Value 'here/manage_tabs' (3:29)> value=<_ast.Str object at 0x7f29d97814e0> at 7f29d97814a8> -> __condition
            __expression = __cache_139817718912672
            __value = '__default'
            __condition = (__expression is __value)
            if __condition:
                pass
            else:
                __content = __cache_139817718912672
                __content = __convert(__content)
                if (__content is not None):
                    __append(__content)
            __append('\n\n')

            # <Static value=<_ast.Dict object at 0x7f29d97969b0> name=None at 7f29d97812e8> -> __attrs_139817699637288
            __attrs_139817699637288 = _static_139817718999472

            # <main ... (0:0)
            # --------------------------------------------------------
            __append('<main')
            __append(' class="container-fluid"')
            __append('>')
            __append('\n  ')
            __backup_has_order_support_139817719085264 = get('has_order_support', __marker)

            # <Value "python:getattr(here.aq_explicit, 'has_order_support', 0)" (8:38)> -> __value
            __token = 229
            __value = get('getattr', getattr)(_guarded_getattr(getitem('here'), 'aq_explicit'), 'has_order_support', 0)
            econtext['has_order_support'] = __value
            __backup_sm_139817699724312 = get('sm', __marker)

            # <Value 'modules/AccessControl/SecurityManagement/getSecurityManager' (9:22)> -> __value
            __token = 309
            __value = _static_139817719409072(get('modules', modules), econtext, True, ('AccessControl', 'SecurityManagement', 'getSecurityManager', ))
            econtext['sm'] = __value
            __backup_default_sort_139817718914240 = get('default_sort', __marker)

            # <Value "python: 'position' if has_order_support else 'id'" (10:31)> -> __value
            __token = 402
            __value = ('position' if getitem('has_order_support') else 'id')
            econtext['default_sort'] = __value
            __backup_skey_139817699637120 = get('skey', __marker)

            # <Value "python:request.get('skey',default_sort)" (11:22)> -> __value
            __token = 477
            __value = _guarded_getattr(getitem('request'), 'get')('skey', getitem('default_sort'))
            econtext['skey'] = __value
            __backup_rkey_139817699637064 = get('rkey', __marker)

            # <Value "python:request.get('rkey','asc')" (12:21)> -> __value
            __token = 542
            __value = _guarded_getattr(getitem('request'), 'get')('rkey', 'asc')
            econtext['rkey'] = __value
            __backup_rkey_alt_139817699639080 = get('rkey_alt', __marker)

            # <Value "python:'desc' if rkey=='asc' else 'asc'" (13:24)> -> __value
            __token = 604
            __value = ('desc' if (getitem('rkey') == 'asc') else 'asc')
            econtext['rkey_alt'] = __value
            __backup_obs_139817699639192 = get('obs', __marker)

            # <Value 'python: here.manage_get_sortedObjects(sortkey = skey, revkey = rkey)' (14:18)> -> __value
            __token = 668
            __value = _guarded_getattr(getitem('here'), 'manage_get_sortedObjects')(sortkey=getitem('skey'), revkey=getitem('rkey'))
            econtext['obs'] = __value

            # <Static value=<_ast.Dict object at 0x7f29d851f9b0> name=None at 7f29d851f080> -> __attrs_139817699638800
            __attrs_139817699638800 = _static_139817699637680

            # <form ... (0:0)
            # --------------------------------------------------------
            __append('<form')
            __append(' name="objectItems"')
            __append(' method="post"')
            __default_139817699638352 = '__default__'

            # <Substitution 'string:${request/URL1}/' (16:31)> -> __attr_action
            __token = 796
            __token = 805
            __attr_action = _static_139817719409072(getitem('request'), econtext, True, ('URL1', ))
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
            __condition = _static_139817719409072(getitem('obs'), econtext, True, ())
            if __condition:
                __append('\n      ')

                # <Value 'obs' (19:89)> -> __condition
                __token = 948
                __condition = _static_139817719409072(getitem('obs'), econtext, True, ())
                if __condition:

                    # <Static value=<_ast.Dict object at 0x7f29d851d828> name=None at 7f29d851d7f0> -> __attrs_139817699630832
                    __attrs_139817699630832 = _static_139817699629096

                    # <table ... (0:0)
                    # --------------------------------------------------------
                    __append('<table')
                    __append(' class="table table-striped table-hover table-sm objectItems"')
                    __append('>')
                    __append('\n        ')

                    # <Static value=<_ast.Dict object at 0x7f29d851dcf8> name=None at 7f29d851dd68> -> __attrs_139817699696480
                    __attrs_139817699696480 = _static_139817699630328

                    # <thead ... (0:0)
                    # --------------------------------------------------------
                    __append('<thead')
                    __default_139817699630160 = 'thead-light'

                    # <Substitution "python:'thead-light sorted_%s'%(request.get('rkey',''))" (20:57)> -> __attr_class
                    __token = 1011
                    __attr_class = ('thead-light sorted_%s' % _guarded_getattr(getitem('request'), 'get')('rkey', ''))
                    __attr_class = __quote(__attr_class, '"', '&quot;', 'thead-light', '__default__')
                    if (__attr_class is not None):
                        __append((' class="%s"' % __attr_class))
                    __append('>')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817699692728
                    __attrs_139817699692728 = _static_139817719828608

                    # <tr ... (0:0)
                    # --------------------------------------------------------
                    __append('<tr')
                    __append('>')
                    __append('\n            ')

                    # <Static value=<_ast.Dict object at 0x7f29d852d470> name=None at 7f29d852d438> -> __attrs_139817699696144
                    __attrs_139817699696144 = _static_139817699693680

                    # <th ... (0:0)
                    # --------------------------------------------------------
                    __append('<th')
                    __append(' scope="col"')
                    __append(' class="zmi-object-check text-right"')
                    __append('>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f29d853b2b0> name=None at 7f29d853be80> -> __attrs_139817699752424
                    __attrs_139817699752424 = _static_139817699750576

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

                    # <Static value=<_ast.Dict object at 0x7f29d853b358> name=None at 7f29d853b438> -> __attrs_139817699753880
                    __attrs_139817699753880 = _static_139817699750744

                    # <th ... (0:0)
                    # --------------------------------------------------------
                    __append('<th')
                    __append(' scope="col"')
                    __append(' class="zmi-object-type"')
                    __append('>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f29d8534240> name=None at 7f29d85341d0> -> __attrs_139817699724816
                    __attrs_139817699724816 = _static_139817699721792

                    # <a ... (0:0)
                    # --------------------------------------------------------
                    __append('<a')
                    __default_139817699723192 = 'Sort Ascending by Meta-Type'

                    # <Substitution "python:'Sort %s by Meta-Type'%( rkey_alt.upper() )" (28:39)> -> __attr_title
                    __token = 1441
                    __attr_title = ('Sort %s by Meta-Type' % _guarded_getattr(getitem('rkey_alt'), 'upper')())
                    __attr_title = __quote(__attr_title, '"', '&quot;', 'Sort Ascending by Meta-Type', '__default__')
                    if (__attr_title is not None):
                        __append((' title="%s"' % __attr_title))
                    __default_139817699723696 = '?skey=meta_type&rkey=asc'

                    # <Substitution "python:'?skey=meta_type&rkey=%s'%( rkey_alt )" (29:37)> -> __attr_href
                    __token = 1530
                    __attr_href = ('?skey=meta_type&rkey=%s' % getitem('rkey_alt'))
                    __attr_href = __quote(__attr_href, '"', '&quot;', '?skey=meta_type&rkey=asc', '__default__')
                    if (__attr_href is not None):
                        __append((' href="%s"' % __attr_href))
                    __default_139817699723808 = '__default__'

                    # <Substitution "python:request.get('skey',None)=='meta_type' and 'zmi-sort_key' or None" (30:37)> -> __attr_class
                    __token = 1615
                    __attr_class = (((_guarded_getattr(getitem('request'), 'get')('skey', None) == 'meta_type') and 'zmi-sort_key') or None)
                    __attr_class = __quote(__attr_class, '"', '&quot;', None, '__default__')
                    if (__attr_class is not None):
                        __append((' class="%s"' % __attr_class))
                    __append('>')
                    __append('\n                ')

                    # <Static value=<_ast.Dict object at 0x7f29d8534da0> name=None at 7f29d8534fd0> -> __attrs_139817699815608
                    __attrs_139817699815608 = _static_139817699724704

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

                    # <Static value=<_ast.Dict object at 0x7f29d854b400> name=None at 7f29d854b438> -> __attrs_139817699817624
                    __attrs_139817699817624 = _static_139817699816448

                    # <th ... (0:0)
                    # --------------------------------------------------------
                    __append('<th')
                    __append(' scope="col"')
                    __append(' class="zmi-object-id"')
                    __append('>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f29d854bbe0> name=None at 7f29d854b940> -> __attrs_139817699841304
                    __attrs_139817699841304 = _static_139817699818464

                    # <a ... (0:0)
                    # --------------------------------------------------------
                    __append('<a')
                    __default_139817699843544 = 'Sort Ascending by Name'

                    # <Substitution "python:'Sort %s by Name'%( rkey_alt.upper() )" (38:39)> -> __attr_title
                    __token = 1985
                    __attr_title = ('Sort %s by Name' % _guarded_getattr(getitem('rkey_alt'), 'upper')())
                    __attr_title = __quote(__attr_title, '"', '&quot;', 'Sort Ascending by Name', '__default__')
                    if (__attr_title is not None):
                        __append((' title="%s"' % __attr_title))
                    __default_139817699840408 = '?skey=id&rkey=asc'

                    # <Substitution "python:'?skey=id&rkey=%s'%( rkey_alt )" (39:37)> -> __attr_href
                    __token = 2069
                    __attr_href = ('?skey=id&rkey=%s' % getitem('rkey_alt'))
                    __attr_href = __quote(__attr_href, '"', '&quot;', '?skey=id&rkey=asc', '__default__')
                    if (__attr_href is not None):
                        __append((' href="%s"' % __attr_href))
                    __default_139817699840520 = '__default__'

                    # <Substitution "python:request.get('skey',None)=='id' and 'zmi-sort_key' or None" (40:37)> -> __attr_class
                    __token = 2147
                    __attr_class = (((_guarded_getattr(getitem('request'), 'get')('skey', None) == 'id') and 'zmi-sort_key') or None)
                    __attr_class = __quote(__attr_class, '"', '&quot;', None, '__default__')
                    if (__attr_class is not None):
                        __append((' class="%s"' % __attr_class))
                    __append('>')
                    __append('\n                Name\n                ')

                    # <Static value=<_ast.Dict object at 0x7f29d8551630> name=None at 7f29d8551390> -> __attrs_139817699842256
                    __attrs_139817699842256 = _static_139817699841584

                    # <i ... (0:0)
                    # --------------------------------------------------------
                    __append('<i')
                    __append(' class="fa fa-sort"')
                    __append('>')
                    __append('</i>')
                    __append('\n              ')
                    __append('</a>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f29d8551ac8> name=None at 7f29d8551cc0> -> __attrs_139817699842088
                    __attrs_139817699842088 = _static_139817699842760

                    # <i ... (0:0)
                    # --------------------------------------------------------
                    __append('<i')
                    __append(' class="fa fa-search tablefilter"')
                    __append(' onclick="$(\'#tablefilter\').focus()"')
                    __append('>')
                    __append('</i>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f29d84dc160> name=None at 7f29d84dc0f0> -> __attrs_139817699363640
                    __attrs_139817699363640 = _static_139817699361120

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

                    # <Static value=<_ast.Dict object at 0x7f29d84dca90> name=None at 7f29d84dc780> -> __attrs_139817699363808
                    __attrs_139817699363808 = _static_139817699363472

                    # <th ... (0:0)
                    # --------------------------------------------------------
                    __append('<th')
                    __append(' scope="col"')
                    __append(' class="zmi-object-size text-right hidden-xs"')
                    __append('>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f29d84dcef0> name=None at 7f29d84dcda0> -> __attrs_139817699219104
                    __attrs_139817699219104 = _static_139817699364592

                    # <a ... (0:0)
                    # --------------------------------------------------------
                    __append('<a')
                    __default_139817699218096 = 'Sort Ascending by File-Size'

                    # <Substitution "python:'Sort %s by File-Size'%( rkey_alt.upper() )" (51:39)> -> __attr_title
                    __token = 2826
                    __attr_title = ('Sort %s by File-Size' % _guarded_getattr(getitem('rkey_alt'), 'upper')())
                    __attr_title = __quote(__attr_title, '"', '&quot;', 'Sort Ascending by File-Size', '__default__')
                    if (__attr_title is not None):
                        __append((' title="%s"' % __attr_title))
                    __default_139817699218376 = '?skey=get_size&rkey=asc'

                    # <Substitution "python:'?skey=get_size&rkey=%s'%( rkey_alt )" (52:37)> -> __attr_href
                    __token = 2915
                    __attr_href = ('?skey=get_size&rkey=%s' % getitem('rkey_alt'))
                    __attr_href = __quote(__attr_href, '"', '&quot;', '?skey=get_size&rkey=asc', '__default__')
                    if (__attr_href is not None):
                        __append((' href="%s"' % __attr_href))
                    __default_139817699218600 = '__default__'

                    # <Substitution "python:request.get('skey',None)=='get_size' and 'zmi-sort_key' or None" (53:37)> -> __attr_class
                    __token = 2999
                    __attr_class = (((_guarded_getattr(getitem('request'), 'get')('skey', None) == 'get_size') and 'zmi-sort_key') or None)
                    __attr_class = __quote(__attr_class, '"', '&quot;', None, '__default__')
                    if (__attr_class is not None):
                        __append((' class="%s"' % __attr_class))
                    __append('>')
                    __append('\n                Size\n                ')

                    # <Static value=<_ast.Dict object at 0x7f29d84b9828> name=None at 7f29d84b97f0> -> __attrs_139817699220280
                    __attrs_139817699220280 = _static_139817699219496

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

                    # <Static value=<_ast.Dict object at 0x7f29d84b9cc0> name=None at 7f29d84b9c88> -> __attrs_139817699225896
                    __attrs_139817699225896 = _static_139817699220672

                    # <th ... (0:0)
                    # --------------------------------------------------------
                    __append('<th')
                    __append(' scope="col"')
                    __append(' class="zmi-object-date text-right hidden-xs"')
                    __append('>')
                    __append('\n              ')

                    # <Static value=<_ast.Dict object at 0x7f29d84bb2e8> name=None at 7f29d84bb240> -> __attrs_139817699228080
                    __attrs_139817699228080 = _static_139817699226344

                    # <a ... (0:0)
                    # --------------------------------------------------------
                    __append('<a')
                    __default_139817699227072 = 'Sort Ascending by Modification Date'

                    # <Substitution "python:'Sort %s by Modification Date'%( rkey_alt.upper() )" (62:39)> -> __attr_title
                    __token = 3431
                    __attr_title = ('Sort %s by Modification Date' % _guarded_getattr(getitem('rkey_alt'), 'upper')())
                    __attr_title = __quote(__attr_title, '"', '&quot;', 'Sort Ascending by Modification Date', '__default__')
                    if (__attr_title is not None):
                        __append((' title="%s"' % __attr_title))
                    __default_139817699227352 = '?skey=_p_mtime&rkey=asc'

                    # <Substitution "python:'?skey=_p_mtime&rkey=%s'%( rkey_alt )" (63:37)> -> __attr_href
                    __token = 3528
                    __attr_href = ('?skey=_p_mtime&rkey=%s' % getitem('rkey_alt'))
                    __attr_href = __quote(__attr_href, '"', '&quot;', '?skey=_p_mtime&rkey=asc', '__default__')
                    if (__attr_href is not None):
                        __append((' href="%s"' % __attr_href))
                    __default_139817699227576 = '__default__'

                    # <Substitution "python:request.get('skey',None)=='_p_mtime' and 'zmi-sort_key' or None" (64:37)> -> __attr_class
                    __token = 3612
                    __attr_class = (((_guarded_getattr(getitem('request'), 'get')('skey', None) == '_p_mtime') and 'zmi-sort_key') or None)
                    __attr_class = __quote(__attr_class, '"', '&quot;', None, '__default__')
                    if (__attr_class is not None):
                        __append((' class="%s"' % __attr_class))
                    __append('>')
                    __append('\n                Last Modified\n                ')

                    # <Static value=<_ast.Dict object at 0x7f29d84bbb38> name=None at 7f29d84bbb00> -> __attrs_139817699229256
                    __attrs_139817699229256 = _static_139817699228472

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

                    # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817699238128
                    __attrs_139817699238128 = _static_139817719828608

                    # <tbody ... (0:0)
                    # --------------------------------------------------------
                    __append('<tbody')
                    __append('>')
                    __append('\n          ')
                    __backup_ob_dict_139817699628760 = get('ob_dict', __marker)

                    # <Value 'obs' (73:34)> -> __iterator
                    __token = 3914
                    __iterator = _static_139817719409072(getitem('obs'), econtext, True, ())
                    (__iterator, ____index_139817699239024, ) = getitem('repeat')('ob_dict', __iterator)
                    econtext['ob_dict'] = None
                    for __item in __iterator:
                        econtext['ob_dict'] = __item

                        # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817699238856
                        __attrs_139817699238856 = _static_139817719828608

                        # <tr ... (0:0)
                        # --------------------------------------------------------
                        __append('<tr')
                        __append('>')
                        __append('\n            ')
                        __backup_ob_139817699630608 = get('ob', __marker)

                        # <Value 'nocall:ob_dict/obj' (74:32)> -> __value
                        __token = 3952
                        __value = _static_139817719409072(getitem('ob_dict'), econtext, False, ('obj', ))
                        econtext['ob'] = __value
                        __append('\n              ')

                        # <Static value=<_ast.Dict object at 0x7f29d84be978> name=None at 7f29d84be8d0> -> __attrs_139817699241376
                        __attrs_139817699241376 = _static_139817699240312

                        # <td ... (0:0)
                        # --------------------------------------------------------
                        __append('<td')
                        __append(' class="zmi-object-check text-right"')
                        __append(' onclick="$(this).children(\'input\').trigger(\'click\');"')
                        __append('>')
                        __append('\n                ')

                        # <Static value=<_ast.Dict object at 0x7f29d84c4048> name=None at 7f29d84beeb8> -> __attrs_139817699264328
                        __attrs_139817699264328 = _static_139817699262536

                        # <input ... (0:0)
                        # --------------------------------------------------------
                        __append('<input')
                        __append(' type="checkbox"')
                        __append(' class="checkbox-list-item"')
                        __append(' name="ids:list"')
                        __append(' onclick="event.stopPropagation();$(this).parent().parent().toggleClass(\'checked\');"')
                        __default_139817699263992 = '__default__'

                        # <Substitution 'ob_dict/id' (76:104)> -> __attr_value
                        __token = 4186
                        __attr_value = _static_139817719409072(getitem('ob_dict'), econtext, True, ('id', ))
                        __attr_value = __quote(__attr_value, '"', '&quot;', None, '__default__')
                        if (__attr_value is not None):
                            __append((' value="%s"' % __attr_value))
                        __append(' />')
                        __append('\n              ')
                        __append('</td>')
                        __append('\n              ')

                        # <Static value=<_ast.Dict object at 0x7f29d84c48d0> name=None at 7f29d84c4898> -> __attrs_139817699265784
                        __attrs_139817699265784 = _static_139817699264720

                        # <td ... (0:0)
                        # --------------------------------------------------------
                        __append('<td')
                        __append(' class="zmi-object-type"')
                        __append(' onclick="$(this).prev().children(\'input\').trigger(\'click\')"')
                        __append('>')
                        __append('\n                ')

                        # <Static value=<_ast.Dict object at 0x7f29d84c4e10> name=None at 7f29d84c4e48> -> __attrs_139817699259504
                        __attrs_139817699259504 = _static_139817699266064

                        # <i ... (0:0)
                        # --------------------------------------------------------
                        __append('<i')
                        __default_139817699258664 = 'Broken object'

                        # <Substitution 'ob/meta_type | default' (79:122)> -> __attr_title
                        __token = 4530
                        try:
                            __attr_title = _static_139817719409072(getitem('ob'), econtext, True, ('meta_type', ))
                        except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                            __attr_title = _static_139817719409072(__default_139817699258664, econtext, True, ())

                        __attr_title = __quote(__attr_title, '"', '&quot;', 'Broken object', '__default__')
                        if (__attr_title is not None):
                            __append((' title="%s"' % __attr_title))
                        __default_139817699259000 = 'fas fa-ban text-danger'

                        # <Substitution 'ob/zmi_icon | default' (79:94)> -> __attr_class
                        __token = 4502
                        try:
                            __attr_class = _static_139817719409072(getitem('ob'), econtext, True, ('zmi_icon', ))
                        except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                            __attr_class = _static_139817719409072(__default_139817699259000, econtext, True, ())

                        __attr_class = __quote(__attr_class, '"', '&quot;', 'fas fa-ban text-danger', '__default__')
                        if (__attr_class is not None):
                            __append((' class="%s"' % __attr_class))
                        __append('>')
                        __append('\n                  ')

                        # <Static value=<_ast.Dict object at 0x7f29d84c3828> name=None at 7f29d84c37f0> -> __attrs_139817699261240
                        __attrs_139817699261240 = _static_139817699260456

                        # <span ... (0:0)
                        # --------------------------------------------------------
                        __append('<span')
                        __append(' class="sr-only"')
                        __append('>')
                        __default_139817699260176 = '__default'

                        # <Value 'ob/meta_type | default' (80:53)> -> __cache_139817699259784
                        __token = 4609
                        try:
                            __cache_139817699259784 = _static_139817719409072(getitem('ob'), econtext, True, ('meta_type', ))
                        except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                            __cache_139817699259784 = _static_139817719409072(__default_139817699260176, econtext, True, ())


                        # <Identity expression=<Value 'ob/meta_type | default' (80:53)> value=<_ast.Str object at 0x7f29d84c35f8> at 7f29d84c3630> -> __condition
                        __expression = __cache_139817699259784
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:
                            __append('Broken object')
                        else:
                            __content = __cache_139817699259784
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('</span>')
                        __append('\n                ')
                        __append('</i>')
                        __append('\n              ')
                        __append('</td>')
                        __append('\n              ')

                        # <Static value=<_ast.Dict object at 0x7f29d84c3cc0> name=None at 7f29d84c3c88> -> __attrs_139817699262416
                        __attrs_139817699262416 = _static_139817699261632

                        # <td ... (0:0)
                        # --------------------------------------------------------
                        __append('<td')
                        __append(' class="zmi-object-id"')
                        __append('>')
                        __append('\n                ')

                        # <Static value=<_ast.Dict object at 0x7f29d84c7160> name=None at 7f29d84c7128> -> __attrs_139817699276112
                        __attrs_139817699276112 = _static_139817699275104

                        # <a ... (0:0)
                        # --------------------------------------------------------
                        __append('<a')
                        __default_139817699275608 = '__default__'

                        # <Substitution "python:'%s/manage_workspace'%(ob_dict['quoted_id'])" (84:40)> -> __attr_href
                        __token = 4776
                        __attr_href = ('%s/manage_workspace' % _guarded_getitem(getitem('ob_dict'), 'quoted_id'))
                        __attr_href = __quote(__attr_href, '"', '&quot;', None, '__default__')
                        if (__attr_href is not None):
                            __append((' href="%s"' % __attr_href))
                        __append('>')
                        __append('\n                  ')
                        __default_139817699277344 = '__default'

                        # <Value 'ob_dict/id' (85:37)> -> __cache_139817699276952
                        __token = 4867
                        __cache_139817699276952 = _static_139817719409072(getitem('ob_dict'), econtext, True, ('id', ))

                        # <Identity expression=<Value 'ob_dict/id' (85:37)> value=<_ast.Str object at 0x7f29d84c7908> at 7f29d84c7940> -> __condition
                        __expression = __cache_139817699276952
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:

                            # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817699276840
                            __attrs_139817699276840 = _static_139817719828608

                            # <span ... (0:0)
                            # --------------------------------------------------------
                            __append('<span')
                            __append('>')
                            __append('Id')
                            __append('</span>')
                        else:
                            __content = __cache_139817699276952
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('\n                  ')

                        # <Value 'ob/wl_isLocked | nothing' (86:111)> -> __condition
                        __token = 5000
                        try:
                            __condition = _static_139817719409072(getitem('ob'), econtext, True, ('wl_isLocked', ))
                        except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                            __condition = _static_139817719409072(get('nothing', nothing), econtext, True, ())

                        if __condition:

                            # <Static value=<_ast.Dict object at 0x7f29d84c7be0> name=None at 7f29d84c7b38> -> __attrs_139817699295304
                            __attrs_139817699295304 = _static_139817699277792

                            # <span ... (0:0)
                            # --------------------------------------------------------
                            __append('<span')
                            __append(' class="badge badge-warning"')
                            __append(' title="This item has been locked by WebDAV"')
                            __append('>')
                            __append('\n                    ')

                            # <Static value=<_ast.Dict object at 0x7f29d84cc278> name=None at 7f29d84cc240> -> __attrs_139817699296648
                            __attrs_139817699296648 = _static_139817699295864

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
                            __condition = _static_139817719409072(getitem('ob'), econtext, True, ('title', ))
                        except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                            __condition = _static_139817719409072(get('nothing', nothing), econtext, True, ())

                        if __condition:

                            # <Static value=<_ast.Dict object at 0x7f29d84cc6d8> name=None at 7f29d84cc6a0> -> __attrs_139817699297768
                            __attrs_139817699297768 = _static_139817699296984

                            # <span ... (0:0)
                            # --------------------------------------------------------
                            __append('<span')
                            __append(' class="zmi-object-title hidden-xs"')
                            __append('>')
                            __append('\n                    &nbsp;(')
                            __default_139817699299112 = '__default'

                            # <Value 'ob/title' (90:46)> -> __cache_139817699298720
                            __token = 5239
                            __cache_139817699298720 = _static_139817719409072(getitem('ob'), econtext, True, ('title', ))

                            # <Identity expression=<Value 'ob/title' (90:46)> value=<_ast.Str object at 0x7f29d84cce10> at 7f29d84cce48> -> __condition
                            __expression = __cache_139817699298720
                            __value = '__default'
                            __condition = (__expression is __value)
                            if __condition:

                                # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817699298608
                                __attrs_139817699298608 = _static_139817719828608

                                # <span ... (0:0)
                                # --------------------------------------------------------
                                __append('<span')
                                __append('>')
                                __append('</span>')
                            else:
                                __content = __cache_139817699298720
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

                        # <Static value=<_ast.Dict object at 0x7f29d84ce278> name=None at 7f29d84ce240> -> __attrs_139817699304840
                        __attrs_139817699304840 = _static_139817699304056

                        # <td ... (0:0)
                        # --------------------------------------------------------
                        __append('<td')
                        __append(' class="text-right zmi-object-size hidden-xs"')
                        __append('>')
                        __default_139817699303832 = '__default'

                        # <Value 'python:here.compute_size(ob)' (94:76)> -> __cache_139817699299280
                        __token = 5401
                        __cache_139817699299280 = _guarded_getattr(getitem('here'), 'compute_size')(getitem('ob'))

                        # <Identity expression=<Value 'python:here.compute_size(ob)' (94:76)> value=<_ast.Str object at 0x7f29d84ce080> at 7f29d84ce0b8> -> __condition
                        __expression = __cache_139817699299280
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:
                            __append('\n              ')
                        else:
                            __content = __cache_139817699299280
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('</td>')
                        __append('\n              ')

                        # <Static value=<_ast.Dict object at 0x7f29d84ce908> name=None at 7f29d84ce8d0> -> __attrs_139817699306520
                        __attrs_139817699306520 = _static_139817699305736

                        # <td ... (0:0)
                        # --------------------------------------------------------
                        __append('<td')
                        __append(' class="text-right zmi-object-date hidden-xs pl-3"')
                        __append('>')
                        __default_139817699305512 = '__default'

                        # <Value 'python:here.last_modified(ob)' (96:81)> -> __cache_139817699305120
                        __token = 5533
                        __cache_139817699305120 = _guarded_getattr(getitem('here'), 'last_modified')(getitem('ob'))

                        # <Identity expression=<Value 'python:here.last_modified(ob)' (96:81)> value=<_ast.Str object at 0x7f29d84ce710> at 7f29d84ce748> -> __condition
                        __expression = __cache_139817699305120
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:
                            __append('\n              ')
                        else:
                            __content = __cache_139817699305120
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('</td>')
                        __append('\n            ')
                        if (__backup_ob_139817699630608 is __marker):
                            del econtext['ob']
                        else:
                            econtext['ob'] = __backup_ob_139817699630608
                        __append('\n          ')
                        __append('</tr>')
                        ____index_139817699239024 -= 1
                        if (____index_139817699239024 > 0):
                            __append('\n          ')
                    if (__backup_ob_dict_139817699628760 is __marker):
                        del econtext['ob_dict']
                    else:
                        econtext['ob_dict'] = __backup_ob_dict_139817699628760
                    __append('\n        ')
                    __append('</tbody>')
                    __append('\n      ')
                    __append('</table>')
                __append('\n\n      ')
                __backup_delete_allowed_139817699639248 = get('delete_allowed', __marker)

                # <Value "python:sm.checkPermission('Delete objects', context)" (104:21)> -> __value
                __token = 5734
                __value = _guarded_getattr(getitem('sm'), 'checkPermission')('Delete objects', getitem('context'))
                econtext['delete_allowed'] = __value

                # <Value 'obs' (104:90)> -> __condition
                __token = 5803
                __condition = _static_139817719409072(getitem('obs'), econtext, True, ())
                if __condition:

                    # <Static value=<_ast.Dict object at 0x7f29d84be588> name=None at 7f29d84be630> -> __attrs_139817699307304
                    __attrs_139817699307304 = _static_139817699239304

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
                        __condition = _static_139817719409072(getitem('context'), econtext, True, ('dontAllowCopyAndPaste', ))
                    except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                        __condition = _static_139817719409072(get('nothing', nothing), econtext, True, ())

                    __condition = not __condition
                    if __condition:
                        __append('\n          ')

                        # <Static value=<_ast.Dict object at 0x7f29d84d4630> name=None at 7f29d84d45f8> -> __attrs_139817699331040
                        __attrs_139817699331040 = _static_139817699329584

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
                        __condition = _static_139817719409072(getitem('delete_allowed'), econtext, True, ())
                        if __condition:

                            # <Static value=<_ast.Dict object at 0x7f29d84d4e48> name=None at 7f29d84d4e10> -> __attrs_139817699341368
                            __attrs_139817699341368 = _static_139817699331656

                            # <input ... (0:0)
                            # --------------------------------------------------------
                            __append('<input')
                            __append(' class="btn btn-primary"')
                            __append(' type="submit"')
                            __append(' name="manage_cutObjects:method"')
                            __append(' value="Cut"')
                            __append(' />')
                        __append('\n          ')

                        # <Static value=<_ast.Dict object at 0x7f29d84d7710> name=None at 7f29d84d76d8> -> __attrs_139817699343552
                        __attrs_139817699343552 = _static_139817699342096

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
                        __condition = _static_139817719409072(getitem('here'), econtext, True, ('cb_dataValid', ))
                        if __condition:

                            # <Static value=<_ast.Dict object at 0x7f29d84d7f28> name=None at 7f29d84d7ef0> -> __attrs_139817699353880
                            __attrs_139817699353880 = _static_139817699344168

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
                    __condition = _static_139817719409072(getitem('delete_allowed'), econtext, True, ())
                    if __condition:

                        # <Static value=<_ast.Dict object at 0x7f29d84da668> name=None at 7f29d84da630> -> __attrs_139817699355672
                        __attrs_139817699355672 = _static_139817699354216

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

                        # <Static value=<_ast.Dict object at 0x7f29d84daeb8> name=None at 7f29d84dae80> -> __attrs_139817699345576
                        __attrs_139817699345576 = _static_139817699356344

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
                if (__backup_delete_allowed_139817699639248 is __marker):
                    del econtext['delete_allowed']
                else:
                    econtext['delete_allowed'] = __backup_delete_allowed_139817699639248
                __append('\n      ')

                # <Static value=<_ast.Dict object at 0x7f29d84d8668> name=None at 7f29d84d8630> -> __attrs_139817699346808
                __attrs_139817699346808 = _static_139817699346024

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

                    # <Static value=<_ast.Dict object at 0x7f29d84d8b00> name=None at 7f29d84d8ac8> -> __attrs_139817699347984
                    __attrs_139817699347984 = _static_139817699347200

                    # <div ... (0:0)
                    # --------------------------------------------------------
                    __append('<div')
                    __append(' class="form-group row zmi-controls"')
                    __append('>')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f29d8462198> name=None at 7f29d8462160> -> __attrs_139817698863200
                    __attrs_139817698863200 = _static_139817698861464

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

                    # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817698863872
                    __attrs_139817698863872 = _static_139817719828608

                    # <span ... (0:0)
                    # --------------------------------------------------------
                    __append('<span')
                    __append('>')
                    __append('/')
                    __append('</span>')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f29d8462da0> name=None at 7f29d8462d68> -> __attrs_139817698854056
                    __attrs_139817698854056 = _static_139817698864544

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

                    # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817698854728
                    __attrs_139817698854728 = _static_139817719828608

                    # <span ... (0:0)
                    # --------------------------------------------------------
                    __append('<span')
                    __append('>')
                    __append('by')
                    __append('</span>')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f29d84608d0> name=None at 7f29d8460898> -> __attrs_139817698855904
                    __attrs_139817698855904 = _static_139817698855120

                    # <div ... (0:0)
                    # --------------------------------------------------------
                    __append('<div')
                    __append(' class="col-xs-2"')
                    __append('>')
                    __append('\n            ')

                    # <Static value=<_ast.Dict object at 0x7f29d8460da0> name=None at 7f29d8460cf8> -> __attrs_139817698869768
                    __attrs_139817698869768 = _static_139817698856352

                    # <select ... (0:0)
                    # --------------------------------------------------------
                    __append('<select')
                    __append(' class="form-control"')
                    __append(' name="delta:int"')
                    __append('>')
                    __append('\n              ')
                    __backup_val_139817699240032 = get('val', __marker)

                    # <Value 'python:range(1,min(5,len(obs)))' (122:38)> -> __iterator
                    __token = 7387
                    __iterator = get('range', range)(1, get('min', min)(5, len(getitem('obs'))))
                    (__iterator, ____index_139817698871000, ) = getitem('repeat')('val', __iterator)
                    econtext['val'] = None
                    for __item in __iterator:
                        econtext['val'] = __item

                        # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817698870832
                        __attrs_139817698870832 = _static_139817719828608

                        # <option ... (0:0)
                        # --------------------------------------------------------
                        __append('<option')
                        __append('>')
                        __default_139817698870440 = '__default'

                        # <Value 'val' (122:84)> -> __cache_139817698870048
                        __token = 7433
                        __cache_139817698870048 = _static_139817719409072(getitem('val'), econtext, True, ())

                        # <Identity expression=<Value 'val' (122:84)> value=<_ast.Str object at 0x7f29d8464390> at 7f29d84643c8> -> __condition
                        __expression = __cache_139817698870048
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:
                            pass
                        else:
                            __content = __cache_139817698870048
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('</option>')
                        ____index_139817698871000 -= 1
                        if (____index_139817698871000 > 0):
                            __append('\n              ')
                    if (__backup_val_139817699240032 is __marker):
                        del econtext['val']
                    else:
                        econtext['val'] = __backup_val_139817699240032
                    __append('\n              ')
                    __backup_val_139817699239752 = get('val', __marker)

                    # <Value 'python:range(5,len(obs),5)' (123:38)> -> __iterator
                    __token = 7479
                    __iterator = get('range', range)(5, len(getitem('obs')), 5)
                    (__iterator, ____index_139817698872120, ) = getitem('repeat')('val', __iterator)
                    econtext['val'] = None
                    for __item in __iterator:
                        econtext['val'] = __item

                        # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817698871952
                        __attrs_139817698871952 = _static_139817719828608

                        # <option ... (0:0)
                        # --------------------------------------------------------
                        __append('<option')
                        __append('>')
                        __default_139817698871560 = '__default'

                        # <Value 'val' (123:79)> -> __cache_139817698871168
                        __token = 7520
                        __cache_139817698871168 = _static_139817719409072(getitem('val'), econtext, True, ())

                        # <Identity expression=<Value 'val' (123:79)> value=<_ast.Str object at 0x7f29d84647f0> at 7f29d8464828> -> __condition
                        __expression = __cache_139817698871168
                        __value = '__default'
                        __condition = (__expression is __value)
                        if __condition:
                            pass
                        else:
                            __content = __cache_139817698871168
                            __content = __quote(__content, None, '\xad', None, None)
                            if (__content is not None):
                                __append(__content)
                        __append('</option>')
                        ____index_139817698872120 -= 1
                        if (____index_139817698872120 > 0):
                            __append('\n              ')
                    if (__backup_val_139817699239752 is __marker):
                        del econtext['val']
                    else:
                        econtext['val'] = __backup_val_139817699239752
                    __append('\n            ')
                    __append('</select>')
                    __append('\n          ')
                    __append('</div>')
                    __append('\n          ')

                    # <Static value=<_ast.Dict object at 0x7f29d8464d68> name=None at 7f29d8464d30> -> __attrs_139817698886768
                    __attrs_139817698886768 = _static_139817698872680

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

                    # <Static value=<_ast.Dict object at 0x7f29d84686d8> name=None at 7f29d84686a0> -> __attrs_139817698889120
                    __attrs_139817698889120 = _static_139817698887384

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
            __condition = _static_139817719409072(getitem('obs'), econtext, True, ())
            __condition = not __condition
            if __condition:
                __append('\n      ')

                # <Static value=<_ast.Dict object at 0x7f29d846b080> name=None at 7f29d846b048> -> __attrs_139817698898832
                __attrs_139817698898832 = _static_139817698898048

                # <div ... (0:0)
                # --------------------------------------------------------
                __append('<div')
                __append(' class="alert alert-info mt-4 mb-4"')
                __append('>')
                __append('\n        There are currently no items in ')

                # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817698900064
                __attrs_139817698900064 = _static_139817719828608

                # <em ... (0:0)
                # --------------------------------------------------------
                __append('<em')
                __append('>')
                __default_139817698899504 = '__default'

                # <Value 'here/title_or_id' (134:57)> -> __cache_139817698899112
                __token = 8074
                __cache_139817698899112 = _static_139817719409072(getitem('here'), econtext, True, ('title_or_id', ))

                # <Identity expression=<Value 'here/title_or_id' (134:57)> value=<_ast.Str object at 0x7f29d846b518> at 7f29d846b550> -> __condition
                __expression = __cache_139817698899112
                __value = '__default'
                __condition = (__expression is __value)
                if __condition:
                    pass
                else:
                    __content = __cache_139817698899112
                    __content = __quote(__content, None, '\xad', None, None)
                    if (__content is not None):
                        __append(__content)
                __append('</em>')
                __append('.\n      ')
                __append('</div>')
                __append('\n      ')

                # <Static value=<_ast.Dict object at 0x7f29d846b9b0> name=None at 7f29d846b978> -> __attrs_139817698901184
                __attrs_139817698901184 = _static_139817698900400

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
                    __condition = _static_139817719409072(getitem('context'), econtext, True, ('dontAllowCopyAndPaste', ))
                except (AttributeError, LookupError, NameError, TypeError, ValueError, _NotFound, _Unauthorized, _LocationError, ):
                    __condition = _static_139817719409072(get('nothing', nothing), econtext, True, ())

                __condition = not __condition
                if __condition:
                    __append('\n          ')

                    # <Value 'here/cb_dataValid' (138:118)> -> __condition
                    __token = 8340
                    __condition = _static_139817719409072(getitem('here'), econtext, True, ('cb_dataValid', ))
                    if __condition:

                        # <Static value=<_ast.Dict object at 0x7f29d846d240> name=None at 7f29d846d208> -> __attrs_139817698908144
                        __attrs_139817698908144 = _static_139817698906688

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

                    # <Static value=<_ast.Dict object at 0x7f29d846d908> name=None at 7f29d846bf98> -> __attrs_139817698909880
                    __attrs_139817698909880 = _static_139817698908424

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
            if (__backup_has_order_support_139817719085264 is __marker):
                del econtext['has_order_support']
            else:
                econtext['has_order_support'] = __backup_has_order_support_139817719085264
            if (__backup_sm_139817699724312 is __marker):
                del econtext['sm']
            else:
                econtext['sm'] = __backup_sm_139817699724312
            if (__backup_default_sort_139817718914240 is __marker):
                del econtext['default_sort']
            else:
                econtext['default_sort'] = __backup_default_sort_139817718914240
            if (__backup_skey_139817699637120 is __marker):
                del econtext['skey']
            else:
                econtext['skey'] = __backup_skey_139817699637120
            if (__backup_rkey_139817699637064 is __marker):
                del econtext['rkey']
            else:
                econtext['rkey'] = __backup_rkey_139817699637064
            if (__backup_rkey_alt_139817699639080 is __marker):
                del econtext['rkey_alt']
            else:
                econtext['rkey_alt'] = __backup_rkey_alt_139817699639080
            if (__backup_obs_139817699639192 is __marker):
                del econtext['obs']
            else:
                econtext['obs'] = __backup_obs_139817699639192
            __append('\n')
            __append('</main>')
            __append('\n\n\n')

            # <Static value=<_ast.Dict object at 0x7f29d9861080> name=None at 7f29d9861e80> -> __attrs_139817698889400
            __attrs_139817698889400 = _static_139817719828608

            # <script ... (0:0)
            # --------------------------------------------------------
            __append('<script')
            __append('>')
            __append("\n  // +++++++++++++++++++++++++++\n  // checkbox_all: Item  Selection\n  // +++++++++++++++++++++++++++\n  function checkbox_all() {\n    var checkboxes = document.getElementsByClassName('checkbox-list-item');\n    // Toggle Highlighting CSS-Class\n    if (document.getElementById('checkAll').checked) {\n      $('table.objectItems tbody tr').addClass('checked');\n    } else {\n      $('table.objectItems tbody tr').removeClass('checked');\n    };\n    // Set Checkbox like checkAll-Box\n    for (i = 0; i ")
            __append('<')
            __append(' checkboxes.length; i++) {\n      checkboxes[i].checked = document.getElementById(\'checkAll\').checked;\n    }\n  };\n\n\n  $(function () {\n\n    // +++++++++++++++++++++++++++\n    // Icon Tooltips\n    // +++++++++++++++++++++++++++\n    $(\'td.zmi-object-type i\').tooltip({\n      \'placement\': \'top\'\n    });\n\n    // +++++++++++++++++++++++++++\n    // Tablefilter/Search Element\n    // +++++++++++++++++++++++++++\n\n    function isModifierKeyPressed(event) {\n      return event.altKey ||\n        event.ctrlKey ||\n        event.metaKey;\n    }\n\n    $(document).keypress(function (event) {\n\n      if (isModifierKeyPressed(event)) {\n        return; // ignore\n      }\n\n      // Set Focus to Tablefilter only when Modal Dialog is not Shown\n      if (!$(\'#zmi-modal\').hasClass(\'show\')) {\n        $(\'#tablefilter\').focus();\n        // Prevent Submitting a form by hitting Enter\n        // https://stackoverflow.com/questions/895171/prevent-users-from-submitting-a-form-by-hitting-enter\n        if (event.which == 13) {\n          event.preventDefault();\n          return false;\n        };\n      };\n    })\n\n    $(\'#tablefilter\').keyup(function (event) {\n\n      if (isModifierKeyPressed(event)) {\n        return; // ignore\n      }\n\n      var tablefilter = $(this).val();\n      if (event.which == 13) {\n        if (1 === $(\'tbody tr:visible\').length) {\n          window.location.href = $(\'tbody tr:visible a\').attr(\'href\');\n        } else {\n          window.location.href = \'manage_findForm?btn_submit=Find&search_sub:int=1&obj_ids%3Atokens=\' + tablefilter;\n        }\n        event.preventDefault();\n      };\n      $(\'table.objectItems\').find("tbody tr").hide();\n      $(\'table.objectItems\').find("tbody tr td.zmi-object-id a:contains(" + tablefilter + ")").closest(\'tbody tr\').show();\n    });\n\n    // +++++++++++++++++++++++++++\n    // OBJECTIST SORTING: Show skey=meta_type\n    // +++++++++++++++++++++++++++\n    let searchParams = new URLSearchParams(window.location.search);\n    if (searchParams.get(\'skey\') == \'meta_type\') {\n      $(\'td.zmi-object-type i\').each(function () {\n        $(this).parent().parent().find(\'td.zmi-object-id\').prepend(\'')

            # <Static value=<_ast.Dict object at 0x7f29d8471198> name=None at 7f29d8471160> -> __attrs_139817698923688
            __attrs_139817698923688 = _static_139817698922904

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
            __default_139817698924584 = '__default'

            # <Value 'here/manage_page_footer' (237:31)> -> __cache_139817698924192
            __token = 11448
            __cache_139817698924192 = _static_139817719409072(getitem('here'), econtext, True, ('manage_page_footer', ))

            # <Identity expression=<Value 'here/manage_page_footer' (237:31)> value=<_ast.Str object at 0x7f29d8471710> at 7f29d8471748> -> __condition
            __expression = __cache_139817698924192
            __value = '__default'
            __condition = (__expression is __value)
            if __condition:
                pass
            else:
                __content = __cache_139817698924192
                __content = __convert(__content)
                if (__content is not None):
                    __append(__content)
            __append('\n')
        except:
            if (__token is not None):
                rcontext.setdefault('__error__', []).append((__tokens[__token] + (__filename, _exc_info()[1], )))
            raise

    return {'render': render, }