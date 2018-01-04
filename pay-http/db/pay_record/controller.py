# -*- coding: utf-8 -*-

from decimal import Decimal
import datetime
import logging
from random import randint

from utils.decorator import sql_wrapper
from db.pay_record.model import PAY_STATUS, PayRecord, NotifyRecord, \
        WithdrawRecord, DaifuRecord, WITHDRAW_STATUS, WITHDRAW_TYPE, \
        PAY_TYPE, DAIFU_STATUS, DAIFU_TYPE, DAIFU_FEE
from db.account.model import AccountRelation, Appid, Account, Transaction, TRANS_TYPE, ADMIN_MCH_ID
from db import orm
from utils.tz import utc_to_local_str
from utils import tz, err
from cache.redis_cache import get_appid_balance
from utils.id_generator import generate_long_id
from utils import err

_DEFAULT_PAGE_SIZE  = 10

_LOGGER = logging.getLogger(__name__)

@sql_wrapper
def save_originid(payid, originid):
    PayRecord.query.filter(PayRecord.id == payid).update({
        'originid': originid,
        'pay_status': PAY_STATUS.UP_SUCCESS
    })
    orm.session.commit()


@sql_wrapper
def get_withdraw_balance(appid, pay_type):
    app_data = Appid.query.filter(
        Appid.appid == appid).filter(
        Appid.pay_type == pay_type).first()
    if not app_data:
        return None
    else:
        return app_data.recharge_total - app_data.withdraw_total - app_data.fee_total - app_data.daifu_total


@sql_wrapper
def get_balance_by_accountid(accountid):
    app_data = Appid.query.filter(
        Appid.accountid == accountid).first()
    if not app_data:
        return None, None
    else:
        return app_data.appid, app_data.recharge_total - app_data.withdraw_total - app_data.fee_total - app_data.daifu_total


@sql_wrapper
def succeed_pay(originid, orderid, amount, extend=None):
    pay_record = PayRecord.query.filter(PayRecord.id == orderid) \
        .filter(PayRecord.amount == amount) \
        .filter(PayRecord.pay_status.in_((PAY_STATUS.UP_SUCCESS, PAY_STATUS.READY))) \
        .with_lockmode('update').first()
    service_fee = pay_record.service_fee
    if originid:
        pay_record.originid = originid
    pay_record.pay_status = PAY_STATUS.PAY_SUCCESS
    pay_record.pay_time = datetime.datetime.utcnow()
    if extend:
        pay_record.extend = extend
    pay_record.save(auto_commit=False)

    if pay_record.service_fee > 0:
        account = Account.query.filter(Account.id == pay_record.mchid) \
            .with_lockmode('update').first()
        account.balance -= service_fee
        account.save(auto_commit=False)

        last_trans = Transaction.query.filter(Transaction.accountid == account.id).\
            filter(Transaction.trans_type == TRANS_TYPE.COST).\
            filter(orm.func.date_(Transaction.updated_at) == orm.func.date_(tz.local_now())).first()
        if not last_trans:
            last_trans = Transaction()
            last_trans.amount = 0
            last_trans.accountid = account.id
            last_trans.trans_type = TRANS_TYPE.COST

        last_trans.amount -= pay_record.service_fee  # 总钱数
        last_trans.save(auto_commit=False)

    appid = Appid.query.filter(
        Appid.appid == pay_record.appid).with_lockmode('update').first()
    appid.recharge_total += Decimal(amount)
    appid.fee_total += pay_record.fee
    appid.service_fee_total += pay_record.service_fee
    appid.save(auto_commit=False)

    orm.session.commit()


@sql_wrapper
def fail_pay(originid, orderid, amount, extend=None):
    pay_record = PayRecord.query.filter(PayRecord.id == orderid) \
        .filter(PayRecord.amount == amount).first()
    if pay_record:
        pay_record.originid = originid
        pay_record.pay_status = PAY_STATUS.PAY_FAIL
        if extend:
            pay_record.extend = extend
        pay_record.save()


@sql_wrapper
def get_pay(payid):
    pay_record = PayRecord.query.filter(PayRecord.id == payid).first()
    return pay_record


