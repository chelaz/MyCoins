#!/usr/bin/python3

import datetime
import sys

class MyTrade:

  __F  = None # (Funds) Balance { 'btc' : 0.0, 'dsh' : 0.0, 'eth' : 0.0 }
  __O  = []   # Order Book
  __Ha = []   # Orders History ask
  __Hb = []   # Orders History bid
  __HF = []   # [[ ts, price, f ] ,...] # f is copy of __F

  __Ea = []   # event ask
  __Eb = []   # event bid

  __HaCanceled = 0
  __HbCanceled = 0

  __HaBankrupt = 0
  __HbBankrupt = 0

  __TypeOfLastFilled = {'': [ '', 0 ] } # eg: [ 'bid', ts ]

  __tmp_ts  = 0
  __tmp_age = 0
   
  def __init__(self, StartBalance = { 'btc' : 0.0, 'dsh' : 0.0, 'eth' : 0.0 } ):
    self.__StartBalance = dict(StartBalance) # explicit copy of fund
    self.__F = StartBalance

  def GetF(self):
    return self.__F

  def LenOrderBook(self):
    return len(self.__O)

  def LenOrderHistAsk(self):
    return len(self.__Ha)

  def LenOrderHistBid(self):
    return len(self.__Hb)

  def NumBankruptAsk(self):
    return self.__HaBankrupt

  def NumBankruptBid(self):
    return self.__HbBankrupt

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
    return self.__TypeOfLastFilled[id][0]
 
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
    op = o['price']
    if o['type'] == 'ask':
      if op > price:
        self.FillOrderAsk(op, o['amount'], o['couple'], o['id'], ts=ts)
        self.__Ha.append([ts, op, o['id']])
        self.__HF.append([ts, op, o['couple'], dict(self.__F)]) # make copy of balance

        Ret=False # remove from list
    else:
      if op < price:
        self.FillOrderBid(op, o['amount'], o['couple'], o['id'], ts=ts)
        self.__Hb.append([ts, op, o['id']])
        self.__HF.append([ts, op, o['couple'], dict(self.__F)]) # make copy of balance

        Ret=False # remove from list
    return Ret

  def __CheckTypeAsk(self, o):
    return o['type'] == 'ask'

  def __CheckTypeBid(self, o):
    return o['type'] == 'bid'

  def CancelOrders(self, type):
    if type == 'ask':    
      OrdersRemoved=list(filter(self.__CheckTypeBid, self.__O))
      self.__HaCanceled += len(self.__O)-len(OrdersRemoved)
    else:
      OrdersRemoved=list(filter(self.__CheckTypeAsk, self.__O))
      self.__HbCanceled += len(self.__O)-len(OrdersRemoved)
 
    Debug=True
    if Debug:
      print("OrdersRemoved: %d of type %s. Remaining Order Book:" % (len(self.__O)-len(OrdersRemoved), type))
      for o in self.__O:
        print("  "+str(o))

    self.__O = OrdersRemoved    


  # {'type':'ask', 'price':price, 'amount':amount, 'couple':couple}
  # ts is current timestamp, age is cur ts minus place order ts
  def FillOrders(self, price, age=0, ts=0, Debug=False):
    if Debug:
      print("FillOrders with price %f" % price)

    if Debug:
      print("Orders before remove outdated:")
      for o in self.__O:
        print("  "+str(o))

