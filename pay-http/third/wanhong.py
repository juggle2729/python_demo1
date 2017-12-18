# -*- coding: utf-8 -*-
"""
万洪支付通道
"""
from urlparse import parse_qs
import time
import json
import binascii
import datetime
import logging
import base64
from pprint import pprint

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA, SHA256
from Crypto.PublicKey import RSA
import requests

from db.pay_record.model import PAY_TYPE
from db.account.controller import get_account_appid
from utils import err
from utils import tz

_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEA5ynjiZLohxGwLDEGniPOGhi2zSCiK/0Ex5Kaa8S4d5ZqsLNj
O9tdiP+90IDPvku8KBMzuiy/hcb/G8PN0KFJ0AXZNvlUNIQBNocR701U6YyTv2/B
hPkfd7gbfMSkFHmeIhADT6FFzR3/T9xPi4IXBac/tJ4J3ynMX2nuyLT5VrKOz833
6iPnxfNUdBF76Eewoaucq8j4lGmX1gbLwTHl0dLyg2NFH8ohWbwas7oe4+gzCymD
3io+USGocrfB5VEnVwN9xiFpmACdlYrsbydh0SEx99W2KnFe+sdFU57AVg04sU01
QLaXrL09t/7focfQw9Qtpq0hbzMniCxbIy5rSQIDAQABAoIBAH3LfddP6toV9hkW
VNOaCH6LFG9sYtQtTHyOexpKY1gwsr6V4FqidbQn99OPRX35GNt2F6Ao2dCjChDB
7S6rls9tX1dbN0eczkwuFMR1ANBXf8+dsWH7b/RmbA7ps6Cwzi0bKbIbwTBuMpHz
AhaZJI4fBbv0hMq8pEsICrmOQmG6oNiwkCM9YUlfSqroHxc1LAyffyUedYrHi1kZ
o6reyfXSIoZaCWzidl5Dl5CXwAQYmSTdbrN/WO/6L5/c/1Ys6g01IBToE/0djNel
aB9SVFka6KPRi5bIDw70pnD752hWsMvJQgJbTfH0zV+h4LtVc4LpJfNJrJIsvstn
3ij81UECgYEA9B4sxfMY/suHne5RhUI8w0xKBLFekvEklWuMWPN/pRtuZjeRsZtm
cuh3UJD6adGc+6x371hUcPb8GCudW1tp0pblIQoJu+egRoX1EaORb8rESJWLFc17
yHzSnIyPUHu4mHRwDnwLaOFebV64FbWOE03yP2xAY0hL8Dk4JaICxbMCgYEA8mpM
QgREpaC4Dxz8pa8zN0iqNYTToz7pbiPsv0LTS3mqURZwL27xJyTv37KLrQ/R9G5E
GlDnSO9tzpGqMrf8O2ku64knzvVGbWtVil3USE9MPvTEQarNHmx40AQHVlNlVBMZ
7DnzE5g+FiVBRfr/LM3/Ce690+NrZq7OPWxNxRMCgYEA6hY1YOwnv8xzk2IAEgTe
N3hkUfOzeLx8FDw5LOLyN+UCDEqlDuaxaua34y3isq4qFrvflkfhUSHFw3evQPd7
llDUDsaNZv5JltbFldB/me+aIPAlmxab6DipzSyMEOVSsf6VpY4VctEJt17orwiV
4LUR4vdvFsUw7H4x9QRSHDkCgYEAh0ET50mmW5s+1v/fXzpPoyrh/RZtVwoFCDT3
JQfOCLCLfM6+LVkDKEoNpIxkLl1DUdQsH1rAkQs2Ayl3AvFwxF09lqFiGrDzaJ2Y
jqknhmjoK8A5uEHqTG1NQxLcXSgOw0gdEJaMr4QkMAr9TmRq976/6/TO6WhcRmCG
JfNFuQ0CgYEAjuUQYBCEjRuwfp3tV6g369nFwv5BIEYlgPPsqN7+6y+xJBd9ApnB
wOwbNTDSA7lW2pxeAKs16/ZyzsUx//hr3/nEkQxIiTbnWtJOHP1l5xNGvwYb4Blr
NC5Faab1jJXFUbLBc4tx0lWDQOIwByuFuXOijWcA+zsiHmdTC1eMN0A=
-----END RSA PRIVATE KEY-----"""

_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5ynjiZLohxGwLDEGniPO
Ghi2zSCiK/0Ex5Kaa8S4d5ZqsLNjO9tdiP+90IDPvku8KBMzuiy/hcb/G8PN0KFJ
0AXZNvlUNIQBNocR701U6YyTv2/BhPkfd7gbfMSkFHmeIhADT6FFzR3/T9xPi4IX
Bac/tJ4J3ynMX2nuyLT5VrKOz8336iPnxfNUdBF76Eewoaucq8j4lGmX1gbLwTHl
0dLyg2NFH8ohWbwas7oe4+gzCymD3io+USGocrfB5VEnVwN9xiFpmACdlYrsbydh
0SEx99W2KnFe+sdFU57AVg04sU01QLaXrL09t/7focfQw9Qtpq0hbzMniCxbIy5r
SQIDAQAB
-----END PUBLIC KEY-----"""


