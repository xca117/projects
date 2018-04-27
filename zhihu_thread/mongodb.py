#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-02-24 22:58:17
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$

'''mongodb存储最终数据'''
import pymongo
import redisdb

client = pymongo.MongoClient('127.0.0.1',27017)
db = client.zhihudb
data = db.data  # 集合名


def main():
	up_data = redisdb.up_data(SET_KEY_NAME)
		for url_token in up_data:
			data.insert({'url_token':url_token})

mai()



