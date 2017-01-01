## report报表

* [1 简单了解内容](#1-简单了解内容)
* [2 报表](#2-报表)
	* [2.1 服务器可用性报表1](#21-服务器可用性报表1)
	* [2.2 服务器可用性报表2](#22-服务器可用性报表2)
* [3 内部算法](#3-内部算法)
	* [3.1 服务器可用性报表1](#31-服务器可用性报表1)
	* [3.2 服务器可用性报表2](#32-服务器可用性报表2)
* [4 提示](#4-提示)

## 1 简单了解内容

report 包括以下内容

***服务器可用性报表***
    
+ 服务器可用性报表使用Agent ping计算，Agent ping 成功时会入库1，如果失败时，则不入库。
+ trend会每个小时将history中的值计算出最大值，最小值，和平均值，这里我们需要的是trend小时的记录个数即可

## 2 报表

### 2.1 服务器可用性报表1

输出显示时加--table可以表框显示
![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_available_table.jpg)

输出显示时加--xls ceshi.xls可以导出excel文件，如下

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_available_xls.jpg)

### 2.2 服务器可用性报表2

```
#zabbix_api --report_available2 "2016-07-01 00:00:00" "2016-09-01 00:00:00" --hostid 10105 --table

其他参数说明
--item_key itemkey.example   # 选择特定 item 进行输出
--hostid  hostid             # 选择特定主机
--hostgroupid hostgroupid    # 选择特定主机组
```
程序输出

```
+Availability report---------------+--------------------------------------------------------------+----------+----------+-----------+
| hostname        | ip             | Name                                                         | Problems | OK       | prevvalue |
+-----------------+----------------+--------------------------------------------------------------+----------+----------+-----------+
| Zabbix server   | 127.0.0.1      | Zabbix agent on Zabbix server is unreachable for 5 minutes   | 0        | 100%     | 1         |
| Zabbix server   | 127.0.0.1      | Processor load is too high on Zabbix server                  | 0        | 100%     | 0.0000    |
| Zabbix server   | 127.0.0.1      | Free disk space is less than 20% on volume /                 | 0        | 100%     | 68.9522   |
| net137          | 192.168.19.137 | Zabbix agent on net137 is unreachable for 5 minutes          | 0        | 100%     | 1         |
| net137          | 192.168.19.137 | Processor load is too high on net137                         | 0        | 100%     | 0.0000    |
| net137          | 192.168.19.137 | Free disk space is less than 20% on volume /                 | 0        | 100%     | 18.0277   |
| net139          | 192.168.19.139 | Zabbix agent on net139 is unreachable for 5 minutes          | 0        | 100%     | 1         |
| net139          | 192.168.19.139 | Processor load is too high on net139                         | 0        | 100%     | 0.0000    |
| net139          | 192.168.19.139 | Free disk space is less than 20% on volume /                 | 0        | 100%     | 18.0279   |
| net225          | 192.168.19.225 | Zabbix agent on net225 is unreachable for 5 minutes          | 0        | 100%     | 1         |
| net225          | 192.168.19.225 | Processor load is too high on net225                         | 0        | 100%     | 0.0400    |
| net225          | 192.168.19.225 | Free disk space is less than 20% on volume /                 | 0        | 100%     | 59.8441   |
| 192.168.19.153  | 192.168.19.153 | Zabbix agent on 192.168.19.153 is unreachable for 5 minutes  | 0        | 100%     | 1         |
| 192.168.19.153  | 192.168.19.153 | Processor load is too high on 192.168.199.153                | 0.2694%  | 99.7306% | 0.0000    |
| 192.168.19.153  | 192.168.19.153 | Free disk space is less than 20% on volume /                 | 0        | 100%     | 25.7349   |
+-----------------+----------------+--------------------------------------------------------------+----------+----------+-----------+
```


zabbix界面上显示

![Screenshot](https://github.com/BillWang139967/zabbix_manager/raw/master/images/report_available_table3.jpg)

输出显示时加--xls ceshi.xls可以导出excel文件，如下


## 3 内部算法

### 3.1 服务器可用性报表1

可用性

> * 分子是：每小时统计个数的总和
> * 分母是：每小时应该统计的个数 * 小时数

每小时的个数 = 3600(小时总秒数)/X(每X秒采集一次数据)

X为item的delay值

### 3.2 服务器可用性报表2

可用性

> * 分子是：触发器判断后正常的时间段
> * 分母是：统计的时间段值

当触发器判断正常时，在event中记录的value值为0，反之，记录的值为1

根据统计1———>0状态的总时间  与  统计的时间段相比，就可以得出服务器的可用性

在程序设计时有以下几种情况，event表中存放的是0101010101值，每个值都记录着发生的时间
 
> * 取值time_from时，此item在此阶段还没有值，即还未开始监控此节点的服务，即获取到的值为0101010....，***此情况需要将分母中统计的时间段的开始值time_from设置为检查为0的时间点值***
> * 取值time_from时，此item在此阶段后，检测到有异常，即获取到的值为10101010.......
> * 取值time_till时，此item在time_till时是正常状态,即获取到的值为....101010
> * 取值time_till时，此item在time_till时是异常状态,即获取到的值为....1010101***此情况需要将最后检测为1的时间点到time_till之间的值加入到分子中***

在程序中重点需要处理，第一个值为0或者1，和最后一个值是0或者1的部分，中间部分都是使用0的时间点减去1的时间点的值

## 4 提示

(1)不加条件项时默认输出所有主机信息，如果有特定选择可以选择以下方式

```
--hostgroupid "主机组ID1，主机组ID2..."
--hostid "主机ID1，主机ID2..."
```
