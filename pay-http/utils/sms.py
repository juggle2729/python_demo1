# coding: utf-8

# -*- coding: utf-8 -*-
import json
import logging

import requests
from future.utils import raise_with_traceback

from . import EnhencedEncoder

URL = 'http://api.mysubmail.com/message/xsend'
APPID = '15662'
APP_KEY = '1b497d24e50ef9aed9f3f496714bcfb1'

_LOGGER = logging.getLogger(__name__)

TEMPLATE_DICT = {
    'auth_code': 'nJIHK',
}


class SMSSender(object):
    """base class for sms platforms"""

    def send_sms(self, phone_nums, template_id, params, use_unicode=True):
        raise Exception('this is an abstract class!')


class SubMailSender(SMSSender):
    def send_sms(self, phone_nums, template_id, params, use_unicode=True):
        post_data = {
            'appid': APPID,
            'project': TEMPLATE_DICT[template_id],
            'vars': json.dumps(params, cls=EnhencedEncoder,
                               ensure_ascii=False),
            'signature': APP_KEY
        }
        for phone_num in phone_nums:
            post_data['to'] = phone_num
            _LOGGER.info("sms send %s", json.dumps(post_data, ensure_ascii=False))
            _LOGGER.info('send to %s', phone_num)
            resp = requests.post(URL, post_data).json()
            _LOGGER.info("sms api response: %s", resp)
            if resp['status'] != 'success':
                raise_with_traceback(RuntimeError(
                    resp.get('msg', 'unknown error')))


INSTANCES = {
    'cn': [SubMailSender()],
}


def send_sms(phone_nums, template_name, params=None, country=None):
    if not country:
        country = 'cn'
    senders = INSTANCES.get(country.lower())
    if not senders:
        raise_with_traceback(RuntimeError(
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
                RuntimeError('fail to send message through all platforms'))


def send_sms_code(phone, code, country=None):
    send_sms([phone], 'auth_code', {'code': code}, country)


if __name__ == '__main__':
    sender = SubMailSender()
    sender.send_sms(['8618502710984'], 'jN9zt3', {'name': 'terran'})
