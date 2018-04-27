#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-02-24 23:02:16
# @Author  : xca117 (408114416@qq.com)
# @Link    : *
# @Version : $Id$

'''对访问失败等出错url重新构建访问'''

import threading
import queue
import time

import redisdb
from setting import *
from zhihu import ThreadGet

'''队列PUT error url'''
class ThreadPut(threading.Thread):
	"""docstring for ThreadPut"""
	def __init__(self, queue,threadname):
		super(ThreadPut, self).__init__()
		self.q = queue
		self.threadname = threadname
	def run(self):
		have = 0
		while True:
			if not self.q.full():
				url = redisdb.extract_data(ERROR_LIST_NAME)
				if url != None:
					self.q.put(url)
				else:
					break
					print('第 %s URL_Get线,无数据获取,退出工作状态!')
			else: time.sleep(10)

'''重载zhihu.ThreadGet'''
class ThreadGet(ThreadGet,threading.Thread):
	"""docstring for ThreadGet"""
	def __init__(self,queue,threadname):
		super(ThreadGet,self).__init__(queue,threadname)
		self.q = queue
		self.threadname = threadname
	def run(self):
		have = 0
		while True:
			if not self.q.empty:
				try:
					url = self.q.get_nowait()
					if url:
						self.get_data(url)
				except: pass
			else:
				have += 1
				if have < 10:
					time.sleep(10)
				else: break

if __name__ == '__main__':
	q = queue.Queue(100)
	for x in range(10):
		if x%2 == 0:
			t = ThreadPut(q,x) # 双数线程运行put 单数运行get
		else:
			t = ThreadGet(q,x)
		t.setDaemon(True)
		t.start()
	q.join()
