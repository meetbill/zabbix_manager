zabbix
======

###简介：
		根据日常工作中常用到zabbix的功能，整理以下功能
		1.基于 zabbix 官方 api
		2.提供查询单个或者多个host,hostgroup,template,usergroup,user功能
		3.提供增加host,hostgroup,usergroup功能
		4.提供disable host功能
		5.添加删除host功能
###使用说明：
		修改自己的url，及user,password,详见zabbix_config.ini

###帮助信息
	直接执行 python zabbix_api.py

    执行方法 python zabbix_api.py host_get 
###参考：
1.[zabbix 官方api](https://www.zabbix.com/documentation/3.0/manual/appendix/api/api)
