#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-30 21:31:01
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$

import requests
import json
import chardet
import time
import re
from openpyxl import Workbook


class Item():
    startdate = None #发布日期
    enddate = None #有效期
    job_name = None #职位
    salary = None #工资范围
    education = None #学历
    experience = None #工作经验
    number = None #招聘人数
    description = None #职位要求
    company_name = None #公司名称
    employertype = None #公司属性[公有,私有]
    size = None #公司人数
    district = None #区域地址
    url = None #真正地址
    main_page = None #百度网页地址

#输出日志
def login(func):
    def func_name(*arg):
        print('正在运行 %s 字段...' % func.__name__)
        return func(*arg)
    return func_name

@login
def request(page):
    print('正在请求第 %s 页...' % page)
    headers = {
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Connection':'keep-alive',
        'Host':'zhaopin.baidu.com',
        'Referer':'http://zhaopin.baidu.com/quanzhi',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
    }
    start_url = 'http://zhaopin.baidu.com/api/quanzhiasync?query={key}&sort_key=5&sort_type=1&city={city}&detailmode=close&rn=20{pn}'
    #start_url.format(pn='&pn='+str(page)) if i>1 page=20*(i-1) for i in range(1,10) else start_url.format(pn='')
    if page > 1:
        page_index=20*(page-1)
        url = start_url.format(key=key,city=city,pn='&pn='+str(page_index))
    else:
        url = start_url.format(key=key,city=city,pn='')
    try:
        response = requests.get(url,headers=headers,timeout=10)
    except Exception as e:
        print(e)
    # print(chardet.detect(response.content))
    # print(response.content)
    return response.content

@login
def parse(page):
    items = []
    try:
        datas = json.loads(request(page))['data']['main']['data']['disp_data']
        for data in datas:
            # print(data)
            item = Item()
            item.startdate = data.get('startdate')
            item.enddate = data.get('enddate')
            item.job_name = data.get('name')
            item.salary = data.get('ori_salary')
            item.education = data.get('ori_education')
            item.experience = data.get('ori_experience')
            item.number = data.get('ori_number')
            item.description = data.get('description')
            item.company_name = data.get('officialname')
            item.employertype = data.get('ori_employertype')
            item.size = data.get('ori_size')
            item.district = data.get('ori_district')
            item.url = data.get('url')
            item.main_page = data.get('@id')
            items.append(item)
        return items
    except Exception:
        print('Json数据出错!')

@login
def save(items):
    for item in items:
        salary = item.salary.split('-')[0]
        if salary!= '面议' and salary!= '25000以上' and int(salary) <= 10000:
            sh.append([item.startdate,item.enddate,item.job_name,salary,item.education,item.experience,
                item.number,item.description,item.company_name,item.employertype,
                item.size,item.district,item.url,item.main_page])
    workbook.save(r'%s招聘%s.xlsx'%(key,time.strftime('%Y-%m-%d',time.localtime())))

def start():
    for i in range(1,10):
        items = parse(i)
        save(items)
        time.sleep(2)

if __name__ == '__main__':
    city = '杭州'
    key = 'python'
    workbook = Workbook()
    sh = workbook.create_sheet('Data',index=0)
    sh.append(['发布日期','结束日期','职位','工资范围','学历','工作经验','招聘人数','职位要求',
            '公司名称','公司属性','公司人数','地址区域','URL链接','副链接URL'])
    start()
