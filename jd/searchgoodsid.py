#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-06 07:42:15
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$


import requests
import time
import threading
import re
import random

from setting import USERAGENT,PSORT,getcookies,getproxies
from datamanager import ConnectRedis
from datamanager import ConnectMongoDB

redis = ConnectRedis()
mongodb = ConnectMongoDB()

'''
大概流程:
1.请求网页上半部分获得商品数据及下半部分所需参数args
:相关方法run--up_request parse_request_end_args
2.请求网页下半部分获得商品数据
:相关方法run--end_request
3.redis,mongodb去重存储数据
:相关方法parse_goods_args

:key:搜索关键字
:queue:队列(包含:页码page_index)
:threadx:多线程线路名称
:add_nums:完成存储的有效数据量
'''
class SearchGoods(threading.Thread):
    def __init__(self,key,cookies,queue,threadx):
        super(SearchGoods,self).__init__()
        self.url = 'https://search.jd.com/s_new.php'
        self.key=key
        self.psort = PSORT
        self.cookies=cookies
        self.proxies = getproxies()
        self.ua = USERAGENT
        self.headers = {
            'Host':'search.jd.com',
            'Referer':'https://search.jd.com/Search',
            'User-Agent':self.ua,
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.queue = queue
        #线路
        self.threadx = threadx
        self.add_nums = 0
    '''
    间隔getime请求次数重新获取一次proxies与cookies
    :proxies:代理
    :cookies:重新采集到的cookie
    :getime:访问次数,30以上则更换cookies,初次访问为30,获取初始参数值
    '''
    def run(self,getime=0):
        print('%s线程,开启关键字[%s]采集任务......'%(self.threadx,self.key))
        while True:
            if not self.queue.empty():
                page_index = self.queue.get_nowait()
                #s_num:请求参数params中参数s,分析应为反爬的一项策略
                s_num = 0
                for p in range(1,page_index):
                    s_num += random.randint(26,30) if page_index != 1 else 1
                getime += 1
                #随机产生一个数值用来确定是否更换cookies
                rd = random.randint(15,30)
                if getime > rd:
                    #从setting模块中获取cookies和proxies
                    url_cookie = 'https://search.jd.com/s_new.php?keyword={key}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq={wq}&psort=3&stock=1&page=1&s=61&click=0'.format(key=self.key,wq=self.key)
                    self.proxies = getproxies()
                    print('%s线程,正在获取cookies......'%self.threadx)
                    self.cookies = getcookies(url_cookie)[0]
                    self.ua = USERAGENT
                    getime = 0
                #若请求出错未获得有效数据,重复请求3次
                for req_num in range(3):
                    print('%s线程开始第[%s]页请求......'%(self.threadx,page_index))
                    datas_1 = self.request_up(page_index=page_index,s_num=s_num,req_num=req_num)
                    if datas_1:
                        #执行网页上部分数据搜集任务
                        self.parse_goods_args(datas_1)
                        #获取网页下部分所需API参数
                        args = self.parse_request_end_args(datas_1)
                        #网页下部分page参数 +1
                        page_index += 1
                        s_num += random.randint(26,30) #在前面值的基础上再加一次基数
                        for req_num in range(3):
                            print('%s线程开始第[%s]页请求......'%(self.threadx,page_index))
                            datas_2 = self.request_end(page_index=page_index,s_num=s_num,log_id=args[0],show_items=args[1],req_num=req_num)
                            if datas_2:
                                #执行网页下部分数据搜集任务
                                self.parse_goods_args(datas_2)
                                break
                        break
                    sleep = random.randint(3,10)
                    print('%s线程开始第[%s]页请求出错,暂停%s秒......'%(self.threadx,page_index,sleep))
                    #如果出错则暂停一会再继续,无错则不会执行
                    time.sleep(sleep)
                t = random.uniform(5,15)
                print('%s线程暂停 %s 秒......'%(self.threadx,t))
                time.sleep(t)
            else:
                print('%s线程,完成关键字[%s]的采集任务,共存储 %s 有效数据!' % (self.key,self.threadx,self.add_nums))
                break

    '''
    完整网页需分两次完成requests请求
    :page_index:(1,3,5..)奇数前半部分页码 (2,4,6...)偶数后半部分页码 对应[request_up(),request_end()函数])
    '''
    #请求网页前半部分数据
    def request_up(self,page_index,s_num,req_num=0,timeout=5):
        params = {
            'keyword': self.key,
            'enc': 'utf-8',
            'qrst': '1',
            'rt': '1',
            'stop': '1',
            'vt': '2',
            'wq': self.key,
            'psort': self.psort,
            'stock': '1',
            'page': page_index,
            's': s_num,
            'click': '0'
        }
        try:
            resp = requests.get(self.url,params=params,headers=self.headers,cookies=self.cookies,proxies=self.proxies,timeout=timeout)
            result = resp.content.decode('utf-8')
            return result
        except Exception as e:
            if req_num > 1:
                redis.add_error(resp.url)
                print('%s线程第[%s]页请求错误已存档!'%(self.threadx,page_index))
            print('%s线程第[%s]页请求出错: %s '%(self.threadx,page_index,e))
            return None

    #请求网页后半部分数据
    def request_end(self,page_index,s_num,log_id,show_items,req_num=0,timeout=5):
        params = {
            'keyword':self.key,
            'enc':'utf-8',
            'qrst':'1',
            'rt':'1',
            'stop':'1',
            'vt':'2',
            'wq':self.key,
            'psort':self.psort,
            'stock':'1',
            'page':page_index,
            's':s_num,
            'scrolling':'y',
            'log_id':log_id,
            'tpl':'3_M',
            'show_items':show_items
        }
        try:
            resp = requests.get(self.url,params=params,headers=self.headers,cookies=self.cookies,proxies=self.proxies,timeout=timeout)
            result = resp.content.decode('utf-8')
            return result
        except Exception as e:
            if req_num > 1:
                redis.add_error(resp.url)
                print('%s线程第[%s]页请求错误已存档!'%(self.threadx,page_index))
            print('%s线程第[%s]页请求出错: %s '%(self.threadx,page_index,e))
            return None
    #解析后半部分所需API参数
    def parse_request_end_args(self,datas):
        if datas:
            re_showitem = 'li class=\"gl-item\" data-sku=.*?data-pid=\"(\d+)\">'
            re_log_id = 'log_id=\"(\d+\.\d+)\"'
            show_items = ','.join(re.compile(re_showitem,re.S).findall(datas))
            log_id = ''.join(re.compile(re_log_id).findall(datas))
            # print(show_items,log_id)
        return (log_id,show_items)

    #提取商品ID
    def parse_goods_args(self,datas):
        if datas:
            re_goods = 'li class=\"gl-item\" (data-sku=.*?)\s+</div>\s+</div>\s+</li>'
            goods = re.compile(re_goods,re.S).findall(datas)
            # print(len(goods))
            num = 0
            add_num = 0
            for good in goods:
                re_goods_id = 'data-sku=\"(\d+)\" data-spu='
                re_goods_price = '<em>￥</em><i>(.*?)</i>' #不用数字,防止价格缺失
                re_shop_url = 'href=\"(//mall\.jd\.com/index-\d+\.html)\"'
                goods_id = ''.join(re.compile(re_goods_id).findall(good)) #商品id
                goods_price = ''.join(re.compile(re_goods_price).findall(good)) #商品价格
                shop_url = ''.join(re.compile(re_shop_url).findall(good)) #商品对应店铺网址
                print('商品:%s;价格:%s;URL:%s'%(goods_id,goods_price,shop_url))
                num += 1
                #判断goods_id 是否重复,若无则返回True并记录
                if redis.add_goods_id(value=goods_id):
                    add_num += 1
                    mongodb.insert_data(goods_id=goods_id,shop_url=shop_url,price=goods_price)
                else: continue
            print('成功捕获有效goods_id: %s......'%num)
            self.add_nums += add_num
            print('去重后有效数据: %s......'%add_num)

