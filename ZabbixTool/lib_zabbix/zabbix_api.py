#!/usr/bin/python 
#coding:utf-8 
#
# {"status":"OK","output":output}
from __future__ import print_function
__version__ = "1.4.02"
 
import json 
import ConfigParser
import sys
import os
import time
import unicodedata
import config
from pydoc import render_doc
from w_lib.zabbix_api_lib import ZabbixAPI
import re

root_path = os.path.split(os.path.realpath(__file__))[0]
os.chdir(root_path)
sys.path.insert(0, os.path.join(root_path, 'w_lib'))
zabbix_config = os.path.exists("/etc/zabbix_tool/zabbix_config.ini") and  "/etc/zabbix_tool/zabbix_config.ini" or "./etc/zabbix_config.ini"
zabbix_setting = os.path.exists("/etc/zabbix_tool/zabbix_setting.ini") and "/etc/zabbix_tool/zabbix_setting.ini" or "./etc/zabbix_setting.ini"


from colorclass import Color
from terminaltables import AsciiTable
import my_sort
import my_compare
import XLSWriter
from BLog import Log
import argparse
import logging
import math
reload(sys)
sys.setdefaultencoding("utf-8")
def err_msg(msg):
    print("\033[41;37m[Error]: %s \033[0m"%msg)
    exit()
def warn_msg(msg):
    print("\033[43;37m[Warning]: %s \033[0m"%msg)

