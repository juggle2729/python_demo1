# -*- coding: utf-8 -*-
import json
import logging
from decimal import Decimal

import requests

from db.pay_record.model import PAY_STATUS, PayRecord, PAY_TYPE, NOTIFY_STATUS
from db.account.model import Account
from db.pay_record.controller import get_pay, add_notify
from db.account.controller import get_appkey, get_appid_detail
from common.sign import generate_sign
from cache.redis_cache import submit_timer_event
from timer import EVENT_ENUM
from utils.tz import now_milli_ts, now_ts
from utils.id_generator import generate_long_id
from utils.err import InsufficientFunds
from utils.decorator import sql_wrapper

_TRACKER = logging.getLogger('tracker')
_LOGGER = logging.getLogger('51paypay')

NOTIFY_INTERVAL = (
    15,  # index: 重试次数, value: 间隔时间
    15,
    30,
    180,
    1800,
    1800,
    1800,
    1800,
    3600
)


_SERVICE_FEE_LIMIT = -50


def notify_success(payid):
    """
    通知商户,支付成功
    """
    pay_record = get_pay(payid)
    if not (pay_record and pay_record.pay_status == PAY_STATUS.PAY_SUCCESS):
        return
    appid = pay_record.appid
    appkey = get_appkey(appid)
    params = {
        "amount": str(pay_record.amount),
        "appid": appid,
        "orderid": pay_record.orderid,
        'status': 2  # 给商户的交易状态,2成功,1失败
    }
    sign = generate_sign(params, appkey)
    params['signature'] = sign
    _LOGGER.info(params)
    try:
        resp = requests.post(pay_record.notify_url, json=params, timeout=3)
        _LOGGER.info('notify pay_record[%s] detail: %s %s %s' %
                     (payid, pay_record.notify_url, resp.status_code, resp.content))
    except Exception,e:
        _LOGGER.info('notify pay_record[%s] http error: %s' % (payid, e))
        resp = None
    if resp and resp.status_code == 200 and resp.content == 'SUCCESS':
        add_notify(payid, NOTIFY_STATUS.SUCCESS)
        _LOGGER.info('notify pay_record[%s] success' % payid)
        return True
    else:
        _LOGGER.info('notify pay_record[%s] fail' % payid)
        notify_record = add_notify(payid, NOTIFY_STATUS.FAIL)
        try_times = notify_record.try_times
        if try_times < len(NOTIFY_INTERVAL):
            timestamp = now_ts() + NOTIFY_INTERVAL[try_times]
            submit_timer_event(EVENT_ENUM.NOTIFY_PAY, json.dumps({'payid': payid}), timestamp)
        return True


def get_fee(fee_rate, amount):
    if amount < Decimal('1'):
        return Decimal('0')
    if pay_type == PAY_TYPE.ALIPAY_REAL_H5:
        if fee_rate == 60 and amount < Decimal('34'):
            return Decimal('0.2')
        if fee_rate == 120 and amount < Decimal('42'):
            return Decimal('0.5')
    return amount * (Decimal(fee_rate) / 10000)


@sql_wrapper
def create_pay_record(orderid, mchid, appid, pay_type, amount, notify_url, description=''):
    appid_detail = get_appid_detail(appid, pay_type, polling=True)
    fee_rate = appid_detail.fee_rate
    service_rate = appid_detail.service_rate
    accountid = appid_detail.accountid
    account = Account.query.filter(Account.id == accountid).one()
    service_fee = appid_detail.service_rate / 10000.0 * float(amount)
#    if service_rate and account.balance < _SERVICE_FEE_LIMIT:  # service_fee:
#        raise InsufficientFunds(u"服务费余额不足")

    pay_record = PayRecord()
    pay_record.id = generate_long_id('pay')
    pay_record.orderid = orderid
    pay_record.description = description
    pay_record.mchid = mchid or None
    pay_record.appid = appid
    pay_record.pay_type = pay_type or PAY_TYPE.WECHAT_H5
    pay_record.amount = amount
    pay_record.description = description
    pay_record.fee = get_fee(fee_rate, amount)
    pay_record.notify_url = notify_url
    pay_record.real_pay = appid_detail.real_pay
    pay_record.real_custid = appid_detail.custid
    pay_record.pay_status = PAY_STATUS.READY
    pay_record.service_fee = service_fee
    pay_record.save(auto_commit=True)
    return pay_record


def notify_merchant(orderid):
    try:
        notify_success(orderid)
    except Exception as e:
        _LOGGER.exception('notify pay_record[%s] error[%s]' % (orderid, e))
        submit_timer_event(
            EVENT_ENUM.NOTIFY_PAY,
            json.dumps({'payid': orderid}),
            now_ts() + 30 # retry 30 seconds later
        )
