# -*- coding: utf-8 -*-

import requests
from datetime import datetime
import time
import json
import random
import string
from urlparse import parse_qs
from urllib import unquote
from urllib import urlencode

from base64 import b64decode, b64encode
from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES



_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC3JuHwP5EzDVBX
GxwwUKdvnOGwR/I+VDTJ7n5VjYQEX2vAK2gzEs7qVnRtHi7xLA7UY9STgeJT9G1D
+ArGJ69JcC5bKEMOmLuXFaGyzcz94iH4bGlWso+NTvnyjJYdFltmQlhD/SJDbgRv
/fCaLfeuKV1tvaNCHZXVijTOy6MrOiyc19AdEGCz8xgyA1Q+kgHJtoWpWQ8OYXDx
Um1tNS5OsT5hPZVS1yNuL3IvMG8gYPfeLfgLNLhysyGLvZ7+yOpstZynK028u4yq
8H7w/v5MPGqlMahg2Q+AZkiXTSYajaVakf2ypiTpnT8p+efBmv11pOFldIpjYyqt
g6PuXGbXAgMBAAECggEACP2Gn7VvGjNwGyaAhrqezXLE/VM6x+Z4ROVJHEf7D//j
GSbIUaF9uLEPu/98TGhePfy8hZUdmANqjaiSVtHB3/f6vozGZeQHaU4thsplYp0E
D966eQAA3e3fhRFzmO/tAqMFFClL0kWHQDwV4GubOdhb9rQVXHx5S2ciWnhShR+b
qOc9q/pPj2vwplwJ70Nnbp1z+A5wmPdTMPijhUR5LX9dnX7uViFD84/DqHTj3yzQ
U0dQJ898Ndx2j6YutobqNYcgd2KL1ius2CmhZ3O23CmSJNYlktq2C7JcbqsTClh2
G18o3ern1I6pATPYRaIwaysxRUbkWMMM/xMr7mFnqQKBgQDY3dPlt/iCpBXO++bh
s6Q2RXE+NwPPFZnU8c86Rir9fHMfCnVEgm8scKGYc+xDQ8vf/8MhCAN4C0sUInii
PD9zTHLviOVmkoqTPdjAAUkmPIS4+ZBqX+iOOmk7Alq82wwY9u5G67wG0VlocoO2
8gMY0Hi4M8wg0jzIok39Kutv6wKBgQDYM5qW0kZMN9oY4ldPqe/jY2oTrk09ePwe
KbOz6ntkyZrmiCgPee/0skvxbY4m7DRd+BHq5Z5FT2ZtX1e9HwkMdRAlKNsXur4Q
Rxi8OWOyCIV010ts3+RqzNbs34zQbSS5rpR+6FrmCRs1qclPphjN244BhvOkj6+X
6FdkRcMVxQKBgQCi4eGQLSA6xxEWOD7OEIXquTd32gxDUl8LAF97zk3lu74fd1Ri
k3D6uNG2VoMCdn4/DLM7MPCiDiFiyw0+FPA3IhlFbdWWt8PbGV2dwJl3XYb2A4OD
UeuyP47f4kHSjNdGPNj0bYP4vu5fM3tYQecvkQzKlSThFebPbpAS8VSJ5wKBgCDu
42p8B2dOzrMhr0kcSsVpfFwZHfzyM/1oPs52Nmuo5iadsPSCj5HHoxfYp2G4c1Wp
Fxmf9pb6PFEGx/ewBZHXNylh6tXXhWI3YkYxu8T/1UxyCzQ/eqzmHQsiFnIdXg3G
0SnvvQDzfCiVf2vZkkexXRVQeEal+Ip8QuusUMY9AoGASjlzivH9Mcjxe9aEGjLi
1O/Juqs9jPjQdn89XEUGjFE2jVEY4447c8hW/quX65J/iZne8Oy9LlhkTWjyKnSh
t+92952llc3JjQ9Sr3KUpMcSJQ5HjK3Cx/U1ng0rKEwcKtbeUVp0tLtiVzntD6Ja
WQ7A8hv5ocek9+yC/BStWDA=
-----END PRIVATE KEY-----"""


_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1ewKj9VGbrVepANQQHCG
1CriwYys1ioK9lXuTLX6A7jxk2pSv0gl2uS4a0fLRYZknfnBIGHj7RHYmdIhiqWw
SYcq91d+hvFQ+HHTc0gM2faNdb2SSztqFzhpzkpCd+EiVaEDQK9/yGg211DAXNwk
okztHjSQ27BezZZryP8lItx1EqZ65yC5IR84e1fHeO4SZDKZlXYbO/3WwftxurFv
987JbyCkOqYJj3fwFJ3suk2Ur9MYLpJxz9iSrfG19Mkr6tYLZbnSwfDlgmYgmV9a
nO+t9Z0hDMe0G20plwxnJhbI5JDjfcZILRU42XUWxPfJQSJd75ZTAp+1vj9yak8M
JQIDAQAB
-----END PUBLIC KEY-----"""


