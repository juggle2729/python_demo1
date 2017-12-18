# -*- coding: utf-8 -*-
import random
from datetime import datetime

import requests
from alipay import ISVAliPay
from . import AliPayKeyStr as AliPay

from db.pay_record.model import PAY_TYPE
from db.account.controller import get_appid_detail, get_alipay_appid, get_alipay_appid_by_alipay_id
from utils import err


def alipay_h5_pay(pay_record, ordername, return_url):
    appid, pay_type, amount, pay_id = pay_record.appid, pay_record.pay_type, pay_record.amount, pay_record.id
    appid_detail = get_appid_detail(appid, pay_type)
    alipay_appid = get_alipay_appid(appid)
    alipay_id, pub_key, notify_url = alipay_appid.aliappid, alipay_appid.public_key, alipay_appid.notify_url
    if not appid_detail or not alipay_id:
        raise err.AppIDWrong()
    alipay = AliPay(
        appid = alipay_id,
        app_notify_url = "http://p.51paypay.net/pay/404/",
        app_private_key_path = open("static/private.key").read(),
        alipay_public_key_path = open("static/public.key").read(),
        sign_type="RSA2", # RSA 或者 RSA2
        debug=False  # 默认False
    )
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no = pay_id,
        total_amount = float(amount),
        subject = ordername,
        return_url = return_url,
        notify_url = notify_url
    )
    mid_url = 'https://openapi.alipay.com/gateway.do?' + order_string
    pay_request = requests.get(mid_url, allow_redirects=False)
    real_url = pay_request.headers.get('Location')
    if real_url:
        return {
            'status': 0,
            'pay_url': real_url
        }
    else:
        raise err.SystemError()

def alipay_h5_withdraw(appid, amount, to_account, order_code):
    """ {u'msg': u'Success', u'order_id': u'20171214110070001502760014672416',
         u'out_biz_no': u'20171214032609', u'code': u'10000',
         u'pay_date': u'2017-12-14 11:26:09'}
    """
    appid_detail = get_appid_detail(appid, 23)
    alipay_appid = get_alipay_appid(appid)
    alipay_id, pub_key, notify_url = alipay_appid.aliappid, alipay_appid.public_key, alipay_appid.notify_url
    alipay = AliPay(
        appid = alipay_id,
        app_notify_url = "http://p.51paypay.net/pay/404/",
        app_private_key_path = open("static/private.key").read(),
        alipay_public_key_path = open("static/public.key").read(),
        sign_type="RSA2", # RSA 或者 RSA2
        debug=False  # 默认False
    )
    result = alipay.api_alipay_fund_trans_toaccount_transfer(
        str(order_code),
        payee_type = "ALIPAY_LOGONID",
        payee_account = to_account,
        amount = float(amount)
    )
    return result


def alipay_h5_withdraw_query(appid, order_code):
    """
    {u'code': u'10000',
     u'msg': u'Success',
     u'order_fee': u'0.00',
     u'order_id': u'20171214110070001502760014672416',
     u'out_biz_no': u'20171214032609',
     u'pay_date': u'2017-12-14 11:26:09',
     u'status': u'SUCCESS'}
    """

    alipay_appid = get_alipay_appid(appid)
    alipay_id, pub_key, notify_url = alipay_appid.aliappid, alipay_appid.public_key, alipay_appid.notify_url
    alipay = AliPay(
        appid=alipay_id,
        app_notify_url="http://p.51paypay.net/pay/404/",
        app_private_key_path=open("static/private.key").read(),
        alipay_public_key_path=open("static/public.key").read(),
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False  # 默认False
    )
    result = alipay.api_alipay_fund_trans_order_query(out_biz_no=order_code)
    return result


def alipay_traffic_pay(amount, orderid):
    alipay = AliPay(
        appid = "2017112300109792",
        app_notify_url = "http://p.51paypay.net/pay/404/",
        app_private_key_path = open("static/private.key").read(),
        alipay_public_key_path = open("static/public.key").read(),
        sign_type="RSA2", # RSA 或者 RSA2
        debug=False  # 默认False
    )
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no = orderid,
        total_amount = amount,
        subject = '流量充值',
        return_url = 'http://www.51paypay.net/',
        notify_url = "http://p.51paypay.net/admin/service/alipay/pay_callback"
    )
    mid_url = 'https://openapi.alipay.com/gateway.do?' + order_string
    pay_request = requests.get(mid_url, allow_redirects=False)
    real_url = pay_request.headers.get('Location')
    if real_url:
        return real_url
    else:
        raise err.SystemError()

def check_data(data, signature):
    alipay_id = data.get('app_id')
    alipay_appid = get_alipay_appid_by_alipay_id(alipay_id)
    pub_key = alipay_appid.public_key
    alipay = AliPay(
        appid = alipay_id,
        app_notify_url = "http://p.51paypay.net/pay/404/",
        app_private_key_path = open("static/private.key").read(),
        alipay_public_key_path = pub_key,
        sign_type="RSA2", # RSA 或者 RSA2
        debug=False  # 默认False
    )
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        return True
    else:
        return False
