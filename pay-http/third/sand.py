# -*- coding: utf-8 -*-
"""
sand 支付接口, sand支付只接支付宝和微信
"""
from base64 import b64encode, b64decode
from datetime import datetime, timedelta
import json
import logging
import random
import string
import time
from urlparse import parse_qs
from urllib import unquote

import requests
from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES

from db.pay_record.model import PAY_TYPE
from db.pay_record.controller import save_originid
from utils import tz, id_generator

_LOGGER = logging.getLogger()

_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCXZKnlpzU9s9J1
8XTdLWEK9Fx7I/nR7c1+Ro3iTPM43NTqVsjglciiENZzBtbhohhZRHkNvNUZ02PX
hALq3tmnxFHTHJPKXSJYlLq3RRZuprBKuCifS2rX/5GJRoWyHYWYBknqshOM259L
jVebemt53/8WBcTNbtcH98LhrlCeeecfvmDslhHSC5kYxuk4TwO0JAgvuZmdQzoK
2vQIJqrctdRz+gN6RGV7w8X6qn75TfQttiREP9R+TN6E0Pr/E6t4gN2FoQL0FWC1
+RgEhvuowi5+Ot/wIln5sugHhSJH2cqEj+3aG+5VjGy97sDvANP7oO+704+cri+G
OqdiJwg1AgMBAAECggEBAIHqsKGTS+0XU5RDELZ9Krnr2TETPl8YYy/p+/gncNFr
MIuozdlssC/joyQyylP2dk6ko/1V/smaziMz9gz4EHAX2OABthICumapu1FqyEVM
Zhy4zKNmZNnXR102V6TyEKLVQrlU99H45ko/kN6rv29m+dA8QxbH91+vDl386NIV
GIJY03eJLSp+mhH3xjJuRLwbrS8lnk70hqCWamEqXpJlmW15+ai0TQY1MHJ0/XOP
T2X8R7hrGVfdeXQwgq2e8nwyfj0e5T0fHOJZXRSO66FXG/TwZqAwpswEmQOXyrwL
CFXH/HLDKkwKjX9SzXsAQ40uisciPfMILFBbatcikkECgYEAwXfVcJB0ANzrIGQq
P1r0tt9YMQliu/jjRl0kNSM33CPPe6mIu01DMGDgfdUvLOjoOSkpdu4eKBx39QnL
SKhxKMRAnXmPlQQXRDWwntXLOpVIiffNiRcI3VBfXZ4KVPRUSKDin53B1XZ0QEoE
EDYDeOKpHIccRJa7gsqs0Ms3+C8CgYEAyFNrkh2DkK+Xv1lGGnzCRRBespy/05IU
1oXjjzp8wXtWvmAqv9MRbDCndR75nAVqKOUt3Kewad/MPTpy6VWI8k2JeGt9R/Ae
VG2uzZpSlfWHfilLDmD38/krdfttxeFL84BoQH6hMX3qicbenW62bOE+N1KEbx+O
dm9Wgj1vyNsCgYAh53s7H8WEhTKbWZJhyfHKvnc5GLj50hMaOKZovYRDiu8Ib9xr
Xo3gw4lz49FBoItZwRHoKrCUPPD0u0OptwMlrsbYEf6Mkcv2AyaxnyvfV1v/+bJG
TQgbqMMdp92Np8fBdphgeogGfZy/y3jM0npnS+lw+2iDyJqRwCzq5kIntwKBgQC8
+SytvpfA4lQVFuMx02Tz/7hFZ+bxb4mmwNDk6TiM0IwItPE+2Z5C4DboHls7WkRF
5cP4tluN1Kd3Tu7dvGmeoZQ/+65IMXR7EqjmnWCww9iYI94A52qgRPpBpvhrxdd/
Ei/GP25SIMUiSW7xNmJynZyyVW5G4Y7jnK4P2GLeJwKBgQC8ryuk7ldWy65EbqjN
1DyvClZO0iA4iDvRIDvtNBfLKrIwSCSg8wbiB+nCzqZ7NRH/eQfwNh+iUZdzzhRw
O5fQKwdDymtiLFIL4kVUf6J+2lzmQ60tOs02sPiRr26aNyIVg9OKEPMaKfgTWY8R
99q/trFBTFXi0jUz5NJOq9IdTw==
-----END PRIVATE KEY-----"""

_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyIwo8Jq6XiUSY8cMrDfT
Rb65QaWcPH2hITZrei3jgLIdHP3kTQjZueWhp2nQ7H9s6nD99MYSydB4YKZ5qVAo
VxuwRE1fnNKOx8M3npIcr/JKtvCN5TrE1XIUyxWG3F7sPbsafN+7Gwxqh5gT4/u/
zq5busBztvXh+/woiqi3EGQ1WO9+P4AtYA6nr3KoVU7hdO8Aj+6aXMjQQTtDrgH/
oiAHkEMJfrQmZ6irdnxzRwQ53D/GzVieAqME/sUMeIBWiy/Uj7d2TVJZkLLlC76l
g6AVo/z9Wl26T0wyttxlCzjfZt1naT3B5IIp8k6lYrOdj3SX1gMD3ej0NGnnrQuu
vwIDAQAB
-----END PUBLIC KEY-----"""

