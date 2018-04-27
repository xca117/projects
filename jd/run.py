#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-30 21:26:27
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$

'''
任务: 
1. 获取孕妇服装相关大型店铺3000+  
2. 获取相关商品评论数据100000+
数据包括:商品价格,用户购买状况,对应店铺等等.

'''
import threading
import queue

from setting import *
from searchgoodsid import SearchGoods
from searchcomment import PutQueue,SearchComment

'''
流程:
1.根据关键字采集商品ID
:相关函数run_goodsid
2.去重后根据商品ID采集各详细信息
:相关函数run_comment
'''


#关键字列表序号
key_num=0
#搜索完一个关键词,callback返回此函数执行下一个关键词
def run_goodsid():
    global key_num
    q_page = queue.Queue()
    key = KEYWORDS[key_num]
    if key:
        print('开启关键字搜索,初始化cookies......')
        start_url = 'https://search.jd.com/Search?keyword={key}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq={wq}&stock=1&psort={psort}&click=0'.format(key=key,wq=key,psort=PSORT)
        #获取初始cookies及关键词搜索对应的最大页码
        result = getcookies(start_url)
        cookies = result[0]
        page_count = result[1]
        for page in range(int(page_count)):
        #网页上部分page参数,奇数(1,3,5...)下部分在类内实现
            page_index = 2*page + 1
            q_page.put_nowait(page_index)
        key_num += 1
        for i in range(THREAD_NUM):
            sg = SearchGoods(key=key,cookies=cookies,queue=q_page,threadx=i)
            sg.setDaemon(True)
            sg.start()
        sg.join()
        print('继续主线程下一个关键字搜索!!!!!!')
        run_goodsid()
    else:
        print('所有关键词已搜索完毕!!!!!')
        #执行搜索评论

def run_comment():
    q_goodis = queue.Queue(3)
    #调用redis数据,填充队列
    #开启多线程
    #因队列有上限,需单独支出一个线程用于填充队列
    for i in range(THREAD_NUM):
        if i == 0:
            #执行队列填充任务的线程
            pq = PutQueue(queue=q_goodis)
            pq.setDaemon(True)
            pq.start()
        else:
            sm = SearchComment(queue=q_goodis,threadx=i)
            sm.setDaemon(True)
            sm.start()
    pq.join()
    sm.join()
    print('所有评论任务采集完毕!!')




if __name__ == '__main__':
    run_goodsid()
    run_comment()





