#!/usr/bin/python
#coding:utf8
import os
import sys
import re
def read_config(hosts_file):
    host=[]
    host_file=open(hosts_file)
    # 判断第一行是否有主机组
    for line in host_file:
        if re.search("^#",line) or re.search("^ *$",line):
            continue
        host_info=line.strip().split("===")
        if len(host_info) < 4:
            print "the config file is err"
            sys.exit()
        host.append((host_info[0],host_info[1],host_info[2],host_info[3]))
    return host

if __name__ == "__main__":
    hosts_file="./switch"
    host_info = read_config(hosts_file)
    print host_info
