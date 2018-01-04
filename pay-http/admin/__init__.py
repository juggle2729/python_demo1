# coding: utf-8

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

bcrypt = Bcrypt()
orm = SQLAlchemy()
cors = CORS()
login_manager = LoginManager()
login_manager.session_protect = 'strong'
login_manager.login_view = 'auth.login'

from admin.auth import auth as auth_blueprint
from admin.bill import bill as bill_blueprint
from admin.jinjian import jinjian as jinjian_blueprint
from admin.service_fee import fee as service_blueprint
from admin.withdraw import withdraw as withdraw_blueprint
from admin.daifu import daifu as daifu_blueprint
from base.config import config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    bcrypt.init_app(app)
    orm.init_app(app)
    cors.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_blueprint, url_prefix='/admin/auth')
    app.register_blueprint(bill_blueprint, url_prefix='/admin/bill')
    app.register_blueprint(jinjian_blueprint, url_prefix='/admin/jinjian')
    app.register_blueprint(withdraw_blueprint, url_prefix='/admin/withdraw')
    app.register_blueprint(daifu_blueprint, url_prefix='/admin/daifu')
    app.register_blueprint(service_blueprint, url_prefix='/admin/service_fee')
    app.register_blueprint(service_blueprint, url_prefix='/admin/withdraw')
    return app
