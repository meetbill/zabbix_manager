# 产品设计

## 设计思想

* lib_zabbix/zabbix_api.py -- zabbix 的 api 功能，主要用于定时任务执行，如生成报表等。
* main.sh -- shell 菜单式执行程序，主要用于查询任务
* main.py -- python 终端管理界面(待完成)，主要用于配置和查询操作

待完成

> * [#] 输出时统一为一个函数，generate_output函数，提供table/text 
> * [#] 根据self.console True/False 决定是否使用 generate_output 函数输出到终端，函数返回值统一为json
> * [ ] 程序 options 全部从初始化参数初始，子函数直接调用
> * [ ] 子函数调用直接返回json
> * [ ] main.py 终端管理界面
