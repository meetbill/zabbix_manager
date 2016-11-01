#!/usr/bin/python
#coding=utf8
"""
# Author: Bill
# Created Time : 2016-10-25 10:01:13

# File Name: main.py
# Description:

"""
import sys
import os
import datetime
root_path = os.path.split(os.path.realpath(__file__))[0]
os.chdir(root_path)
sys.path.insert(0, os.path.join(root_path, 'lib_zabbix'))
sys.path.insert(0, os.path.join(root_path, 'py_menu/my_lib'))

import date
from zabbix_api import zabbix_api
import pyMail

def week_report():
    weekreport_name = "/opt/weekreport.xls"
    d = datetime.datetime.now()
    date_from,date_to = date.week_get(d)
    print date_from,date_to
    terminal_table = False
    zabbix=zabbix_api(terminal_table)
    itemkey_list=['vm.memory.size[available]', 'agent.ping', 'vfs.fs.size[/,pfree]', 'system.cpu.load[percpu,avg1]']
    export_xls = {"xls":"ON",
                  "xls_name":weekreport_name,
                  "title":"ON",
                  "title_name":u"周报"
    }
    select_condition = {"hostgroupID":"",
            "hostID":""
    }
    zabbix.report_available2(str(date_from),str(date_to),export_xls,select_condition,itemkey_list=itemkey_list)
    
    # 1 初始化发送邮件类
    # 25 端口时，usettls = False
    # 465 端口时,usettls = True
    usettls = False
    sml = pyMail.SendMailDealer('mail_address','mail_pwd','smtp.gmail.com','25',usettls = usettls)
    # 2 设置邮件信息
    # 参数包括("收件人","标题","正文","格式html/plain","附件路径1","附件路径2")
    sml.setMailInfo('paramiao@gmail.com','测试','正文','plain',weekreport_name)
    # 3 发送邮件
    sml.sendMail()


    
    
    

# 函数作为模块调用 不必理会
if __name__ == '__main__':
    import sys
    import inspect

    if len(sys.argv) < 2:
        print "Usage:"
        for k, v in globals().items():
            if inspect.isfunction(v) and k[0] != "_":
                print sys.argv[0], k, str(v.func_code.co_varnames[:v.func_code.co_argcount])[1:-1].replace(",", "")
        sys.exit(-1)
    else:
        func = eval(sys.argv[1])
        args = sys.argv[2:]
        func(*args)
