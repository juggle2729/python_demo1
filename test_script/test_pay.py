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
        'subject': 'test',
        'orderid': orderid,
        'notifyUrl': 'http://www.sina.com/',
        'payType': 23   # 只可取值2或21
    }
    sign = generate_sign(parameter_dict, APP_KEY)
    parameter_dict['signature'] = sign
    return parameter_dict


if __name__ == '__main__':
    import requests

    APP_ID = '100009'
    APP_KEY = '115a7ab33f4a479cb12a7ac0996f7fb1'
    #APP_ID = '30000628'
    #APP_KEY = '7f112c27446447c74433344b08ec747f'
    # url = "http://localhost:5000/api/v1/pay/submit"
    url = "http://p.51paypay.net/api/v1/pay/submit"

    params = create_charge(int(time.time() * 1000), 20.01)  # 10.00)
    headers = {
        "Content-Type": "application/json;charset=utf-8"
    }
    d = requests.post(url, data=json.dumps(params), headers=headers, timeout=10)
    print url
    print headers
    print params
    print d.text
