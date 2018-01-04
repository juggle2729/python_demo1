#-*- coding: utf-8 -*-
import random
from datetime import datetime
import base64
import json

import requests
from OpenSSL.crypto import load_privatekey, FILETYPE_PEM, sign, verify, load_certificate
import codecs

from utils import err, tz

PARTNER_ID = "mingde888"
DAIFU_NOTIFY_URL = "http://47.96.154.221:8088/admin/daifu/ysepay_callback"
BOEING_KEY = """-----BEGIN PRIVATE KEY-----
MIICeQIBADANBgkqhkiG9w0BAQEFAASCAmMwggJfAgEAAoGBALqfUn8M4Dr6dhwl
9gqEJP3mFI6iyUQOH5pgNfM1hyO0L3AvRID5xanhK2Dg7DBsn5V8fY9QzK+yXVcx
v+RKf2asNuxspHebH//F4IyZTNbCUwXVF8Peo1Yozq9tuHEhj6UIrFkIbNT5B19i
4q+qFXWGOn1ZrPwj1VDjlV7wO8zLAgMBAAECgYEAp/cHf/QtyMduEE2WUca3qJEx
RWN8NDVl+kLHq9ssg1UEMTtJs6+aWRihOzOVQMwzIY8HTzsQzr2BRx4usKDgYhJJ
24NKPla2bhbz9p3svl02sTn/Vcixcarqulr/FBxvFvr5acZE0ZjaV6TBoa6p6m1S
OcCzhvzE7rM5NSK1T7ECQQD6uhuP29N5p+208eBTiosp4MWVWc8++Ry1wrdpwoW4
Lnnw+K1I0BiIAxNyraPg2GZfivLUUQhzcmP/VgPcdzgZAkEAvowUsEyGY2ixyu0u
i4Y389OZ/qEtaeGwbDEpg+43KC11cCADeMDgZ6R4Pu5L3/cG86BH8b9OeCTCoI0c
d63YgwJBAO1fEQULm5UL1VJ/xF+TRNlrAeS52CnIctPp+vdXwH11EuF+rZ/H09HB
B8KEfig6+ADwbaFw7k1OOTnd1138SNECQQCbcfuOt18KyeYA/ezytdP/fagrKaG6
tvsNyC1uC2/DvxIHHpa2c+KdqnbOH+iWFRf+t8r5VG/XY2XDRFrs502xAkEAmWbd
Z7T79Of4BXCLoHp+kjLrBwrQI6yHbrgJzON/amgnZPPztiBPXR9PcFjTjne0dXyp
PjqGeuwVUcUcSXX3Xg==
-----END PRIVATE KEY-----"""
YSEPAY_KEY = """-----BEGIN CERTIFICATE-----
MIICizCCAfSgAwIBAgIEIL4JYzANBgkqhkiG9w0BAQQFADBcMQ8wDQYDVQQDDAZ5
c2VwYXkxDzANBgNVBAsMBnlzZXBheTERMA8GA1UECgwIb3JnYW5pemUxCzAJBgNV
BAcMAnN6MQswCQYDVQQGEwJjbjELMAkGA1UECAwCZ2QwHhcNMTMwMzA0MDgwMzUy
WhcNNDMwMjI1MDgwMzUyWjBcMQ8wDQYDVQQDDAZ5c2VwYXkxDzANBgNVBAsMBnlz
ZXBheTERMA8GA1UECgwIb3JnYW5pemUxCzAJBgNVBAcMAnN6MQswCQYDVQQGEwJj
bjELMAkGA1UECAwCZ2QwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBALtI+SYh
R/Zq7CSBtVyEzJ94IOAgK4DUYqtLBFsMjbhQxWHMOBwjEJSYUbn8N9w8nPR3ehX0
aCR3j/s2a15G+Y2c44Y06eZHoAYQpp8OkvWYB2md2amQBnR/o5Wjc/LkkODbC3x3
67d0XQAVbB3auuuqxxa/ElUHnkOe5l9eXYLJAgMBAAGjWjBYMB0GA1UdDgQWBBQB
rC+ShJLjpMYmmEbcr6p6Ma6FTDAfBgNVHSMEGDAWgBTNRc1cSoLvynQarb/pETbg
WClymDAJBgNVHRMEAjAAMAsGA1UdDwQEAwIEkDANBgkqhkiG9w0BAQQFAAOBgQBB
5m8oxrt1KnfbFP+akJvctjhbta5JzenDlCfYcZtykYLSMwkmhd670/y4tJc35P0Z
X/x1bJiAS+2i90L6f8P/WuBMxeI1KuX4Grk22ivw3nweWbGOUCN/PEC5YwUqHope
qHzs09O12ANXXgS35L2wgUxQOB1jcuhLXy2Z94pGYg==
-----END CERTIFICATE-----"""


