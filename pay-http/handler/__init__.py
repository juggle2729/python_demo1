# -*- coding: utf-8 -*-
"""
逻辑处理层，部分操作需要同时处理cache和db
一般先更新db，再更新cache
API从cache中取数据；推送消息通过cache完成；
"""