#!/bin/env python

import sys
from itertools import cycle, product
import pandas as pd
import numpy as np
import pylab as pl

pl.rcParams['font.size']=14
#pl.rcParams['legend.fontsize']*=1.1
#pl.rcParams['xtick.labelsize']*=1.25
#pl.rcParams['ytick.labelsize']*=1.25
pl.rcParams['legend.fontsize']='x-small'

colors = cycle( list('bgrcmyw')
                + ['orange', 'pink', 'grey', 'brown', 'lightblue', 'lightgreen', 'turquoise', 'navy', 'purple', 'gold',
                   'aqua', 'silver', 'tan', 'tomato', 'steelblue', 'lightcoral', 'chocolate', 'fuchsia', 'indianred'])

input, ylabel, title = sys.argv[1:4]
only_these = sys.argv[4:]

# get the data
df = pd.read_csv(input, low_memory=False, parse_dates={'Date': ['Year','Month']})

# Make a mostly-coherent processor family entry
df['ProcFix'] = df['Processor Family'].where(pd.notnull(df['Processor Family']), df['Processor Technology'])
remap = dict((x,'Intel EM64T') for x in ('Intel Nehalem', 'Intel Westmere', 'Intel SandyBridge', 'Intel IvyBridge', 'Intel Haswell', 'Intel Core'))
for k in ('PowerPC', 'Power'): remap[k] = 'POWER'
df.ProcFix = df.ProcFix.map(lambda x: remap.get(x,x))

# Make unified date field
#df['Date'] = pd.lib.try_parse_year_month_day(  df['Year'].astype(object), df['Month'].astype(object), np.ones(len(df), dtype=object)  )

# Summarize data to proc/date and country/date levels
dfs = dict()
for k in ('ProcFix','Country'):
    dfs[k] = pd.DataFrame( df.groupby((k,'Date')).size(), columns=['Count'] )
    #ensure that Cartesian product of k/date keys appears
    cprod = pd.MultiIndex.from_tuples( list(product( *dfs[k].index.levels )), names=(k,'Date') )
    dfs[k] = dfs[k].reindex(cprod, fill_value=0, copy=False)

# plot 'em
for (k,d) in dfs.iteritems():
    pl.figure()
    base = None
    patches, labels = [], []

    order = d.max(level=k).sort_index(by='Count', ascending=False).index
    #colors = ( getattr(pl.cm, cm)(i) for i in np.linspace(0, 0.9, len(order)) )

    for pp in order:
        ser = d.Count[pp]

        if only_these and pp not in only_these:
            continue
        if base is None:
            base = np.zeros_like(ser)
        dates, lower, upper = ser.index, base, base+ser
        base = upper

        facecolor = colors.next()
        pl.fill_between(dates, lower, upper, edgecolor='k', facecolor=facecolor, label=pp)
        patches.append( pl.Rectangle((0,0), 1, 1, edgecolor='k', facecolor=facecolor) )
        labels.append( pp )

    # show legend and labels
    pl.legend(patches, labels, loc='upper right')
    pl.xlabel("Year")
    pl.ylabel(ylabel)
    pl.title(title)

    pl.xlim(dates.min(), dates.max()+pd.datetools.relativedelta(years=7))

pl.show()
