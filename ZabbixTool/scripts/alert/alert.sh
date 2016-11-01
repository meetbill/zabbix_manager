#########################################################################
# File Name: alert.sh
# Author: Bill
# mail: XXXXXXX@qq.com
# Created Time: 2016-06-20 11:58:11
#########################################################################
#!/bin/bash

info_echo(){
    echo -e "\033[42;37m[Info]: $1 \033[0m"
}

info_echo "create mediatype script alerts.py"
python ./lib_zabbix/zabbix_api.py --mediatype_add alerts alerts.py
info_echo "create hostgroup 'store'"
python ./lib_zabbix/zabbix_api.py --hostgroup_add store
info_echo "create usergroup op"
python ./lib_zabbix/zabbix_api.py --usergroup_add op store
info_echo "create user op"
python ./lib_zabbix/zabbix_api.py --user_add op 123456 op alerts "ceshi@qq.com"

