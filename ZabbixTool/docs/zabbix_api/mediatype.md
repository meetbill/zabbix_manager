## mediatype(报警方式)管理

### mediatype 管理

**mediatype列表**

```bash
[root@Linux lib_zabbix]# python zabbix_api.py mediatype_get --table
1.2.2
+-------------+------+-------------+-----------+-------------+
| mediatypeid | type | description | exec_path | users       |
+-------------+------+-------------+-----------+-------------+
| 1           | 0    | Email       |           |             |
| 2           | 3    | Jabber      |           |             |
| 3           | 2    | SMS         |           |             |
| 4           | 1    | alerts      | alerts.py | op          |
|             |      |             |           | ceshi_user2 |
|             |      |             |           | ceshi_user1 |
|             |      |             |           | ceshi_user  |
|             |      |             |           |             |
+-------------+------+-------------+-----------+-------------+
sum:  4
```

**创建 mediatype**

```bash
[root@Linux ~]#zabbix_api mediatype_create "alerts2" "alerts.py" 
1.2.2
{"status": "OK", "output": "create mediatype:[alerts2] id:[6] OK"}
```

**删除 mediatype**

```bash
[root@Linux ~]#zabbix_api mediatype_delete alerts2
1.2.2
{"status": "OK", "output": "delete mediatype:[alerts2] OK"}
```