@sql_wrapper
def get_pay_by_id(appid, order_id):
    pay_record = PayRecord.query.filter(PayRecord.appid == appid) \
        .filter(PayRecord.orderid == order_id).first()
    return pay_record


@sql_wrapper
def get_child_appids(accountid):
    if accountid in ADMIN_MCH_ID:
        appids = Appid.query
    else:
        child_mchids = get_child_mchids(accountid)
        appids = Appid.query.filter(Appid.accountid.in_(child_mchids))
    appids = appids.all()
    return appids


def get_child_mchids(mchid):
    child_mchids = AccountRelation.query.filter(AccountRelation.accountid == mchid)
    child_mchids = [each.childid for each in child_mchids]
    child_mchids.append(mchid)
    return child_mchids


def get_query(mchid):
    query = PayRecord.query
    count_query = orm.session.query(orm.func.count(PayRecord.id))
    sum_query = orm.session.query(orm.func.sum(PayRecord.amount),
                                  orm.func.sum(PayRecord.fee), orm.func.sum(PayRecord.service_fee))
    if mchid not in ADMIN_MCH_ID:
        child_mchids = get_child_mchids(mchid)
        query = PayRecord.query.filter(PayRecord.mchid.in_(child_mchids))
        count_query = orm.session.query(orm.func.count(PayRecord.id)).filter(PayRecord.mchid.in_(child_mchids))
        sum_query = orm.session.query(orm.func.sum(PayRecord.amount),
                                      orm.func.sum(PayRecord.fee), orm.func.sum(PayRecord.service_fee)).filter(
            PayRecord.mchid.in_(child_mchids))
    return query, count_query, sum_query


def get_service_fee_by_appid(appid):
    appid_detail = Appid.query.filter(Appid.appid==appid).first()
    return appid_detail.service_fee_total

def get_service_fee_by_mchid(mchid):
    resp = orm.session.query(orm.func.sum(Appid.service_fee_total)).filter(Appid.accountid==mchid).first()
    return resp[0] or 0

def get_balance(mchid):
    child_appids = get_child_appids(mchid)
    appids = []
    if child_appids:
        for child in child_appids:
            appids.append(child.appid)
    appids = list(set(appids))
    balance = 0.0
    for appid in appids:
        appid_detail = Appid.query.filter(Appid.appid == appid).first()
        balance += float(appid_detail.recharge_total - appid_detail.withdraw_total - appid_detail.fee_total - appid_detail.service_fee_total)
    return balance 


@sql_wrapper
def get_pay_record(mchid, pay_type, pay_status, start_date, end_date, order_id, appid, limit=0, offset=0):
    query, count_query, sum_query = get_query(mchid)
    filters = []
    junction = orm.and_
    balance = get_balance(mchid)
    if pay_type:
        filters.append(PayRecord.pay_type == pay_type)
    if pay_status:
        filters.append(PayRecord.pay_status == pay_status)
    if order_id:
        filters.append(PayRecord.orderid == order_id)
    if start_date:
        filters.append(PayRecord.created_at >= start_date)
    if end_date:
        filters.append(PayRecord.created_at < end_date)
    if appid:
        filters.append(PayRecord.appid == appid)
        appid_detail = Appid.query.filter(Appid.appid == appid).first()
        balance = float(appid_detail.recharge_total - appid_detail.withdraw_total - appid_detail.fee_total - get_service_fee_by_appid(appid))
    if filters:
        query = query.filter(junction(*filters))
        count_query = count_query.filter(junction(*filters))
        sum_query = sum_query.filter(junction(*filters))

    query = query.order_by(PayRecord.created_at.desc())
    if limit > 0:
        query = query.limit(limit)
        query = query.offset(offset)
    return count_query.all()[0][0] or 0, query.all(), sum_query.all()[0][0] or 0,\
        sum_query.all()[0][1] or 0, sum_query.all()[0][2] or 0, balance


