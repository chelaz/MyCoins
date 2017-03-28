#!/usr/bin/python3

#http://matplotlib.org/2.0.0/users/pyplot_tutorial.html

from MyRich import MyRich
from Keys import Keys

#import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates  as mdates
import matplotlib.ticker as mticker

import datetime

def timestampToDayMonth(x, pos):
  if not pos:
    return ""
  if not x:
    return ""
  if pos % 2 == 0:
    return ""
  return datetime.datetime.fromtimestamp(x).strftime('%02d.%02m')

def timestampToHrsMin(x, pos):
  if not pos:
    return ""
  if not x:
    return ""
  if pos % 2 == 1:
    return ""
  return datetime.datetime.fromtimestamp(x).strftime('%H:%M')



R = MyRich(Keys, "Trades/")
#R.Info()

R.LoadList()
#R.RecPublicTrades("dsh_eur", 10)

couple1="dsh_btc"
couple2="eth_btc"
 
#L1=R.GetPlotListFromCouple(couple1)
#L2=R.GetPlotListFromCouple(couple2)

#print("Plotting %d samples of %s" % (len(L1), couple1))
#print("Plotting %d samples of %s" % (len(L2), couple2))

#plot1=(list(map(lambda v:v[0],L1)), list(map(lambda v:v[1],L1)))
#plot2=(list(map(lambda v:v[0],L2)), list(map(lambda v:v[1],L2)))

plt.subplot(2,1,1)
plt.plot(*R.GetPlot(couple1), 'b-')

ax=plt.gca()

ax.xaxis.set_major_formatter(mticker.FuncFormatter(timestampToDayMonth))
ax.xaxis.set_minor_locator(mticker.AutoLocator())
ax.xaxis.set_minor_formatter(mticker.FuncFormatter(timestampToHrsMin))


plt.grid(True)
plt.ylabel(couple1)



plt.subplot(2,1,2)
plt.plot(*R.GetPlot(couple1), 'r-')

ax=plt.gca()

ax.xaxis.set_major_formatter(mticker.FuncFormatter(timestampToDayMonth))
ax.xaxis.set_minor_locator(mticker.AutoLocator())
ax.xaxis.set_minor_formatter(mticker.FuncFormatter(timestampToHrsMin))


plt.grid(True)
plt.ylabel(couple2)
plt.show()


