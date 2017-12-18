# -*- coding: utf-8 -*-
from utils.respcode import HttpCode, StatusCode


# Basic Exceptions
class Error(Exception):
    HTTPCODE = HttpCode.SERVER_ERROR
    STATUS = StatusCode.UNKNOWN_ERROR

    def __init__(self, msg='', httpcode=None, status=None):
        super(Error, self).__init__(msg)
        if httpcode:
            self.HTTPCODE = httpcode
        if status:
            self.STATUS = status


class PayApiError(Error):
    HTTPCODE = 200
    MSG = u"未知错误"


class InsufficientFunds(PayApiError):
    STATUS = 101
    MSG = u"服务费余额不足"


class SignWrongError(PayApiError):
    STATUS = 102
    MSG = u"签名错误"


class DuplicateOrderID(PayApiError):
    STATUS = 103
    MSG = u"订单号重复"


class NoOrderID(PayApiError):
    STATUS = 104
    MSG = u"没有对应的订单号信息"


class AppIDWrong(PayApiError):
    STATUS = 105
    MSG = u"无效appid或payType"


class PayTypeNotSupport(PayApiError):
    STATUS = 106
    MSG = u"不支持的支付方式"


class MiniAmount(PayApiError):
    STATUS = 107
    MSG = u"最低支付1元"


class RequestParamError(PayApiError):
    STATUS = 108
    MSG = u"请求参数错误"


class OnlyD0SupportWithdraw(PayApiError):
    STATUS = 109
    MSG = u"只有D0通道支持提现接口"


class SystemError(PayApiError):
    STATUS = -1
    MSG = u"未知错误"


class ClientError(Error):
    HTTPCODE = HttpCode.BAD_REQUEST


class ServerError(Error):
    pass


class ThirdPartyError(ServerError):
    pass


class WechatError(ThirdPartyError):
    pass


class PingXXError(ThirdPartyError):
    STATUS = StatusCode.PINGXX_PLATFORM_ERROR


# General Exceptions


class ParamError(ClientError):
    STATUS = StatusCode.PARAM_REQUIRED


class DataError(ClientError):
    STATUS = StatusCode.DATA_ERROR


class Issue(ClientError):      # --> Issue给客户端一个重复entity的提示
    STATUS = StatusCode.DATA_ERROR
    HTTPCODE = 200


class DbError(ServerError):
    STATUS = StatusCode.DB_ERROR


class CacheError(ServerError):
    STATUS = StatusCode.CACHE_ERROR


# Specific Exception
class ProtocolError(ClientError):
    HTTPCODE = HttpCode.FORBIDDEN
    STATUS = StatusCode.HTTPS_REQUIRED


class SmsPlatformError(ServerError):
    STATUS = StatusCode.SMS_PLATFORM_ERROR


class AuthenticateError(DataError):
    HTTPCODE = HttpCode.UNAUTHORIZED


class PermissionError(ClientError):
    STATUS = StatusCode.NOT_ALLOWED
    HTTPCODE = HttpCode.FORBIDDEN


class NotImplementedError(ServerError):
    HTTPCODE = HttpCode.NOT_IMPLEMENTED


class ResourceInsufficient(ClientError):
    HTTPCODE = HttpCode.FORBIDDEN
    STATUS = StatusCode.RESOURCE_INSUFFICIENT


class ResourceNotFound(ClientError):
    HTTPCODE = HttpCode.NOT_FOUND


class ResourceNotModified(ClientError):
    HTTPCODE = HttpCode.NOT_MODIFIED


class BalanceInsufficient(ClientError):
    STATUS = StatusCode.BALANCE_INSUFFICIENT


class TermExpired(ClientError):
    STATUS = StatusCode.TERM_EXPIRED


class ReachLimit(ClientError):
    STATUS = StatusCode.REACH_LIMIT
