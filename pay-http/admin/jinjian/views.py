# coding: utf-8

import logging

from flask.views import MethodView
from flask import render_template, g, request, redirect, url_for
from admin.jinjian import jinjian as jj_blueprint
from utils.api import token_required, response_wrapper
from utils import err, tz

from db.account.model import REAL_PAY, ADMIN_MCH_ID, VALID_STATUS
from db.account import controller as db
from admin.jinjian import controller

_JINJIAN_LOGGER = logging.getLogger('jinjian')


@jj_blueprint.route('/status', methods=['GET'])
# @response_wrapper
# @token_required
def list_jinjians():
    # if not g.user['id'] == 21:
    #     raise err.PermissionError("不是管理员")
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', 100)
    status = request.args.get('status', 'all')

    if status == "all":  # 列出所有进件
        jinjians, _ = db.get_jinjians(ADMIN_MCH_ID[0], offset=offset, limit=limit)
    elif status == "unaudit":  # 列出未审核的进件
        jinjians, _ = db.get_jinjians(ADMIN_MCH_ID[0], offset=offset, limit=limit, status=VALID_STATUS.AUDIT)
    else:
        raise err.NotImplementedError('TODO')

    return render_template('list_jinjian.html', jinjians=jinjians)


@jj_blueprint.route('/merchant_jinjian/<int:real_pay>', methods=['POST'])
@response_wrapper
@token_required
def merchant_jinjian(real_pay):

    if not real_pay == REAL_PAY.KEDA:
        raise err.NotImplementedError("只有客达能用")

    if request.form.get('paymentType_0'):
        db.init_jinjian(g.user['id'], real_pay, request.form,
                        files=request.files,
                        payment_type='D0')
    if request.form.get('paymentType_1'):
        db.init_jinjian(g.user['id'], real_pay, request.form,
                        files=request.files,
                        payment_type='D1')

    return {}


@jj_blueprint.route('/audit/<int:jj_id>', methods=['GET', 'PUT'])
@response_wrapper
# @token_required
def audit(jj_id):

    action = request.args.get('action', '')
    if not action:
        jinjian = db.get_jinjian(jj_id)
        return render_template('record_show.html', record=jinjian)

    # if g.user['id'] not in ADMIN_MCH_ID:
    #     raise err.PermissionError("不是管理员")

    if action not in ["refused", "submit"]:
        return err.PermissionError("不支持该操作")

    if action == 'refused':
        controller.refuse_jinjian(jj_id)

    if action == 'submit':
        controller.req_jinjian(jj_id)

    return redirect(url_for('jinjian.list_jinjians', status='unaudit'))


@jj_blueprint.route('/merchant_jinjians', methods=['GET'])
@response_wrapper
@token_required
def list_merchant_jinjians():
    """ 列出商户进件信息 """
    accountid = g.user['id']
    merchant_id = request.args.get('id')
    if merchant_id:
       jinjian = db.get_jinjian_by_appmanageid(merchant_id)
       if not jinjian:
           raise err.Issue(merchant_id)  # 这个错误有问题
       return {
           "info": controller.parse_jinjian_info(jinjian),
           "status": jinjian.status,
           "updated_at": tz.utc_to_local_str(jinjian.updated_at)
       }

    begin_at = request.args.get('begin_at')
    end_at = request.args.get('end_at')
    bank_name = request.args.get("bank_name")
    mch_name = request.args.get("mch_name")
    mch_short_name = request.args.get("mch_shortName")
    appname = request.args.get('appname')
    app_type = request.args.get('app_type')
    appid = request.args.get('appid')
    page = request.args.get('page', 1)
    page = int(page)
    size = request.args.get('size', 10)
    size = int(size)
    if bank_name not in ['', 'd0', 'd1', 'd0,d1']:
        raise err.ParamError(bank_name)
    if bank_name == 'd0,d1':
        bank_name = ''
    valid, status = '', ''

    return controller.get_app_manage(accountid, page, size, appid, app_type,
                                     valid, status, bank_name, begin_at,
                                     end_at, mch_name, mch_short_name,
                                     appname, bank_name.upper())


@jj_blueprint.route('/merchant_appids', methods=['GET'])
@response_wrapper
@token_required
def merchant_app():
    """ 展示有效appid """
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', 10)
    return controller.get_appids(g.user['id'], limit, offset)


@jj_blueprint.route('/pca', methods=['GET'])
@response_wrapper
@token_required
def pca():
    """ 查询省份城市地区 """
    province = request.args.get("province", "")
    city = request.args.get("city", "")
    pca = open('utils/pca.json').read()
    import json
    pca = json.loads(pca)

    if not province:
        return pca.keys()

    if not city:
        return pca.get(province, [])
    else:
        return pca.get(province, '湖北省').get(city, '武汉市')


@jj_blueprint.route('/banklist', methods=['GET'])
@response_wrapper
def banklist():
    from admin.jinjian.banklist import banklist
    return banklist


class MerchantManagement(MethodView):
    @response_wrapper
    @token_required
    def get(self):
        merchant_id = request.args.get('id')
        accountid = g.user['id']
        if not merchant_id:
            mch_name = request.args.get('mch_name')
            appid = request.args.get('appid')
            page = request.args.get('page', 1)
            page = int(page)
            size = request.args.get('size', 10)
            size = int(size)
            return controller.get_merchants(accountid, mch_name, appid, page, size)
        else:
            return controller.get_merchant(accountid, merchant_id)

    @response_wrapper
    @token_required
    def post(self):
        if not g.user['id'] in ADMIN_MCH_ID:
            raise err.PermissionError("权限不对")

        for key in request.form:
            if key not in ['real_pay', 'mch_name', 'phone', 'appname', 'app_type',
                           'pay_type', 'service_fee', 'pay_fee', 'trans_fee',
                           'withdraw_fee', 'extend', 'bank_name', 'balance_type',
                           'card_number', 'balance_name', 'bank_city', 'card_name',
                           'bank_no', 'userid_card']:
                raise err.ParamError(key)

        print 'post a management', request.form
        phone = request.form.get('phone')
        appname = request.form.get('appname')
        if db.get_user_by_phone(phone):
            raise err.Issue("手机号重复%s" % phone)
        if db.get_appmanage_by_name(appname):
            raise err.Issue("产品名重复%s" % appname)
        db.create_merchant(request.form)
        return {}

    @response_wrapper
    @token_required
    def delete(self):
        merchant_id = request.args.get('id')
        if not g.user['id'] in ADMIN_MCH_ID:
            raise err.PermissionError("权限不对")

        if merchant_id:
            db.delete_merchant(merchant_id)
        return {}


merchant_manage_view = MerchantManagement.as_view('merchant_manage')
jj_blueprint.add_url_rule('/merchant_management', view_func=merchant_manage_view,
                          methods=["GET", "PUT", "DELETE", "POST"])
