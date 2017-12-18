# -*- coding: utf-8 -*-
import json
import random
import uuid
import logging

from db.account.model import (
    Appid, Account, UserToken, AppManage, VALID_STATUS, IMG_PATH, RechargeRecord,
    AppidChannel, PollingCustID, JinjianAppid, JinjianRecord, Transaction, AlipayAppid,
    AccountRelation, APPID_STATUS, MCH_TYPE)
from db.account.model import ADMIN_MCH_ID
from utils.decorator import sql_wrapper
from db.pay_record.model import PAY_TYPE
from db.account.model import TRANS_TYPE, RECHARGE_STATUS, BankCardInfo
from cache import redis_cache
from utils import err
from db import bcrypt
from db import orm
from utils import id_generator
from utils.respcode import StatusCode

_LOGGER = logging.getLogger(__name__)


@sql_wrapper
def get_appkey(appid):
    account_appid = Appid.query.filter(Appid.appid == appid).first()
    return account_appid.appkey if account_appid else None


@sql_wrapper
def get_mch_name(appid):
    app_data = Appid.query.filter(Appid.appid== appid).first()
    if app_data:
        return app_data.mch_name
    else:
        return None


@sql_wrapper
def get_jinjian_appkey(appid):
    jinjian = JinjianAppid.query.filter(JinjianAppid.appid == appid).first()
    return jinjian.appkey


@sql_wrapper
def create_jinjian_record(appid, real_pay, jinjian_data, resp_data, mch_name=None, custid=None, jinjian_id=None,
                          status=0):
    jinjian = JinjianAppid.query.filter(JinjianAppid.appid == appid).first()
    accountid = jinjian.accountid
    record = JinjianRecord()
    record.id = id_generator.generate_long_id('jinjian') if jinjian_id else jinjian_id
    record.accountid = accountid
    record.real_pay = real_pay
    record.jinjian_data = jinjian_data
    record.resp_data = resp_data
    record.status = status
    record.mch_name = mch_name
    record.custid = custid
    record.save()


@sql_wrapper
def get_appid_detail(appid, pay_type=None, real_pay=None, polling=False):
    query = Appid.query.filter(Appid.appid == appid)
    if pay_type:
        query = query.filter(Appid.pay_type == pay_type)
    if real_pay:
        return query.filter(Appid.real_pay == real_pay).first()
    appid_channel = AppidChannel.query.filter(Appid.appid == appid).first()
    if appid_channel:
        account_appid = query.filter(Appid.real_pay == appid_channel.real_pay).first()
    else:
        account_appid = query.first()
        # 轮询的情况
    if polling and account_appid and account_appid.polling:
        _LOGGER.info('polling #########################')
        polling_custids = PollingCustID.query.filter(PollingCustID.appid == appid) \
            .filter(PollingCustID.valid == True).all()
        polling_custids = list(polling_custids)
        polling_custid = random.choice(polling_custids)
        polling_custid.accountid = account_appid.accountid
        polling_custid.fee_rate = account_appid.fee_rate
        print polling_custid.custid, polling_custid.id
        return polling_custid
    return account_appid


@sql_wrapper
def get_random_polling(appid_detail):
    polling_custids = PollingCustID.query.filter(PollingCustID.appid == appid_detail.appid) \
        .filter(PollingCustID.valid == True).all()
    polling_custids = list(polling_custids)
    polling_custid = random.choice(polling_custids)
    polling_custid.accountid = appid_detail.accountid
    return polling_custid


@sql_wrapper
def get_account_appid(accountid):
    account_appids = Appid.query.filter(Appid.accountid == accountid).all()
    return account_appids


@sql_wrapper
def create_account_appid(accountid, custid, real_pay, pay_type, **kwargs):
    account_appid = Appid()
    account_appid.accountid = accountid
    account_appid.custid = custid
    account_appid.pay_type = pay_type
    account_appid.real_pay = real_pay
    account_appid.appkey = uuid.uuid4().hex

    for k, v in kwargs.items():
        if k not in ['valid', 'sceneInfo', 'extend', 'fee_rate', 'appid', 'appkey',
                     'banklinknumber', 'paymenttype', 'mch_name', 'polling']:
            raise err.ServerError('keyword[%s] unknown for appid' % k)
        setattr(account_appid, k, v)

    account_appid.save()
    return account_appid


@sql_wrapper
def trash_appid(appid):
    appid = Appid.query.filter(Appid.appid == appid).first()
    if appid:
        appid.valid = False
        appid.save()


