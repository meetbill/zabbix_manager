#!/usr/bin/python
#coding=utf8
"""
# Author: meetbill
# Created Time : 2017-08-30 20:54:25

# File Name: zabbix_re.py
# Description:

"""
import re
# vfs.fs.size[/,pfree]
#subject="vfs.[]"
#regex="vfs.\[\]$"
subject_list=["vfs.fs.size[/,pfree]","vfs.fs.size[/home,pfree]"]
regex="vfs.fs.size\[.*,pfree\]$"
regex1="vfs.fs.size\[.,pfree\]$"


print "regex:-------------------------",regex
for subject in subject_list:
    if re.match(regex, subject):
        print subject,"OK"
    else:
        print subject,"ERR"

print "regex:-------------------------",regex1
for subject in subject_list:
    if re.match(regex1, subject):
        print subject,"OK"
    else:
        print subject,"ERR"
