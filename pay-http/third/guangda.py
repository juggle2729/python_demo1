# -*- coding: utf-8 -*-
"""
光大银行支付接口
"""
import json
import binascii
import datetime
import time
import logging

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA, SHA256
from Crypto.PublicKey import RSA
import requests

from db.pay_record.model import PAY_TYPE, convert_accquire_type
from db.account.controller import get_appid_detail
from db.pay_record.controller import save_originid
from utils import err

_LOGGER = logging.getLogger(__name__)

_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCuhDE334YKOw8rsxJ50KbFYzAJ
p9MDkyoBC9ZX+YzGKR/WcHGlIiJfZflQhd9ZBwbkDvyEJxBC8M8ktx6/sCpo5Epw
sfpjrFPW4ugEpiuGB6RDUgMWelZcl8Nf/a3yEB4SkZ8+zEyRT+5KWIeOpY0hDy15
A1G1BjGekCEDR8LavQIDAQAB
-----END PUBLIC KEY-----"""

_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAKfr7xl
ECZ93UWa313Hofedt7ujuxFQE3BpKU/eevwrvbyf4hTa84scz8IHRkj
Fz7owHCPtUcf0iy2kwjivrT67ajG7x7EJKJJUGkV/3Yrs78X2DFFvDl
veANT3NCNZcuA5F3PRUIjzLB13VJjxEBDUjuJ9dVWk07o0vKi7Gq7KH
AgMBAAECgYAFOXLz70j5XCX9MyUR1zDrnWD8gEk9b/VFICDiqF67QV3
M+Y9zd4b6uaP29gU9YqT+WE2wPB1bydRYTnlt5mFROzfP/LRTVvwiqf
umVe1gtoz/cDjuQH54aJV2YM7TKzlTTV5ub5yegY+mp6UjQoX3kLXPL
OKVIiG+V7orqF9n2QJBAPvuP92IJaMFHSMCKDi/YUhLPn0gn2ZwJ+Re
7+Pa8CCBTZsuNeTjvQt0Soo7uwBBq9AAMG8viaxlfSzVXb8u38UCQQC
qok0lrY3cjF2iO6+S+2iGVINr2pDeoVyYtuvSLYaPBBbVZ1RWgOatmd
P6NlmiBVGfYZDeG5Nb+uDeO8iMkIHbAkEAm6m0kH9FMhtAy5bTn2yxA
WhsrgfwNe1q2LLIavOml48NkqrU5h7JekBaplsNyrTJInZbdvfai0kS
NReJG04tOQJATeaLEgiKG4Z5uPdG0PO2ZJ1w4myGdx10CMR6JRpjtCd
JxWPHPTbcGaWBAVqO0UlcWkdQvBYa0INY5hylEodmwQJBAPtemvhBjg
qMM68kvWbBJiwk4Qr+2Mgx7GGWjn/cB1TVuduTkf/2ovLwe5/3SvuPe
NaAB2zLLdXgc7RXyDx7vyQ=
-----END PRIVATE KEY-----"""

_NOTIFY_URL = 'http://p.51paypay.net/api/v1/pay/guangda/callback'


def sign_string(unsigned_string):
    h = SHA.new(unsigned_string)
    key = RSA.importKey(_PRIVATE_KEY)
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(SHA.new(unsigned_string.encode('utf8')))
    return binascii.b2a_hex(signature).upper()


def verify_sign(data, sign):
    """
    公钥验签
    """
    public_key = RSA.importKey(_PUBLIC_KEY)
    h = SHA.new(data)
    verifier = PKCS1_v1_5.new(public_key)
    sign = binascii.a2b_hex(sign)
    return verifier.verify(h, sign)


def gen_pay_params(amount, orderid, ordername, notify_url, clientip, appid):
    """
    only use for wehchat h5 pay
    """
    appid_detail = get_appid_detail(appid, PAY_TYPE.WECHAT_H5)
    data = {
        "action": "wallet/trans/h5Sale",
        "version": "2.0",
        "reqTime": datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        "reqId": orderid,
        "custId": appid_detail.custid,
        "totalAmount": str(int(amount * 100)),
        "orderDesc": ordername,
        "deviceIp": clientip,
        "sceneInfo": json.dumps(appid_detail.sceneInfo),
        "acquirerType": "wechat",
        "notifyUrl": notify_url
    }
    return '[%s]' % json.dumps(data)


def wechat_h5_pay(pay_record, ordername, clientip):
    amount, orderid, appid = pay_record.amount, pay_record.id, pay_record.appid
    url = 'https://cebwhaop.koolyun.com/apmp/rest/v2/'
    data = gen_pay_params(amount, orderid, ordername, _NOTIFY_URL, clientip, appid)
    sign = sign_string(data)
    appkey = 'HYM17002P-K6'  # 扫码的appkey没有-k6
    params = {
        "params": '%s' % data
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "x-appkey": appkey,
        "x-apsignature": sign
    }
    d = requests.post(url, data=params, headers=headers)
    _LOGGER.info(d.content)
    try:
        resp_data = json.loads(d.text[1:-1])
        h5_url = resp_data.get('mwUrl')
        originid = resp_data.get('transId')
        save_originid(pay_record.id, originid)
    except Exception:
        _LOGGER.exception("guangda h5 pay error")
        raise err.SystemError()
        h5_url = None
    try:
        if d.status_code == 200 and h5_url:
            return {
                'status': 0,
                'url': h5_url
            }
        else:
            raise err.SystemError(resp_data.data.get('errorMsg'))
    except Exception, e:
        _LOGGER.exception(e)
        raise err.SystemError()


