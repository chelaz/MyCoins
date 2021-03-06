#!/usr/bin/python3

# vim:
#set smartindent
#set tabstop=2
#set shiftwidth=2
#set expandtab


#{'success': 1, 'return': {'funds': {'usd': 0, 'btc': 7e-05, 'ltc': 0, 'nmc': 0, 'rur': 0, 'eur': 0, 'nvc': 0, 'trc': 0, 'ppc': 0, 'ftc': 0, 'xpm': 0, 'cnh': 0, 'gbp': 0, 'dsh': 0.23952001, 'eth': 0.5988}, 'rights': {'info': 1, 'trade': 0, 'withdraw': 0}, 'transaction_count': 0, 'open_orders': 0, 'server_time': 1490357983}}
#{'type': 4, 'amount': 0.5988, 'currency': 'ETH', 'desc': 'Buy 0.6 ETH (-0.2%) from your order :order:1653889701: by price 0.03455 BTC', 'status': 2, 'timestamp': 1489664887}


#trades:api/2
#149: {'date': 1490392308, 'price': 964, 'amount': 0.00363446, 'tid': 95990860, 'price_currency': 'USD', 'item': 'BTC', 'trade_type': 'bid'}

#trades:api/3
#1999: {'type': 'ask', 'price': 963.253, 'amount': 0.3754092, 'tid': 95986030, 'timestamp': 1490389511}

import datetime,time
import json
import os.path
import sys

from btceapi import api
from Keys import Keys
from MyTrade import MyTrade
from MySimu import SimuConf
from MyAlgos import MyAlgos
from MyAlgos import MyTime
from MyAlgos import MyH

class MyRich:
  # cmd line args
  week=0 # 0 is this week
  weeks=[] # list of weeks given by cmd line args comma separated
  year=0 # 0 is this year
  couple='dsh_btc'
   
  version=None
  __filename=""

  C = None # Configuration if set 

  # data member
  __API = None  # Instance of BTCeAPI

  # V01: [ts, couple, {"type": "ask", "price": 83.696, "amount": 0.17413282, "tid": 96247757}]
  __L  = []   # Trades History
  __OB = {}   # current Orderbook: {'asks": [[price, amount],...], 'bids':[[price, amount],...]
  __F = []    # Funds
  __V = 1     # File Version
  __A = None  # MyAlgos

  __L_TID = dict() # dict of couples with dicts, sorted by tid: __L_TID[couple]: tid: (ts, price, amount)

  __AvailCouples = [ "dsh_btc",
                     "dsh_eur", 
                     "dsh_usd",
                     "btc_usd",
                     "btc_eur",
                     "eth_btc",
                     "eth_eur",
                     "eth_usd" ]


  __DebugTS=0
  __FromTS=0
  __ToTS=0

  __DataPath = "FuncTests/"
  __StartDate = MyTime()


  # functions
  def __init__(self, Keys):
    self.__API = api(api_key=Keys.Key, api_secret=Keys.Secret, wait_for_nonce=True)
    self.__A   = MyAlgos()

  def SetDataPath(self, DataPath):
    if DataPath[-1] != '/':
      self.__DataPath=DataPath+"/"
    else:
      self.__DataPath=DataPath

  def SetDebugTS(self, ts):
    self.__DebugTS = ts

  def SetFromTS(self, ts):
    self.__FromTS = ts

  def SetToTS(self, ts):
    self.__ToTS = ts

  def PrintElapsed(self, Str=""):
    print("_> ", end='')
    self.__StartDate.PrintDiff(end='') 
    print(" elapsed for %s " % Str)

  def GetStartDate(self):
    return self.__StartDate

  def Info(self):
    I=self.__API.getInfo()
    print("Info:\n  Balance from Server:")
    #print(I)
    self.__F=I['return']['funds']
     
    for v in self.__F:
      if self.__F[v] > 0:
        print("    %s: %s" % (v, self.__F[v]))
    SrvTm = MyTime(I['return']['server_time'])
    print("  Server Time: "+SrvTm.Str())
    print("-----------------------------------------")

  def GetServerBalance(self, currency):
    if currency in self.__F:
      return float(self.__F[currency])
    else:
      return 0.0

  def CleanHist(self):
    self.__L = []

  def TransHist(self, BeginDay, EndDay):
    History=self.__API.TransHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="ASC", tsince=BeginDay, tend=EndDay)
    #print(History)

    if (History and History['success']):
      Ret=History['return']
      for v in Ret:
        TransTime=MyTime((Ret[v]['timestamp']))
        print(TransTime.Str(), end='')
        print(Ret[v])


  def RecOrder(self, couple, limit=10):
    self.__OB[couple] = self.__API.get_param3(couple, method='depth', param="limit=%d"%limit)[couple]

    Debug=False

    if Debug:
     print("Order Book (%s):" % couple)
     for i in range(limit):
       a = self.__OB[couple]['asks'][i]
       b = self.__OB[couple]['bids'][i]
       print("  %9f (%9f)" % (a[0], a[1]), end='')
       print(" - %9f - " % (a[0]-b[0]), end='' )
       print("  %9f (%9f)" % (b[0], b[1]))



  # we use RecPublicTrades function below
  def __unused_PublicTrades(self, couple):
    T=self.__API.get_param3(couple, method='trades', param="limit=100")

    cnt=0
    for v in T[couple]:
      print ("%4d: " % cnt, end='')
      Time=MyTime(v['timestamp'])
      print(Time.Str(), end='')
      print(v)
      cnt+=1

  def _SortByTimestamp(self, item):
    return item[0]

  def _SortByTID(self, item):
    return item[2]['tid']


  # Tuples: 
  # V00:  [1490601525, "2017-03-27 09:58:45", "dsh_eur", {"type": "ask", "price": 83.696, "amount": 0.17413282, "tid": 96247757, "timestamp": 1490601525}]
  # V01:  [1490601525, "dsh_eur", {"type": "ask", "price": 83.696, "amount": 0.17413282, "tid": 96247757}]
  def _BuildTuple(v, couple, timestamp=0):
    if timestamp == 0:
      ts = v['timestamp']
      del v['timestamp']
    else:
      ts = timestamp
    return [ts, couple, v]
