# visitor_analysis
analysis the visitor ip address from nginx log
# Usage
give the python script execute privileges
> chmod +x main.py

get the visitor address for certain day
> main.py -d 20160825
 
get the visitor address for a duration
> main.py --begin-date 20160821 --end-date 20160825

# additional
for some reason you need to set some keywords to exclude some robot visit records.you can specify the log which is to be analysised that must include some keywords and  exclude some keywords,to do that,you can change the script  line 16 and line 17.
```python
exclude_keywords = ['google','baidu','.aspx','spider','robots','gt-i9500']
include_keywords = ['www.xiangblog.com']
```
for use these two rules,you need to run
> main.py --enable-rule
