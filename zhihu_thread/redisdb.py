#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-02-03 00:40:35
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$


import redis


r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True, db=0)

'''添加redis list数据'''
def add_list(key_name,value):
	if key_name !=None and value != None:
		r.rpush(key_name, value)
		return True
	else: return False
'''提取redis list数据'''
def extract_data(key_name):
	if key_name:
		if r.llen(key_name) > 0:
			user = r.lpop(key_name)
			return user
		else: return None 

'''检查redis set 数据是否已存在,无则存入并返回True'''
def check_add(key_name,value):
	if not r.sismember(key_name,value):
		r.sadd(key_name, value)
		return True
	else: return False

def up_data(self):
	for item in r.hscan_iter(key_name):
		yield item

