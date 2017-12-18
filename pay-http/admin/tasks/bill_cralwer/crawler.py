# coding: utf-8

import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))))

from admin import create_app
from db.bill.model import Bill
import query


def update_account_bill(delta=0):
    result = query.query_bill(delta)
    print(result)
    if not result:
        return

    for r in result:
        r = r.split(',')
        bill = Bill()
        bill.fill(r)
        custID = CustomID.query.filter(CustomID.custID == bill.channel_flag).first()
        if not custID:
            print('%r not belong to any registered user' % bill)
            return
        bill.belonged_account = custID.account
        bill.save()


if __name__ == '__main__':
    delta = 0
    app = create_app('default')
    if len(sys.argv) > 1:
        delta = int(sys.argv[1])
    with app.app_context():
        update_account_bill(delta)