@sql_wrapper
def login_user(phone, password):
    user = Account.query.filter(Account.phone == phone).first()
    if not user:
        raise err.AuthenticateError(status=StatusCode.INVALID_USER)

    if not bcrypt.check_password_hash(user.passwd_hash, password):
        raise err.AuthenticateError(status=StatusCode.WRONG_PASSWORD)

    user_token = UserToken()
    user_token.token = id_generator.generate_uuid()
    user_token.deleted = 0
    user_token.user_id = user.id
    user_token.save()

    user_info = user.as_dict()
    if user.id in ADMIN_MCH_ID:
        user_info['admin'] = 1
    else:
        user_info['admin'] = 0
    user_info['token'] = user_token.token
    user_info['balance'] = float(user_info['balance'] or 0)
    user_info.pop('passwd_hash', '')
    return user_info


@sql_wrapper
def logout_user(user_id):
    UserToken.query.filter(
        UserToken.user_id == user_id).update({'deleted': 1})
    orm.session.commit()


@sql_wrapper
def get_online_info(user_id, token):
    return UserToken.query.filter(
        UserToken.user_id == user_id).filter(UserToken.token == token).first()


@sql_wrapper
def get_user(user_id):
    return Account.query.filter(Account.id == user_id).first()


@sql_wrapper
def register_user(phone, passwd):
    user = Account()
    user.phone = phone
    user.password = passwd
    user.balance = 1.0
    user.save()


@sql_wrapper
def get_user_by_phone(phone):
    return Account.query.filter(Account.phone == phone).first()


@sql_wrapper
def create_app_manage(appname, app_type, pay_type, account_id):
    for t in pay_type:
        if t not in PAY_TYPE.values():
            raise err.ParamError('pay_type')
    appid = redis_cache.appid_generator()
    app_manage = AppManage()
    app_manage.accountid = account_id
    app_manage.appid = appid
    app_manage.appname = appname
    app_manage.app_type = app_type
    app_manage.pay_type = json.dumps(pay_type)
    app_manage.valid = VALID_STATUS.AUDIT
    app_manage.save()


@sql_wrapper
def query_app_manage(accountid, **kwargs):
    query = AppManage.query
    if accountid not in ADMIN_MCH_ID:
        child_mchids = get_child_mchids(accountid)
        query = AppManage.query.filter(AppManage.accountid.in_(child_mchids))
    filters = []
    junction = orm.and_
    query = query.filter(AppManage.valid != APPID_STATUS.DELETE)
    for key in ['appid', 'app_type', 'valid', 'balance_type', 'industry_no']:
        if key in kwargs and kwargs[key]:
            filters.append(getattr(AppManage, key) == int(kwargs[key]))
    if 'begin_at' in kwargs and kwargs['begin_at']:
        filters.append(AppManage.begin_at >= kwargs['begin_at'])
    if 'end_at' in kwargs and kwargs['end_at']:
        filters.append(orm.func.DATE(AppManage.end_at) <= kwargs['end_at'])
    if 'mch_number' in kwargs and kwargs['mch_number']:
        filters.append(getattr(AppManage, 'id') == kwargs['mch_number'])
    for key in ['appname', 'mch_name', 'mch_short_name', 'bank_no', 'card_number',
                'paymenttype', 'industry_no', 'bank_name', 'balance_name']:
        if key in kwargs and kwargs[key]:
            filters.append(getattr(AppManage, key) == kwargs[key])
    if filters:
        query = query.filter(junction(*filters))
    query = query.order_by(AppManage.created_at.desc())
    count = query.count()
    if 'limit' in kwargs and kwargs['limit']:
        query = query.limit(kwargs['limit'])
    if 'offset' in kwargs and kwargs['offset']:
        query = query.offset(kwargs['offset'])
    return query.all(), count


def _save_file(filestorage):
    old_filename = filestorage.filename
    postfix = old_filename.split('.')[-1]
    filename = uuid.uuid4().hex + '.' + postfix.lower()
    filestorage.filename = filename
    filestorage.save(IMG_PATH + filename)
    filestorage.stream.seek(0)
    return filename


@sql_wrapper
def get_jinjian(jinjian_id, mchid=None):
    query = JinjianRecord.query.filter(JinjianRecord.id == jinjian_id)

    if (mchid is not None) and mchid not in ADMIN_MCH_ID:
        query = JinjianRecord.query.filter(JinjianRecord.accountid.in_(get_child_mchids(mchid)))

    return query.first()


