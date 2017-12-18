# -*- coding: utf-8 -*-
''' 支付宝批量提现接口Demo '''
import json
import hashlib
import logging
import json
import time

key = "4e0bdlvznjwnx37z4qcnhyodenyfefeo"

def generate_sign(parameter, key):
    s = ''
    for k in sorted(parameter.keys()):
        if parameter[k] != "":
            s += '%s=%s&' % (k, parameter[k])
    s = s[:-1] + key
    m = hashlib.md5()
    m.update(s.encode('utf8'))
    sign = m.hexdigest()
    return sign


def gen_params():
    data = {
        "service": "batch_trans_notify",
        "partner": "2088821170471762",
        "_input_charset": "UTF-8",
        "notify_url": "http://p.51paypay.net/api/v1/pay/ali_transfer/callbak",
        "account_name": u"武汉海羽毛网络科技有限公司",
        "detail_data": u"11112111^1213111@qq.com^张三^0.01^测试费用",
        "batch_no": "111111111117",
        "batch_num": "1",
        "batch_fee": "0.01",
        "email": "chengwm@51paypay.net",
        "pay_date": "20171209"
    }
    data['sign'] = generate_sign(data, key)
    data["sign_type"] = "MD5"
    resp = ""
    for k, v in data.items():
        resp += "%s=%s&" % (k,v)
    return resp[:-1]


if __name__ == "__main__":
    print 'https://mapi.alipay.com/gateway.do?' + gen_params()
