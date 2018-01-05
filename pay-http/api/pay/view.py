# -*- coding: utf-8 -*-
import base64
import logging
import json
import os.path
import time
import requests
import pyDes
import xmltodict
from decimal import Decimal
from random import randint

from flask import request
import sqlalchemy.exc
import _mysql_exceptions
from flask import redirect
from werkzeug.utils import secure_filename

from common.sign import generate_sign
from api.pay import bp_pay
from utils.api import response_wrapper, payapi_wrapper
from utils import err
from db.pay_record.model import PAY_TYPE, convert_pay_status
from third import guangda, keda, sand, wanhong, swiftpass, alipay_official
from db.account.model import REAL_PAY
from db.pay_record.controller import (
    succeed_pay, fail_pay, get_pay, get_pay_by_id, create_withdraw_record,
    update_withdraw_record, get_withdraw_balance)
from handler.pay import create_pay_record, notify_merchant
from db.account.controller import get_appid_detail, get_appkey, get_jinjian_appkey, create_jinjian_record
from cache.redis_cache import submit_timer_event, fresh_overload_alipay_set, incr_alipay_today_amount
from timer import EVENT_ENUM
from db import orm
from cache.redis_cache import set_alipay_qr, get_alipay_qr
from utils.id_generator import generate_long_id
from utils.types import Enum

# 订单号重复,这2个错误都出现过,可能与版本有关,待研究
IntegrityErrors = (sqlalchemy.exc.IntegrityError, _mysql_exceptions.IntegrityError)

_LOGGER = logging.getLogger(__name__)
_TRACKER = logging.getLogger('tracker')
_EVERY_DAY_MAX = 2000000

_PAY_HANDLER = {
    REAL_PAY.GUANGDA: guangda,
    REAL_PAY.KEDA: keda,
    REAL_PAY.SAND: sand,
    REAL_PAY.SWIFTPASS: swiftpass,
    REAL_PAY.ALIPAY: alipay_official
}


@response_wrapper
def test_wechat_h5():
    """
    微信扫码付转H5测试
    """
    pay_type = PAY_TYPE.WECHAT_QR
    amount = Decimal(1)
    appid = '100000'
    try:
        pay_record = create_pay_record(int(time.time() * 1000), '', appid, pay_type, amount, '')
    except IntegrityErrors:
        return {
            'status': -1,
            'error': 'Duplicate order id'
        }
    result = guangda.qr_pay(pay_record)
    return redirect(result['qrCode'])


@response_wrapper
def get_public_alipay_qr():
    amount = request.args.get('amount')
    _type = request.args.get('type')
    if amount:
        amount = Decimal(amount) / 100
    else:
        amount = Decimal(randint(1, 3))
    pay_type = PAY_TYPE.ALIPAY_QR
    appid = '100002'
    try:
        pay_record = create_pay_record(int(time.time() * 1000), '', appid, pay_type, amount, '')
    except IntegrityErrors:
        return {
            'status': -1,
            'error': 'Duplicate order id'
        }
    result = keda.qr_pay(pay_record, order_info=u'体验支付')
    result['orderid'] = str(pay_record.id)
    result['amount'] = str(amount)
    if _type == 'h5':
        return redirect(result['qrCode'])
    return result


@response_wrapper
def get_public_wechat_h5_status():
    pass


@response_wrapper
def get_public_wechat_h5(amount):
    clientip = request.headers.get('X-Real-IP') or request.remote_addr
    pay_type = PAY_TYPE.WECHAT_H5
    amount = Decimal(amount) / 100
    appid = '100000'
    try:
        pay_record = create_pay_record(int(time.time() * 1000), '', appid, pay_type, amount, '')
    except Exception as e:
        return {
            'status': -1,
            'error': 'Duplicate order id'
        }
    result = guangda.wechat_h5_pay(pay_record, u'体验支付', clientip)
    result['orderid'] = str(pay_record.id)
    url = result['url']
    return """
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document</title>
</head>
<body>
    <a href="%s">点击这里跳转完成支付</a>
</body>
</html>
    """ % url


@response_wrapper
def get_public_wechat_qr_status():
    orderid = request.args['orderid']
    pay_record = get_pay(orderid)
    if not pay_record:
        raise err.ParamError('invalid orderid')

    return {'pay_status': pay_record.pay_status}


