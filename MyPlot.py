#!/usr/bin/python3

#http://matplotlib.org/2.0.0/users/pyplot_tutorial.html

from MyRich import MyRich
from Keys import Keys

#import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates  as mdates

import datetime

R = MyRich(Keys, "Trades/")
#R.Info()

R.LoadList()

#R.RecPublicTrades("dsh_eur", 10)

couple1="dsh_btc"
couple2="eth_btc"
 
L1=R.GetPlotListFromCouple(couple1, UseTime=False)
L2=R.GetPlotListFromCouple(couple2)

#for v in L:
#  print(v)

print("Plotting %d samples of %s" % (len(L1), couple1))
print("Plotting %d samples of %s" % (len(L2), couple2))

plot1=(list(map(lambda v:mdates.date2num(datetime.datetime.fromtimestamp(v[0])),L1)), list(map(lambda v:v[1],L1)))
plot2=(list(map(lambda v:v[0],L2)), list(map(lambda v:v[1],L2)))

#plt.plot(*plot1, 'b-', *plot2, 'r-')

plt.subplot(2,1,1)
plt.plot_date(*plot1, 'b-', xdate=True, ydate=False)
plt.grid(True)
plt.ylabel(couple1)
#not working: plt.format_xdata = mdates.DateFormatter('%Y-%m-%d')

plt.subplot(2,1,2)
plt.plot(*plot2, 'r-')

plt.grid(True)
plt.ylabel(couple2)
plt.show()


