#!/bin/env python
# -*- coding: utf-8 -*-

import sys
from itertools import cycle, product
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt, dates as mpld, use

plt.rcParams['font.size']=20
#pl.rcParams['legend.fontsize']*=1.1
#pl.rcParams['xtick.labelsize']*=1.25
#pl.rcParams['ytick.labelsize']*=1.25
plt.rcParams['legend.fontsize']='x-small'

colors = cycle( list('bcgmry') )
                #+ ['orange', 'pink', 'grey', 'brown', 'lightblue', 'lightgreen', 'turquoise', 'navy', 'purple', 'gold',
                #   'aqua', 'silver', 'tan', 'tomato', 'steelblue', 'lightcoral', 'chocolate', 'fuchsia', 'indianred'])
hatches = cycle(('/', '*', '\\', 'o', 'x', 'O', '.'))

input, only_these = sys.argv[1], sys.argv[2:]

##########################

# get the data
df = pd.read_csv(input, low_memory=False, parse_dates={'Date': ['Year','Month','Day']})

# Make mostly-coherent processor family and vendor columns
df['Country'].replace('Saudia Arabia', 'Saudi Arabia', inplace=True)
def remap(procfam):
    if procfam in ('Intel EM64T','Intel Nehalem','Intel Westmere','Intel SandyBridge','Intel IvyBridge','Intel Haswell','Intel Core','Intel MIC','AMD x86_64'):
        i,v='x86-64', procfam.split()[0]
    elif procfam in ('POWER','Power','PowerPC'):
        i=v='POWER'
    elif procfam == 'Intel IA-64':
        i,v='Itanium', 'Intel'
    elif procfam in ('Intel IA-32','AMD'):
        i,v='x86-32', procfam.split()[0]
    else:
        i,v=procfam, procfam
    return pd.Series((i,v))

procfam = df['Processor Family'].where(df['Processor Family'], df['Processor Technology'])
df[['ISA','Vendor']] = procfam.apply(remap)

##########################

# Find what set of countries (sorted by weight) account for most of the total counts
country_by_date = df.groupby(('Date','Country')).size()
country_wt = country_by_date.sum(level='Country').order(ascending=False).to_frame('sum')
#country_wt['sum'] = country_by_date.sum(level='Country')
cutoff = country_wt['sum'].cumsum() > 0.90*country_wt['sum'].sum()

#country_by_date = country_by_date.reset_index()
#country_by_date = country_by_date.groupby(('Date','Country')).sum()
country_by_date = country_by_date.unstack()             # pivot Country from row to column index
country_by_date = country_by_date.fillna(0)                # fill in missing values (e.g. x86_64 in 1993 ;-))
major_minor_countries = [ country_by_date.reindex(columns=country_wt.index[cutoff==polarity])
                          for polarity in (False,True) ]

# plot it
fig = plt.figure(figsize=(14,10))
sharex = None
patches, labels = [], []
dates = country_by_date.index
for pos, cbd in enumerate(major_minor_countries):
    plt.subplot(2, 1, pos, sharex=sharex)
    sharex = ax = fig.gca()

    edge = np.zeros(dates.size)
    bottom = None
    for pp, ser in cbd.iteritems():
        hatch = hatches.next()
        facecolor = colors.next()

        if bottom is None:
            bottom = max(0, ser.min() - 0.1*ser.ptp())
            edge = bottom
            ser -= bottom

        ax.fill_between(dates, edge, edge+ser, edgecolor='k', facecolor=facecolor, hatch=hatch, label=pp)
        ax.xaxis.set_major_formatter(mpld.DateFormatter("’%y"))
        ax.xaxis.set_major_locator(mpld.YearLocator())
        ax.xaxis.set_minor_locator(mpld.YearLocator(month=7))
        plt.xticks(rotation='60')
        patches.append( plt.Rectangle((0,0), 2, 2, edgecolor='k', facecolor=facecolor, hatch=hatch) )
        labels.append(pp)

        edge += ser
        pplast = pp

    # show legend and labels
    plt.ylabel("Number of systems")
    plt.ylim(bottom, min(500, edge.max() + 0.1*edge.ptp()))
    if pos==0:
        plt.xlabel("TOP500 Date")
    elif pos==1:
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.setp(ax.get_xlabel(), visible=False)
        plt.title("TOP500 Supercomputers by Country")

