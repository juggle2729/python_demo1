# -*- coding: utf-8 -*-
"""
一个根据时间戳执行的简易定时器，可以用celery代替
"""
from abc import ABCMeta, abstractmethod
import json
import logging

from future.utils import raise_with_traceback

from utils.types import Enum
from cache import redis_cache
from utils import id_generator
from utils.err import DataError
from utils import EnhencedEncoder

_LOGGER = logging.getLogger(__name__)


EVENT_ENUM = Enum({
    'NOTIFY_PAY': (1, u"异步通知支付结果")
})

SINGLETON_EVENT = {EVENT_ENUM.NOTIFY_PAY}       # 单例事件


class TimerEvent(object):
    """Timer event wrapper
    """

    def __init__(self, event_type, event_value, timestamp):
        self.event_type = event_type
        # must be a json dict, like {'id': xxxx, 'msg': xxxx}
        self.event_value = event_value
        self.timestamp = timestamp

    @classmethod
    def submit(cls, event_type, event_msg, timestamp, max_try=None):
        # construct event_value dict
        uuid = id_generator.generate_uuid()
        event_value = {
            'id': uuid,
            'msg': event_msg,
            'max_try': max_try,
        }
        try:
            cache_value = json.dumps(event_value, cls=EnhencedEncoder,
                                     ensure_ascii=False)
            if event_type in SINGLETON_EVENT:    # 单例事件，永远应该只有一例
                redis_cache.replace_timer_event(event_type, cache_value, timestamp)
            else:
                redis_cache.submit_timer_event(event_type, cache_value, timestamp)
        except Exception as e:
            _LOGGER.error('timer event submit error.(%s)' % e)
            raise_with_traceback(DataError(e))

        return uuid


class EventHandler(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, event):
        """处理过程"""
        pass

    def before_abort_callback(self, event_msg):
        """如果事件被抛弃，回调此方法, event_msg是dict"""
        _LOGGER.error("abort event after try: %s", event_msg)
