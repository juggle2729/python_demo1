# -*- coding: utf-8 -*-
import logging
from db.pay_record import controller
from utils.tz import utc_to_local_str

_LOGGER = logging.getLogger('bill')

_DEFAULT_PAGE_SIZE = 100


def convert_bills(bills):
    results = []
    for bill in bills:
        result = {}
        result['access_seq'] = bill.orderid
        result['mchid'] = bill.mchid
        result['appid'] = bill.appid
        result['pay_type'] = bill.pay_type
        result['pay_status'] = bill.pay_status
        result['created_at'] = utc_to_local_str(bill.created_at)
        result['amount'] = str(bill.amount)
        result['description'] = bill.description
        results.append(result)
    return results


def get_pay_record(mchid, pay_type, pay_status, start_date, end_date, order_id, appid, page, size):
    limit = _DEFAULT_PAGE_SIZE if not size or size > _DEFAULT_PAGE_SIZE else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page - 1) * limit
    counts, resp, amount_sum, fee_sum, service_fee, balance = controller.get_pay_record(mchid, pay_type, pay_status,
                                                                                        start_date, end_date, order_id,
                                                                                        appid, limit, offset)
    resp = convert_bills(resp)
    pages = int(counts / float(limit)) + 1
    return resp, counts, pages, amount_sum, fee_sum, service_fee, balance


def get_withdraw_record(accountid, order_code, pay_type, pay_status, start_amount, end_amount, appid,
                        start_date, end_date, withdraw_status, page, size):
    pages, records, count, amount, fee, service_fee, balance = controller.get_withdraw_record(accountid, order_code,
                                                                                              pay_type, pay_status,
                                                                                              start_amount, end_amount,
                                                                                              appid, start_date,
                                                                                              end_date, page, size, withdraw_status=withdraw_status, source=True)
    resp = {"pages": pages, "record": [], "count": '%.2f' % count, "amount": '%.2f' % amount, "fee": '%.2f' % fee,
            "service_fee": '%.2f' % service_fee, "balance": '%.2f' % balance}
    if records:
        for record in records:
            resp['record'].append(
                {
                    "id": str(record.id),
                    "updated_at": utc_to_local_str(record.updated_at),
                    "channel": record.channel,
                    "appid": record.appid,
                    "paystatus": record.status,
                    "amount": '%.2f' % record.amount,
                    "fee": '%.2f' % record.fee,
                    "to_account": record.to_account,
                    "order_code": record.order_code,
                    "extend": record.extend
                }
            )
    return resp
