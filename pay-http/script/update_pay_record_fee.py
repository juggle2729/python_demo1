# -*- coding: utf-8 -*-

from db.pay_record.model import PayRecord
from db.account.model import Appid
from handler.pay import get_fee


def update_appid_fee(appid, fee):
    appid_detail = Appid.query.filter(Appid.appid == appid).first()
    appid_detail.fee_total += fee
    appid_detail.save()


def get_fee_rate(appid):
    appid_detail = Appid.query.filter(Appid.appid == appid).first()
    return appid_detail.fee_rate or None


def update_fee():
    payrecords = PayRecord.query.all()
    for pr in payrecords:
        if pr.appid and pr.pay_status==3 and pr.pay_type==23 and pr.real_pay==6:
	    FEE_RATE = get_fee_rate(pr.appid)
	    fee = get_fee(pr.amount, FEE_RATE, pr.pay_type)
            pr.fee = fee
            print fee, pr.appid, pr.id, pr.orderid
            # pr.save()
            # update_appid_fee(pr.appid, fee)
        
