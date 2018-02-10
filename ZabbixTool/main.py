#!/usr/bin/python
#coding=utf8
"""
# Author: Bill
# Created Time : 2016-10-25 10:01:13

# File Name: main.py
# Description:

"""
__version__ = "1.0.1"
import sys
import os
root_path = os.path.split(os.path.realpath(__file__))[0]
os.chdir(root_path)
sys.path.insert(0, os.path.join(root_path, 'lib_zabbix'))
sys.path.insert(0, os.path.join(root_path, 'py_tool/my_lib'))

from zabbix_api import zabbix_api
import json
zabbix_tool="/etc/zabbix_tool/zabbix_tool.ini"

def week_report():
    import date
    import datetime
    import pyMail
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
def create_config():
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read(zabbix_tool)
    applitions = config.get("create_file", "applitions")
    monit_config = config.get("create_file","monit_config")
    ignore_key_list = config.get("create_file","ignore_key").split(",")

    zabbix=zabbix_api(output=False)

    # 主机名和 IP 字典
    hostname_ip={}

    # 主机名和 监控项字典
    hostname_key={}

    host_list=zabbix.host_list()
    for host in host_list:
        # host[0]---hostid ,host[1]---hostname,host[2]---hostip
        hostid=host[0]
        hostname=host[1]
        hostip=host[2]
        hostname_ip[hostname]=hostip

        items = zabbix.item_list(hostid,applitions)
        if not items:
            items = []
        else:
            for ignore_key_item in ignore_key_list:
                if ignore_key_item in items:
                    items.remove(ignore_key_item)
            hostname_key[hostname]=items



    hostname_ip=json.dumps(hostname_ip,indent=4)
    #print hostname_ip
    hostname_key=json.dumps(hostname_key,indent=4)
    #print hostname_key

    # 生成配置文件
    config_file = "#!/usr/bin/python\n#coding=utf8\n"
    config_file = config_file + "hostname_ip="+hostname_ip+"\n"
    config_file = config_file + "hostname_key="+hostname_key+"\n"

    # 写入配置文件
    fo = open(monit_config, "wb")
    fo.write(config_file)
    fo.close()
def status():
    zabbix=zabbix_api(output=False)
    host_ip={}
    host_list=zabbix.host_list()
    #print host_list
    for host in host_list:
        host_ip[host[1]]=host[2]
    print host_ip
    #for host in host_list:
    issues_list=zabbix.issues()
    exception_host=[]

    ## 异常主机
    for issues in issues_list:
        exception_host.append(issues)
    exception_host=list(set(exception_host))
    print "exception_host",exception_host

    ## 正常主机
    normal_host=[]
    for host in host_ip:
        if host not in exception_host:
            normal_host.append(host)
    print "normal_host",normal_host
def version():
    print __version__


# 函数作为模块调用 不必理会
if __name__ == '__main__':
    import sys, inspect
    if len(sys.argv) < 2:
        print "Usage:"
        for k, v in sorted(globals().items(), key=lambda item: item[0]):
            if inspect.isfunction(v) and k[0] != "_":
                args, __, __, defaults = inspect.getargspec(v)
                if defaults:
                    print sys.argv[0], k, str(args[:-len(defaults)])[1:-1].replace(",", ""), \
                          str(["%s=%s" % (a, b) for a, b in zip(args[-len(defaults):], defaults)])[1:-1].replace(",", "")
                else:
                    print sys.argv[0], k, str(v.func_code.co_varnames[:v.func_code.co_argcount])[1:-1].replace(",", "")
        sys.exit(-1)
    else:
        func = eval(sys.argv[1])
        args = sys.argv[2:]
        try:
            r = func(*args)
        except Exception, e:
            print "Usage:"
            print "\t", "python %s" % sys.argv[1], str(func.func_code.co_varnames[:func.func_code.co_argcount])[1:-1].replace(",", "")
            if func.func_doc:
                print "\n".join(["\t\t" + line.strip() for line in func.func_doc.strip().split("\n")])
            print e
            r = -1
            import traceback
            traceback.print_exc()
        if isinstance(r, int):
            sys.exit(r)
