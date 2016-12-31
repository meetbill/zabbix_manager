# 安装 zabbix 后一键配置

## 配置内容

一键配置主要是配置以下内容

> * 创建自动注册 action ，使用脚本安装的 agent 会自动添加到[Linux servers]中
> * 创建[alerts]脚本报警设置
> * 创建用户群组[op_group]，并对[Linux servers]拥有可管理权限
> * 创建用户[op]，属于用户群组[op_group]，密码为123456，同时邮箱为"ceshi@qq.com"
> * 创建触发器 action，设置发生问题使用[alerts]邮件方式发送到设置的邮箱

## 脚本位置及内容

脚本位置:/opt/ZabbixTool/scripts/init/init.sh

```bash
#!/bin/bash

zabbix_api action_autoreg_create "ceshi_action" "Linux servers"
zabbix_api mediatype_create alerts alerts.py
zabbix_api usergroup_create "op_group" "Linux servers"
zabbix_api user_create op 123456 "op_group" alerts "ceshi@qq.com"
zabbix_api action_trigger_create "trigger_action" "op_group" "alerts"
``` 
修改好脚本后，直接执行即可
