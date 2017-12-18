# -*- coding: utf-8 -*-
import logging
from functools import partial

from future.utils import raise_with_traceback
from sqlalchemy.exc import SQLAlchemyError
from redis import RedisError

from utils import err
from db import orm

_LOGGER = logging.getLogger(__name__)


def common_sql_wrapper(db):
    def handler(func):
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except SQLAlchemyError as e:
                raise_with_traceback(err.DbError(e))
            except err.Error:
                raise
            except Exception as e:
                raise_with_traceback(e)
            finally:
                db.session.rollback()
                # db.session.close()  # 在request之后关闭session，加上hook
        return _wrapper
    return handler


sql_wrapper = partial(common_sql_wrapper(db=orm))
# slave_wrapper = partial(common_sql_wrapper(orm=slave))


def cache_wrapper(func):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RedisError as e:
            raise_with_traceback(err.CacheError(e))
        except err.Error:
            raise
        except Exception as e:
            raise_with_traceback(e)

    return _wrapper