#    return [v['timestamp'], MyTime(v['timestamp']).str(), couple, v]


  def BuildPriceDict(self, couple):
    self.__L_TID[couple] = { v[2]['tid']: (v[0], v[2]['price'], v[2]['amount']) for v in filter(lambda v : v[1] == couple, self.__L) }
   
    Debug=False

    if Debug:
      print("List")
      for v in self.__L:
        print("  v: '%s'" % (str(v)))

      print("Price Dict for %s" % couple)
      for tid in self.__L_TID[couple]:
        print("  tid=%d v: '%s'" % (tid, str(self.__L_TID[couple][tid])))

  # (ts, price, amount)
  def GetPriceList(self, couple):
    return list(map(lambda v : (v[0], v[2]['price'], v[2]['amount']),
                filter(lambda v : v[1] == couple, self.__L)))
   
  # returns (tid, ts, price, amount)
  def __GetPriceTuple(self, tid, couple):
    #L_couple = list(filter(lambda v : v[1] == couple, self.__L))
    #v_nearest=L_couple[0]
    #for v in L_couple:
    #  if v[0] > ts:
    #    break
    #  v_nearest = v
    #return v_nearest[2]['price']

    L_TID=self.__L_TID[couple]
    if L_TID == None:
      return (None, None, None, None) 

    cnt=0
    while not tid+cnt in L_TID and cnt < 1000:
      cnt += 1

    if cnt == 1000:
      return (None, None, None, None)

    return (tid+cnt, *L_TID[tid+cnt])


  # couples
  #  "dsh_btc"
  #  "dsh_eur"
  #  "dsh_usd"
  #  "btc_usd"
  #  "btc_eur"
  #  "eth_btc"
  #  "eth_eur"
  #  "eth_usd"

  # chains: normal: sell - inverse: buy
  ## 1. btc ->(b) dsh ->(s) eur ->(b) btc
  # 2. btc ->(s) eur ->(b) dsh ->(s) btc
 
  def GetPriceInChain(self, tid, btc):

    (tid_dsh_btc, ts_dsh_btc, p_dsh_btc, a) = self.__GetPriceTuple(tid, "dsh_btc")
    (tid_dsh_eur, ts_dsh_eur, p_dsh_eur, a) = self.__GetPriceTuple(tid, "dsh_eur")
    (tid_btc_eur, ts_btc_eur, p_btc_eur, a) = self.__GetPriceTuple(tid, "btc_eur")

    if tid_dsh_btc == None:
      return
    if tid_dsh_eur == None:
      return
    if tid_btc_eur == None:
      return

    return self.GetPriceInChainWPrices(btc, p_dsh_btc, p_dsh_eur, p_btc_eur) 

  def GetPriceInChainWPrices(self, btc, p_dsh_btc, p_dsh_eur, p_btc_eur): 

    Debug=False
    ## buy dsh (ask)
    #btc -= p_dsh_btc*amount # in btc
    #dsh += amount

    ## sell dsh
    #eur += p_dsh_eur*amount # in eur
    #dsh -= amount

    ## buy btc
    #amount2 = eur
    #eur -= p_btc_eur*amount2 # in eur
    #btc += amount2

    ###########
    dsh    = 0.0
    eur    = 0.0

    # 1. btc ->(b) dsh ->(s) eur ->(b) btc

    # buy_dsh 
    (a_dsh, p_btc) = MyTrade.CalcTrading2(p_dsh_btc, btc)  # dsh_btc = 0.08
    dsh += a_dsh # 0.25
    btc += p_btc # 0

    # sell dsh 
    (a_dsh, p_eur) = MyTrade.CalcTrading1(p_dsh_eur, -dsh) # dsh_eur = 100
    dsh += a_dsh # 0
    eur += p_eur # 25

    # buy btc    
    (a_btc, p_eur) = MyTrade.CalcTrading2(p_btc_eur, eur) # btc_eur = 1000
    btc += a_btc # 0.025
    eur += p_eur # 0

    if Debug:
      print("PriceInChain balance:")
      print("  btc: %f" % btc)
      print("  dsh: %f" % dsh)
      print("  eur: %f" % eur)

    return btc


  def GetPriceInChainWPricesR(self, btc, p_dsh_btc, p_dsh_eur, p_btc_eur):
    Debug=False

    dsh    = 0.0
    eur    = 0.0
   
    # sell btc    
    (a_btc, p_eur) = MyTrade.CalcTrading1(p_btc_eur, -btc) 
    btc += a_btc # 0.025
    eur += p_eur # 0

    # buy dsh 
    (a_dsh, p_eur) = MyTrade.CalcTrading2(p_dsh_eur, eur) # dsh_eur = 100
    dsh += a_dsh # 0
    eur += p_eur # 25

    # sell dsh 
    (a_dsh, p_btc) = MyTrade.CalcTrading1(p_dsh_btc, -dsh)  # dsh_btc = 0.08
    dsh += a_dsh # 0.25
    btc += p_btc # 0

    if Debug:
      print("PriceInChain balance:")
      print("  btc: %f" % btc)
      print("  dsh: %f" % dsh)
      print("  eur: %f" % eur)

    return btc


  # GetPriceInChainWPriceGen("btc_dsh_usd_btc") 
  def GetPriceInChainWPriceGen(self, chain_str, doBuy=False):
    Chain = chain_str.split('_')
    
    Couples = []

    for i in range(len(Chain)-1):
      print("Checking %s_%s" % (Chain[i], Chain[i+1]))
      if "%s_%s" % (Chain[i], Chain[i+1]) in self.__AvailCouples:
        Couples.append((Chain[i], Chain[i+1], False, 
                        "%s_%s" % (Chain[i], Chain[i+1])))
      elif "%s_%s" % (Chain[i+1], Chain[i]) in self.__AvailCouples:
        Couples.append((Chain[i], Chain[i+1], True,
        "%s_%s" % (Chain[i+1], Chain[i])))
      else:
        print("Requsted chain error %s: Couple %s_%s not available" % (chain_str, Chain[i], Chain[i+1]))
        return

    print("Found Chain:")
    for c in Couples:
      print(str(c))

    DoBuy=doBuy

    v = 1.0

    for c in Couples:

      self.RecOrder(c[3], 1)
      if (not DoBuy and c[2]) or (DoBuy and not c[2]):
        p = self.__OB[c[3]]['asks'][0][0]
      else:
        p = self.__OB[c[3]]['bids'][0][0]
    
      if DoBuy:
        amount=-v
      else:
        amount=v

      if c[2]: # reverse
        (v, v2) = MyTrade.CalcTrading2(p, amount)
      else:
        (a1, v) = MyTrade.CalcTrading1(p, amount)
      
      if DoBuy:
        print("Bought amount %f %s for price %f. got %f %s" % 
              (amount, c[0], p, v, c[1]))
      else: 
        print("Sold amount %f %s for price %f. got %f %s" % 
              (amount, c[0], p, v, c[1]))
        
      DoBuy = not DoBuy  

