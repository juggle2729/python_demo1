# -*- coding: utf-8 -*-
import logging
from db.account import controller
from db.account.model import TRANS_TYPE, RECHARGE_STATUS
from utils.id_generator import generate_long_id
from third.swiftpass import qq_traffic_pay
from third.alipay_official import alipay_traffic_pay
from utils import tz

_LOGGER = logging.getLogger('51paypay')

_DEFAULT_PAGE_SIZE = 100


def select_trans(trans_list):
    trans = []
    for tran in trans_list:
        if tran.trans_type == TRANS_TYPE.COST:
            trans.append({"trans_time": tz.utc_to_local(tran.updated_at).strftime("%Y-%m-%d %H:00:00"),
                          "amount": str(float(tran.amount)),
                          "trans_type": tran.trans_type})
        else:
            if tran.charge_type == 0:
                bank_number = '***********'
                bank_name = 'QQ钱包'
            elif tran.charge_type == 2:
                bank_number = '***********'
                bank_name = '支付宝充值'
            else:
                bank_number = '***********'
                bank_name = '网银充值'

            trans.append({"trans_time": tz.utc_to_local(tran.updated_at).strftime("%Y-%m-%d %H:%M:%S"),
                          "amount": "+" + str(float(tran.amount)/100),
                          "trans_type": tran.trans_type,
                          "bank_number": bank_number,
                          "bank_name": bank_name,
                          "status": tran.status})

    return trans


def export_service_fee(trans):
    alist = []
    for tran in trans:
        alist.append([tran.get('trans_time', None),
                      tran.get('amount', None),
                      TRANS_TYPE.get_label(tran.get('trans_type', None)),
                      RECHARGE_STATUS.get_label(tran.get('status', None)),
                      tran.get('bank_name', None),
                      tran.get('bank_number', None)])

    return alist


def get_service_fee(accountid, begin_at, end_at, charge_type,
                    status, trans_type, page, size):

    limit = _DEFAULT_PAGE_SIZE if not size or size > _DEFAULT_PAGE_SIZE else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page-1) * limit
    if charge_type is not None:
        charge_type = 0 if charge_type == 'qq' else 1

    query_data = controller.get_transaction_record(accountid, begin_at, end_at, charge_type,
                                                   status, trans_type, limit, offset)

    query_data['transaction'] = select_trans(query_data['transaction'])
    query_data['consumed'] = round((query_data['consumed'][0] or 0), 2)
    query_data['total_recharge'] = round((query_data['total_recharge'][0] or 0), 2)
    query_data['remain'] = float(controller.get_user(accountid).balance)
    query_data['total_recharge'] = '%.2f' % (float(query_data['total_recharge']) / 100)
    query_data['average_consume_per_day'] = round((query_data['average_consume_per_day'] or 0), 2)

    return query_data


def _convert_recharge_type(recharge_type):
    recharge_map = {
        "qq": 0L,
        "wy": 1L,
        "alipay": 2L,
    }
    return recharge_map[recharge_type.lower()]


def create_recharge_order(recharge_type, amount, accountid):
    recharge_type = _convert_recharge_type(recharge_type)
    orderid = generate_long_id("pay")
    if recharge_type == 0:
        pay_url = qq_traffic_pay(amount, orderid)
    else:
        pay_url = alipay_traffic_pay(float(amount) / 100, orderid)
    rech = controller.create_recharge(orderid, accountid, pay_url, amount, recharge_type)
    return {
        "order_id": str(rech.id),
        "pay_url": rech.pay_url
    }


def succeed_traffic_pay(orderid, amount, extend=None):
    controller.update_recharge(orderid, amount, RECHARGE_STATUS.SUCCESS, extend)


def failed_traffic_pay(orderid, amount, extend=None):
    controller.update_recharge(orderid, amount, RECHARGE_STATUS.FAILED, extend)
