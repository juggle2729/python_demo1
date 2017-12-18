# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient

from base import app
from utils import tz
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
cors = CORS()

orm = SQLAlchemy(app, session_options={
    "autocommit": False,
    "autoflush": False,
    "expire_on_commit": False,
})

mg = MongoClient(app.config.get('MONGO_ADDR')).crazy


class TimeColumnMixin(orm.Model):
    __abstract__ = True

    created_at = orm.Column(orm.DateTime, default=orm.func.now(),
                            nullable=False)
    updated_at = orm.Column(orm.DateTime, default=orm.func.now(),
                            nullable=False, onupdate=orm.func.now())


class BaseModel(orm.Model):
    __abstract__ = True

    def save(self, auto_commit=True):
        orm.session.add(self)
        if auto_commit:
            orm.session.commit()

    def merge(self, auto_commit=True):
        orm.session.merge(self)
        if auto_commit:
            orm.session.commit()

    def as_dict(self, convert_time=False):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if convert_time:
            for k in data:
                if k.endswith('_at'):
                    data[k] = tz.utc_to_local_str(data[k])

        return data

    @classmethod
    def generate_from_dict(cls, data):
        inst = cls()
        for k, v in data.iteritems():
            if k in cls.__table__.columns and k not in (
                    'updated_at', 'created_at'):
                setattr(inst, k, v)
        return inst
