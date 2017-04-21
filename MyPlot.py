#!/usr/bin/python3

#http://matplotlib.org/2.0.0/users/pyplot_tutorial.html

from MyRich import MyRich
from Keys import Keys

#import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates  as mdates
import matplotlib.ticker as mticker

import datetime
import sys

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
  lines = None

  if ConsiderBalance:
    lines = plt.plot(*R.GetPlot(couple, R.GetServerBalance(currency)), fmt)
  else:
    lines = plt.plot(*R.GetPlot(couple, 1.0, Percentage), fmt) 

  plt.setp(lines, linewidth=0.5)

#def onclick(event):
#  print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
#        (event.button, event.x, event.y, event.xdata, event.ydata))

def ConfigPlot(couple, ax=None):
  if ax == None:
    ax=plt.gca()

  ax.xaxis.set_major_formatter(mticker.FuncFormatter(timestampToDayMonth))
  ax.xaxis.set_minor_locator(mticker.AutoLocator())
  ax.xaxis.set_minor_formatter(mticker.FuncFormatter(timestampToHrsMin))

  ax.grid(True)
  #plt.ylabel(couple)
  ax.set_ylabel(couple)

#  fig=plt.figure()
#  fig.canvas.mpl_connect('button_press_event', onclick)

  return ax
 

R = MyRich(Keys)

if len(sys.argv) > 1:
  modes = ["plot", "simulate"]
  mode=R.ParseCmdLineArgs(sys.argv, modes)

  if mode == "help":
    exit(0)



#R.Info()

if not R.LoadWeeks(weeks=MyRich.weeks, year=0):
  exit(0)
#R.LoadList(week=13)
#R.LoadList(week=14)


#R.RecPublicTrades("dsh_eur", 10)

R.PrintElapsed("Load")

#couple1="dsh_eur"
#couple2="eth_eur"

couple_db="dsh_btc"
couple_eb="eth_btc"
couple_de="dsh_eur"
couple_ee="eth_eur"

couple=couple_db
#couple=couple_ee
#
if mode == "simulate":
  AskBidPlots=R.SimulateTradingAndPlot(couple)
  R.PrintElapsed("Simulate Trading")
  
#plt.subplot(3,1,1)
#DoPlot(R, couple_db, 'b-', ConsiderBalance=False, Percentage=True)
#DoPlot(R, couple_de, 'g-', ConsiderBalance=False, Percentage=True)
#ConfigPlot(couple_db)
#
#plt.subplot(3,1,2)
#DoPlot(R, couple_eb, 'r-', ConsiderBalance=False, Percentage=True)
#DoPlot(R, couple_ee, 'g-', ConsiderBalance=False, Percentage=True)
#ConfigPlot(couple_eb)

#plt.subplot(2,1,1)

if mode != "simulate":
  MMPlot=R.GetMMPlot(couple, R.C.WinSize, Percentage=False)
  lines=plt.plot(*MMPlot[0], 'r-', *MMPlot[1],'g-')
  plt.setp(lines, linewidth=3, linestyle='-', alpha=0.3)

MMPlot2=R.GetMMPlot2()
lines2=plt.plot(*MMPlot2[0], 'r:', *MMPlot2[1],'g:')
plt.setp(lines2, linewidth=1, linestyle=':', alpha=0.8)


DoPlot(R, couple, 'b-', Percentage=False)
#ConfigPlot(couple)

if mode == "simulate":
  #linesS=plt.plot(*AskBidPlots[0], 'ro', *AskBidPlots[1],'go', *AskBidPlots[2], 'b-')
  linesSA,=plt.plot(*AskBidPlots[0], 'rv', label="Ask", markersize=7)
  linesSB,=plt.plot(*AskBidPlots[1], 'g^', label="Bid", markersize=7)
  plt.legend([linesSA,linesSB], ['Ask v', 'Bid ^'])
  #plt.setp(lines, linewidth=3, linestyle='-', alpha=0.3)

  # print labels for bid
  for i in range(len(AskBidPlots[1][0])):
    ts=AskBidPlots[1][0][i]
    v=AskBidPlots[1][1][i]
    plt.annotate(str(ts), xy=(ts, v), xytext=(ts, v*0.9), arrowprops=dict(arrowstyle='->'), ) #arrowprops=dict(facecolor='black', shrink=1.0),)

  plt.plot(*AskBidPlots[3], 'ro', markersize=15, fillstyle='none')
  plt.plot(*AskBidPlots[4], 'go', markersize=15, fillstyle='none')

ax=ConfigPlot(couple)

if mode == "simulate":
  ax2 = ax.twinx()
  #plt.subplot(2,1,2)
  linesS=ax2.plot(*AskBidPlots[2], 'b-')
  ConfigPlot(couple, ax2)



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

R.PrintElapsed("Prepare Plots")

plt.show()



