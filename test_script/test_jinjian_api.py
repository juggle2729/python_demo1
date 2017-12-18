# -*- coding: utf-8 -*-
import requests
import hashlib


def test_jinjian_api():
    url = 'http://localhost:5000/api/v1/jinjian/k'
    # url = 'http://p.51paypay.net/api/v1/jinjian/k'
    appid = '60001'
    appkey = 'a02jalkj0q'
    data = {
        'appid': appid,
        'mchName': u'武汉海羽毛网络科技有限公司',
        'mchShortName': u'海羽毛网络',
        'city': u'武汉市',
        'province': u'湖北省',
        'address': u'武汉市东湖新技术开发区光谷大道3号激光工程设计总部二期研发楼06幢06单元15层5号（Y121)',
        'mobile': '13125059010',
        'bankNo': '308521015549',
        'industryNo': '161215010100351',
        'balanceType': '1',
        'balanceName': u'武汉海羽毛网络科技有限公司',
        'userIdNumber': '410728197310055000',
        'legalIdNumber': '410728197310055000',
        'cardNumber': '127910189610101',
        'contact': u'陈喻君',
        'licenseNum': '91420100MA4KUKQM6K',
        'licenseStartDate': '20170620',
        'licensePeriod': '1',  # 和licenseEndDate 二选一填写
        # 'licenseEndDate': '',
        'licenseScope': u'计算机系统开发、系统集成：网络系统开发；通信设备技术咨询',
        'wxValue': 20,
        'aliValue': 20,
        'paymentType': 'D0',
        'zfbpay': 20,
        'wxpay': 20,
    }
    sign = generate_sign(data, appkey)
    data['signature'] = sign
    files = {
        'legalIDCardA': (file('farenA.png'), 'rb')
    }
    resp = requests.post(url, data=data, files=files)
    print resp.content


def generate_sign(parameter, key):
    s = ''
    for k in sorted(parameter.keys()):
        if parameter[k] != "":
            s += '%s=%s&' % (k, parameter[k])
    s += 'key=%s' % key
    print 's:', s
    m = hashlib.md5()
    m.update(s.encode('utf8'))
    sign = m.hexdigest()
    return sign


if __name__ == "__main__":
    test_jinjian_api()
