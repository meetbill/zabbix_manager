#########################################################################
# File Name: alert.sh
# Author: Bill
# mail: XXXXXXX@qq.com
# Created Time: 2016-06-20 11:58:11
#########################################################################
#!/bin/bash

python ./lib_zabbix/zabbix_api.py  action_autoreg_create "ceshi_action" "Linux servers"
python ./lib_zabbix/zabbix_api.py mediatype_create alerts alerts.py
python ./lib_zabbix/zabbix_api.py usergroup_create "op_group" "Linux servers"
python ./lib_zabbix/zabbix_api.py user_create op 123456 "op_group" alerts "ceshi@qq.com"
python ./lib_zabbix/zabbix_api.py action_trigger_create "trigger_action" "op_group" "alerts"
