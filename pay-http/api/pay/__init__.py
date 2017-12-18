# -*- coding: utf-8 -*-

from flask import Blueprint

bp_pay = Blueprint('pay', __name__)

from api.pay import view