def get_child_mchids(mchid):
    child_mchids = AccountRelation.query.filter(AccountRelation.accountid == mchid)
    child_mchids = [each.childid for each in child_mchids]
    child_mchids.append(mchid)
    return child_mchids


@sql_wrapper
def get_jinjians(mchid,
                 limit,
                 offset,
                 status=None,
                 bank_link_number=None,
                 begin_at=None,
                 end_at=None,
                 mch_name=None,
                 mch_short_name=None):

    query = JinjianRecord.query
    if mchid not in ADMIN_MCH_ID:
        child_mchids = get_child_mchids(mchid)
        query = JinjianRecord.query.filter(JinjianRecord.accountid.in_(child_mchids))

    if status is not None:
        query = query.filter(JinjianRecord.status == status)
    if bank_link_number is not None:
        query = query.filter(JinjianRecord.banklinknumber == bank_link_number)
    if begin_at is not None:
        query = query.filter(JinjianRecord.created_at >= begin_at)
    if end_at is not None:
        query = query.filter(orm.func.date_(JinjianRecord.updated_at) <= end_at)
    if mch_name is not None:
        query = query.filter(JinjianRecord.mch_name == mch_name)
    if mch_short_name is not None:
        query = query.filter(JinjianRecord.mch_name == mch_short_name)
    count = query.count()
    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)

    return query.all(), count


def _convert_mch_type(industryNo):
    MCH_RANGE = {
        (161215010100001, 161215010100360): MCH_TYPE.ENTERPRISE,
        (161215010100361, 161215010100662): MCH_TYPE.PRIVATE,
        (161215010100663, 161215010100692): MCH_TYPE.PUBLIC
    }
    for key in MCH_RANGE.keys():
        if key[0] <= industryNo <= key[1]:
            return MCH_RANGE[key]
    return None


@sql_wrapper
def init_jinjian(user_id, real_pay, form, files, payment_type):
    appid_detail = Appid.query.order_by(Appid.appid.desc()).with_for_update(of='account_appid').first()
    appid = (appid_detail.appid if appid_detail else 0) + 1
    appkey = uuid.uuid4().hex
    appmanage = AppManage()
    appmanage.accountid = user_id
    appmanage.appid = appid
    appmanage.paymenttype = payment_type
    extend = {'url': form.get('url'),
              'serviceTel': form.get('serviceTel'),
              'legalMobile': form.get('legalMobile'),
              'ic_card': form.get('ic_card', '')}
    appmanage.extend = json.dumps(extend)
    print 'form', form
    print 'files', files
    if payment_type == 'D0':  # 浦发d0
        appmanage.appname = form.get('pf_appname')
        appmanage.app_type = form.get('pf_app_type')
        pf_pay_type = []
        for key in ['pf_pay_type_wx', 'pf_pay_type_zfb', 'pf_pay_type_zfbh5']:
            if form.get(key):
                pf_pay_type.append(int(form.get(key)))
        appmanage.pay_type = json.dumps(pf_pay_type)
    if payment_type == 'D1':
        appmanage.appname = form.get('zh_appname')
        appmanage.app_type = form.get('zh_app_type')
        zh_pay_type = []
        for key in ['zh_pay_type_wx', 'zh_pay_type_zfb', 'zh_pay_type_zfbh5']:
            if form.get(key):
                zh_pay_type.append(int(form.get(key)))
        appmanage.pay_type = json.dumps(zh_pay_type)
    appmanage.mch_number = form.get('mchNumber')
    appmanage.mch_name = form.get('mchName')
    appmanage.mch_short_name = form.get('mch_short_name')
    appmanage.balance_type = form.get('balance_type')
    appmanage.balance_name = form.get('balance_name')
    appmanage.valid = APPID_STATUS.UNREADY
    appmanage.userid_card = form.get('userid_card')
    appmanage.bank_city = form.get('bank_city')
    appmanage.card_name = form.get('card_name')
    appmanage.card_number = form.get('card_number')
    appmanage.bank_name = form.get('bank_name')
    appmanage.bank_no = form.get('bank_no')
    appmanage.industry_no = _convert_mch_type(long(form.get('industryNo')))
    appmanage.save(auto_commit=False)
    orm.session.flush()
    record = JinjianRecord()
    record.id = id_generator.generate_long_id("jinjian")
    form_dct = {}
    for key, value in form.items():
        if key in ['officeCode', 'bankLinkNumber', 'mchName', 'mchShortName',
                   'city', 'province', 'district', 'address', 'mobile',
                   'bankNo', 'industryNo', 'balanceType', 'balanceName',
                   'userIdNumber', 'legalIdNumber', 'cardNumber', 'contact',
                   'wxUseParent', 'licenseNum', 'licenseStartDate',
                   'licensePeriod', 'licenseEndDate', 'licenseScope',
                   'useDine', 'wxValue', 'aliValue', 'zfbpay', 'wxpay',
                   'notifyUrl', 'appid', 'payDirectory']:
            form_dct[key] = value
    form_dct['paymentType'] = payment_type
    _officeCode = '0000000035'
    form_dct['officeCode'] = _officeCode

    for key in files:
        if files[key] and key in ['userIDCardA', 'userIDCardB', 'cardImgA',
                                  'licenseImg', 'mchFrontImg', 'mchInnerImg',
                                  'mchDeskImg', 'accountLicense', 'inScene',
                                  'outScene', 'legalIDCardA', 'legalIDCardB']:
            form_dct[key] = _save_file(files[key])
    pufa_banklinknumber = '310290000013'
    zhaoshang_banklinknumber = '308584000013'
    if payment_type == 'D0':  # 浦发d0
        form_dct["bankLinkNumber"] = pufa_banklinknumber
        record.banklinknumber = pufa_banklinknumber
    if payment_type == 'D1':
        form_dct.pop("wxValue", '')
        form_dct.pop("aliValue", '')
        form_dct["bankLinkNumber"] = zhaoshang_banklinknumber
        record.banklinknumber = zhaoshang_banklinknumber
    if form_dct["licensePeriod"] != "1":
        form_dct.pop("licensePeriod")
    record.accountid = user_id
    mch_name = form.get('mchName', '') or form.get('mchtName', '')
    record.paymenttype = payment_type
    record.appmanageid = appmanage.id
    record.mch_name = mch_name
    record.real_pay = real_pay
    record.jinjian_data = json.dumps(form_dct)
    record.status = VALID_STATUS.AUDIT
    record.save(auto_commit=False)
    pay_type = json.loads(appmanage.pay_type)
    for key in pay_type:
        account_appid = Appid()
        account_appid.appid = appid
        account_appid.appkey = appkey
        account_appid.accountid = user_id
        account_appid.valid = APPID_STATUS.UNVALID
        account_appid.pay_type = key
        account_appid.real_pay = real_pay
        account_appid.save(auto_commit=False)
    orm.session.commit()


