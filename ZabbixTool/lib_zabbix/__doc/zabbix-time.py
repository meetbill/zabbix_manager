#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
import datetime
import calendar
import os
import os.path

#当天日期
today = datetime.date.today()

def custom_report(startTime,endTime):
    sheetName =  time.strftime('%m%d_%H%M',startTime) + "_TO_" +time.strftime('%m%d_%H%M',endTime)
    print sheetName
    customStart = int(time.mktime(startTime))
    print customStart
    customEnd = int(time.mktime(endTime))
    print customEnd

def main():
    #最好加上时间类型检查
    argvCount = len(sys.argv) #参数个数，用于判断是生成自定义报表还是周期性报表 
    dateFormat = "%Y-%m-%d %H:%M:%S"
    dateFormat = "%Y-%m-%d"
    today = datetime.date.today()
    if(argvCount == 3):
        #传入两个参数，生成自定义报表为：以第一参数为起始时间，第二参数为结束时间的区别报表
        startTime =  time.strptime(sys.argv[1],dateFormat)
        endTime =  time.strptime(sys.argv[2],dateFormat)
        print "startTime:",startTime
        print "startTime:",endTime
        custom_report(startTime,endTime)        
    else:
        #参数个数大于2为非法情况，打印异常信息，退出报表生成
        usage()
def usage():
    print """注意时间格式强制要求： zabbix-report.py ['2012-09-01 01:12:00'] ['2012-09-01 01:12:00']"""

#运行程序
main()
