# configure template

* [配置模板](#配置模板)
	* [修改配置文件zabbix_config.ini](#修改配置文件zabbix_configini)

## 配置模板

### 修改配置文件zabbix_config.ini

第一步是修改配置文件zabbix_config.ini 

主要是修改zabbix的ip、端口、admin账户、admin密码

然后修改scripts/template/template_import.sh程序

```bash
#!/bin/bash
python ./lib_zabbix/zabbix_api.py --template_import ./scripts/template/ceshi_templates.xml
``` 
直接执行在本目录执行 

```bash
sh scripts/template/template_import.sh
```
直接执行程序后，会执行操作如下

(1)会将本目录下测试模板进行上传
