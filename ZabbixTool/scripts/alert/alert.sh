#########################################################################
# File Name: alert.sh
# Author: Bill
# mail: XXXXXXX@qq.com
# Created Time: 2016-06-20 11:58:11
#########################################################################
#!/bin/bash

zabbix_api action_autoreg_create "ceshi_action" "Linux servers"
zabbix_api mediatype_create alerts alerts.py
zabbix_api usergroup_create "op_group" "Linux servers"
zabbix_api user_create op 123456 "op_group" alerts "ceshi@qq.com"
zabbix_api action_trigger_create "trigger_action" "op_group" "alerts"