#    AlternatingAge=10000
    AlternatingAge=1000000


    #print("last filled: "+str(self.__TypeOfLastFilled))
    for id in self.__TypeOfLastFilled:
      v = self.__TypeOfLastFilled[id]
      #print("id: "+str(v))
      if ts-v[1] > AlternatingAge:
        v[0] = ''
        v[1] = 0
    #print("last filled after deletion: "+str(self.__TypeOfLastFilled))
         
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

  def PrintEventAsk(self):
    print("PrintEventAsk")
    for f in self.__Ea:
      print("  "+str(f))

  def PrintEventBid(self):
    print("PrintEventBid")
    for f in self.__Eb:
      print("  "+str(f))

  def PrintHistBid(self):
    print("PrintHistBid")
    for f in self.__Hb:
      print("  "+str(f))
   

  def GetPlotHistAsk(self):
    return (list(map(lambda v:v[0], self.__Ha)), list(map(lambda v:v[1],self.__Ha)))
 
  def GetPlotHistBid(self):
    return (list(map(lambda v:v[0], self.__Hb)), list(map(lambda v:v[1],self.__Hb)))

  def GetPlotEventAsk(self):
    return (list(map(lambda v:v[0], self.__Ea)), list(map(lambda v:v[1],self.__Ea)))
 
  def GetPlotEventBid(self):
    return (list(map(lambda v:v[0], self.__Eb)), list(map(lambda v:v[1],self.__Eb)))


  # eg: amount=0.24, price=0.08, base=1.0, currency=dsh
  def RecalcToCurrency(self, uprice, F, couple):
    cur=couple.split('_')
    cur_buy  = cur[0]
    cur_sell = cur[1]

    price = uprice*(self.__StartBalance[cur_buy]-F[cur_buy])
    #print("Equalized: with uprice %f %s to %f %s" % (uprice, cur_buy+"/"+cur_sell, F[cur_sell]-price, cur_sell))

    return F[cur_sell]-price

  def GetPlotHistBalance(self, currency):
    Factor=1.0 # 18.0
    Add=0.0 #-16.15-1.835
    return (list(map(lambda v:v[0], self.__HF)), list(map(\
            lambda v:self.RecalcToCurrency(v[1], v[3], v[2])*Factor+Add, \
           # lambda v:v[2][currency]*Factor+Add,\
            self.__HF)))
 
  def PlaceOrderAsk(self, price, amount, couple, ts=0, id='', OnlyAlternating=False, OverwriteOrder=False):
    if OnlyAlternating:
      if self.GetTypeOfLastFilled(id) == 'ask':
        return False
      if self.HasActiveAsk():
        if not OverwriteOrder:
          return False
        else:
          self.CancelOrders('ask')
    self.__O.append({'type':'ask', 'price':price, 'amount':amount, 'couple':couple, 'ts':ts, 'id':id})
    self.__Ea.append([ts, price, id])
 
    #print("Order Book:")
    #for o in self.__O:
    #  print("  "+str(o))


  def PlaceOrderBid(self, price, amount, couple, ts=0, id='', OnlyAlternating=False, OverwriteOrder=False):
    if OnlyAlternating:
      if self.GetTypeOfLastFilled(id) == 'bid':
        return False
      if self.HasActiveBid():
        if not OverwriteOrder:
          return False
        else:
          self.CancelOrders('bid')
    self.__O.append({'type':'bid', 'price':price, 'amount':amount, 'couple':couple, 'ts':ts, 'id':id})
    self.__Eb.append([ts, price, id])
 
    #print("Order Book:")
    #for o in self.__O:
    #  print("  "+str(o))

    
  # PlaceOrder(0.08, 1, "dsh_btc") # buy 1 dsh for 0.08 btc
  def FillOrderAsk(self, price, amount, couple, id='', ts=0):
    cur=couple.split('_')
    cur_ask  = cur[0]  # dsh
    cur_sell = cur[1]  # btc
   
    sell_price = price*amount # in btc
     
    if self.__F[cur_sell] < sell_price: # btc
      self.__HaBankrupt +=1
      return 0.0
    self.__F[cur_sell] = self.__F[cur_sell]-sell_price #btc
    self.__F[cur_ask]  = self.__F[cur_ask] +amount  #dsh

    self.__TypeOfLastFilled[id] = [ 'ask', ts ]

    #print("  [%d] Sold   %f %s for %f %s at exchange rate %f %s/%s" % (ts, sell_price, cur_sell, amount, cur_ask, price, cur_sell, cur_ask))
    print("  [%d] Bought %f %s for %f %s at exchange rate %f %s/%s" % (ts, amount, cur_ask, sell_price, cur_sell, price, cur_sell, cur_ask))


  def FillOrderBid(self, price, amount, couple, id='', ts=0):
    cur=couple.split('_')
    cur_bid = cur[0] # dsh gets less
    cur_buy = cur[1] # btc gets more
   
    buy_price = price*amount
     
    if self.__F[cur_bid] < amount: # btc
      #print("Avail amount %f %s is too less to sell %f" % (self.__F[cur_bid], cur_bid, amount))
      self.__HbBankrupt +=1
      return 0.0
    self.__F[cur_buy] = self.__F[cur_buy]+buy_price # btc
    self.__F[cur_bid] = self.__F[cur_bid]-amount # dsh

    self.__TypeOfLastFilled[id] = [ 'bid', ts ]

 #  print("  [%d] Bought %f %s for %f %s at exchange rate %f %s/%s" % (ts, buy_price, cur_buy, amount, cur_bid, price, cur_buy, cur_bid))
    print("  [%d] Sold   %f %s for %f %s at exchange rate %f %s/%s" % (ts, amount, cur_bid, buy_price, cur_buy, price, cur_buy, cur_bid))

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
      self.FillOrderBid(price, self.__F[cur_buy]-self.__StartBalance[cur_buy], couple, id='FinalFill')


    self.PrintBalance()

                              

        