#    Debug=False
#
#    dsh    = 0.0
#    eur    = 0.0
#   
#    # sell btc    
#    (a_btc, p_eur) = MyTrade.CalcTrading1(p_btc_eur, -btc) 
#    btc += a_btc # 0.025
#    eur += p_eur # 0
#
#    # buy dsh 
#    (a_dsh, p_eur) = MyTrade.CalcTrading2(p_dsh_eur, eur) # dsh_eur = 100
#    dsh += a_dsh # 0
#    eur += p_eur # 25
#
#    # sell dsh 
#    (a_dsh, p_btc) = MyTrade.CalcTrading1(p_dsh_btc, -dsh)  # dsh_btc = 0.08
#    dsh += a_dsh # 0.25
#    btc += p_btc # 0
#
#    if Debug:
#      print("PriceInChain balance:")
#      print("  btc: %f" % btc)
#      print("  dsh: %f" % dsh)
#      print("  eur: %f" % eur)
#
#    return btc





  def ChainMode(self):
    Debug=False

    max_val=0
    for i in range(20):
      CurTime=MyTime()

      self.RecOrder("dsh_btc", 1)
      self.RecOrder("dsh_eur", 1)
      self.RecOrder("btc_eur", 1)

      btc=1.0
    
      #print(str(self.__OB))

      p_dsh_btc = self.__OB['dsh_btc']['asks'][0][0]
      p_dsh_eur = self.__OB['dsh_eur']['bids'][0][0]
      p_btc_eur = self.__OB['btc_eur']['asks'][0][0]

      if Debug:
        print("Using prices:")
        print("  dsh_btc: %f" % p_dsh_btc)
        print("  dsh_eur: %f" % p_dsh_eur)
        print("  btc_eur: %f" % p_btc_eur)

      val=self.GetPriceInChainWPrices(btc, p_dsh_btc, p_dsh_eur, p_btc_eur) 
      print("%s: btc->dsh->eur->btc: %f" % (CurTime.Str(), val))     

      p_dsh_btc = self.__OB['dsh_btc']['bids'][0][0]
      p_dsh_eur = self.__OB['dsh_eur']['asks'][0][0]
      p_btc_eur = self.__OB['btc_eur']['bids'][0][0]

      val=self.GetPriceInChainWPricesR(btc, p_dsh_btc, p_dsh_eur, p_btc_eur) 
      print("%s: btc->eur->dsh->btc: %f"  % (CurTime.Str(), val), end='')
      if val > 1.0:
        print(" <---- found")
        print("Used prices:")
        print("  dsh_btc: %f" % p_dsh_btc)
        print("  dsh_eur: %f" % p_dsh_eur)
        print("  btc_eur: %f" % p_btc_eur)
      else:
        print(" ")

      if val > max_val:
        max_val = val

      #time.sleep(5)

    print("Max: %f" % max_val)

  # Tuple in MMList: [ts, {'min': 0.074, 'max': 0.07415, 'amount': 6.835143370000001}]
  # now in MyH (MyAlgos) as a static function
  def _unused_BuildMinMaxList2(self, PriceList, winsize, Debug=False):

    L=PriceList #self.GetPriceList(couple)

    L2=L[winsize:]
    
    #if Debug:
    #  print("Starting List from %d" % L2[0])
    
    MMList = []

    for i in range(len(L2)):
      v=L2[i]
      min=v[1]
      max=v[1]
      sum=v[2]
      cnt=1
      
      for j in range(winsize):
        w=L[j+i+1]
        if Debug:
          print(" [%d] ts %d val: %f amount: %f" % (j+i+1, w[0], w[1], w[2])) 
        if min > w[1]:
          min=w[1]
        if max < w[1]:
          max=w[1]
        sum += w[2]
        cnt += 1

      if Debug:
        print("[%2d] ts %d val %f min: %f max: %f sum: %f cnt: %d" 
               % (i+winsize, v[0], v[1], min, max, sum, cnt))
 
      MMList.append([v[0], {'min':min, 'max':max, 'amount':sum , 'cnt':cnt }])
  
    return MMList

     
