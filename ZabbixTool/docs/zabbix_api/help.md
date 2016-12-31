## 运行及帮助

## 运行

### 帮助信息

直接执行 zabbix_api 输出帮助信息
```
#zabbix_api
```
输出 zabbix_api 成员函数信息以及选项

### 运行方式

```
#zabbix_api function param [options]
zabbix_api 方法名 参数 选项(非必须)
```
如#zabbix_api host_get 

如果方法名对应的参数个数不对，会默认输出此方法的提示

```
[root@Linux ~]# zabbix_api hostgroup_create 
1.2.1
Python Library Documentation: method hostgroup_create in module __main__

hostgroup_create(self, hostgroupName) method of __main__.zabbix_api instance
    create a hostgroup
    [eg1]./zabbix_api.py hostgroup_create "ceshi_hostgroup"
```

## 官方API

[zabbix 官方api](https://www.zabbix.com/documentation/3.0/manual/appendix/api/api)
