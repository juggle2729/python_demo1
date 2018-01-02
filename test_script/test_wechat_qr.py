# -*- coding: utf-8 -*-

import sys
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
        'amount': '11.3',
        'appid': APP_ID,
        'orderid': orderid,
        'notifyUrl': 'http://127.0.0.1:5001/notify',
        'payType': 23,
        'clientip': '192.168.1.6',
        'orderInfo': u'会员充值',
        # 'subject': u'会员充值'
    }
    sign = generate_sign(parameter_dict, APP_KEY)
    print sign
    parameter_dict['signature'] = sign
    return parameter_dict


if __name__ == '__main__':
    import requests

    APP_ID = '30000637'
    APP_KEY = 'c297a5d032f7c523e5d6428895b98c99'
    # APP_ID = '30000546'
    # APP_KEY = '1386157083764f518ed612fb9f58503e'
    if len(sys.argv) == 3:
        APP_ID = sys.argv[1]
        APP_KEY = sys.argv[2]
    # APP_ID = '30000541'
    # APP_KEY = '8f721e6515674fe6bfab2a00eaf771c0'
    # APP_ID = '30000543'
    # APP_KEY = '0c21a683d2e0423ab73895b7d6c8472e'
    # APP_ID = '30000544'
    # APP_KEY = '748e6830873344ba9d9bb9a0d938c72a'
    # APP_ID = '30000542'
    # APP_KEY = '5f247c528511c56770bb8499a9681074'
    # url = "http://localhost:5000/api/v1/pay/submit"
    # url = "http://47.96.154.221/api/v1/pay/submit"
    url = 'http://192.168.200.93/api/v1/pay/submit'
    params = create_charge(int(time.time() * 1000), 1)
    headers = {
        "Content-Type": "application/json;charset=utf-8"
    }
    d = requests.post(url, data=json.dumps(params), headers=headers, timeout=3)
    print url
    print headers
    print params
    print d.content
