## template 管理

## template 列表
```
[root@Linux ~]# zabbix_api template_get
```

## template模板导入

template模板路径尽量使用绝对路径，相对路径是以 /opt/ZabbixTool/lib_zabbix/为基本目录
```
[root@Linux ~]# zabbix_api template_import "/tmp/ceshi_templates.xml"
1.2.2
{"status": "OK", "output": "import template [/tmp/ceshi_templates.xml] OK"}
```

