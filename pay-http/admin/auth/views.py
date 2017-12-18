# coding: utf-8
import random
import json
import logging

from flask import request, Response, g
from flask.views import MethodView
# from flask_login import login_user, logout_user
from flask_login import login_required, current_user
from admin.auth import auth
from db.account.model import Account
from db.account.controller import get_account_appid, login_user, logout_user, get_user_by_phone, register_user, \
    create_app_manage, create_bankcard_info, delete_bankcard_info
from db.pay_record.controller import get_child_appids
from admin.auth.image_codes import IMAGE_CODES
from utils.sms import send_sms_code
from utils.api import response_wrapper, token_required, get_client_ip
from utils import err
from utils.respcode import StatusCode
from .controller import send_auth_code, check_auth_code, get_app_manage, get_bankcard_info
from .acc_info import ACCINFO
from cache.redis_cache import (
    get_sms_sended_cache, get_sms_cache, set_sms_sended_cache, set_sms_cache, cache_id_code, get_cache_code,
    get_auth_code)

_LOGGER = logging.getLogger('51paypay')


def verify_user(phone, passwd):
    account = Account.query.filter(Account.phone == phone).first()
    if not account:
        return False

    if account.verify_passwd(passwd):
        login_user(account)
        return True
    else:
        return False


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def strip_phone(phone_number):
    phone_number = str(phone_number)
    prefix_list = ['62', '0', '620', '062']
    for prefix in prefix_list:
        phone_number = remove_prefix(phone_number, prefix)
    return phone_number


def get_id_code():
    import random
    id = request.args.get('id', 'fuck')
    code = random.choice(IMAGE_CODES)
    cache_id_code(id, code)
    image = file('image/codes/%s.png' % code)
    return Response(image, mimetype='image/png')


def pre_forget():
    phone = request.form.get('userinfo', '')
    code = request.form.get('code', '')
    id = request.form.get('id', 'fuck')
    print(phone)
    print(code)
    print(id)
    cache_code = get_cache_code(id)
    if cache_code.lower() != code.lower():
        return 'CodeFail'

    account = Account.query.filter(Account.phone == phone).first()
    if not account:
        return u'AccountFail'

    set_sms_cache(phone)
    return 'success'


def get_smscode():
    phone = request.args.get('phone', '')
    print('get_smscode', phone)
    if not get_sms_cache(phone):
        return '{"status":1, "msg": "Follow the rule Please!"}'

    # verify phone again
    account = Account.query.filter(Account.phone == phone).first()
    if not account:
        return '{"status":1, "msg": "AccountNotExist"}'

    if get_sms_sended_cache(phone):
        return '{"status":1, "msg": "SMSCodeAlreadySent"}'

    def gen_sms_code(length=4):
        start = 10 ** 4
        stop = 10 ** (length + 1)
        return str(random.randrange(start, stop))

    sms_code = gen_sms_code()
    set_sms_cache(phone, sms_code)
    try:
        send_sms_code(phone, sms_code)
        set_sms_sended_cache(phone)
    except:
        pass

    return '{"status":0}'


@response_wrapper
def doforget():
    phone = request.form.get('phone', '')
    passwd = request.form.get('passwd', '')
    code = request.form.get('code', '')
    _LOGGER.info('forget password: %s, %s, %s', phone, passwd, code)
    cached_code = get_auth_code(phone)
    _LOGGER.info('cached_code;%s, post_code:%s' % (cached_code, code))
    if not cached_code or cached_code != code:
        return {"status": 1, "msg": "WrongCode"}

    # verify phone again
    account = Account.query.filter(Account.phone == phone).first()
    if not account:
        return {"status": 1, "msg": "AccountNotExist"}

    # verify passwd
    def check_simple_passwd(passwd):
        return True

    if not check_simple_passwd(passwd):
        return {"status": 1, "msg": "PasswdTooSimple"}

    account.password = passwd
    account.save()
    return {"status": 0}


def logout():
    logout_user()


@response_wrapper
@token_required
def get_appids():
    infos = get_child_appids(g.user['id'])
    appids = [info.appid for info in infos]
    appids = list(set(appids))
    return appids


@response_wrapper
@token_required
def get_appid_mchnames():
    infos = get_child_appids(g.user['id'])
    appid_mchids = {
        info.appid:
            {'accountid': info.accountid,
             'mch_name': info.mch_name
             }
        for info in infos}
    appids = appid_mchids.keys()
    sorted(appids)

    appid_mchnames = []
    for appid in appids:
        mch_name = ACCINFO.get(appid_mchids[appid]['accountid'], {}).get('mchname', '')
        if not mch_name:  # 代理商下的子商户如果没有注册,就不在ACCINFO里
            mch_name = appid_mchids[appid]['mch_name']
        appid_mchnames.append('%s-%s' % (appid, mch_name))
    return [appids, appid_mchnames]


@response_wrapper
def login():
    phone = request.form.get('userinfo', '')
    passwd = request.form.get('password', '')
    return login_user(phone, passwd)