def generate_sign(data):
    keys = data.keys()
    keys.sort()
    unsigned_string = u'&'.join(u'%s=%s' % (key, data[key]) for key in keys)
    print unsigned_string
    key = RSA.importKey(_PRIVATE_KEY)
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(SHA.new(unsigned_string.encode('utf8')))
    return base64.b64encode(signature)


def verify_sign(data):
    sign = data.pop('signature')
    public_key = RSA.importKey(_PUBLIC_KEY)
    keys = data.keys()
    keys.sort()
    h = SHA.new(('&'.join('%s=%s' % (key, data[key]) for key in keys)).encode('utf-8'))
    verifier = PKCS1_v1_5.new(public_key)
    return verifier.verify(h, base64.b64decode(sign))


def test_web_bank():
    import time
    _URL = 'http://115.182.112.96/trans-api/trans/api/back'
    # _URL = 'http://api.wanhongpay.com/trans-api/trans/api/back'
    data = {
        # 'merNo': '850420050945224',
        'merNo': '800001702700003',
        'version': '1.0.0',
        'transType': 'SALES',
        'productId': '0001',
        'orderDate': time.strftime('%Y%m%d', time.localtime()),
        'orderNo': int(time.time() * 1000),
        'transAmt': 500,
        'notifyUrl': 'http://www.baidu.com/',
        'commodityName': u'优惠充值',
        'commodityDetail': u'真的很优惠哟',
        'bankAbbr': 'CMB',
        'returnUrl': 'http://www.baidu.com/'
    }
    sign = generate_sign(data)
    print sign
    data['signature'] = sign
    resp = requests.post(_URL, data=data)
    print resp.request.body
    print 'resp.text: ', resp.text
    # print verify_sign(d)


def daifu():
    _URL = 'http://api.wanhongpay.com/trans-api/trans/api/back.json'
    data = {
        'merNo': '800001702700003',
        # 'merNo': '850420050945224',
        'version': '1.0.0',
        'transType': 'PROXY_PAY',
        'productId': '8001',
        'orderDate': time.strftime('%Y%m%d', time.localtime()),
        'orderNo': int(time.time() * 1000),
        'transAmt': 100,
        'notifyUrl': 'http://www.baidu.com/',
        'commodityName': u'优惠充值',
        'commodityDetail': u'真的很优惠哟',
        'bankAbbr': 'CMB',
        'phoneNo': '18062596910',
        'cardName': u'帅锅',
        'cardType': '01',
        'cerdId': '420821199909090099',
        'cardNo': '6217857600035798680',
        'accBankNo': u'中国银行',
        'isCompany': u'0'
    }
    sign = generate_sign(data)
    print sign
    data['signature'] = sign
    resp = requests.post(_URL, data=data)
    print resp.request.body
    pprint(json.loads(resp.text))
    # print verify_sign(d)


