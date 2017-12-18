# -*- coding: utf-8 -*-
import json
import logging

from timer import EventHandler, EVENT_ENUM
from utils import tz
from handler.pay import notify_success

_LOGGER = logging.getLogger('worker')
_TRACKER = logging.getLogger('tracker')


class NotifySuccessHandler(EventHandler):
    def _process(self, event_msg):
        _LOGGER.info('start processing notify')
        payid = event_msg['payid']
        notify_success(payid)
        return True

    def process(self, event):
        try:
            return self._process(event)
        except Exception as e:
            _LOGGER.exception(e)
            return False
