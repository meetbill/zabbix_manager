## 服务器日常使用报表

***服务器日常使用报表***

+ item在一段时间内的最高值、平均值、最小值等
+ item支持模糊搜索
+ 文件系统的使用情况等
+ 支持选择特定主机组或者主机

```
直接输出
#zabbix_api --report item_name date_from date_till

以表格形式展示在终端输出
#zabbix_api --report item_name date_from date_till --table

以表格形式展示在终端输出,同时将第六列升序输出
#zabbix_api --report item_name date_from date_till --table --sort 6

以表格形式展示在终端输出,同时将第六列降序输出
#zabbix_api --report item_name date_from date_till --table --sort 6 --desc
```

输出显示时加--table可以表框显示
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_table.jpg)

输出显示时加--xls /tmp/ceshi.xls可以导出excel文件到/tmp/ceshi.xls目录中(如果是相对路径则输出到 /opt/ZabbixTool/lib_zabbix/)

同时加--title可以输出logo旁边的title name如下

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_xls.jpg)

不加条件项时默认输出所有主机信息，如果有特定选择可以选择以下方式

```
--hostgroupid "主机组ID1，主机组ID2..."
--hostid "主机ID1，主机ID2..."
```
