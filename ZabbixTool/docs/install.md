## 安装

```
#git clone https://github.com/BillWang139967/zabbix_manager.git
#cd zabbix_manager
#sh start.sh
```
### 常见问题

git clone 失败

```
[root@localhost ~]# git clone https://github.com/BillWang139967/zabbix_manager.git
Initialized empty Git repository in /root/zabbix_manager/.git/
error:  while accessing https://github.com/BillWang139967/Vim.git/info/refs

fatal: HTTP request failed
```
解决方法
```
#git config --global http.sslVerify false
```

## 配置

配置文件位置

/etc/zabbix_tool/zabbix_config.ini

```
[zabbixserver]----------------------默认连接(可通过--profile选择连接的zabbix)
server = 127.0.0.1------------------zabbix server IP
port = 80---------------------------zabbix 端口
user = admin------------------------zabbix 管理员账号
password = zabbix-------------------zabbix 管理员密码
[bendi]
server = 192.168.199.128
port = 80
user = admin
password = zabbix
```
