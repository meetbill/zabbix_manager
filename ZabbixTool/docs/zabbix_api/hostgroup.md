## hostgroups 管理

**主机组列表**

```bash
#zabbix_api hostgroup_get --table
----------------------------------------------以下为程序输出
+-------------+------------------+
| hostgroupID | hostgroupName    |
+-------------+------------------+
| 1           | Templates        |
| 2           | Linux servers    |
| 4           | Zabbix servers   |
| 5           | Discovered hosts |
| 6           | Virtual machines |
| 7           | Hypervisors      |
+-------------+------------------+

```
**创建主机组**

```bash
#zabbix_api hostgroup_create "ceshi"
----------------------------------------------以下为程序输出
添加主机组:ceshi  hostgroupID : [u'11']
```
