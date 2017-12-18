# -*- coding: utf-8 -*-


class Enum(object):
    '''
    An enum type used in django convenience.

    >>> from enum import Enum
    >>> e = Enum({"ONE":(1,"One")})
    >>> print e.ONE
    1
    >>> print e.to_choices()
    ((1, 'One'),)
    >>> print e.to_dict()
    {1: 'One'}
    >>> print e.get_label(1)
    One
    >>> print e.get_key(1)
    ONE
    '''

    def __init__(self, mapping):
        self._DATA_MAPPING = mapping
        self.value_list = []
        for v in mapping.values():
            self.value_list.append(v[0])
        self.value_dct = {}
        self.label_dct = {}
        self.key_dct = {}
        for k, v in self._DATA_MAPPING.iteritems():
            self.value_dct[v[0]] = v[1]
            self.label_dct[v[1]] = v[0]
            self.key_dct[v[0]] = k

    def values(self):
        return self.value_list

    def __getattr__(self, name):
        if name in self._DATA_MAPPING:
            return self._DATA_MAPPING[name][0]
        raise AttributeError('%s not exist' % name)

    def to_choices(self):
        return self._DATA_MAPPING.values()

    def to_dict(self):
        return self.value_dct

    def get_label(self, value):
        return self.value_dct.get(value)

    def get_key(self, value):
        return self.key_dct.get(value)

    def get_value(self, label):
        return self.label_dct.get(label)
