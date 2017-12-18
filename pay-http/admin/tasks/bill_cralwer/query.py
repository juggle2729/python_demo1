# coding: utf-8

import binascii
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
import json
from datetime import datetime, timedelta
import requests

APPKEY = 'HYM17002P'

PRIVATE_KEY = '''-----BEGIN PRIVATE KEY-----
MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAKfr7xl
ECZ93UWa313Hofedt7ujuxFQE3BpKU/eevwrvbyf4hTa84scz8IHRkj
Fz7owHCPtUcf0iy2kwjivrT67ajG7x7EJKJJUGkV/3Yrs78X2DFFvDl
veANT3NCNZcuA5F3PRUIjzLB13VJjxEBDUjuJ9dVWk07o0vKi7Gq7KH
AgMBAAECgYAFOXLz70j5XCX9MyUR1zDrnWD8gEk9b/VFICDiqF67QV3
M+Y9zd4b6uaP29gU9YqT+WE2wPB1bydRYTnlt5mFROzfP/LRTVvwiqf
umVe1gtoz/cDjuQH54aJV2YM7TKzlTTV5ub5yegY+mp6UjQoX3kLXPL
OKVIiG+V7orqF9n2QJBAPvuP92IJaMFHSMCKDi/YUhLPn0gn2ZwJ+Re
7+Pa8CCBTZsuNeTjvQt0Soo7uwBBq9AAMG8viaxlfSzVXb8u38UCQQC
qok0lrY3cjF2iO6+S+2iGVINr2pDeoVyYtuvSLYaPBBbVZ1RWgOatmd
P6NlmiBVGfYZDeG5Nb+uDeO8iMkIHbAkEAm6m0kH9FMhtAy5bTn2yxA
WhsrgfwNe1q2LLIavOml48NkqrU5h7JekBaplsNyrTJInZbdvfai0kS
NReJG04tOQJATeaLEgiKG4Z5uPdG0PO2ZJ1w4myGdx10CMR6JRpjtCd
JxWPHPTbcGaWBAVqO0UlcWkdQvBYa0INY5hylEodmwQJBAPtemvhBjg
qMM68kvWbBJiwk4Qr+2Mgx7GGWjn/cB1TVuduTkf/2ovLwe5/3SvuPe
NaAB2zLLdXgc7RXyDx7vyQ=
-----END PRIVATE KEY-----'''

def gen_bill_params(daydelta, app_key):
    date = datetime.now() - timedelta(days=daydelta)
    date = date.strftime('%Y%m%d')
    params = {
        'action': 'mcht/bill/download',
        'version': '2.0',
        'coopId': app_key,
        'billDate': date
        }
    return '[%s]' % json.dumps(params)

def sign_string(private_key_path, unsigned_string):
    key = RSA.importKey(PRIVATE_KEY) #open(private_key_path).read())
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(SHA.new(unsigned_string.encode('utf8')))
    return binascii.b2a_hex(signature).upper()

def verify_rsp_headers(headers):
    return True

def query_bill(daydelta=0, app_key=APPKEY):
    url = 'https://cebwhaop.koolyun.com/apmp/rest/v2/'
    data = gen_bill_params(daydelta, app_key)
    sign = sign_string('test.pem',data)
    params = {
        'params': '%s' % data
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "x-appkey": APPKEY,
        "x-apsignature": sign
    }

    rsp = requests.post(url, data=params, headers=headers)
    if rsp.status_code != 200:
        return

    if not verify_rsp_headers(rsp.headers):
        return

    try:
        results = json.loads(rsp.text)
    except:
        return

    bills = []
    for result in results:
        if result['responseCode'] != '00':
            continue

        url = result['billUrl']
        rsp = requests.get(url)
        if rsp.status_code != 200:
            continue
        bills.append(rsp.content)

    return bills

if __name__ == '__main__':
    for i in range(15):
        print(i, query_bill(daydelta=i))
