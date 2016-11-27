# ManagerTool

使用 zabbix_manage 有三种方式

> * [zabbix_api.py]---直接使用lib_zabbix/zabbix_api.py[推荐]
> * [main.sh]---------可将日常使用zabbix_api.py程序通过 main.sh 调用---可添加shell脚本实现新的功能
> * [main.py]---------main.py 实现比较复杂的功能

## 【目录】
----
[1 使用zabbix_manage ]  
........[1.1 main.sh](docs/sh_main.md)  

[2 直接使用zabbix_api.py ]  
........[2.1 配置报警](docs/alert.md)  
........[2.2 导入模板](docs/template.md)  
........[2.3 agent自动加入监控](docs/config.md)  
........[2.4 导出report报表](docs/report.md)  
........[2.5 预估mysql存储大小](docs/mysql.md)  

[3 调试 ]  
........[3.1 log](docs/log.md)  

[4 zabbix_api ]  
........[4.1 zabbix_api简介](docs/zabbix_api.md)  
........[4.2 zabbix_api功能](docs/zabbix_api_f.md)  
[5 产品功能设计 ]  
........[5.1 产品设计](docs/arch.md)  
[6 应用场景 ]  
........[6.1 定时发送可用性报表(特定item)](docs/app/send_report1.md)  

