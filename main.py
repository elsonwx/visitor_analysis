#!/usr/bin/python
# -*-coding:utf-8-*-

import os
import sys
import getopt
import gzip
import requests
import codecs
import re
import json
import shutil
from datetime import datetime, timedelta
from os.path import isfile, join, basename
import time


ip_address_api = 'http://api.elsonwx.com:3001/ip/'
exclude_keywords = []
include_keywords = []


def decompress_gzip(zipfile, outfile):
    '''decompress a gzip file to outfile'''
    inputfile = gzip.open(zipfile,'rb')
    with open(outfile,'wb') as outputfile:
        for line in inputfile:
            outputfile.write(line)


def remove_someline(target_file, keywords_list, include_or_exclude):
    '''exclude some robot access log
    it's like the effect like os.system("sed -i '/keywords/Id' target_file")
       include some domain keywords
    it's like the effect like os.system("sed -i '/keywords/I!d' target_file")
    '''
    if len(keywords_list) == 0:
        return
    f = open(target_file, "r+")
    lines = f.readlines()
    f.seek(0)
    for line in lines:
        if include_or_exclude == 'exclude':
            if not any(line.lower().find(keyword.lower()) >-1 for keyword in keywords_list):
                f.write(line)
        else:
            if any(line.lower().find(keyword.lower()) > -1 for keyword in keywords_list):
                f.write(line)
        
    f.truncate()
    f.close()


def print_visitor_address(target_log_file):
    with codecs.open(target_log_file, 'r', 'utf-8') as f:
        content = f.read()
        ipreg = '((\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5]))'
        ips = re.findall(ipreg, content)
        allip = set(ips)   
        for ip_format in allip:
            ip = ip_format[0]
            res = None
            try:
                res = requests.get(ip_address_api + ip)
            except Exception as e:
                continue
            try:
                ret_obj = json.loads(res.text)
                ip_location = ret_obj['ipipnet_location']
                print "ip:%s,location:%s,file:%s" % (ip, ip_location, basename(target_log_file))
                time.sleep(1)
            except Exception as e:
                continue


if __name__ == "__main__":
    opt, args = getopt.getopt(sys.argv[1:], "d:", ["days=", "start-date=", "end-date=", "log-path=", "enable-rule"])
    days = start_date_time = end_date_time = log_path = None
    enable_rule = False
    for name, value in opt:
        if name in('-d', '--days'):
            days = int(value)
        if name == '--start-date':
            start_date_time = datetime.strptime(str(value),'%Y%m%d')
        if name == '--end-date':
            end_date_time = datetime.strptime(str(value),'%Y%m%d')
        if name == '--log-path':
            log_path = str(value)
        if name == '--enable-rule':
            enable_rule = True
    if start_date_time or end_date_time:
        if not (start_date_time and end_date_time):
            print "you must set the start-date and the end-date at the same time"
            sys.exit(1)
    # compare end_date>begin_date
    if not log_path:
        log_path = '/var/log/nginx'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    start_time=end_time=None
    if start_date_time:
        start_time = int(time.mktime(start_date_time.timetuple()))
        end_time = int(time.mktime(end_date_time.timetuple()))
    if days:
        start_time = int(time.mktime((datetime.now()-timedelta(days)).timetuple()))
        end_time = int(time.mktime(datetime.now().timetuple()))
    log_file_list = []

    #include subdirectory
    #for dirpath, dirnames, filenames in os.walk(mypath):
    #    for filename in filenames:
    #        log_file_list.append(join(dirpath,filename))
    
    #not include subdirectory file
    for log_file in [f for f in os.listdir(log_path) if isfile(join(log_path, f))]:
        log_file = join(log_path, log_file)
        file_mtime = int(os.path.getmtime(log_file))
        if start_time <= file_mtime and end_time > file_mtime:
            log_file_list.append(log_file)
    for log_file in log_file_list:
        target_file = None
        if os.path.splitext(log_file)[1] == '.gz':
            target_file = join(current_dir, basename(log_file)[:-3])
            decompress_gzip(log_file, target_file)
        else:
            shutil.copy2(log_file, current_dir)
            target_file = join(current_dir, basename(log_file))
        if enable_rule:
            remove_someline(target_file, exclude_keywords, 'exclude')
            remove_someline(target_file, include_keywords, 'include')
        print_visitor_address(target_file)
        os.remove(target_file)