@sql_wrapper
def update_jinjian_info(record, forms, files):
    form_dct = {}
    for key, value in forms.items():
        if value:
            form_dct[key] = value
    for key in files:
        if files[key]:
            form_dct[key] = _save_file(files[key])
    info = record.jinjian_info
    info.update(form_dct)
    record.jinjian_data = json.dumps(info)
    record.status = VALID_STATUS.AUDIT
    record.save()
    return record


@sql_wrapper
def get_jinjian_record_from_appmanageid(appmanageid):
    return JinjianRecord.query.filter(JinjianRecord.appmanageid == appmanageid).first()


@sql_wrapper
def create_recharge(orderid, accountid, pay_url, amount, recharge_type):
    recharge = RechargeRecord()
    trans = Transaction()
    trans.recharge_id = orderid
    trans.status = RECHARGE_STATUS.READY
    trans.accountid = accountid
    trans.amount = amount
    trans.charge_type = recharge_type
    trans.trans_type = TRANS_TYPE.RECHARGE
    trans.save(auto_commit=False)
    recharge.id = orderid
    recharge.accountid = accountid
    recharge.pay_url = pay_url
    recharge.amount = amount
    recharge.recharge_type = recharge_type
    recharge.status = RECHARGE_STATUS.READY
    recharge.save(auto_commit=False)
    orm.session.commit()
    return recharge


@sql_wrapper
def get_recharge(orderid):
    return RechargeRecord.query.filter(RechargeRecord.id == orderid).one()


@sql_wrapper
def get_transaction_by_rechargeid(orderid):
    return Transaction.query.filter(Transaction.recharge_id == orderid).first()


@sql_wrapper
def update_recharge(orderid, amount, status, extend=''):
    recharge = RechargeRecord.query.filter(RechargeRecord.id == orderid).one()
    # if not recharge.amount == amount:
    #     raise err.InsufficientFunds("回调资金对不上")

    trans = Transaction.query.filter(Transaction.recharge_id == orderid).first()
    recharge.status = status
    recharge.extend = extend
    trans.status = status
    trans.extend = extend
    trans.save(auto_commit=False)
    recharge.save(auto_commit=False)
    if status == RECHARGE_STATUS.SUCCESS:
        acc = Account.query.filter(Account.id == trans.accountid).first()
        acc.balance += amount
        acc.save(auto_commit=False)
    orm.session.commit()