def aes_crypto(plain_text, key):
    # plainText = '12345678901234567890123456789012'
    # key = '1234567812345678'
    BLOCK_SIZE = 16  # Bytes
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    raw_buf = pad(plain_text)
    aes = AES.new(key, AES.MODE_ECB)
    ret = b64encode(aes.encrypt(raw_buf))
    # print 'key', key
    # print 'ret', ret
    # print 'plain_text', plain_text
    return ret


def decrypt_aes_key(encrypt_key):
    """ 解密AES KEY """
    rsakey = RSA.importKey(_PRIVATE_KEY)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    # random_generator = Random.new().read
    aes_key = cipher.decrypt(b64decode(encrypt_key.replace(' ', '+')), "1234567890123456")
    return aes_key


def sign_string(unsigned_string):
    key = RSA.importKey(_PRIVATE_KEY)
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(SHA.new(unsigned_string.encode('utf8')))
    return signature


def test_sand_jinjian():
    URL = "http://61.129.71.103:8013/new_ecmis/api/sandpay/merch/add.do"
    head = {
        "version": "1.0",
        "access_token": "test",
        "method": "sandpay.merch.add",
        "accessType": "2",
        "mid": "P79915",
        "reqTime": datetime.now().strftime("%Y%m%d%H%M%S")
    }

    body = {
        "orderCode": str(int(time.time())),
        "shopLinkman": "业务联系人",
        "shopLinkmanMobile": "13211112222",
        "shopLinkmanMail": "test@example.com",
        "serviceTel": "010-11111111",
        "td0CreditMonery": "1000000",
        "shopJoinType": "3",  # 3 终端商户， 4 普通商户
        "openBusinessWay": "1",  # 【1：API   2：Web】
        "holidayCharge": "0",  # 节假日计费标识【0：否 1：是】",
        "holidayFactorage": "10",  # "节假日手续费",
        "holidayMinLimit": "10",  # "节假日保底值(元)",
        "chargeType": "1",  # "手续费收取方式【1：实收 2：非实收】",
        "agentPayFlag": "0",  # "支付转代付【0：否  1：是】",
        "industryFlg": "121321",  # "行业标识（对应码值）",
        "signRemark": "签约备注",
        "sign_image": [
            # --商户协议书,
            {
              'imgSysNo': 1123
            },
        ],
        "merchInfo": {
            "shopRegName": "商户注册名称",
            "shopNickName": "商户简称",
            "shopOperateAddr": "商户经营地址",
            "website": "http: //www.sandpay.com.cn",
            "businessScope": "主营业务范围",
            "businessDepict": "主营业务场景描述",
            "shopType": "1",  # "企业性质【1：股份公司2：有限公司3：个体工商户4：机关事业单位5：个人6：其他】",
            "registCost": "100000",  # "注册资本（万元）",
            "registDate": "20111111111111",   # "注册时间",
            "shopCorp": "商户法人",
            "corpCretType": "32232",  # "法人证据类型（对应码值）",
            "corpCretNo": "法人证件号",
            "corpStartDate": "证件有效起始日期",
            "corpExpiryDate": "证件有效结束日期",
            "shopRemark": "商户备注",
            "bmBusinessLicense": {
                "businessLicenseType": "营业执照类型（对应码表）",
                "businessLicense": "营业执照号",
                "licenseStartDate": "营业执照有效起始日期",
                "licenseExpiryDate": "营业执照有效结束日期",
            },
            "merch_image": [
                # --法人证件营业执照开户许可证,
                {
                  'imgSysNo': 324234
                },
            ],
        },
        "payAccountInfos": [
            {
                "openType": "1",  # "账户性质【1：对公2：对私】",
                "accountName": "账户名称",
                "accountBank": "开户银行",
                "accountBankCode": "开户行联行号",
                "account": "帐号",
                "postscript": "附言",
                "accountType": "1",  # "账户类型【1：代付自动充值账户 2：结算账户 3：来款账户】",
                "effectDate": "账户启用日期",
                "ineffectDate": "账户停用日期",
                "account_image": [
                    {
                         'imgSysNo': 23232
                    },
                ],
            },
        ],
        "payProductInfos": [
            {
                "productSysNo": "开通产品编码",
                "oneMaxMonery": "单笔限额",
                "dayMaxMonery": "日累计限额",
                "dayMaxPen": "日累计交易笔数",
                "creditMonery": "授信额度（单位元）",
                "effectDate": "产品启用日期",
                "ineffectDate": "产品停用日期",
                "isBatchFlg": "0",  # "是否批转单标识【0：支持1：不支持】",
                "isCreditCardFlg": "0",  # "是否屏蔽贷记卡【0：否 1：是】",
                "clearingCycle": "0",  # "清算周期【0：T1  1：T0  2：D0】",
                "td0Factorage": "T0/D0费率",
                "td0MinLimit": "T0/D0手续费保底（单位元）",
                "chargeMode": "计费方式【1：标准 2：按交易金额区间】",
                "rateType": "扣率计费类型【0：按笔 1：按扣率】",
                "productRates": [
                    {
                        "startYuan": "金额区间起始值",
                        "endYuan": "金额区间结束值",
                        "yuanPen": "元/笔或扣率(0.38%值为0.38)",
                        "upperLimitYuan": "上限值",
                        "lowerLimitYuan": "下限值",
                        "debitNratePer": "借记卡费率信息(0.38%值为0.38)",
                        "debitUpperLimitYuan": "借记卡上限值(元)",
                        "debitLowerLimitYuan": "借记卡限值(元)",
                        "creditNratePer": "贷记卡费率信息(0.38%值为0.38)",
                        "creditUpperLimitYuan": "贷记卡上限值(元)",
                        "creditLowerLimitYuan": "贷记卡限值(元)",
                        "effectDate": "扣率启用日期",
                        "ineffectDate": "扣率停用日期",
                    },
                ],
                "channelInfos": [
                    {
                        "channelCode": "渠道编码",

                    },
                ],
            },
        ]
    }

    payload = {"head": head, "body": body}
    _data = json.dumps(payload).replace(' ', '')
    _rsakey = RSA.importKey(_PUBLIC_KEY)
    cipher = Cipher_pkcs1_v1_5.new(_rsakey)
    key = "".join(random.sample(string.letters + string.digits, 16))
    data = {
        "charset": "utf-8",
        "mid": "m9999",
        "encryptKey": b64encode(cipher.encrypt(key)),
        "encryptData": aes_crypto(_data, key),
        "sign": b64encode(sign_string(_data)),
        "access_token": "test",
        "extend": "",
    }
    resp = requests.post(URL, data=data)
    print "-------------------------", resp.content
    print 'resp', resp
    resp_dct = parse_qs(unquote(resp.text))
    print resp_dct
    encrypt_data = resp_dct['encryptData'][0]
    print 'encrypt_data', encrypt_data
    encrypt_key = resp_dct['encryptKey'][0]
    print encrypt_key
    aes_key = decrypt_aes_key(encrypt_key)
    print 'aes_key', aes_key

    handler(aes_key, encrypt_data.replace(' ', '+'))


