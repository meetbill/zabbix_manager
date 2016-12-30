#########################################################################
# File Name: start.sh
# Author: meetbill
# mail: meetbill@163.com
# Created Time: 2016-12-30 14:49:49
#########################################################################
#!/bin/bash
# Check if user is root
if [ $(id -u) != "0" ]; then
    echo "Error: You must be root to run this script, please use root to install"
    exit 1
fi

##########################################################process
x=''
NUM=3
function ProcessBar()
{
	x=##########$x
	printf "install-ZabbixTool:[%-${NUM}0s]\r" $x
	sleep 0.1
}
##########################################################process_end
g_BACKUP_DIR=/opt/ZabbixTool_oldbackup
function check_dir()
{
	if [[ -d /opt/ZabbixTool ]]
	then
        if [ ! -d ${g_BACKUP_DIR} ]
        then
            mkdir -p ${g_BACKUP_DIR}
        else
            rm -rf ${g_BACKUP_DIR}
            mkdir -p ${g_BACKUP_DIR}
        fi
        mv /opt/ZabbixTool ${g_BACKUP_DIR}/
        cp -rf ./ZabbixTool /opt/
	else
        cp -rf ./ZabbixTool /opt/
	fi
    ProcessBar
}
function check_config()
{
    if [[ ! -f /etc/zabbix_tool/zabbix_config.ini ]]
    then
        mkdir -p /etc/zabbix_tool
        cp ./ZabbixTool/lib_zabbix/zabbix_config.ini /etc/zabbix_tool/
    fi
    ProcessBar
}
function check_command()
{
    if [[ -f /usr/bin/zabbix_api ]]
    then
        unlink /usr/bin/zabbix_api
        ln -s /opt/ZabbixTool/lib_zabbix/zabbix_api.py /usr/bin/zabbix_api
    else
        ln -s /opt/ZabbixTool/lib_zabbix/zabbix_api.py /usr/bin/zabbix_api
    fi
    chmod +x /usr/bin/zabbix_api
    ProcessBar
}
check_dir
check_config
check_command
echo