@sql_wrapper
def export_pay_records(mchid, pay_type, pay_status, start_date, end_date, order_id, appid):
    query, _, _ = get_query(mchid)
    filters = []
    junction = orm.and_
    if pay_type:
        filters.append(PayRecord.pay_type == pay_type)
    if pay_status:
        filters.append(PayRecord.pay_status == pay_status)
    if order_id:
        filters.append(PayRecord.orderid == order_id)
    if start_date:
        filters.append(PayRecord.created_at >= start_date)
    if end_date:
        filters.append(PayRecord.created_at < end_date)
    if appid:
        filters.append(PayRecord.appid == appid)
    if filters:
        query = query.filter(junction(*filters))
    items = query.all()
    resp_items = []

    for item in items:
        data = [item.mchid, item.appid, item.orderid, utc_to_local_str(item.created_at), item.pay_type, item.pay_status,
                str(item.amount)]
        resp_items.append(data)
    return resp_items


def add_notify(payid, status):
    notify_record = NotifyRecord.query.filter(NotifyRecord.payid == payid).first()
    if not notify_record:
        notify_record = NotifyRecord()
        notify_record.payid = payid
        notify_record.pay_status = status
        notify_record.try_times = 0
    notify_record.try_times += 1
    notify_record.status = status
    notify_record.save()
    return notify_record


@sql_wrapper
def create_daifu_record(daifu_data):
    try:
        mchid = daifu_data['accountid']
        amount = daifu_data['amount']
        bank_name = daifu_data['bank_name']
        bank_city = daifu_data['bank_city']
        bank_account_name = daifu_data['bank_account_name']
        bank_account_no = daifu_data['bank_account_no']
        card_type = daifu_data['card_type']
        bank_province = daifu_data['bank_province']
        bank = daifu_data['bank']
        status = DAIFU_STATUS.READY
        fee = DAIFU_FEE
        daifu_type = DAIFU_TYPE.YSEPAY
    except Exception, e:
        raise err.ParamError(e)

    account_detail = Appid.query.filter(Appid.accountid == mchid).first()
    account_detail.daifu_total += Decimal('%s' % amount)
    account_detail.save(auto_commit=False)

    daifu_record = DaifuRecord()
    daifu_record.id = int('%s%s' % (tz.times_str(), randint(1111,9999)))
    daifu_record.mchid = mchid
    daifu_record.daifu_type = daifu_type
    daifu_record.bank_name = bank_name
    daifu_record.bank_city = bank_city
    daifu_record.bank_province = bank_province
    daifu_record.bank = bank
    daifu_record.bank_account_name = bank_account_name
    daifu_record.bank_account_no = bank_account_no
    daifu_record.card_type = card_type
    daifu_record.amount = Decimal('%s' % amount)
    daifu_record.fee = Decimal('%s' % fee)
    daifu_record.extend = ''
    daifu_record.status = status
    daifu_record.save(auto_commit=False)

    orm.session.commit()
    return daifu_record


@sql_wrapper
def get_daifu_record(accountid, status, bank_account_no, bank_account_name, page, size):
    query = DaifuRecord.query
    if accountid not in ADMIN_MCH_ID:
        child_mchids = get_child_mchids(accountid)
        query = DaifuRecord.query.filter(DaifuRecord.mchid.in_(child_mchids))
    junction = orm.and_
    filters = []
    if status:
        filters.append(DaifuRecord.status == int(status))
    if bank_account_no:
        filters.append(DaifuRecord.bank_account_no == bank_account_no)
    if bank_account_name:
        filters.append(DaifuRecord.bank_account_name == bank_account_name)
    if filters:
        query = query.filter(junction(*filters))
    query = query.order_by(DaifuRecord.created_at.desc())
    pagination = query.paginate(page, size)
    return pagination.pages, pagination.items