_DAIFU_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAl2Sp5ac1PbPSdfF03S1h
CvRceyP50e3NfkaN4kzzONzU6lbI4JXIohDWcwbW4aIYWUR5DbzVGdNj14QC6t7Z
p8RR0xyTyl0iWJS6t0UWbqawSrgon0tq1/+RiUaFsh2FmAZJ6rITjNufS41Xm3pr
ed//FgXEzW7XB/fC4a5QnnnnH75g7JYR0guZGMbpOE8DtCQIL7mZnUM6Ctr0CCaq
3LXUc/oDekRle8PF+qp++U30LbYkRD/UfkzehND6/xOreIDdhaEC9BVgtfkYBIb7
qMIufjrf8CJZ+bLoB4UiR9nKhI/t2hvuVYxsve7A7wDT+6Dvu9OPnK4vhjqnYicI
NQIDAQAB
-----END PUBLIC KEY-----"""

_NOTIFY_URL = 'http://p.51paypay.net/api/v1/pay/sand/callback'


def sign_string(unsigned_string):
    key = RSA.importKey(_PRIVATE_KEY)
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(SHA.new(unsigned_string.encode('utf8')))
    return signature
    # return binascii.b2a_hex(signature).upper()


def verify_sign(data, sign):
    """
    公钥验签
    """
    public_key = RSA.importKey(_PUBLIC_KEY)
    h = SHA.new(data.encode('utf8'))
    verifier = PKCS1_v1_5.new(public_key)
    # sign = binascii.a2b_hex(sign)
    return verifier.verify(h, sign)


def get_random_str():
    rule = string.letters + string.digits
    key = "".join(random.sample(rule, 16))
    return key


def test_create_pay():
    # url = "http://61.129.71.103:8003/qr/api/order/create"
    url = "https://cashier.sandpay.com.cn/qr/api/order/create"
    head = {
        "version": "1.0",
        "method": "sandpay.trade.precreate",
        "productId": "00000006",
        "accessType": "2",  # 1 普通商户， 2平台商户
        "mid": "Z1033992",  # "Z1456812",
        "plMid": "P47428",  # "P79915",
        "channelType": "08",
        "reqTime": datetime.now().strftime("%Y%m%d%H%M%S"),
        'subMidAddr': '',
        'subMidName': ''
    }

    order_id = str(int(time.time() * 1000))
    print 'order_id', order_id

    body = {
        'bizExtendParams': '',
        'extend': '',
        'limitPay': '',
        'merchExtendParams': '',
        'operatorId': 'SAND001613',
        'riskRateInfo': '',
        'storeId': '',
        'terminalId': '',
        "payTool": "0401",
        "orderCode": order_id,
        "totalAmount": "000000000400",
        "subject": "testpay",
        "body": "test",
        "notifyUrl": _NOTIFY_URL,
        'txnTimeOut': "20171229170000",
        # 'clearCycle': "0-T1"
    }
    payload = {"head": head, "body": body}
    _data = json.dumps(payload).replace(' ', '')
    data = {
        "charset": "utf-8",
        "data": _data,
        "signType": "01",
        "sign": b64encode(sign_string(_data)),
    }
    try:
        resp = requests.post(url, data=data)
        print resp.content
    except Exception as e:
        print e
    resp_dct = parse_qs(unquote(resp.content))
    # resp_sign = resp_dct['sign'][0]
    resp_code = json.loads(resp_dct['data'][0])['head']['respCode']
    resp_msg = json.loads(resp_dct['data'][0], encoding='utf-8')['head']['respMsg']
    print resp_dct
    print resp_code
    print resp_msg
    print json.loads(resp_dct['data'][0])['body']['qrCode']
    if not resp_code == "000000":
        print "Error!"


def qr_pay(pay_record, order_info=None):
    """
    sand 只支持微信扫码和支付宝扫码, pay_type 取值2, 21
    """
    pay_type = pay_record.pay_type
    appid = pay_record.appid
    custid = pay_record.real_custid
    pay_type = pay_record.pay_type
    amount = pay_record.amount
    pay_id = pay_record.id
    url = "https://cashier.sandpay.com.cn/qr/api/order/create"
    _LOGGER.info('custid: %s' % custid)
    now = tz.local_now()
    expire_time = now + timedelta(hours=2)
    print 'custid', custid
    head = {
        "version": "1.0",
        "method": "sandpay.trade.precreate",
        "productId": "00000005" if pay_type == PAY_TYPE.WECHAT_QR else "00000006",
        "accessType": "2",  # 1 普通商户接入， 2 平台商户接入
        "mid": custid,
        "plMid": 'P47428',
        "channelType": "08",  # 07 互联网 08 移动端
        "reqTime": now.strftime("%Y%m%d%H%M%S"),
        'subMidAddr': '',
        'subMidName': ''
    }

    body = {
        'bizExtendParams': '',
        'extend': '',
        'limitPay': '',
        'merchExtendParams': '',
        'operatorId': 'SAND001602',
        'riskRateInfo': '',
        'storeId': '',
        'terminalId': '',
        "payTool": "0402" if pay_type == PAY_TYPE.WECHAT_QR else "0401",
        "orderCode": "%s" % pay_id,
        "totalAmount": str(int(amount * 100)).zfill(12),
        "subject": str(order_info),
        "body": str(order_info),
        "notifyUrl": _NOTIFY_URL,
        'txnTimeOut': expire_time.strftime("%Y%m%d%H%M%S"),
        # 'clearCycle': "0-T1"
    }
    payload = {"head": head, "body": body}
    _data = json.dumps(payload).replace(' ', '')
    data = {
        "charset": "utf-8",
        "data": _data,
        "signType": "01",
        "sign": b64encode(sign_string(_data)),
    }
    try:
        resp = requests.post(url, data=data)
        resp_dct = parse_qs(unquote(resp.content))
        resp_sign = resp_dct['sign'][0]
        resp_dct = json.loads(resp_dct['data'][0], encoding='utf-8')
        resp_code = resp_dct['head']['respCode']
        resp_msg = resp_dct['head']['respMsg']
        _LOGGER.info("sand qr pay response dict: %s", resp_dct)
        qr_code = resp_dct['body']['qrCode']
        originid = resp_dct['body']['orderCode']
    except Exception as e:
        _LOGGER.exception("sand qr pay error")
        return {
            'status': -1,
            'error': 'unknown error'
        }

    if not resp_code == "000000":
        return {
            'status': -1,
            'error': resp_msg
        }

    save_originid(pay_record.id, originid)
    return {
        'status': 0,
        'qrCode': qr_code
    }


BYTE_LEN = 128


def encrypt(message):
    """ 加密AES key """
    # RSA/ECB/PKCS1Padding
    # 128字节搞一次
    ret = ''
    input_text = message[:BYTE_LEN]
    while input_text:
        # h = SHA.new(input_text)
        key = RSA.importKey(_DAIFU_PUBLIC_KEY)
        cipher = Cipher_pkcs1_v1_5.new(key)
        # ret += cipher.encrypt(input_text + h.digest())
        ret += cipher.encrypt(input_text)
        message = message[BYTE_LEN:]
        input_text = message[:BYTE_LEN]
    enc = b64encode(ret)
    return enc


def aes_crypto(plain_text, key):
    # plainText = '12345678901234567890123456789012'
    # key = '1234567812345678'
    BLOCK_SIZE = 16  # Bytes
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    raw_buf = pad(plain_text)
    aes = AES.new(key, AES.MODE_ECB)
    ret = b64encode(aes.encrypt(raw_buf))
    return ret


def decrypt_aes_key(encrypt_key):
    """ 解密AES KEY """
    rsakey = RSA.importKey(_PRIVATE_KEY)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    # random_generator = Random.new().read
    aes_key = cipher.decrypt(b64decode(encrypt_key.replace(' ', '+')), "1234567890123456")
    return aes_key


def query_balance(custid):
    url = "https://caspay.sandpay.com.cn/agent-main/openapi/queryBalance"
    key = get_random_str()
    order_code = id_generator.generate_long_id("pay")
    print 'order_code', order_code
    payload = {
        "version": "01",
        "productId": "00000004",
        "tranTime": tz.local_now().strftime("%Y%m%d%H%M%S"),
        "orderCode": str(order_code),
        "channelType": "08",
        "extend": "",
    }
    _data = json.dumps(payload, ensure_ascii=False).replace(' ', '')
    _rsakey = RSA.importKey(_PUBLIC_KEY)
    cipher = Cipher_pkcs1_v1_5.new(_rsakey)
    data = {
        "transCode": "MBQU",
        "accessType": "1",
        "merId": custid,  # 子商户号
        "plId": "P47428",  # 平台商户号
        "encryptKey": b64encode(cipher.encrypt(key)),
        "encryptData": aes_crypto(_data, key),
        "sign": b64encode(sign_string(_data)),
        "extend": "",
    }
    resp = requests.post(url, data=data)
    resp_dct = parse_qs(unquote(resp.text))
    encrypt_data = resp_dct['encryptData'][0]
    encrypt_key = resp_dct['encryptKey'][0]
    aes_key = decrypt_aes_key(encrypt_key)
    cipher = AES.AESCipher(aes_key)
    decrypt_data = cipher.decrypt(b64decode(encrypt_data.replace(' ', '+')))
    _LOGGER.info('sand agent pay decrypt_data: %s' % decrypt_data)
    resp_detail = json.loads(decrypt_data.split('}')[0] + '}')
    return resp_detail


def create_agent_pay(custid, amount, order_code, acc_attr, acc_type, acc_no,
                     acc_name, pay_mode, trans_time):

    url = "https://caspay.sandpay.com.cn/agent-main/openapi/agentpay"
    key = get_random_str()
    print 'order_code', order_code

    payload = {
        "version": "01",
        "productId": "00000004",
        "tranTime": trans_time,
        "orderCode": order_code,
        "tranAmt": amount.zfill(12),
        "currencyCode": "156",
        "accAttr": acc_attr,
        "accType": acc_type,
        "accNo": acc_no,
        "accName": acc_name.encode('utf-8'),
        "bankName": "",
        "bankType": "",
        "remark": "",
        "payMode": "2",  # 1 商户预存款 2 在线支付 3 银行卡帐户
        "channelType": "08",
        "reqReserved": "",
        "noticeUrl": "",
        "extend": "",
    }
    _data = json.dumps(payload, ensure_ascii=False).replace(' ', '')
    _rsakey = RSA.importKey(_PUBLIC_KEY)
    cipher = Cipher_pkcs1_v1_5.new(_rsakey)
    data = {
        "transCode": "RTPM",
        "accessType": "1",
        "merId": custid,  # 子商户号
        "plId": "P47428",  # 平台商户号
        # "merId": "P47428",
        # "plId": "P47428",
        "encryptKey": b64encode(cipher.encrypt(key)),
        "encryptData": aes_crypto(str(_data), key),
        "sign": b64encode(sign_string(_data)),
        "extend": "",
    }
    print 'req_data', data
    resp = requests.post(url, data=data)
    print resp.content
    resp_dct = parse_qs(unquote(resp.text))
    print resp_dct
    print 'status', resp.status_code
    print 'text', resp.text
    encrypt_data = resp_dct['encryptData'][0]
    print 'encrypt_data: ', encrypt_data
    encrypt_key = resp_dct['encryptKey'][0]
    print encrypt_key
    # 解密AES key
    aes_key = decrypt_aes_key(encrypt_key)
    print 'aes_key: ', aes_key
    cipher = AES.AESCipher(aes_key)
    decrypt_data = cipher.decrypt(b64decode(encrypt_data.replace(' ', '+')))
    _LOGGER.info('sand agent pay decrypt_data: %s' % decrypt_data)
    resp_detail = json.loads(decrypt_data.split('}')[0] + '}')
    resp_detail.pop('respDesc', '')
    resp_detail.pop('tranDate', '')
    resp_detail.pop('sandSerial', '')
    resp_detail.pop('origRespCode', '')
    resp_detail.pop('origRespDesc', '')
    return resp_detail


def test_agent_pay():
    # url = "http://61.129.71.103:7970/agent-main/openapi/agentpay"
    url = "https://caspay.sandpay.com.cn/agent-main/openapi/agentpay"
    key = get_random_str()
    # iv = Random.new().read(AES.block_size)
    order_code = id_generator.generate_long_id("pay")
    print 'order_code', order_code

    payload = {
        "version": "01",
        "productId": "00000004",
        "tranTime": (datetime.now() + timedelta(hours=8)).strftime("%Y%m%d%H%M%S"),
        "orderCode": order_code,
        "timeOut": '20171024120000',
        "tranAmt": "000000000050",
        "currencyCode": "156",
        "accAttr": "0",
        "accType": "4",
        "accNo": "6230582000023229449",
        "accName": u"陈喻君".encode('utf-8'),
        "provNo": "100016",
        "cityNo": "100017",
        "bankName": "",
        "bankType": "",
        "remark": "",
        "payMode": "2",  # 1 ? 2 ?
        "channelType": "07",
        # "extendParams": "",
        "reqReserved": "",
        "noticeUrl": "",
        "extend": "",
    }
    _data = json.dumps(payload, ensure_ascii=False).replace(' ', '')
    _rsakey = RSA.importKey(_PUBLIC_KEY)
    cipher = Cipher_pkcs1_v1_5.new(_rsakey)
    data = {
        "transCode": "RTPM",
        "accessType": "1",
        "merId": "Z1033992",
        "plId": "P47428",
        # "merId": "P47428",
        # "plId": "P47428",
        "encryptKey": b64encode(cipher.encrypt(key)),
        "encryptData": aes_crypto(_data, key),
        "sign": b64encode(sign_string(_data)),
        "extend": "",
    }
    print 'req_data', data
    resp = requests.post(url, data=data)
    print resp.content
    resp_dct = parse_qs(unquote(resp.text))
    print resp_dct
    print 'status', resp.status_code
    print 'text', resp.text
    encrypt_data = resp_dct['encryptData'][0]
    print 'encrypt_data: ', encrypt_data
    encrypt_key = resp_dct['encryptKey'][0]
    print encrypt_key
    # 解密AES key
    aes_key = decrypt_aes_key(encrypt_key)
    print 'aes_key: ', aes_key
    cipher = AES.AESCipher(aes_key)
    resp_detail = json.loads(cipher.decrypt(b64decode(encrypt_data)))
    return resp_detail


def query_d0_withdraw(office_code, order_code, trans_time):
    """
    office_code: 平台编号
    返回举例：
    {u'orderCode': u'1623327232084675584',
     u'respCode': u'3003',
     u'respDesc': u'\u539f\u8ba2\u5355\u4e0d\u5b58\u5728',
     u'tranTime': u'20171129150627'}
    成功返回：
    """

    url = "https://caspay.sandpay.com.cn/agent-main/openapi/queryOrder"

    key = get_random_str()
    payload = {
        "version": "01",
        "productId": "00000004",
        "tranTime": trans_time,
        "orderCode": order_code,
        "extend": ""
    }
    _data = json.dumps(payload, ensure_ascii=False).replace(' ', '')
    _rsakey = RSA.importKey(_PUBLIC_KEY)
    cipher = Cipher_pkcs1_v1_5.new(_rsakey)

    data = {
        "transCode": "ODQU",
        "accessType": "1",
        "merId": office_code,
        "plId": "P47428",
        "encryptKey": b64encode(cipher.encrypt(key)),
        "encryptData": aes_crypto(_data, key),
        "sign": b64encode(sign_string(_data)),
        "extend": ""
    }
    resp = requests.post(url, data=data)
    resp_dct = parse_qs(unquote(resp.text))
    print resp_dct
    print 'status', resp.status_code
    print 'text', resp.text
    encrypt_data = resp_dct['encryptData'][0]
    print 'encrypt_data: ', encrypt_data
    encrypt_key = resp_dct['encryptKey'][0]
    print encrypt_key
    # 解密AES key
    aes_key = decrypt_aes_key(encrypt_key)
    print 'aes_key: ', aes_key
    cipher = AES.AESCipher(aes_key)
    decrypt_data = cipher.decrypt(b64decode(encrypt_data.replace(' ', '+')))
    _LOGGER.info('sand query agent pay decrypt_data: %s' % decrypt_data)
    resp_detail = json.loads(decrypt_data.split('}')[0] + '}')
    return resp_detail


if __name__ == "__main__":
    # print qr_pay("0401", "122345343232", "12131", "000000000001")
    #test_create_pay()
    # test_agent_pay()
    query_balance('Z1033992')
    # qr_pay(0.01, '2131213213122', 1, pay_type=21, order_info=None)
