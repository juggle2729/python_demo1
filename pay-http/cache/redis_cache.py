# -*- coding: utf-8 -*-
"""
"""
import logging
import time

from cache import cache, prefix_key
from utils.decorator import cache_wrapper
from utils import tz
from db.account.model import REAL_PAY

_LOGGER = logging.getLogger(__name__)
_LOCK_TIMEOUT = 10
_CODE_EXPIRE_TIME = 5 * 60  # 5 minutes
_IP_EXPIRE_TIME = 3600
_MAX_SENT = 2  # at most 2 sms in 5 seconds
_MAX_COUNT = 5  # if 5 req in 5 seconds then
_FORBID_TIME = 3600  # forbid this ip 5 mins


def _add_prefix(key, isIp=False):
    if isIp:
        return prefix_key('ip:%s' % key)
    else:
        return prefix_key('phone:%s' % key)


@cache_wrapper
def submit_timer_event(event_type, cache_value, timestamp):
    key = prefix_key('timerzset:%s' % event_type)
    return cache.zadd(key, timestamp, cache_value)


@cache_wrapper
def replace_timer_event(event_type, cache_value, timestamp):
    key = prefix_key('timerzset:%s' % event_type)
    cache.delete(key)
    return cache.zadd(key, timestamp, cache_value)


@cache_wrapper
def exist_any_event(event_type):
    key = prefix_key('timerzset:%s' % event_type)
    return cache.zcard(key) > 0


@cache_wrapper
def appid_generator():
    key = prefix_key('appid:pay')
    return cache.incr(key)


@cache_wrapper
def pop_expired_events(event_type, max_time):
    key = prefix_key('timerzset:%s' % event_type)
    resp = cache.zrangebyscore(key, 0, max_time)
    if resp:
        cache.zrem(key, *resp)
    return resp


@cache_wrapper
def timer_event_processed(event_id):
    key = prefix_key('timerlock:%s' % event_id)
    return not cache.setnx(key, int(time.time()))


@cache_wrapper
def save_auth_code(phone, code):
    cache.setex(_add_prefix(phone), _CODE_EXPIRE_TIME, code)


@cache_wrapper
def delete_auth_code(phone):
    cache.delete(_add_prefix(phone))


@cache_wrapper
def get_auth_code(phone):
    return cache.get(_add_prefix(phone))


@cache_wrapper
def get_auth_code_ttl(phone):
    return cache.ttl(_add_prefix(phone))


@cache_wrapper
def check_count(key, max_sent, max_count, forbid_time, default_expire):
    count = cache.get(key)
    if count is not None:
        cache.incr(key)
        if int(count) < max_sent:
            return True
        elif int(count) >= max_count:
            cache.expire(key, forbid_time)
            return False
        else:
            return False
    else:
        cache.setex(key, default_expire, 1)
        return True


@cache_wrapper
def check_ip_count(ip):
    # short_key = _add_prefix(ip, True)
    # short_check = check_count(short_key, _MAX_SENT, _MAX_COUNT, _FORBID_TIME, _IP_EXPIRE_TIME)
    long_key = prefix_key('ipcount:%s' % ip)
    long_check = check_count(long_key, 6, 10, 3600, 3600)
    return long_check


@cache_wrapper
def check_phone_count(phone):
    key = prefix_key('phonecount:%s' % phone)
    phone_check = check_count(key, 10, 20, 12 * 3600, 12 * 3600)
    return phone_check


@cache_wrapper
def get_alipay_qr(payid):
    key = prefix_key('payid:%s' % payid)
    return cache.get(key)


@cache_wrapper
def set_alipay_qr(payid, qrCode):
    key = prefix_key('payid:%s' % payid)
    return cache.setex(key, 3600, qrCode)


# 控制台验证码等cache
DEFAULT_CACHE_TIMEOUT = 1 * 60
DEFAULT_SMS_CACHE_TIMEOUT = 10 * 60
DEFAULT_SMS_SENDED_CACHE_TIMEOUT = 55


@cache_wrapper
def set_sms_cache(phone, value=True):
    key = prefix_key('sms_cache:%s' % phone)
    cache.setex(key, DEFAULT_SMS_CACHE_TIMEOUT, value)


@cache_wrapper
def get_sms_cache(phone):
    key = prefix_key('sms_cache:%s' % phone)
    return cache.get(key)


@cache_wrapper
def cache_id_code(id, code):
    key = prefix_key('id_cache:%s' % id)
    cache.setex(key, DEFAULT_CACHE_TIMEOUT, code)


@cache_wrapper
def get_cache_code(id):
    key = prefix_key('id_cache:%s' % id)
    code = cache.get(key) or 'FUCK'
    return code


@cache_wrapper
def set_sms_sended_cache(phone):
    key = prefix_key('sms_sended_cache:%s' % phone)
    cache.setex(key, DEFAULT_SMS_SENDED_CACHE_TIMEOUT, True)


@cache_wrapper
def get_sms_sended_cache(phone):
    key = prefix_key('sms_sended_cache:%s' % phone)
    return cache.get(key)


@cache_wrapper
def set_appid_balance(appid, real_pay, balance):
    key = prefix_key('appid:%s:real_pay:%s' % (appid, real_pay))
    return cache.set(key, balance)


@cache_wrapper
def get_appid_balance(appid):
    real_pay_list = REAL_PAY.to_dict().keys()
    balance = 0.0
    for real_pay in real_pay_list:
        key = prefix_key('appid:%s:real_pay:%s' % (appid, real_pay))
        balance += float(cache.get(key) or 0)
    return balance
