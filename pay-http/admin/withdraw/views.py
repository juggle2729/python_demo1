# coding: utf-8
import json
from datetime import datetime, date, timedelta
from flask import request, g
from utils.api import token_required, response_wrapper
from admin.withdraw import withdraw as withdraw_blueprint
from admin.withdraw import controller
from db.account.model import ADMIN_MCH_ID
from db.pay_record.controller import create_withdraw_record
from db.account.controller import get_appid_detail, get_bank_card
from utils import err


@withdraw_blueprint.route('/withdraw_balance', methods=['GET'])
@response_wrapper
@token_required
def withdraw_balance():
    page = request.args.get('page', 1)
    page = int(page)
    size = request.args.get('size', 10)
    size = int(size)
    accountid = g.user['id']
    return controller.get_withdraw_balance(accountid, page, size)


@withdraw_blueprint.route('/', methods=['GET'])
@response_wrapper
@token_required
def withdraw_appid():
    app_type = request.args.get('app_type')
    valid = request.args.get('status')
    appname = request.args.get('name')
    appid = request.args.get('appid')
    page = request.args.get('page', 1)
    page = int(page)
    size = request.args.get('size', 10)
    size = int(size)
    infos = controller.get_withdraw_info(g.user['id'], appid, app_type, valid, appname, page, size)
    return infos


@withdraw_blueprint.route('/apply', methods=['POST'])
@response_wrapper
@token_required
def withdraw_apply():
    data = json.loads(request.data)
    amount = float(data.get('amount'))
    extend = data.get('extend')
    appid = data.get('id')
    accountid = g.user['id']
    bank_card = get_bank_card(accountid)
    appid_detail = get_appid_detail(appid, 23)
    if not appid_detail:
        raise err.ResourceInsufficient("APPID不存在")
    if appid_detail.get_balance() - amount < -0.0001:
        raise err.ResourceInsufficient("提现金额不足%s" % amount)
    if amount < 2:
        raise err.ResourceInsufficient(u"提现金额必须大于2元")
    if not bank_card:
        raise err.ResourceInsufficient("先绑定银行卡")
    create_withdraw_record(appid, 6, amount, mchid=accountid, to_account=bank_card.card_number,
                           acc_name=bank_card.card_name,
                           extend=extend, paystatus=0, bank_name=bank_card.bank_name, withdraw_type=2, channel='bank')

    return {}


@withdraw_blueprint.route('/record', methods=['GET', 'POST'])
@response_wrapper
@token_required
def withdraw_record():
    if g.user['id'] in ADMIN_MCH_ID:
        admin = 1
    else:
        admin = 0

    def get():
        begin_at = request.args.get("begin_at", "") or str(date.today() - timedelta(days=365))
        end_at = request.args.get("end_at", "") or str(date.today())
        status = request.args.get("status", "")
        appid = request.args.get("appid", "")
        to_acc = request.args.get("to_account", "")
        to_acc_name = request.args.get("to_acc_name", "")
        order_code = request.args.get("order_code", "")
        withdraw_type = int(request.args.get("withdraw_type", 2))
        page = int(request.args.get("page", 0))
        size = int(request.args.get("size", 10))
        end_at = str(datetime.strptime(end_at, "%Y-%m-%d") + timedelta(1))

        pages, infos, apply_amount, apply_count, suc_apply_amount = controller.withdraw_record(g.user['id'], to_acc,
                                                                                               to_acc_name, begin_at,
                                                                                               end_at, appid,
                                                                                               status, order_code,
                                                                                               withdraw_type, page,
                                                                                               size)
        return {
            'records': infos,
            'pages': pages,
            'apply_amount': '%.2f' % apply_amount,
            'apply_count': apply_count,
            'suc_apply_amount': '%.2f' % suc_apply_amount,
            'admin': admin
        }

    def post():
        if not admin:
            raise err.PermissionError('Not allowed')
        params = request.get_json()
        withdraw_id = params.get('withdraw_id')
        status = params.get('status')
        record = controller.update_withdraw(withdraw_id,
                                            status)
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


@withdraw_blueprint.route('/account_management', methods=['GET'])
@response_wrapper
@token_required
def withdraw_account_management():
    """ 结算帐号管理 """
    account_id = g.user['id']
    bank_name = request.args.get('bank_name')
    mch_type = request.args.get('mch_type')
    balance_type = request.args.get('balance_type')
    bank_number = request.args.get('bank_number')
    balance_name = request.args.get('balance_name')
    mch_number = request.args.get('mch_number')  # 商户编号
    mch_name = request.args.get('mch_name')  # 商户名称
    page = request.args.get('page', 1)
    size = request.args.get('size', 10)
    page = int(page)
    size = int(size)
    return controller.get_withdraw_account(account_id, bank_name, balance_type,
                                           mch_type, bank_number, balance_name,
                                           mch_number, mch_name, page, size)
