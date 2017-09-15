#########################################################################
# File Name: start.sh
# Author: meetbill
# mail: meetbill@163.com
# Created Time: 2016-12-30 14:49:49
#########################################################################
#!/bin/bash

CUR_DIR=$(cd `dirname $0`; pwd)
cd ${CUR_DIR}

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
        cp ./ZabbixTool/lib_zabbix/etc/zabbix_config.ini /etc/zabbix_tool/
    fi
    if [[ ! -f /etc/zabbix_tool/zabbix_setting.ini ]]
    then
        mkdir -p /etc/zabbix_tool
        cp ./ZabbixTool/lib_zabbix/etc/zabbix_setting.ini /etc/zabbix_tool/
    fi
    if [[ ! -f /etc/zabbix_tool/zabbix_tool.ini ]]
    then
        mkdir -p /etc/zabbix_tool
        cp ./ZabbixTool/py_tool/config/zabbix_tool.ini /etc/zabbix_tool/
    fi
    ProcessBar
}
function check_command()
{
    # zabbix_api
    if [[ -f /usr/bin/zabbix_api ]]
    then
        unlink /usr/bin/zabbix_api
        ln -s /opt/ZabbixTool/lib_zabbix/zabbix_api.py /usr/bin/zabbix_api
    else
        ln -s /opt/ZabbixTool/lib_zabbix/zabbix_api.py /usr/bin/zabbix_api
    fi
    chmod +x /usr/bin/zabbix_api
    
    # zabbix_menu
    if [[ -f /usr/bin/zabbix_menu ]]
    then
        unlink /usr/bin/zabbix_menu
        ln -s /opt/ZabbixTool/main.sh /usr/bin/zabbix_menu
    else
        ln -s /opt/ZabbixTool/main.sh /usr/bin/zabbix_menu
    fi
    chmod +x /usr/bin/zabbix_menu
    
    # zabbix_tool
    if [[ -f /usr/bin/zabbix_tool ]]
    then
        unlink /usr/bin/zabbix_tool
        ln -s /opt/ZabbixTool/main.py /usr/bin/zabbix_tool
    else
        ln -s /opt/ZabbixTool/main.py /usr/bin/zabbix_tool
    fi
    chmod +x /usr/bin/zabbix_tool
    ProcessBar
}
check_dir
check_config
check_command
echo

