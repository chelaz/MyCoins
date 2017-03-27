#!/usr/bin/python3

#http://matplotlib.org/2.0.0/users/pyplot_tutorial.html

from MyRich import MyRich
from Keys import Keys

#import numpy as np
import matplotlib.pyplot as plt

R = MyRich(Keys, "Trades/")
R.Info()

R.LoadList()

#R.RecPublicTrades("dsh_eur", 10)

couple="dsh_btc"
 
L=R.GetPlotListFromCouple(couple)
L2=R.GetPlotListFromCouple("eth_btc")

#for v in L:
#  print(v)

print("Plotting %d samples of %s" % (len(L), couple))

plot1=(list(map(lambda v:v[0],L)), list(map(lambda v:v[1],L)))
plot2=(list(map(lambda v:v[0],L2)), list(map(lambda v:v[1],L2)))


#plt.plot(list(map(lambda v:v[0],L)), list(map(lambda v:v[1],L)))
plt.plot(*plot1, 'b-', *plot2, 'r-')

plt.ylabel(couple)
plt.show()


#print(R.GetTuple(1490115189, "dsh_eur"))

#tx = np.arange(1490115180, 1490115189, 1)

#def f(t):
#  return R.GetTuple(t, "dsh_eur")['price']

#print(f(1490115180000))

#plt.plot(tx, f(tx), 'bo')
#plt.ylabel('Dash')
#plt.show()

