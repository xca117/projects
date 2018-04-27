#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-06 07:40:02
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$


import requests
import simplejson
# import json
import time



headers={
	'Host':'www.lagou.com',
	'Origin':'https://www.lagou.com',
	'Referer':'https://www.lagou.com/jobs/list_%E7%88%AC%E8%99%AB?city=%E6%9D%AD%E5%B7%9E&cl=false&fromSearch=true&labelWords=&suginput=',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
	'X-Anit-Forge-Code':'0',
	'X-Anit-Forge-Token':None,
	'X-Requested-With':'XMLHttpRequest'
}
cookies={
	'_ga':'GA1.2.1793001860.1517587074',
	'user_trace_token':'20180218215732-c6fde6e3-0a59-4e72-a424-8d8493f9ff97',
	'LGUID':'20180218215734-ab7d5d98-14b3-11e8-b073-5254005c3644',
	'X_HTTP_TOKEN':'a6f4cc0e3d0f2e39099d6703e8ee386b',
	'index_location_city':'%E6%9D%AD%E5%B7%9E',
	'JSESSIONID':'ABAAABAACBHABBI6B73B45C66B34258BE79B77BF14E2961',
	'_putrc':'1C810BAF81ABE9B4',
	'login':'true',
	'unick':'%E8%AE%B8%E9%95%BF%E5%AE%89',
	'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6':'1519399243,1520293365,1520291765,1520291054',
	'hideSliderBanner20180305WithTopBannerC':'1',
	'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6':'1520292200',
	'TG-TRACK-CODE':'jobs_code',
	'_gid':'GA1.2.497555463.1520293364',
	'_gat':'1',
	'PRE_HOST':'www.baidu.com',
	'LGSID':'20180309174833-07ad29b0-237f-11e8-b188-5254005c3644',
	'PRE_UTM':'m_cf_cpt_baidu_pc',
	'PRE_SITE':'https%3A%2F%2Fwww.baidu.com%2Fs%3Fie%3Dutf-8%26f%3D3%26rsv_bp%3D1%26tn%3Dbaidu%26wd%3D%25E6%258B%2589%25E5%258B%25BE%26oq%3D%2525E7%252588%2525AC%2525E8%252599%2525AB%2525E6%25258B%252589%2525E5%25258B%2525BE%26rsv_pq%3D849c30f50001fa56%26rsv_t%3D84ddZh1htyC%252F0JjYaZ0sz7pv4t5qVC0diQ1432z5QPot%252BLiLbcjduOKrSS8%26rqlang%3Dcn%26rsv_enter%3D1%26rsv_sug3%3D4%26rsv_sug1%3D4%26rsv_sug7%3D100%26rsv_sug2%3D0%26prefixsug%3D%2525E6%25258B%252589%2525E5%25258B%2525BE%26rsp%3D1%26inputT%3D650%26rsv_sug4%3D2448',
	'PRE_LAND':'https%3A%2F%2Fwww.lagou.com%2Flp%2Fhtml%2Fcommon.html%3Futm_source%3Dm_cf_cpt_baidu_pc',
	'showExpriedIndex':'1',
	'showExpriedCompanyHome':'1',
	'showExpriedMyPublish':'1',
	'hasDeliver':'0',
	'gate_login_token':'2060430aa6017cb2cf83e2b336bcc6bde3e96e1fe571f8d9',
	'SEARCH_ID':'09a51299646148289a4ac5d8dc526ebe',
	'LGRID':'20180310180157-1198afdf-244a-11e8-a898-525400f775ce'
}
url = 'https://www.lagou.com/jobs/positionAjax.json'
proxies = ''  #代理
'''
发起网页请求
'''
def lagou(page):
	'''
	Api参数最重要的就是data参数,可以看到不同的选择亦会出现不同的value甚至key数量也会变化
	因只爬取杭州职位,所以参数基本可以固定
	'''
	params ={
		'city':city,
		'needAddtionalResult':'false',
		'isSchoolJob':'0',
		'first':'false',
		'pn':page,
		'kd':keyword
	}
	response = requests.get(url,params=params,headers=headers,cookies=cookies)
	try:
		data = simplejson.loads(response.text)['content']
		# print(data)
	except:
		print(response.status_code)
		data = None
	return data
'''
获得搜索总页数
'''
def page_next():
	data = lagou(1)
	if data:
		pages = (data['positionResult']['totalCount'] // 15) + 1 #所搜页面总页数
		# print(pages)
	return pages
'''
解析所有数据
'''
def parse(page):
	items = []
	datas = lagou(page)
	if datas:
		for data in datas['positionResult']['result']:
			item ={
				"positionName": data['positionName'], #标题关键字
				"companyFullName": data['companyFullName'], #公司名称
				"companySize":data['companySize'], #公司人员规模
				"salary": data['salary'], #薪资范围
				"workYear":data['workYear'], #要求工作年限
				"formatCreateTime":data['formatCreateTime'], #发布时间
				"businessZones":data['businessZones'], #工作位置
				"URL":http.format(positionId=data['positionId']) #网址链接ID
			}
			items.append(item)
		return items
'''
保存数据
'''
def save_txt(items):
	for item in items:
		with open(filename,'a') as f:
			f.write(' %s , %s , %s , %s , %s , %s , %s , %s  \n' % 
                (item['positionName'],item['companyFullName'],item['companySize'],
                    item['salary'],item['workYear'],item['formatCreateTime'],item['businessZones'],item['URL']))
	f.close()

def manger():
	page = page_next()
	if page > 1:
		for x in range(1,page+1):
			items = parse(x)
			save_txt(items)
			time.sleep(2)
	else:
		items = parse(1)
		save_txt(items)

if __name__ == '__main__':
	'''
	可变参数
	:city 城市
	:keyword 搜索关键字
	'''
	http = 'https://www.lagou.com/jobs/{positionId}.html'
	city = '杭州'
	keyword = '爬虫'
	filename = city+keyword+'.txt' 
	manger()