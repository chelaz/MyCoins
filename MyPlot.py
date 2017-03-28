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


def DoPlot(R, couple, fmt):
  currency=couple.split('_')[0]

  plt.plot(*R.GetPlot(couple, R.GetBalance(currency)), fmt)

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

couple1="dsh_eur"
couple2="eth_eur"

plt.subplot(2,1,1)
DoPlot(R, couple1, 'b-')

plt.subplot(2,1,2)
DoPlot(R, couple2, 'r-')


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


