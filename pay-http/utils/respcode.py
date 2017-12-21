# -*- coding: utf-8 -*-

from utils.types import Enum


class HttpCode(object):
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    PARTIAL_CONTENT = 206
    NOT_MODIFIED = 304
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    EXPECTATION_FAILED = 417
    SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501


StatusCode = Enum({
    "OK": (0, ""),
    "UNKNOWN_ERROR": (1, u"未知错误"),
    "PARAM_REQUIRED": (2, u"缺少参数"),
    "HTTPS_REQUIRED": (3, u"需要使用HTTPS"),
    "DATA_ERROR": (4, u"数据错误"),
    "DB_ERROR": (5, u"数据库错误"),
    "CACHE_ERROR": (6, u"缓存错误"),
    # user related
    "INVALID_USER": (101, u"用户不存在"),
    "WRONG_PASSWORD": (102, u"密码错误"),
    "WRONG_AUTH_CODE": (103, u"验证码错误"),
    "DUPLICATE_ACCOUNT": (104, u"账户已存在"),
    "INVALID_TOKEN": (105, u"TOKEN失效"),
    "NOT_ALLOWED": (106, u"权限不足"),
    "DUPLICATE_PHONE": (107, u"手机号已存在"),
    "INVALID_OTP": (109, u"动态密码验证不通过"),
    # third party component
    "SMS_PLATFORM_ERROR": (108, u"短信平台错误"),
    "PINGXX_PLATFORM_ERROR": (130, u"ping++ 平台错误"),

    "RESOURCE_INSUFFICIENT": (201, u"资源不足"),
    "BALANCE_INSUFFICIENT": (202, u"余额不足"),
    "TERM_EXPIRED": (203, u"期限已过"),

    "REACH_LIMIT": (301, u"达到限制"),
})

StatusCodeDict = StatusCode.to_dict()