@response_wrapper
def get_public_wechat_qr(amount=0):
    if not amount:
        amount = Decimal(randint(1, 3))
    pay_type = PAY_TYPE.WECHAT_QR
    appid = '100001'
    try:
        pay_record = create_pay_record(int(time.time() * 1000), '', appid, pay_type, amount, '')
    except IntegrityErrors:
        raise err.DuplicateOrderID(u"订单号重复")
    result = keda.qr_pay(pay_record, order_info=u'体验支付')
    result['orderid'] = str(pay_record.id)
    result['amount'] = str(amount)
    return result


@payapi_wrapper
def query_pay():
    query_dct = request.get_json(force=True) or {}
    _LOGGER.info(query_dct)
    check_sign(query_dct)
    try:
        appid = query_dct['appid']
        orderid = query_dct['orderid']
    except Exception as e:
        return {'error': 'miss column'}
    pay_record = get_pay_by_id(appid, orderid)
    if not pay_record:
        raise err.NoOrderID()
    pay_type = pay_record.pay_type
    resp_data = {
        'orderid': pay_record.orderid,
        'amount': str(pay_record.amount),
        'pay_type': pay_type,
        'pay_status': convert_pay_status(pay_record.pay_status)
    }
    appkey = get_appkey(appid)
    sign = generate_sign(resp_data, appkey)
    resp_data['signature'] = sign
    return resp_data


@payapi_wrapper
def submit_pay():
    def check_payamount(s):
        if int(float(s)) % 10 == 0 and abs(int(float(s)) - float(s)) < 0.0099999999999999999999:
            return False
        return True

    # raise err.SystemError('支付宝渠道维护,请使用其他方式支付.')
    query_dct = request.get_json(force=True) or {}
    _LOGGER.info('submit_pay: %s' % query_dct)
    check_sign(query_dct)
    try:
        appid = query_dct['appid']
        wechatid = query_dct.get('wechatid')
        pay_type = int(query_dct.get('payType'))
        appid_detail = get_appid_detail(appid, pay_type, polling=False)
    except Exception, e:
        _LOGGER.exception('create pay error!')
        raise err.SystemError()
    if not appid_detail:
        raise err.AppIDWrong()
    if not appid_detail.valid:
        raise err.AppidInvalid()
    orderid = query_dct['orderid']
    amount = Decimal(query_dct['amount'])
    if not check_payamount(amount):
        raise err.ParamError('amount should not be divided by 10')
    notify_url = query_dct['notifyUrl']
    ordername = query_dct.get('subject')
    clientip = query_dct.get('clientip')
    order_info = query_dct.get('orderInfo')
    return_url = query_dct.get('returnUrl')
    description = query_dct.get('description')
    try:
        pay_record = create_pay_record(orderid, appid_detail.accountid, appid,
                                       pay_type, amount, notify_url,
                                       description)
    except IntegrityErrors:
        raise err.DuplicateOrderID()
    except Exception as e:
        _LOGGER.exception('db error')
        raise err.SystemError()
    finally:
        orm.session.rollback()

    pay_handler = _PAY_HANDLER[appid_detail.real_pay]
    # 支付宝扫码付线下要一元以上
    if pay_type == PAY_TYPE.ALIPAY_QR and amount < Decimal('1'):
        raise err.MiniAmount()
    if pay_type == PAY_TYPE.WECHAT_H5:
        result = pay_handler.wechat_h5_pay(pay_record, ordername, clientip)
    elif pay_type == PAY_TYPE.ALIPAY_REAL_H5:
        result = pay_handler.alipay_h5_pay(pay_record, ordername, return_url)
    elif pay_type in (PAY_TYPE.WECHAT_QR, PAY_TYPE.QQ_QR, PAY_TYPE.ALIPAY_QR, PAY_TYPE.ALIPAY_H5):
        result = pay_handler.qr_pay(pay_record, order_info)
        if pay_type == PAY_TYPE.ALIPAY_H5 and 'qrCode' in result:
            qrCode = result.pop('qrCode')
            pay_id = pay_record.id
            set_alipay_qr(pay_record.id, qrCode)
            result['url'] = 'http://p.51paypay.net/api/v1/pay/alipay_h5/%s' % pay_id
            return result
    elif pay_type == PAY_TYPE.WECHAT_SDK:
        result = pay_handler.wechat_sdk_pay(pay_record, wechatid, ordername)
    else:
        raise err.PayTypeNotSupport()
    return result


