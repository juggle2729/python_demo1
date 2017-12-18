# -*- coding: utf-8 -*-
import time
import binascii
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
import json
import requests


# 奥付代理-付通进件
def gen_params():
    params = {
        "action": "mcht/info/enter",
        "version": "2.0",
        "expanderCd": "0303603070",
        "coopMchtId": "100005",  # 我们自己的子商户号
        "mchtName": "武汉万洪信息技术有限公司",
        "mchtShortName": "万洪信息",
        "bizLicense": "91420106MA4KU7N793",
        "legalIdExpiredTime": "2099-01-01",
        "idNo": "422130196710282251",
        "mchtAddr": "武汉市武昌区中北路凯德1818中心6栋26楼03号",
        "province": "420000",
        "city": "420100",
        "area": "420106",
        "accountType": "0",
        "account": "15000089797456",
        "accountName": "武汉万洪信息技术有限公司",
        "bankCode": "307584007998",
        "bankName": "平安银行武汉分行营业部",
        "openBranch": "307521005712",
        "contactName": "洪猛",
        "contactMobile": "18772445333",
        "contactEmail": "771301091@qq.com",
        "mchtLevel": "2",
        "openType": "C",
        "acquirerTypes":
        # "[{\"acquirerType\":\"wechat\",\"scale\":\"6.5\",\"countRole\":\"0\",\"tradeType\":\"203\"}]",
        "[{\"acquirerType\":\"qq\",\"scale\":\"3.2\",\"countRole\":\"0\",\"tradeType\":\"Q000041\"}]",
        # "[{\"acquirerType\":\"alipay\",\"scale\":\"6.5\",\"countRole\":\"0\",\"tradeType\":\"2015062600002758\"}]",
        # "[{\"acquirerType\":\"baidu\",\"scale\":\"6.5\",\"countRole\":\"0\",\"tradeType\":\"5411\"}]",
        # "[{\"acquirerType\":\"jd\",\"scale\":\"6.5\",\"countRole\":\"0\",\"tradeType\":\"017\"}]",
    }
    return '[%s]' % json.dumps(params)


def sign_string(private_key_path, unsigned_string):
    h = SHA.new(unsigned_string)
    key = RSA.importKey(open(private_key_path).read())
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(SHA.new(unsigned_string.encode('utf8')))
    return binascii.b2a_hex(signature).upper()


def gen_pay_params():
    data = {
        "action": "wallet/trans/csbSale",
        "version": "2.0",
        "reqTime": time.strftime('%Y%m%d%H%M%S', time.localtime()),
        "reqId": str(int(time.time() * 1000)),
        "custId": "170904114646071",
        "totalAmount": "2",
        "acquirerType": "wechat",
        "notify_url": "http://p.51paypay.net/api/v1/pay/guangda/callback",
        "payType": "1"
    }
    return '[%s]' % json.dumps(data, ensure_ascii=False)


def gen_query_params():
    data = {
        "action": "mcht/info/query",
        "acquirerType": "wechat",
        "version": "2.0",
        "coopMchtId": "100001"
    }
    return '[%s]' % json.dumps(data)


if __name__ == "__main__":
    url = 'https://cebwhaop.koolyun.com/apmp/rest/v2/'
    data = gen_params()
    # data = gen_query_params()
    sign = sign_string('test.pem', data)
    appkey = 'HYM17002P'
    params = {
        "params": data
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "x-appkey": appkey,
        "x-apsignature": sign
    }
    d = requests.post(url, data=params, headers=headers)
    print url
    print headers
    print params
    print d.request.body
    print d.text
