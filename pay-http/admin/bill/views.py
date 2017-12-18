# coding: utf-8
import json
import logging

from datetime import datetime
from flask import request, g
from flask_login import login_required, current_user

from db.account.model import Account
from db.pay_record.model import PayRecord, convert_mch_pay_status
from db.pay_record.controller import export_pay_records, get_withdraw_by_id
from db.account.controller import get_appid_detail, get_withdraw_done
from controller import get_pay_record, get_withdraw_record
from . import bill as bill_blueprint
from utils.api import token_required, response_wrapper
from utils.export import gen_filename, redirect_to_file
from utils.tz import local_to_utc, utc_to_local_str

ITEMS_PER_PAGE = 100

_LOGGER = logging.getLogger(__name__)


def fill_results(bills):
    results = []
    for bill in bills:
        result = {}
        result['order'] = bill.access_seq
        result['bank_merchant_number'] = bill.bank_merchant_number
        result['access_submit_date'] = datetime.strftime(
            bill.access_submit_date, '%Y-%m-%d %H:%M:%S')
        result['platform_seq'] = bill.platform_seq
        result['platform_trade_date'] = datetime.strftime(
            bill.platform_trade_date, '%Y-%m-%d %H:%M:%S')
        result['account'] = bill.account
        result['pay_type'] = bill.pay_type
        result['pay_status'] = bill.trade_status
        result['trade_type'] = bill.trade_type
        result['trade_amount'] = bill.trade_amount
        result['poundage'] = bill.poundage
        result['settling_amount'] = bill.settling_amount
        results.append(result)
    return results


def convert(bills):
    result = {}
    result['counts'] = len(bills)
    sum = 0.0
    for bill in bills:
        amount = float(bill.trade_amount)
        sum += amount

    result['sum'] = '%.2f' % sum
    result['bills'] = fill_results(bills)
    return json.dumps(result)


EMPTY_RESULT = '{"counts":0,"sum":"0.00","bills":[]}'


@bill_blueprint.route('/query_bill', methods=['GET'])
@response_wrapper
@token_required
def query_pay_record():
    pay_type = request.args.get('pay_type')
    pay_status = request.args.get('pay_status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    access_seq = request.args.get('order')
    appid = request.args.get('appid')
    page = request.args.get('page', 1)
    vip = int(request.args.get('vip', 0))
    page = int(page)
    size = request.args.get('size', 10)
    size = int(size)
    export = request.args.get('export', 0)
    export = int(export)
    pay_status = convert_mch_pay_status(pay_status)
    if start_date:
        start_date = local_to_utc(datetime.strptime(start_date + '000000', '%Y-%m-%d%H%M%S'))
    if end_date:
        end_date = local_to_utc(datetime.strptime(end_date + '235959', '%Y-%m-%d%H%M%S'))

    user_id = g.user['id']

    if export:
        if vip:
            cn_headers = [u'商户ID', u'应用ID', u'流水单号', u'备注信息',
                          u'交易日期', u'交易类型', u'交易状态', u'交易金额']
        else:
            cn_headers = [u'商户ID', u'应用ID', u'流水单号', u'交易日期',
                          u'交易类型', u'交易状态', u'交易金额']
        data = export_pay_records(user_id, pay_type, pay_status, start_date, end_date, access_seq, appid)
        filename = gen_filename('export_pay_record')
        if data:
            return redirect_to_file(data, cn_headers, filename, u'流水单号')
    else:
        bills, counts, pages, amount_sum, fee, service_fee, balance = get_pay_record(user_id, pay_type, pay_status,
                                                                                     start_date, end_date, access_seq,
                                                                                     appid,
                                                                                     page,
                                                                                     size)
        if not vip:
            [bill.pop('description') for bill in bills]
        resp = {
            'pages': pages,
            'bills': bills,
            'counts': counts,
            'amount_sum': '%.2f' % amount_sum,
            'fee': '%.2f' % fee,
            'service_fee': '%.2f' % service_fee,
            'balance': '%.2f' % balance,
            'withdraw_done': '%.2f' % get_withdraw_done(user_id, appid=appid)
        }
        return resp


@bill_blueprint.route('/query_withdraw', methods=['GET'])
@response_wrapper
@token_required
def query_withdraw_record():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_amount = request.args.get('start_amount')
    end_amount = request.args.get('end_amount')
    pay_type = request.args.get('pay_type')
    order_code = request.args.get('order_code')
    pay_status = request.args.get('pay_status')
    withdraw_status = request.args.get('withdraw_status')
    appid = request.args.get('appid')
    page = request.args.get('page', 1)
    page = int(page)
    size = request.args.get('size', 10)
    size = int(size)
    _CONVERT_PAY_TYPE = {
        1: "bank",
        2: "weixin",
        3: "alipay_h5",
    }
    if pay_type:
        pay_type = _CONVERT_PAY_TYPE[int(pay_type)]
    if start_date:
        start_date = local_to_utc(datetime.strptime(start_date + '000000', '%Y-%m-%d%H%M%S'))
    if end_date:
        end_date = local_to_utc(datetime.strptime(end_date + '235959', '%Y-%m-%d%H%M%S'))
    accountid = g.user['id']
    resp_to = get_withdraw_record(accountid, order_code, pay_type, pay_status, start_amount, end_amount, appid,
                               start_date, end_date, withdraw_status, page, size)
    resp_to.update({'withdraw_done': '%.2f' % get_withdraw_done(accountid, appid=appid)})
    return resp_to


@bill_blueprint.route('/query_withdraw_detail', methods=['GET'])
@response_wrapper
@token_required
def query_withdraw_detail():
    id = request.args.get('id')
    withdraw_detail = get_withdraw_by_id(id)
    appid = withdraw_detail.appid
    appid_detail = get_appid_detail(appid)
    resp = {
        "channel": withdraw_detail.channel,
        "to_account": withdraw_detail.to_account,
        "to_acc_name": withdraw_detail.acc_name,
        "created_at": utc_to_local_str(withdraw_detail.created_at),
        "extend": withdraw_detail.extend,
        "appid": withdraw_detail.appid,
        "amount": '%.2f' % withdraw_detail.amount,
        "fee": '%.2f' % withdraw_detail.fee,
        "total": '%.2f' % (withdraw_detail.amount + withdraw_detail.fee)
    }
    return resp
