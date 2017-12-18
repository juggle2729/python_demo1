# -*- coding: utf-8 -*-

from utils import tz


class BaseModel(dict):
    structure = {}
    default_fields = {}
    required_fields = []

    def __init__(self, d=None):
        if d:
            self.set_fromdict(d)
        for k, v in self.default_fields.iteritems():
            if k not in self:
                self[k] = v

    def __getattr__(self, name):
        return self[name] if name in self else None

    def __setattr__(self, name, value):
        if name in self.structure:
            t = self.structure[name]
            if value is None:
                self[name] = None
            elif isinstance(t, type) or issubclass(t, BaseModel):
                # 如果是一个类型或者是一个model，最常见的情况
                # 如果内嵌的model已经校验过了，t直接写`dict`而不是具体的model类
                if t is basestring:
                    t = unicode
                self[name] = t(value)
            elif isinstance(t, list):
                # 约定list内部是同构的model，如果已经校验过，t应该直接写`list`
                if not isinstance(value, list):
                    raise AttributeError('%s should be a list' % name)
                model = t[0]
                data = []
                for v in value:
                    data.append(model(v))
                self[name] = data
            else:
                # 其他情况下，直接赋值，不做校验
                self[name] = value
        else:
            raise AttributeError('%s not in structure' % name)

    def __delattr__(self, name):
        del self[name]

    def set_fromdict(self, d):
        for k, v in d.iteritems():
            if k in self.structure:
                t = self.structure[k]
                if t is basestring:
                    t = unicode
                if k.endswith('_at'):    # 如果是时间，转换成北京时间，并去除时区信息
                    v = tz.utc_to_local(v).replace(tzinfo=None)
                self[k] = t(v) if v is not None else None

    def valid(self):
        """可以考虑在DEBUG模式下，在response_wrapper里面判断返回类型作校验，
           不宜在生产环境下使用
        """
        for field in self.required_fields:
            if field not in self:
                raise ValueError('miss required field %s' % field)
