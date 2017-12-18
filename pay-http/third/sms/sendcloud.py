# -*- coding: utf-8 -*-

import requests
from urllib import urlencode

API_KEY = "YGo5XTX9OSN1Ev20"
API_USER = "51paypay_jinjian_notify"

data = {
    'api_user': API_USER,
    'api_key': API_KEY,
    'from': "admin@51paypay.net",
    'fromname': "进件审核通过",
    'subject': "测试",
    'template_invoke_name': "51paypay_jinjian_audit",
    'resp_email_id': True
}


def mailto(to, mch_name, appid, appkey):
    url = 'http://sendcloud.sohu.com/webapi/mail.send_template.json'

    substitution = {
        'to': [to],
        'sub': {
            "%mch_name%": [mch_name],
            "%appid%": [appid],
            "%appkey%": [appkey],
        }
    }

    query = urlencode({'substitution_vars': substitution})
    resp = requests.post(url + "?" + query, data=data)
    print resp.content


if __name__ == "__main__":
    mailto("qiandiao@51paypay.net", "515151", "sadfas", "dsafasdfqwe")