@sql_wrapper
def update_daifu_record_by_id(daifu_id, status, extend=''):
    if status == DAIFU_STATUS.READY:
        raise err.ResourceInsufficient('status not valid')
    record = DaifuRecord.query.filter(
        DaifuRecord.id == daifu_id).with_lockmode('update').first()
    if record:
        if status == DAIFU_STATUS.REFUSED:
            assert record.status == DAIFU_STATUS.READY
            record.fee = 0
        elif status == DAIFU_STATUS.PERMITED:
            assert record.status == DAIFU_STATUS.READY
        elif status == DAIFU_STATUS.PROCESSING:
            assert record.status == DAIFU_STATUS.PERMITED
        elif status == DAIFU_STATUS.SUCCESS:
            assert record.status == DAIFU_STATUS.PROCESSING
        elif status == DAIFU_STATUS.FAIL:
            record.fee = 0
            assert record.status in (DAIFU_STATUS.PROCESSING,
                                     DAIFU_STATUS.PERMITED)

        record.extend = extend
        record.status = status
        record.save(auto_commit=False)

        if record.fee == 0:
            app_data = Appid.query.filter(
                Appid.accountid == record.mchid).with_lockmode('update').first()
            app_data.daifu_total -= Decimal(record.amount)
            app_data.save(auto_commit=False)

        orm.session.commit()
        return record
    else:
        raise err.ResourceInsufficient('record not valid')


@sql_wrapper
def get_daifu_sum(accountid):
    sum_query = orm.session.query(orm.func.sum(DaifuRecord.amount))
    fee_sum_query = orm.session.query(orm.func.sum(DaifuRecord.fee))
    count_query = orm.session.query(orm.func.count(DaifuRecord.id))
    suc_sum_query = orm.session.query(orm.func.sum(DaifuRecord.amount))
    submit_sum_query = orm.session.query(orm.func.sum(DaifuRecord.amount))
    if accountid not in ADMIN_MCH_ID:
        child_mchids = get_child_mchids(accountid)
        sum_query = sum_query.filter(DaifuRecord.mchid.in_(child_mchids))
        fee_sum_query = fee_sum_query.filter(DaifuRecord.mchid.in_(child_mchids))
        count_query = count_query.filter(DaifuRecord.mchid.in_(child_mchids))
        suc_sum_query = suc_sum_query.filter(DaifuRecord.mchid.in_(child_mchids))
        submit_sum_query = orm.session.query(orm.func.sum(DaifuRecord.amount))

    sum_query = sum_query.first()
    fee_sum_query = fee_sum_query.first()
    count_query = count_query.first()
    suc_sum_query = suc_sum_query.filter(
        DaifuRecord.status == DAIFU_STATUS.SUCCESS).first()
    subumit_sum_query = submit_sum_query.filter(
        DaifuRecord.status == DAIFU_STATUS.READY).first()
    return sum_query[0] or 0, count_query[0] or 0, suc_sum_query[0] or 0, \
            fee_sum_query[0] or 0, submit_sum_query[0] or 0


@sql_wrapper
def create_withdraw_record(appid, real_pay, amount, fee=2, order_code=0, mchid=None, extend='', acc_name='',
                           paystatus=1, channel=None, to_account='', bank_name='',
                           trans_time=None, withdraw_type=1):
    appid_detail = Appid.query.filter(Appid.appid == appid).filter(Appid.real_pay == real_pay).first()
    appid_detail.withdraw_total += Decimal('%s' % amount)
    appid_detail.save(auto_commit=False)
    withdraw_record = WithdrawRecord()
    withdraw_record.id = generate_long_id('pay')
    withdraw_record.appid = appid
    withdraw_record.mchid = mchid
    withdraw_record.real_pay = real_pay
    withdraw_record.bank_name = bank_name
    withdraw_record.amount = Decimal(amount)
    withdraw_record.extend = extend
    withdraw_record.acc_name = acc_name
    withdraw_record.withdraw_type = withdraw_type
    withdraw_record.fee = Decimal('%s' % fee)
    withdraw_record.status = WITHDRAW_STATUS.READY
    withdraw_record.order_code = order_code
    withdraw_record.channel = channel
    withdraw_record.acc_name = acc_name
    withdraw_record.to_account = to_account
    withdraw_record.trans_time = trans_time
    withdraw_record.save(auto_commit=False)
    orm.session.commit()
    return withdraw_record


@sql_wrapper
def update_withdraw_record(record, fee, order_code, paystatus, extend=None):
    record.fee = Decimal(fee)
    record.order_code = order_code
    record.status = paystatus
    record.extend = extend
    record.save(auto_commit=False)
    appid = Appid.query.filter(
        Appid.appid == record.appid).with_lockmode('update').first()
    appid.withdraw_total += record.amount
    appid.save(auto_commit=False)
    orm.session.commit()