class zabbix_api: 
    def __init__(self,terminal_table=False,debug=False,output=True,output_sort=False,sort_reverse=False,profile="zabbixserver"): 
        web_access = False
        logpath = "/tmp/zabbix_tool.log"
        self.logger = Log(logpath,level="debug",is_console=debug, mbs=5, count=5)
        if os.path.exists(zabbix_setting):
            config = ConfigParser.ConfigParser()
            config.read(zabbix_setting)
            web_access = config.get("web", "apache")
            logo_show_config = config.get("report","logo_show")
            if logo_show_config == "True":
                self.logo_show = True
            else:
                self.logo_show = False

        else:
            print("the config file [%s] is not exist"%zabbix_setting)
            exit(1)

        if os.path.exists(zabbix_config):
            config = ConfigParser.ConfigParser()
            config.read(zabbix_config)
            # 是否输出显示
            self.output = output
            # 输出结果第几列排序
            self.output_sort = int(output_sort)
            self.reverse = sort_reverse
            self.server = config.get(profile, "server")
            self.port = config.get(profile, "port")
            self.user = config.get(profile, "user")
            self.password = config.get(profile, "password")
            zabbix_server="http://%s:%s"%(self.server,self.port)
            if web_access == "True":
                zabbix_server = zabbix_server + '/zabbix'
            if debug:
                self.zapi=ZabbixAPI(server=zabbix_server,log_level=logging.DEBUG)
            else:
                self.zapi=ZabbixAPI(server=zabbix_server)
            self.zapi.login(self.user,self.password)
            self.__host_id__ = ''
            self.__hostgroup_id__ = ''
        else:
            print("the config file [%s] is not exist"%zabbix_config)
            exit(1)
        self.terminal_table=terminal_table
        self.sepsign=None
    def version(self):
        print("zabbix version:[%s]"%self.zapi.api_version()) 
    def host_get(self,hostName=''): 
        '''
        get host
        [eg1]#zabbix_api host_get
        [eg2]#zabbix_api host_get "Zabbix server"
        '''
        output = []
        output.append(["HostID","HostName","ip","Status","Available","templates"])
        response=self.zapi.host.get({
                      "output": ["hostid","host","name","status","available"],
                      "filter":{"name":hostName},
                      "selectParentTemplates":["name"],
                      "selectInterfaces":["ip"]})
        if len(response) == 0:
            return 0
        for host in response:      
            status={"0":"OK","1":"Disabled"}
            available={"0":"Unknown","1":Color('{autobggreen}available{/autobggreen}'),"2":Color('{autobgred}Unavailable{/autobgred}')}
            if len(hostName)==0:
                template = ""
                if len(host["parentTemplates"]):
                    for template_item in host["parentTemplates"]:
                        template =  template_item["name"] + '\n'+ template
                output.append([host['hostid'],host['name'],host['interfaces'][0]["ip"],status[host['status']],available[host['available']],template])
            else:
                return host['hostid']
        self.__generate_output(output)
        return 0
    def __host_get(self,hostgroupID='',hostID=''): 
        '''
        内部函数
        返回特定主机组下的主机列表和某个主机的列表

        返回值为列表
        host['hostid']
        host['host']
        host['name']
        host['interfaces'][0]["ip"]
        host["available"]
        '''
        #  (1)Return all hosts.
        #  (2)Return only hosts that belong to the given groups.
        #  (3)Return only hosts with the given host IDs.
        all_host_list=[]
        if hostgroupID:
            group_list=[]
            group_list[:]=[]
            for i in hostgroupID.split(','):
                try:
                    int(i)  
                    hostgroup_id = i
                except:
                    hostgroup_id = self.hostgroup_get(i)
                    if not hostgroup_id:
                        continue
                group_list.append(hostgroup_id)
            data_params = {
                    "groupids":group_list,
                    "output": ["hostid","host","name","status","available"],
                    "selectInterfaces":["ip"]
                    }
        elif hostID:
            host_list=[]
            host_list[:]=[]
            for i in hostID.split(','):
                # 判断输入的 hostID 是数字还是字符串(主机名)
                try:
                    int(i)  
                    host_id = i
                except:
                    host_id = self.host_get(i)
                    if not host_id:
                        continue
                host_list.append(host_id)
            data_params = {
                    "hostids":host_list,
                    "output": ["hostid","host","name","status","available"],
                    "selectInterfaces":["ip"]
                    }
        else:
            data_params = {
                    "output": ["hostid","host","name","status","available"],
                    "selectInterfaces":["ip"]
                    }
        response=self.zapi.host.get(data_params)
        if len(response) == 0:
            return []
        for host in response:      
            all_host_list.append((host['hostid'],host['host'],host['name'],host['interfaces'][0]["ip"],host["available"]))
        return all_host_list
    def host_list(self):
        '''
        get host list
        '''
        host_list = self._hosts_get()
        hostlist_info = []
        hostlist_info.append(["host_id","host_name","host_ip"])
        for host in host_list:
            host_id = host[0]
            host_name = host[2]
            host_ip = host[3]
            hostlist_info.append([host_id,host_name,host_ip])
        self.__generate_output(hostlist_info)
        # 只返回主机信息记录
        return hostlist_info[1:]
    def _hosts_get(self):
        '''
        获取特定条件下的主机列表
        '''
        if self.__hostgroup_id__ or self.__host_id__:
            host_list_g=[]
            host_list_h=[]
            if self.__hostgroup_id__:
                host_list_g=self.__host_get(hostgroupID=self.__hostgroup_id__)
            if self.__host_id__:
                host_list_h=self.__host_get(hostID=self.__host_id__)
            # 将host_list_h的全部元素添加到host_list_g的尾部
            host_list_g.extend(host_list_h)

            # 去除列表中重复的元素
            host_list = list(set(host_list_g))
        else:
            host_list = self.__host_get()
        return host_list
    def _host_set(self,hostgroupID='',hostID=''):
        '''
        设置需要输出的主机组或者主机
        '''
        if hostgroupID:
            self.__hostgroup_id__ = hostgroupID
        if hostID:
            self.__host_id__ = hostID
    def host_create(self, hostip,hostname,hostgroupName,templateName): 
        '''
        create a host
        [eg1]#zabbix_api host_create 192.168.199.2 "ceshi_host" "store" "Template OS Linux"
        '''
        if self.host_get(hostname):
            return self.__generate_return("ERR","host [%s] is exist"%hostname)
        group_list=[]
        template_list=[]
        for i in hostgroupName.split(','):
            var = {}
            hostgroup_id = self.hostgroup_get(i)
            if hostgroup_id:
                var['groupid'] = hostgroup_id
                group_list.append(var)
        if not len(group_list):
            return self.__generate_return("ERR","not found hostgroup %s " % hostgroupName)
        for i in templateName.split(','):
            var={}
            templates_info=self.template_get(i)
            if not len(templates_info):
                continue
            var['templateid']=templates_info[0]['templateid']
            template_list.append(var)   

        data_params = {
                "host": hostname, 
                "interfaces": [ 
                        { 
                            "type": 1, 
                            "main": 1, 
                            "useip": 1, 
                            "ip": hostip, 
                            "dns": "", 
                            "port": "10050" 
                        } 
                    ], 
                "groups": group_list,
                "templates": template_list,
                }
        response=self.zapi.host.create(data_params)
        # print(response)
        return self.__generate_return("OK","create host:[%s] hostid:[%s] OK"%(hostname,response['hostids'][0]))
    def host_status(self,hostname,status="Disabled"):
        '''
        Turns a host Enabled or Disabled[default]
        [eg1]#zabbix_api host_status "ceshi_host" "Disabled"
        [eg2]#zabbix_api host_status "ceshi_host" "Enabled"
        '''
        hostid = self.host_get(hostname)
        if not hostid:
            return self.__generate_return("ERR","host [%s] is not exist"%hostname)
        status_flag={"Enabled":0,"Disabled":1}
        data_params = {
                "hostid": hostid,
                "status": status_flag[status]
                }
        self.zapi.host.update(data_params)
        return self.__generate_return("OK","host [%s] set status [%s]"%(hostname,status))
    def host_delete(self,hostname):
        '''
        Remove the host
        [eg1]#zabbix_api host_delete "ceshi_host"
        '''
        hostid = self.host_get(hostname)
        if not hostid:
            return self.__generate_return("ERR","host [%s] is not exist"%hostname)
        response = self.zapi.host.delete([
            hostid
        ])
        return self.__generate_return("OK","delete host:[%s] id:[%s] OK"%(hostname,response["hostids"][0]))
    # hostgroup
    def hostgroup_get(self, hostgroupName=''): 
        '''
        get hostgroup list
        [eg1]#zabbix_api hostgroup_get
        [eg1]#zabbix_api hostgroup_get "Templates"
        '''
        response=self.zapi.hostgroup.get({
                                     "output": ["groupid","name"], 
                                     "filter": { 
                                                "name": hostgroupName 
                                                } 
                                     }) 
         
        if len(response) == 0:
            return 0
        output = []
        output.append(["hostgroupID","hostgroupName"])
        for group in response:
            if  len(hostgroupName)==0:
                output.append([group["groupid"],group["name"]])
            else:
                self.hostgroupID = group['groupid'] 
                return group['groupid'] 
        self.__generate_output(output)
    def dev_hosts_info(self): 
        '''
        '''
        host_list = self._hosts_get()
        output = []
        output.append(["hostname","ip","CPU","mem","available"])
        available={"0":"Unknown","1":Color('{autobggreen}available{/autobggreen}'),"2":Color('{autobgred}Unavailable{/autobgred}')}
        
        # 返回信息使用
        return_info = []
        for host in host_list:
            # host----- host['hostid'],host['host'],host['name'],host['interfaces'][0]["ip"],host["available"]
            # print(host)
            hostid = host[0]
            hostname = host[2]
            hostip = host[3]
            host_available = host[4]

            response=self.zapi.item.get({
                                         "output":["name", "key_", "lastvalue"],
                                         "hostids":hostid,
                                         "monitored":True,
                                         "filter":{
                                             "key_":["system.cpu.util[,user]","vm.memory.size[available]","vm.memory.size[total]"]
                                             }
                                         }) 
            # 返回信息使用
            host_info = {}
            if len(response) == 0:
                output.append([hostname,hostip,"-1","-1",available[host_available]])
                ###################################
                host_info["hostname"] = hostname
                host_info["hostip"] = hostip
                host_info["cpu"] = "-1"
                host_info["mem"] = "-1"
                host_info["host_available"] = host_available
            # {u'itemid': u'23889', u'lastvalue': u'16748281856', u'key_': u'vm.memory.size[total]', u'name': u'Total memory'}
            else:
                cpu_p = float('%0.2f' % float(response[0]["lastvalue"]))
                if float(response[2]["lastvalue"]) == 0.0 :
                    mem_p = "-1"
                else:
                    mem_p = float('%0.2f'%((float(response[2]["lastvalue"]) - float(response[1]["lastvalue"]))/float(response[2]["lastvalue"]) * 100))
                output.append([hostname,hostip,str(cpu_p),str(mem_p),available[host_available]])
                ###################################
                host_info["hostname"] = hostname
                host_info["hostip"] = hostip
                host_info["cpu"] = str(cpu_p)
                host_info["mem"] = str(mem_p)
                host_info["host_available"] = host_available
            ###################################
            return_info.append(host_info)
        self.__generate_output(output)
        return return_info
    def dev_hosts_device(self,mountdir = "/"): 
        '''
        [eg1]#zabbix_api dev_hosts_device "/home"
        [eg2]#zabbix_api dev_hosts_device
        '''
        host_list = self._hosts_get()
        output = []
        output.append(["hostname","ip","use_p","total","use","available"])
        available={"0":"Unknown","1":Color('{autobggreen}available{/autobggreen}'),"2":Color('{autobgred}Unavailable{/autobgred}')}
        
        # 返回信息使用
        return_info = []
        for host in host_list:
            # host----- host['hostid'],host['host'],host['name'],host['interfaces'][0]["ip"],host["available"]
            # print(host)
            hostid = host[0]
            hostname = host[2]
            hostip = host[3]
            host_available = host[4]

            response=self.zapi.item.get({
                                         "output":["name", "key_", "lastvalue","value_type",'units'],
                                         "hostids":hostid,
                                         "monitored":True,
                                         "filter":{
                                             "key_":["vfs.fs.size[%s,total]" % mountdir,"vfs.fs.size[%s,used]" % mountdir,"vfs.fs.size[%s,pfree]" % mountdir]
                                             }
                                         }) 
            # 返回信息使用
            host_dev = {}
            if len(response) == 0:
                output.append([hostname,hostip,"-1","-1","-1",available[host_available]])
                ###################################
                host_dev["hostname"] = hostname
                host_dev["hostip"] = hostip
                host_dev["use_p"] = "-1"
                host_dev["total"] = "-1"
                host_dev["use"] = "-1"
                host_dev["host_available"] = host_available
            # {u'itemid': u'23889', u'lastvalue': u'16748281856', u'key_': u'vm.memory.size[total]', u'name': u'Total memory'}
            else:
                mountdir_free_p = response[0]["lastvalue"]
                mountdir_total = int(response[1]["lastvalue"])
                mountdir_use = int(response[2]["lastvalue"])
                # 检测是 item 类型是否是整数或者浮点数，不是则直接返回-1 
                mountdir_total=self.__ByteFormat(mountdir_total)
                mountdir_use=self.__ByteFormat(mountdir_use)
                mountdir_use_p =float('%0.2f'%( 100.0 - float(mountdir_free_p)))
                mountdir_use_p = str(mountdir_use_p) + " %"
                mountdir_total=str(mountdir_total) + response[1]["units"]
                mountdir_use=str(mountdir_use) + response[2]["units"]
                output.append([hostname,hostip,str(mountdir_use_p),str(mountdir_total),str(mountdir_use),available[host_available]])
                ###################################
                host_dev["hostname"] = hostname
                host_dev["hostip"] = hostip
                host_dev["use_p"] = str(mountdir_use_p)
                host_dev["total"] = str(mountdir_total)
                host_dev["use"] = str(mountdir_use)
                host_dev["host_available"] = host_available
            ###################################
            return_info.append(host_dev)
        self.__generate_output(output)
        # print(return_info)
        return return_info
    def __hostgroup_get_name(self,groupid): 
        '''
        内部函数
        根据hostgroup id 获得主机群组的 name
        '''
        response=self.zapi.hostgroup.get({
                                    "output": "extend", 
                                    "groupids":groupid
                                    })
        if len(response) == 0:
            return 0
        return response[0]['name'] 
    def hostgroup_create(self,hostgroupName):
        '''
        create a hostgroup
        [eg1]#zabbix_api hostgroup_create "ceshi_hostgroup"
        '''
        if self.hostgroup_get(hostgroupName):
            return self.__generate_return("ERR","hostgroup [%s] is exists"%hostgroupName)
        response=self.zapi.hostgroup.create({
                      "name": hostgroupName
                      })
        if len(response) == 0:
            return 0
        return self.__generate_return("OK","create hostgroup [%s] OK"% response['groupids'][0])
    def application_get(self, host_ID,app_name=""): 
        '''
        return a item list
        [eg1]#zabbix_api application_get 10084
        [eg2]#zabbix_api application_get 10084 "CPU"
        '''
        # @return list
        # list_format
        # [item['itemid'],item['name'],item['key_'],item['delay'],item['value_type']],item['units']

        response=self.zapi.application.get({
                                     "output":"extend",
                                     "hostids":host_ID,
                                     #"selectItems":["itemid"]
                                     "filter":{"name":app_name} 
                                     }) 
         
        if len(response) == 0:
            return 0
        output=[]
        output[:]=[]
        output.append(["applicationid","name"])
        # {u'flags': u'0', u'hostid': u'10084', u'applicationid': u'503', u'name': u'app', u'templateids': [u'502']}
        for application in response:
            if len(app_name)==0:
                output.append([application['applicationid'],application['name']])
            else:
                return application['applicationid']
        self.__generate_output(output)
        return 0
    def __appitem_get(self,app_id): 
        '''
        获取某个 applicationid 的所有 item 列表,和 item_get 类似
        return a item list
        '''
        # @return list
        # list_format
        # [item['itemid'],item['name'],item['key_'],item['delay'],item['value_type']],item['units']

        response=self.zapi.item.get({
                                     "output":"extend",
                                     "applicationids":app_id,
                                     }) 
         
        if len(response) == 0:
            return 0
        output=[]
        output[:]=[]
        output.append(["itemid","name","key_","update_time","value_type","history","units"])
        for item in response:
            #########################################
            # alt the $1 and $2 
            #########################################
            position = item['key_'].find('[')+1
            if position:
                list_para = item['key_'][position:-1].split(",")
               # 将$1,$2等置换为真正name
                for para_a in range(len(list_para)):
                    para='$'+str(para_a+1)
                    item['name']=item['name'].replace(para,list_para[para_a])
            output.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history'],item['units']])
        #self.__generate_output(output)
        if len(output[1:]):
            return output[1:]
        else:
            return 0
    def item_get(self, host_ID,itemName=''): 
        '''
        return a item list
        [eg1]#zabbix_api item_get 10084
        [eg2]#zabbix_api item_get 10084 "Free disk"
        '''
        # @return list
        # list_format
        # [item['itemid'],item['name'],item['key_'],item['delay'],item['value_type']],item['units']

        response=self.zapi.item.get({
                                     #"output":"extend",
                                     "output":['itemid','name','key_','delay','value_type','history','units'],
                                     "hostids":host_ID,
                                     "monitored":True,
                                     }) 
         
        if len(response) == 0:
            return 0
        output=[]
        output[:]=[]
        output.append(["itemid","name","key_","update_time","value_type","history","units"])
        for item in response:
            #########################################
            # alt the $1 and $2 
            #########################################
            position = item['key_'].find('[')+1
            if position:
                list_para = item['key_'][position:-1].split(",")
                # 将$1,$2等置换为真正name
                for para_a in range(len(list_para)):
                    para='$'+str(para_a+1)
                    item['name']=item['name'].replace(para,list_para[para_a])
            if  len(itemName)==0:
                output.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history'],item['units']])
            else:
                if item['name']==itemName:
                    output.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history'],item['units']])
                else:
                    if my_compare.my_compare(item['name'],itemName,self.sepsign):
                        output.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history'],item['units']])
        self.__generate_output(output)
        if len(output[1:]):
            return output[1:]
        else:
            return 0
    def item_list(self, host_ID,application): 
        '''
        return a item list
        [eg]#zabbix_api item_list 10084 "CPU,Zabbix agent"
        '''
        # @return list
        # list_format
        # [item['itemid'],item['name'],item['key_'],item['delay'],item['value_type']],item['units']

        
        applicationids=[]
        applicationids[:]=[]
        for i in application.split(','):
            try:
                int(i)  
                applicationid = i
            except:
                applicationid = self.application_get(host_ID,i)
                if not applicationid:
                    continue
            applicationids.append(applicationid)

        self.logger.info("function[%s],hostid[%s],applicationids[%s]"%("item_list",str(host_ID),str(applicationids)))
        response=self.zapi.item.get({
                                     "output":['itemid','name','key_','delay','value_type','history','units'],
                                     "hostids":host_ID,
                                     "applicationids":applicationids,
                                     "monitored":True
                                     }) 
        if len(response) == 0:
            return 0
        output=[]
        output[:]=[]
        itemkey_list=[]
        itemkey_list[:]=[]
        output.append(["itemid","name","key_","update_time","value_type","history","units"])
        for item in response:
            #########################################
            # alt the $1 and $2 
            #########################################
            position = item['key_'].find('[')+1
            if position:
                list_para = item['key_'][position:-1].split(",")
                # 将$1,$2等置换为真正name
                for para_a in range(len(list_para)):
                    para='$'+str(para_a+1)
                    item['name']=item['name'].replace(para,list_para[para_a])
            output.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history'],item['units']])
            itemkey_list.append(item['key_'])
        self.__generate_output(output)
        if len(itemkey_list):
            return itemkey_list
        else:
            return 0
    def __item_get2(self, host_ID,key_name): 
        '''
        return a item list
        [eg1]#zabbix_api item_get 10084
        [eg2]#zabbix_api item_get 10084 "agent.ping"
        Function:根据 key_name 获取唯一 item
        '''
        # @return list
        # list_format
        # [item['itemid'],item['name'],item['key_'],item['delay'],item['value_type']],item['units']

        response=self.zapi.item.get({
                                     "output":"extend",
                                     "hostids":host_ID,
                                     "monitored":True,
                                     }) 
         
        if len(response) == 0:
            return 0
        output=[]
        output[:]=[]
        for item in response:
            #########################################
            # alt the $1 and $2 
            #########################################
            position = item['key_'].find('[')+1
            if position:
                list_para = item['key_'][position:-1].split(",")
                # 将$1,$2等置换为真正name
                for para_a in range(len(list_para)):
                    para='$'+str(para_a+1)
                    item['name']=item['name'].replace(para,list_para[para_a])
            if re.match(key_name, item['key_']):
                output.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history'],item['units']])
        # self.__generate_output(output)
        if len(output):
            return output
        else:
            return 0
    def __item_search(self,item_ID=''): 
        '''
        内部函数
        根据 某个item_ID 确定 item 的value_type 
        '''
        response=self.zapi.item.get({
                                     "output":"extend",
                                     "itemids":item_ID,
                                     }) 
         
        if len(response) == 0:
            return 0
        return response[0]['value_type']
    # history
    def history_get(self,item_ID,date_from,date_till): 
        '''
        return history of item
        [eg1]#zabbix_api history_get 23296 "2016-08-01 00:00:00" "2016-09-01 00:00:00"
        [note]The date_till time must be within the historical data retention time
        '''
        dateFormat = "%Y-%m-%d %H:%M:%S"
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")
        time_from = int(time.mktime(startTime))
        time_till = int(time.mktime(endTime))
        history_type=self.__item_search(item_ID)
        self.__history_get(history_type,item_ID,time_from,time_till)
            
    def __history_get(self,history,item_ID,time_from,time_till): 
        '''
        内部函数
        输出某个 item  特定时间段中的 history 值
        '''
        history_data=[]
        history_data[:]=[]
        response=self.zapi.history.get({
                 "time_from":time_from,
                 "time_till":time_till,
                 "output": "extend",
                 "history": history,
                 "itemids": item_ID,
                 "sortfield":"clock",
                 "limit": 10080
            })
        if len(response) == 0:
            warn_msg("not have history_data")
            debug_info=str([history,item_ID,time_from,time_till,"####not have history_data"])
            self.logger.debug(debug_info)
            return 0.0
        for history_info in response:
            timeArray = time.localtime(int(history_info['clock']))
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            print(item_ID,history_info['value'],otherStyleTime)
    def __get_select_condition_info(self): 
        '''
        内部函数
        获得特定条件的主机信息
        '''
        output = ""
        if self.__hostgroup_id__ or self.__host_id__:
            if self.__hostgroup_id__:
                flag = 1
                for i in self.__hostgroup_id__.split(','):
                    try:
                        int(i)
                        hostgroup_name = self.__hostgroup_get_name(i)
                    except:
                        hostgroup_name = i

                    if flag:
                        flag = 0
                        output = hostgroup_name + output
                    else:
                        output = hostgroup_name+u"、"+output
                output = u"主机组:" + output 
            else:
                output = u"主机组:" + u"无"
            if self.__host_id__:
                flag = 1
                host_name = self.__host_get(hostID=self.__host_id__)
                for host_info in host_name:
                    if flag:
                        output = host_info[2]+"\n"+output
                    else:
                        output = host_info[2]+u"、"+output
                output = u"主机:" + output 
            else:
                output = u"主机:" + u"无" + "\n" + output
            return output
        else:
            return 0
    ##
    # @brief report 
    #
    # @param itemName
    # @param date_from
    # @param date_till
    # @param export_xls 
    #
    # @return 
    def __ByteFormat(self,size):
        if size > math.pow(1024,3):
            return '%.2f G' % (size/math.pow(1024,3))
        if size > math.pow(1024,2):
            return '%.2f M' % (size/math.pow(1024,2))
        if size > 1024:
            return '%.2f K' % (size/math.pow(1024,1))
        return size

    def _report(self,itemName,date_from,date_till,export_xls,select_condition): 

        units_list = ["B","vps","bps","sps"]

        # 设置为调用的函数不输出
        self.output = False
        dateFormat = "%Y-%m-%d %H:%M:%S"
        #dateFormat = "%Y-%m-%d"
        report_output=[]
        
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            title_table =  date_from + "~" + date_till
            info_msg=str(sheetName)
            self.logger.info(info_msg)
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")

        
        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))
        if time_from > time_till:
            return self.__generate_return("ERR","date_till must after the date_from time")
        # 获取需要输出报表信息的host_list
        xls_range = self.__get_select_condition_info()
        if not xls_range:
            xls_range = u"ALL"
        print(xls_range)
        host_list = self._hosts_get()
        for host_info in host_list: 
            ######################################################
            itemid_all_list = self.item_get(host_info[0],itemName)
            ######################################################
            if itemid_all_list == 0:
                debug_msg="host %s No related monitoring items found"% host_info[0]
                self.logger.debug(debug_msg)
                continue
            for itemid_sub_list in itemid_all_list:
                itemid = itemid_sub_list[0]
                item_name = itemid_sub_list[1]
                value_type = itemid_sub_list[4]
                units = itemid_sub_list[6]
                debug_msg="[report]itemid:%s"%itemid
                self.logger.debug(debug_msg)

                # 检测是 item 类型是否是整数或者浮点数，不是则直接返回-1 
                if value_type=="3" or value_type=="0":
                    report_min,report_max,report_avg = self.__trend_get(itemid,time_from,time_till)
                    if value_type=="3":
                        report_min=int(report_min)
                        report_max=int(report_max)
                        report_avg=int(report_avg)
                        if units in units_list:
                            report_min=self.__ByteFormat(report_min)
                            report_max=self.__ByteFormat(report_max)
                            report_avg=self.__ByteFormat(report_avg)
                    report_min=str(report_min) + " " + units
                    report_max=str(report_max) + " " + units
                    report_avg=str(report_avg) + " " + units
                else:
                    report_min="-1"
                    report_max="-1"
                    report_avg="-1"
                itemid=str(itemid)
                report_output.append([host_info[0],host_info[2],item_name,report_min,report_max,report_avg])
        if self.output_sort:
            # 排序，如果是false，是升序
            # 如果是true，是降序
            if self.output_sort in [1,4,5,6]:
                reverse = self.reverse
                report_output = sorted(report_output,key=lambda x:float(x[self.output_sort-1].split()[0]),reverse=reverse)
            else:
                print("Does not support this column sorting")
        ################################################################output
        if self.terminal_table:
            table_show=[]
            table_show.append(["hostid","name","itemName","min","max","avg"])
            for report_item in report_output:
                table_show.append(report_item)
            table=AsciiTable(table_show)
            table.title = itemName
            print(table.table)
        else:
            print("hostid",'\t',"name",'\t',"itemName",'\t',"min",'\t',"max","avg")
            for report_item in report_output:
                for report_item_i in report_item:
                    print(report_item_i,'\t',end=" ")
                print() 
        if export_xls["xls"] == "ON":
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            # title
            if export_xls["title"] == 'ON':
                xlswriter.add_big_head(self.logo_show,0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_big_head(self.logo_show,0,0,sheet_name=sheetName)
            # 报告周期
            xlswriter.add_header(u"报告周期:"+title_table,6,sheet_name=sheetName)
            xlswriter.setcol_width([10,50,35,10,10,10],sheet_name=sheetName)
            
            ## 范围
            xlswriter.add_remark(u"范围:"+xls_range,6,sheet_name=sheetName)
            xlswriter.writerow(["hostid","name","itemName","min","max","avg"],sheet_name=sheetName,border=True,pattern_n=22)
            
            ## 输出内容
            for report_item in report_output:
                xlswriter.writerow(report_item,sheet_name=sheetName,border=True)
            xlswriter.save()
        return 0
    def _report_app(self,appName,date_from,date_till,export_xls,select_condition): 

        units_list = ["B","vps","bps","sps"]

        # 设置为调用的函数不输出
        self.output = False
        dateFormat = "%Y-%m-%d %H:%M:%S"
        #dateFormat = "%Y-%m-%d"
        report_output=[]
        
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            title_table =  date_from + "~" + date_till
            info_msg=str(sheetName)
            self.logger.info(info_msg)
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")

        
        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))
        if time_from > time_till:
            return self.__generate_return("ERR","date_till must after the date_from time")
        # 获取需要输出报表信息的host_list
        xls_range = self.__get_select_condition_info()
        if not xls_range:
            xls_range = u"ALL"
        print(xls_range)
        host_list = self._hosts_get()
        for host_info in host_list: 
            ######################################################
            applicationid = self.application_get(host_info[0],appName)
            # 如果某个 host 没有此 application 则跳过
            if not applicationid:
                continue
            itemid_all_list = self.__appitem_get(applicationid)
            ######################################################
            if itemid_all_list == 0:
                debug_msg="host %s No related monitoring items found"% host_info[0]
                self.logger.debug(debug_msg)
                continue
            for itemid_sub_list in itemid_all_list:
                itemid = itemid_sub_list[0]
                item_name = itemid_sub_list[1]
                value_type = itemid_sub_list[4]
                units = itemid_sub_list[6]
                debug_msg="[report]itemid:%s"%itemid
                self.logger.debug(debug_msg)

                # 检测是 item 类型是否是整数或者浮点数，不是则直接返回-1 
                if value_type=="3" or value_type=="0":
                    report_min,report_max,report_avg = self.__trend_get(itemid,time_from,time_till)
                    if value_type=="3":
                        report_min=int(report_min)
                        report_max=int(report_max)
                        report_avg=int(report_avg)
                        if units in units_list:
                            report_min=self.__ByteFormat(report_min)
                            report_max=self.__ByteFormat(report_max)
                            report_avg=self.__ByteFormat(report_avg)
                    report_min=str(report_min) + " " + units
                    report_max=str(report_max) + " " + units
                    report_avg=str(report_avg) + " " + units
                else:
                    report_min="-1"
                    report_max="-1"
                    report_avg="-1"
                itemid=str(itemid)
                report_output.append([host_info[0],host_info[2],item_name,report_min,report_max,report_avg])
        if self.output_sort:
            # 排序，如果是false，是升序
            # 如果是true，是降序
            if self.output_sort in [1,4,5,6]:
                reverse = self.reverse
                report_output = sorted(report_output,key=lambda x:float(x[self.output_sort-1].split()[0]),reverse=reverse)
            else:
                print("Does not support this column sorting")
        ################################################################output
        if self.terminal_table:
            table_show=[]
            table_show.append(["hostid","name","itemName","min","max","avg"])
            for report_item in report_output:
                table_show.append(report_item)
            table=AsciiTable(table_show)
            print(table.table)
        else:
            print("hostid",'\t',"name",'\t',"itemName",'\t',"min",'\t',"max","avg")
            for report_item in report_output:
                for report_item_i in report_item:
                    print(report_item_i,'\t',end=" ")
                print() 
        if export_xls["xls"] == "ON":
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            # title
            if export_xls["title"] == 'ON':
                xlswriter.add_big_head(self.logo_show,0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_big_head(self.logo_show,0,0,sheet_name=sheetName)
            # 报告周期
            xlswriter.add_header(u"报告周期:"+title_table,6,sheet_name=sheetName)
            xlswriter.setcol_width([10,50,35,10,10,10],sheet_name=sheetName)
            
            ## 范围
            xlswriter.add_remark(u"范围:"+xls_range,6,sheet_name=sheetName)
            xlswriter.writerow(["hostid","name","itemName","min","max","avg"],sheet_name=sheetName,border=True,pattern_n=22)
            
            ## 输出内容
            for report_item in report_output:
                xlswriter.writerow(report_item,sheet_name=sheetName,border=True)
            xlswriter.save()
        return 0
    def _report_key(self,item_key,date_from,date_till,export_xls,select_condition): 

        units_list = ["B","vps","bps","sps"]

        # 设置为调用的函数不输出
        self.output = False
        dateFormat = "%Y-%m-%d %H:%M:%S"
        #dateFormat = "%Y-%m-%d"
        report_output=[]
        
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            title_table =  date_from + "~" + date_till
            info_msg=str(sheetName)
            self.logger.info(info_msg)
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")

        
        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))
        if time_from > time_till:
            return self.__generate_return("ERR","date_till must after the date_from time")
        # 获取需要输出报表信息的host_list
        xls_range = self.__get_select_condition_info()
        if not xls_range:
            xls_range = u"ALL"
        print(xls_range)
        host_list = self._hosts_get()
        for host_info in host_list: 
            itemid_all_list = self.__item_get2(host_info[0],item_key)
            ######################################################
            if itemid_all_list == 0:
                debug_msg="host %s No related monitoring items found"% host_info[0]
                self.logger.debug(debug_msg)
                continue
            for itemid_sub_list in itemid_all_list:
                itemid = itemid_sub_list[0]
                item_name = itemid_sub_list[1]
                value_type = itemid_sub_list[4]
                units = itemid_sub_list[6]
                debug_msg="[report]itemid:%s"%itemid
                self.logger.debug(debug_msg)

                # 检测是 item 类型是否是整数或者浮点数，不是则直接返回-1 
                if value_type=="3" or value_type=="0":
                    report_min,report_max,report_avg = self.__trend_get(itemid,time_from,time_till)
                    if value_type=="3":
                        report_min=int(report_min)
                        report_max=int(report_max)
                        report_avg=int(report_avg)
                        if units in units_list:
                            report_min=self.__ByteFormat(report_min)
                            report_max=self.__ByteFormat(report_max)
                            report_avg=self.__ByteFormat(report_avg)
                    report_min=str(report_min) + " " + units
                    report_max=str(report_max) + " " + units
                    report_avg=str(report_avg) + " " + units
                else:
                    report_min="-1"
                    report_max="-1"
                    report_avg="-1"
                itemid=str(itemid)
                report_output.append([host_info[0],host_info[2],item_name,report_min,report_max,report_avg])
        if self.output_sort:
            # 排序，如果是false，是升序
            # 如果是true，是降序
            if self.output_sort in [1,4,5,6]:
                reverse = self.reverse
                report_output = sorted(report_output,key=lambda x:float(x[self.output_sort-1].split()[0]),reverse=reverse)
            else:
                print("Does not support this column sorting")
        ################################################################output
        if self.terminal_table:
            table_show=[]
            table_show.append(["hostid","name","itemName","min","max","avg"])
            for report_item in report_output:
                table_show.append(report_item)
            table=AsciiTable(table_show)
            print(table.table)
        else:
            print("hostid",'\t',"name",'\t',"itemName",'\t',"min",'\t',"max","avg")
            for report_item in report_output:
                for report_item_i in report_item:
                    print(report_item_i,'\t',end=" ")
                print() 
        if export_xls["xls"] == "ON":
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            # title
            if export_xls["title"] == 'ON':
                xlswriter.add_big_head(self.logo_show,0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_big_head(self.logo_show,0,0,sheet_name=sheetName)
            # 报告周期
            xlswriter.add_header(u"报告周期:"+title_table,6,sheet_name=sheetName)
            xlswriter.setcol_width([10,50,35,10,10,10],sheet_name=sheetName)
            
            ## 范围
            xlswriter.add_remark(u"范围:"+xls_range,6,sheet_name=sheetName)
            xlswriter.writerow(["hostid","name","itemName","min","max","avg"],sheet_name=sheetName,border=True,pattern_n=22)
            
            ## 输出内容
            for report_item in report_output:
                xlswriter.writerow(report_item,sheet_name=sheetName,border=True)
            xlswriter.save()
        return 0
    def __agent_ping(self,item_ID='',time_from='',time_till=''): 
        '''
        此函数为 report_available 引用函数
        '''
        response=self.zapi.trend.get({
               "time_from":time_from,
               "time_till":time_till,
               "output":[
                   "itemid",
                   "clock",
                   "num",
                   "value_min",
                   "value_avg",
                   "value_max"
                        ],
               "itemids":item_ID,
               "limit":"8760"
            })
        if len(response) == 0:
            debug_info=str([item_ID,time_from,time_till,"####not have trend_data"])
            self.logger.debug(debug_info)
            return 0,0,0
        sum_num_value = 0
        sum_avg_value = 0
        for result_info in response:
            hour_num_string = unicodedata.normalize('NFKD',result_info['num']).encode('ascii','ignore')
            hour_num=eval(hour_num_string)
            sum_num_value = sum_num_value + hour_num
            
            hour_avg_string = unicodedata.normalize('NFKD',result_info['value_avg']).encode('ascii','ignore')
            hour_avg=eval(hour_avg_string)
            sum_avg_value = sum_avg_value + hour_avg
        trend_sum = len(response)
        return trend_sum,sum_num_value,sum_avg_value
    def __diff_hour(self,date1,date2):
        '''
        内部函数
        输出两个时间点相差的小时数
        '''
        diff_seconds = date2 - date1
        diff_hour = diff_seconds / 3600
        return diff_hour
    def _set_sepsign(self,sepsign=None):
        self.sepsign = sepsign
    def _report_available(self,itemName,date_from,date_till,export_xls,select_condition,value_type=False): 
        # 设置为调用的函数不输出
        self.output = False

        dateFormat = "%Y-%m-%d %H:%M:%S"
        #dateFormat = "%Y-%m-%d"
        report_output=[]
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            title_table =  date_from + "~" + date_till
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")

        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))-1
        diff_hour = self.__diff_hour(time_from,time_till)

        if time_from > time_till:
            err_msg("date_till must after the date_from time")

        # 获取需要输出报表信息的host_list
        xls_range = self.__get_select_condition_info()
        if not xls_range:
            xls_range = u"ALL"
        print(xls_range)
        host_list = self._hosts_get()
        for host_info in host_list: 
            itemid_all_list = self.item_get(host_info[0],itemName)
            if itemid_all_list == 0:
                continue
            for itemid_sub_list in itemid_all_list:
                itemid=itemid_sub_list[0]
                item_name=itemid_sub_list[1]
                item_key=itemid_sub_list[2]
                item_update_time=itemid_sub_list[3]
                
                check_time=int(item_update_time)
                if not check_time:
                    check_time = 60
                hour_check_num = int(3600/check_time)
                trend_sum,sum_num_value,sum_avg_value = self.__agent_ping(itemid,time_from,time_till)
                
                if (sum_avg_value > 0) and (trend_sum > 0):
                    # 分子为trend_avg平均值之和
                    sum_avg_value_p = float(sum_avg_value*100)
                    sum_check=trend_sum*hour_check_num

                    # 默认0不入库，分母为时间小时差
                    sum_value = diff_hour
                    value_type_info = "null"
                    # 如果0入库，分母为获取到的thrend数
                    if value_type:
                        sum_value = trend_sum
                        value_type_info = "zero"
                    avg_ping=sum_avg_value_p/sum_value
                    if avg_ping == 100:
                        avg_ping =int(avg_ping)
                    else:
                        avg_ping=float('%0.2f'% avg_ping)
                    diff_ping = avg_ping - 100
                else:
                    avg_ping = 0
                    diff_ping = 0
                    sum_check = -1
                    value_type_info = "-1"
                debug_msg="time[%s] hour[%s] itemid:%s update_time:%s trend_sum:%d,sum_avg:%s,sum_num:%d,expected_value:%s type:%s"\
                        %(str(sheetName),str(diff_hour),itemid,item_update_time,trend_sum,str(sum_avg_value),sum_num_value,str(sum_check),value_type_info)
                self.logger.debug(debug_msg)
                report_output.append([host_info[0],host_info[2],item_name,"100",str(avg_ping),str(diff_ping)])
        if self.output_sort:
            # 排序，如果是false，是升序
            # 如果是true，是降序
            if self.output_sort in [1,4,5,6]:
                reverse = self.reverse
                report_output = sorted(report_output,key=lambda x:float(x[self.output_sort-1]),reverse=reverse)
            else:
                print("Does not support this column sorting")
        ################################################################output
        if self.terminal_table:
            table_show=[]
            table_show.append([u"hostid",u"资源类型",u"itemName",u"期望值(%)",u"平均值(%)",u"差值(%)"])
            for report_item in report_output:
                table_show.append(report_item)
            table=AsciiTable(table_show)
            table.title = itemName
            print(table.table)
        else:
            print("hostid",'\t',u"资源类型",'\t',"itemName",'\t',u"期望值(%)",'\t',u"平均值(%)",'\t',u"差值(%)")
            for report_item in report_output:
                for report_item_i in report_item:
                    print(report_item_i,'\t',end=" ")
                print() 
        if export_xls["xls"] == "ON":
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            # title
            if export_xls["title"] == 'ON':
                xlswriter.add_big_head(self.logo_show,0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_big_head(self.logo_show,0,0,sheet_name=sheetName)
            # 报告周期
            xlswriter.add_header(u"报告周期:"+title_table,6,sheet_name=sheetName)
            xlswriter.setcol_width([10,50,35,10,10,10],sheet_name=sheetName)
            
            ## 范围
            xlswriter.add_remark(u"范围:"+xls_range,6,sheet_name=sheetName)
            xlswriter.writerow(["hostid",u"资源类型","itemName",u"期望值(%)",u"平均值(%)",u"差值(%)"],sheet_name=sheetName,border=True,pattern_n=22)
            
            ## 输出内容
            for report_item in report_output:
                xlswriter.writerow(report_item,sheet_name=sheetName,border=True)
            xlswriter.save()
        return 0
    ##
    # @return 
    def _report_available2(self,date_from,date_till,export_xls,select_condition,itemkey_list=''): 
        dateFormat = "%Y-%m-%d %H:%M:%S"
        #dateFormat = "%Y-%m-%d"
        report_output=[]
        
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            title_table =  date_from + "~" + date_till
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")

        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))-1
        diff_hour = self.__diff_hour(time_from,time_till)

        if time_from > time_till:
            err_msg("date_till must after the date_from time")

        # 获取需要输出报表信息的host_list
        xls_range = self.__get_select_condition_info()
        if not xls_range:
            xls_range = u"ALL"
        print(xls_range)
        host_list = self._hosts_get()
        for host_info in host_list: 
            # host_info[1]是host_name,host_info[2]是name
            hostname = host_info[2]
            hostip = host_info[3]
            triggerid_all_list = self.__triggers_get(host_info[0])
            if triggerid_all_list == 0:
                continue
            for triggerid_sub_list in triggerid_all_list:
                triggerid=triggerid_sub_list[0]
                trigger_name=triggerid_sub_list[1]
                trigger_key = triggerid_sub_list[2]
                trigger_prevvalue = triggerid_sub_list[3]
                trigger_units = triggerid_sub_list[4]
                if itemkey_list:
                    if trigger_key not in itemkey_list:
                        continue
                event_result = self.__event_get(triggerid,time_from,time_till,value="1")
                if not event_result:
                    report_output.append([hostname,hostip,trigger_name,"0","100%",trigger_prevvalue+trigger_units])
                else:
                    event_result = self.__event_get(triggerid,time_from,time_till)
                    if not event_result:
                        report_output.append([hostname,hostip,trigger_name,"0","100%",trigger_prevvalue+trigger_units])
                    else:
                        event_result = float(event_result)
                        event_diff = "%0.4f%%"%event_result
                        event_value = "%0.4f%%"%(100.0 - event_result)
                        report_output.append([hostname,hostip,trigger_name,event_diff,event_value,trigger_prevvalue+trigger_units])
        if self.terminal_table:
            table_show=[]
            table_show.append(["hostname","ip","Name","Problems","OK","prevvalue"])
            for report_item in report_output:
                table_show.append(report_item)
            table=AsciiTable(table_show)
            table.title = "Availability report"
            print(table.table)
        else:
            print("hostname",'\t','ip','\t'"Name",'\t',"Problems",'\t',"OK",'\t',"prevvalue")
            for report_item in report_output:
                for report_item_i in report_item:
                    print(report_item_i,'\t',end=" ")
                print() 
        if export_xls["xls"] == "ON":
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            # title
            if export_xls["title"] == 'ON':
                xlswriter.add_big_head(self.logo_show,0,0,4,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_big_head(self.logo_show,0,0,sheet_name=sheetName)
            # 报告周期
            xlswriter.add_header(u"报告周期:"+title_table,6,sheet_name=sheetName)
            xlswriter.setcol_width([15,15,50,10,10,15],sheet_name=sheetName)
            
            ## 范围
            xlswriter.add_remark(u"范围:"+xls_range,6,sheet_name=sheetName)
            xlswriter.writerow(["hostname","ip","name","Problems","OK","prevvalue"],sheet_name=sheetName,border=True,pattern_n=22)
            
            ## 输出内容
            for report_item in report_output:
                xlswriter.writerow(report_item,sheet_name=sheetName,border=True)
            xlswriter.save()
        return 0
    ##
    # @return 
    def _report_flow(self,date_from,date_till,export_xls,hosts_file="./switch"): 
        host_all_info = config.read_config(hosts_file)
        dateFormat = "%Y-%m-%d %H:%M:%S"
        report_output=[]
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
            sheetName =  time.strftime('%Y%m%d',startTime) + "_TO_" +time.strftime('%Y%m%d',endTime)
            title_table =  date_from + "~" + date_till
            info_msg=str(sheetName)
            self.logger.info(info_msg)
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")

        time_from = int(time.mktime(startTime))+1
        time_till = int(time.mktime(endTime))
        if time_from > time_till:
            err_msg("date_till must after the date_from time")

        # 获取需要输出报表信息的host_list
        num=1
        for host_info in host_all_info: 
            # host_info (description,hostid,ethernet_port,default_speed)
            description = host_info[0]
            hostid = host_info[1]
            host_name_list = self.__host_get(hostID=hostid)
            if len(host_name_list) == 0:
                continue
            host_name=host_name_list[0][2]
            ethernet_port = host_info[2]
            default_speed = host_info[3]
            
            item_ethernet_port_in = "Incoming network traffic on " + ethernet_port
            item_ethernet_port_out = "Outgoing network traffic on " + ethernet_port

            # speed
            speed_flag=False
            if default_speed != "AUTO":
                speed = float(default_speed)
            else:
                item_speed = "Speed on " + ethernet_port
                itemid_all_list = self.item_get(hostid,item_speed)
                if itemid_all_list:
                    itemid=itemid_all_list[0][0]
                    report_min,report_max,report_avg = self.__trend_get(itemid,time_from,time_till)
                    speed = report_max
                    if speed == 0:
                        speed = 1000
                        speed_flag = True
                else:
                    speed = -1
            # ethernet_port
            itemid_in_list = self.item_get(hostid,item_ethernet_port_in)
            if itemid_in_list:
                itemid_in=itemid_in_list[0][0]
                in_min,in_max,in_avg = self.__trend_get(itemid_in,time_from,time_till)
                in_min = float('%0.4f'%(in_min /1000000.0))
                in_max = float('%0.4f'%(in_max /1000000.0))
                in_avg = float('%0.4f'%(in_avg /1000000.0))
                rate_in_min = float('%0.4f'% (in_min/speed * 100))
                rate_in_max = float('%0.4f'% (in_max/speed * 100))
                rate_in_avg = float('%0.4f'% (in_avg/speed * 100))
            else:
                print("no item[%s]"%item_ethernet_port_in)
                in_min = -1
                in_max = -1
                in_avg = -1
                rate_in_min = -1
                rate_in_max = -1
                rate_in_avg = -1
            itemid_out_list = self.item_get(hostid,item_ethernet_port_out)
            if itemid_out_list:
                itemid_out = itemid_out_list[0][0]
                out_min,out_max,out_avg = self.__trend_get(itemid_out,time_from,time_till)
                out_min = float('%0.4f'%(out_min /1000000.0))
                out_max = float('%0.4f'%(out_max /1000000.0))
                out_avg = float('%0.4f'%(out_avg /1000000.0))
                rate_out_min = float('%0.4f'%(out_min/speed * 100))
                rate_out_max = float('%0.4f'%(out_max/speed * 100))
                rate_out_avg = float('%0.4f'%(out_avg/speed * 100))
            else:
                print("no item[%s]"%item_ethernet_port_out)
                out_min = -1
                out_max = -1
                out_avg = -1
                rate_out_min = -1
                rate_out_max = -1
                rate_out_avg = -1
            if rate_in_max > rate_out_max:
                bandwidth = rate_in_max
            else:
                bandwidth =rate_out_max
            if speed_flag:
                report_output.append([
                    num,\
                    description,\
                    host_name,\
                    ethernet_port,\
                    speed,\
                    in_max,\
                    in_avg,\
                    in_min,\
                    rate_in_max,\
                    rate_in_avg,\
                    rate_in_min,\
                    out_max,\
                    out_avg,\
                    out_min,\
                    rate_out_max,\
                    rate_out_avg,\
                    rate_out_min,\
                    bandwidth,\
                    1])
            else:
                report_output.append([
                    num,\
                    description,\
                    host_name,\
                    ethernet_port,\
                    speed,\
                    in_max,\
                    in_avg,\
                    in_min,\
                    rate_in_max,\
                    rate_in_avg,\
                    rate_in_min,\
                    out_max,\
                    out_avg,\
                    out_min,\
                    rate_out_max,\
                    rate_out_avg,\
                    rate_out_min,\
                    bandwidth,\
                    0])
            num=num+1
                    
        if self.output_sort:
            # 排序，如果是false，是升序
            # 如果是true，是降序
            if self.output_sort in range(5,19):
                reverse = self.reverse
                report_output = sorted(report_output,key=lambda x:float(x[self.output_sort-1]),reverse=reverse)
            else:
                print("Does not support this column sorting")
        print( \
            "nu",\
            "description",\
            "hostname|",\
            "ethernet_port|",\
            "speed",\
            "in_max|",\
            "in_avg|",\
            "in_min|",\
            "rate_in_max|",\
            'rate_in_avg|',\
            "rate_in_min|",\
            "out_max|",\
            "out_avg|",\
            "out_min",\
            "rate_out_max|",\
            "rate_out_avg|",\
            "rate_out_min|",\
            "bandwidth")
        for report_item in report_output:
            for report_item_i in report_item[:-1]:
                print(report_item_i,end="")
            print()
        if export_xls["xls"] == "ON":
            xlswriter = XLSWriter.XLSWriter(export_xls["xls_name"])
            # title
            if export_xls["title"] == 'ON':
                xlswriter.add_big_head(self.logo_show,0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_big_head(self.logo_show,0,0,sheet_name=sheetName)
            # 报告周期
            xlswriter.add_header(u"报告周期:"+title_table,6,sheet_name=sheetName)
            xlswriter.setcol_width([5,58,20,20,8,8,8,8,8,8,8,8,8,8,8,8,8,11],sheet_name=sheetName)
            xlswriter.write_title(sheet_name=sheetName,border=True,pattern_n=22)
            ## 范围
            #xlswriter.add_remark(u"范围:"+xls_range,6,sheet_name=sheetName)
            #xlswriter.writerow(["hostid",u"资源类型","itemName",u"期望值(%)",u"平均值(%)",u"差值(%)"],sheet_name=sheetName,border=True,pattern_n=22)
            ## 输出内容
            for report_item in report_output:
                if report_item[-1] == 1:
                    xlswriter.writerow(report_item[:-1],sheet_name=sheetName,border=True,pattern_n=2)
                else:
                    xlswriter.writerow(report_item[:-1],sheet_name=sheetName,border=True)
            xlswriter.save()
        return 0
    def action_log(self,date_from,date_till):
        '''
        Outputs the action_log for a specific time
        [eg1]#zabbix_api action_log "2016-08-01 00:00:00" "2016-09-01 00:00:00"
        '''
        dateFormat = "%Y-%m-%d %H:%M:%S"
        try:
            startTime =  time.strptime(date_from,dateFormat)
            endTime =  time.strptime(date_till,dateFormat)
        except:
            err_msg("时间格式 ['2016-05-01 00:00:00'] ['2016-06-01 00:00:00']")
        time_from = int(time.mktime(startTime))
        time_till = int(time.mktime(endTime))
        response=self.zapi.alert.get({
                                "output":"extend",
                                "time_from":time_from,
                                "time_till":time_till
                                }) 
         
        if len(response) == 0:
            print("no alert")
            return 0
        for alert in response:      
            timeArray = time.localtime(int(alert['clock']))
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            print(alert['alertid'],otherStyleTime,alert['sendto'],alert['subject'],alert['status'])
    def __trend_get(self,itemID='',time_from='',time_till=''): 
        '''
        内部函数
        输出一段时间内的某个item的最大值、平均值、最小值
        '''
        trend_min_data=[]
        trend_max_data=[]
        trend_avg_data=[]
        trend_min_data[:]=[]
        trend_max_data[:]=[]
        trend_avg_data[:]=[]
        response = self.zapi.trend.get({
            "time_from":time_from,
            "time_till":time_till,
            "output":[
                "itemid",
                "clock",
                "num",
                "value_min",
                "value_avg",
                "value_max"
                     ],
            "itemids":itemID,
            "limit":"8760"
        })
        if len(response) == 0:
            debug_info=str([itemID,time_from,time_till,"####not have trend_data"])
            self.logger.debug(debug_info)
            return 0.0,0.0,0.0
        for result_info in response:
            trend_min_data.append(result_info['value_min'])
                
            trend_max_data.append(result_info['value_max'])
            trend_avg_data.append(result_info['value_avg'])
        trend_min_data_all=my_sort.Stats(trend_min_data)
        trend_max_data_all=my_sort.Stats(trend_max_data)
        trend_avg_data_all=my_sort.Stats(trend_avg_data)
        trend_min=trend_min_data_all.min()
        trend_max=trend_max_data_all.max()
        trend_avg=float('%0.4f'% trend_avg_data_all.avg())
        
        return (trend_min,trend_max,trend_avg)
    # template
    def template_get(self,identifier=''): 
        '''
        Look up a template list by name or ID number
        [eg1]#zabbix_api template_get
        [eg2-Internal call]#zabbix_api template_get "Template OS Linux"
        [eg3-Internal call]#zabbix_api template_get 10001
        '''
        if identifier:
            try:                 
                int(identifier)  
                params = {"output":["templateid","name"],"templateids":[int(identifier)]}
            except:
                params = {"output":["templateid","name"],"filter":{"name":identifier}}
            return self.zapi.template.get(params)
        else:
            params = {"output":["templateid","name"]}
            response = self.zapi.template.get(params)
            output = []
            output[:] = []
            output.append(["id","template"])
            for template in response: 
                output.append([template['templateid'],template['name']])
            self.__generate_output(output)
            return 0
    def template_import(self,template_path): 
        '''
        import template
        [eg]#zabbix_api template_import template_path
        '''
        try:
            with open(template_path, 'r') as f:
                template = f.read()
        except:
            return self.__generate_return("ERR","the file [%s] not exist"%template_path)
        rules = {
            'applications': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'discoveryRules': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'graphs': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'groups': {
                'createMissing': 'true'
            },
            'hosts': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'images': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'items': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'maps': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'screens': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'templateLinkage': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'templates': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'templateScreens': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
            'triggers': {
                'createMissing': 'true',
                'updateExisting': 'true'
            },
        }
        response = self.zapi.configuration.import_({
                "format": "xml", 
                "rules": rules,
                "source":template
            })
        if response:
            return self.__generate_return("OK","import template [%s] OK"%template_path)
        else:
            return self.__generate_return("ERR","import template [%s] ERR"%template_path)
    def user_get(self,userName=''): 
        '''
        get user list
        [eg1]#zabbix_api user_get
        '''
        response = self.zapi.user.get({
            "output": "extend",
            "filter":{"alias":userName} 
            })
        if len(response) == 0:
            return 0
        output = []
        output[:]=[]
        output.append(["userid","alias","name","url"])
        for user in response:      
            if len(userName)==0:
                output.append([user['userid'],user['alias'],user['name'],user['url']])
            else:
                return user['userid']
        self.__generate_output(output)
    def user_create(self, userName,userPassword,usergroupName,mediaName,email): 
        '''
        create a user
        [eg1]#zabbix_api user_create "ceshi_user" "123456" "ceshi_usergroup" "alerts" "meetbill@163.com"
        '''
        usergroupID=self.usergroup_get(usergroupName)[0]
        mediatypeID=self.mediatype_get(mediaName)[0]
        if self.user_get(userName):
            return self.__generate_return("ERR","user [%s] is exist"%userName)
        if not usergroupID:
            return self.__generate_return("ERR","usergroup [%s] is not exist"%usergroupName)
        if not mediatypeID:
            return self.__generate_return("ERR","mediatype [%s] is not exist"%mediaName)
        response=self.zapi.user.create({
            "alias": userName,
            "name" : userName,
            "passwd": userPassword,
            "usrgrps": [
                {
                    "usrgrpid": usergroupID
                }      
            ],
            "user_medias": [
                {
                    "mediatypeid": mediatypeID,
                    "sendto": email,
                    "active": 0,
                    "severity": 63,
                    "period": "1-7,00:00-24:00"
                }
            ]
        })
        return self.__generate_return("OK","create user:[%s] id:[%s] OK"%(userName,response["userids"][0]))
    def user_delete(self,userName): 
        '''
        Remove user
        [eg1]#zabbix_api user_delete "ceshi_user"
        '''
        userid = self.user_get(userName)
        if not userid:
            return self.__generate_return("ERR","user [%s] is not exist"%userName)
        response = self.zapi.user.delete([
            userid    
        ])
        return self.__generate_return("OK","delete user:[%s] id:[%s] OK"%(userName,response["userids"][0]))
    def usergroup_get(self,usergroupName=''): 
        '''
        return usergroup list
        [eg1]#zabbix_api usergroup_get
        '''
        response = self.zapi.usergroup.get({
            "output": "extend",
            "selectUsers":["alias"],
            "filter":{"name":usergroupName} 
        })
        if len(response) == 0:
            return (0,0)
        output = []
        output[:] = []
        output.append(["usrgrpid","name","gui_access","users_status","users"])
        for user_group in response:      
            if len(usergroupName)==0:
                user_info=""
                for user in user_group["users"]:
                    user_info =  user["alias"] + '\n'+ user_info
                output.append([user_group['usrgrpid'],user_group['name'],user_group['gui_access'],user_group['users_status'],user_info])
            else:
                return (user_group['usrgrpid'],len(user_group["users"]))
        self.__generate_output(output)
        return 0
    def usergroup_create(self, usergroupName,hostgroupName): 
        '''
        Create a usergroup
        [eg1]#zabbix_api usergroup_create "ceshi_usergroup" "Linux servers"
        '''
        if self.usergroup_get(usergroupName)[0]:
            return self.__generate_return("ERR","usergroup [%s] is exist"%usergroupName)
        hostgroupID=self.hostgroup_get(hostgroupName)
        if not hostgroupID:
            return self.__generate_return("ERR","hostgroup [%s] is not exist"%hostgroupName)
        response = self.zapi.usergroup.create({
            "name":usergroupName,
            "rights":{ 
                "permission": 3,
                "id":hostgroupID
            }
            })
        if len(response) == 0:
            return 0
        return self.__generate_return("OK","create usergroup:[%s] id:[%s] is OK"%(usergroupName,response['usrgrpids'][0]))
    def usergroup_delete(self,usergroupName):
        '''
        Remove a usergroup
        [eg1]#zabbix_api usergroup_delete "ceshi_usergroup"
        '''
        usergroupID,usercount=self.usergroup_get(usergroupName)
        if not usergroupID:
            return self.__generate_return("ERR","usergroup [%s] is not exist"%usergroupName)
        if usercount:
            return self.__generate_return("ERR","usergroup [%s] have users"%usergroupName)
        response=self.zapi.usergroup.delete([usergroupID])
        return self.__generate_return("OK","delete usergroup [%s] OK"%usergroupName)
    def mediatype_get(self,mediatypeName=''): 
        '''
        return a mediatype list
        [eg1]#zabbix_api mediatype_get
        '''
        response = self.zapi.mediatype.get(
            {
                "output": "extend",
                "selectUsers" : ["alias"],
                "filter":{"description":mediatypeName} 
            }
        )

        if len(response) == 0:
            return 0,0
        output = []
        output[:] = []
        output.append(["mediatypeid","type","description","exec_path","users"])
        for mediatype in response:      
            if len(mediatypeName):
                return (mediatype['mediatypeid'],len(mediatype["users"]))
            else:
                user_info=""
                for user in mediatype["users"]:
                    user_info =  user["alias"] + '\n'+ user_info
                output.append([mediatype['mediatypeid'],mediatype['type'],mediatype['description'],mediatype['exec_path'],user_info])
        self.__generate_output(output)
        return 0
    def mediatype_create(self, mediatypeName,script_name): 
        '''
        create a mediatype[script]
        [eg1]#zabbix_api mediatype_create "alerts" "alerts.py"
        '''

        # mediatypeType Possible values: 
        # 0 - email; 
        # 1 - script; 
        # 2 - SMS; 
        # 3 - Jabber; 
        if self.mediatype_get(mediatypeName)[0]:
            return self.__generate_return("ERR","mediatype [%s] is exist"%mediatypeName)
        response = self.zapi.mediatype.create(
            { 
                "description": mediatypeName,
                "type": 1,
                "exec_path": script_name,
                "exec_params":"{ALERT.SENDTO}\n{ALERT.SUBJECT}\n{ALERT.MESSAGE}\n"
            }
        )
        return self.__generate_return("OK","create mediatype:[%s] id:[%s] OK"%(mediatypeName,response['mediatypeids'][0]))
    def mediatype_delete(self,mediatypeName):
        '''
        Remove a mediatype
        [eg1]#zabbix_api mediatype_delete "alerts"
        '''
        mediatypeid,userscount=self.mediatype_get(mediatypeName)
        if not mediatypeid:
            return self.__generate_return("ERR","mediatype [%s] is not exist"%mediatypeName)
        if userscount:
            return self.__generate_return("ERR","mediatype [%s] have users"%mediatypeName)
        response = self.zapi.mediatype.delete(
            [
                mediatypeid
            ]
        )
        return self.__generate_return("OK","delete mediatype:[%s] OK"%mediatypeName)
    def drule_get(self,druleName=''): 
        """
        get drule(discoveryRules)
        """
        response=self.zapi.drule.get({
                      "output":["druleid","name","iprange","status"],
                      "filter":{"name":druleName}
                      })
        if len(response) == 0:
            return 0
        output = []
        output[:] = []
        output.append(["druleid","name","iprange","status"])
        status={"0":Color('{autobggreen}Enabled{/autobggreen}'),"1":Color('{autobgred}Disabled{/autobgred}')}
        for drule in response:      
            if len(druleName)==0:
                output.append([drule['druleid'],drule['name'],drule['iprange'],status[drule['status']]])
            else:
                return drule['druleid']
        self.__generate_output(output)
        return 0
    def drule_create(self, druleName,iprange): 
        if self.drule_get(druleName):
            return self.__generate_return("ERR","druleName [%s] is exist"%druleName)

        response=self.zapi.drule.create({
                     "name": druleName,
                     "iprange": iprange,
                     "dchecks": [
                               {
                                   "type": "9",
                                   "key_": "system.uname",
                                   "ports": "10050",
                                   "uniq": "0"
                                }
                              ]
                      })
        if len(response) == 0:
            return 0
        else:
            return self.__generate_return("OK","druleName [%s] is create OK"%druleName)
    def action_get(self,actionName=''): 
        '''
        rerun action list
        [eg1]#zabbix_api action_get
        '''
        # action
        # eventsource 0 triggers
        # eventsource 1 discovery
        # eventsource 2 auto registration
        # eventsource 3 internal
        response=self.zapi.action.get({
                "output": "extend",
                "filter":{
                    "name":actionName,
                } 
            })
        if len(response) == 0:
            return 0
        output = []
        output[:] = []
        output.append(["actionid","name","eventsource","status"])
        status={"0":Color('{autobggreen}Enabled{/autobggreen}'),"1":Color('{autobgred}Disabled{/autobgred}')}
        eventsource={"0":"triggers","1":"discovery","2":"registration","3":"internal"}
        for action in response:      
            if len(actionName)==0:
                self.logger.info(str(action))
                output.append([action['actionid'],action['name'],eventsource[action['eventsource']],status[action['status']]])
            else:
                self.logger.info(str(action))
                return action['actionid']
        self.__generate_output(output)
        return 0
    def action_autoreg_create(self, actionName,metaname,hostgroupName): 
        '''
        create autoreg action
        [eg1]#zabbix_api action_autoreg_create "ceshi_action" "Linux" "Linux servers"
        '''
        if self.action_get(actionName):
            output_print={}
            output_print["status"]="ERR"
            output_print["output"]="this druleName is exists"
            if self.output:
                print(json.dumps(output_print))
            return json.dumps(output_print)

        hostgroupID = self.hostgroup_get(hostgroupName)
        if not hostgroupID:
            output_print={}
            output_print["status"]="ERR"
            output_print["output"]="this hostgroup is not exists"
            if self.output:
                print(json.dumps(output_print))
            return json.dumps(output_print)
        templateName = "Template OS Linux"
        templateID=self.template_get(templateName)[0]['templateid']
        data_params = {
               "name": actionName,
               "eventsource": 2,
               "status": 0,
               "esc_period": 0,
               "filter": {
                   "evaltype": 0,
                   "conditions": [
                        {
                            "conditiontype": 24,
                            "operator": 2,
                            "value": metaname
                        }
                   ]
               },
               "operations": [
                    {
                        "operationtype": 2,# add host
                        "esc_step_from": 1,
                        "esc_period": 0,
                        "esc_step_to": 1
                    },
                    {
                        "operationtype": 4,# add to host group
                        "esc_step_from": 2,
                        "esc_period": 0,
                        "opgroup": [
                            {
                                "groupid":hostgroupID
                            }
                        ],
                        "esc_step_to": 2
                    },
                    {
                        "operationtype": 6, # link to template
                        "esc_step_from": 3,
                        "esc_period": 0,
                        "optemplate": [
                            {
                                "templateid":templateID
                            }
                        ],
                        "esc_step_to": 3
                    }
                ]
            }
        self.zapi.action.create(data_params)
        return self.__generate_return("OK","action [%s] is create OK"%actionName)
    def action_trigger_create(self, actionName,usergroupName,mediatypeName): 
        '''
        create trigger action
        [eg1]#zabbix_api action_trigger_create "ceshi_trigger_action" "op" "alerts"
        '''
        if self.action_get(actionName):
            return self.__generate_return("ERR","this druleName is not exists")
        mediatypeid = self.mediatype_get(mediatypeName)[0]
        if not mediatypeid:
            return self.__generate_return("ERR","this mediatype is not exists")
        usergroupid = self.usergroup_get(usergroupName)
        if not usergroupid:
            return self.__generate_return("ERR","this usergroup is not exists")
        data_params = {
                "name": actionName,
                "eventsource": 0,
                "status": 0,
                "esc_period": 120,
                "def_shortdata": "{HOST.NAME1}_{TRIGGER.NAME}: {TRIGGER.STATUS}",
                "def_longdata": "{TRIGGER.NAME}: {TRIGGER.STATUS}\r\nLast value: \r\n\r\n1. {ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): {ITEM.VALUE1}",
                "filter": {
                    "evaltype": 0,
                    "formula": "A and B",
                    "conditions": [
                        {
                            "conditiontype": 16,  # maintenance status.
                            "operator": 7,  # not in
                            "value": "",
                            "formulaid": "A"
                        },
                        {
                            "conditiontype": 5,
                            "operator": 0,
                            "value": 1,
                            "formulaid": "B"
                        }
                    ]
                },
                "operations": [
                    {
                        "operationtype": 0,
                        "esc_period": 0,
                        "esc_step_from": 1,
                        "esc_step_to": 2,
                        "evaltype": 0,
                        "opmessage_grp": [
                            {
                                "usrgrpid": self.usergroup_get(usergroupName)[0]
                            }
                        ],
                        "opmessage": {
                            "default_msg": 1,
                            "mediatypeid": mediatypeid
                        }
                    }
                ]
            }
        self.zapi.action.create(data_params)
        return self.__generate_return("OK","action [%s] is create OK"%actionName)
    def action_discovery_create(self, actionName,hostgroupName): 
        '''
        create autoreg action
        [eg1]#zabbix_api action_discovery_create "ceshi_action" "Linux servers"
        '''

        if self.action_get(actionName):
            print("\033[041mthis druleName is exists\033[0m")
            sys.exit(1)

        hostgroupID = self.hostgroup_get(hostgroupName)
        if not hostgroupID:
            print("this hostgroup is not exists")
            sys.exit(1)
        templateName = "Template OS Linux"
        templateID=self.template_get(templateName)
        data_params = {
            "name": actionName,
            "eventsource": 1,
            "status": 0,
            "esc_period": 0,
            "filter": {
                "evaltype": 0,
                "conditions": [
                     {
                        "conditiontype": 12,
                        "operator": 2,
                        "value": "Linux"
                     },
                     {
                        "conditiontype":10,
                        "operator": 0,
                        "value":"0"
                     },
                     {
                        "conditiontype":8,
                        "operator": 0,
                        "value":"9"
                     }
                ]
            },
            "operations": [
                {
                    "operationtype": 2,
                    "esc_step_from": 1,
                    "esc_period": 0,
                    "esc_step_to": 1
                },
                {
                    "operationtype": 4,
                    "esc_step_from": 2,
                    "esc_period": 0,
                    "opgroup": [
                        {
                            "groupid":hostgroupID
                        }
                    ],
                    "esc_step_to": 2
                },
                {
                    "operationtype": 6,
                    "esc_step_from": 3,
                    "esc_period": 0,
                    "optemplate": [
                        {
                            "templateid":templateID
                        }
                    ],
                    "esc_step_to": 3
                }
            ]
        }
        self.zapi.action.create(data_params)
        return self.__generate_return("OK","action [%s] is create OK"%actionName)
    def mysql_quota(self): 
        # 设置为调用的函数不输出
        self.output = False

        # 获取host列表
        host_list = self.__host_get()
        sum_history_quota = 0
        sum_trends_quota = 0
        sum_event_quota = 0
        sum_item_num = 0
        for host_info in host_list: 
            # 获取host中的item
            itemid_all_list = self.item_get(host_info[0])
            if itemid_all_list == 0:
                continue
            itemid_num = len(itemid_all_list)
            sum_item_num = sum_item_num + itemid_num
            for itemid_sub_list in itemid_all_list:
                item_history=int(itemid_sub_list[5])
                item_update_time=int(itemid_sub_list[3])
                if not item_update_time:
                    item_update_time = 60
                history_quota = item_history * 24 * 3600 * 50 / item_update_time
                sum_history_quota = sum_history_quota + history_quota
                
        sum_trends_quota = 365 * sum_item_num * 24 * 128
        sum_event_quota = 365 * sum_item_num * 24 * 130 * 5
        mysql_quota = (sum_history_quota + sum_trends_quota + sum_event_quota)/1000000000.0
        print("item_num:%d Pre-estimated use:%fG"%(sum_item_num,mysql_quota))
        return 0
    def __triggers_get(self, host_ID=''): 
        '''
        内部函数
        输出某个 host 的所有 trigger_get
        '''
        if  len(host_ID)==0:
            print("ERR- host_ID is null")
            return 0

        all_trigger_list=[]
        data_params = {
            "output":"extend",
            "hostids":host_ID,
            "expandData":"1",
            "monitored":1,
            #"selectItems":"extend",
            "selectItems":["key_","prevvalue","units","value_type"],
            "expandDescription":"1"
            } 
        response=self.zapi.trigger.get(data_params)
        if len(response) == 0:
            return 0
        for trigger in response:
            all_trigger_list.append((trigger["triggerid"],trigger["description"],trigger["items"][0]["key_"],trigger["items"][0]["prevvalue"],trigger["items"][0]["units"]))
        return all_trigger_list
    def issues(self): 
        '''
        output issues list
        [eg1]#zabbix_api issues
        '''
        params = { 
               "output":"extend",
               "expandDescription":1,
               "only_true":1,
               "skipDependent":1,
               "active":1,
               "withLastEventUnacknowledged":1,
               "monitored":1,
               "selectHosts":["host","name"],
               "selectItems":["key_","prevvalue","units","value_type"],
               "filter": {
                  "value": 1
               }
        }
        response = self.zapi.trigger.get(params)
        if len(response) == 0:
            print(":) no issues")
            return 0
        output = []
        output[:] = []
        output.append(["hostname","key_","trigger","time","prevvalue"])

        issues_info={}
        for trigger in response:
            output.append([trigger["hosts"][0]["name"],trigger["items"][0]["key_"],trigger["description"],time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(trigger["lastchange"]))),trigger["items"][0]["prevvalue"]+trigger["items"][0]["units"]])
            if trigger["hosts"][0]["name"] not in issues_info.keys():
                issues_info[trigger["hosts"][0]["name"]]=[]
            issues_info[trigger["hosts"][0]["name"]].append(trigger["items"][0]["key_"])
        self.__generate_output(output)
        return issues_info
         
    def __event_get(self, triggerid='',time_from='',time_till='',value=""): 
        '''
        The method allows to retrieve events according to the given parameters.
        用于可用性报表使用
        '''
        if value:
            data_params = {
                 "output":"extend",
                 "objectids": triggerid,
                 "time_from":time_from,
                 "time_till":time_till,
                 "value":"1",
            }
        else:
            data_params = {
                    "output":"extend",
                    "objectids": triggerid,
                    "time_from":time_from,
                    "time_till":time_till,
                } 
        response=self.zapi.event.get(data_params)
        if len(response) == 0:
            return 0
        # 当输出的value 包含0值时
        if not value:
            # 当输出只有1个值时，可用性为100%
            if len(response) == 1:
                return 0
            # 输出的列表第一个值为0,表示添加此监控项的时间在时间条件之间，应根据添加监控项的时间为起始时间
            if response[0]["value"] == "0":
                time_from_record = int(response[0]["clock"])
                response=response[1:]
                time_range = time_till - time_from_record
                time_event_sum = 0
                time_diff = 0
                
                for i in range(len(response)):
                    # 如果取的时间值time_till恰好是还在故障时间
                    # 则最后一个值为1，同时将time_till - 最后发生故障的时间的值 并入到故障时间内
                    if (i == (len(response)-1)) and response[i]["value"] == "1":
                        time_diff = int(time_till) - int(response[i]["clock"])
                        time_event_sum = time_event_sum + time_diff
                        break
                    if(i%2) == 0:
                        time_diff = int(response[i+1]["clock"]) - int(response[i]["clock"])
                        time_event_sum = time_event_sum + time_diff
                event_diff = float('%0.4f'%(time_event_sum * 100 / float(time_range)))
                return event_diff
            else:
                time_from_record = time_from
                time_range = time_till - time_from_record
                time_event_sum = 0
                time_diff = 0
                if len(response)%2 == 1:
                       return 0
                for i in range(len(response)):
                    if(i%2) == 0:
                        time_diff = int(response[i+1]["clock"]) - int(response[i]["clock"])
                        time_event_sum = time_event_sum + time_diff
                event_diff = float('%0.4f'%(time_event_sum * 100 / float(time_range)))
                return event_diff
        else:
            # 表示包含值为1的事件
            return 1
    def __generate_output(self,output_list):
        '''
        内部函数
        输出格式化结果
        '''
        if self.output:
            if self.terminal_table:
                #table=AsciiTable(output_list)
                table=AsciiTable(output_list)
                print(table.table)
            else:
                for output in output_list:
                    for output_sub in output:
                        output_sub=output_sub.replace('\n', ',')
                        print("[%s]"%output_sub,end=" ")
                    print()
            print("sum: ",len(output_list[1:]))
    def __generate_return(self,status,output_info):
        '''
        内部函数
        返回格式化结果
        '''
        output_print={}
        output_print["status"] = status
        output_print["output"] = output_info
        if self.output:
            print(json.dumps(output_print))
        return json.dumps(output_print)
    def hosts_template_clear(self,template):
        '''
        clear template
        [eg1]#zabbix_api hosts_template_clear 10001
        [eg2]#zabbix_api hosts_template_clear "Template OS Linux"
        '''
        templates_info = self.template_get(template)
        if not len(templates_info):
            return {"status":"ERR","output":"Template not found"}
        print("clear template [%s]..."%templates_info[0]["name"])
        host_list = self._hosts_get()
        for host in host_list:
            self.zapi.host.update({"hostid": host[0],
                    "templates_clear": [
                                    {
                                        "templateid": templates_info[0]["templateid"]
                                    },
                    ]})
            print("host:[%s] ip:[%s] OK"%(host[2],host[3]))
    def hosts_template_link(self,template):
        '''
        link template
        [eg1]#zabbix_api hosts_template_link 10001
        [eg2]#zabbix_api hosts_template_link "Template OS Linux"
        '''
        templates_info = self.template_get(template)
        if not len(templates_info):
            return {"status":"ERR","output":"Template not found"}
        print("link template [%s]..."%templates_info[0]["name"])
        host_list = self._hosts_get()
        for host in host_list:
            self.zapi.host.massadd({
                "hosts":[
                    {
                        "hostid": host[0]
                    }
                ],
                
                "templates": [
                    {
                        "templateid":templates_info[0]["templateid"]
                    }
                ]
            })
            print("host:[%s] ip:[%s] OK"%(host[2],host[3]))

            
