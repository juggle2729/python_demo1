# -*- coding: utf-8 -*-
import time
from random import randint, choice
import hashlib
from pprint import pprint

import dicttoxml
import xmltodict
import requests

from db.pay_record.model import PAY_TYPE
from db.account.controller import get_appid_detail
from utils import err


APPS = {
    '100008': [
         #('127560058532', '34a760f325c45180940114dcd37b6702'),
         #('127530058576', 'b9511e21414021da7f2a34ef067a9d8d'),
         #('127520058229', 'da45c11ca7fd26fb5a6771c7db76e088'),
         #('127590058259', '0682d3ffab1f9dc4246346d35990081c'),
         #('127570058067', 'f17e2d0230af263631be37bf9648ab67')
         ('127520058245', '263c53d70723d25338964ba686b1f31f'),
         ('127520058244', '4fc842a7bd9015c265e308e1b9bed8a8'),
         ('127590058274', '18eedda68a492f8924dc70d25b29efa0'),
         ('127520058243', '6081dac1aacff5a7903c1e99ab6b2e02'),
         ('127530058591', '17ab4681b11ac4ed35a20f2839b27f14')
    ],
    '100005': [
        ('399590515270', 'd50339212ab28a7fb6801568cd92d066'),
        ('399540519995', 'f8d0017a7cd18e6e2e7879518c5659d8'),
        ('399540514434', 'dfb2e9099c99812196eb3b60218bcdcf')
    ],
    '30000556': [
        ('127510058381', '1545fdb41b45f1b325a7a1ae232ae378')
    ]
}


def get_keypair_by_appid(appid):
    keypair = APPS.get(appid)
    if not keypair:
        raise err.AppIDWrong()
    return choice(keypair)

def generate_sign(parameter, skey):
    s = ''
    for k in sorted(parameter.keys()):
        if parameter[k] != "":
            s += '%s=%s&' % (k, parameter[k])
    s += 'key=%s' % skey
    m = hashlib.md5()
    m.update(s.encode('utf8'))
    sign = m.hexdigest()
    return sign.upper()

def get_skey(wanted_sid):
    for keypairs in APPS.values():
        for sid, skey in keypairs:
            if sid == wanted_sid:
                return skey
    raise err.AppIDWrong

def check_sign(data, sign):
    sid = data['mch_id']
    skey = get_skey(sid)
    calc_sign = generate_sign(data, skey)
    return calc_sign == sign


def check_traffic_sign(data, sign):
    calc_sign = generate_traffic_sign(data)
    return calc_sign == sign


def verify_sign(data):
    data = xmltodict.parse(data)['xml']
    data = dict(data)
    from pprint import pprint
    pprint(data)
    sign = data.pop('sign')
    print check_sign(data, sign)


def generate_traffic_sign(parameter):
    TRAFFIC_KEY = 'dfb2e9099c99812196eb3b60218bcdcf'
    s = ''
    for k in sorted(parameter.keys()):
        if parameter[k] != "":
            s += '%s=%s&' % (k, parameter[k])
    s += 'key=%s' % TRAFFIC_KEY
    m = hashlib.md5()
    m.update(s.encode('utf8'))
    sign = m.hexdigest()
    return sign.upper()


def qq_traffic_pay(amount, orderid):
    """
    QQ流量充值
    """
    TRAFFIC_KEY = 'dfb2e9099c99812196eb3b60218bcdcf'
    TRAFFIC_MCH_ID = '399540514434'

    qq_type = 'pay.tenpay.native'
    url = 'https://pay.swiftpass.cn/pay/gateway'
    nonce_str = str(randint(10000, 99999))
    orderid = long(orderid)

    data = {
        'service': qq_type,
        'version': '2.0',
        'charset': 'UTF-8',
        'sign_type': 'MD5',
        'mch_id': TRAFFIC_MCH_ID,
        'out_trade_no': str(orderid),
        'body': u'流量充值',
        'total_fee': str(amount),
        'mch_create_ip': '127.0.0.1',
        'notify_url': 'http://pay.52paypay.net/admin/service/qq/pay_callback',
        # 'notify_url': 'http://pay.51paypay.net/api/v1/pay/swiftpass_traffic/callback',
        'nonce_str': nonce_str,
    }

    sign = generate_traffic_sign(data)
    data['sign'] = sign
    post_data = dicttoxml.dicttoxml(data, custom_root='xml')
    print post_data
    resp = requests.post(url, post_data)
    if resp.status_code != 200:
        print 'error', resp.text
    resp_data = xmltodict.parse(resp.text)['xml']
    pprint(resp_data)
    sign = resp_data.pop('sign')
    calc_sign = generate_traffic_sign(resp_data)
    if calc_sign != sign:
        print 'error', 'sign not pass'
    _status = resp_data['status']
    if _status == '0':
        result_code = resp_data['result_code']
        if result_code == '0':
            code_url = resp_data['code_url']
            code_img_url = resp_data['code_img_url']
            print code_url, code_img_url
            return code_url   # , code_img_url
        else:
            print resp_data['err_code'], resp_data['err_msg']
    else:
        print _status, resp_data['message']