@response_wrapper
def guangda_callback():
    """
    json loads body后的格式
    {u'acctCat': u'06',
     u'acquirerType': u'wechat',
     u'currency': u'CNY',
     u'custId': u'170822185829458',
     u'reqId': u'1000005',
     u'totalAmount': u'1',
     u'transAmount': u'1',
     u'transId': 708301706522270082,
     u'transResult': u'2',
     u'transTime': u'20170830170256',
     u'transType': u'1',
     u'uuid': u'ofCcf0y1wyICkeYS57V23wx6QSiQ',
     u'walletOrderId': u'1708300013436934',
     u'walletTransId': u'4000752001201708309139290722'}
    """
    try:
        body, sign = request.form['body'], request.form['sign']
        if guangda.verify_sign(body, sign):
            pay_detail = json.loads(body)
            orderid = pay_detail['reqId']
            amount = Decimal(pay_detail['totalAmount']) / 100
            originid = pay_detail['transId']  # 上游的订单号
            result = pay_detail['transResult']
            if result == '2':
                succeed_pay(originid, orderid, amount, extend=body)
                notify_merchant(orderid)
            else:
                fail_pay(originid, orderid, amount, extend=body)
            return 'SUCCESS'
        else:
            _LOGGER.info('sign error')
            return 'FAIL'
    except Exception as e:
        _LOGGER.exception('pay callback error')
        return 'FAIL'


@response_wrapper
def sand_callback():
    _LOGGER.info('sand callback form: %s' % request.form)

    data = request.form['data']
    req_dct = json.loads(data)
    sign = request.form['sign']
    # if not sand.verify_sign(data, sign):  # 验签有问题
    #     _LOGGER.info("sand verify sign error: %s" % request.form)
    #     return 'respCode=111111'

    orderid = req_dct['body']['orderCode']
    amount = int(req_dct['body']['buyerPayAmount']) / 100.0
    succeed_pay('', int(orderid), amount, extend=data)
    notify_merchant(orderid)

    return 'respCode=000000'

@response_wrapper
def alipay_callback():
    data = request.form.to_dict()
    _LOGGER.info('alipay callback form: %s' % data)
    signature = data.pop('sign')
    if alipay_official.check_data(data, signature):
        orderid = data['out_trade_no']
        amount = float(data['total_amount'])
        succeed_pay('', int(orderid), amount, extend=json.dumps(data))
        alipayid = data['app_id'].strip()
        if float(incr_alipay_today_amount(alipayid, amount)) > _EVERY_DAY_MAX:
            fresh_overload_alipay_set(alipayid)
        notify_merchant(orderid)
        return 'success'
    else:
        return 'fail'


def parse_callback(body):
    data = json.loads(body)


def check_sign(data):
    sign = data.pop('signature')
    appid = data['appid']
    appkey = get_appkey(appid)
    calculated_sign = generate_sign(data, appkey)
    if sign.lower() != calculated_sign:
        _LOGGER.info("sign: %s, calculated sign: %s",
                     sign, calculated_sign)
        raise err.SignWrongError('签名错误')


def check_jinjian_sign(data, appid, signature):
    from copy import deepcopy
    data = deepcopy(data)
    data['appid'] = appid
    appkey = get_jinjian_appkey(appid)
    calculated_sign = generate_sign(data, appkey)
    if signature.lower() != calculated_sign:
        _LOGGER.info("sign: %s, calculated sign: %s",
                     signature, calculated_sign)
        raise err.ParamError('sign not pass')