plt.legend(patches, labels, loc='upper left', bbox_to_anchor=(1.02, 1), handleheight=1.2, handlelength=3, ncol=2)
plt.subplots_adjust(left=.08, top=.92, bottom=0.12, right=0.6, hspace=0.02)
plt.xlim(dates.min(), dates.max())
plt.savefig("Countries_with_TOP500_supercomputers.png", bbox_inches='tight')
plt.savefig("Countries_with_TOP500_supercomputers.svg", bbox_inches='tight')

##########################

# Processor families by date, sorted by weight of ISA then by Vendor
proc_counts = df.groupby(('ISA','Vendor','Date')).size()
proc_by_date = proc_counts.unstack(level=(0,1)).fillna(0) # pivot ISA,Vendor from row to column index
proc_wt = proc_by_date.sum().to_frame()                   # weight (ISA,Vendor) across all dates
ISA_wt = proc_wt.sum(level='ISA')                         # weight by (ISA) across all dates
ISA_wt.columns = [1]
proc_wt = proc_wt.join( ISA_wt.reindex(proc_wt.index, level='ISA') )
proc_wt.sort([1,0], ascending=(False,False), inplace=True)
proc_by_date = proc_by_date.reindex(columns=proc_wt.index)

# plot it
fig = plt.figure(figsize=(14,10))
patches, labels = [], []
dates = proc_by_date.index
edge = np.zeros(dates.size)

pplast = facecolor = bottom = None
for pp, ser in proc_by_date.iteritems():

    #print ser.shape, edge.shape, dates.shape
    if isinstance(pp, basestring): pp=pp,
    if pplast is None or pp[0]!=pplast[0]:
        hatch = hatches.next()
    if pplast is None or len(pp)<2 or pp[1]!=pplast[1]:
        facecolor = colors.next()
    label = ("%s (%s)"%pp if pp[0]!=pp[1] else pp[0])

    ax = fig.gca()
    ax.fill_between(dates, edge, edge+ser, edgecolor='k', facecolor=facecolor, hatch=hatch, label=label)
    ax.xaxis.set_major_formatter(mpld.DateFormatter("’%y"))
    ax.xaxis.set_major_locator(mpld.YearLocator(month=6))
    ax.xaxis.set_minor_locator(mpld.YearLocator(month=11))
    plt.xticks(rotation=60)
    patches.append( plt.Rectangle((0,0), 2, 2, edgecolor='k', facecolor=facecolor, hatch=hatch) )
    labels.append(label)

    edge += ser
    pplast = pp
    if bottom is None:
        bottom = max(0, edge.min() - 0.1*edge.ptp())

# show legend and labels
plt.legend(patches, labels, loc='upper left', bbox_to_anchor=(1.02, 1), handleheight=1, handlelength=4)
plt.subplots_adjust(left=.08, top=.92, bottom=0.12, right=0.75)
plt.xlabel("TOP500 Date")
plt.ylabel("Number of systems")
plt.title("TOP500 Supercomputers by Processor Family")

plt.xlim(dates.min(), dates.max())#+pd.datetools.relativedelta(months=6))
plt.ylim(bottom, min(500, edge.max() + 0.1*edge.ptp()))

plt.savefig("Processor_families_in_TOP500_supercomputers.png", bbox_inches='tight')
plt.savefig("Processor_families_in_TOP500_supercomputers.svg", bbox_inches='tight')
plt.show()