if __name__ == "__main__":
    print("zabbix_manager:[%s]"% __version__)
    parser=argparse.ArgumentParser(usage='\033[43;37m#%(prog)s function param [options]\033[0m')
   
    #####################################
    parser_report = parser.add_argument_group('report')
    parser_report.add_argument('--report',
                        nargs=3,
                        metavar=('item_name','date_from','date_till'),
                        dest='report',
                        help='eg:"CPU" "2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    parser_report.add_argument('--report_app',
                        nargs=3,
                        metavar=('app_name','date_from','date_till'),
                        dest='report_app',
                        help='eg:"CPU" "2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    parser_report.add_argument('--report_key',
                        nargs=3,
                        metavar=('item_key','date_from','date_till'),
                        dest='report_key',
                        help='eg:"system.cpu.util[,steal]" "2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    parser_report.add_argument('--report_available',
                        nargs=3,
                        metavar=('itemName','date_from','date_till'),
                        dest='report_available',
                        help='eg:"ping" "2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    parser_report.add_argument('--report_available2',
                        nargs=2,
                        metavar=('date_from','date_till'),
                        dest='report_available2',
                        help='eg:"2016-06-03 00:00:00" "2016-06-10 00:00:00"')
    parser_report.add_argument('--report_flow',
                        nargs=2,
                        metavar=('date_from','date_till'),
                        dest='report_flow',
                        help='eg: "2016-06-03 00:00:00" "2016-06-10 00:00:00"')

    # specialhost_get
    #####################################
    parser_condition = parser.add_argument_group('condition')
    parser_condition.add_argument('--hostgroupid',nargs=1,metavar=('hostgroupID'),dest='hostgroupid',\
            help='eg:"2,3,4"')
    parser_condition.add_argument('--hostid',nargs=1,metavar=('hostID'),dest='hostid',\
            help='eg:"10105,10106"')
    parser_condition.add_argument('--profile',nargs='?',metavar=('zabbixserver'),dest='profile',default='list_profile',help='选择配置文件')
    parser_condition.add_argument('--zero',dest='zero',default="OFF",help='入库时有0',action="store_true")
    parser_condition.add_argument('--item_key',
                                nargs=1,
                                metavar=('itemkey'),
                                dest='itemkey',
                                help='eg: "itemkey.example"')
    
    #####################################
    parser_output = parser.add_argument_group('output_input')
    parser_output.add_argument('-f',
                                nargs=1,
                                metavar=('switch.file'),
                                dest='switch_file',
                                help='eg: "switch1.txt"')
    parser_output.add_argument('--table',dest='terminal_table',default="OFF",help='show the terminaltables',action="store_true")
    parser_output.add_argument('--xls',nargs=1,metavar=('xls_name.xls'),dest='xls',\
                        help='export data to xls')
    parser_output.add_argument('--sign',nargs=1,default="OFF",dest='set_sepsign',\
                        help='set sepsign')
    parser_output.add_argument('--title',nargs=1,metavar=('title_name'),dest='title',\
                        help="add the xls's title")
    parser_output.add_argument('--sort',nargs=1,metavar=('num'),dest='output_sort',default="OFF",help='设置第几列进行排序')
    parser_output.add_argument('--desc',dest='sort_reverse',default="OFF",help='排序设置为降序',action="store_true")
    
    parser.add_argument('-d',dest='debug_output',default="OFF",help='show the debug info',action="store_true")
    

    #######################################################################################################
    if len(sys.argv)==1:
        from pydoc import render_doc
        print(render_doc(zabbix_api,title="[zabbix_api Documentation] %s"))
        print(parser.print_help())
        sys.exit()
    else:
        #args=parser.parse_args()
        args, unknown_args = parser.parse_known_args()
        # 默认为普通输出格式
        terminal_table = False
        if args.terminal_table != "OFF":
            terminal_table = True
        
        # 默认不输出debug信息
        debug = False
        if args.debug_output != "OFF":
            debug = True
        
        # 值默认为入库值
        value_type = False
        if args.zero != "OFF":
            value_type = True
        
        # 输出结果默认不排序
        output_sort=False
        if args.output_sort != "OFF":
            output_sort = args.output_sort[0]
        
        # 默认排序方式为升序
        sort_reverse = False
        if args.sort_reverse != "OFF":
            sort_reverse = True
        
        # 默认选中配置文件中的 zabbixserver section
        if args.profile != 'list_profile' :
            if args.profile:
                profile = args.profile
            else:
                if os.path.exists(zabbix_config):
                    config=ConfigParser.ConfigParser()
                    config.read(zabbix_config)
                    print(config.sections())
                else:
                    print("the %s is not found"%zabbix_config)
                sys.exit()
        else:
            profile = "zabbixserver"

        zabbix=zabbix_api(terminal_table,debug,output_sort=output_sort,sort_reverse=sort_reverse,profile = profile)
        if args.set_sepsign != "OFF":
            zabbix._set_sepsign(args.set_sepsign[0])
        #print(args)
        #print(unknown_args)
        export_xls = {"xls":"OFF",
                      "xls_name":"ceshi.xls",
                      "title":"OFF",
                      "title_name":u"测试"
        }
        
        select_condition = {"hostgroupID":"",
                "hostID":""
                }

        # 导出报表
        if args.xls:
            export_xls["xls"] = 'ON'
            export_xls["xls_name"]=args.xls[0]
        if args.title:
            if export_xls["xls"] == "ON":
                export_xls["title"] = 'ON'
                export_xls["title_name"]=unicode(args.title[0],"utf-8")
            else:
                print("the title params invalid")
        if args.switch_file:
            hosts_file=args.switch_file[0]
        else:
            hosts_file="./switch"
        
        if args.itemkey:
            itemkey_file=args.itemkey[0]
            fd = file(itemkey_file, "r" )  
            itemkey_list=[]
            for line in fd.readlines():  
                line=line.replace('\t','').replace('\n','').replace(' ','')
                itemkey_list.append(line)  
        else:
            itemkey_list=0

        # 选择特定机器
        if args.hostgroupid:
            select_condition["hostgroupID"]=args.hostgroupid[0]
            zabbix._host_set(hostgroupID=args.hostgroupid[0])
            
        if args.hostid:
            select_condition["hostID"] = args.hostid[0]
            zabbix._host_set(hostID=args.hostid[0])
        ############
        # report
        ############

        if args.report:
            zabbix._report(args.report[0],args.report[1],args.report[2],export_xls,select_condition)
        if args.report_app:
            zabbix._report_app(args.report_app[0],args.report_app[1],args.report_app[2],export_xls,select_condition)
        if args.report_key:
            zabbix._report_key(args.report_key[0],args.report_key[1],args.report_key[2],export_xls,select_condition)
        if args.report_flow:
            zabbix._report_flow(args.report_flow[0],args.report_flow[1],export_xls,hosts_file)
        if args.report_available:
            zabbix._report_available(args.report_available[0],args.report_available[1],args.report_available[2],export_xls,select_condition,value_type)
        if args.report_available2:
            zabbix._report_available2(args.report_available2[0],args.report_available2[1],export_xls,select_condition,itemkey_list=itemkey_list)
        if unknown_args:
            func = unknown_args.pop(0)
            try:
                cmd = getattr(zabbix, func)
            except:
                print('No such function: %s' % func)
                print(render_doc(zabbix))
                exit()

            try:
                kwargs = {}
                func_args = []
                for arg in unknown_args:
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        kwargs[key] = value
                    else:
                        func_args.append(arg)
                func_args = tuple(func_args)
                function_result = cmd(*func_args, **kwargs)
            except Exception,e:
                print(render_doc(cmd))
                warn_msg("DEBUG")
                import traceback
                traceback.print_exc()
