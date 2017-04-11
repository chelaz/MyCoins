#!/usr/bin/python3

import datetime
import sys

class MyTrade:

  __F  = None # (Funds) Balance { 'btc' : 0.0, 'dsh' : 0.0, 'eth' : 0.0 }
  __O  = []   # Order Book
  __Ha = []   # Orders History ask
  __Hb = []   # Orders History bid
  __HaCanceled = 0
  __HbCanceled = 0

  __TypeOfLastFilled = {'':''}

  __tmp_ts  = 0
  __tmp_age = 0
   
  def __init__(self, StartBalance = { 'btc' : 0.0, 'dsh' : 0.0, 'eth' : 0.0 } ):
    self.__StartBalance = dict(StartBalance) # explicit copy of fund
    self.__F = StartBalance

  def LenOrderBook(self):
    return len(self.__O)

  def LenOrderHistAsk(self):
    return len(self.__Ha)

  def LenOrderHistBid(self):
    return len(self.__Hb)

  def CanceledAsk(self):
    return self.__HaCanceled

  def CanceledBid(self):
    return self.__HbCanceled

  def HasActiveBid(self):
    for o in self.__O:
      if o['type'] == 'bid':
        return True
    return False
 
  def HasActiveAsk(self):
    for o in self.__O:
      if o['type'] == 'ask':
        return True
    return False

  def GetTypeOfLastFilled(self, id=''):
    if not id in self.__TypeOfLastFilled:
      return ''
    return self.__TypeOfLastFilled[id]
 
  ############ Helpers for FillOrders
  def __CheckOutdated(self, o):
    bOutdated = self.__tmp_ts-o['ts'] > self.__tmp_age
    if bOutdated:
      if o['type'] == 'ask':
        self.__HaCanceled +=1
      else:
        self.__HbCanceled +=1
    return not bOutdated

  def __CheckAndFillOrders(self, o):
    Ret=True
    ts    = self.__tmp_ts
    price = self.__tmp_price
    #print("CheckAndFillOrders ts %d price %f o %s" % (ts, price, str(o)))
    if o['type'] == 'ask':
      if o['price'] > price:
        self.FillOrderAsk(price, o['amount'], o['couple'], o['id'], ts=ts)
        self.__Ha.append([ts, price, o['id']])
        Ret=False # remove from list
    else:
      if o['price'] < price:
        self.FillOrderBid(price, o['amount'], o['couple'], o['id'], ts=ts)
        self.__Hb.append([ts, price, o['id']])
        Ret=False # remove from list
    return Ret

  # {'type':'ask', 'price':price, 'amount':amount, 'couple':couple}
  # ts is current timestamp, age is cur ts minus place order ts
  def FillOrders(self, price, age=0, ts=0):
    Debug=False
    if Debug:
      print("FillOrders with price %f" % price)

    if Debug:
      print("Orders before remove outdated:")
      for o in self.__O:
        print("  "+str(o))
 
    self.__tmp_ts    = ts
    self.__tmp_age   = age
    self.__tmp_price = price

    if age > 0 and ts > 0:
      OrdersRemovedOutdated=list(filter(self.__CheckOutdated, self.__O))
    else:
      OrdersRemovedOutdated=self.__O

    if Debug:
     print("OrdersRemovedOutdated: %d" % (len(self.__O)-len(OrdersRemovedOutdated)))
     for o in OrdersRemovedOutdated:
        print("  "+str(o))
    
    self.__O=list(filter(self.__CheckAndFillOrders, OrdersRemovedOutdated))

    if Debug:
      print("OrdersNotFilled:")
      for o in self.__O:
        print("  "+str(o))
 
#    #OrdersOutdated=[] # or filled
#    for o in OrdersRemovedOutdated:
#      if o['type'] == 'ask':
#        if o['price'] > price:
#          self.FillOrderAsk(price, o['amount'], o['couple'], ts=ts)
#          #OrdersOutdated.append(i)
#          self.__Ha.append([ts, price])
#      else:
#        if o['price'] < price:
#          self.FillOrderBid(price, o['amount'], o['couple'], ts=ts)
#          #OrdersOutdated.append(i)
#          self.__Hb.append([ts, price])

#    O = dict(self.__O)
#    for i in OrdersOutdated:
#      #if Debug:
#      print("  ->remove order due to age %d > %d:" % (ts-o['ts'], age) +str(o))
#      #self.__O.remove(o)
#      del self.__O[i]

  def PrintBalance(self):
    print("Balance")
    for f in self.__F:
      print("  %s: %f" % (f, self.__F[f]))

  def PrintStartBalance(self):
    print("StartBalance")
    for f in self.__StartBalance:
      print("  %s: %f" % (f, self.__StartBalance[f]))

  def PrintHistAsk(self):
    print("PrintHistAsk")
    for f in self.__Ha:
      print("  "+str(f))

  def PrintHistBid(self):
    print("PrintHistBid")
    for f in self.__Hb:
      print("  "+str(f))
   

  def GetPlotHistAsk(self):
    return (list(map(lambda v:v[0], self.__Ha)), list(map(lambda v:v[1],self.__Ha)))
 
  def GetPlotHistBid(self):
    return (list(map(lambda v:v[0], self.__Hb)), list(map(lambda v:v[1],self.__Hb)))
 
  def PlaceOrderAsk(self, price, amount, couple, ts=0, id=''):
    self.__O.append({'type':'ask', 'price':price, 'amount':amount, 'couple':couple, 'ts':ts, 'id':id})

  def PlaceOrderBid(self, price, amount, couple, ts=0, id=''):
    self.__O.append({'type':'bid', 'price':price, 'amount':amount, 'couple':couple, 'ts':ts, 'id':id})
     
  # PlaceOrder(0.08, 1, "dsh_btc") # buy 1 dsh for 0.08 btc
  def FillOrderAsk(self, price, amount, couple, id='', ts=0):
    cur=couple.split('_')
    cur_ask  = cur[0]  # dsh
    cur_sell = cur[1]  # btc
   
    sell_price = price*amount # in btc
     
    if self.__F[cur_sell] < sell_price: # btc
      return 0.0
    self.__F[cur_sell] = self.__F[cur_sell]-sell_price #btc
    self.__F[cur_ask]  = self.__F[cur_ask] +amount  #dsh

    self.__TypeOfLastFilled[id] = 'ask'

    print("  [%d] Sold %f %s for %f %s at exchange rate %f %s/%s" % (ts, sell_price, cur_sell, amount, cur_ask, price, cur_sell, cur_ask))

  def FillOrderBid(self, price, amount, couple, id='', ts=0):
    cur=couple.split('_')
    cur_bid = cur[0] # dsh gets less
    cur_buy = cur[1] # btc gets more
   
    buy_price = price*amount
     
    if self.__F[cur_bid] < amount: # btc
      #print("Avail amount %f %s is too less to sell %f" % (self.__F[cur_bid], cur_bid, amount))
      return 0.0
    self.__F[cur_buy] = self.__F[cur_buy]+buy_price # btc
    self.__F[cur_bid] = self.__F[cur_bid]-amount # dsh

    self.__TypeOfLastFilled[id] = 'bid'

    print("  [%d] Bought %f %s for %f %s at exchange rate %f %s/%s" % (ts, buy_price, cur_buy, amount, cur_bid, price, cur_buy, cur_bid))

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
      self.FillOrderAsk(price, self.__StartBalance[cur_buy]-self.__F[cur_buy], couple, id='FinalFill')
    else:
      self.FillOrderBid(price, self.__F[cur_buy]-self.__StartBalance[cur_buy], couple)


    self.PrintBalance()

                              

        