@response_wrapper
def keda_callback():
    """
    {"orderCode":"1617773825225665536","date":"mw+xc48bhv4v2ByZHA6wOJcCSV/xum3FiNahHgNYth2YZhUlJOLqPLfJnsRVT9DwijxSemMFMfTc\nkp24wgv1cKmuyp9zdzvoJlcjtvOuBkBygbeE87IjqVYqWZ0tNsW9GOJiswNxRmo4AF7d+TJ1Kf/wRnF4TEgQLqH0MLDriH2yx5kntdvp0GDa6KZcue+8oIhevOhRcR3k8fpOK9KAAg=="}
    """
    resp_data = request.data
    _LOGGER.info(resp_data)
    json_data = json.loads(resp_data)
    orderid = int(json_data['orderCode'])
    crypto_data = json_data['date']
    pay_detail = keda.decrypto(crypto_data)

    amount = Decimal(pay_detail["totalFee"]) / 100
    # FIXME： 支付宝和微信返回不一样
    result = pay_detail.get("state") or pay_detail['tradeState']

    if result in ('SUCCESS', 'TRADE_SUCCESS'):
        succeed_pay('', int(orderid), amount, extend=json.dumps(pay_detail))
        notify_merchant(orderid)
    else:
        fail_pay('', orderid, amount, extend=pay_detail)
    return 'SUCCESS'


@response_wrapper
def keda_jinjian_callback():
    """
    审核回调: status(2-通过,1-不通过), merchantcode, comment
    激活回调: paystatus(2-通过,1-不通过), merchantcode,
    """
    data = request.get_json(force=True) or {}
    data['action'] = 'keda_jinjain'
    _TRACKER.info(data)
    merchantcode = data['merchantcode']
    bankLinkNumber = data['bankLinkNumber']
    status = str(data.get('status'))
    paystatus = str(data.get('paystatus'))
    comment = data.get('comment')
    if 'status' in data:
        if status == '2':  # 审核通过
            pass
        if status == '1':  # 不通过
            pass
    if 'paystatus' in data:
        if paystatus == '2':  # 费率激活
            pass
        if paystatus == '1':  # 费率不通过
            pass
    return 'SUCCESS'


@response_wrapper
def get_alipay_h5(payid):
    qrCode = get_alipay_qr(payid)
    if qrCode:
        return redirect(qrCode)
    else:
        return """
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="X-UA-Compatible" content="ie=edge">
                <title>支付错误</title>
            </head>
            <body>
                <h4>支付遇到错误!</h4>
            </body>
            </html>
        """


@payapi_wrapper
def withdraw_query():
    data = request.get_json(force=True) or {}
    check_sign(data)
    try:
        appid = data['appid']
        order_code = data['orderCode']
        # appid_detail = get_appid_detail(appid, real_pay=REAL_PAY.KEDA)
        trans_time = data.get('transTime', None)
        appid_detail = get_appid_detail(appid)  # , real_pay=REAL_PAY.KEDA)
    except KeyError as e:
        raise err.RequestParamError(u"缺少%s" % str(e))
    except Exception:
        _LOGGER.exception('withdraw query error')
        raise err.SystemError()
    if appid_detail.real_pay == REAL_PAY.KEDA:
        if appid_detail.paymenttype != 'D0':
            raise err.OnlyD0SupportWithdraw()
        result = keda.query_d0_withdraw(appid_detail.custid, order_code)
        if result['error'] == -1:
            raise err.SystemError(result['message'])
        else:
            _data = result['data']
            _data['orderMoney'] = str(Decimal(_data['orderMoney']) / 100)
            return {
                'status': 0,
                'data': _data
            }
    if appid_detail.real_pay == REAL_PAY.SAND:
        if not trans_time:
            raise err.SystemError("transTime arg missing")
        result = sand.query_d0_withdraw(appid_detail.custid, order_code, trans_time)
        if result['respCode'] != '0000':
            raise err.SystemError(result['respDesc'])
        else:
            return result



