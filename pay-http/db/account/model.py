# coding: utf-8

import json
from flask_login import UserMixin
from db import BaseModel
from db import orm
from db import bcrypt
from db import TimeColumnMixin
from utils.types import Enum
from base import login_manager
from db.bill.model import Bill


ADMIN_MCH_ID = [116, 120]  # 财务,管理员,新增加同事, 马云

IP_DICT = {
    116: ('113.57.172.122',),
    111:('134.159.205.34', '134.159.148.26','134.159.148.25', '203.177.197.72',),
    110:('134.159.205.34', '203.190.69.126','134.159.148.26', '134.159.148.25',),
}

# 上游支付渠道
REAL_PAY = Enum({
    'GUANGDA': (1L, u'光大银行'),
    'KEDA': (2L, u'客达文化'),
    'SAND': (3L, u'杉德支付'),
    'WANHONG': (4L, u'万洪支付'),
    'SWIFTPASS': (5L, u'威富通'),
    'ALIPAY': (6L, u'支付宝官方支付'),
})

APP_TYPE = Enum({
    'H5': (1L, u'h5'),
    'WEB': (2L, u'web'),
    'APP': (3L, u'app')
})

VALID_STATUS = Enum({   # ---> JINJIAN_STATUS
    'AUDIT': (0L, u'商户提交此单'),
    'REFUSED': (1L, u'我们拒绝此单'),
    'FAILED': (2L, u'银行拒单'),
    'SUCCESS': (3L, u'银行通过'),  # 客达光大之类的第三方通过, 不一定能真正支付
    'VALID': (4L, u'APPID生效'),  # 已经能够正常支付
})

TRANS_TYPE = Enum({
    'RECHARGE': (0L, u'充值'),
    'COST': (1L, u'消耗')
})

RECHARGE_STATUS = Enum({
    'READY': (0L, u"预设状态"),
    'SUCCESS': (1L, u'充值成功'),
    'FAIL': (2L, u'充值失败'),
})

# 服务费充值
RECHARGE_TYPE = Enum({
    'QQ': (0L, u"QQ钱包充值"),
    'GONGSHANG': (1L, u"中国工商银行"),
    'ZHAOSHANG': (2L, u"中国招商银行"),
    'JIANGSHE': (3L, u"中国建设银行"),
    'MINSHENG': (4L, u"中国民生银行"),
    'PINGAN': (5L, u"中国平安银行"),
    'JIAOTONG': (6L, u"中国交通银行"),
    'YOUZHENG': (7L, u"中国邮政"),
    'XINGYE': (8L, u"兴业银行"),
    'BANKOFCHINA': (9L, u"中国银行"),
})

CHARGE_TYPE = Enum({
    'QQ': (0L, u"QQ"),
    'WY': (1L, u"网银"),
})


APPID_STATUS = Enum({
    "UNREADY": (0L, u"待审核"),
    "VALID": (1L, u"已生效"),
    "UNVALID": (2L, u"被拒绝"),
    "DELETE": (3L, u"被删除")
})


MCH_TYPE = Enum({
    "ENTERPRISE": (1L, u"企业"),
    "PRIVATE": (2L, u"个体工商户"),
    "PUBLIC": (3L, u"事业单位")
})


BALANCE_TYPE = Enum({
    "PUBLIC": (1L, u"对公"),
    "PRIVATE": (2L, u"对私"),
})


class AccountRelation(BaseModel):
    __tablename__ = 'acc_relation'
    id = orm.Column(orm.Integer, primary_key=True)
    accountid = orm.Column(orm.Integer)
    childid = orm.Column(orm.Integer)
    extend = orm.Column(orm.TEXT)


class JinjianAppid(BaseModel):
    __tablename__ = 'jinjian_appid'
    accountid = orm.Column(orm.Integer)
    appid = orm.Column(orm.String(30), primary_key=True)  # 主键自增
    appkey = orm.Column(orm.String(30))


IMG_PATH = "/home/ubuntu/flask-env/data/images/"


