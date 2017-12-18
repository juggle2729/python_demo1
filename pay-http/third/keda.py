# -*- coding: utf-8 -*-
"""
客达文化支付接口
"""
import time
import json
import pyDes
import base64
import requests
import logging
import copy

from db.pay_record.model import PAY_TYPE
from handler.pay import get_appid_detail
from db.pay_record.controller import save_originid
from utils import err

_LOGGER = logging.getLogger(__name__)

# product args
_MERCHANTCODE = '00000000353000000042'
_OFFICECODE = '0000000035'
_KEY = 'UyRk88Ec'

_BANK_ZHAOHANG = '308584000013'
_BANK_PUFA = '310290000013'
_NOTIFY_URL = 'http://p.51paypay.net/api/v1/pay/keda/callback'


def test_wechat_qr():
    """
    客达接口返回数据格式:
    {
        "message": "请求正常",
        "error": 0,
        "data": {
            "picURL": "weixin://wxpay/bizpayurl?pr=P8otqp5",
            "merchantcode": "00000000301000000021",
            "orderCode": "1506305827408",
            "platformTradeCode": "wx20170925101705223",
            "orderMoney": "100"
        },
        "success": true
    }
    """
    des_key = '12345678'
    data = json.dumps({
        'bankLinkNumber': '308584000013',
        'orderInfo': '订单详情',
        'orderMoney': 100,
        'orderCode': int(time.time() * 1000),
        'notifyUrl': 'http://localhost',
        'tradeType': 'NATIVE',
        'productId': '101',
        'paymentType': 'D0'
    }, ensure_ascii=False)
    print data
    k = pyDes.des(des_key, pyDes.ECB, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = base64.b64encode(k.encrypt(data))
    print d
    assert k.decrypt(k.encrypt(data), padmode=pyDes.PAD_PKCS5) == data
    url = 'http://116.62.100.174/Bank/mobile/zhBank/placeOrder'

    resp = requests.post(url, json={
        'officeCode': _OFFICECODE,
        'merchantcode': _MERCHANTCODE,
        'date': d
    })
    print resp.request.url
    print resp.request.body
    print resp.text


def test_alipay_qr():
    """
    {
        "message": "下单成功！",
        "error": 0,
        "data": {
            "orderInfo": "订单详情",
            "platformTradeCode": "AL20170925102516685",
            "deviceNo": "null",
            "orderCode": "1506306318588",
            "picURL": "https://qr.alipay.com/bax07561wvsaceq7ffro60d5",
            "orderMoney": "100",
            "merchantcode": "00000000301000000021",
            "bankLinkNumber": "308584000013"
        },
        "success": true
    }
    """
    des_key = '12345678'
    data = json.dumps({
        'bankLinkNumber': '308584000013',
        'orderInfo': '订单详情',
        'orderMoney': 100,
        'orderCode': int(time.time() * 1000),
        'notifyUrl': 'http://localhost',
        'tradeType': 'NATIVE',
        'productId': '101',
        'paymentType': 'D0'
    }, ensure_ascii=False)
    print data
    k = pyDes.des(des_key, pyDes.ECB, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = base64.b64encode(k.encrypt(data))
    print d
    assert k.decrypt(k.encrypt(data), padmode=pyDes.PAD_PKCS5) == data
    url = 'http://116.62.100.174/Bank/mobile/zhBank/aliScanPay'

    resp = requests.post(url, json={
        'officeCode': _OFFICECODE,
        'merchantcode': _MERCHANTCODE,
        'date': d
    })
    print resp.request.url
    print resp.request.body
    print resp.text


def query_d0_balance(merchantcode):
    """
    {"message":"请求正常","error":0,"data":{"state":"SUCCESS","wxBalance":"0","merchantcode":"00000000353000000042","aliBalance":"0"},"success":true}
    """
    url = 'http://116.62.100.174/Bank/mobile/zhBank/getBalance'
    data = {
        'officeCode': _OFFICECODE,
        'merchantcode': merchantcode,
        'bankLinkNumber': _BANK_PUFA,
    }
    d = crypto_data(data)
    data['date'] = d

    resp = requests.post(url, json=data, timeout=3)
    _LOGGER.info(resp.request.body)
    text = resp.content
    _LOGGER.info(resp.text)
    resp_data = json.loads(text)
    return resp_data


def jinjian():
    url = 'http://116.62.100.174/Bank/mobile/zhBank/addMerchant'
    data = {
        'officeCode': _OFFICECODE,
        'bankLinkNumber': _BANK_PUFA,
        'mchName': '武汉海羽毛网络科技有限公司',
        'mchShortName': '海羽毛网络',
        'city': '武汉市',
        'province': '湖北省',
        'address': '武汉市东湖新技术开发区光谷大道3号激光工程设计总部二期研发楼06幢06单元15层5号（Y121)',
        'mobile': '13125059010',
        'bankNo': '308521015549',
        'industryNo': '161215010100351',
        'balanceType': '1',
        'balanceName': '武汉海羽毛网络科技有限公司',
        'userIdNumber': '410728197310055000',
        'legalIdNumber': '410728197310055000',
        'cardNumber': '127910189610101',
        'contact': '陈喻君',
        'licenseNum': '91420100MA4KUKQM6K',
        'licenseStartDate': '20170620',
        'licensePeriod': '1',  # 和licenseEndDate 二选一填写
        # 'licenseEndDate': '',
        'licenseScope': '计算机系统开发、系统集成：网络系统开发；通信设备技术咨询',
        'wxValue': '40',
        'aliValue': '40',
        'paymentType': 'D0',
        'zfbpay': 40,
        'wxpay': 40,
        'notifyUrl': 'http://p.51paypay.net/api/v1/callback',
    }
    post_files = {
        'userIDCardA': open('farenA.png', 'rb'),
        # 'userIDCardB': open(u'farenB.png', 'rb'),
        # 'legalIDCardA': open(u'farenA.png', 'rb'),
        # 'legalIDCardB': open(u'farenA.png', 'rb'),
        # 'licenseImg': open('license.png', 'rb'),
        # 'cardImgA': ('cardImgA', open(u'')),
    }

    auth_str = json.dumps({'officeCode': _OFFICECODE, 'Key': _KEY})
    k = pyDes.des(_KEY, pyDes.ECB, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = base64.b64encode(k.encrypt(auth_str))

    headers = {'Authorization': d}

    resp = requests.post(url=url, data=data, headers=headers, files=post_files, timeout=3)
    _LOGGER.info("keda jinjian request headers: %s", resp.request.headers)
    _LOGGER.info("keda jinjian response content: %s", resp.content)


def qr_pay(pay_record, order_info):
    """
    response:
    {"message":"您的支付宝支付未激活","error":-1,"success":false}
    """
    appid, pay_type, amount, pay_id = pay_record.appid, pay_record.pay_type, pay_record.amount, pay_record.id
    appid_detail = get_appid_detail(appid, pay_type)
    if not appid_detail:
        raise err.AppIDWrong()
    custid = appid_detail.custid
    banklinknumber = appid_detail.banklinknumber
    paymenttype = appid_detail.paymenttype
    data = {
        'bankLinkNumber': banklinknumber,
        'orderInfo': order_info,
        'orderMoney': int(amount * 100),
        'orderCode': pay_id,
        'notifyUrl': _NOTIFY_URL,
        'paymentType': paymenttype
    }
    if pay_type == PAY_TYPE.WECHAT_QR:
        url = 'http://116.62.100.174/Bank/mobile/zhBank/placeOrder'
        data['tradeType'] = 'NATIVE'
        data['productId'] = '101'
    elif pay_type in (PAY_TYPE.ALIPAY_QR, PAY_TYPE.ALIPAY_H5):
        url = 'http://116.62.100.174/Bank/mobile/zhBank/aliScanPay'
        data['limitPay'] = 'pcredit,pcreditpayInstallment,creditCard,creditCardExpress,creditCardCartoon,credit_group'
    else:
        raise ValueError('not support pay type')
    k = pyDes.des(_KEY, pyDes.ECB, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = base64.b64encode(k.encrypt(json.dumps(data)))

    resp = requests.post(url, json={
        'officeCode': _OFFICECODE,
        'merchantcode': custid,
        'date': d
    }, timeout=3)
    resp_data = json.loads(resp.text)
    if resp_data['error'] == 0:
        orginid = resp_data['data']['platformTradeCode']
        save_originid(pay_record.id, orginid)
        return {
            'status': 0,
            'qrCode': resp_data['data']['picURL']
        }
    else:
        raise err.SystemError(resp_data['message'])


def query_merchant():
    url = 'http://116.62.100.174/Bank/mobile/zhBank/getMerchant'
    data = {
        'merchantcode': _MERCHANTCODE,
        'bankLinkNumber': _BANK_PUFA,
        'officeCode': _OFFICECODE,
    }
    resp = requests.post(url, data, timeout=3)
    print resp.text


def withdraw(merchantcode, amount, channel):
    """
    {"message":"23:00-10:00间不能提现","error":-1,"success":false}
    """
    url = 'http://116.62.100.174/Bank/mobile/zhBank/withdraw'
    data = {
        'merchantcode': merchantcode,
        'bankLinkNumber': _BANK_PUFA,
        'fee': int(amount * 100),
        'channel': channel,
        'officeCode': _OFFICECODE
    }
    d = crypto_data(data)
    data['date'] = d
    resp = requests.post(url, json=data, timeout=3)
    text = resp.text
    _LOGGER.info("keda withdraw response: %s", text)
    resp_data = json.loads(text)
    return resp_data


def query_d0_withdraw(office_code, order_code):
    url = 'http://116.62.100.174/Bank/mobile/zhBank/querywithdraw'
    data = {
        'merchantcode': _MERCHANTCODE,
        'bankLinkNumber': _BANK_PUFA,
        'orderCode': order_code,
        'officeCode': _OFFICECODE
    }
    d = crypto_data(data)
    data['date'] = d
    resp = requests.post(url, json=data, timeout=3)
    text = resp.text
    _LOGGER.info("keda query d0 withdraw: ", text)
    resp_data = json.loads(text)
    return resp_data


def crypto_data(data):
    _data = copy.deepcopy(data)
    _data.pop('merchantcode')
    _data.pop('officeCode')
    k = pyDes.des(_KEY, pyDes.ECB, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = base64.b64encode(k.encrypt(json.dumps(data)))
    return d


def decrypto(crypto_data):
    """
    {"wxpaynum":"4200000006201709294956729312","platformTradeCode":"wx20170929151444241","timeEnd":"20170929151513","totalFee":"100","state":"SUCCESS","info":null}
    """
    k = pyDes.des(_KEY, pyDes.ECB, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    data = k.decrypt(base64.b64decode(crypto_data))
    return json.loads(data)


if __name__ == "__main__":
    # test_wechat_qr()
    # test_query()
    # test_alipay_qr()
    # query_d0_balance()
    jinjian()
    # query_merchant()
    # query_d0_balance(_MERCHANTCODE)
    # withdraw('00000000353000000042', 100, 'weixin')
    # query_d0_withdraw('00000000353000000042', '123')
