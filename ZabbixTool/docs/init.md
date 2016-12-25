# 安装 zabbix 后一键配置

## 一键配置

一键配置主要是配置以下内容

> * 创建自动注册 action ，使用脚本安装的 agent 会自动添加到[Linux servers]中
> * 创建[alerts]脚本报警设置
> * 创建用户群组[op_group]，并对[Linux servers]拥有可管理权限
> * 创建用户[op]，属于用户群组[op_group]，密码为123456，同时邮箱为"ceshi@qq.com"
> * 创建触发器 action，设置发生问题使用[alerts]邮件方式发送到设置的邮箱

第一步是修改配置文件zabbix_config.ini 

主要是修改zabbix的ip、端口、admin账户、admin密码

然后修改scripts/alert/alert.sh程序

```bash
#cat scripts/alert/alert.sh
#!/bin/bash

python ./lib_zabbix/zabbix_api.py  action_autoreg_create "ceshi_action" "Linux servers"
python ./lib_zabbix/zabbix_api.py mediatype_create alerts alerts.py
python ./lib_zabbix/zabbix_api.py usergroup_create "op_group" "Linux servers"
python ./lib_zabbix/zabbix_api.py user_create op 123456 "op_group" alerts "ceshi@qq.com"
python ./lib_zabbix/zabbix_api.py action_trigger_create "trigger_action" "op_group" "alerts"
``` 
**执行脚本**
```bash
sh scripts/alert/alert.sh
```
