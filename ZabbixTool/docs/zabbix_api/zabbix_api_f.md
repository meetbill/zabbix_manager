# zabbix_manager api 手册

以下方法只是 zabbix_api 的冰山一角，详情可以直接#python zabbix_api.py 获取 zabbix_api 使用方法

* [zabbix api 功能](#zabbix-api-功能)
	* [usergroups 管理](#usergroups-管理)
	* [host 管理](#host-管理)
	* [mediatype 管理](#mediatype-管理)
	* [issues 管理](#issues-管理)
	* [action 管理](#action-管理)

**add a usergroup**

```bash
#zabbix_api usergroup_create "op" "HostgroupName"
```

## mediatype 管理

**list mediatype**

```bash
#zabbix_api mediatype_get --table
```

**add a mediatype**

```bash
#zabbix_api mediatype_create mediaName scriptName
```

**delete a mediatype**

```bash
#zabbix_api mediatype_del mediaName
```
## issues 管理

**查看最近问题**

```bash
#zabbix_api issues --table
----------------------------------------------以下为程序输出
分别为[主机名]--[触发器名称]--[触发时间]--[最新值]
+----------+----------------------------------------------+---------------------+-----------+
| hostname | trigger                                      | time                | prevvalue |
+----------+----------------------------------------------+---------------------+-----------+
| net139   | Free disk space is less than 20% on volume / | 2016/10/26 09:10:44 | 18.0161   |
| net137   | Free disk space is less than 20% on volume / | 2016/10/26 09:11:32 | 18.0161   |
+----------+----------------------------------------------+---------------------+-----------+
```
## action 管理

**zabbix自动发现配置**


第一步是修改配置文件lib_zabbix/zabbix_config.ini 

主要是修改zabbix的ip、端口、admin账户、admin密码

```bash
#!/bin/bash
zabbix_api drule_create "agent discovery" "192.168.199.1-252"
zabbix_api  action_discovery_create "Auto discovery" store
``` 
自动发现规则是zabbix server去扫描一个网段，把在线的主机添加到Host列表中。适合内网下

直接执行在本目录执行 
直接执行程序后，会执行操作如下

(1)创建自动发现规则

(2)自动创建action，根据action，自动将discovery的机器加到特定的主机群组中，同时链接上linux模板

**zabbix客户端自动注册(推荐)**

这次是Active agent主动联系zabbix server，最后由zabbix server将这些agent加到host里。对于需要部署特别多服务器的人来说，这功能相当给力。

(1)agent

修改agent配置文件
```
ServerActive=66.175.222.222
Hostname=auto-reg-test01
HostMetadataItem=system.uname
```
(2)server

步骤：configuration>>actions>>Event source（选择Auto registration）>>CreaAction

* Action选项卡-----------定义Action名称：Action_for_autoreg
* Conditions选项卡------添加:Host metadata like Linux
* Operations选项卡-----添加:Add host,Add to host group ,Link to template

直接执行python main.py即可

执行后需要输入action_name和hostgroup_name

```
#!/bin/bash
zabbix_api action_autoreg_create "ceshi_action" "Linux servers"
```
