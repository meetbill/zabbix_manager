#!/usr/bin/python
#coding=utf8
"""
# Author: Bill
# Created Time : 2016-06-11 14:43:35

# File Name: my_compare.py
# Description:

"""
__version__ = "1.0.2"
import re
def my_compare(str_all,str_sub,sep_sign=None):
    if not sep_sign:
        sep_sign = ' '
    str_sub_list=re.split(sep_sign, str_sub)
    #str_sub_list=re.split(r' ', str_sub)
    str_all=sep_sign+str_all+sep_sign
    for sub in str_sub_list:
        sub =sep_sign+sub+sep_sign
        if sub in str_all:
            continue
        else:
            return 0
    return 1


if __name__ == "__main__":
    str_sub="to world"
    str1="I want to say hello world"
    str2="I want say hello world"
    str3="I want say hello wor"
    info=my_compare(str1,str_sub)
    print "ceshi:1",info
    info=my_compare(str2,str_sub)
    print "ceshi:0",info
    info=my_compare(str3,str_sub)
    print "ceshi:0",info
    
    str_sub="to_world"
    str1="I_want_to_say_hello_world"
    str2="I_want_say_hello_world"
    str3="I_want_say_hello_wor"
    info=my_compare(str1,str_sub,sep_sign='_')
    print "ceshi:1",info
    info=my_compare(str2,str_sub,sep_sign='_')
    print "ceshi:0",info
    info=my_compare(str3,str_sub,sep_sign='_')
    print "ceshi:0",info
