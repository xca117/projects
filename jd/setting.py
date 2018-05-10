#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-06 07:20:43
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$


'''
参数配置 
cookies,headers,proxies,page_count,redis_name,mongodb_name,keyword等
'''
import random
from selenium import webdriver
import re
import sys
import requests
#添加代理池模块
# sys.path.append('C:\\Users\\Administrator\\Desktop\\python_pro\\jd\\ProxyPool_master')
# from ProxyPool_master.run import main


#开启多线程数量
THREAD_NUM = 8

#浏览器user-agent
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]
#获取随机user-agent
USERAGENT = random.choice(USER_AGENTS)

# 3代表销量排序,searchgoodsid模块,搜索商品排序方式
PSORT = '3'

#搜索关键字
KEYWORDS = ['孕妇装','孕妈装','怀孕服装','孕妇夏装','孕妇春装']

#Redis 名称
REDISLIST = 'list_data'
REDISSET = 'set_data'
REDISERROR = 'list_error'


#执行selenium 获得完整cookie及搜索结果最大页
def getcookies(url):
    driver=webdriver.Firefox()
    try:
        driver.get(url)
        # 获得 cookie信息
        cookies={}
        cookie_list = driver.get_cookies()
        print(cookie_list)
        for cookie in cookie_list:
            key,value = cookie['name'],cookie['value']
            cookies[key] = value
        re_1 = r'page_count:\"(\d+)\"'
        html = driver.page_source
        #获得搜索的最大页,goodid搜索项
        page_count = ''.join(re.compile(re_1).findall(html))
        if page_count:
            return (cookies,page_count)
        else:
            return cookies
    except:
        pass
    finally:
        driver.quit()
    # print(cookies)
    # driver.quit() driver.close()

#开启代理池
# main()
#获得代理
PROXY_POOL_URL = 'http://localhost:5000/get'
def getproxies():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None
    return 
