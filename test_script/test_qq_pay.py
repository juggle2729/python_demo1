# -*- coding: utf-8 -*-

import hashlib
import logging
import json
import time

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


def create_charge(orderid, pay_amount):
    parameter_dict = {
        # 'version': version,
        'amount': pay_amount,
        'appid': APP_ID,
        'orderid': orderid,
        'notifyUrl': 'http://www.baidu.com/',
        'payType': 11
    }
    sign = generate_sign(parameter_dict, APP_KEY)
    parameter_dict['signature'] = sign
    return parameter_dict


if __name__ == '__main__':
    import requests

    APP_ID = '30000006'
    APP_KEY = '526afbd42ea892cde90c9230fc3a1164'
    # url = "http://192.168.200.46/api/v1/pay/submit"
    url = "http://p.51paypay.net/api/v1/pay/submit"

    params = create_charge(int(time.time() * 1000), 1)
    headers = {
        "Content-Type": "application/json;charset=utf-8"
    }
    d = requests.post(url, data=json.dumps(params), headers=headers, timeout=10)
    print url
    print headers
    print params
    print d.text
