#!/usr/bin/python3

import datetime
import sys

class MyTrade:

  __F = None # (Funds) Balance { 'btc' : 0.0, 'dsh' : 0.0, 'eth' : 0.0 }
  __O = []   # Orders

  def __init__(self, StartBalance = { 'btc' : 0.0, 'dsh' : 0.0, 'eth' : 0.0 } ):
    self.__StartBalance = dict(StartBalance) # explicit copy of fund
    self.__F = StartBalance

  # {'type':'ask', 'price':price, 'amount':amount, 'couple':couple}
  # ts is current timestamp, age is cur ts minus place order ts
  def FillOrders(self, price, age=0, ts=0):
    Debug=True
    if Debug:
      print("FillOrders")

    OrdersOutdated=[]
    for o in self.__O:
      if Debug:
        print("  "+str(o))
      if age > 0 and ts > 0:
        if ts-o['ts'] > age:
          OrdersOutdated.append(o)
          continue
      if o['type'] == 'ask':
        if o['price'] > price:
          self.FillOrderAsk(price, o['amount'], o['couple'])
      else:
        if o['price'] < price:
          self.FillOrderBid(price, o['amount'], o['couple'])

    for o in OrdersOutdated:
      if Debug:
        print("  ->remove order due to age %d:" % (ts-o['ts']) +str(o))
      self.__O.remove(o)

  def PrintBalance(self):
    print("Balance")
    for f in self.__F:
      print("  %s: %f" % (f, self.__F[f]))

  def PrintStartBalance(self):
    print("StartBalance")
    for f in self.__StartBalance:
      print("  %s: %f" % (f, self.__StartBalance[f]))

  def PlaceOrderAsk(self, price, amount, couple, ts=0):
    self.__O.append({'type':'ask', 'price':price, 'amount':amount, 'couple':couple, 'ts':ts})

  def PlaceOrderBid(self, price, amount, couple, ts=0):
    self.__O.append({'type':'bid', 'price':price, 'amount':amount, 'couple':couple, 'ts':ts})
     
  # PlaceOrder(0.08, 1, "dsh_btc") # buy 1 dsh for 0.08 btc
  def FillOrderAsk(self, price, amount, couple):
    cur=couple.split('_')
    cur_ask  = cur[0]  # dsh
    cur_sell = cur[1]  # btc
   
    sell_price = price*amount # in btc
     
    if self.__F[cur_sell] < sell_price: # btc
      return 0.0
    self.__F[cur_sell] = self.__F[cur_sell]-sell_price #btc
    self.__F[cur_ask]  = self.__F[cur_ask] +amount  #dsh

    print("  Sold %f %s for %f %s at exchange rate %f %s/%s" % (sell_price, cur_sell, amount, cur_ask, price, cur_sell, cur_ask))

  def FillOrderBid(self, price, amount, couple):
    cur=couple.split('_')
    cur_bid = cur[0] # dsh gets less
    cur_buy = cur[1] # btc gets more
   
    buy_price = price*amount
     
    if self.__F[cur_bid] < amount: # btc
      print("Avail amount %f %s is too less to sell %f" % (self.__F[cur_bid], cur_bid, amount))
      return 0.0
    self.__F[cur_buy] = self.__F[cur_buy]+buy_price # btc
    self.__F[cur_bid] = self.__F[cur_bid]-amount # dsh

    print("  Bought %f %s for %f %s at exchange rate %f %s/%s" % (buy_price, cur_buy, amount, cur_bid, price, cur_buy, cur_bid))

  def SellAll(self, price, couple):
    cur=couple.split('_')
    cur_buy  = cur[0]
    cur_sell = cur[1]
    
    print("Sell all")

    self.PlaceOrderBid(price, self.__F[cur_buy], couple)

    self.PrintBalance()

  def SellToEqualizeStartBalance(self, price, couple):
    cur=couple.split('_')
    cur_buy  = cur[0]
    cur_sell = cur[1]
 
    print("Sell to equalize")
    self.PrintBalance()

    if self.__StartBalance[cur_buy] > self.__F[cur_buy]:
      self.FillOrderAsk(price, self.__StartBalance[cur_buy]-self.__F[cur_buy], couple)
    else:
      self.FillOrderBid(price, self.__F[cur_buy]-self.__StartBalance[cur_buy], couple)


    self.PrintBalance()

                              

        
