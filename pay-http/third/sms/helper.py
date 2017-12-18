# -*- coding: utf-8 -*-
import logging

from future.utils import raise_with_traceback

from third.sms.submail import SubMailSender
from utils.err import SmsPlatformError, ServerError
from base import app

_LOGGER = logging.getLogger(__name__)

INSTANCES = {
    'cn': [SubMailSender()],
}


def send_sms(phone_nums, template_name, params=None, country=None):
    if not country:
        country = 'cn'
    senders = INSTANCES.get(country.lower())
    if not senders:
        raise_with_traceback(ServerError(
            "fail to find sms platform in %s" % country))

    for index, sender in enumerate(senders):
        try:
            params = params or {}
            sender.send_sms(phone_nums, template_name, params)
            return
        except Exception as e:
            _LOGGER.exception(e)

        if index == len(senders) - 1:
            raise_with_traceback(
                SmsPlatformError('fail to send message through all platforms'))
