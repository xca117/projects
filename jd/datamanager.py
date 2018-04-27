#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-30 21:41:28
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$


import redis
import pymongo
import hashlib

from setting import REDISLIST,REDISSET,REDISERROR

class ConnectRedis(object):
    def __init__(self):
        self.r = redis.StrictRedis(host='127.0.0.1',port=6379,decode_responses=True,db=0)
        self.list_name = REDISLIST
        self.set_name = REDISSET
        self.error_name = REDISERROR
        self.error_name_md5 = 'URL_MD5'
        self.md5 = hashlib.md5()
    #数据去重,添加数据到Set
    def add_goods_id(self,value):
        if not self.r.sismember(self.set_name,value) and value!=None:
            self.r.sadd(self.set_name,value)
            return True
        else:
            return False
    #随机取一个值并从Set中移除,添加到list做备份
    def get_goods_id(self):
        result = self.r.spop(self.set_name)
        if result:
            self.r.rpush(self.list_name,result)
        return result
    #保存出错goods_id
    def add_error(self,value):
        if value!=None:
            self.md5.update(value.encode('utf-8'))
            if not self.r.sismember(self.error_name_md5,self.md5.hexdigest()):
                self.r.sadd(self.error_name_md5,self.md5.hexdigest())
                self.r.rpush(self.error_name,value)
            return True
        else:
            return False
    #获得错误URL
    def get_error(self):
        result = self.r.lpop(self.error_name)
        return result


class ConnectMongoDB(object):
    def __init__(self):
        self.connect = pymongo.MongoClient('localhost',27017)
        self.db = self.connect.work_1.jd
    #添加数据
    def insert_data(self,goods_id,price=None,shop_url=None):
        if goods_id:
            self.db.insert({u'商品ID':goods_id,u'商品价格':price,u'店铺网址':shop_url})
    #更新数据并添加新字段--items
    def up_data(self,goods_id,items):
        if goods_id:
            self.db.update({u'商品ID':goods_id},{'$set':items},upsert=True,multi=True)





