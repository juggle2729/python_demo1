# -*- coding: utf-8 -*-
from os import path

from uuid import uuid4
import pandas as pd

from base import app


def redirect_to_file(items, header, filename, index='ID'):
    dir = app.config.get('EXPORT_PATH', '/tmp/')
    file_path = path.join(dir, filename)
    data = pd.DataFrame.from_records(items, columns=header, index=index)
    data.to_excel(file_path)
    return {'url': '/export_data/%s' % filename}


def gen_filename(base):
    qs = base + '_' + str(uuid4())
    return qs + '.xlsx'
