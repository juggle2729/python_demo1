# coding: utf-8
import json
from datetime import datetime, date, timedelta
import logging

from flask import request, g
from flask.views import MethodView

from utils.api import token_required, response_wrapper
from utils.export import gen_filename, redirect_to_file
from utils.tz import local_to_utc
from admin.daifu import daifu as daifu_blueprint
from admin.daifu import controller
from db.account.model import ADMIN_MCH_ID
from db.pay_record.model import DAIFU_STATUS
from db.pay_record.controller import get_balance_by_accountid
from utils import err

_LOGGER = logging.getLogger("51paypay")

@daifu_blueprint.route('/apply', methods=['POST'])
@response_wrapper
@token_required
def daifu_apply():
    accountid = g.user['id']
    post_data = json.loads(request.data)
    daifu_list = post_data['list']
    total_amount = 0.00
    for data in daifu_list:
        if ['amount', 'bank_name', 'bank_city', 'bank_account_no',
            'bank_account_name', 'account_type', 'card_type'] >= data.keys():
            raise err.ParamError('params not valid')
        if float(data['amount']) <= 2:
            raise err.ResourceInsufficient(u"代付金额必须大于2元")
        total_amount += float(data['amount'])
    appid, account_balance = get_balance_by_accountid(accountid)
    if account_balance and total_amount >= account_balance:
        raise err.ResourceInsufficient("提现金额不足%s" % total_amount)
    controller.create_daifu_records(daifu_list, accountid)
    return {}


@daifu_blueprint.route('/record', methods=['GET', 'POST'])
@response_wrapper
@token_required
def daifu_record():
    accountid = g.user['id']
    if accountid in ADMIN_MCH_ID:
        admin = 1
    else:
        admin = 0

    def get():
        status = request.args.get("status", "")
        bank_account_no = request.args.get("bank_account_no", "")
        bank_account_name = request.args.get("bank_account_name", "")
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 10))
        if status:
            status = int(status)
        result = controller.daifu_record(accountid, status, bank_account_no, bank_account_name, page, size)
        result['admin'] = admin
        return result

    def post():
        if not admin:
            raise err.PermissionError('Not allowed')
        params = request.get_json()
        daifu_ids = params.get('list')
        status = int(params.get('status', 1))
        record = controller.update_daifu_records(daifu_ids, status)
        if status not in (DAIFU_STATUS.PERMITED, DAIFU_STATUS.REFUSED):
            raise err.ParamError('status invalid')
        if record:
            return {
                'result': 'success'
            }
        else:
            raise err.SystemError('record not found')

    if request.method == 'GET':
        return get()
    elif request.method == 'POST':
        return post()


@daifu_blueprint.route('/balance', methods=['GET'])
@response_wrapper
@token_required
def daifu_balance():
    accountid = g.user['id']
    appid, balance = controller.get_balance_by_accountid(accountid)
    return {
        "balance": float(balance)
    }


@daifu_blueprint.route('/ysepay_callback', methods=['POST'])
def alipay_pay_callback():
    data = request.form.to_dict()
    _LOGGER.info('ysepay callback form: %s' % data)
    result = controller.update_daifu_by_ysepay(data)
    return result
