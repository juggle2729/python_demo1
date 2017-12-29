# -*- coding: utf-8 -*-
import logging
import json

from db.pay_record.model import PayRecord, PAY_STATUS
from db.account.model import Appid
from datetime import timedelta
import datetime

_LOGGER = logging.getLogger(__name__)


def ban_dead_appid_():
    hours = 72
    now = datetime.datetime.utcnow()
    appid_objs = Appid.query.filter(Appid.valid == True).all()
    for appid_obj in appid_objs:
        if now - appid_obj.created_at < timedelta(hours=hours):
            continue
        appid = appid_obj.appid
        last_success_pay = PayRecord.query.filter(PayRecord.appid == appid) \
            .filter(PayRecord.pay_status == PAY_STATUS.PAY_SUCCESS) \
            .order_by(PayRecord.created_at.desc()).first()
        if not last_success_pay or \
                                now - last_success_pay.created_at >= timedelta(hours=hours):
            extend = json.loads(appid_obj.extend or '{}') or {}
            extend['banned_for'] = '72 hours no success pay'
            appid_obj.extend = json.dumps(extend)
            appid_obj.valid = False
            appid_obj.save()
            _LOGGER.info('ban dead appid [%s]' % appid)
