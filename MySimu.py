#!/usr/bin/python3


#from MyTrade import MyTrade


### Simu Config
class SimuConf:
  #T = None # MyTrade
  WinSize = 100 
  PlaceBidFact=0.0
  PlaceAskFact=0.0
#  PlaceBidFact=0.99
#  PlaceAskFact=1.01
  OnlyAlternating = False
  OverwriteOrder = False #currently only if OnlyAlternating
  SkipIfSameTS = False 
  MinMaxEpsPerc= 0.0
  AltTradingVal=0.01

  #__Algo = None

  # T: MyTrade (Trading interface)
  def __init__(self, couple, Algos, PrepareFct=None, WinSize=100, MinMaxEpsPerc=None):
    self.couple = couple
    self.WinSize = WinSize
    if MinMaxEpsPerc != None:
      self.MinMaxEpsPerc = MinMaxEpsPerc
    #self.T = T
    self.__Algos=Algos
    self.__PrepareFct=PrepareFct

  def Print(self):
    print("Configuration: \n\t"\
          "WinSize %d, "\
          "MMEps %f, "\
          "PlaceBidFact %f, "\
          "PlaceAskFact %f, "\
          "OnlyAlternating %s, "\
          "OverwriteOrder %s, "\
          "SkipIfSameTS %s" % (\
          self.WinSize, \
          self.MinMaxEpsPerc,
          self.PlaceBidFact,
          self.PlaceAskFact,
          str(self.OnlyAlternating),
          str(self.OverwriteOrder),
          str(self.SkipIfSameTS)))

  def Apply(self, vc, LastL):
    if self.__PrepareFct != None:
      self.__PrepareFct(vc, LastL, self)
    for a in self.__Algos:
      if a(vc, LastL, self):
        return True
    return False


