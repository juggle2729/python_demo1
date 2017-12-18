# -*- coding: utf-8 -*-

import hashlib
import logging
import json
import time

import requests

_LOGGER = logging.getLogger('pay')


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


def create_charge(orderid, pay_amount, ip):
    parameter_dict = {
        # 'version': version,
        'amount': pay_amount,
        'appid': APP_ID,
        'subject': u'优惠充值',
        'orderid': orderid,
        'clientip': ip,
        'notifyUrl': 'http://www.baidu.com/',
        'payType': 1
    }
    sign = generate_sign(parameter_dict, APP_KEY)
    parameter_dict['signature'] = sign
    return parameter_dict


def check_data(data):
    sign = data.pop('signature')
    calculated_sign = generate_sign(data, _KEY)
    if sign.lower() != calculated_sign:
        _LOGGER.info("mingtianyun sign: %s, calculated sign: %s",
                     sign, calculated_sign)
        raise err.ParamError('sign not pass, data: %s' % data)
    return data


def test_pay():
    pass


def test_query():
    # APP_ID = '10000002'
    # APP_KEY = '880357ccd28db91f6f0f88d54889c34c'
    # url = "http://192.168.200.46/api/v1/pay/query"
    APP_ID = '100000'
    APP_KEY = 'a1223b981e74cfd29bcb628877b08b17'
    url = "http://p.51paypay.net/api/v1/pay/query"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'appid': APP_ID,
        'orderid': 1505444528273
    }
    sign = generate_sign(data, APP_KEY)
    data['signature'] = sign
    d = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
    print url
    print headers
    print d.text


if __name__ == '__main__':
    test_query()