@sql_wrapper
def update_withdraw_record_by_id(withdraw_id, status):
    if status not in (WITHDRAW_STATUS.SUCCESS, WITHDRAW_STATUS.FAIL):
        raise err.ResourceInsufficient('status not valid')
    record = WithdrawRecord.query.filter(WithdrawRecord.id == withdraw_id) \
        .with_lockmode('update').first()
    if record and record.status == WITHDRAW_STATUS.READY:
        if status == WITHDRAW_STATUS.FAIL:
            record.fee = 0
        record.status = status
        record.save(auto_commit=False)

        app_data = Appid.query.filter(Appid.appid == record.appid) \
            .filter(Appid.pay_type == PAY_TYPE.ALIPAY_REAL_H5) \
            .with_lockmode('update').first()
        app_data.withdraw_total -= Decimal(record.amount)
        app_data.save(auto_commit=False)

        orm.session.commit()
        return True
    else:
        raise err.ResourceInsufficient('record not valid')


@sql_wrapper
def get_withdraw_data(account_id):
    sum_query = orm.session.query(orm.func.sum(WithdrawRecord.amount, WithdrawRecord.fee))
    if account_id not in ADMIN_MCH_ID:
        child_appids = get_child_appids(account_id)
        appids = [child.appid for child in child_appids] if child_appids is not None else []
        sum_query = sum_query.filter(WithdrawRecord.appid.in_(appids))
    return sum_query.filter(WithdrawRecord.status == WITHDRAW_STATUS.SUCCESS).all()[0][0], \
        sum_query.filter(WithdrawRecord.status == WITHDRAW_STATUS.SUCCESS).all()[0][1], \
        sum_query.filter(WithdrawRecord.status == WITHDRAW_STATUS.READY).all()[0][0], \
        sum_query.filter(WithdrawRecord.status == WITHDRAW_STATUS.READY).all()[0][1]

@sql_wrapper
def get_withdraw_sum(accountid, order_code, pay_type, appid, start_date, end_date, withdraw_type, withdraw_status, to_account, acc_name):
    sum_query = orm.session.query(orm.func.sum(WithdrawRecord.amount))
    count_query = orm.session.query(orm.func.count(WithdrawRecord.id))
    suc_sum_query = orm.session.query(orm.func.sum(WithdrawRecord.amount))
    fee_sum_query = orm.session.query(orm.func.sum(WithdrawRecord.fee))
    if accountid not in ADMIN_MCH_ID:
        child_mchids = get_child_mchids(accountid)
        sum_query = sum_query.filter(WithdrawRecord.mchid.in_(child_mchids))
        count_query = count_query.filter(WithdrawRecord.mchid.in_(child_mchids))
        suc_sum_query = suc_sum_query.filter(WithdrawRecord.mchid.in_(child_mchids))
        fee_sum_query = fee_sum_query.filter(WithdrawRecord.mchid.in_(child_mchids))
    junction = orm.and_
    filters = []
    suc_filters = []
    suc_filters.append(WithdrawRecord.status == WITHDRAW_STATUS.SUCCESS)
    if withdraw_type:
        filters.append(WithdrawRecord.withdraw_type == withdraw_type)
        suc_filters.append(WithdrawRecord.withdraw_type == withdraw_type)
    if order_code:
        filters.append(WithdrawRecord.order_code == order_code)
        suc_filters.append(WithdrawRecord.order_code == order_code)
    if pay_type:
        filters.append(WithdrawRecord.channel == pay_type)
        suc_filters.append(WithdrawRecord.channel == pay_type)
    if appid:
        filters.append(WithdrawRecord.appid == appid)
        suc_filters.append(WithdrawRecord.appid == appid)
    if withdraw_status:
        filters.append(WithdrawRecord.status == int(withdraw_status))
        suc_filters.append(WithdrawRecord.status == int(withdraw_status))
    if to_account:
        filters.append(WithdrawRecord.to_account == to_account)
        suc_filters.append(WithdrawRecord.to_account == to_account)
    if acc_name:
        filters.append(WithdrawRecord.acc_name == acc_name)
        suc_filters.append(WithdrawRecord.acc_name == acc_name)
    if start_date:
        filters.append(WithdrawRecord.created_at >= start_date)
        suc_filters.append(WithdrawRecord.created_at >= start_date)
    if end_date:
        filters.append(WithdrawRecord.updated_at <= end_date)
        suc_filters.append(WithdrawRecord.updated_at <= end_date)
    if filters:
        sum_query = sum_query.filter(junction(*filters)).first()
        fee_sum_query = fee_sum_query.filter(junction(*filters)).first()
        count_query = count_query.filter(junction(*filters)).first()
    if suc_filters:
        suc_sum_query = suc_sum_query.filter(junction(*suc_filters)).first()
    return sum_query[0] or 0, count_query[0] or 0, suc_sum_query[0] or 0, fee_sum_query[0] or 0


