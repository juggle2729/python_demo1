# coding: utf-8
import random
import json
import time
import logging
import ctypes
from ctypes import c_uint64, c_int64, byref, c_int, c_uint,c_char_p
from cache import redis_cache as cache
from db.account.controller import query_app_manage, get_appkey, get_bank_card, get_auth_key
from utils.sms import send_sms_code
from utils import err
from utils.tz import utc_to_local_str
from utils.respcode import StatusCode

_LOGGER = logging.getLogger(__name__)
_DEFAULT_PAGE_SIZE = 100
_so = ctypes.CDLL('/home/ubuntu/libetotpverify.so')

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
    
def otp_check(account_id, otp):
    auth_key = get_auth_key(account_id)
    last_info = cache.get_last_succ(account_id)
    if not last_info:
        last_drift = last_succ = 0
    else:
        last_drift = int(last_info['drift'])
        last_succ = int(last_info['succ'])
    now_succ  = c_uint64()
    now_drift  = c_int64()
    checked_resp = _so.ET_CheckPwdz201(c_char_p(auth_key.strip()), c_uint64(int(time.time())),c_uint64(0),c_uint(60), c_int(last_drift), c_int(2), c_uint64(last_succ), c_char_p(otp.strip()), c_int(6), byref(now_succ),byref(now_drift))
    if checked_resp == 0:
        otp_token = cache.generate_otp_token(account_id)
        cache.save_last_succ(account_id, int(now_drift.value), int(now_succ.value))
        return {'otp_token': otp_token}
    else:
        raise err.AuthenticateError(status=StatusCode.INVALID_OTP)

        

