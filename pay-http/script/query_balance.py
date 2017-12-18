# coding: utf-8

import logging
from db.account.model import Appid, REAL_PAY
from third import keda, sand
from cache.redis_cache import set_appid_balance


_LOGGER = logging.getLogger("51paypay")


def schedule_query_balance():
    appids_detail = Appid.query.all()
    for appid_detail in appids_detail:
        custid = appid_detail.custid
        appid = appid_detail.appid
        real_pay = appid_detail.real_pay
        if real_pay == REAL_PAY.KEDA and appid_detail.paymenttype == 'D0':  # 客达
            try:
                ret = keda.query_d0_balance(custid)
                set_appid_balance(appid, real_pay, float(ret['data']['aliBalance']) + float(ret['data']['wxBalance']))
            except:
                _LOGGER.info("appid[%s] query keda d0 balance error" % appid)

        if real_pay == REAL_PAY.SAND:  # 杉德
            try:
                ret = sand.query_balance(custid)
                balance = ret.get('balance', '')
                set_appid_balance(appid, real_pay, balance[0] + str(int(balance[1:].lstrip('0')) / 100.0))
            except:
                _LOGGER.info("appid[%s] query sand balance error" % appid)