@sql_wrapper
def get_transaction_record(accountid, begin_at, end_at, charge_type,
                           status, trans_type, limit, offset):

    """
    {
        "total_recharge": "1000",
        "consumed": "900",
        "average_consume_per_day": "101",
        "total_size": 2003,
        "transaction: []
    }
    """
    query = Transaction.query.filter(Transaction.accountid == accountid)

    junction = orm.and_
    filters = []
    if begin_at:
        filters.append(Transaction.created_at >= begin_at)
    if end_at:
        filters.append(Transaction.updated_at < end_at)
    if charge_type is not None:
        filters.append(Transaction.charge_type == charge_type)
    if status is not None:
        filters.append(Transaction.status == status)
    if trans_type is not None:
        filters.append(Transaction.trans_type == trans_type)

    if filters:
        query = query.filter(junction(*filters))

    total_size = query.count()
    trans = query.order_by(Transaction.updated_at.desc()).limit(limit).offset(offset).all()
    total_recharge = orm.session.query(orm.func.sum(Transaction.amount)).\
        filter(Transaction.accountid == accountid).\
        filter(Transaction.trans_type == TRANS_TYPE.RECHARGE).\
        filter(Transaction.status == RECHARGE_STATUS.SUCCESS).first()
    consumed = orm.session.query(orm.func.sum(Transaction.amount)).\
        filter(Transaction.accountid == accountid).\
        filter(Transaction.trans_type == TRANS_TYPE.COST).first()
    query_date = orm.session.query(Transaction.created_at).filter(Transaction.accountid == accountid).\
        filter(Transaction.trans_type == TRANS_TYPE.COST)
    begin_date = query_date.order_by(Transaction.created_at).first()
    end_date = query_date.order_by(Transaction.updated_at.desc()).first()
    if begin_date is None or end_date is None:
        days_cnt = 0
    else:
        days_cnt = (end_date[0] - begin_date[0]).days or 1

    return {'total_size': total_size or 0,
            'transaction': trans,
            'total_recharge': total_recharge or 0,
            'consumed': consumed,
            'average_consume_per_day': float(consumed[0] or 0) / (days_cnt or 1)  # 总消耗 / 总使用天数
            }


@sql_wrapper
def update_jinjian_status(jj_id, status):
    record = JinjianRecord.query.filter(JinjianRecord.id == jj_id).first()
    record.status = status
    record.save()


@sql_wrapper
def get_jinjian_by_appmanageid(appmanageid):
    record = JinjianRecord.query.filter(JinjianRecord.appmanageid == appmanageid).first()
    return record


@sql_wrapper
def get_appmanage(appmanageid):
    return AppManage.query.filter(AppManage.id == appmanageid).filter(AppManage.valid != APPID_STATUS.DELETE).first()


@sql_wrapper
def delete_merchant(appmanageid):
    merchant = AppManage.query.filter(AppManage.id == appmanageid).first()
    merchant.valid = APPID_STATUS.DELETE
    appid_details = Appid.query.filter(Appid.appid == merchant.appid).all()
    for appid_detail in appid_details:
        appid_detail.valid = APPID_STATUS.DELETE
        appid_detail.save(auto_commit=False)
    merchant.save(auto_commit=False)
    orm.session.commit()


