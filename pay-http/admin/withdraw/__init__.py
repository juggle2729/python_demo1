# coding: utf-8

from flask import Blueprint

withdraw = Blueprint('withdraw', __name__)

from . import views
