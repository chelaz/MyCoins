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

def ConfigPlot(couple):
  ax=plt.gca()

  ax.xaxis.set_major_formatter(mticker.FuncFormatter(timestampToDayMonth))
  ax.xaxis.set_minor_locator(mticker.AutoLocator())
  ax.xaxis.set_minor_formatter(mticker.FuncFormatter(timestampToHrsMin))

  plt.grid(True)
  plt.ylabel(couple)

 

R = MyRich(Keys, "Trades/")
#R.Info()

R.LoadList()
#R.RecPublicTrades("dsh_eur", 10)

#couple1="dsh_eur"
#couple2="eth_eur"

couple_db="dsh_btc"
couple_eb="eth_btc"
couple_de="dsh_eur"
couple_ee="eth_eur"


plt.subplot(3,1,1)
DoPlot(R, couple_db, 'b-', ConsiderBalance=False, Percentage=True)
DoPlot(R, couple_de, 'g-', ConsiderBalance=False, Percentage=True)
ConfigPlot(couple_db)

plt.subplot(3,1,2)
DoPlot(R, couple_eb, 'r-', ConsiderBalance=False, Percentage=True)
DoPlot(R, couple_ee, 'g-', ConsiderBalance=False, Percentage=True)
ConfigPlot(couple_eb)

plt.subplot(3,1,3)
MMPlot=R.GetMMPlot(couple_ee, 15*60, Percentage=True)
plt.plot(*MMPlot[0], 'b-', *MMPlot[1],'r-') 
ConfigPlot(couple_ee)



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


