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
        'amount': '0.1',
        'appid': APP_ID,
        'orderid': orderid,
        'notifyUrl': 'http://127.0.0.1:5001/notify',
        'payType': 2,
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

    # 30000101 | 14899c0c0a2803a4c0138c5c432d697a
    # 100002   appkey: 880357ccd28db91f6f0f88d54889c34c
    # 30000502,'5f247c528511c56770bb8499a9681074 广州莱双 招行D1
    # 30000501,'5f247c528511c56770bb8499a9681074 广州莱双 浦发D0
    # 30000402, 03c49e032ba9ae9f86ecd293374a01b7  深圳市路宣科技有限公司
    # 30000402, 'a0fc20371ab7b37e74654ce60f6e3426' 华盛恒力
    # 30000401, 'b4b17abeb61b9e852e90a7805fa8f77d' 牛牛乐
    # 30000301, 'a1223b981e74cfd29bcb628877b08b17'  武汉趣享互动
    # 30000201, '295bff0773b265ac9e1f1aac5ddfad4e 深圳缘游 支付宝 H5 D1
    # 30000101, '14899c0c0a2803a4c0138c5c432d697a'  上海结根 支付宝 D1
    # 100000   a1223b981e74cfd29bcb628877b08b17
    # '30000009', '2f1e014a755d446c82443526ec3b1907'
    # 30000057, '537896a7057a267f087e5505503f8276' 海南翎麦
    # 100003 880357ccd28db91f6f0f88d54889c34c 商户轮询测试
    # 30000410 03c49e032ba9ae9f86ecd293374a01b7

    # 长沙市雨花区王佳妮小吃店  招行 D1  5b4f3a73c6b340b7961a787db3ba202e  30000540
    # 盱眙杨娟酒业有限公司 浦发 D0 8f721e6515674fe6bfab2a00eaf771c0  30000541
    # 新罗区冬平伊便利店 浦发 D0 0c21a683d2e0423ab73895b7d6c8472e 30000543
    # 博罗县福田镇钟锦荣水产养殖场 浦发 D0 748e6830873344ba9d9bb9a0d938c72a 30000544
    # 广州莱双信息科技有限公司 浦发 D0 5f247c528511c56770bb8499a9681074  30000501
    # 北京达书亮科技有限公司  b60963fb7fbb494fa8779df266670fd3 30000545

    # 王佳尼 5b4f3a73c6b340b7961a787db3ba202e  30000540
    # 1386157083764f518ed612fb9f58503e 30000546
    # 亿昆  D1 30000550, 'b1bccea3a1834169a1bdb648bc4ba97a'
    # 9b3c275cfaaf4c65a71995388169419d  30000551
    # 广州珐嘉贸易有限公司  30000554  0e03007ab9674602a6f35572663fe355
    # 深圳市桂春贸易有限公司 30000553  c6b77f3f53b5484887c61d901f211574


    # 100003	880357ccd28db91f6f0f88d54889c34c
    APP_ID = '30000546'
    APP_KEY = '1386157083764f518ed612fb9f58503e'
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
    url = "http://test.51paypay.net/api/v1/pay/submit"
    params = create_charge(int(time.time() * 1000), 1)
    headers = {
        "Content-Type": "application/json;charset=utf-8"
    }
    d = requests.post(url, data=json.dumps(params), headers=headers, timeout=3)
    print url
    print headers
    print params
    print d.content
