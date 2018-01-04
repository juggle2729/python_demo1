# -*- coding: utf-8 -*-
from db import orm, BaseModel, TimeColumnMixin
from utils.types import Enum

PAY_STATUS = Enum({
    'READY': (0L, u'预设状态'),
    'UP_SUCCESS': (1L, u'调用上游接口成功'),
    'UP_FAIL': (2L, u'调用上游接口失败'),
    'PAY_SUCCESS': (3L, u'上游通知支付成功'),
    'PAY_FAIL': (4L, u'上游通知支付失败')
})

NOTIFY_STATUS = Enum({
    'READY': (0L, u"预设状态"),
    'FAIL': (1L, u"回调失败"),
    'SUCCESS': (2L, u"回调成功")
})

PAY_TYPE = Enum({
    'WECHAT_H5': (1L, u'微信H5支付'),
    'WECHAT_QR': (2L, u'微信扫码付'),
    'WECHAT_SDK': (3L, u'微信SDK付'),
    'QQ_QR': (11L, u'QQ钱包支付'),
    'ALIPAY_QR': (21L, u'支付宝扫码'),
    'ALIPAY_H5': (22L, u'支付宝H5'),  # 支付宝扫码付包装为支付宝H5支付
    'ALIPAY_REAL_H5': (23L, u'支付宝官方H5'),  # <真>支付宝H5支付
    'BAIDU_QR': (31L, u'百度钱包支付'),
    'JD_QR': (41L, u'京东钱包支付')
})

_acquire_type_map = {
    PAY_TYPE.ALIPAY_H5: 'alipay',
    PAY_TYPE.ALIPAY_REAL_H5: 'alipay',
    PAY_TYPE.ALIPAY_QR: 'alipay',
    PAY_TYPE.WECHAT_QR: 'wechat',
    PAY_TYPE.QQ_QR: 'qq',
    PAY_TYPE.BAIDU_QR: 'baidu',
    PAY_TYPE.JD_QR: 'jd'
}

# 给下游商户看的订单状态
MCH_PAY_STATUS = Enum({
    'READY': (0L, u'预设状态'),
    'FAIL': (1L, u'支付失败'),
    'SUCCESS': (2L, u'支付成功')
})

WITHDRAW_STATUS = Enum({
    'READY': (1L, u'初始状态'),
    'SUCCESS': (2L, u'打款成功'),
    'FAIL': (3L, u'打款失败'),
    'UNKNOWN': (4L, u'状态未明')
})

WITHDRAW_TYPE = Enum({
    'API': (1L, u"支付宝API转账"),
    'HAND': (2L, u"人工转账")
})

def convert_accquire_type(pay_type):
    return _acquire_type_map[pay_type]


# TODO: 和前段同步修改订单状态
def convert_pay_status(pay_status):
    """
    将pay_record的pay_status转换为给商户看的订单状态
    """
    _status = {
        PAY_STATUS.READY: MCH_PAY_STATUS.READY,
        PAY_STATUS.UP_SUCCESS: MCH_PAY_STATUS.READY,
        PAY_STATUS.UP_FAIL: MCH_PAY_STATUS.FAIL,
        PAY_STATUS.PAY_FAIL: MCH_PAY_STATUS.FAIL,
        PAY_STATUS.PAY_SUCCESS: MCH_PAY_STATUS.SUCCESS
    }
    return _status[pay_status]


def convert_mch_pay_status(mch_pay_status):
    """
    将商户看到的支付状态转换为pay_record的pay_status
    """
    if not mch_pay_status:
        return None
    mch_pay_status = int(mch_pay_status)
    _status = {
        MCH_PAY_STATUS.READY: PAY_STATUS.READY,
        MCH_PAY_STATUS.FAIL: PAY_STATUS.PAY_FAIL,
        MCH_PAY_STATUS.SUCCESS: PAY_STATUS.PAY_SUCCESS
    }
    return _status[mch_pay_status]


class PayRecord(BaseModel, TimeColumnMixin):
    __tablename__ = 'pay_record'
    id = orm.Column(orm.BigInteger, primary_key=True)
    orderid = orm.Column(orm.String(60))  # 订单号(商户传来的订单号)
    mchid = orm.Column(orm.Integer, default=None, nullable=True)  # 商户号
    appid = orm.Column(orm.String(30))  # 给商户分配的appid
    originid = orm.Column(orm.String(30))  # 上游订单号
    pay_type = orm.Column(orm.Integer)
    pay_status = orm.Column(orm.Integer)
    notify_status = orm.Column(orm.Integer, default=NOTIFY_STATUS.READY)  # 回调下游商户的状态
    amount = orm.Column(orm.Float)
    description = orm.Column(orm.String(100))
    notify_url = orm.Column(orm.String(200), default=None, nullable=True)
    fee = orm.Column(orm.Float, default=0)  # 手续费, Decimal(10, 5)
    extend = orm.Column(orm.TEXT)
    real_pay = orm.Column(orm.Integer)
    real_custid = orm.Column(orm.String(30))  # 轮询时标记真实custid
    pay_time = orm.Column(orm.DateTime, default=None)  # 支付时间-收到上游回调的时间
    service_fee = orm.Column(orm.Float)


class NotifyRecord(BaseModel, TimeColumnMixin):
    __tablename__ = 'notify_record'
    payid = orm.Column(orm.BigInteger, primary_key=True)
    pay_status = orm.Column(orm.Integer)
    try_times = orm.Column(orm.Integer)


class WithdrawRecord(BaseModel, TimeColumnMixin):
    __tablename__ = 'withdraw_record'
    id = orm.Column(orm.BigInteger, primary_key=True)
    mchid = orm.Column(orm.Integer, default=None, nullable=True)  # 商户号
    appid = orm.Column(orm.String(30))
    withdraw_type = orm.Column(orm.Integer)
    order_code = orm.Column(orm.String(30))
    amount = orm.Column(orm.Float)  # 提现金额
    fee = orm.Column(orm.Float)  # 手续费
    status = orm.Column(orm.Integer)
    real_pay = orm.Column(orm.Integer)
    channel = orm.Column(orm.String(30))
    to_account = orm.Column(orm.String(30))
    bank_name = orm.Column(orm.String(30))
    acc_name = orm.Column(orm.String(30))
    trans_time = orm.Column(orm.String(30))  # 杉德代付商户上送时间
    extend = orm.Column(orm.TEXT)


