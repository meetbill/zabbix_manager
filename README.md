# zabbix_manager(server)

> * [zabbix管理工具手册(GitHub)(推荐)](https://github.com/BillWang139967/zabbix_manager/wiki)-------------------优先更新
> * [zabbix管理工具手册(w3cschool)](http://www.w3cschool.cn/zabbix_manager/)

## Supported versions

> * zabbix3.0.X

## 功能

**monitor**

When we plan to monitor, we must first create a host group, and then import some template, and finally add some hosts, zabbix_manager is a better choice

**alarm**

When we plan to use zabbix alarm . 
first, we need to add the alarm mode. 
the second, we need to create user groups and users.
the third, the user configuration of alarms. 
fourth, create action

**report**

Daily we need to export the report, use zabbix manager can export xls file using zabbix_manager will greatly save us time

## zabbix_api version

* V1.3
    * v1.3.04，2017-09-22 [更新] 添加 `dev_hosts_device` 输出每台机器的指定挂载目录的使用信息
    * v1.3.03，2017-09-21 [更新] 添加 `dev_hosts_info` 输出常用监控项信息(可以自己定制),优化部分程序
    * v1.3.02，2017-09-16 [更新] 更新程序调用时 `issues` 返回值
    * v1.3.01，2017-09-15 [更新] 增加 `item_list`方法，`issues` 方法输出添加`item key`信息
* V1.2
    * v1.2.16，2017-09-13 [更新] `host_get` 输出项中，模板由之前获取的 `host(Template name)` 修改为 `name(Visible name)`
    * v1.2.15，2017-09-11 [更新] `--hostid/--hostgroupid` 参数可以通过直接输入`主机名/主机组名`进行获取主机列表,检查配置文件不存在时会使用本目录下`etc`下的配置文件
    * v1.2.13，2017-09-09 [更新] agent 自动注册功能修改参数，增加 hostmeta 参数
    * v1.2.12，2017-08-30 [更新] 报表 [report_key](https://github.com/BillWang139967/zabbix_manager/wiki/app_report_key) 修改为使用 key 的正则表达式进行搜索
    * v1.2.11，2017-08-29 [更新] item_get 只输出已启用的监控项 [增加] 增加 [report_key](https://github.com/BillWang139967/zabbix_manager/wiki/app_report_key)
    * v1.2.10，2017-08-26 [修复] 导出报表时设置 --table `SingleTable` 没有定义的错误
    * v1.2.9，2017-08-01  [更新] 增加 application_get 获取 application 列表功能 [增加] 增加[report_app](https://github.com/BillWang139967/zabbix_manager/wiki/app_report_app)
    * v1.2.8，2017-07-28  [更新] 增加3次重试机制
    * v1.2.7，2017-07-25  [更新] 导出报表时，只计算 item_type 为 0(浮点数) 或者 3(整数) 的数据，其他item返回"-1" (2)执行命令时会输出 zabbix server 的版本号
    * v1.2.6，2017-07-21  [更新] 1 [XLSWriter](https://github.com/BillWang139967/XLSWriter) 使之可控制是否显示logo (2)可通过配置以适应 apache 搭建的 zabbix server
    * v1.2.4，2017-06-15  [增加] 输出日常使用报表时会在值后面加上单位(K/M/G也会自动进行换算)
    * v1.2.3，2017-04-04  [增加] -sign 参数(设置搜索分割符)
    * v1.2.1，2016-12-25  [增加] 对主机批量 link 、clear 模板操作
    * v1.2.0，2016-11-27  [修改] `zabbix_api` 调用方式(报表类函数不变)
* V1.1
    * v1.1.7，2016-11-25 优化程序
    * v1.1.6，2016-11-08 add 通过 profile 参数选择配置文件中不同的 `section`
    * v1.1.5，2016-10-24 add `report_available2` 可以对特定 item 进行输出，除报表项外，其他函数统一输出函数
    * v1.1.4，2016-10-24 add `issues`获取最近问题
    * v1.1.3，2016-09-09 add report_available2,可设置排序
    * v1.1.2，2016-09-05 add zabbix_manager gui
    * v1.1.1，2016-08-22 add mysql_quota
    * v1.1.0，2016-07-14 release 1.1.0
* V1.0
    * v1.0.8，2016-07-13 add report
    * v1.0.6，2016-06-23 add rule and discovery manage
    * v1.0.5，2016-06-19 add mediatype manage
    * v1.0.4，2016-06-18 add usergroup manage
    * v1.0.3，2016-06-11 add history_report
    * v1.0.2，2016-06-03 Modify the command line in interactive mode
    * v1.0.1，2016-04-16 First edit

## 参加步骤

* 在 GitHub 上 `fork` 到自己的仓库，然后 `clone` 到本地，并设置用户信息。
```
$ git clone https://github.com/BillWang139967/zabbix_manager.git
$ cd zabbix_manager
$ git config user.name "yourname"
$ git config user.email "your email"
```
* 修改代码后提交，并推送到自己的仓库。
```
$ #do some change on the content
$ git commit -am "Fix issue #1: change helo to hello"
$ git push
```
* 在 GitHub 网站上提交 pull request。
* 定期使用项目仓库内容更新自己仓库内容。
```
$ git remote add upstream https://github.com/BillWang139967/zabbix_manager.git
$ git fetch upstream
$ git checkout master
$ git rebase upstream/master
$ git push -f origin master
```
## 相关链接

> * zabbix安装-------------------------------------------------[zabbix_install](https://github.com/BillWang139967/zabbix_install)
> * zabbix报警工具---------------------------------------------[zabbix_alert](https://github.com/BillWang139967/zabbix_alert)
> * zabbix常用模板---------------------------------------------[zabbix_templates](https://github.com/BillWang139967/zabbix_templates)
> * 导出报表工具-----------------------------------------------[XLSWriter](https://github.com/BillWang139967/XLSWriter)
> * linux终端表格----------------------------------------------[linux_terminal](https://github.com/BillWang139967/linux_terminal)
> * shell菜单工具----------------------------------------------[shell_menu](https://github.com/BillWang139967/shell_menu)

## 小额捐款

如果觉得 `zabbix_manager` 对您有帮助，可以请笔者喝杯咖啡

![Screenshot](images/5.jpg)

## 致谢

1. 感谢南非蜘蛛的指导
