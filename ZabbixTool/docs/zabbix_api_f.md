# zabbix_manager api 手册

以下方法只是 zabbix_api 的冰山一角，详情可以直接使用zabbix_api

* [使用方法](#使用方法)
* [zabbix api 功能](#zabbix-api-功能)
	* [hostgroups 管理](#hostgroups-管理)
	* [usergroups 管理](#usergroups-管理)
	* [host 管理](#host-管理)
	* [mediatype 管理](#mediatype-管理)
	* [issues 管理](#issues-管理)

# 使用方法

修改配置文件

第一步是修改配置文件zabbix_config.ini 

主要是修改zabbix的ip、端口、admin账户、admin密码
```bash
$ cat zabbix_config.ini

[zabbixserver]
server = 192.168.199.128
port = 80
user = admin
password = zabbix
``` 
# zabbix api 功能
## hostgroups 管理

(1)list hostgroups
```bash
#python zabbix_api.py --group --table
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
(2)add a hostgroup
```bash
# python zabbix_api.py --hostgroup_add "ceshi"
----------------------------------------------以下为程序输出
添加主机组:ceshi  hostgroupID : [u'11']
```
## usergroups 管理
(1)list usergroups
```bash
#python zabbix_api.py --usergroup --table
----------------------------------------------以下为程序输出
+----------+---------------------------+------------+--------------+
| usrgrpid | name                      | gui_access | users_status |
+----------+---------------------------+------------+--------------+
| 7        | Zabbix administrators     | 0          | 0            |
| 8        | Guests                    | 0          | 0            |
| 9        | Disabled                  | 0          | 0            |
| 11       | Enabled debug mode        | 0          | 0            |
| 12       | No access to the frontend | 2          | 0            |
+----------+---------------------------+------------+--------------+
```
(2)add a usergroup
```bash
# python zabbix_api.py --usergroup_add "op" "HostgroupName"
```
## host 管理
(1)list hosts
```bash
#python zabbix_api.py --host --table
```
## mediatype 管理
(1)list mediatype
```bash
#python zabbix_api.py --mediatype --table
```

(2)add a mediatype
```bash
# python zabbix_api.py --mediatype_add mediaName scriptName
```

(3)delete a mediatype
```bash
# python zabbix_api.py --mediatype_del mediaName
```
## issues 管理
可以直接看到最近问题
```bash
#python zabbix_api.py --issues --table
----------------------------------------------以下为程序输出
分别为[主机名]--[触发器名称]--[触发时间]--[最新值]
+----------+----------------------------------------------+---------------------+-----------+
| hostname | trigger                                      | time                | prevvalue |
+----------+----------------------------------------------+---------------------+-----------+
| net139   | Free disk space is less than 20% on volume / | 2016/10/26 09:10:44 | 18.0161   |
| net137   | Free disk space is less than 20% on volume / | 2016/10/26 09:11:32 | 18.0161   |
+----------+----------------------------------------------+---------------------+-----------+
```
