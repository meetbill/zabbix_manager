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

info_echo()
{echo -e "\033[42;37m[Info]: $1 \033[0m"}
                                        
info_echo "create mediatype script alerts.py"
python ./lib_zabbix/zabbix_api.py --mediatype_add alerts alerts.py
info_echo "create hostgroup 'store'"
python ./lib_zabbix/zabbix_api.py --hostgroup_add store
info_echo "create usergroup op"
python ./lib_zabbix/zabbix_api.py --usergroup_add op store
info_echo "create user op"
python ./lib_zabbix/zabbix_api.py --user_add op 123456 op alerts "ceshi@qq.com"

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


### 添加action

需要在界面上创建action
