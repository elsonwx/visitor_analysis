# visitor_analysis
analysis the visitor ip address from nginx log
# Usage
give the python script execute privileges
> chmod +x main.py

- get the visitor address for certain day
> main.py -d 20160825
- get the visitor address for a during day
> main.py --begin-date 20160821 --end-date 20160825

# additional
for some reson you need to set some keywords to exclude some robot visit record.you can specify the log which is to be analysised that must include some keywords or exclude some keywords,to do that,you can change the script  line 16 and line 17.
```python
exclude_keywords = ['google','baidu','.aspx','spider','robots','gt-i9500']
include_keywords = ['www.xiangblog.com']
