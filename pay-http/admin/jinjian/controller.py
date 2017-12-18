# -*- coding: utf-8 -*-
import time
import logging
import os
import binascii
from flask import url_for
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
import json
import requests
import pyDes
import base64
from db.account.model import REAL_PAY, VALID_STATUS, IMG_PATH, APP_TYPE
from db.pay_record.model import PAY_TYPE
from db.account import controller as db
from utils import tz, err
from utils.types import Enum

_LOGGER = logging.getLogger("51paypay")
_DEFAULT_PAGE_SIZE = 100

BANKLINKNO = Enum({
    "ZHAOSHANG": ("308584000013", u"招商银行"),
    "PUFA": ("310290000013", u"浦发银行"),
})


def convert_bankname_to_number(bank_name):
    bank_dct = {
        u"招商银行": BANKLINKNO.ZHAOSHANG,
        u"浦发银行": BANKLINKNO.PUFA,
    }
    return bank_dct.get(bank_name, None)


def sign_string(private_key_path, unsigned_string):
    key = RSA.importKey(open(private_key_path).read())
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(SHA.new(unsigned_string.encode('utf8')))
    return binascii.b2a_hex(signature).upper()


def req_jinjian(jj_id):
    jinjian = db.get_jinjian(jj_id)
    real_pay = jinjian.real_pay
    if real_pay == REAL_PAY.GUANGDA:
        # 光大进件
        status, custid, content = req_guangdajinjian_with_dct(jinjian.jinjian_info)
    elif real_pay == REAL_PAY.KEDA:
        info = jinjian.jinjian_info
        if jinjian.custid is not None:
            info.update({'merchantcode': jinjian.custid})
        status, custid, content = req_kedajinjian_with_dct(info)
    else:  # TODO sand进件
        return None
    jinjian.status = status
    jinjian.custid = custid
    jinjian.resp_data = content
    jinjian.save()
    return status


def req_kedajinjian_with_dct(jinjian_info):
    url = 'http://116.62.100.174/Bank/mobile/zhBank/addMerchant'

    form_dct = {}
    post_files = {}
    for key, value in jinjian_info.items():
        if value and isinstance(value, unicode) and (value.endswith('.png') or
                                                     value.endswith('.jpg') or value.endswith('.bmp')):

            post_files[key] = (key, open(os.path.join(IMG_PATH, value), 'rb'))  # open(IMG_PATH + value).read()
        else:
            form_dct[key] = value

    if "merchantcode" in form_dct:   # 修改商户进件信息
        url = 'http://116.62.100.174/Bank/mobile/zhBank/addMerchantUpdate'

    _KEY = 'UyRk88Ec'
    _officeCode = '0000000035'
    form_dct['officeCode'] = _officeCode
    form_dct['notifyUrl'] = 'http://p.51paypay.net/api/v1/keda/jinjian/callback'
    auth_str = json.dumps({'officeCode': _officeCode, 'Key': _KEY})
    k = pyDes.des(_KEY, pyDes.ECB, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = base64.b64encode(k.encrypt(auth_str))
    headers = {'Authorization': d}

    resp = requests.post(url=url, data=form_dct, headers=headers, files=post_files)
    _LOGGER.info("keda jinjian response: %s", resp.text)
    if resp.status_code == 200:
        content = resp.content
        resp_data = json.loads(content)
        error = resp_data['error']
        success = resp_data['success']
        if error == 0 and success:
            custid = resp_data['data']['merchantCode']
            return VALID_STATUS.SUCCESS, custid, content
    return VALID_STATUS.FAILED, None, resp.content


def req_guangdajinjian_with_dct(jinjian_info):
    aT = [item for item in jinjian_info['acquirerTypes'] if item['scale']]
    jinjian_info["acquirerTypes"] = json.dumps(aT).replace(" ", '')
    jinjian_info["coopMchtId"] = str(int(time.time()) * 1000)
    data = '[%s]' % json.dumps(jinjian_info)
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
    url = 'https://cebwhaop.koolyun.com/apmp/rest/v2/'
    resp = requests.post(url, data=params, headers=headers)
    _LOGGER.info("guangda jinjian request: %s", resp.text)
    if resp.status_code == 200:
        return VALID_STATUS.SUCCESS, None, resp.content
    return VALID_STATUS.FAILED, None, resp.content


def get_appids(mchid, limit, offset):
    """ 只列出有效的appid """
    results = db.get_appids(mchid, limit, offset)

    return [
        {"appid": result[0].appid,
         "appkey": result[0].appkey,
         "jinjian_id": result[1].jinjian_id,
         "mch_name": result[1].mch_name,
         "pay_type": result[0].pay_type} for result in results
    ]


def _convert_paymenttype_to_banklinkname(paymenttype):
    banklinkname = {
        'D0': u'浦发',
        'D1': u'招商',
    }
    return banklinkname.get(paymenttype, '')


def get_app_manage(mchid, page, size, appid, app_type, valid, status,
                   bank_name, begin_at, end_at, mch_name, mch_short_name,
                   appname, paymenttype):
    limit = _DEFAULT_PAGE_SIZE if not size or size > _DEFAULT_PAGE_SIZE else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page - 1) * limit
    apps, count = db.query_app_manage(mchid, appid=appid, app_type=app_type,
                                      valid=valid, appname=appname, limit=limit,
                                      offset=offset, begin_at=begin_at,
                                      end_at=end_at, mch_name=mch_name,
                                      mch_short_name=mch_short_name,
                                      paymenttype=paymenttype)

    return {"total": count,
            "jinjians": [
                {
                 "id": app.id,
                 "status": app.valid,
                 "appname": app.appname,
                 "app_type": app.app_type,
                 "appid": app.appid,
                 "appkey": db.get_appkey(app.appid),
                 "mch_name": app.mch_name,
                 "mch_short_name": app.mch_short_name,
                 "updated_at": tz.utc_to_local_str(app.updated_at),
                 "bank_name": _convert_paymenttype_to_banklinkname(app.paymenttype)
                } for app in apps
            ] if apps else []
            }