### Simulate Trading functions
  # T: MyTrade
  # C: SimuConf
  def SimulateTrading(self, T, C):

    self.__A.SetTrading(T)

    if self.__DebugTS > 0:
      print("Debug ts: %d" % self.__DebugTS)

    Debug=False

    if Debug:
      T.PrintBalance()

    L=self.GetPriceList(C.couple)

    if len(L) == 0:
      print("Length of trade list for %s is 0" % C.couple)
      return False

    #C.WinSize=100
    #PlaceBidFact=0.99
    #PlaceAskFact=1.01

    #cnt_bid=0
    #cnt_ask=0

    if C.OnlyAlternating:
      # Buy very first:
      v  = L[0]
      ts=v[0]
      price = v[1]*0.99
      print("Placing first order: %f" % price)
      T.PlaceOrderAsk(price, C.AltTradingVal, C.couple, id='first', ts=ts)

    ts_prev=0
    perc_prev=-1
    for i in range(len(L)):
      v  = L[i]
      #v is last traded value
      ts = v[0]

      if ts == self.__DebugTS:
        Debug = True
      else:
        Debug = False

      if Debug:
        print("<D>  ts=%d" % ts)

      if i <= C.WinSize:
        ts_prev = ts
        continue

      perc=round(i/len(L)*100, 0)
      if perc % 10 == 0:
        if perc_prev != perc:
          print("%2d%% [%s](%d)" % (perc, MyTime(ts).StrDayTime(), ts))
          perc_prev = perc

      if Debug:
        print("{%d} overall filled orders Ask=%d Bid=%d. Current orderbook: %d" % (ts, T.LenOrderHistAsk(), T.LenOrderHistBid(), T.LenOrderBook()))

      T.FillOrders(v[1], ts=ts, age=C.WinSize*10, Debug=Debug)
      #T.FillOrders(v[1], ts=ts, age=1000)

      #LastL = L[i-C.WinSize-1:i]
      LastL = L[:i]

      if C.SkipIfSameTS:
        if ts == ts_prev:
          continue

      #print("{%d}" %i, end='')
      C.Apply(v, LastL)

      ts_prev = ts

    # end for __L
    T.SellToEqualizeStartBalance(L[-1][1], C.couple)
    #T.SellAll(L[-1][1], couple)
    print("\n-------------------------------------\nSimulation Summary:");
    print("  Bankrupt ask: %d bid: %d" % (T.NumBankruptAsk(), T.NumBankruptBid()))
    print("  asked %d (canceled %d),  bid %d (canceled %d)" % \
          (T.LenOrderHistAsk()+T.CanceledAsk(), T.CanceledAsk(), \
           T.LenOrderHistBid()+T.CanceledBid(), T.CanceledBid()))

    T.PrintStartBalance()
    T.PrintBalance()
    C.Print()
    return True


### Plot functions

  # returns a tuple of two sequences: ([timestamp0..timestampn],[price0..pricen])
  def GetPlot(self, couple, NumCoins=1.0, Percentage=False):
    #L=self.__GetPlotListFromCouple(couple)
    L=self.GetPriceList(couple)
    if len(L) == 0:
      return []
    if Percentage:
      #first entry is 100 %
      factor=100.0/L[0][1]
      return (list(map(lambda v:v[0],L)), list(map(lambda v:v[1]*factor,L)))
    else:
      return (list(map(lambda v:v[0],L)), list(map(lambda v:v[1]*NumCoins,L)))
 
  
  def GetTimePerWSPlot(self):
    TPWSL = self.__A.GetTimePerWinSize()
    return (list(map(lambda v:v[0], TPWSL)), list(map(lambda v:v[1], TPWSL)))


  # Tuple in MMList: [1490910279, {'min': 0.074, 'max': 0.07415, 'amount': 6.835143370000001}]
  def GetMMPlot(self, couple, WinSize, Percentage=False):
    L=MyH.BuildMinMaxList(self.GetPriceList(couple), WinSize)
    factor=1.0

    if Percentage:
      factor=100.0/((L[0][1]['min']+L[0][1]['max'])/2.0) #first entry is 100 %
       
    MinPlot=(list(map(lambda v:v[0],L)), list(map(lambda v:v[1]['min']*factor,L)))
    MaxPlot=(list(map(lambda v:v[0],L)), list(map(lambda v:v[1]['max']*factor,L)))

    return MinPlot, MaxPlot

 
  def GetMMPlot2(self):
    MML = self.__A.GetMinMaxList()
    MinPlot=(list(map(lambda v:v[0], MML)), list(map(lambda v:v[1], MML)))
    MaxPlot=(list(map(lambda v:v[0], MML)), list(map(lambda v:v[2], MML)))
    SumPlot=(list(map(lambda v:v[0], MML)), list(map(lambda v:v[3], MML)))

    return MinPlot, MaxPlot, SumPlot
 

  def PlotInterCurrencyChain(self):
    self.BuildPriceDict("dsh_btc")
    self.BuildPriceDict("dsh_eur")
    self.BuildPriceDict("btc_eur")

    return (list(map(lambda v:v[0], self.__L)), 
            list(map(lambda v:self.GetPriceInChain(v[2]['tid'], 1.0), self.__L)))



### Crawler

  def RecPublicTrades(self, couple, limit=2000):
    T=self.__API.get_param3(couple, method='trades', param="limit=%d"%limit)

    cnt=0
    new=0
    for v in T[couple]:
      Tuple = MyRich._BuildTuple(v, couple)
      if not Tuple in self.__L:
        self.__L.append(Tuple)
        new+=1
      else:
        cnt+=1
      #else:
      #  print("Tuple already in list: ", end='')
      #  print(v)
    
    #if cnt > 0:
    #  print("  %d tuples already exist in list" % cnt)
    print("  %s: %d/%d new tuples" % (couple, new, new+cnt)) 
        
    self.__L=sorted(self.__L, key=self._SortByTimestamp)
 

  def PrintPublicTrades(self):
    #print (self.__L)
    #SortedList=sorted(self.__L, key=self._SortByTimestamp)
    #print(SortedList)

    for v in self.__L:
      print("  ", end='')
      print(v)


  def LoadWeeks(self, weeks, year=0):
    Loaded=False
    if len(weeks) == 0:
      if not self.LoadList(week=0, year=year):
        return False
      else:
        Loaded=True
    else:
      for w in weeks:
        if self.LoadList(week=w, year=year):
          Loaded=True
    return Loaded 

  def LoadList(self, version=None, week=0, year=0):
    if version == None:
      version = self.__V

    if self.__filename != "" and week == 0:
      FileName="%s%s.dat" % (self.__DataPath, self.__filename)
    else:
      if week == 0:
        week = self.__StartDate.Week()
      if year == 0:
        year = self.__StartDate.Year()
      FileName="%sTrades-V%02d-%4d-%02d.dat" % (self.__DataPath, version, year, week)

    print("Loading data from "+FileName, end='\n  ', flush=True) 
    if not os.path.isfile(FileName):
      print(" ..does not exist. Aborted.")
      return False

