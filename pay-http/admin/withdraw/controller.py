# coding: utf-8

import logging
from db.account.controller import query_app_manage, get_mch_name
from cache.redis_cache import get_appid_balance
from db.pay_record.controller import get_withdraw_data, get_dealing_balance
from db.account.controller import query_withdraw_balance, get_appmanage_by_appid, get_bank_card
from db.pay_record.model import WITHDRAW_STATUS
from db.pay_record.controller import get_withdraw_data, get_withdraw_record, update_withdraw_record_by_id, withdraw_dealing_count, get_withdraw_sum
from db.account.model import MCH_TYPE, BALANCE_TYPE
from utils import tz


_LOGGER = logging.getLogger(__name__)
_DEFAULT_PAGE_SIZE = 100


def get_withdraw_info(account_id, appid, app_type, valid, name, page, size):

    limit = _DEFAULT_PAGE_SIZE if not size or size > _DEFAULT_PAGE_SIZE else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page - 1) * limit

    apps, counts = query_app_manage(account_id, appid, app_type, valid, name, limit, offset)
    pages = int(counts / float(limit)) + 1
    resp = []
    for app in apps:
        data = {
            'mch_name': app.mch_name,
            'app_name': app.appname,
            'appid': app.appid,
            'bank_name': app.card_name,
            'balance': get_appid_balance(app.appid),
            'card_number': app.card_number,
        }
        resp.append(data)
    succeed, succeed_fee, dealing, dealing_fee = get_withdraw_data(account_id)

    resp_wrap = {'pages': pages,
                 'list': resp,
                 'succeed': succeed,
                 'succeed_fee': succeed_fee,
                 'dealing': dealing,
                 'dealing_fee': dealing_fee}
    return resp_wrap


def get_withdraw_account(account_id, bank_name, balance_type,
                         mch_type, bank_number, balance_name,
                         mch_number, mch_name, page, size):
    limit = _DEFAULT_PAGE_SIZE if not size or size > _DEFAULT_PAGE_SIZE else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page - 1) * limit
    apps, counts = query_app_manage(account_id,
                                    bank_name=bank_name,
                                    balance_type=balance_type,
                                    industry_no=mch_type,
                                    card_number=bank_number,
                                    balance_name=balance_name,
                                    mch_number=mch_number,
                                    mch_name=mch_name,
                                    offset=offset,
                                    limit=limit)

    resp = []
    for app in apps:
        resp.append({
            "mch_number": app.id,
            "mch_name": app.mch_name,
            "mch_type": MCH_TYPE.get_label(app.industry_no),
            "balance_type": BALANCE_TYPE.get_label(app.balance_type),
            "balance_name": app.balance_name,
            "card_number": app.card_number,
            "bank_no": app.bank_no,
            "bank_name": app.bank_name,
            "updated_at": tz.utc_to_local(app.updated_at).strftime("%Y-%m-%d %H:%M:%S")
        })
    pages = int(counts / float(limit)) + 1
    return {"pages": pages, "list": resp}


def get_withdraw_balance(accountid, page, size):
    pages, withdraw_apps, withdraw_total, fee_total, recharge_total = query_withdraw_balance(accountid, page, size)
    _, _, _, withdraw_fee = get_withdraw_sum(accountid, None, 'bank', None, None, None, None, WITHDRAW_STATUS.SUCCESS, None, None)
    resp = []
    if withdraw_apps:
        for app in withdraw_apps:
            appmanage = get_appmanage_by_appid(app.appid)
            bank_card = get_bank_card(accountid)
            amount = round(float(app.recharge_total - app.withdraw_total - app.fee_total), 2)
            resp.append({"amount": amount if amount >= 0 else 0,
                         "mch_name": app.mch_name,
                         "appid": app.appid,
                         "dealing": '%.2f' % get_dealing_balance(app.appid),
                         "bank_name": bank_card.bank_name if bank_card else '',
                         "card_number": bank_card.card_number if bank_card else '',
                         "id": app.appid})
    dealing_total = sum([float(item['dealing']) or 0 for item in resp])
    return {'pages': pages, 'resp': resp, 'withdraw_total': '%.2f' % (float(withdraw_total) - float(dealing_total)), 'dealing_total': dealing_total,
            'fee_total': '%.2f' % (withdraw_fee), 'recharge_total': '%.2f' % (float(recharge_total) - float(withdraw_total) - float(fee_total)) }


def withdraw_record(account_id, to_acc, to_acc_name, begin_at, end_at, appid, status, order_code, withdraw_type, page, size):
    limit = _DEFAULT_PAGE_SIZE if not size or size > _DEFAULT_PAGE_SIZE else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page-1) * limit
    total_pages, items = get_withdraw_record(account_id, order_code, 'bank', '',
                                             '', '', appid, begin_at, end_at, page, size,
                                             withdraw_type, status, to_account = to_acc, acc_name=to_acc_name)
    apply_amount, apply_count, suc_apply_amount, _ = get_withdraw_sum(account_id, order_code, 'bank', appid, begin_at, end_at, withdraw_type, status, to_acc, to_acc_name)
    data = []
    for item in items:
        resp = {}
        resp['withdraw_id'] = str(item.id)
        resp['appid'] = item.appid
        resp['withdraw_type'] = item.withdraw_type
        resp['amount'] = float(item.amount)
        resp['fee'] = float(item.fee)
        resp['status'] = item.status
        resp['mch_name'] = get_mch_name(item.appid)
        resp['mchid'] = item.mchid
        resp['bank_name'] = item.bank_name
        resp['bank_no'] = item.to_account
        resp['acc_name'] = item.acc_name
        resp['updated_at'] = tz.utc_to_local_str(item.updated_at)
        data.append(resp)

    return total_pages, data, apply_amount, apply_count, suc_apply_amount


def update_withdraw(withdraw_id, status):
    return update_withdraw_record_by_id(withdraw_id, status)