def handler(aes_key, encrypt_data):
    cryptor = AES.new(aes_key, AES.MODE_ECB, b'0000000000000000')
    plain_text = b64decode(encrypt_data)
    # print 'plain_text: ', plain_text
    # c = a2b_hex(encrypt_data)
    aaaa = cryptor.decrypt(plain_text)
    print 'aaaa: ', aaaa
    print '$###########'


def test_upload():
    url = "http://61.129.71.103:8013/new_ecmis/api/sandpay/file/upload.do"

    payload = {
        "head": {
            "version": "1.0",
            "access_token": "test",
            "method": "sandpay.merch.add",
            "accessType": "1",
            "mid": "P79915",
            "reqTime": datetime.now().strftime("%Y%m%d%H%M%S")
        },
        "body": {
            "optType": "1",
            "uploadFlg": "1",
        }
    }

    _data = json.dumps(payload).replace(' ', '')
    _rsakey = RSA.importKey(_PUBLIC_KEY)
    cipher = Cipher_pkcs1_v1_5.new(_rsakey)
    key = "".join(random.sample(string.letters + string.digits, 16))

    data = {
        "charset": "utf-8",
        "mid": "P79915",
        # "encryptKey": b64encode(cipher.encrypt(key)),
        # "encryptData": aes_crypto(_data, key),
        # "sign": b64encode(sign_string(_data)),
        "access_token": "test",
        "data": payload,
    }
    # print 'data', data['data']
    post_files =dict()
    post_files['back'] = ('back.jpg', open('/home/neil/payS/PayService/test_script/farenA.png', 'rb'))
    print 'data', b64encode(json.dumps(data))
    data = '{"body":{"optType":"1","uploadFlg":"1"},"head":{"reqTime":"20171109102100","method":"","mid":"P79915","access_token":"cGF5Lm1lcmNo","accessType":"1","version":"1.0"}}'
    resp = requests.post(url, data={"data": b64encode(data)}, files=post_files)
    print resp, resp.text


if __name__ == "__main__":
    # test_sand_jinjian()
    test_upload()
