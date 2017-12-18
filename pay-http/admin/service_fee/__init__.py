# coding: utf-8

from flask import Blueprint

fee = Blueprint('fee', __name__)

from . import views
