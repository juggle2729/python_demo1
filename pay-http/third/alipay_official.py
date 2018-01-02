# -*- coding: utf-8 -*-
import random
from datetime import datetime

import requests
from . import AliPayKeyStr as AliPay

from db.account.controller import get_appid_detail, get_cached_random_alipay_appid, get_alipay_appid_by_alipay_id
from utils import err


def alipay_h5_pay(pay_record, ordername, return_url):
    appid, pay_type, amount, pay_id = pay_record.appid, pay_record.pay_type, pay_record.amount, pay_record.id
    appid_detail = get_appid_detail(appid, pay_type)
    alipay_appid = get_cached_random_alipay_appid()
    alipay_id, pub_key, notify_url = alipay_appid.aliappid, alipay_appid.public_key, alipay_appid.notify_url
    if not appid_detail or not alipay_id:
        raise err.AppIDWrong()
    alipay = AliPay(
        appid=alipay_id,
        app_notify_url="http://p.51paypay.net/pay/404/",
        app_private_key_path=open("static/private.key").read(),
        alipay_public_key_path=pub_key,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False  # 默认False
    )
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no=str(pay_id),
        total_amount=float(amount),
        subject=ordername,
        return_url=return_url,
        notify_url=notify_url
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


def alipay_traffic_pay(amount, orderid):
    alipay = AliPay(
        appid="2017112300109792",
        app_notify_url="http://p.51paypay.net/pay/404/",
        app_private_key_path=open("static/private.key").read(),
        alipay_public_key_path=open("static/public.key").read(),
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False  # 默认False
    )
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no=orderid,
        total_amount=amount,
        subject='流量充值',
        return_url='http://www.51paypay.net/',
        notify_url="http://p.51paypay.net/admin/service/alipay/pay_callback"
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
        appid=alipay_id,
        app_notify_url="http://p.51paypay.net/pay/404/",
        app_private_key_path=open("static/private.key").read(),
        alipay_public_key_path=pub_key,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False  # 默认False
    )
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        return True
    else:
        return False