#    tid_L=list(map(lambda v : v[2]['tid'], self.__L))

    with open(FileName, "r") as ins:
      for line in ins:
#        if line.lstrip()[0] == '#':
        if line[0] == '#':
          print(line.lstrip(), end='')
          print("  ",end='')
          continue
        v=json.loads(line)
        if (len(v) == 4): # V0
          self.__L.append(MyRich._BuildTuple(v[3], v[2]))
        if (len(v) == 3): # V1
#          if v[2]['tid'] in tid_L:
#            print("  Skipping: "+str(v[2]))
#          else:
          self.__L.append(MyRich._BuildTuple(v[2], v[1], timestamp=v[0]))
#          tid_L.append(v[2]['tid'])
        if (len(self.__L) % 100000 == 0):
          print("[%d] " % len(self.__L), end='', flush=True)

    FirstEntry=MyTime(self.__L[0][0])
    LastEntry =MyTime(self.__L[-1][0])
    print(" ..loaded %d entries from %s (w %d) to %s (w %d)\n" % (len(self.__L), FirstEntry.Str(), FirstEntry.Week(), LastEntry.Str(), LastEntry.Week()))
    
    #self.__L=sorted(self.__L, key=self._SortByTimestamp)
    self.__L=sorted(self.__L, key=self._SortByTID)

    if self.__FromTS > 0:
      self.__L=list(filter(lambda v: v[0] >= self.__FromTS, self.__L))
    if self.__ToTS > 0:
      self.__L=list(filter(lambda v: v[0] <= self.__ToTS, self.__L))
 
    return True

  def _Save(self, FileName, L=None):
    if L == None:
      L = self.__L

    FirstEntry=MyTime(L[0][0])
    LastEntry =MyTime(L[-1][0])

    f=open(FileName, "w")
    f.write("#Num entries: %d \t from \t%s (w %d ts %d) \t to \t%s (w %d ts %d)\n" % (len(L), \
            FirstEntry.Str(), FirstEntry.Week(), FirstEntry.Timestamp(),\
            LastEntry.Str(),  LastEntry.Week(),  LastEntry.Timestamp()))
    for v in L:
      f.write(json.dumps(v)+"\n")
    f.close()
                                              

  def SaveList(self, version=None):
    #I=self.__API.getInfo()
    #SrvTm = MyTime(I['return']['server_time'])
  
    if version == None:
      version = self.__V

    if version == 0: 
      FileName="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, self.__StartDate.StrWeek())
      print("Saving data (%d entries) to %s" %(len(self.__L), FileName)) 

      f=open(FileName, "w")
      for v in self.__L:
        f.write(json.dumps(v))
        f.write("\n")
      f.close()

    if version == 1:
      print("Saving File version "+str(version))
      FirstEntry=MyTime(self.__L[0][0])
      LastEntry =MyTime(self.__L[-1][0])
      wk1 = FirstEntry.Week()
      wk2 = LastEntry.Week()
      if wk1 != wk2:
        print("  First entry wk: %d != %d last entry" % (wk1, wk2))

        self.LoadList(version=version, week=wk1, year=FirstEntry.Year())
        self.LoadList(version=version, week=wk2, year=LastEntry.Year())
      
        self.RemoveDuplicates()
                
        FileNameWk1="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, FirstEntry.StrWeek())
        FileNameWk2="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, LastEntry.StrWeek())
         
        L1 = list(filter(lambda v: MyTime(v[0]).Week() == wk1, self.__L))
        LN = list(filter(lambda v: MyTime(v[0]).Week() != wk1, self.__L))
   
        print("Saving data (%d entries) to %s" %(len(L1), FileNameWk1)) 
#        for v in L1:
#          print("Wk[%s] " % MyTime(v[0]).strWeek(), end='')
#          print(str(v))

        self._Save(FileNameWk1, L1)

#        L1_FirstEntry=MyTime(L1[0][0])
#        L1_LastEntry =MyTime(L1[-1][0])

#        f=open(FileNameWk1, "w")
#        f.write("#Num entries: %d \t from \t%s (w %d ts %d) \t to \t%s (w %d ts %d)\n" % (len(L1), \
#                L1_FirstEntry.Str(), L1_FirstEntry.Week(), L1_FirstEntry.Timestamp(),\
#                L1_LastEntry.Str(),  L1_LastEntry.Week(),  L1_LastEntry.Timestamp()))
#        for v in L1:
#          f.write(json.dumps(v)+"\n")
#        f.close()
      else:
        LN = self.__L
        FileNameWk2="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, LastEntry.StrWeek())
      
      print("Saving data (%d entries) to %s" %(len(LN), FileNameWk2)) 
      self._Save(FileNameWk2, LN)
                
      #LN_FirstEntry=MyTime(LN[0][0])
      #LN_LastEntry =MyTime(LN[-1][0])

