# coding: utf-8
import random
import json
import logging
from cache import redis_cache as cache
from db.account.controller import query_app_manage, get_appkey, get_bank_card
from utils.sms import send_sms_code
from utils.tz import utc_to_local_str

_LOGGER = logging.getLogger(__name__)
_DEFAULT_PAGE_SIZE = 100


def generate_auth_code(length=6):
    l = 10 ** (length - 1)
    h = 10 ** length
    return str(random.randrange(l, h))


def send_auth_code(phone, country=None, ip='', need_check=True):
    if need_check:
        if ip and not cache.check_ip_count(ip):
            _LOGGER.error('same ip send sms too quick!!!, ip:%s, phone:%s', ip, phone)
            return None
        if not cache.check_phone_count(phone):
            _LOGGER.error('same phone send sms too quick!!!, ip:%s, phone: %s', ip, phone)
            return None
    code = cache.get_auth_code(phone)
    if not code:
        code = generate_auth_code()
        cache.save_auth_code(phone, code)
    try:
        send_sms_code(phone, code)
        _LOGGER.info(', ip:%s, phone:%s', ip, phone)
    except Exception as e:
        cache.delete_auth_code(phone)
        raise e
    return code


def check_auth_code(phone, code):
    saved_code = cache.get_auth_code(phone)
    # FIXME: this code for test only
    return saved_code == code  # or code == '12345678'


def get_app_manage(account_id, appid, app_type, valid, name, page, size):

    limit = _DEFAULT_PAGE_SIZE if not size or size > _DEFAULT_PAGE_SIZE else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page - 1) * limit

    apps, counts = query_app_manage(account_id, appid=appid, app_type=app_type,
                                    valid=valid, appname=name, limit=limit, offset=offset)
    pages = int(counts / float(limit)) + 1
    resp = []
    for app in apps:
        data = {
            'name': app.appname,
            'appid': app.appid,
            'appkey': get_appkey(app.appid),
            'app_type': app.app_type,
            'pay_type': json.loads(app.pay_type),
            'status': app.valid,
            'created_at': utc_to_local_str(app.created_at),
        }
        resp.append(data)

    resp_wrap = {'pages': pages, 'resp': resp}  # 需有加个分页
    return resp_wrap

def get_bankcard_info(account_id):
    bancard = get_bank_card(account_id)
    resp = {}
    if bancard:
        for k in ('card_number', 'card_name', 'bank_name', 'subbank_name', 'card_type', 'extend'):
            resp.update({k:getattr(bancard, k)})
    return resp
    
    
