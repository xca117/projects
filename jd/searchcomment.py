#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-30 21:46:12
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$

import requests
import time
import re
import threading
import random
import json

from setting import USERAGENT,getcookies,getproxies
from datamanager import ConnectRedis,ConnectMongoDB


redis = ConnectRedis()
mongodb = ConnectMongoDB()


'''
将redis数据goodsid放入队列
'''
class PutQueue(threading.Thread):
    def __init__(self,queue):
        super(PutQueue,self).__init__()
        self.queue = queue
    def run(self):
        print('开始填充队列......')
        while True:
            if not self.queue.full():
                goodsid = redis.get_goods_id()
                if goodsid:
                    self.queue.put(goodsid,timeout=10)
                else: 
                    print('所有数据已加入队列,此线程关闭!')
                    break
            else:
                print('队列填充完毕!')
                time.sleep(10)
                print('开始填充队列......')

'''
流程:
先请求商品主页获得源码
:相关函数run--main_page_request,
从源码中提取评论API所需参数,继而请求评论API
:相关函数request

:queue:队列
:threadx:线程名
:eval_nums:获得评论总数
'''
class SearchComment(threading.Thread):
    def __init__(self,queue,threadx):
        super(SearchComment,self).__init__()
        #商品评价url
        self.url = 'https://sclub.jd.com/comment/productPageComments.action'
        self.queue = queue
        self.threadx = threadx
        self.ua = USERAGENT
        self.eval_nums = 0
    '''
    请求网址获得商品网页html源码,从源码中提取参数commentVersion,再API请求获取评论数据
    :commentVersion:评价页面API参数fetchJSON_comment98vv + commentVersion
    :have:当队列为空时重复请求的判断参数
    :getime:判断循环次数,更新cookies
    '''
    def run(self,have=0,getime=15):
        print('%s线程,开启商品评论采集任务......'%self.threadx)
        while True:
            if not self.queue.empty():
                have = 0
                goodsid = self.queue.get(timeout=10)
                if goodsid:
                    path = '/{}.html'.format(goodsid)
                    #headers参数s_time请求时间与标准时间有时间差,这里取最大 8小时30分 每分钟 60点,此值不固定可能需维护
                    s_time = time.strftime('%a, %d %b %Y %H:%M:%S GMT',time.localtime(time.time() - 28980.0))
                    headers={
                        'authority': 'item.jd.com',
                        'method': 'GET',
                        'path': path, #/26027416815.html
                        'scheme': 'https',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'zh-CN,zh;q=0.9',
                        'cache-control': 'max-age=0',
                        'if-modified-since': 'Mon, 16 Apr 2018 16:06:50 GMT',
                        "referer": 'https://search.jd.com/Search',
                        'upgrade-insecure-requests': '1',
                        'user-agent':self.ua
                    }
                    getime += 1
                    #间隔一定循环次数获取cookies,user-agent,proxies
                    rb = random.randint(5,15)
                    if getime > rb:
                        print('%s线程,正在获取cookies......'%self.threadx)
                        proxies = getproxies()
                        url_cookie = 'https://item.jd.com/{}.html'.format(goodsid)
                        cookies = getcookies(url_cookie)
                        self.ua = USERAGENT
                        getime = 0
                    url = 'https://item.jd.com/{}.html'.format(goodsid)
                    def main_page_request(mpr_num):
                        try:
                            print('◆◆◆◆◆◆%s线程,开始网络请求ID[%s]请求◆◆◆◆◆◆'%(self.threadx,goodsid))
                            res = requests.get(url,headers=headers,cookies=cookies,timeout=10).text
                            commentVersion = ''.join(re.compile('commentVersion:\'(\d+)\'').findall(res)).strip()
                            # print(res)
                            return commentVersion
                        except Exception as e:
                            if mpr_num > 1:
                                redis.add_error(url)
                            print('%s线程,网络请求出错: %s !'%(self.threadx,e))
                    #若出错重复请求3次
                    for mpr_num in range(3):
                        commentVersion = main_page_request(mpr_num)
                        if commentVersion:
                            self.request(goodsid=goodsid,commentVersion=commentVersion,cookies=cookies,proxies=proxies)
                            break
                        sleep = random.randint(10,20)
                        print('%s线程,网络请求出错暂停%s秒......'%(self.threadx,sleep))
                        time.sleep(sleep)
                    sleep = random.uniform(5,10)
                    print('%s线程,网络请求暂停%s秒......'%(self.threadx,sleep))
                    time.sleep(sleep)
                else: continue
            else:
                if have < 3:
                    have += 1
                    time.sleep(10)
                    continue
                else:
                    print('%s线程,完成商品评论采集任务,共获得[%s]评价!' % (self.threadx,self.eval_nums))
                    break
    '''
    正式开启评论采集
    '''
    def request(self,goodsid,commentVersion,cookies,proxies,have=0):
        referer = 'https://item.jd.com/{}.html'.format(goodsid)
        callback = 'fetchJSON_comment98vv' + commentVersion
        path = '/comment/productPageComments.action?callback={callback}&productId={goodsid}&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'.format(callback=callback,goodsid=goodsid)
        headers = {
            'authority': 'sclub.jd.com',
            'method': 'GET',
            'path': path,
            'scheme': 'https',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'referer': referer,  #https://item.jd.com/26027416815.html
            'User-Agent': self.ua
        }
        def param():
            param = {
                'callback': callback,
                'productId': goodsid,
                'score': sore, # 0 全部 1 差评 2 中评 3 好评 4 晒图 5 追评
                'sortType': '5',
                'page': page, # 0开始
                'pageSize': '10',
                'isShadowSku': '0',
                'fold': '1'
            }
            return param
        comment_data = {}
        #评价集合(1:差评,2:中评,3:好评,5:追评)
        comments_sore = {}
        #当前网页获得的评论数
        eval_num = 0
        for sore in [0,1,2,3,5]:
            page = 0
            comment_sore = []
            while True:
                try:
                    params =param()
                    res = requests.get(self.url,params=params,headers=headers,cookies=cookies,proxies=proxies,timeout=10)
                    # print(res.content)
                    data_1 = ''.join(re.compile('%s\((.*?)\);'%callback,re.S).findall(res.text))
                    # print(data_1)
                    have = 0
                    try:
                        data = json.loads(data_1)
                        maxpage = data.get('maxPage',{})
                        have = 0
                        print('%s线程,开始[%s]标签,数据采集......'%(self.threadx,sore))
                        if sore == 0:
                            data_next = data.get('productCommentSummary',{})
                            comment_data = {
                                u'最大采集页':data.get('maxPage',{}),
                                u'全部评论数':data_next.get('commentCount',{}),
                                u'好评率':data_next.get('goodRate',{}),
                                u'中评率':data_next.get('generalRate',{}),
                                u'差评率':data_next.get('poorRate',{}),
                                u'追加评价数':data_next.get('afterCount',{}),
                                u'综合评分':data_next.get('averageScore',{})
                            }
                            #只需采集一次即可,进入下一个循环
                            break
                        else:
                            if maxpage > 0 and page < maxpage:
                                print('%s线程,[%s]标签当前采集页[%s/%s]页......'%(self.threadx,sore,page+1,maxpage))
                                data_next = data.get('comments',{})
                                for item in data_next:
                                    comment_specific = {
                                        u'用户ID':item.get('id',{}),
                                        u'评价时段':item.get('days',{}),
                                        u'评价内容':item.get('content',{}),
                                        u'服装颜色':item.get('productColor',{}),
                                        u'服装尺码':item.get('productSize',{}),
                                        u'是否手机购物':item.get('isMobile',{}),
                                        u'付款方式':item.get('userClientShow',{}),
                                        u'追评内容':item.get('afterUserComment',{}).get('hAfterUserComment',{}).get('content',{}),
                                        u'追评时段':item.get('afterDays',{})
                                    }
                                    # print(comment_specific)
                                    comment_sore.append(comment_specific)
                            else:
                                break
                        sleep = random.uniform(5,10)
                        print('%s线程,数据采集暂停%s秒......'%(self.threadx,sleep))
                        time.sleep(sleep)
                        page += 1
                    except Exception as e:
                        print('%s线程,数据采集json转换出错:%s'%(self.threadx,e))
                        # print(res.text)
                        if have < 3:
                            have += 1
                            sleep = random.randint(10,20)
                            print('%s线程,数据采集请求出错暂停%s秒......'%(self.threadx,sleep))
                            time.sleep(sleep)
                        else:
                            redis.add_error(res.url)
                            break
                except Exception as e:
                    print('%s线程,数据采集请求出错:%s'%(self.threadx,e))
                    # print(res.text)
                    if have < 3:
                        have += 1
                        sleep = random.randint(10,20)
                        print('%s线程,数据采集请求出错暂停%s秒......'%(self.threadx,sleep))
                        time.sleep(sleep)
                    else:
                        redis.add_error(res.url)
                        break
            comments_sore[u'评价标签:[%s]'%sore]=comment_sore
        comment_data[u'商品评价详情'] = comments_sore
        # print(comment_data)
        mongodb.up_data(goodsid,comment_data)
        self.eval_nums += eval_num






