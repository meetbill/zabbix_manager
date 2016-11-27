# configure alert

* [配置报警](#配置报警)
	* [修改配置文件zabbix_config.ini](#修改配置文件zabbix_configini)
	* [创建报警用户及群组](#创建报警用户及群组)
	* [添加action](#添加action)

## 配置报警

### 修改配置文件zabbix_config.ini

第一步是修改配置文件zabbix_config.ini 

主要是修改zabbix的ip、端口、admin账户、admin密码

然后修改scripts/alert/alert.sh程序

```bash
#cat scripts/alert/alert.sh
#!/bin/bash

python ./lib_zabbix/zabbix_api.py mediatype_create alerts alerts.py
python ./lib_zabbix/zabbix_api.py hostgroup_create store
python ./lib_zabbix/zabbix_api.py usergroup_create op store
python ./lib_zabbix/zabbix_api.py user_create op 123456 op alerts "ceshi@qq.com"
python ./lib_zabbix/zabbix_api.py action_trigger_create "trigger_action"
``` 
### 创建报警用户及群组
直接执行在本目录执行 

```bash
sh scripts/alert/alert.sh
```
直接执行程序后，会执行操作如下

(1)创建alerts脚本报警方式

(2)创建主机群组store

(3)创建用户群组op，并对store拥有可管理权限

(4)创建用户op，属于用户群组op，密码为123456，同时邮箱为"ceshi@qq.com"

(5)需要在界面上创建action

