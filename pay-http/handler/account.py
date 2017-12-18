# -*- coding: utf-8 -*-

from cache import account as cache
from db.account import controller as db


def get_account_info(user_id):
    resp = cache.get_account(user_id)
    if not resp:
        resp = db.get_account(user_id)
        if not resp:
            return None
        else:
            resp = resp.as_dict()
            cache.update_account(user_id, resp)
    return resp