# 定时发送可用性报表(特定item)]  

## 需求

每周一发送上周特定机器的报表

### 每周一定时发送
```
(1)将ZabbixTool放在/opt目录下
(2)修改/opt/ZabbixTool/lib_zabbix/zabbix_config.ini中的账号密码
(3)修改/opt/ZabbixTool/main.py中发送邮箱及收件人
(4)创建定时任务每周一执行python /opt/ZabbixTool/main.py week_report

```
