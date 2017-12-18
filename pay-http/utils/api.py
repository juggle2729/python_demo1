# -*- coding: utf-8 -*-
import json
import logging
import re
from os import path
from functools import wraps

from future.utils import raise_with_traceback
from smartencoding import smart_unicode
import geoip2.database
from geoip import geolite2
from flask import jsonify, make_response, request, g

from base import app
from utils import err, EnhencedEncoder
from utils.err import PayApiError
from utils.respcode import StatusCode

_DEFAULT_PAGE_SIZE = 10
_MAX_PAGE_SIZE = 20
DATA_PATH = '/home/ubuntu/flask-env/data/GeoLite2-City.mmdb'
_LOGGER = logging.getLogger(__name__)

city_reader = geoip2.database.Reader(DATA_PATH)


def _wrap2json(data):
    if data is None:
        data = {}
    elif isinstance(data, dict) or isinstance(data, list):
        return make_response(jsonify(status=0, msg='', data=data), 200)
    else:
        return data


def payapi_wrapper(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return _wrap2json(func(*args, **kwargs))
        except PayApiError as e:
            _LOGGER.exception('catch pay api error')
            return make_response(jsonify(status=0, msg='', data={'status': e.STATUS, 'error': str(e) or e.MSG}), 200)
        except Exception:
            _LOGGER.exception('unexcepted error!!')
            return make_response(jsonify(status=0, msg='system error', data={}), 200)

    return _wrapper


def response_wrapper(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        # if app.debug:
        #     return _wrap2json(func(*args, **kwargs))

        try:
            return _wrap2json(func(*args, **kwargs))
        except err.Error as e:
            if isinstance(e, err.ServerError):
                _LOGGER.exception('server error!')
            return make_response(
                jsonify(status=e.STATUS,
                        msg=str(e) or StatusCode.get_label(e.STATUS)),
                e.HTTPCODE)
        except Exception as e:
            _LOGGER.exception('unexcepted error!!')
            return make_response(
                jsonify(status=err.Error.STATUS,
                        msg=str(e) or u'未知错误'),
                err.Error.HTTPCODE)

    return _wrapper


def check_params(params, required_params,  # 必须值
                 default_param_dct=None,  # 默认值
                 param_type_dct=None,  # 参数类型，GET一般需要强制转换
                 param_validfunc_dct=None):  # 参数合法判定
    """验证传入参数有效性，注意这里会对params做in-place修改
    """
    params = params or {}
    if not params and required_params:
        raise_with_traceback(err.ParamError('missing all'))

    for param in required_params:
        if param not in params:
            raise_with_traceback(err.ParamError('missing %s' % param))

    if default_param_dct:
        for param in default_param_dct:
            if param not in params:
                params[param] = default_param_dct[param]

    if param_type_dct:
        for field, t in param_type_dct.iteritems():
            if field in params:
                try:
                    if t is basestring:
                        t = smart_unicode
                    params[field] = t(params[field])
                except Exception:
                    raise_with_traceback(err.ParamError(
                        'param %s type wrong' % field))

    if param_validfunc_dct:
        for field, func in param_validfunc_dct.iteritems():
            if field in params:
                try:
                    assert func(params[field])
                except AssertionError:
                    raise_with_traceback(err.ParamError(
                        'param %s illegal' % field))


def check_auth():
    if not g.get('user'):
        raise err.AuthenticateError(status=StatusCode.INVALID_TOKEN)


def token_required(func):
    @wraps(func)
    def _wrapped(*args, **kwargs):
        check_auth()
        return func(*args, **kwargs)

    return _wrapped


def get_country(ip, locale=None):
    country = ""
    geo = geolite2.lookup(ip)
    if geo:
        country = geo.country
    if not country and locale:
        try:
            lang, cty = re.split(r'[-_]', locale)
            country = cty
        except:
            pass
    return country or 'cn'


def get_city(ip, lan='zh-CN'):
    try:
        city_obj = city_reader.city(ip)
        return city_obj.city.names.get(lan)
    except Exception:
        return None


def get_client_ip():
    return request.access_route[-1] or request.remote_addr


def get_client_ua():
    return request.user_agent.string


def parse_common_params(query_dct):
    page = int(query_dct.get('page', 1))
    size = int(query_dct.get('size', 0))
    return page, size


def page2offset(page, size,
                max_size=_MAX_PAGE_SIZE, default_size=_DEFAULT_PAGE_SIZE):
    """return limit, offset
    """
    limit = default_size if not size or size > max_size else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page - 1) * limit
    return limit, offset


_COM_P = re.compile(
    r'\[aid:(.*)\],\[code:(.*)\],\[lan:(.*)\],\[svc:(.*)\],\[svn:(.*)\],\[cvn:(.*)\],\[cvc:(.*)\],\[chn:(.*)\]')


def parse_p(p):
    if not p:
        return {}
    g = _COM_P.match(p)
    if not g:
        return {}
    else:
        return {
            'aid': g.group(1),
            'code': g.group(2),
            'lan': g.group(3),
            'svc': g.group(4),
            'svn': g.group(5),
            'cvn': g.group(6),
            'cvc': int(g.group(7)),  # app version
            'chn': g.group(8)  # channel: ios or android channel
        }