#      for v in LN:
#        print("Wk[%s] " % MyTime(v[0]).strWeek(), end='')
#        print(str(v))

      #f=open(FileNameWk2, "w")
      #f.write("#Num entries: %d \t from \t%s (w %d ts %d) \t to \t%s (w %d ts %d)\n" % (len(LN), \
      #        LN_FirstEntry.Str(), LN_FirstEntry.Week(), LN_FirstEntry.Timestamp(),\
      #        LN_LastEntry.Str(),  LN_LastEntry.Week(),  LN_LastEntry.Timestamp()))
      #for v in LN:
      #  f.write(json.dumps(v)+"\n")
      #f.close()


  #  V01:  [1490601525, "dsh_eur", {"type": "ask", "price": 83.696, "amount": 0.17413282, "tid": 96247757}]
  def __uniquify(self, L):
    seen = set()
    for item in L:
      if item[2]['tid'] not in seen:
        seen.add(item[2]['tid'])
        yield item 
  
  def RemoveDuplicates(self):
    print("RemoveDuplicates: orig len %d " % len(self.__L), end='')
    self.__L=list(self.__uniquify(self.__L))
    print("new len %d " % len(self.__L))

  def RemoveDuplicatesMode(self, week=0, year=0):
    if self.LoadList(week=week, year=year):
      self.RemoveDuplicates()

      if self.__filename != "":
        self._Save(self.__filename+".dat", self.__L)
      else:
        self.SaveList()


  def Crawler(self):
    self.LoadList()

    self.RecPublicTrades("dsh_btc", limit=500)
    self.RecPublicTrades("dsh_eur", limit=1000)
    self.RecPublicTrades("dsh_usd", limit=500)
    self.RecPublicTrades("btc_usd")
    self.RecPublicTrades("btc_eur")
    self.RecPublicTrades("eth_btc", limit=500)
    self.RecPublicTrades("eth_eur")
    self.RecPublicTrades("eth_usd", limit=500)
    
    self.SaveList()

  def SimulateTradingAndPlot(self, couple, attrL):
    
#    C=SimuConf(T, Algo=self.AInterBand, couple=couple, WinSize=1000)
    C=SimuConf(couple=couple, WinSize=100, \
               PrepareFct=self.__A.ACalcMinMax, \
               Algos=[self.__A.AInterBand] \
               #Algos=[self.__A.AIntraBand] \
               #Algos=[self.__A.AInterBand, self.__A.AStopLoss] \
               #Algos=[self.__A.AApproachExtr, self.__A.AIntraBand] \
               #Algos=[self.__A.AApproachExtr] \
               )

    if "alt" in attrL:
      C.OnlyAlternating = True
    else:
      if "noalt" in attrL:
        C.OnlyAlternating = False
      #else: take default
 

#    C=SimuConf(T, Algo=self.__A.AStopLoss, couple=couple, WinSize=10)
#    C=SimuConf(T, Algo=self.SimuInterBand, couple=couple, WinSize=20)
#please edit in MySimu:    #C.OnlyAlternating=False
    #C.OverwriteOrder=True 
#    C.MinMaxEpsPerc=0.0
 
#  T=MyTrade({ 'btc' : 0.2, 'dsh' : 0.0, 'eth' : 0.0 }) 
    T=MyTrade(C, { 'btc' : 1.0, 'dsh' : 1.0, 'eth' : 1.0 }) 
#    T=MyTrade({ 'btc' : 1.0, 'dsh' : 0.0, 'eth' : 1.0 }) 

    self.C = C # save for external access

    self.SimulateTrading(T, C)
 
#    T.PrintHistAsk()
#    T.PrintEventAsk()  
#    T.PrintHistBid()
#    T.PrintEventBid()  

    dict = {}
    dict['ask'] = T.GetPlotHistAsk()
    dict['bid'] = T.GetPlotHistBid()
    dict['askAppr'] = T.GetPlotHistAsk('ApproachExtr')
    dict['bidAppr'] = T.GetPlotHistBid('ApproachExtr')
    dict['askIntr'] = T.GetPlotHistAsk('InterBand')
    dict['bidIntr'] = T.GetPlotHistBid('InterBand')
    dict['askStop'] = T.GetPlotHistAsk('StopLoss')
    dict['bidStop'] = T.GetPlotHistBid('StopLoss')
    dict['balance'] = T.GetPlotHistBalance("btc")
    dict['askApEv'] = T.GetPlotEventAsk('InterBand')
    dict['bidApEv'] = T.GetPlotEventBid('InterBand')
    dict['askSLEv'] = T.GetPlotEventAsk('StopLoss')
    dict['bidSLEv'] = T.GetPlotEventBid('StopLoss')
    dict['timePerWS'] = self.GetTimePerWSPlot()

    return dict

  def SimulateTradingMode(self, weeks=[], year=0):
    if not self.LoadWeeks(weeks, year):
      return

    self.RemoveDuplicates()

    Best_Bal=0.0
    Best_WS=0
    Best_P=0
    Best_Fact=0
    L_WZ = []

