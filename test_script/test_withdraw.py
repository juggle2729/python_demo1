# -*- coding: utf-8 -*-

import sys
import hashlib
import json
import time

import requests

_HOST = 'http://p.51paypay.net/'
# _HOST = 'http://localhost:5000/'

# 100001  bb845b0f2e3dd8529848e2b490187f0d 海羽毛 D0 支付宝+微信
# 30000201, '295bff0773b265ac9e1f1aac5ddfad4e 深圳缘游 支付宝 H5 D1
# 30000101, '14899c0c0a2803a4c0138c5c432d697a'  上海结根 支付宝 D1
# 100000   a1223b981e74cfd29bcb628877b08b17
# '30000009', '2f1e014a755d446c82443526ec3b1907'
# 30000057, '537896a7057a267f087e5505503f8276' 海南翎麦
APP_ID = '100009'
APP_KEY = '115a7ab33f4a479cb12a7ac0996f7fb1'
#APP_ID = '30000628'
#APP_KEY = '7f112c27446447c74433344b08ec747f'


def generate_sign(parameter, key):
    s = ''
    for k in sorted(parameter.keys()):
        if parameter[k] != "":
            s += '%s=%s&' % (k, parameter[k])
    s += 'key=%s' % key
    m = hashlib.md5()
    m.update(s.encode('utf8'))
    sign = m.hexdigest()
    return sign


def test_query_balance():
    global APP_ID
    global APP_KEY
    url = _HOST + 'api/v1/pay/withdraw/balance'
    data = {
        'appid': APP_ID,
    }
    sign = generate_sign(data, APP_KEY)
    data['signature'] = sign
    resp = requests.post(url, json=data, timeout=3)
    print resp.content


def test_query_withdraw():
    global APP_ID
    global APP_KEY
    url = _HOST + 'api/v1/pay/withdraw/query'
    data = {
        'appid': APP_ID,
        'orderCode': '123'
    }
    sign = generate_sign(data, APP_KEY)
    data['signature'] = sign
    resp = requests.post(url, json=data, timeout=3)
    print resp.text


def test_withdraw():
    global APP_ID
    url = _HOST + 'api/v1/pay/withdraw/submit'
    data = {
        'appid': APP_ID,
        'amount': 1.01,
        'to_account': '371750218@qq.com',
        'channel': 'alipay_h5'
    }
    sign = generate_sign(data, APP_KEY)
    data['signature'] = sign
    resp = requests.post(url, json=data, timeout=3)
    print resp.text


if __name__ == '__main__':
    if len(sys.argv) == 3:
        # print 'Usage: python %s APP_ID, APP_KEY' % __file__
        # raise SystemExit(1)
        APP_ID, APP_KEY = sys.argv[1], sys.argv[2]
    # test_query_balance()
    # test_query_withdraw()
    test_withdraw()