def test_qr_pay():
    wechat_type = 'pay.weixin.native'
    alipay_type = 'pay.alipay.native'
    qq_type = 'pay.tenpay.native'

    url = 'https://pay.swiftpass.cn/pay/gateway'
    nonce_str = str(randint(10000, 99999))
    orderid = int(time.time())

    data = {
        # 'service': alipay_type,
        'service': wechat_type,
        'version': '2.0',
        'charset': 'UTF-8',
        'sign_type': 'MD5',
        'mch_id': REAL_MCH_ID,
        'out_trade_no': str(orderid),
        'body': u'支付测试',
        'total_fee': '1',
        'mch_create_ip': '127.0.0.1',
        'notify_url': 'http://p.51paypay.net/api/v1/pay/swiftpass/callback',
        'nonce_str': nonce_str,
    }
    sign = generate_sign(data)
    data['sign'] = sign
    post_data = dicttoxml.dicttoxml(data, custom_root='xml')
    print post_data
    resp = requests.post(url, post_data)
    if resp.status_code != 200:
        print 'error', resp.text
    resp_data = xmltodict.parse(resp.text)['xml']
    pprint(resp_data)
    sign = resp_data.pop('sign')
    calc_sign = generate_sign(resp_data)
    if calc_sign != sign:
        print 'error', 'sign not pass'
    _status = resp_data['status']
    if _status == '0':
        result_code = resp_data['result_code']
        if result_code == '0':
            code_url = resp_data['code_url']
            code_img_url = resp_data['code_img_url']
            print code_url, code_img_url
        else:
            print resp_data['err_code'], resp_data['err_msg']
    else:
        print _status, resp_data['message']


def qr_pay(pay_record, order_info=None):
    _TRANS_PAY_TYPE = {
        PAY_TYPE.WECHAT_QR: 'pay.weixin.native',
        PAY_TYPE.ALIPAY_QR: 'pay.alipay.native',
        PAY_TYPE.QQ_QR: 'pay.tenpay.native'
    }

    appid, pay_type, amount, pay_id = pay_record.appid, pay_record.pay_type, pay_record.amount, pay_record.id
    appid_detail = get_appid_detail(appid, pay_type)
    if not appid_detail:
        raise err.AppIDWrong()
    trans_pay_type = _TRANS_PAY_TYPE[pay_type]
    #custid = appid_detail.custid
    sid, skey = get_keypair_by_appid(appid)
    url = 'https://pay.swiftpass.cn/pay/gateway'
    nonce_str = str(randint(10000, 99999))

    data = {
        'service': trans_pay_type,
        'version': '2.0',
        'charset': 'UTF-8',
        'sign_type': 'MD5',
        'mch_id': sid,
        'out_trade_no': pay_id,
        'body': u'购买商品',
        'total_fee': '%s' % int(amount * 100),
        'mch_create_ip': '127.0.0.1',
        'notify_url': 'http://p.51paypay.net/api/v1/pay/swiftpass/callback',
        'nonce_str': nonce_str,
    }
    sign = generate_sign(data, skey)
    data['sign'] = sign
    print data
    post_data = dicttoxml.dicttoxml(data, custom_root='xml')
    print post_data
    resp = requests.post(url, post_data)
    if resp.status_code != 200:
        print 'error', resp.text
    resp_data = xmltodict.parse(resp.text)['xml']
    pprint(resp_data)
    sign = resp_data.pop('sign')
    calc_sign = generate_sign(resp_data, skey)
    if calc_sign != sign:
        print 'error', 'sign not pass'
    _status = resp_data['status']
    if _status == '0':
        result_code = resp_data['result_code']
        if result_code == '0':
            code_url = resp_data['code_url']
            code_img_url = resp_data['code_img_url']
            return {
                'qrCode': code_url,
                'status': 0
            }
        else:
            print  resp_data['err_code'], resp_data['err_msg']
            return {
                'error': resp_data['err_msg'],
                'status': 0
            }
    else:
        print _status, resp_data['message']
        return {
            'error': resp_data['message'],
            'status': 0
        }


if __name__ == "__main__":
    # print xml2dict(dict2xml({"a": 1, "b": 123}))
    # print dict2xml({"a": 1, "b": 123})
    # test_qr_pay()
    qq_traffic_pay(1, 13223434348821)
    callback_data = """<xml><bank_type><![CDATA[ALIPAYACCOUNT]]></bank_type>
    <buyer_logon_id><![CDATA[308***@qq.com]]></buyer_logon_id>
    <buyer_user_id><![CDATA[2088012072223887]]></buyer_user_id>
    <charset><![CDATA[UTF-8]]></charset>
    <fee_type><![CDATA[CNY]]></fee_type>
    <fund_bill_list><![CDATA[[{"amount":"1.00","fundChannel":"ALIPAYACCOUNT"}]]]></fund_bill_list>
    <gmt_create><![CDATA[20171110133649]]></gmt_create>
    <mch_id><![CDATA[399540514434]]></mch_id>
    <nonce_str><![CDATA[1510292226086]]></nonce_str>
    <openid><![CDATA[2088012072223887]]></openid>
    <out_trade_no><![CDATA[1510292197]]></out_trade_no>
    <out_transaction_id><![CDATA[2017111021001004880203984470]]></out_transaction_id>
    <pay_result><![CDATA[0]]></pay_result>
    <result_code><![CDATA[0]]></result_code>
    <sign><![CDATA[A88EB8E9C43E9CE56A302BF22E7BFB4D]]></sign>
    <sign_type><![CDATA[MD5]]></sign_type>
    <status><![CDATA[0]]></status>
    <time_end><![CDATA[20171110133705]]></time_end>
    <total_fee><![CDATA[100]]></total_fee>
    <trade_type><![CDATA[pay.alipay.native]]></trade_type>
    <transaction_id><![CDATA[399540514434201711104298061303]]></transaction_id>
    <version><![CDATA[2.0]]></version>
    </xml>
    """
    # verify_sign(callback_data)