@sql_wrapper
def create_merchant(form):
    acc = Account()
    appid_detail = Appid.query.order_by(Appid.appid.desc()).with_for_update(of='account_appid').first()
    appid = long(appid_detail.appid if appid_detail else 0) + 1
    appkey = uuid.uuid4().hex
    pay_types = form.get('pay_type')
    pay_types = [int(item) for item in pay_types.split(',')]
    acc.phone = form.get('phone')
    acc.password = acc.phone
    acc.save(auto_commit=False)
    orm.session.flush()
    merchant = AppManage()
    merchant.accountid = acc.id
    merchant.app_type = form.get('app_type')
    merchant.pay_type = json.dumps(pay_types)
    merchant.appid = appid
    merchant.appname = form.get('appname')
    merchant.balance_name = form.get('balance_name')
    merchant.balance_type = form.get('balance_type')
    merchant.bank_city = form.get('bank_city')
    merchant.mch_name = form.get('mch_name')
    merchant.bank_name = form.get('bank_name')
    fee = {'withdraw_fee': form.get('withdraw_fee'),
           'service_fee': form.get('service_fee'),
           'trans_fee': form.get('trans_fee'),
           'pay_fee': form.get('pay_fee')}
    extend = {'extend': form.get('extend'),
              'fee': fee}
    merchant.extend = json.dumps(extend)
    merchant.bank_no = form.get('bank_no')
    merchant.card_name = form.get('card_name')
    merchant.card_number = form.get('card_number')
    merchant.userid_card = form.get('userid_card')
    merchant.valid = APPID_STATUS.VALID
    merchant.save(auto_commit=False)
    orm.session.flush()
    for pay_type in pay_types:
        appid_detail = Appid()
        appid_detail.accountid = acc.id
        appid_detail.appid = appid
        appid_detail.appkey = appkey
        appid_detail.mch_name = form.get('mch_name')
        appid_detail.fee_rate = float(form.get('pay_fee') or 0) * 100
        appid_detail.service_rate = float(form.get('service_rate') or 0) * 100
        appid_detail.real_pay = form.get('real_pay')
        appid_detail.pay_type = pay_type
        appid_detail.save(auto_commit=False)
    orm.session.commit()


@sql_wrapper
def get_appmanage_by_name(appname):
    return AppManage.query.filter(AppManage.appname == appname).first()

@sql_wrapper
def get_bank_card(user_id):
    return BankCardInfo.query.filter(BankCardInfo.accountid == user_id).filter(BankCardInfo.is_deleted == 0).first() or {}

@sql_wrapper
def create_bankcard_info(user_id, data):
    bankcard = BankCardInfo.query.filter(BankCardInfo.accountid == user_id).filter(BankCardInfo.is_deleted == 0).first()
    if bankcard:
        tobe_save = bankcard
    else:
        tobe_save = BankCardInfo()
    for k, v in data.iteritems():
        setattr(tobe_save, k, v)
    tobe_save.is_deleted = 0
    tobe_save.save()

@sql_wrapper
def delete_bankcard_info(user_id):
    bankcard = BankCardInfo.query.filter(BankCardInfo.accountid == user_id).filter(BankCardInfo.is_deleted==0).first()
    if not bankcard:
        return
    else:
        bankcard.is_deleted = 1
        bankcard.save()

@sql_wrapper
def get_alipay_appid(appid):
    return AlipayAppid.query.filter(AlipayAppid.appid == appid).first()


@sql_wrapper
def get_alipay_appid_by_alipay_id(alipay_id):
    return AlipayAppid.query.filter(AlipayAppid.aliappid == alipay_id).first()


@sql_wrapper
def query_withdraw_balance(accountid, page, size):
    sum_query = orm.session.query(orm.func.sum(Appid.recharge_total), orm.func.sum(Appid.withdraw_total), orm.func.sum(Appid.fee_total))
    query = Appid.query
    if accountid not in ADMIN_MCH_ID:
        child_mchids = get_child_mchids(accountid)
        query = Appid.query.filter(Appid.accountid.in_(child_mchids))
        sum_query = sum_query.filter(Appid.accountid.in_(child_mchids))
    try:
        query = query.filter(Appid.pay_type==23).order_by(Appid.created_at.desc())
        pagination = query.paginate(page, size)
    except:
        return 0, []
    withdraw_total, fee_total, recharge_total = sum_query.first()[1] or 0, sum_query.first()[2] or 0, sum_query.first()[0] or 0
    return pagination.pages, pagination.items, withdraw_total, fee_total, recharge_total


@sql_wrapper
def delete_bankcard_info(user_id):
    bankcard = BankCardInfo.query.filter(BankCardInfo.accountid == user_id).filter(BankCardInfo.is_deleted == 0).first()
    if not bankcard:
        return
    else:
        bankcard.is_deleted = 1
        bankcard.save()


@sql_wrapper
def get_appmanage_by_appid(appid):
    return AppManage.query.filter(AppManage.appid == appid).first()


@sql_wrapper
def get_withdraw_done(accountid, appid=''):
    sum_query = orm.session.query(orm.func.sum(Appid.withdraw_total))
    if accountid not in ADMIN_MCH_ID:
        child_mchids = get_child_mchids(accountid)
        sum_query = sum_query.filter(Appid.accountid.in_(child_mchids))
    if appid:
        appid_detail = Appid.query.filter(Appid.appid==appid).first()
        return appid_detail.withdraw_total or 0
    return sum_query.first()[0] or 0