def get_balance():
    """
    获取可用余额
    """
    pass


def test_daifu(orderno, amount):
    _URL = 'http://115.182.112.96/trans-api/trans/api/back.json'
    # _URL = 'http://api.wanhongpay.com/trans-api/trans/api/back.json'
    data = {
        'merNo': '800001702700003',
        # 'merNo': '850420050945224',
        'version': '1.0.0',
        'transType': 'PROXY_PAY',
        'productId': '8005',
        'orderDate': time.strftime('%Y%m%d', time.localtime()),
        'orderNo': orderno,
        'transAmt': int(amount * 100),
        'notifyUrl': 'http://p.51paypay.net/api/v1/pay/wanhong/callback',
        'commodityName': u'优惠充值',
        'commodityDetail': u'真的很优惠哟',
        'bankAbbr': 'CMB',
        'phoneNo': '18062596910',
        'cardName': u'邱阳',
        'cardType': '01',
        'cerdId': '420821199909090099',
        'cardNo': '6217857600035798680',
        'accBankNo': u'中国银行',
        'isCompany': u'0'
    }
    sign = generate_sign(data)
    print sign
    data['signature'] = sign
    resp = requests.post(_URL, data=data)
    pprint(json.loads(resp.text))
    # print verify_sign(d)


def test_union_qr():
    _URL = 'http://115.182.112.96/trans-api/trans/api/back.json'
    data = {
        'version': '1.0.0',
        'transType': 'SALES',
        'productId': '0101',  # 0130 qq钱包, 0101 微信扫码, 0103 支付宝扫码
        'merNo': '800001702700003',
        'orderDate': time.strftime('%Y%m%d', time.localtime()),
        'orderNo': int(time.time()),
        'notifyUrl': 'http://p.51paypay.net/api/v1/pay/wanhong/callback',
        'transAmt': '1000',
        'commodityName': u'充值',
    }
    sign = generate_sign(data)
    print sign
    data['signature'] = sign
    resp = requests.post(_URL, data=data)
    print resp.request.body
    resp_data = json.loads(resp.text)
    pprint(resp_data)


_TRANS_PAY_TYPE = {
    PAY_TYPE.QQ_QR: '0130',
    PAY_TYPE.WECHAT_QR: '0101',
    PAY_TYPE.ALIPAY_QR: '0103'
}


def qr_pay(pay_record, order_info=None):
    url = 'http://115.182.112.96/trans-api/trans/api/back.json'
    appid, pay_type, amount, pay_id = pay_record.appid, pay_record.pay_type, pay_record.amount, pay_record.id
    appid_detail = get_account_appid(appid, pay_type)
    trans_pay_type = _TRANS_PAY_TYPE[pay_type]
    if not appid_detail:
        raise err.AppIDWrong()
    custid = appid_detail.custid
    data = {
        'version': '1.0.0',
        'transType': 'SALES',
        'productId': trans_pay_type,
        'merNo': custid,
        'orderDate': tz.ts_to_local_date_str(tz.now_milli_ts()),
        'orderNo': int(time.time()),
        'notifyUrl': 'http://p.51paypay.net/api/v1/pay/wanhong/callback',
        'transAmt': int(amount * 100),
        'commodityName': order_info,
    }
    sign = generate_sign(data)
    data['signature'] = sign
    resp = requests.post(url, data=data)
    resp_data = json.loads(resp.text)
    respCode = resp_data.get('respCode')
    codeUrl = resp_data.get('codeUrl')
    if respCode == '0000':
        return {
            'status': 0,
            'qrCode': codeUrl
        }
    else:
        respDesc = resp_data.get('respDesc')
        raise err.SystemError(respDesc)


if __name__ == "__main__":
    # test_web_bank()
    # test_union_qr()
    # test_daifu()
    orderno = int(time.time())
    amount = 1
    daifu(orderno, amount)
