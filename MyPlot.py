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


def DoPlot(R, couple, fmt, ConsiderBalance=False, Percentage=False):
  currency=couple.split('_')[0]

  if ConsiderBalance:
    plt.plot(*R.GetPlot(couple, R.GetBalance(currency)), fmt)
  else:
    plt.plot(*R.GetPlot(couple, 1.0, Percentage), fmt) 

  ax=plt.gca()

  ax.xaxis.set_major_formatter(mticker.FuncFormatter(timestampToDayMonth))
  ax.xaxis.set_minor_locator(mticker.AutoLocator())
  ax.xaxis.set_minor_formatter(mticker.FuncFormatter(timestampToHrsMin))

  plt.grid(True)
  plt.ylabel(couple)

 

R = MyRich(Keys, "Trades/")
R.Info()

R.LoadList()
#R.RecPublicTrades("dsh_eur", 10)

#couple1="dsh_eur"
#couple2="eth_eur"

couple1b="dsh_btc"
couple2b="eth_btc"
couple1e="dsh_eur"
couple2e="eth_eur"



plt.subplot(2,1,1)
DoPlot(R, couple1b, 'b-', ConsiderBalance=False, Percentage=True)
DoPlot(R, couple1e, 'g-', ConsiderBalance=False, Percentage=True)


plt.subplot(2,1,2)
DoPlot(R, couple2b, 'r-', ConsiderBalance=False, Percentage=True)
DoPlot(R, couple2e, 'g-', ConsiderBalance=False, Percentage=True)



#plt.subplot(2,1,1)
#plt.plot(*R.GetPlot(couple1, R.GetBalance("dsh")), 'b-')
#
#ax=plt.gca()
#
#ax.xaxis.set_major_formatter(mticker.FuncFormatter(timestampToDayMonth))
#ax.xaxis.set_minor_locator(mticker.AutoLocator())
#ax.xaxis.set_minor_formatter(mticker.FuncFormatter(timestampToHrsMin))
#
#
#plt.grid(True)
#plt.ylabel(couple1)
#
#
#
#plt.subplot(2,1,2)
#plt.plot(*R.GetPlot(couple2, R.GetBalance("eth")), 'r-')
#
#ax=plt.gca()
#
#ax.xaxis.set_major_formatter(mticker.FuncFormatter(timestampToDayMonth))
#ax.xaxis.set_minor_locator(mticker.AutoLocator())
#ax.xaxis.set_minor_formatter(mticker.FuncFormatter(timestampToHrsMin))
#
#
#plt.grid(True)
#plt.ylabel(couple2)
plt.show()


