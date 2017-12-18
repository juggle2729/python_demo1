# -*- coding: utf-8 -*-

# 每30分钟检查数据库里面各商户最近30分钟是否有交易，没有的话以短信形式发给财务
# mailto: chengwm@51paypay.net


import json
import time
import torndb
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

HOST = "10.170.153.182"
USER = "pay"
DBNAME = "51paypay"
PASSWORD = "payme_pas"


my_sender = 'qiandiao@51paypay.net'
# my_pass = 'XXXXXXXXXXX'
my_user = 'chengwm@51paypay.net'


URL = 'https://api.submail.cn/message/xsend.json'
APPID = '15662'
APP_KEY = '1b497d24e50ef9aed9f3f496714bcfb1'
AUTH_CODE = 'Ma5eW3'
REPORT_TO = '18071505358'

db = torndb.Connection(HOST, DBNAME, USER, PASSWORD)

mch = db.query("select mchid, account_appid.mch_name from pay_record join account_appid "
               "where pay_record.mchid is not  NULL and account_appid.mch_name is not NULL "
               "and mchid in (14, 18, 22, 24, 25, 26) "
               "and mchid=account_appid.accountid group by mchid")

pay_state = []

print (str(datetime.now() - timedelta(minutes=30)))
for item in mch:
    ret = db.get("select count(*) as `cnt` from pay_record where mchid = %s and created_at > %s",
                 item["mchid"],
                 datetime.now() - timedelta(minutes=30))
    if not ret['cnt']:
        pay_state.append(item['mch_name'])

# print pay_state

text = u'\r\n'
for mch in pay_state:
    text += mch + u'\r\n'
# print text


def mail():
    ret = True
    try:
        msg = MIMEText(text, 'plain', 'utf-8')
        msg['From'] = formataddr([u"qiandiao@51paypay.net", my_sender])
        msg['To'] = formataddr([u"Hi", my_user])
        msg['Subject'] = u"近期30分钟未发起支付请求的商户"

        server = smtplib.SMTP_SSL("smtp.mxhichina.com", 465)
        server.login(my_sender, my_pass)
        time.sleep(1)
        server.sendmail(my_sender, [my_user, ], msg.as_string())
        server.quit()
    except Exception as e:
        print e
        ret = False
    return ret


# ret = mail()
# if ret:
#     print("邮件发送成功")
# else:
#     print("邮件发送失败")

POST_DATA = {
    'appid': APPID,
    'project': AUTH_CODE,
    'vars': json.dumps({'mchs': text}),
    'signature': APP_KEY,
    'to': REPORT_TO
}

# print POST_DATA

resp = requests.post(URL, POST_DATA, verify=False).json()
if resp['status'] != 'success':
    print resp.get('msg', 'unknown error')
