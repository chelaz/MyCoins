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
  modes = ["plot", "simulate", "info"]
  attrs = ["alt", "noalt", "nomm" ]
  (mode,attrL)=R.ParseCmdLineArgs(sys.argv, modes, attrs)

  if mode == "help":
    exit(0)


#R.Info()

if mode != "info":
  if not R.LoadWeeks(weeks=MyRich.weeks, year=0):
    print("exiting")
    exit(0)

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
  SimPlots=R.SimulateTradingAndPlot(couple)
  R.PrintElapsed("Simulate Trading")
 
  #if len(AskBidPlots[0][0]) == 0:
  #  print("Plot is empty")
  #  exit(0)
      
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

if mode == "info":
  R.InfoMode(R.week, R.year, R.version)
  R.PrintElapsed("Info")

# print min max graphs if not "nomm"
if "nomm" not in attrL:
  if mode != "simulate":
    MMPlot=R.GetMMPlot(couple, 100, Percentage=False)
    lines=plt.plot(*MMPlot[0], 'r-', *MMPlot[1],'g-')
    plt.setp(lines, linewidth=3, linestyle='-', alpha=0.3)

  MMPlot2=R.GetMMPlot2()
  lines2=plt.plot(*MMPlot2[0], 'r:', *MMPlot2[1],'g:')
  plt.setp(lines2, linewidth=1, linestyle=':', alpha=0.8)


DoPlot(R, couple, 'b-', Percentage=False)
#ConfigPlot(couple)

if mode == "simulate":
#  linesSA,=plt.plot(*SimPlots['askAppr'], 'rv', label="Ask", markersize=7)
#  linesSB,=plt.plot(*SimPlots['bidAppr'], 'g^', label="Bid", markersize=7)
  linesSA,=plt.plot(*SimPlots['askIntr'], 'rv', label="Ask", markersize=7)
  linesSB,=plt.plot(*SimPlots['bidIntr'], 'g^', label="Bid", markersize=7)
  #plt.setp(lines, linewidth=3, linestyle='-', alpha=0.3)
  linesS2A,=plt.plot(*SimPlots['askStop'], 'bv', label="Ask", markersize=7)
  linesS2B,=plt.plot(*SimPlots['bidStop'], 'k^', label="Bid", markersize=7)
  plt.legend([linesSA,linesSB, linesS2A, linesS2B], ['Ask v', 'Bid ^', 'Ask v', 'Bid ^'])
 
  PrintLabels = False
  if PrintLabels:
    # print labels for bid
    for i in range(len(SimPlots['bidAppr'][0])):
      ts=SimPlots['bidAppr'][0][i]
      v =SimPlots['bidAppr'][1][i]
      plt.annotate(str(ts), xy=(ts, v), xytext=(ts, v*0.9), arrowprops=dict(arrowstyle='->'), ) #arrowprops=dict(facecolor='black', shrink=1.0),)

  plt.plot(*SimPlots['askApEv'], 'ro', markersize=15, fillstyle='none')
  plt.plot(*SimPlots['bidApEv'], 'go', markersize=15, fillstyle='none')
  plt.plot(*SimPlots['askSLEv'], 'bo', markersize=10, fillstyle='none')
  plt.plot(*SimPlots['bidSLEv'], 'ko', markersize=10, fillstyle='none')


ax=ConfigPlot(couple)

if mode == "simulate":
  ax2 = ax.twinx()
  #plt.subplot(2,1,2)
  linesS=ax2.plot(*SimPlots['balance'], 'b-')
  #linesS=ax2.plot(*SimPlots['timePerWS'], 'r-')
  #linesS=ax2.plot(*MMPlot2[2], 'g-')
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



