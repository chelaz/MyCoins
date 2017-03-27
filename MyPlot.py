#!/usr/bin/python3

#http://matplotlib.org/2.0.0/users/pyplot_tutorial.html

from MyRich import MyRich
from Keys import Keys

import numpy as np
import matplotlib.pyplot as plt

R = MyRich(Keys, "Trades/")
R.Info()

R.LoadList()

print(R.GetTuple(1490115189, "dsh_eur"))

tx = np.arange(1490115180, 1490115189, 1)

def f(t):
  return R.GetTuple(t, "dsh_eur")['price']

print(f(1490115180000))

#plt.plot(tx, f(tx), 'bo')
#plt.ylabel('Dash')
#plt.show()