def qr_pay(pay_record, order_info=None):
    appid, pay_type, amount, pay_id = pay_record.appid, pay_record.pay_type, pay_record.amount, pay_record.id
    acquirer_type = convert_accquire_type(pay_type)
    url = 'https://cebwhaop.koolyun.com/apmp/rest/v2/'
    custid = pay_record.real_custid
    _LOGGER.info('custid: %s' % custid)
    data = {
        "action": "wallet/trans/csbSale",
        "version": "2.0",
        "reqTime": datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        "reqId": pay_id,
        "custId": custid,
        "totalAmount": int(amount * 100),
        "acquirerType": acquirer_type,
        "notify_url": _NOTIFY_URL
    }
    data = '[%s]' % json.dumps(data)
    sign = sign_string(data)
    params = {
        'params': '%s' % data
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "x-appkey": 'HYM17002P',
        "x-apsignature": sign
    }
    try:
        resp = requests.post(url, data=params, headers=headers, timeout=3)
        text = resp.text
        _LOGGER.info(text)
        resp_data = json.loads(text[1:-1])
        qrCode = resp_data.get('qrCode')
        originid = resp_data.get('transId')
        save_originid(pay_record.id, originid)
    except Exception as e:
        _LOGGER.exception('get guangda qrCode error')
        raise err.SystemError()
    if qrCode:
        return {
            'status': 0,
            'qrCode': qrCode
        }
    else:
        raise err.SystemError()


def wechat_sdk_pay(pay_record, wechatid, ordername):
    appid, pay_id, amount = pay_record.appid, pay_record.id, pay_record.amount
    url = 'https://cebwhaop.koolyun.com/apmp/rest/v2/'
    custid = pay_record.real_custid
    data = {
        'action': 'wallet/trans/appSale',
        'version': '2.0',
        'reqTime': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        'appId': wechatid,
        'reqId': pay_id,
        'custId': custid,
        'orderDesc': ordername,
        'totalAmount': int(amount * 100),
        'notifyUrl': _NOTIFY_URL,
        'acquirerType': 'wechat',
    }
    data = '[%s]' % json.dumps(data)
    sign = sign_string(data)
    params = {
        'params': '%s' % data
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "x-appkey": 'HYM17002P-K6',
        "x-apsignature": sign
    }
    try:
        resp = requests.post(url, data=params, headers=headers)
        text = resp.text
        _LOGGER.info(text)
        resp_data = json.loads(text[1:-1])
        originid = resp_data.get('transId')
        save_originid(pay_record.id, originid)
        payinfo = resp_data.get('payInfo')
    except Exception as e:
        _LOGGER.exception('get wechat app pay error')
        raise err.SystemError()
    if payinfo:
        return json.loads(payinfo)
    else:
        raise err.SystemError()


def test_wechat_app_pay():
    url = 'https://cebwhaop.koolyun.com/apmp/rest/v2/'
    data = {
        'action': 'wallet/trans/appSale',
        'version': '2.0',
        'reqTime': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        'appId': 'wxc94e7b3fafedc343',
        'reqId': int(time.time() * 1000),
        'custId': '170824215224269',
        'orderDesc': '优惠充值',
        'totalAmount': '100',
        'notifyUrl': 'http://p.51paypay.net/api/v1/pay/guangda/callback',
        'acquirerType': 'wechat',
    }
    data = '[%s]' % json.dumps(data)
    sign = sign_string(data)
    params = {
        'params': '%s' % data
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "x-appkey": 'HYM17002P-K6',
        "x-apsignature": sign
    }
    resp = requests.post(url, data=params, headers=headers)
    text = resp.text
    print text


def test_qr_pay():
    acquirer_type = 'wechat'
    custid = '171024164055545'
    url = 'https://cebwhaop.koolyun.com/apmp/rest/v2/'
    pay_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    data = {
        "action": "wallet/trans/csbSale",
        "version": "2.0",
        "reqTime": pay_id,
        "reqId": pay_id,
        "custId": custid,
        "totalAmount": int(1 * 100),
        "acquirerType": acquirer_type,
        "notify_url": _NOTIFY_URL
    }
    data = '[%s]' % json.dumps(data)
    sign = sign_string(data)
    params = {
        'params': '%s' % data
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "x-appkey": 'HYM17002P',
        "x-apsignature": sign
    }
    resp = requests.post(url, data=params, headers=headers)
    print resp.content


if __name__ == "__main__":
    # test_wechat_app_pay()
    # test_qq_wallet()
    test_qr_pay()
