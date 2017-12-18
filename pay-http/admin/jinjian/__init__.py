# coding: utf-8

from flask import Blueprint


jinjian = Blueprint('jinjian',
                    __name__,
                    template_folder="templates/",
                    static_url_path='/data',
                    static_folder="/home/ubuntu/flask-env/data/images")

from . import views
