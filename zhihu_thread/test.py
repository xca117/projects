#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import random
from selenium import webdriver

#执行selenium 获得完整cookie
# def getcookies(url):
#     driver=webdriver.Firefox()
#     driver.get(url)
#     return driver.get_cookies()

# url = 'https://item.jd.com/10113060794.html#comment'
# print(getcookies(url))

import re
import json
import pymongo

import requests
from setting import *

# url = 'https://search.jd.com/Search?keyword=%E5%AD%95%E5%A6%87%E8%A3%85&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E5%AD%95%E5%A6%87%E8%A3%85&psort=3&stock=1&page=1&s=26&click=0'
# cookies = getcookies(url)
# r = requests.get(url,cookies=cookies)
# print(r.text)
print(REDISLIST)

