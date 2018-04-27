#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-06 07:29:12
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$

import requests

PROXY_POOL_URL = 'http://localhost:5000/get'

def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None
