# -*- coding: utf-8 -*-
import time
import random
import string
import hashlib
import json
import requests
import copy

from cache.wechat import *

class Sign:
    def __init__(self, appId, appSecret, url):
        self.appId = appId
        self.appSecret = appSecret

        self.ret = {
            'appid': self.appId,
            'jsapi_ticket': self.getJsApiTicket(),
            'nonceStr': self.__create_nonce_str(),
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        sig_dic = copy.deepcopy(self.ret)
        sig_dic.pop('appid')
        string = '&'.join(['%s=%s' % (key.lower(), sig_dic[key]) for key in sorted(sig_dic)])
        sig_dic['signature'] = hashlib.sha1(string).hexdigest()
        sig_dic['appid'] = self.ret['appid']
        sig_dic.pop('jsapi_ticket')
        return sig_dic

    def getJsApiTicket(self):
        jsapi_ticket = get_jsapi_ticket()
        if not jsapi_ticket:
            url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi&access_token=%s"% (self.getAccessToken())
            response = requests.get(url)
            print response.text
            jsapi_ticket = json.loads(response.text)['ticket']
            set_jsapi_ticket(jsapi_ticket)
        return jsapi_ticket

    def getAccessToken(self):
        access_token = get_access_token()
        if not access_token:
            url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (self.appId, self.appSecret)
            response = requests.get(url)
            print response.text
            access_token = json.loads(response.text)['access_token']
            set_access_token(access_token)
        return access_token