@response_wrapper
def keda_jinjian():
    '''
    进件格式:
    {
        "appid": "xxxxx",
        "signature": "yyyyyy",
        "mchName": "bankLinkNumber"
        "address": "xx路yy街道"
    }
    '''
    _OFFICECODE = '0000000035'
    _KEY = 'UyRk88Ec'
    columns = ('bankLinkNumber', 'mchName', 'mchShortName', 'city', 'province', 'district',
               'address', 'mobile', 'bankNo', 'industryNo', 'balanceType', 'balanceName',
               'userIdNumber', 'cardImgA', 'legalIdNumber', 'cardNumbercontact', 'licenseStartDate',
               'licenseScope', 'licenseImg', 'paymentType', 'zfbpay', 'wxpay', 'accountLicense',
               'licensePeriod', 'licenseEndDate', 'wxValue', 'aliValue', 'cardNumber', 'contact', 'licenseNum')
    file_columns = ('legalIDCardA', 'legalIDCardB', 'userIDCardA', 'userIDCardB', 'cardImgA', 'licenseImg')
    jinjian_id = generate_long_id('jinjian')
    post_files = {}
    for file_column in file_columns:
        f = request.files.get(file_column)
        if f:
            filename = secure_filename(f.filename)
            d = os.path.join('/home/ubuntu/flask-env/data/jinjian', str(jinjian_id))
            os.makedirs(d)
            fp = os.path.join(d, filename)
            f.save(fp)
            post_files[file_column] = (file_column, open(fp, 'rb'))
    post_data = {}
    for column in columns:
        value = request.form.get(column)
        if value:
            post_data[column] = value
    appid = request.form['appid']
    check_jinjian_sign(post_data, appid, request.form['signature'])
    url = 'http://116.62.100.174/Bank/mobile/zhBank/addMerchant'
    post_data['officeCode'] = _OFFICECODE
    post_data['notifyUrl'] = 'http://p.51paypay.net/api/v1/callback'
    auth_str = json.dumps({'officeCode': _OFFICECODE, 'KEY': _KEY})
    k = pyDes.des(_KEY, pyDes.ECB, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = base64.b64encode(k.encrypt(auth_str))

    headers = {'Authorization': d}

    resp = requests.post(url=url, data=post_data, headers=headers, files=post_files)
    if resp.status_code == 200:
        content = resp.content
        resp_data = json.loads(content)
        """
        {
            "message": "进件申请成功，等待审核！",
            "error": 0,
            "data":{
                "bankLinkNumber":"308584000013",
                "merchantCode":"T20170921145929293"
            },
            "success":true
        }
        """
        mch_name = post_data.get('mchShortName')
        if resp_data.get('success') and resp_data.get('error') == 0:
            custid = resp_data['data']['merchantCode']
        else:
            custid = None
        create_jinjian_record(
            appid, REAL_PAY.KEDA, json.dumps(post_data), content.encode('utf-8'), mch_name=mch_name,
            custid=custid, jinjian_id=jinjian_id,
            status=0)
        return resp_data
    else:
        _LOGGER.info("keda jinjian response error")
        _LOGGER.info(post_data)
        return '{"message":"system error", "error":-1,"success":false}'


@response_wrapper
def wanhong_callback():
    data = request.form
    _LOGGER.info('wanhong callback: %s' % data)
    if not wanhong.verify_sign(data):
        _LOGGER.info('wanhong callback verify sign false')
        return 'fail'
    respCode = data['respCode']
    amount = Decimal(data['transAmt']) / 100
    originid = data['serialId']
    orderid = data['orderNo']
    if respCode == '0000':
        succeed_pay(originid, int(orderid), amount, extend=json.dumps(data))
        notify_merchant(orderid)
    else:
        fail_pay(originid, orderid, amount, extend=data)
    return 'success'


@response_wrapper
def swiftpass_callback():
    data = request.data
    _LOGGER.info('swiftpass callback: %s' % data)
    data = xmltodict.parse(data)['xml']
    data = dict(data)
    sign = data.pop('sign')
    if not swiftpass.check_sign(data, sign):
        _LOGGER.info('swiftpass callback verify sign false')
        return 'fail'
    status = data.get('status')
    result_code = data.get('result_code')
    pay_result = data.get('pay_result')
    originid = data.get('399540514434201711104298061303')
    orderid = data.get('out_trade_no')
    if status == '0' and result_code == '0':
        amount = Decimal(data['total_fee']) / 100
        if pay_result == '0':
            succeed_pay(originid, orderid, amount, extend=json.dumps(data))
            notify_merchant(orderid)
        else:
            fail_pay(originid, orderid, amount, extend=json.dumps(data))
    else:
        _LOGGER.error('swiftpass callback order data error')
    return 'success'

@response_wrapper
def yinshengdf_callback():
    return 'success'

@response_wrapper
def sand_agent_pay():
    query_dct = request.get_json(force=True) or {}
    _LOGGER.info('sand agent pay: %s' % query_dct)
    check_sign(query_dct)
    try:
        amount = str(query_dct['amount'])
        appid = query_dct['appid']
        order_code = query_dct['orderCode']
        acc_attr = query_dct['accAttr']
        acc_type = query_dct['accType']
        acc_no = query_dct['accNo']
        acc_name = query_dct['accName']
        pay_mode = query_dct['payMode']
        trans_time = query_dct['transTime']
        appid_detail = get_appid_detail(appid, real_pay=REAL_PAY.SAND)
    except Exception, e:
        _LOGGER.exception('sand agent pay error! %s' % e)
        raise err.ParamError(e)

    if not appid_detail or not appid_detail.custid:
        raise err.AppIDWrong()

    record = create_withdraw_record(appid, REAL_PAY.SAND, amount, channel="bank",
                                    mchid=appid_detail.accountid,
                                    order_code=order_code, acc_name=acc_name,
                                    to_account=acc_no, trans_time=int(trans_time))
    resp = sand.create_agent_pay(appid_detail.custid, amount, order_code, acc_attr, acc_type,
                                 acc_no, acc_name, pay_mode, trans_time)
    _PAY_STATUS = Enum({
        "SUCCESS": (2L, "代付成功"),
        "FAILED": (3L, "代付失败"),
    })
    if resp['data'].get('respCode', '') == '0000':
        fee = float(resp['data']['tranFee']) / 100.0
        update_withdraw_record(record, fee, order_code, _PAY_STATUS.SUCCESS)  # paystatus=2表示成功，跟客达一致
    else:
        update_withdraw_record(record, 0, order_code, _PAY_STATUS.FAILED)  # paystatus=3表示失败

    return resp


# 体验支付
bp_pay.add_url_rule('/pay/public/wechat_qr/status/', view_func=get_public_wechat_qr_status, methods=['GET'])
bp_pay.add_url_rule('/pay/public/wechat_qr/', view_func=get_public_wechat_qr, methods=['GET'])
bp_pay.add_url_rule('/pay/public/wechat_qr/<int:amount>', view_func=get_public_wechat_qr, methods=['GET'])
bp_pay.add_url_rule('/pay/public/wechat_h5/status/', view_func=get_public_wechat_h5_status, methods=['GET'])
bp_pay.add_url_rule('/pay/public/wechat_h5/<int:amount>', view_func=get_public_wechat_h5, methods=['GET'])
bp_pay.add_url_rule('/pay/public/alipay_qr/', view_func=get_public_alipay_qr, methods=['GET'])
bp_pay.add_url_rule('/pay/public/tw', view_func=test_wechat_h5, methods=['GET'])
# 支付回调
bp_pay.add_url_rule('/pay/guangda/callback', view_func=guangda_callback, methods=['POST'])
bp_pay.add_url_rule('/pay/keda/callback', view_func=keda_callback, methods=['POST'])
bp_pay.add_url_rule('/pay/sand/callback', view_func=sand_callback, methods=['POST'])
bp_pay.add_url_rule('/pay/wanhong/callback', view_func=wanhong_callback, methods=['POST'])
bp_pay.add_url_rule('/pay/swiftpass/callback', view_func=swiftpass_callback, methods=['POST'])
bp_pay.add_url_rule('/pay/alipay/callback', view_func=alipay_callback, methods=['POST'])
bp_pay.add_url_rule('/pay/ali/callback', view_func=alipay_callback, methods=['POST'])
bp_pay.add_url_rule('/p/alipay/callback', view_func=alipay_callback, methods=['POST'])
# 下单接口
bp_pay.add_url_rule('/pay/submit', view_func=submit_pay, methods=['POST'])
bp_pay.add_url_rule('/pay/alipay_h5/<int:payid>', view_func=get_alipay_h5, methods=['GET'])
# 查询接口
bp_pay.add_url_rule('/pay/query/', view_func=query_pay, methods=['POST'])
# 客达进件回调
bp_pay.add_url_rule('/keda/jinjian/callback', view_func=keda_jinjian_callback, methods=['POST'])
bp_pay.add_url_rule('/ysdf/callback', view_func=yinshengdf_callback, methods=['POST'])
# 平台商进件
bp_pay.add_url_rule('/jinjian/k/', view_func=keda_jinjian, methods=['POST'])
# 杉德代付
bp_pay.add_url_rule('/pay/agent_pay', view_func=sand_agent_pay, methods=['POST'])
