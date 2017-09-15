#!/usr/bin/python
#coding=utf8
"""
# Author: Bill
# Created Time : 2016-10-24 12:46:46

# File Name: date.py
# Description:

"""
import datetime
import time

d = datetime.datetime.now()
#print d

def day_get(d):
    """
    获取前一天
    """
    oneday = datetime.timedelta(days=1)
    day = d - oneday
    date_from = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
    date_to = datetime.datetime(d.year, d.month, d.day, 0, 0, 0)
    # print '---'.join([str(date_from), str(date_to)])
    
def week_get(d):
    """
    获取上一周
    """
    week_today = d.weekday()
    dayscount = datetime.timedelta(days=week_today)
    dayto = d - dayscount
    sevendays = datetime.timedelta(days=7)
    dayfrom = dayto - sevendays
    date_from = datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0)
    date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 0, 0, 0)
    # print '---'.join([str(date_from), str(date_to)])
    return date_from,date_to
    
def month_get(d):
    """    
    返回上个月第一个天和本月第一天的时间
    """
    dayscount = datetime.timedelta(days=d.day)
    dayto = d - dayscount
    date_from = datetime.datetime(dayto.year, dayto.month, 1, 0, 0, 0)
    date_to = datetime.datetime(d.year, d.month, 1, 0, 0, 0)
    # print '---'.join([str(date_from), str(date_to)])
    return date_from, date_to
if __name__ == "__main__":
    day_get(d)
    week_get(d)
    month_get(d)
