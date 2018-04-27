#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-02-23 22:51:59
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$

'''
思路: 通过特定Api接口连接个人关注与被关注列表获取并拓展到大多数人个人信息
技术要点: 
	1. 多线程提高工作速率
	2. 队列保障数据安全
	3. Redis即时数据去重(减少访问率)与Redis错误记录(对访问失败等数据做记录)
	4. 代理池减少反爬几率
	5. MongoDB存储最终结果
同: 可以用多进程,模式类似
	利用pool进程池模块.
'''
import threading
import queue
import requests
import json
import time
'''Made_Self'''
import redisdb
import agent_pool
from setting import *

'''将地址标签(包括初始标签和后获取)放入队列'''
class ThreadPut(threading.Thread):
	"""docstring for ThreadPut"""
	def __init__(self, queue,threadname):
		super(ThreadPut, self).__init__()
		self.q = queue
		self.threadname = threadname
	def run(self):
		have = 0 #当put队列为空时重试次数
		while True:
			if not self.q.full():
				user = redisdb.extract_data(LIST_KEY_NAME)
				if user != None:
					have = 0
					if redisdb.check_add(SET_KEY_NAME,user):
							self.q.put(user) # 数据满则等待 直到可以放入?
				else:
					have += 1
					if have < 30: # 由于redis是边下载数据边提取可能会出现暂无数据状态
						time.sleep(1)
					else: 
						print('第 %s PUT数据线,长时间未获取到有效数据,退出工作状态!' % self.threadname)
						break
			else: time.sleep(1)

'''根据队列标签访问api接口获取更多数据'''
class ThreadGet(threading.Thread):
	def __init__(self,queue,threadname):
		super(ThreadGet, self).__init__()
		self.q = queue
		self.threadname = threadname
		self.req = requests.Session()
		self.headers = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language': 'en',
			'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
		}
		proxies = agent_pool.get_proxy()
		self.proxies = {
			'http':proxies
		}
		self.include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
	def run(self):
		have = 0 #当get队列为空时重试次数
		while True:
			if not self.q.empty():
				try:
					have = 0
					user = self.q.get_nowait()
					# print(user)
					if user != None:
						urls = [
								'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit=20',
								'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit=20'
							]
						for url in urls:
							self.get_data(url.format(user=user,include=self.include,offset=0))
				except:
					print('第 %s Get线,获取数据失败!' % threadname)
			else: 
				have += 1
				if have < 30:
					time.sleep(1)
				else: 
					print('第 %s Get线,长时间无数据,退出工作状态!' % threadname)
					break
	'''得到数据并完成Redis存入与下一页继续'''
	def get_data(self,url):
		_json = self.parse(url)
		try:
			list_atts = _json['data']  # 关注列表信息
			next_atts = _json['paging'] # 关注列表下一页信息
			if list_atts != None:
				for li in list_atts:
					url_token = li['url_token']
					redisdb.add_list(LIST_KEY_NAME,url_token)
					# print(url_token)
			if not next_atts['is_end']:
				print(next_atts['next'])
				self.get_data(next_atts['next'])
		except:
			print('未获取到data或paging数据')
			# 记录url
			redisdb.add_list(ERROR_LIST_NAME,url)
	def parse(self,url):
		try:
			response = self.req.get(url,headers=self.headers,proxies=self.proxies)
			try:
				jsons = json.loads(response.text)
				return jsons
			except:
				print('JSON数据解析失败!')
				return None
		except:
			print('访问网址失败:%s '% response.status_code)
			# 保存错误url
			redisdb.add_list(ERROR_LIST_NAME,url)


if __name__ == '__main__':
	q = queue.Queue(100)
	start_user = 'gong-lu-shang-dian-ontheroadstore'
	redisdb.add_list(LIST_KEY_NAME,start_user)
	for x in range(10):
		if x%2 == 0:
			t = ThreadPut(q,x) # 双数线程运行put 单数运行get
		else:
			t = ThreadGet(q,x)
		t.setDaemon(True)
		t.start()
	q.join()
