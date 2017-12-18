# coding: utf-8
import json
from datetime import datetime

from db import orm
from db import BaseModel
from utils.types import Enum

TRADE_TYPE = Enum({
    'SPEND': (1L, u'消费'),
    'WITHDRAW': (2L, u'消费撤销'),
    'REFUND': (3L, u'退货')
})


CURRENCY = Enum({
    'RMB': (156L, u'人民币')
})

TRADE_STATUS = Enum({
    'success': (2L, u'交易成功')
})


class Bill(BaseModel):
    __tablename__ = 'bills'
    id = orm.Column(orm.Integer, primary_key=True)
    access_number = orm.Column(orm.String(32))
    pay_type = orm.Column(orm.String(8))
    trade_type = orm.Column(orm.String(1))
    access_seq = orm.Column(orm.String(32))
    access_submit_date = orm.Column(orm.DateTime) ## yyyyMMdd
    trade_amount = orm.Column(orm.String(32))
    poundage = orm.Column(orm.String(32))
    currency_type = orm.Column(orm.String(8))
    channel_number = orm.Column(orm.String(32))
    card_code = orm.Column(orm.String(32))
    account = orm.Column(orm.String(32))
    protocol = orm.Column(orm.String(32))
    platform_seq  = orm.Column(orm.String(32))
    platform_trade_date = orm.Column(orm.DateTime)
    trade_status = orm.Column(orm.String(1))
    bank_merchant_number = orm.Column(orm.String(32))
    channel_flag = orm.Column(orm.String(32))
    exchange_rate = orm.Column(orm.String(8))
    settling_amount = orm.Column(orm.String(32))
    settling_currency_type = orm.Column(orm.String(8))

    account_id = orm.Column(orm.Integer, orm.ForeignKey('accounts.id'))

    def fill(self, array):
        self.access_number = array[0]
        self.pay_type = array[1]
        self.trade_type = array[2]
        self.access_seq = array[3]
        self.access_submit_date = datetime.strptime(
            array[14]+array[15], '%Y%m%d%H%M%S')
        self.trade_amount = array[6]
        self.poundage = array[7]
        self.currency_type = array[8]
        self.channel_number = array[9]
        self.card_code = array[10]
        self.account = array[11]
        self.protocol = array[12]
        self.platform_seq = array[13]
        self.platform_trade_date = datetime.strptime(
            array[14]+array[15], '%Y%m%d%H%M%S')
        self.trade_status = array[16]
        self.bank_merchant_number = array[17]
        self.channel_flag = array[18]
        self.exchange_rate = array[19]
        self.settling_amount = array[20]
        self.settling_currency_type = array[21]

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data['access_submit_date'] = datetime.strftime(
                data['access_submit_date'], '%Y-%m-%d %H:%M:%S')
        data['platform_trade_date'] = datetime.strftime(
                data['platform_trade_date'], '%Y-%m-%d %H:%M:%S')
        return data

    def __repr__(self):
        return "Bill:\n%s" %json.dumps(self.to_dict(), indent=2,
                ensure_ascii=False)
