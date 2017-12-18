# coding: utf-8
import os
import logging.config

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager

from base.config import config, config_name
from base.jsonlogger import JsonFormatter

app = Flask(__name__)

login_manager = LoginManager()
login_manager.session_protect = 'strong'
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

app.config.from_object(config[config_name])
toolbar = DebugToolbarExtension(app)
app.url_map.strict_slashes = False  # url 最后一个`/`是可选的
bcrypt = Bcrypt(app)
CORS(app)

from . import middleware
app.before_request(middleware.check_user)
app.after_request(middleware.clean_up)
# blueprints
from api.pay import bp_pay
from admin.auth import auth as auth_blueprint
from admin.bill import bill as bill_blueprint
from admin.jinjian import jinjian as jj_blueprint
from admin.service_fee import fee as fee_blueprint
from admin.withdraw import withdraw as withdraw_blueprint

app.register_blueprint(bp_pay, url_prefix='/api/v1')
app.register_blueprint(auth_blueprint, url_prefix='/admin/auth')
app.register_blueprint(bill_blueprint, url_prefix='/admin/bill')
app.register_blueprint(fee_blueprint, url_prefix='/admin/service')
app.register_blueprint(jj_blueprint, url_prefix='/super_admin/jinjian')
app.register_blueprint(withdraw_blueprint, url_prefix='/admin/withdraw')

# LOG CONFIG
DEBUG = app.debug
LOG_DIR = "/var/log/51paypay/"
LOG_FILE = os.path.join(LOG_DIR, "51paypay.log")
LOG_ERR_FILE = os.path.join(LOG_DIR, "51paypay.err.log")
WORKER_LOG_FILE = os.path.join(LOG_DIR, "worker.log")
WORKER_LOG_ERR_FILE = os.path.join(LOG_DIR, "worker.err.log")
PAY_LOG_FILE = os.path.join(LOG_DIR, "pay.log")
PAY_LOG_ERR_FILE = os.path.join(LOG_DIR, "pay.err.log")
TRACK_LOG = os.path.join(LOG_DIR, 'track.json')
JINJIAN_LOG = os.path.join(LOG_DIR, 'jinjian.log')

if not os.path.exists(app.config.get('EXPORT_PATH')):
    os.mkdir(app.config.get('EXPORT_PATH'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json_stat': {
            '()': JsonFormatter,
            'format': '%(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        'detail': {
            'format': '%(levelname)s %(asctime)s [%(module)s.%(funcName)s line:%(lineno)d] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'formatter': 'simple',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_FILE,
        },
        'pay_file': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'formatter': 'simple',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': PAY_LOG_FILE,
        },
        'worker_file': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'formatter': 'simple',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': WORKER_LOG_FILE,
        },
        'err_file': {
            'level': 'WARN',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_ERR_FILE,
        },
        'worker_err_file': {
            'level': 'WARN',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': WORKER_LOG_ERR_FILE,
        },
        'pay_err_file': {
            'level': 'WARN',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': PAY_LOG_ERR_FILE,
        },
        'track_file': {
            'level': 'INFO',
            'formatter': 'json_stat',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': TRACK_LOG
        },
        'jinjian_file': {
            'level': 'INFO',
            'formatter': 'simple',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': JINJIAN_LOG
        },
    },
    'loggers': {
        'crazy': {
            'handlers': ['console', 'file', 'err_file'] if DEBUG else ['file', 'err_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'worker': {
            'handlers': ['console', 'worker_file', 'worker_err_file'] if DEBUG else ['worker_file', 'worker_err_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'timer': {
            'handlers': ['console', 'worker_file', 'worker_err_file'] if DEBUG else ['worker_file', 'worker_err_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'pay': {
            'handlers': ['console', 'pay_file', 'pay_err_file'] if DEBUG else ['pay_file', 'pay_err_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'tracker': {
            'handlers': ['track_file'],
            'level': 'INFO',
            'propagate': False
        },
        'jinjian': {
            'handlers': ['jinjian_file'],
            'level': 'INFO',
            'propagate': False
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file', 'err_file'] if DEBUG else ['file', 'err_file']
    }
}

logging.config.dictConfig(LOGGING)
