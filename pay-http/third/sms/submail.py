# -*- coding: utf-8 -*-
import json

import requests
from future.utils import raise_with_traceback

from third.sms import SMSSender
from utils.err import SmsPlatformError
from utils import EnhencedEncoder

URL = 'https://api.submail.cn/message/xsend.json'
APPID = '13844'
APP_KEY = '790c2dcd0671c91ea00d48f2132a85d5'


TEMPLATE_DICT = {
    'auth_code': '8SxtG2',
}


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

            resp = requests.post(URL, post_data).json()
            if resp['status'] != 'success':
                raise_with_traceback(SmsPlatformError(
                    resp.get('msg', 'unknown error')))


if __name__ == '__main__':
    sender = SubMailSender()
    sender.send_sms(['8618502710984'], 'jN9zt3', {'name': 'terran'})