class JinjianRecord(BaseModel, TimeColumnMixin):
    __tablename__ = 'jinjian_record'
    id = orm.Column(orm.BigInteger, primary_key=True)
    accountid = orm.Column(orm.Integer)
    real_pay = orm.Column(orm.Integer)
    jinjian_data = orm.Column(orm.TEXT)
    resp_data = orm.Column(orm.TEXT)
    appmanageid = orm.Column(orm.Integer)
    status = orm.Column(orm.Integer, default=0)
    mch_name = orm.Column(orm.String(30))
    custid = orm.Column(orm.String(30))
    banklinknumber = orm.Column(orm.String(30))  # 客达用
    paymenttype = orm.Column(orm.String(30))  # D0, D1, T1

    @property
    def jinjian_info(self):
        return json.loads(self.jinjian_data)

    @jinjian_info.setter
    def jinjian_info(self, info_dct):
        self.jinjian_data = json.dumps(info_dct)


class Appid(BaseModel, TimeColumnMixin):
    __tablename__ = "account_appid"
    id = orm.Column(orm.Integer, primary_key=True)
    accountid = orm.Column(orm.Integer)
    appid = orm.Column(orm.String(30))
    appkey = orm.Column(orm.String(30))
    custid = orm.Column(orm.String(30))
    pay_type = orm.Column(orm.Integer)
    real_pay = orm.Column(orm.Integer)
    valid = orm.Column(orm.Boolean)
    sceneInfo = orm.Column(orm.TEXT)  # H5支付需要
    extend = orm.Column(orm.TEXT)
    fee_rate = orm.Column(orm.Integer)  # 手续费,万分率,60表示 千分之6
    banklinknumber = orm.Column(orm.String(30))  # 浦发或招行的银行卡，客达用
    paymenttype = orm.Column(orm.String(30))  # 客达用, D0或D1
    mch_name = orm.Column(orm.String(30))
    polling = orm.Column(orm.Boolean, default=False)  # 是否为轮询appid
    service_rate = orm.Column(orm.Integer)  # 服务费,万分率
    recharge_total = orm.Column(orm.Float, default=0)  # 充值总额 Decimal(20, 5)
    withdraw_total = orm.Column(orm.Float, default=0)  # 提现总额 Decimal(20, 5)
    fee_total = orm.Column(orm.Float, default=0)   # 实时更新每笔充值的手续费
    daifu_total = orm.Column(orm.Float, default=0)  # 代付总额 Decimal(20, 5)
    service_fee_total = orm.Column(orm.Float, default=0)  # 服务费总额 Decmal(20, 5)


class PollingCustID(BaseModel):
    """
    用于扫码付轮询
    """
    __tablename__ = 'polling_custid'
    id = orm.Column(orm.Integer, primary_key=True)
    appid = orm.Column(orm.Integer)
    custid = orm.Column(orm.String(30))
    pay_type = orm.Column(orm.Integer)
    real_pay = orm.Column(orm.Integer)
    valid = orm.Column(orm.Integer)
    banklinknumber = orm.Column(orm.String(30))
    paymenttype = orm.Column(orm.String(30))
    mch_name = orm.Column(orm.String(30))
    father_mch_name = orm.Column(orm.String(30))
    service_rate = orm.Column(orm.Integer)


class AppidChannel(BaseModel):
    __tablename__ = 'appid_channel'
    id = orm.Column(orm.Integer, primary_key=True)
    appid = orm.Column(orm.String(30))
    real_pay = orm.Column(orm.Integer)


class AppManage(BaseModel, TimeColumnMixin):
    __tablename__ = "appid_manage"
    id = orm.Column(orm.Integer, primary_key=True)
    accountid = orm.Column(orm.Integer)
    appid = orm.Column(orm.String(30))
    appname = orm.Column(orm.String(60))
    app_type = orm.Column(orm.Integer)
    pay_type = orm.Column(orm.String(30))
    valid = orm.Column(orm.SMALLINT)
    paymenttype = orm.Column(orm.String(30))
    mch_name = orm.Column(orm.String(30))
    mch_short_name = orm.Column(orm.String(30))
    mch_number = orm.Column(orm.BigInteger)   # 商户编号
    balance_type = orm.Column(orm.Integer)   # 结算方式，1-对公，2-对私
    balance_name = orm.Column(orm.String(30))  # 结算户名
    userid_card = orm.Column(orm.BigInteger)  # 提现人身份证
    bank_city = orm.Column(orm.String(30))  # 开户城市
    bank_name = orm.Column(orm.String(30))  # 银行名
    card_number = orm.Column(orm.BigInteger)  # 结算银行卡号码
    card_name = orm.Column(orm.String(30))  # 支付联行号银行名
    bank_no = orm.Column(orm.BigInteger)  # 支行联行号
    industry_no = orm.Column(orm.BigInteger) # 行业编号
    extend = orm.Column(orm.TEXT)

