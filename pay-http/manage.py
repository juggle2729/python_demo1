# coding: utf-8

import os
import signal
import sys
from flask import url_for
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand
from base import app

# 编码设置
reload(sys)
sys.setdefaultencoding('utf-8')

manager = Manager(app)


def make_shell_context():
    """自动加载环境"""
    return dict(
        app=app,
    )


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def run_timer():  # 启动定时器
    from timer.processor import start
    start()

@manager.command
def ban_dead_appid():
    from script.appid_risk_control import _ban_dead_appid
    _ban_dead_appid()


@manager.command
def flush_balance():  # 查询余额
    from script.query_balance import schedule_query_balance
    schedule_query_balance()


@manager.command
def test():
    """run your unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('test')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        line = urllib.unquote(
            "{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print line


if __name__ == '__main__':
    manager.run()
