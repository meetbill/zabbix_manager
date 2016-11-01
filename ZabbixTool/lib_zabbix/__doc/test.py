#!/usr/bin/python
#coding=utf8
"""
# Author: Bill
# Created Time : Wed 02 Dec 2015 10:17:28 AM CST

# File Name: wb_zabbix.py
# Description:

"""
import os
import sys
root_path = os.path.dirname(__file__)
print root_path
sys.path.insert(0, os.path.join(root_path))
sys.path.insert(0, os.path.join(root_path, 'mylib'))
from zabbix_api import zabbix_api
#新增帮助信息，可直接执行脚本
zabbix=zabbix_api()
#获取所有主机列表
zabbix.host_get()
#查询单个主机列表
#zabbix.host_get('WP227')
#获取所有主机组列表
#zabbix.hostgroup_get()
#查询单个主机组列表
#zabbix.hostgroup_get('test01')
#获取所有模板列表
#zabbix.template_get()
#查询单个模板信息
# zabbix.template_get('Template OS Linux')
#添加一个主机组
#zabbix.hostgroup_create('test01')
#添加一个主机，支持将主机添加进多个组，多个模板，多个组、模板之间用逗号隔开，如果添加的组不存在，新创建组
#zabbix.host_create('192.168.199.137', 'ceshi3','Qywp', 'Template OS Linux')
#zabbix.host_create('192.168.2.1', 'Linux servers,test01 ', 'Template OS Linux,Template App MySQL')
#禁用一个主机
# zabbix.host_disable('192.168.2.1')
#删除host,支持删除多个，之间用逗号
#zabbix.host_delete('192.168.2.1,192.168.2.2')
#zabbix.alert_get()
