#!/usr/bin/env python2
from __future__ import print_function
import os
import textwrap
#os.environ["HTTP_PROXY"] = 'http://proxy-jf.intel.com:911'

import csv
import xlrd
from datetime import datetime
import urllib

# Download all the XLS files that we don't already have
now = datetime.now()
xls_files = []
url_template = 'http://www.top500.org/lists/{0:04d}/{1:02d}/download/TOP500_{0:04d}{1:02d}.xls'

for year in range(1993, now.year+1):
    for month in (6, 11):
        if (year, month) > (now.year, now.month):
            break
        url = url_template.format(year,month)
        fn = os.path.basename(url)

        if os.path.exists(fn):
            print("{} exists, skipping.".format(fn))
        else:
            print("Fetching {}...".format(fn))
            try:
                urllib.urlretrieve(url, fn)
                xls_files.append((year,month,fn))
            except urllib.error.URLError as e:
                print(e)

        xls_files.append((year,month,fn))

# First pass, figure out all the headers
all_headers = ['Year', 'Month', 'Day']
last_headers = []
headers_to_rename = {'Rmax':'RMax', 'Rpeak':'RPeak', 'Effeciency (%)':'Efficiency (%)','Proc. Frequency':'Processor Speed (MHz)','Cores':'Total Cores'}

for (year, month, fn) in xls_files:
    w = xlrd.open_workbook(fn, logfile=open(os.devnull, 'w'))
    for s in w.sheets():
        for rr in range(s.nrows):
            r = [unicode(x).encode('ascii','xmlcharrefreplace') for x in s.row_values(rr)]
            if any(r): #skip blank rows
                renamed_headers = {}
                headers = [(renamed_headers.setdefault(h, headers_to_rename[h]) if h in headers_to_rename else h)
                           for h in r]
                new_headers = [h for h in headers if h not in all_headers]
                drop_headers = [h for h in last_headers if h not in headers]

                if new_headers or drop_headers or renamed_headers:
                    print("{}/{}:".format(year,month))
                    if renamed_headers:
                        print(textwrap.fill("renamed headers: " + ', '.join('%s to %s'%kv for kv in renamed_headers.items()), initial_indent='  ', subsequent_indent='    '))
                    if new_headers:
                        print(textwrap.fill("new headers: " + ', '.join(new_headers), initial_indent='  ', subsequent_indent='    '))
                    if drop_headers:
                        print(textwrap.fill("drop headers: " + ', '.join(drop_headers), initial_indent='  ', subsequent_indent='    '))

                all_headers.extend(new_headers)
                last_headers = headers
                break

# Second pass, build a complete CSV table
out = csv.DictWriter(open("TOP500_history.csv", "wb"), all_headers)
out.writeheader()

for (year,month,fn) in xls_files:
    w = xlrd.open_workbook(fn, logfile=open(os.devnull, 'w'))
    for s in w.sheets():
        headers = None
        for rr in range(s.nrows):
            r = [unicode(x).encode('ascii','xmlcharrefreplace') for x in s.row_values(rr)]
            if any(r): #skip blank lines
                if headers is None:
                    headers = [headers_to_rename.get(h,h) for h in r]
                else:
                    rd = dict(zip(headers, r))
                    rd.update({'Year':year, 'Month':month, 'Day':1})
                    out.writerow(rd)