class BankCardInfo(BaseModel, TimeColumnMixin):
    __tablename__ = "bankcard_info"
    id = orm.Column(orm.Integer, primary_key=True)
    accountid = orm.Column(orm.Integer)
    bank_name = orm.Column(orm.String(128))  # 银行名
    subbank_name = orm.Column(orm.String(128))  # 分行名
    card_name = orm.Column(orm.String(32))  # 开户人
    card_number = orm.Column(orm.String(32))  # 银行卡号
    card_type = orm.Column(orm.SMALLINT)
    is_deleted = orm.Column(orm.SMALLINT)
    extend = orm.Column(orm.TEXT)


class Transaction(BaseModel, TimeColumnMixin):
    __tablename__ = "transaction"
    id = orm.Column(orm.Integer, primary_key=True)
    accountid = orm.Column(orm.Integer)
    trans_type = orm.Column(orm.Integer)
    charge_type = orm.Column(orm.Integer)  # 充值类型，QQ, 网银
    amount = orm.Column(orm.Float)  # Decimal(10, 5)
    recharge_id = orm.Column(orm.BigInteger)  # 充值id
    status = orm.Column(orm.Integer)  # 加快查询速度，虽然recharge_record里面有status,但是联表查询很慢
    today_cost = orm.Column(orm.Float)
    extend = orm.Column(orm.TEXT)


# Delete
class RechargeRecord(BaseModel, TimeColumnMixin):
    __tablename__ = 'recharge_record'
    id = orm.Column(orm.BigInteger, primary_key=True)
    accountid = orm.Column(orm.Integer, default=None)
    # appid = orm.Column(orm.String(30), default=None)
    status = orm.Column(orm.Integer)
    pay_url = orm.Column(orm.TEXT)
    recharge_type = orm.Column(orm.Integer)
    extend = orm.Column(orm.TEXT)


class Account(UserMixin, BaseModel):
    __tablename__ = 'accounts'
    id = orm.Column(orm.Integer, primary_key=True)
    phone = orm.Column(orm.String(24), unique=True, index=True)
    passwd_hash = orm.Column(orm.String(128))
    name = orm.Column(orm.String(30))
    balance = orm.Column(orm.Float)  # 服务费 Decimal(10, 5)

    def __init__(self):
        self.added_IDS = []

    @property
    def password(self):
        raise AttributeError('password is not readale')

    @password.setter
    def password(self, password):
        self.passwd_hash = bcrypt.generate_password_hash(password)

    def verify_passwd(self, passwd):
        return bcrypt.check_password_hash(self.passwd_hash, passwd)


class UserToken(BaseModel):
    __tablename__ = 'user_token'
    user_id = orm.Column(orm.BigInteger, primary_key=True)
    token = orm.Column(orm.VARCHAR(64), primary_key=True)
    deleted = orm.Column(orm.SmallInteger, default=0, nullable=False)


class AlipayAppid(BaseModel):
    __tablename__ = 'alipay_appid'
    id = orm.Column(orm.Integer, primary_key=True)
    aliappid = orm.Column(orm.BigInteger, nullable=False)
    notify_url = orm.Column(orm.VARCHAR(200))
    public_key = orm.Column(orm.TEXT)
    private_key = orm.Column(orm.TEXT)
    extend = orm.Column(orm.TEXT)


class UserAuthKey(BaseModel, TimeColumnMixin):
    __tablename__ = 'user_authkey'
    accountid = orm.Column(orm.BigInteger, primary_key=True)
    authkey = orm.Column(orm.VARCHAR(128))

