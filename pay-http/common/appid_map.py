# -*- coding: utf-8 -*-

import json

APPID_MAP = {
    '10000002': {
        'app_key': '880357ccd28db91f6f0f88d54889c34c',
        'name': u'深圳传盛网络',
        'support_pay': [1],
        'custId': '170824215231283',
        'sceneInfo': json.dumps({
            'type': 'Wap',
            'wap_name': u'深圳传盛',
            'wap_url': 'http://www.lovelu365.com/'
        }, ensure_ascii=False),
        'notifyUrl': ''
    },
    '20000001': {
        'app_key': '2a140c86105138d87dd66bc712771d10',
        'name': u'上海桔梗',
        'support_pay': [1],
        'custId': '170824215137191',
        'sceneInfo': json.dumps({
            'type': 'Wap',
            'wap_name': u'上海桔梗',
            'wap_url': 'http://game192.com/'
        }, ensure_ascii=False),
        'notifyUrl': ''
    },
    '100000': {
        'app_key': 'HYM17002P',
        'name': u'海羽毛',
        'support_pay': [2],
        'custId': '170822185829458',
    }
}