def refuse_jinjian(jj_id):
    db.update_jinjian_status(jj_id, VALID_STATUS.REFUSED)


def parse_jinjian_info(jinjian):
    info = {}
    for key, value in jinjian.jinjian_info.items():
        if key == 'bankLinkNumber':
            info['bankLinkName'] = BANKLINKNO.get_label(value)
        if isinstance(value, unicode) and (value.endswith('jpg') or
                                           value.endswith('png') or
                                           value.endswith('bmp') or
                                           value.endswith('jpeg')):
            info[key] = url_for('jinjian.pca')[:-4] + '/data/' + value
        else:
            info[key] = value

    appmanage = db.get_appmanage(jinjian.appmanageid)
    info.update(appmanage.as_dict())
    info.pop('extend')
    if appmanage.extend:
        print appmanage.extend, type(appmanage.extend)
        info.update(json.loads(appmanage.extend))
    info.update({'appkey': db.get_appkey(appmanage.appid)})
    info.pop('mch_name')
    info.pop('mch_short_name')
    info.pop('updated_at')
    info.pop('created_at')
    info.pop('paymenttype')
    info.pop('id')
    info.pop('officeCode')
    info.pop('bankLinkNumber')
    info.update({'app_type': APP_TYPE.get_label(int(info['app_type']))})
    info.update({'wxvalue': 0, 'zfbvalue': 0})  # 只有D0有，现在没有D0
    pay_type_loads = json.loads(info['pay_type'])
    pay_type = '、'.join([PAY_TYPE.get_label(item) for item in pay_type_loads])
    info['pay_type'] = pay_type
    return info


def get_merchants(accountid, mch_name, appid, page, size):
    limit = _DEFAULT_PAGE_SIZE if not size or size > _DEFAULT_PAGE_SIZE else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page - 1) * limit
    apps, counts = db.query_app_manage(accountid,
                                       mch_name=mch_name,
                                       appid=appid,
                                       limit=limit,
                                       offset=offset)
    resp = []
    if apps:
        for app in apps:
            user = db.get_user(app.accountid)
            appid_detail = db.get_appid_detail(app.appid)
            real_pay = REAL_PAY.get_label(appid_detail.real_pay) if appid_detail else None
            extend = None
            if app.extend:
                extend = json.loads(app.extend).get('extend', '')
            resp.append({"real_pay": real_pay,
                         "mch_name": app.mch_name,
                         "phone": user.phone if user else None,
                         "appid": app.appid,
                         "extend": extend,
                         "appkey": db.get_appkey(app.appid),
                         "updated_at": tz.utc_to_local_str(app.updated_at),
                         "mch_number": app.id})

    pages = int(counts / float(limit)) + 1
    return {"pages": pages, "resp": resp}


def get_merchant(accountid, merchant_id):
    mch = db.get_appmanage(merchant_id)
    user = db.get_user(mch.accountid)
    resp = None
    if not mch:
        raise err.ResourceNotFound("无此商户")
    appid_detail = db.get_appid_detail(mch.appid)
    real_pay = REAL_PAY.get_label(appid_detail.real_pay) if appid_detail else None
    resp = mch.as_dict()
    resp.pop("accountid")
    resp.pop("created_at")
    resp.pop("paymenttype")
    resp.pop("mch_number")
    resp.pop("industry_no")
    resp.pop("mch_short_name")
    resp['phone'] = user.phone
    extend = json.loads(resp['extend'])
    resp.update(extend.get('fee', ''))
    resp['extend'] = extend.get('extend', '')
    resp['updated_at'] = tz.utc_to_local_str(resp['updated_at'])
    resp['real_pay'] = real_pay
    return resp
