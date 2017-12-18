import json
import decimal
from datetime import datetime


class EnhencedEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, datetime):
            return o.isoformat(' ')
        return super(EnhencedEncoder, self).default(o)


def to_json(info):
    return json.dumps(info, cls=EnhencedEncoder, ensure_ascii=False)