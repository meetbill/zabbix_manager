#########################################################################
# File Name: config.sh
# Author: Bill
# mail: XXXXXXX@qq.com
# Created Time: 2016-06-20 11:58:11
#########################################################################
#!/bin/bash

info_echo(){
    echo -e "\033[42;37m[Info]: $1 \033[0m"
}

info_echo "create rule"
python ./lib_zabbix/zabbix_api.py  --drule_add "agent discovery" "192.168.199.1-252"
info_echo "create action_discovery"
python ./lib_zabbix/zabbix_api.py  --action_discovery_add "Auto discovery" store
