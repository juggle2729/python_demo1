# coding: utf-8

# project base path
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

"""
 -- SECRET_KEY: secret key
 -- SQLALCHEMY_COMMIT_ON_TEARDOWN: True

 -- SQLALCHEMY_RECORD_QUERIES:
    -- Can be used to explicitly disable or enable query recording.
       Query recording automatically happens in debug or testing mode.

 -- SQLALCHEMY_TRACK_MODIFICATIONS:
    -- If set to True, Flask-SQLAlchemy will track modifications of
       objects and emit signals.
       The default is None, which enables tracking but issues a warning that
       it will be disabled by default in the future.
       This requires extra memory and should be disabled if not needed.

 more configuration keys please see:
  -- http://flask-sqlalchemy.pocoo.org/2.1/config/#configuration-keys
"""


class Config(object):
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = "ItDdCt3!LIprNCFfdJy$sa5^MT!u5AvlHvrFxTmw@eWL1gVI1kpzJ1qQaMx$!hPz"
    DEBUG = True
    TESTING = True
    SERVICE_ID = 1
    INTERNAL_IPS = []
    WTF_CSRF_ENABLED = False

    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379

    MONGO_ADDR = '127.0.0.1'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/51paypay?charset=utf8mb4'

    CELERY_BROKER_URL = 'redis://localhost:6379/3'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/3'

    QINIU_DOMAIN = 'omwce852u.bkt.clouddn.com'
    QINIU_BUCKET = 'football-test'
    QINIU_BUCKET_ICON = 'crazyguess'
    QINIU_ACCESS_KEY = 'ZDhfyc8ntcFvk0rR12SbjOoseIOOFtrgnG8alFO6'
    QINIU_SECERET_KEY = 'GOMx9wf7LGlBA0peX3I8cG66H0hPvMYnuIGV-nNQ'

    WECHAT_APPID = 'wxb5d2f47686d6c180'
    WECHAT_SECRET = '17982f2f183905082c0c115faa049922'
    JSAPI_URL = 'http://www.luckyball-guess.com/'

    WS_HOST = 'http://172.16.1.58:9000/ws'
    TIANHONG_NOTIFY_URL = 'http://120.24.253.152/api/v1/third/pay/tianhong/notify/'
    IOS_CHECK_URL = 'https://sandbox.itunes.apple.com/verifyReceipt'
    EXPORT_PATH = '/tmp/export_data'


class TestingConfig(Config):
    """testing configuration"""
    DEBUG = True
    TESTING = True


# production configuration
class ProductionConfig(Config):
    """production configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mysql://pay:payme_pas@172.16.144.203:3306/51paypay?charset=utf8mb4'
    REDIS_HOST = '172.16.144.203'
    REDIS_PORT = 6379
    MONGO_ADDR = '172.16.144.203'


    IOS_CHECK_URL = 'https://buy.itunes.apple.com/verifyReceipt'
    # QINIU_DOMAIN = 'oow63f0nd.bkt.clouddn.com'
    # QINIU_BUCKET = 'crazyguess'


config = {
    "test": TestingConfig,
    "prod": ProductionConfig,
    "default": Config,
}

config_name = 'default'
config_name='prod'
