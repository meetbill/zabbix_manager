# 用户管理

**用户组列表**

```bash
[root@Linux ~]# zabbix_api usergroup_get --table
1.2.2
+----------+---------------------------+------------+--------------+-------+
| usrgrpid | name                      | gui_access | users_status | users |
+----------+---------------------------+------------+--------------+-------+
| 7        | Zabbix administrators     | 0          | 0            | Admin |
| 8        | Guests                    | 0          | 0            | guest |
| 9        | Disabled                  | 0          | 1            |       |
| 11       | Enabled debug mode        | 0          | 0            |       |
| 12       | No access to the frontend | 2          | 0            |       |
| 13       | op                        | 0          | 0            | op    |
+----------+---------------------------+------------+--------------+-------+
sum:  6
```

**创建用户组**
```bash
[root@Linux ~]# zabbix_api usergroup_create "ceshi_usergroup" "Linux servers"
1.2.2
{"status": "OK", "output": "create usergroup:[ceshi_usergroup] id:[18] is OK"}
```

**删除用户组**
```bash
[root@Linux ~]# zabbix_api usergroup_delete "ceshi_usergroup"
1.2.2
{"status": "OK", "output": "delete usergroup [ceshi_usergroup] OK"}
```

**用户列表**
```bash
[root@Linux ~]#zabbix_api user_get --table
1.2.2
+--------+-------+--------+-----+
| userid | alias | name   | url |
+--------+-------+--------+-----+
| 1      | Admin | Zabbix |     |
| 2      | guest |        |     |
| 3      | op    |        |     |
+--------+-------+--------+-----+
sum:  3
```

**创建用户**
```
[root@Linux ~]#zabbix_api user_create "ceshi_user4" "123456" "op" "alerts" "meetbill@163.com"
1.2.2
{"status": "OK", "output": "create user:[ceshi_user4] id:[8] OK"}
```

**删除用户**
```bash
[root@Linux ~]#zabbix_api user_delete ceshi_user4
1.2.2
{"status": "OK", "output": "delete user:[ceshi_user4] id:[8] OK"}
```
