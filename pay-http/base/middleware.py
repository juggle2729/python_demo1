# -*- coding: utf-8 -*-
from flask import request
from flask import g, jsonify, make_response

from db import orm
#from db.account.model import ACCOUNT_STATUS
from db.account import controller as admin_db
from db.account.model import UserToken
from utils.err import PermissionError


def check_perm(url_array, perm, role):
    l = len(url_array)
    while l >= 1:
        url = '/'.join(url_array[0:l])
        if not url.endswith('/'):
            url += '/'
        k = admin_db.get_perm(url, perm)
        if k and str(role) in k.roles.split(','):
            return True
        l -= 1
    return False


def check_user():
    user_id, token = request.headers.get(
        'X-AUTH-USER'), request.headers.get('X-AUTH-TOKEN')
    if not user_id and request.is_xhr:
        user_id, token = request.cookies.get('auth_user'), request.cookies.get(
            'auth_token')
    if user_id and token:
        try:
            user_id = long(user_id)
        except ValueError:
            return
        if request.path.startswith('/api'):  # service api
            pass
            #user = account.get_account_info(user_id)
            #if not user or user['status'] == ACCOUNT_STATUS.BANNED:
            #    return
            #info = AccountToken.query.filter(
            #    AccountToken.user_id == user_id).filter(
            #    AccountToken.token == token).filter(
            #    AccountToken.deleted == 0).first()
            #if info:
            #    g.user = usert
        else:                               # admin api
            info = admin_db.get_online_info(user_id, token)
            if info and info.deleted == 0:
                user = admin_db.get_user(user_id)
                g.user = user.as_dict()
                return
                #if user.role > 0:
                #    if user.role == admin_db.ROLE.ADMIN:
                #        g.user = user.as_dict()
                #        return
                #    url_array = request.path.split('/')
                #    if request.method == 'GET':
                #        need_perm = admin_db.PERMISSION.READ
                #    else:
                #        need_perm = admin_db.PERMISSION.WRITE
                #    if not check_perm(url_array, need_perm, user.role):
                #        return make_response(jsonify({
                #            'status': PermissionError.STATUS,
                #            'msg': 'permission not enough'
                #        }), PermissionError.HTTPCODE)
                #    else:
                #        g.user = user.as_dict()
                #        return
                #else:
                #    return make_response(jsonify({
                #        'status': PermissionError.STATUS,
                #        'msg': 'user is forbidden or not activited'
                #    }), PermissionError.HTTPCODE)


def clean_up(resp):
    orm.session.close()
    return resp
