#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
import getopt
import gzip
import requests
from datetime import datetime,timedelta


ip_address_api = 'http://ip.taobao.com/service/getIpInfo.php'
exclude_keywords = ['google','baidu']

def decompress_gzip(zipfile,outfile):
    '''decompress a gzip file to outfile'''
    inputfile = gzip.open(zipfile,'rb')
    with open(outfile,'wb') as outputfile:
        for line in inputfile:
            outputfile.write(line)


def exclude_someaccesslog(target_file,keywords_list):
    '''exclude some robot access log
    it's like the effect like os.system("sed -i '/keywords/Id' target_file")
    '''
    f = open(target_file,"r+")
    lines = f.readlines()
    f.seek(0)
    for line in lines:
        if not any(line.lower().find(keyword.lower())>-1 for keyword in keywords_list):
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
            retjson =  requests.get(ipaddress_api,params={'ip':ip})
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


def daterange(start_date,end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


if __name__ == "__main__":
    opt,args = getopt.getopt(sys.argv[1:],"d:bd:ed:",["day=","begin-date=","end-date=","log-path="])
    date,begin_date,end_date,log_path=None
    for name,value in opt:
        if name in('-d','--date'):
            date = value
        if name in('-bd','--begin-date'):
            begin_date = value
        if name in('-ed','--end-date'):
            end_date = value
        if name == '--log-file':
            log_path = value
    if not (begin_date and end_date):
        print "you must set the begin-date and end-date at the same time"
        sys.exit(0)
    # compare end_date>begin_date
    if not log_path:
        log_path = '/var/log/nginx'
    log_file_list = []