#    for w in [100, 290]:
#    for w in range(100, 400, 10):
    w = 290
    p = 0.05
    for pi in range(5, 6, 1):
      pf = pi/100

      T=MyTrade({ 'btc' : 1.0, 'dsh' : 1.0, 'eth' : 1.0 }) 

      C=SimuConf(T, Algo=self.AInterBand, couple="dsh_btc", WinSize=w, MinMaxEpsPerc=p) 
      C.PlaceBidFact = pf
      C.PlaceAskFact = pf
      C.Print()
      self.SimulateTrading(T, C)
      B=T.GetF()['btc']
      if Best_Bal < B:
        Best_Bal = B
        Best_WS  = w
        Best_P  = p
        Best_Fact = pf
      print("---------------> WinSize: %5d and Balance: %f, %f, %f\n\n" % (w, B, p, pf))
 
      L_WZ.append([w, B, p, pf]) 
    print("Best_Bal: %f with WinSize: %d, p %f, fact %f" % (Best_Bal, Best_WS, Best_P, Best_Fact)) 
    
    for w in L_WZ:
      print("  %s" % str(w))    


  def ConvertData_v0to1(self, week=0, year=0):
    if self.LoadList(version=0, week=week, year=year):
      self.SaveList(version=1)

  def FuncTest(self):
    # load V0 with different weeks -> save to different files
    self.SetDataPath("FuncTests")
    if self.LoadList(version=0, week=13, year=2017):
      self.SetDataPath("FuncTests/results")
      self.SaveList(version=1)
    self.CleanHist()
    if self.LoadList(version=1, week=14, year=2017):
      self.SetDataPath("FuncTests/results")
      self.SaveList(version=1)
 
    self.CleanHist()
    self.SetDataPath("FuncTests")
    if self.LoadList(version=1, week=14, year=2016):
      L=MyH.BuildMinMaxList(self.GetPriceList("dsh_btc"), 5)
      print("MMList")
      for v in L:
        print("  "+str(v))

    self.CleanHist()
    self.LoadList(version=1, week=14, year=2012)
    self.RemoveDuplicates()
    print("List after removed duplicates")
    self.SetDataPath("FuncTests/results")
    self.SaveList(version=1)
    for o in self.__L:
      print("  "+str(o))
 


  def InfoMode(self, week=0, year=0, version=None):
    if version == None:
      version = self.__V
    self.LoadList(version=version, week=week, year=year)

    couple="dsh_btc"
 
    L=self.GetPriceList(couple)

    perc_prev=0
    cnt_prev=0
    ts_prev=L[0][0]
    for i in range(len(L)):
      v  = L[i]
      ts = v[0]

      perc=round(i/len(L)*100, 0)
      if perc % 5 == 0:
        if perc_prev != perc:
          print("%3d%% [%s](%d) cnt %5d diff %d timediff %d" % \
                (perc, MyTime(ts).StrDayTime(), ts, i, i-cnt_prev, ts-ts_prev))
          cnt_prev  = i
          ts_prev   = ts
          perc_prev = perc



  def ParseCmdLineArgs(self, argv, modes, attrs=None):
    mode=""
    attrL=[]
    #week=0 # 0 is this week
    #year=0 # 0 is this year 
    #version=0

    if len(argv) > 1:
      for arg in argv:

        if arg in modes:
          mode = arg

        if attrs != None:
          if arg in attrs:
            attrL.append(arg)

        if "version" in arg:
          s = arg.split("=")
          MyRich.version=int(s[1])

        if "weeks" in arg:
          s = arg.split("=")
          if "," in s[1]:
            wks=s[1].split(',')
            #for w in wks:
            #  MyRich.weeks.append(int(w))
            MyRich.weeks=list(map(lambda w: int(w), wks))
            #print("cmd line weeks: "+str(MyRich.weeks))
            MyRich.week=MyRich.weeks[0]
          else:
            MyRich.weeks.append(int(s[1]))
            MyRich.week=int(s[1])
        else:
          if "week" in arg:
            s = arg.split("=")
            MyRich.weeks.append(int(s[1]))
            MyRich.week=int(s[1])

        if "fn" in arg:
          s = arg.split("=")
          MyRich.__filename=s[1]

        if "year" in arg:
          s = arg.split("=")
          MyRich.year=int(s[1])

        if "couple" in arg:
          s = arg.split("=")
          MyRich.couple=s[1]

        if "debugts" in arg:
          s = arg.split("=")
          self.SetDebugTS(int(s[1]))

        if "fromts" in arg:
          s = arg.split("=")
          self.SetFromTS(int(s[1]))

        if "tots" in arg:
          s = arg.split("=")
          self.SetToTS(int(s[1]))

        if "path" in arg:
          s = arg.split("=")
          self.SetDataPath(s[1])

        if arg == "help":
          ModeStr=""
          for m in modes:
            ModeStr = ModeStr+" ["+m+"]"
 
          AttrStr=""
          for a in attrs:
            AttrStr= AttrStr+" {"+a+"}"
           
          print("Usage: [] indicate modes and {} indicate attributes, configuration is [param=val]")
          print("  %s [help] [path=/DATA_PATH]%s %s [version=0] [year=0] [weeks=w1,..,wn] [fn=FILENAME] [fromts=0] [tots=0] [debugts=0]" % (argv[0], ModeStr, AttrStr))
          mode="help"

    return (mode, attrL)
 
###########################################################################

  def TestSaveV1(self):
    self.LoadList()
    #self.RecPublicTrades("dsh_btc", 10)
 
    for v in self.__L:
      print("Wk[%s] " % MyTime(v[0]).StrWeek(), end='')
      print(str(v))

    self.SaveList(1)

  def TestFillTrades(self):
    T=MyTrade({ 'btc' : 1.0, 'dsh' : 1.0, 'eth' : 1.0 }) 
  
    T.PrintBalance()

    T.PlaceOrderAsk( 0.08,    0.2, "dsh_btc", ts=10)
    T.PlaceOrderAsk( 0.06,    0.3, "dsh_btc", ts=11)
    T.PlaceOrderAsk( 0.09,    0.4, "dsh_btc", ts=12)
    T.PlaceOrderAsk( 0.07,    0.5, "dsh_btc", ts=13)
    T.PlaceOrderAsk( 0.04,    0.6, "dsh_btc", ts=14)
 
    T.FillOrders(0.07, ts=15, age=3)

    T.PrintHistAsk()
    T.PrintHistBid()
  
    T.PrintBalance()

  def TestRecalcToCurrency(self):
 
    self.LoadList(week=12)

 #  T=MyTrade({ 'btc' : 0.2, 'dsh' : 0.0, 'eth' : 0.0 }) 
    T=MyTrade({ 'btc' : 1.0, 'dsh' : 1.0, 'eth' : 1.0 }) 
  
    T.PrintBalance()

    T.PlaceOrderAsk( 0.09,    0.4, "dsh_btc", ts=12)
    T.FillOrders(0.07, ts=15, age=10)

    T.PlaceOrderBid( 0.05, 0.01, "dsh_btc", ts=12)
    T.FillOrders(0.1, ts=15, age=10)

    T.PrintBalance()

    price=self.__L[-1][2]['price']
    print("RecalcToBtc: %f" % T.RecalcToCurrency(price, T.GetF(), "dsh_btc"))

    T.SellToEqualizeStartBalance(price, "dsh_btc")
    T.PrintBalance()


  def Test(self):
    self.GetPriceInChainWPriceGen("btc_dsh_eur_btc", False)
    
    return

    for i in range(100):
      self.RecOrder("dsh_btc", 10)
      time.sleep(1)

    return

    #BeginDay="%.0f" % datetime.datetime(2017,3,15).timestamp()
    #EndDay  ="%.0f" % datetime.datetime(2017,3,17).timestamp()
    #R.TransHist(BeginDay, EndDay)

    #TradeHist=A.TradeHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="", tsince=BeginDay, tend=EndDay, tpair='btc_usd')
    #print(TradeHist)

    #R.PublicTrades("dsh_btc")

    self.LoadList()
    #self.RecPublicTrades("dsh_btc", limit=10)
    #self.RecPublicTrades("dsh_eur", limit=10)
    #self.RecPublicTrades("btc_eur", limit=10)
 
    self.BuildPriceDict("dsh_btc")
    self.BuildPriceDict("dsh_eur")
    self.BuildPriceDict("btc_eur")
   
    lenL = len(self.__L) 
    tid=self.__L[int(lenL/2)][2]['tid']
    print("tid %d" % tid)

    v = self.__GetPriceTuple(tid, "dsh_eur")

    print("next dsh_eur: %s" % str(v))

    #print("price in chain: %f" % self.GetPriceInChain(tid, 1.0))

    for v in self.__L:
      print(self.GetPriceInChain(v[2]['tid'], 1.0))

    return

    return
    #self.RecPublicTrades("dsh_btc", 10)
    #self.RecPublicTrades("dsh_eur", 2000)

    #self.PrintPublicTrades()

    #L=self.BuildMinMaxList2(self.GetPriceList("dsh_btc"), 5)
  
     
    C=SimuConf(couple='dsh_btc', WinSize=100, \
               Algos=[])
