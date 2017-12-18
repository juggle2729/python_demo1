# -*- coding: utf-8 -*-
import logging

from qiniu import Auth, BucketManager, build_batch_delete

from base import app

_LOGGER = logging.getLogger(__name__)
EXPIRE_TIME = 3600  # 1 hour

Q = Auth(app.config.get('QINIU_ACCESS_KEY'),
         app.config.get('QINIU_SECERET_KEY'))


def generate_token():
    token = Q.upload_token(app.config.get('QINIU_BUCKET'), expires=EXPIRE_TIME)

    return token


def delete_data_by_url(urls, bucket=app.config.get('QINIU_BUCKET'),
                       key_prefix=''):
    keys = []
    for url in urls:
        if not url.endswith('/'):
            url += '/'
        key = url.split('/')[-2]
        if key_prefix:
            key = '%s/%s' % (key_prefix, key)
        keys.append(key)
    delete_data_by_key(keys, bucket)


def delete_data_by_key(keys, bucket):
    ops = build_batch_delete(bucket, keys)
    b = BucketManager(Q)
    b.batch(ops)
