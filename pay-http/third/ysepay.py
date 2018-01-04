#-*- coding: utf-8 -*-
import random
from datetime import datetime
import base64
import json

import requests
from OpenSSL.crypto import load_privatekey, FILETYPE_PEM, sign

#from db.pay_record.model import PAY_TYPE
#from db.account.controller import get_appid_detail
#from utils import err

PARTNER_ID = "mingde888"
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


def sign_string(data):
    s = ''
    for k, v in ordered_data(data):
        s += "%s=%s&" % (k,v)
    key = load_privatekey(FILETYPE_PEM, BOEING_KEY)
    signed_data = sign(key, s[:-1], 'sha1')
    return base64.b64encode(signed_data)


def ordered_data(data):
    complex_keys = []
    for key, value in data.items():
        if isinstance(value, dict):
            complex_keys.append(key)
    for key in complex_keys:
        data[key] = json.dumps(data[key], sort_keys=True).replace(" ", "")
    return sorted([(k, v) for k, v in data.items()])


def yesepay_daifu(daifu_record):
    data = {
        "method": "ysepay.df.single.quick.accept",
        "partner_id": PARTNER_ID,
        "timestamp": "2017-01-02 12:00:00",
        "charset": "utf-8",
        "sign_type": "RSA",
        "notify_url": DAIFU_NOTIFY_URL,
        "version": "3.0",
        "biz_content": {
            "out_trade_no": daifu_record['id'],
            "business_code": "2010005",
            "currency": "CNY",
            "total_amount": daifu_record['amount'],
            "subject": "波音代付",
            "bank_name": daifu_record['bank_name'],
            "bank_city": daifu_record['bank_city'],
            "bank_account_no": daifu_record['bank_account_no'],
            "bank_account_name": daifu_record['bank_account_name'],
            "bank_account_type": daifu_record['account_type'],
            "bank_card_type": card_type
        }
    }
    url = "https://df.ysepay.com/gateway.do"
    data["biz_content"] = json.dumps(data["biz_content"])
    data["sign"] = signed_data(data)
    r = requests.post(url, data=data, allow_redirects=False)
    print r.headers
    print r.text
    print r.content
    print r.status_code

    if r.status_code == 200:
        response = r.content["code"]["ysepay_df_single_quick_accept_respons"]
        if response['code'] == '10000' & response['msg'] == 'Success':
            return True, response
        else:
            return False, response
    else:
        return False, response