#
    
    #self.TestFillTrades()
    #return
    
  #  T=MyTrade({ 'btc' : 0.2, 'dsh' : 0.0, 'eth' : 0.0 }) 
    T=MyTrade(C, { 'btc' : 1.0, 'dsh' : 1.0, 'eth' : 1.0 }) 
  
    T.PrintBalance()

#    T.PlaceOrderAsk( 0.08,    0.24, "dsh_btc", ts=10)
#    T.PlaceOrderAsk( 0.06,    0.24, "dsh_btc", ts=11)
#    T.PlaceOrderAsk( 0.09,    0.24, "dsh_btc", ts=12)
#    T.PlaceOrderAsk( 0.07,    0.24, "dsh_btc", ts=13)
#    T.PlaceOrderAsk( 0.04,    0.24, "dsh_btc", ts=14)
#    #T.PlaceOrderAsk( 0.03455, 0.5/0.03455,  "eth_btc", ts=15)
#
    T.PlaceOrderAsk( 0.11,    0.4, "dsh_btc", ts=12, id='testAsk')
    T.PlaceOrderAsk( 0.12,    0.4, "dsh_btc", ts=12, id='testAsk2')

    T.CancelOrders('ask', id='testAsk')
 
    T.PlaceOrderBid( 0.06,    0.3, "dsh_btc", ts=12, id='test1')
 
    T.FillOrders(0.05, ts=15, age=10)

    T.PlaceOrderBid( 0.05, 0.01, "dsh_btc", ts=12, id='test1')
 
    T.FillOrders(0.1, ts=15, age=10)


    T.PrintHistAsk()
    T.PrintHistBid()
  
    T.PrintBalance()

    price=self.__L[-1][2]['price']
    print("RecalcToBtc: %f" % T.RecalcToCurrency(price, T.GetF(), "dsh_btc"))

    T.SellToEqualizeStartBalance(price, "dsh_btc")
    T.PrintBalance()


#    T.PlaceOrderBid( 0.03455, 0.6,  "eth_btc")
#    T.PlaceOrderBid( 0.08, 0.24,  "dsh_btc")
#    T.PrintBalance()

    #T.SellAll(0.03455, "eth_btc")
    #T.SellAll(0.08,    "dsh_btc")

    #self.SimulateTrading(T, "eth_btc")


    #L=self.__GetPlotList(C) 
    #print("List from dsh_eur")
  
    #L=self.GetPriceList("dsh_btc")
    #for v in L:
      #print("Wk[%s] " % MyTime(v[0]).strWeek(), end='')
      #print(str(v))


    #self.SaveList(1)

    #self.TestSaveV1()
      
###########################################################################

def main(argv=None):
    if argv is None:
        argv = sys.argv

    R = MyRich(Keys)

    mode=""
    attrL=[]

    if len(argv) > 1:
      modes = ["functest", "info", "crawler", "v0to1", "remdupl", "simulate", "simplot", "chain" ]
      attrs = ["alt", "noalt"]
      (mode,attrL)=R.ParseCmdLineArgs(argv, modes, attrs)

    if mode == "help":
      exit(0)

    print("=============================================================================")
    print("%s started in mode %s with attrs %s\tTS: %d (%s)" % (argv[0], mode, str(attrL), R.GetStartDate().Timestamp(), R.GetStartDate().Str()))
    print("-----------------------------------------------------------------------------")

    #R.Info()
    if mode == "functest":
      R.FuncTest() 
    elif mode == "crawler":
      R.Crawler()
    elif mode == "v0to1":
      R.ConvertData_v0to1(MyRich.week, MyRich.year)
    elif mode == "info":
      R.InfoMode(MyRich.week, MyRich.year, MyRich.version)
    elif mode == "remdupl":
      R.RemoveDuplicatesMode(MyRich.week, MyRich.year)
    elif mode == "simulate":
      R.SimulateTradingMode(MyRich.weeks, MyRich.year)
    elif mode == "chain":
      R.ChainMode()
    elif mode == "simplot":
      if not R.LoadWeeks(weeks=MyRich.weeks, year=MyRich.year):
        print("exiting")
        exit(0)
      SimPlots=R.SimulateTradingAndPlot(MyRich.couple, attrL)
      R.PrintElapsed("Simulate Plot")
    else:
      R.Test()
    
    print("-----------------------------------------------------------------------------")
    R.PrintElapsed("Overall") 
    print("=============================================================================")
    


if __name__ == "__main__":
    sys.exit(main())

