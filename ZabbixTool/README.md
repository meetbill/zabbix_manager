# ManagerTool

使用 zabbix_manage 有三种方式

> * [zabbix_api.py]---直接使用lib_zabbix/zabbix_api.py[推荐]
> * [main.sh]---------可将日常使用zabbix_api.py程序通过 main.sh 调用---可添加shell脚本实现新的功能
> * [main.py]---------main.py 实现比较复杂的功能

## 【目录】
----
* 安装
    * [安装及配置](docs/install.md)  
* zabbix_tool
    * zabbix_api
        * [运行及帮助](docs/zabbix_api/help.md)  
        * [hostgroup管理](docs/zabbix_api/hostgroup.md)  
        * [host管理](docs/zabbix_api/host.md)  
        * [用户管理](docs/zabbix_api/user.md)  
        * [mediatype管理](docs/zabbix_api/mediatype.md)  
        * [template管理](docs/zabbix_api/template.md)
        * [action管理](docs/zabbix_api/action.md)
* 调试 
    * [log](docs/log.md)  
* 产品功能设计
    * [产品设计](docs/arch.md)  
* [应用场景 ]  
    * [zabbix 安装后一键配置](docs/init.md)  
    * [服务器日常使用报表](docs/app/use_report.md)  
    * [服务可用行报表](docs/report.md)  
    * [查看最近问题](docs/app/issues.md)
    * [预估mysql存储大小](docs/app/mysql.md)  
    * [定时发送可用性报表(特定item)](docs/app/send_report1.md)  
    * [main.sh](docs/sh_main.md)  
