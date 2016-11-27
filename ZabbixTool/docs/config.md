# agent自动加入监控

* [1 zabbix自动发现配置](#1-zabbix自动发现配置)
* [2 zabbix客户端自动注册(推荐)](#2-zabbix客户端自动注册推荐)

## 1 zabbix自动发现配置


第一步是修改配置文件lib_zabbix/zabbix_config.ini 

主要是修改zabbix的ip、端口、admin账户、admin密码

```bash
#!/bin/bash
python ./lib_zabbix/zabbix_api.py  drule_create "agent discovery" "192.168.199.1-252"
python ./lib_zabbix/zabbix_api.py  action_discovery_create "Auto discovery" store
``` 
自动发现规则是zabbix server去扫描一个网段，把在线的主机添加到Host列表中。适合内网下

直接执行在本目录执行 
直接执行程序后，会执行操作如下

(1)创建自动发现规则

(2)自动创建action，根据action，自动将discovery的机器加到特定的主机群组中，同时链接上linux模板

## 2 zabbix客户端自动注册(推荐)

这次是Active agent主动联系zabbix server，最后由zabbix server将这些agent加到host里。对于需要部署特别多服务器的人来说，这功能相当给力。

(1)agent

修改agent配置文件
```
ServerActive=66.175.222.222
Hostname=auto-reg-test01
HostMetadataItem=system.uname
```
(2)server

步骤：configuration>>actions>>Event source（选择Auto registration）>>CreaAction

* Action选项卡-----------定义Action名称：Action_for_autoreg
* Conditions选项卡------添加:Host metadata like Linux
* Operations选项卡-----添加:Add host,Add to host group ,Link to template

直接执行python main.py即可

执行后需要输入action_name和hostgroup_name

```
#!/bin/bash
python ./lib_zabbix/zabbix_api.py  action_autoreg_create "ceshi_action" "Linux servers"
```
