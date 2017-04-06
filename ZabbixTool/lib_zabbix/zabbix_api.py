#!/usr/bin/python 
#coding:utf-8 
#
# {"status":"OK","output":output}
from __future__ import print_function
__version__ = "1.2.3"
 
import json 
import urllib2 
from urllib2 import URLError 
import ConfigParser
import sys
import os
import time
import unicodedata
import config
from pydoc import render_doc
from w_lib.zabbix_api_lib import ZabbixAPI

root_path = os.path.split(os.path.realpath(__file__))[0]
os.chdir(root_path)
sys.path.insert(0, os.path.join(root_path, 'w_lib'))
zabbix_config = '/etc/zabbix_tool/zabbix_config.ini'

from colorclass import Color
from terminaltables import SingleTable
import my_sort
import my_compare
import XLSWriter
from BLog import Log
import argparse
import logging
reload(sys)
sys.setdefaultencoding("utf-8")
def err_msg(msg):
    print("\033[41;37m[Error]: %s \033[0m"%msg)
    exit()
def warn_msg(msg):
    print("\033[43;37m[Warning]: %s \033[0m"%msg)

class zabbix_api: 
    def __init__(self,terminal_table=False,debug=False,output=True,output_sort=False,sort_reverse=False,profile="zabbixserver"): 
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
            if debug:
                self.zapi=ZabbixAPI(server="http://%s:%s"%(self.server,self.port),log_level=logging.DEBUG)
            else:
                self.zapi=ZabbixAPI(server="http://%s:%s"%(self.server,self.port))
            self.zapi.login(self.user,self.password)
            self.__host_id__ = ''
            self.__hostgroup_id__ = ''
        else:
            print("the config file [%s] is not exist"%zabbix_config)
            exit(1)

        self.url = 'http://%s:%s/api_jsonrpc.php' % (self.server,self.port) #修改URL
        self.header = {"Content-Type":"application/json"}
        self.terminal_table=terminal_table
        self.authID = self.__user_login() 
        logpath = "/tmp/zabbix_tool.log"
        self.logger = Log(logpath,level="debug",is_console=debug, mbs=5, count=5)

        self.sepsign=None
    def __user_login(self): 
        data = json.dumps({
                           "jsonrpc": "2.0",
                           "method": "user.login",
                           "params": { 
                                      "user": self.user, #修改用户名
                                      "password": self.password #修改密码
                                      },
                           "id": 0 
                           })
         
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
     
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("\033[041m 用户认证失败，请检查 !\033[0m", e)
            exit(1)
        else: 
            response = json.loads(result.read()) 
            result.close() 
            self.authID = response['result'] 
            return self.authID 
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
                      "selectParentTemplates":["host"],
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
                        template =  template_item["host"] + '\n'+ template
                output.append([host['hostid'],host['name'],host['interfaces'][0]["ip"],status[host['status']],available[host['available']],template])
            else:
                #output.append([host['hostid'],host['name'],host['interfaces'][0]["ip"],status[host['status']],available[host['available']]])
                #self.__generate_output(output)
                return host['hostid']
        self.__generate_output(output)
        return 0
    def __host_get(self,hostgroupID='',hostID=''): 
        '''
        内部函数
        返回特定主机组下的主机列表和某个主机的列表
        '''
        #  (1)Return all hosts.
        #  (2)Return only hosts that belong to the given groups.
        #  (3)Return only hosts with the given host IDs.
        all_host_list=[]
        if hostgroupID:
            group_list=[]
            group_list[:]=[]
            for i in hostgroupID.split(','):
                group_list.append(i)
            data=json.dumps({
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                          "groupids":group_list,
                          "output": "extend",
                          "selectInterfaces":["ip"]
                              },
                    "auth":self.authID,
                    "id": 1
                    })
        elif hostID:
            host_list=[]
            host_list[:]=[]
            for i in hostID.split(','):
                host_list.append(i)
            data=json.dumps({
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                          "hostids":host_list,
                          "output": "extend",
                          "selectInterfaces":["ip"]
                              },
                    "auth":self.authID,
                    "id": 1
                    })
        else:
            data=json.dumps({
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                          "output": "extend",
                          "selectInterfaces":["ip"]
                              },
                    "auth":self.authID,
                    "id": 1
                    })

        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            if hasattr(e, 'reason'): 
                print('We failed to reach a server.') 
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'): 
                print('The server could not fulfill the request.')
                print('Error code: ', e.code)
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return []
            for host in response['result']:      
                all_host_list.append((host['hostid'],host['host'],host['name'],host['interfaces'][0]["ip"]))
            return all_host_list
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
            var['groupid'] = self.hostgroup_get(i)
            group_list.append(var)
        for i in templateName.split(','):
            var={}
            templates_info=self.template_get(i)
            if not len(templates_info):
                continue
            var['templateid']=templates_info[0]['templateid']
            template_list.append(var)   

        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"host.create", 
                           "params":{ 
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
                                     }, 
                           "auth":self.authID, 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e)
        else: 
            response = json.loads(result.read()) 
            result.close() 
            return self.__generate_return("OK","create host:[%s] hostid:[%s] OK"%(hostname,response['result']['hostids'][0]))
    def host_status(self,hostname,status="Disabled"):
        '''
        Turns a host Enabled or Disabled[default]
        [eg1]#zabbix_api host_status "ceshi_host" "Disabled"
        [eg2]#zabbix_api host_status "ceshi_host" "Enabled"
        '''
        status_flag={"Enabled":0,"Disabled":1}
        data=json.dumps({
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
            "hostid": self.host_get(hostname),
            "status": status_flag[status]
            },
            "auth":self.authID,
            "id": 1
        })
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key, self.header[key])       
        try: 
            result = urllib2.urlopen(request)
        except URLError as e: 
            print("Error as ", e)
        else: 
            response = json.loads(result.read()) 
            result.close()
            print('----主机现在状态------------')
            self.host_get(hostname)
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
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"hostgroup.get", 
                           "params":{ 
                                     "output": "extend", 
                                     "filter": { 
                                                "name": hostgroupName 
                                                } 
                                     }, 
                           "auth":self.authID, 
                           "id":1, 
                           }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e )
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return 0
            output = []
            output.append(["hostgroupID","hostgroupName"])
            for group in response['result']:
                if  len(hostgroupName)==0:
                    output.append([group["groupid"],group["name"]])
                else:
                    self.hostgroupID = group['groupid'] 
                    return group['groupid'] 
            self.__generate_output(output)
    def __hostgroup_get_name(self, groupid=''): 
        '''
        内部函数
        根据hostgroup id 获得主机群组的 name
        '''
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"hostgroup.get", 
                           "params":{ 
                                     "output": "extend", 
                                     "filter": { 
                                                "groupid": groupid
                                                } 
                                     }, 
                           "auth":self.authID, 
                           "id":1, 
                           }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e )
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return 0
            for group in response['result']:
                if  len(groupid)==0:
                    print("hostgroup:  \033[31m%s\033[0m \tgroupid : %s" %(group['name'],group['groupid']))
            else:
                return group['name'] 
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
    def item_get(self, host_ID,itemName=''): 
        '''
        return a item list
        [eg1]#zabbix_api item_get 10084
        [eg2]#zabbix_api item_get 10084 "Free disk"
        '''
        # @return list
        # list_format
        # [item['itemid'],item['name'],item['key_'],item['delay'],item['value_type']]

        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"item.get", 
                           "params":{ 
                                     "output":"extend",
                                     "hostids":host_ID,
                                     }, 
                           "auth":self.authID, 
                           "id":1, 
                           }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e)
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return 0
            output=[]
            output[:]=[]
            output.append(["itemid","name","key_","update_time","value_type","history"])
            for item in response['result']:
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
                    output.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history']])
                else:
                    if item['name']==itemName:
                        output.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history']])
                    else:
                        if my_compare.my_compare(item['name'],itemName,self.sepsign):
                            output.append([item['itemid'],item['name'],item['key_'],item['delay'],item['value_type'],item['history']])
            self.__generate_output(output)
            if len(output[1:]):
                return output[1:]
            else:
                return 0
    def __item_search(self,item_ID=''): 
        '''
        内部函数
        根据 某个item_ID 确定 item 的value_type 
        '''
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"item.get", 
                           "params":{ 
                                     "output":"extend",
                                     "itemids":item_ID,
                                     }, 
                           "auth":self.authID, 
                           "id":1, 
                           }) 
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e)
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return 0
            return response['result'][0]['value_type']
    # history
    def history(self,item_ID,date_from,date_till): 
        '''
        return history of item
        [eg1]#zabbix_api history 23296 "2016-08-01 00:00:00" "2016-09-01 00:00:00"
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
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"history.get", 
                           "params":{ 
                                     "time_from":time_from,
                                     "time_till":time_till,
                                     "output": "extend",
                                     "history": history,
                                     "itemids": item_ID,
                                     "sortfield":"clock",
                                     "limit": 10080
                                     }, 
                           "auth":self.authID, 
                           "id":1, 
                           }) 
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e)
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                warn_msg("not have history_data")
                debug_info=str([history,item_ID,time_from,time_till,"####not have history_data"])
                self.logger.debug(debug_info)
                return 0.0
            for history_info in response['result']:
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
                    hostgroup_name = self.__hostgroup_get_name(i)
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
    def _report(self,itemName,date_from,date_till,export_xls,select_condition): 

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
            itemid_all_list = self.item_get(host_info[0],itemName)
            if itemid_all_list == 0:
                debug_msg="host %s No related monitoring items found"% host_info[0]
                self.logger.debug(debug_msg)
                continue
            for itemid_sub_list in itemid_all_list:
                itemid = itemid_sub_list[0]
                item_name = itemid_sub_list[1]
                item_key = itemid_sub_list[2]
                history_type = itemid_sub_list[4]
                debug_msg="itemid:%s"%itemid
                self.logger.debug(debug_msg)
                report_min,report_max,report_avg = self.__trend_get(itemid,time_from,time_till)
                if history_type=="3":
                    report_min=int(report_min)
                    report_max=int(report_max)
                    report_avg=int(report_avg)
                report_min=str(report_min)
                report_max=str(report_max)
                report_avg=str(report_avg)
                itemid=str(itemid)
                report_output.append([host_info[0],host_info[2],item_name,report_min,report_max,report_avg])
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
            table_show.append(["hostid","name","itemName","min","max","avg"])
            for report_item in report_output:
                table_show.append(report_item)
            table=SingleTable(table_show)
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
                xlswriter.add_image("python.bmg",0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_image("python.bmg",0,0,sheet_name=sheetName)
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
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"trend.get", 
                           "params":{ 
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
                                     }, 
                           "auth":self.authID, 
                           "id":1, 
                           }) 

        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e )
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                debug_info=str([item_ID,time_from,time_till,"####not have trend_data"])
                self.logger.debug(debug_info)
                return 0,0,0
            sum_num_value = 0
            sum_avg_value = 0
            for result_info in response['result']:
                hour_num_string = unicodedata.normalize('NFKD',result_info['num']).encode('ascii','ignore')
                hour_num=eval(hour_num_string)
                sum_num_value = sum_num_value + hour_num
                
                hour_avg_string = unicodedata.normalize('NFKD',result_info['value_avg']).encode('ascii','ignore')
                hour_avg=eval(hour_avg_string)
                sum_avg_value = sum_avg_value + hour_avg
            trend_sum = len(response['result'])
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
            table=SingleTable(table_show)
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
                xlswriter.add_image("python.bmg",0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_image("python.bmg",0,0,sheet_name=sheetName)
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
            table=SingleTable(table_show)
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
                xlswriter.add_image("python.bmg",0,0,4,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_image("python.bmg",0,0,sheet_name=sheetName)
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
                xlswriter.add_image2("python.bmg",0,0,6,title_name=export_xls["title_name"],sheet_name=sheetName)
            else:
                xlswriter.add_image2("python.bmg",0,0,sheet_name=sheetName)
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
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "alert.get",
                "params": {
                    "output":"extend",
                    "time_from":time_from,
                    "time_till":time_till
                },
                "auth":self.authID,
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
             
        try: 
            result = urllib2.urlopen(request) 
        except Exception,e: 
            print(e)
        else: 
            response = json.loads(result.read()) 
            if len(response['result']) == 0:
                print("no alert")
                return 0
            for alert in response['result']:      
                timeArray = time.localtime(int(alert['clock']))
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                print(alert['alertid'],otherStyleTime,alert['sendto'],alert['subject'],alert['status'])
            result.close() 
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
                params = {"output":"extend","templateids":[int(identifier)]}
            except:
                params = {"output":"extend","filter":{"name":identifier}}
            return self.zapi.template.get(params)
        else:
            params = {"output":"extend"}
            result = self.zapi.template.get(params)
            output = []
            output[:] = []
            output.append(["id","template"])
            for template in result: 
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
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method": "configuration.import", 
                           "params": { 
                                      "format": "xml", 
                                      "rules": rules,
                                      "source":template
                                      }, 
                           "auth":self.authID, 
                           "id":1, 
                           })
         
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e )
        else: 
            response = json.loads(result.read()) 
            result.close() 
            return self.__generate_return("OK","import template [%s] OK"%template_path)
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
    # drule(discoveryRules)
    def drule_get(self,druleName=''): 
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "drule.get",
                "params": {
                          "output": "extend",
                          "filter":{"name":druleName} 
                          },
                "auth":self.authID,
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            if hasattr(e, 'reason'): 
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'): 
                print('The server could not fulfill the request.' )
                print('Error code: ', e.code )
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return 0
            output = []
            output[:] = []
            output.append(["druleid","name","iprange","status"])
            status={"0":Color('{autobggreen}Enabled{/autobggreen}'),"1":Color('{autobgred}Disabled{/autobgred}')}
            for drule in response['result']:      
                if len(druleName)==0:
                    output.append([drule['druleid'],drule['name'],drule['iprange'],status[drule['status']]])
                else:
                    return drule['druleid']
            self.__generate_output(output)
            return 0
    def drule_create(self, druleName,iprange): 
        if self.drule_get(druleName):
            print("\033[041mthis druleName is exists\033[0m" )
            sys.exit(1)

        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"drule.create", 
                           "params": {
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
                                      },
                           "auth":self.authID, 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e )
        else: 
            response = json.loads(result.read()) 
            result.close() 
            print("add drule : \033[42m%s\033[0m \tid :\033[31m%s\033[0m" % (druleName, response['result']['druleids'][0]))
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
        data=json.dumps({
                "jsonrpc": "2.0",
                "method": "action.get",
                "params": {
                          "output": "extend",
                          "filter":{
                              "name":actionName,
                          } 
                          },
                "auth":self.authID,
                "id": 1
                })
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            if hasattr(e, 'reason'): 
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'): 
                print('The server could not fulfill the request.')
                print('Error code: ', e.code )
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return 0
            output = []
            output[:] = []
            output.append(["actionid","name","eventsource","status"])
            status={"0":Color('{autobggreen}Enabled{/autobggreen}'),"1":Color('{autobgred}Disabled{/autobgred}')}
            eventsource={"0":"triggers","1":"discovery","2":"registration","3":"internal"}
            for action in response['result']:      
                if len(actionName)==0:
                    self.logger.info(str(action))
                    output.append([action['actionid'],action['name'],eventsource[action['eventsource']],status[action['status']]])
                else:
                    self.logger.info(str(action))
                    return action['actionid']
            self.__generate_output(output)
            return 0
    def action_autoreg_create(self, actionName,hostgroupName): 
        '''
        create autoreg action
        [eg1]#zabbix_api action_autoreg_create "ceshi_action" "Linux servers"
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
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"action.create", 
                           "params": {
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
                                            "value": "Linux"
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
                           },
                           "auth":self.authID, 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e)
        else: 
            response = json.loads(result.read()) 
            result.close() 

            output_print={}
            output_print["status"]="OK"
            output_print["output"]="add action:%s id:%s" %(actionName, response['result']['actionids'][0]) 
            if self.output:
                print(json.dumps(output_print))
            return json.dumps(output_print)
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
        data = json.dumps({ 
            "jsonrpc": "2.0",
            "method": "action.create",
            "params": {
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
            },
            "auth":self.authID, 
            "id": 1
        })
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e )
        else: 
            response = json.loads(result.read()) 
            result.close() 

            output_print={}
            output_print["status"]="OK"
            output_print["output"]="add action:%s id:%s" %(actionName, response['result']['actionids'][0]) 
            if self.output:
                print(json.dumps(output_print))
            return json.dumps(output_print)
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
            exit(1)
        templateName = "Template OS Linux"
        templateID=self.template_get(templateName)
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"action.create", 
                           "params": {
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
                           },
                           "auth":self.authID, 
                           "id":1                   
        }) 
        request = urllib2.Request(self.url, data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e)
        else: 
            response = json.loads(result.read()) 
            result.close() 
            print("add action : \033[42m%s\033[0m \tid :\033[31m%s\033[0m" %(actionName, response['result']['actionids'][0]))
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
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"trigger.get", 
                           "params":{ 
                               "output":"extend",
                               "hostids":host_ID,
                               "expandData":"1",
                               "monitored":1,
                               #"selectItems":"extend",
                               "selectItems":["key_","prevvalue","units","value_type"],
                               "expandDescription":"1"
                           }, 
                           "auth":self.authID, 
                           "id":1, 
        }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e )
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                return 0
            for trigger in response['result']:
                all_trigger_list.append((trigger["triggerid"],trigger["description"],trigger["items"][0]["key_"],trigger["items"][0]["prevvalue"],trigger["items"][0]["units"]))
            return all_trigger_list
    def issues(self): 
        '''
        output issues list
        [eg1]#zabbix_api issues
        '''
        #trigger_get

        all_trigger_list=[]
        data = json.dumps({ 
                           "jsonrpc":"2.0", 
                           "method":"trigger.get", 
                           "params":{ 
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
                               },
                           }, 
                           "auth":self.authID, 
                           "id":1, 
        }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e)
        else: 
            response = json.loads(result.read()) 
            result.close() 
            if len(response['result']) == 0:
                print(":) no issues")
                return 0
            output = []
            output[:] = []
            output.append(["hostname","trigger","time","prevvalue"])
            for trigger in response['result']:
                output.append([trigger["hosts"][0]["name"],trigger["description"],time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(trigger["lastchange"]))),trigger["items"][0]["prevvalue"]+trigger["items"][0]["units"]])
            self.__generate_output(output)
            return 0
    def __event_get(self, triggerid='',time_from='',time_till='',value=""): 
        '''
        The method allows to retrieve events according to the given parameters.
        用于可用性报表使用
        '''
        if value:
            data = json.dumps({ 
                               "jsonrpc":"2.0", 
                               "method":"event.get", 
                               "params":{ 
                                         "output":"extend",
                                         "objectids": triggerid,
                                         "time_from":time_from,
                                         "time_till":time_till,
                                         "value":"1",
                                         }, 
                               "auth":self.authID, 
                               "id":1, 
                               }) 
        else:
            data = json.dumps({ 
                               "jsonrpc":"2.0", 
                               "method":"event.get", 
                               "params":{ 
                                         "output":"extend",
                                         "objectids": triggerid,
                                         "time_from":time_from,
                                         "time_till":time_till,
                                         }, 
                               "auth":self.authID, 
                               "id":1, 
                               }) 
         
        request = urllib2.Request(self.url,data) 
        for key in self.header: 
            request.add_header(key, self.header[key]) 
              
        try: 
            result = urllib2.urlopen(request) 
        except URLError as e: 
            print("Error as ", e )
        else: 
            response = json.loads(result.read()) 
            result.close() 
            # 如果输出值为0时，可用性为100%
            if len(response['result']) == 0:
                return 0
            # 当输出的value 包含0值时
            if not value:
                # 当输出只有1个值时，可用性为100%
                if len(response['result']) == 1:
                    return 0
                # 输出的列表第一个值为0,表示添加此监控项的时间在时间条件之间，应根据添加监控项的时间为起始时间
                if response['result'][0]["value"] == "0":
                    time_from_record = int(response['result'][0]["clock"])
                    response["result"]=response["result"][1:]
                    time_range = time_till - time_from_record
                    time_event_sum = 0
                    time_diff = 0
                    
                    for i in range(len(response["result"])):
                        # 如果取的时间值time_till恰好是还在故障时间
                        # 则最后一个值为1，同时将time_till - 最后发生故障的时间的值 并入到故障时间内
                        if (i == (len(response["result"])-1)) and response['result'][i]["value"] == "1":
                            time_diff = int(time_till) - int(response["result"][i]["clock"])
                            time_event_sum = time_event_sum + time_diff
                            break
                        if(i%2) == 0:
                            time_diff = int(response["result"][i+1]["clock"]) - int(response["result"][i]["clock"])
                            time_event_sum = time_event_sum + time_diff
                    event_diff = float('%0.4f'%(time_event_sum * 100 / float(time_range)))
                    return event_diff
                else:
                    time_from_record = time_from
                    time_range = time_till - time_from_record
                    time_event_sum = 0
                    time_diff = 0
                    if len(response["result"])%2 == 1:
                           return 0
                    for i in range(len(response["result"])):
                        if(i%2) == 0:
                            time_diff = int(response["result"][i+1]["clock"]) - int(response["result"][i]["clock"])
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
                table=SingleTable(output_list)
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
    print( __version__)
    parser=argparse.ArgumentParser(usage='\033[43;37m#%(prog)s function param [options]\033[0m')
   
    #####################################
    parser_report = parser.add_argument_group('report')
    parser_report.add_argument('--report',
                        nargs=3,
                        metavar=('item_name','date_from','date_till'),
                        dest='report',
                        help='eg:"CPU" "2016-06-03 00:00:00" "2016-06-10 00:00:00"')
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
        print(render_doc(zabbix_api))
        print(parser.print_help())
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
                    config = ConfigParser.ConfigParser()
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
            except TypeError:
                print(render_doc(cmd))
                exit()
