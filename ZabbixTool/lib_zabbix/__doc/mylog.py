#!/usr/bin/python
#coding=utf8
"""
 Author: Bill
 Created Time : 2015年11月23日 星期一 16时20分07秒
 File Name: mylog.py
 Description:
"""
import logging 
logging.basicConfig(level=logging.DEBUG,
		format='%(asctime)s%(filename)s[line:%(lineno)d] %(levelname)s%(message)s',
		datefmt='%a,%d %b %Y %H:%M:%S',
		filename='/tmp/test.log',
		filemode='a')


logging.debug('debug message')
logging.info('info message')
logging.warning('warning message')
logging.error('error message')
logging.critical('critical message')

