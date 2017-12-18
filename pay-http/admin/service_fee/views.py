# coding: utf-8
import logging
import json
from decimal import Decimal
from datetime import datetime, date, timedelta
from flask import request, g
import xmltodict
from controller import (get_service_fee, create_recharge_order,
                        succeed_traffic_pay, failed_traffic_pay)
from controller import export_service_fee
from . import fee as fee_blueprint
from utils.api import token_required, response_wrapper
from utils import err
from third import swiftpass, alipay_official
from db.account import controller as db
from utils.export import gen_filename, redirect_to_file

ITEMS_PER_PAGE = 100

_LOGGER = logging.getLogger("51paypay")


@fee_blueprint.route('/', methods=['GET'])
@response_wrapper
@token_required
def query_service_fee():
    begin_at = request.args.get("begin_at", "") or str(date.today()-timedelta(days=1000))
    end_at = request.args.get("end_at", "") or str(date.today())
    charge_type = request.args.get("charge_type", "")
    status = request.args.get("status", "")
    trans_type = request.args.get("trans_type", "")
    page = request.args.get("page", 0)
    size = request.args.get("size", 10)
    export = request.args.get("export", 0)
    export = int(export)
    page, size = int(page), int(size)
    end_at = str(datetime.strptime(end_at, "%Y-%m-%d") + timedelta(1))

    result = get_service_fee(g.user['id'],
                             begin_at=begin_at,
                             end_at=end_at,
                             charge_type=charge_type or None,
                             status=status or None,
                             trans_type=trans_type or None,
                             page=page,
                             size=size)

    if export:
        cn_headers = [u'交易时间', u'金额', u'类型', u'状态', u'充值方式', u'QQ/银行卡号']
        data = export_service_fee(result['transaction'])
        filename = gen_filename('export_service_fee')
        if data:
            return redirect_to_file(data, cn_headers, filename, index=u'交易时间')

    return result


@fee_blueprint.route('/create_order', methods=['POST'])
@response_wrapper
@token_required
def create_order():
    try:
        data = json.loads(request.data)
        print data
        recharge_type = data.get("recharge_type")
        amount = float(data['amount'] * 100)
    except Exception as e:
        raise err.ParamError(e)

    if recharge_type not in ['QQ', 'qq', 'alipay']:
        raise err.ParamError('recharge_type error')

    if amount < 1:
        raise err.ParamError('充值金额太小')

    result = create_recharge_order(recharge_type, int(amount), g.user['id'])
    return result


@fee_blueprint.route('/qq/pay_callback', methods=['POST'])
def qq_pay_callback():
    data = request.data
    _LOGGER.info('swiftpass callback for traffic: %s' % data)
    data = xmltodict.parse(data)['xml']
    data = dict(data)
    sign = data.pop('sign')
    if not swiftpass.check_traffic_sign(data, sign):
        _LOGGER.info('traffic swiftpass callback verify sign false')
        return 'fail'
    status = data.get('status')
    result_code = data.get('result_code')
    pay_result = data.get('pay_result')
    orderid = data.get('out_trade_no')
    if status == '0' and result_code == '0':
        amount = Decimal(data['total_fee']) / 100
        if pay_result == '0':
            succeed_traffic_pay(orderid, amount, extend=json.dumps(data))
        else:
            failed_traffic_pay(orderid, amount, extend=json.dumps(data))


@fee_blueprint.route('/alipay/pay_callback', methods=['POST'])
def alipay_pay_callback():
    data = request.form.to_dict()
    _LOGGER.info('alipay callback form: %s' % data)
    signature = data.pop('sign')
    if alipay_official.check_data(data, signature):
        orderid = data['out_trade_no']
        amount = Decimal(data['total_amount'])
        succeed_traffic_pay(orderid, amount, extend=json.dumps(data))
        return 'success'
    else:
        failed_traffic_pay(orderid, amount, extend=json.dumps(data))
        return 'fail'


@fee_blueprint.route('/pay_status', methods=['GET'])
@response_wrapper
@token_required
def pay_status():
    """ 查询流量充值定单状态 """
    try:
        order_id = long(request.args.get("order_id"))
    except Exception as e:
        raise err.ParamError("order_id error %s" % e)

    trans = db.get_transaction_by_rechargeid(order_id)
    if not trans:
        raise err.NoOrderID('no order id %s' % order_id)
    return {"status": trans.status}
