#!/usr/bin/python3

import datetime
import sys

class MyTrade:

  __F = None # (Funds) Balance { 'btc' : 0.0, 'dsh' : 0.0, 'eth' : 0.0 }

  def __init__(self, StartBalance = { 'btc' : 0.0, 'dsh' : 0.0, 'eth' : 0.0 } ):
    self.__F = StartBalance

  def PrintBalance(self):
    print("Balance")
    for f in self.__F:
      print("  %s: %f" % (f, self.__F[f]))

  # PlaceOrder(0.08, 1, "dsh_btc") # buy 1 dsh for 0.08 btc
  def PlaceOrder(self, price, amount, couple):
    cur=couple.split('_')
    cur_buy  = cur[0]
    cur_sell = cur[1]
    
    print(self.__F[cur_sell])
    if self.__F[cur_sell] < price:
      return 0.0
    self.__F[cur_sell] = self.__F[cur_sell]-price
    self.__F[cur_buy]  = self.__F[cur_buy] +amount  

    print("  Sold %f %s for %f %s" % (price, cur_sell, amount, cur_buy))

#  def SellAll(self, price, couple):
#    print("Sell all")
#    self.PrintBalance()
#    
#    cur=couple.split('_')
#    cur_buy  = cur[0]
#    cur_sell = cur[1]
#    
#    amount=self.__F[cur_sell]
#
#    self.PlaceOrder(price, amount, couple)
#    self.PrintBalance()
     
