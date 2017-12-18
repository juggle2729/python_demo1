# -*- coding: utf-8 -*-
from __future__ import absolute_import
import time
import json
import logging
import signal
from multiprocessing import Process, Manager
from cache import redis_cache

from timer import EVENT_ENUM
from timer.notify_handler import NotifySuccessHandler
from utils.tz import now_ts
from utils.pid_file import PIDFile
from utils import EnhencedEncoder

_LOGGER = logging.getLogger('worker')

DEFAULT_EVENT_HANDLERS = {
    EVENT_ENUM.NOTIFY_PAY: NotifySuccessHandler()
}


class EventProcessor(object):
    """
    timer event processor
    """

    def __init__(self, event_type_list):
        self.infinite_process = True
        self.event_type_list = event_type_list
        self.event_handlers = DEFAULT_EVENT_HANDLERS
        self.sleep_second = 5

    @staticmethod
    def pop_expired_events(event_type):
        event_list = []
        try:
            max_time = now_ts()
            value_list = redis_cache.pop_expired_events(event_type, max_time)
            for event_value in value_list:
                event_list.append(event_value)
        except Exception as e:
            _LOGGER.exception('get_expired_events failed.(%s)' % e)

        return event_list

    def process(self, event_type):
        _LOGGER.info("begin processing timer event type: %s",
                     EVENT_ENUM.get_label(event_type))
        event_handler = self.event_handlers.get(event_type)
        if not event_handler:
            _LOGGER.error('event handler not found for %s',
                          EVENT_ENUM.get_label(event_type))
            return

        while self.infinite_process:
            events = self.pop_expired_events(event_type)
            if not events:
                time.sleep(self.sleep_second)

            for event_value in events:
                try:
                    self._process(event_handler, event_type, event_value)
                except Exception as e:
                    _LOGGER.exception('event value invalid.(%s:%s) %s' %
                                  (event_type, event_value, e))

        _LOGGER.info('quit event processor for : %s',
                     EVENT_ENUM.get_label(event_type))

    @staticmethod
    def _process(event_handler, event_type, event_value):
        event_msg = json.loads(event_value)
        success = event_handler.process(event_msg)
        if not success:
            _LOGGER.error("event process error, type: %s, value: %s",
                          event_type, event_msg)
            try_count = event_msg.get('try_count', 0)
            max_try = event_msg.get('max_try')
            if max_try is None or (  # 无限制
                        max_try and try_count < max_try):
                try_count += 1
                # 以2的指数次方退避，最多为1分钟
                interval = min(2 ** try_count, 60)
                next_exec_time = now_ts() + interval
                event_msg['try_count'] = try_count
                msg = json.dumps(event_msg, ensure_ascii=False,
                                 cls=EnhencedEncoder)
                redis_cache.submit_timer_event(event_type, msg, next_exec_time)
            else:
                event_handler.before_abort_callback(event_msg)

    def run(self):
        _LOGGER.info("timer processor run...")
        p_list = []
        for event_type in self.event_type_list:
            p = Process(target=self.process, args=(event_type,))
            p_list.append(p)
            p.start()

        for p in p_list:
            p.join()


def start():
    PIDFile('/tmp/pay-http.pid')
    event_type_list = [k for k in EVENT_ENUM.values()]
    event_processor = EventProcessor(event_type_list)

    def handle_terminate(sig, frame):
        print 'wait to quit...'
        event_processor.infinite_process = False

    signal.signal(signal.SIGTERM, handle_terminate)

    event_processor.run()
