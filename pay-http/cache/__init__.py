# -*- coding: utf-8 -*-
import redis
import logging

from base import app

_LOGGER = logging.getLogger(__name__)

_MAX_TRY_COUNT = 3
_REDIS_KEY_PREFIX = '51paypay'

cache = redis.StrictRedis(host=app.config.get('REDIS_HOST'),
                          port=app.config.get('REDIS_PORT'))


def prefix_key(key, prefix=_REDIS_KEY_PREFIX):
    return '%s:%s' % (prefix, key)
