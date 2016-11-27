#########################################################################
# File Name: item_list.sh
# Author: 遇见王斌
# mail: meetbill@qq.com
# Created Time: 2016-06-07 12:35:08
#########################################################################
#!/bin/bash
err_echo(){
    echo -e "\033[41;37m[Error]: $1 \033[0m"
}
read -p  "please host id:" g_HOST_ID
if [[ -z ${g_HOST_ID} ]]
then
    err_echo "host_id is null"
fi
python ./lib_zabbix/zabbix_api.py item_get $g_HOST_ID

