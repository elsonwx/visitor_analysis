#!/usr/bin/python
#-*-coding:utf-8-*-
import os
import sys
import getopt
import gzip
import requests
import codecs
import re
import json
from datetime import datetime,timedelta
import time


ip_address_api = 'http://ip.taobao.com/service/getIpInfo.php'
exclude_keywords = ['google','baidu','.aspx','spider','robots','gt-i9500']
include_keywords = ['www.xiangblog.com']

def decompress_gzip(zipfile,outfile):
    '''decompress a gzip file to outfile'''
    inputfile = gzip.open(zipfile,'rb')
    with open(outfile,'wb') as outputfile:
        for line in inputfile:
            outputfile.write(line)


def exclude_someaccesslog(target_file,keywords_list,include_or_exclude):
    '''exclude some robot access log
    it's like the effect like os.system("sed -i '/keywords/Id' target_file")
       include some domain keywords
    it's like the effect like os.system("sed -i '/keywords/!d' target_file")
    '''
    f = open(target_file,"r+")
    lines = f.readlines()
    f.seek(0)
    for line in lines:
        if include_or_exclude == 'exclude':
            if not any(line.lower().find(keyword.lower())>-1 for keyword in keywords_list):
                f.write(line)
        else: #include
            if any(line.lower().find(keyword.lower())>-1 for keyword in keywords_list):
                f.write(line)
        
    f.truncate()
    f.close()


def print_visitor_address(target_log_file):
    with codecs.open(target_log_file,'r','utf-8') as f:
        content = f.read()
        ipreg = '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        ips = re.findall(ipreg,content)
        allip = set(ips)   
        for ip in allip:
            retjson = None
            try:
                retjson =  requests.get(ip_address_api,params={'ip':ip})
            except Exception as e:
                continue
            try:
                retdict=json.loads(retjson.text)
                if type(retdict['data'])!=dict:
                    continue
                else:
                    country = retdict['data']['country']
                    region = retdict['data']['region']
                    city = retdict['data']['city']
                    isp = retdict['data']['isp']
                    print "ip:%s,country:%s,region:%s,city:%s,isp:%s" % (ip,country,region,city,isp)
                time.sleep(1)
            except Exception as e:
                continue


def daterange(start_date,end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


if __name__ == "__main__":
    opt,args = getopt.getopt(sys.argv[1:],"d:",["day=","begin-date=","end-date=","log-path=","enable-rule"])
    date=begin_date=end_date=log_path=None
    enable_rule = False
    for name,value in opt:
        if name in('-d','--date'):
            date = str(value)
        if name == '--begin-date':
            begin_date = datetime.strptime(str(value),'%Y%m%d')
        if name == '--end-date':
            end_date = datetime.strptime(str(value),'%Y%m%d')
        if name == '--log-path':
            log_path = value
        if name == '--enable-rule':
            enable_rule = True
    if begin_date or end_date:
        if not (begin_date and end_date):
            print "you must set the begin-date and end-date at the same time"
            sys.exit(0)
    # compare end_date>begin_date
    if not log_path:
        log_path = '/var/log/nginx'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_list = []
    log_date_list = []
    if begin_date:
        for date in daterange(begin_date,end_date):
            date_format = datetime.strftime(date,'%Y%m%d')
            log_date_list.append(date_format)
    if date:
        log_date_list.append(str(date))
    else:
        log_date_list.append(time.strftime('%Y%m%d'))
    for log_file in os.listdir(log_path):
        if any(log_file.find(ele)>-1 for ele in log_date_list) and log_file.find('access')>-1:
            log_file_list.append(log_file)
    for log_file in log_file_list:
        if os.path.splitext(log_file)[1] == '.gz':
            target_file = os.path.join(current_dir,log_file[:-3])
            decompress_gzip(os.path.join(log_path,log_file),target_file)
            if enable_rule:
                exclude_someaccesslog(target_file,exclude_keywords,'exclude')
                exclude_someaccesslog(target_file,include_keywords,'include')
            print_visitor_address(target_file)
            os.remove(target_file)
