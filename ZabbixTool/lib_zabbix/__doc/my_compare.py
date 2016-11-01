#!/usr/bin/python
#coding=utf8
"""
# Author: Bill
# Created Time : 2016-06-11 14:43:35

# File Name: my_compare.py
# Description:

"""
import re
def my_compare(str_all,str_sub):
    str_sub_list=re.split(r' ', str_sub)
    for sub in str_sub_list:
        if sub in str_all:
            continue
        else:
            return 0
    return 1


if __name__ == "__main__":
    str_sub="to world"
    str1="I want to say hello world"
    str2="I want say hello world"
    info=my_compare(str1,str_sub)
    print "ceshi:1",info
    info=my_compare(str2,str_sub)
    print "ceshi:0",info