def sign_string(data):
    s = ''
    for k, v in ordered_data(data):
        s += "%s=%s&" % (k,v)
    key = load_privatekey(FILETYPE_PEM, BOEING_KEY)
    signed_data = sign(key, s[:-1], 'sha1')
    return base64.b64encode(signed_data)


def verify_notify(data):
    return True
    #sign = data.pop('sign')
    #s = ''
    #for k, v in ordered_data(data):
    #    s += "%s=%s&" % (k,v)
    #key = load_certificate(FILETYPE_PEM, YSEPAY_KEY)
    #verify(key, sign, s[:-1], 'sha1')
    #return True

def ordered_data(data):
    complex_keys = []
    for key, value in data.items():
        if isinstance(value, dict):
            complex_keys.append(key)
    for key in complex_keys:
        data[key] = json.dumps(data[key], sort_keys=True).replace(" ", "")
    return sorted([(k, v) for k, v in data.items()])


def get_account_daifu_type(card_info):
    if str(card_info)[0] == '1':
        account_type = 'corporate'
    else:
        account_type = 'personal'

    if str(card_info)[1] == '1':
        card_type = 'debit'
    elif str(card_info)[1] == '2':
        card_type = 'credit'
    else:
        card_type = 'unit'
    return account_type, card_type


def ysepay_daifu(daifu_record):
    account_type, card_type = get_account_daifu_type(daifu_record['card_type'])
    data = {
        "method": "ysepay.df.single.quick.accept",
        "partner_id": PARTNER_ID,
        "timestamp": tz.local_now(),
        "charset": "utf-8",
        "sign_type": "RSA",
        "notify_url": DAIFU_NOTIFY_URL,
        "version": "3.0",
        "biz_content": {
            "out_trade_no": str(daifu_record['id']),
            "business_code": "2010005",
            "currency": "CNY",
            "total_amount": float(daifu_record['amount']),
            "subject": "波音代付",
            "bank_name": daifu_record['bank_name'],
            "bank_city": daifu_record['bank_city'],
            "bank_account_no": daifu_record['bank_account_no'],
            "bank_account_name": daifu_record['bank_account_name'],
            "bank_account_type": account_type,
            "bank_card_type": card_type
        }
    }
    url = "https://df.ysepay.com/gateway.do"
    data["biz_content"] = json.dumps(data["biz_content"])
    data["sign"] = sign_string(data)
    r = requests.post(url, data=data, allow_redirects=False)
    print r.headers
    print r.text
    print r.content
    print r.status_code
    if r.status_code == 200:
        response = r.json().get("ysepay_df_single_quick_accept_response")
        if response and response['code'] == '10000' and response['msg'] == 'Success':
            return True, json.dumps(response)
        else:
            return False, r.text
    else:
        return False, r.text


def ysepay_check_data(data):
    if verify_notify(data):
        if data['trade_status'] == u'TRADE_SUCCESS':
            return True
        else:
            return False
    else:
        raise err.SignWrongError('ysepay sig error')
