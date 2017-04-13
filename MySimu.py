#!/usr/bin/python3


from MyTrade import MyTrade


### Simu Config
class SimuConf:
  T = None # MyTrade
  WinSize = 100 
  PlaceBidFact=0.99
  PlaceAskFact=1.01

  __Algo = None

  # T: MyTrade (Trading interface)
  def __init__(self, T, Algo, couple, WinSize=100):
    self.couple = couple
    self.WinSize = WinSize
    self.T = T
    self.__Algo=Algo

  def Apply(self, vc, LastL):
    return self.__Algo(vc, LastL, self)


