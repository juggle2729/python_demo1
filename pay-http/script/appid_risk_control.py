# -*- coding: utf-8 -*-
import logging
import json

from db.pay_record.model import PayRecord, PAY_STATUS
from db.account.model import Appid
from datetime import timedelta
import datetime

_LOGGER = logging.getLogger(__name__)


def _ban_dead_appid():
    appids = Appid.query.filter(Appid.valid == True).all()
    appids = list(set([each.appid for each in appids]))
    for appid in appids:
        last_success_pay = PayRecord.query.filter(PayRecord.appid == appid) \
            .filter(PayRecord.pay_status == PAY_STATUS.PAY_SUCCESS) \
            .order_by(PayRecord.created_at.desc()).first()
        if not last_success_pay or \
                                datetime.datetime.utcnow() - last_success_pay.created_at >= timedelta(hours=72):
            appid_objs = Appid.query.filter(Appid.appid == appid).all()
            for appid_obj in appid_objs:
                appid_obj.valid = False
                extend = json.loads(appid_obj.extend or '{}') or {}
                extend['banned_for'] = '72 hours no success pay'
                appid_obj.extend = json.dumps(extend)
                appid_obj.save()
                _LOGGER.info('ban dead appid [%s]' % appid)