@sql_wrapper
def get_withdraw_record(accountid, order_code, pay_type, pay_status, start_amount,
                        end_amount, appid, start_date, end_date, page, size,
                        withdraw_type=WITHDRAW_TYPE.API,
                        withdraw_status=WITHDRAW_STATUS.READY,
                        to_account = None,
                        acc_name = None,
                        source = False):

    limit = _DEFAULT_PAGE_SIZE if not size or size > _DEFAULT_PAGE_SIZE else size
    if not page or page < 1:
        page = 1
    offset = 0 if not page else (page - 1) * limit

    if source:
        count, _, amount, fee, service_fee, balance = get_pay_record(accountid, pay_type, pay_status,
                                                                   start_date, end_date, '', appid, limit, offset)
    query = WithdrawRecord.query
    if accountid not in ADMIN_MCH_ID:
        child_mchids = get_child_mchids(accountid)
        query = WithdrawRecord.query.filter(WithdrawRecord.mchid.in_(child_mchids))
    junction = orm.and_
    filters = []
    if withdraw_type:
        filters.append(WithdrawRecord.withdraw_type == withdraw_type)
    if order_code:
        filters.append(WithdrawRecord.order_code == order_code)
    if pay_type:
        filters.append(WithdrawRecord.channel == pay_type)
    if appid:
        filters.append(WithdrawRecord.appid == appid)
    if withdraw_status:
        filters.append(WithdrawRecord.status == int(withdraw_status))
    if to_account:
        filters.append(WithdrawRecord.to_account == to_account)
    if acc_name:
        filters.append(WithdrawRecord.acc_name == acc_name)
    if start_amount:
        filters.append(WithdrawRecord.amount >= float(start_amount))
    if end_amount:
        filters.append(WithdrawRecord.amount < float(end_amount))
    if start_date:
        filters.append(WithdrawRecord.created_at >= start_date)
    if end_date:
        filters.append(WithdrawRecord.updated_at <= end_date)
    if filters:
        query = query.filter(junction(*filters))
    print withdraw_type, order_code, pay_type, appid, withdraw_status, to_account, start_amount, end_amount, start_date, end_date
    query = query.order_by(WithdrawRecord.created_at.desc())
    try:
        pagination = query.paginate(page, size)
    except Exception as e:
        _LOGGER.error("page nate error %s" % e)
        return 0, [], 0, 0,0,0,0
    if source:
        return pagination.pages, pagination.items, count, amount, fee, service_fee, balance
    else:
        print query.count()
        return pagination.pages, pagination.items


@sql_wrapper
def get_withdraw_by_id(id):
    return WithdrawRecord.query.filter(WithdrawRecord.id == id).first()


@sql_wrapper
def get_dealing_balance(appid):
    result = orm.session.query(orm.func.sum(WithdrawRecord.amount)).filter(WithdrawRecord.appid==appid).filter(WithdrawRecord.status==WITHDRAW_STATUS.READY).first()
    if result:
        return result[0] or 0
    return 0


@sql_wrapper
def withdraw_dealing_count(mchid):
    query = WithdrawRecord.query
    if mchid not in ADMIN_MCH_ID:
        child_mchids = get_child_mchids(mchid)
        query = WithdrawRecord.query.filter(WithdrawRecord.mchid.in_(child_mchids))
    return query.filter(WithdrawRecord.channel == 'bank').filter(WithdrawRecord.status==WITHDRAW_STATUS.READY).count() or 0