@response_wrapper
def register():
    phone = request.form.get('phone', '')
    code = request.form.get('code', '')
    passwd = request.form.get('passwd', '')
    is_right = check_auth_code(phone, code)
    if is_right:
        register_user(phone, passwd)
        return {}
    else:
        raise err.AuthenticateError(status=StatusCode.WRONG_AUTH_CODE)


@response_wrapper
@token_required
def accinfo():
    user_id = g.user['id']
    return ACCINFO.get(user_id, {})


class AuthCodeView(MethodView):
    @response_wrapper
    def get(self):
        """ send auth_code sms to client.
            required: phone num

            response: {}
        """
        phone = request.args.get('phone', '')
        use = request.args.get('use', '')
        phone = strip_phone(phone)
        exists = True if get_user_by_phone(phone) else False
        # if query_dct['use'] == 'changepwd' and not exists:
        #    raise err.DataError(status=StatusCode.INVALID_USER)
        if use == 'register' and exists:  # in some case, user can register and not set password
            raise err.DataError(status=StatusCode.DUPLICATE_ACCOUNT)
        # if query_dct['use'] == 'changephone' and exists:
        #    raise err.DataError(status=StatusCode.DUPLICATE_ACCOUNT)
        # if query_dct['use'] == 'third_bind' and exists:
        #    raise err.DataError(status=StatusCode.DUPLICATE_ACCOUNT)
        ip = get_client_ip()
        send_auth_code(phone, ip=ip)
        return {}

    @response_wrapper
    def post(self):
        """ check client input auth code
            required: phone, auth_code

            response: {} or error
        """
        phone = request.form.get('phone', '')
        auth_code = request.form.get('auth_code', '')
        phone_num = strip_phone(phone)
        is_right = check_auth_code(phone, auth_code)
        if is_right:
            return {}
        else:
            raise err.AuthenticateError(status=StatusCode.WRONG_AUTH_CODE)

class BankCardView(MethodView):
    @response_wrapper
    @token_required
    def get(self):

        account_id = g.user['id']
        return get_bankcard_info(account_id)

    @response_wrapper
    @token_required
    def post(self):
        """ required: 

            response: {} or error
        """
        card_name = request.form.get('card_name', '')
        bank_name = request.form.get('bank_name', '')
        card_number = request.form.get('card_number', '')
        subbank_name = request.form.get('subbank_name', '')
        card_type = int(request.form.get('card_type', 0))
        extend = request.form.get('extend', '')
        if not card_name or not bank_name or not card_number or not subbank_name:
            raise err.ParamError('missing arguments')
       
        account_id = g.user['id']
        data = {
            'accountid': account_id,
            'card_name': card_name, 
            'bank_name': bank_name,
            'subbank_name': subbank_name,
            'card_number': card_number,
            'card_type': card_type,
            'extend': extend
        }
        create_bankcard_info(account_id, data)
        return {}

    @response_wrapper
    @token_required
    def delete(self):
        account_id = g.user['id']
        delete_bankcard_info(account_id)
        return {}

class AppManageView(MethodView):
    @response_wrapper
    @token_required
    def get(self):

        account_id = g.user['id']
        app_type = request.args.get('type')
        valid = request.args.get('status')
        appname = request.args.get('name')
        appid = request.args.get('appid')
        page = request.args.get('page', 1)
        page = int(page)
        size = request.args.get('size', 10)
        size = int(size)
        return get_app_manage(account_id, appid, app_type, valid, appname, page, size)

    @response_wrapper
    @token_required
    def post(self):
        """ check client input auth code
            required: phone, auth_code

            response: {} or error
        """
        appname = request.form.get('name', '')
        app_type = request.form.get('app_type', '')
        pay_type = request.form.get('pay_type', '')
        try:
            pay_type = json.loads(pay_type)
        except Exception as e:
            raise err.ParamError('pay_type')
        account_id = g.user['id']
        create_app_manage(appname, app_type, pay_type, account_id)
        return {}


auth.add_url_rule('/appmanage', view_func=AppManageView.as_view('appmanage'))
auth.add_url_rule('/bankcard', view_func=BankCardView.as_view('bankcard'))
auth.add_url_rule('/get-id-code', view_func=get_id_code, methods=['GET'])
auth.add_url_rule('/account/preforget', view_func=pre_forget, methods=['POST'])
auth.add_url_rule('/account/smscode', view_func=get_smscode, methods=['GET'])
auth.add_url_rule('/account/doforget', view_func=doforget, methods=['POST'])
auth.add_url_rule('/logout', view_func=logout, methods=['GET'])
auth.add_url_rule('/authcodes', view_func=AuthCodeView.as_view('authcode'))
auth.add_url_rule('/appids', view_func=get_appids, methods=['GET'])
auth.add_url_rule('/login', view_func=login, methods=['POST'])
auth.add_url_rule('/register', view_func=register, methods=['POST'])
auth.add_url_rule('/info', view_func=accinfo, methods=['GET'])
auth.add_url_rule('/appid_mchnames', view_func=get_appid_mchnames, methods=['GET'])
