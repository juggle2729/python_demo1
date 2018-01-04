# coding: utf-8

from flask import Blueprint

daifu = Blueprint('daifu', __name__)

from . import views
