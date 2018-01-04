# coding: utf-8

import json
import logging

from db.pay_record.model import DAIFU_STATUS
from db.pay_record.controller import create_daifu_record, get_daifu_record, \
        get_balance_by_accountid, update_daifu_record_by_id, get_daifu_sum
from utils import tz
from third.ysepay import ysepay_daifu, ysepay_check_data


_LOGGER = logging.getLogger(__name__)
_DEFAULT_PAGE_SIZE = 100


def create_daifu_records(daifu_list, accountid):
    for daifu_data in daifu_list:
        daifu_data['accountid'] = accountid
        create_daifu_record(daifu_data)
    return True


def update_daifu_records(daifu_ids, status):
    for daifu_id in daifu_ids:
        daifu_record = update_daifu_record_by_id(daifu_id, status)
        if daifu_record and daifu_record.status == DAIFU_STATUS.PERMITED:
            success, extend = ysepay_daifu(daifu_record.as_dict())
            if success:
                status = DAIFU_STATUS.PROCESSING
            else:
                status = DAIFU_STATUS.FAIL
            update_daifu_record_by_id(daifu_id, status, extend)
    return True


def update_daifu_by_ysepay(data):
    daifu_id = data['out_trade_no']
    ysepay_callback_success = ysepay_check_data(data)
    if ysepay_callback_success:
        status = DAIFU_STATUS.SUCCESS
    else:
        status = DAIFU_STATUS.FAIL
    update_daifu_record_by_id(daifu_id, status, json.dumps(data))
    return 'success'


def daifu_record(accountid, status, bank_account_no, bank_account_name, page, size):
    limit = _DEFAULT_PAGE_SIZE if not size or size > _DEFAULT_PAGE_SIZE else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page-1) * limit

    total_pages, items = get_daifu_record(accountid, status, bank_account_no,
                                          bank_account_name, page, size)
    apply_amount, apply_count, suc_amount, fee_sum, submit_sum  = get_daifu_sum(accountid)

    data = []
    for item in items:
        appid, balance = get_balance_by_accountid(accountid)
        resp = {}
        resp['daifu_id'] = str(item.id)
        resp['accountid'] = item.mchid
        resp['daifu_type'] = item.daifu_type
        resp['amount'] = float(item.amount)
        resp['fee'] = float(item.fee)
        resp['status'] = item.status
        resp['appid'] = appid
        resp['balance'] = float(balance)
        resp['bank'] = item.bank
        resp['bank_name'] = item.bank_name
        resp['bank_province'] = item.bank_province
        resp['bank_city'] = item.bank_city
        resp['bank_account_no'] = item.bank_account_no
        resp['bank_account_name'] = item.bank_account_name
        resp['card_type'] = item.card_type
        resp['created_at'] = tz.utc_to_local_str(item.created_at)
        data.append(resp)
    return {
        'records': data,
        'pages': total_pages,
        'apply_amount': '%.2f' % apply_amount,
        'apply_count': apply_count,
        'suc_apply_amount': '%.2f' % suc_amount,
        'fee_sum': '%.2f' % fee_sum,
        'submit_sum': '%.2f' % submit_sum,
    }
