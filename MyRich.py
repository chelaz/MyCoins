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

import datetime
import json
import os.path
import sys

from btceapi import api
from Keys import Keys
from MyTrade import MyTrade

class MyTime:
  __datetime = None

  # timestamp == 0 means now
  def __init__(self, timestamp=0):
    if timestamp == 0:
      self.__datetime=datetime.datetime.now()
    else:
      self.__datetime=datetime.datetime.fromtimestamp(timestamp)
  
  def Timestamp(self):
    return int(self.__datetime.timestamp())

  def Str(self):
    """ returns string in format by example: 2017-12-31 23:59:00 """
    return self.__datetime.strftime('%Y-%m-%d %H:%M:%S')

  def StrDay(self):
    """ returns string in format by example: 2017-12-31 """
    return self.__datetime.strftime('%Y-%m-%d')

  def StrWeek(self):
    """ returns string in format by example: 2017-51 """
    return self.__datetime.strftime('%Y-%W')

  def Week(self):
    """ returns integer of week number """
    return int(self.__datetime.strftime('%W'))

  def Year(self):
    """ returns integer of year """
    return int(self.__datetime.strftime('%Y'))

  def PrintDiff(self, end='\n'):
    diff=datetime.datetime.now()-self.__datetime
    print(str(diff), end=end)



class MyRich:
  # cmd line args
  week=0 # 0 is this week
  year=0 # 0 is this year 
  version=0

  # data member
  __A = None  # Instance of BTCeAPI
  __L = []    # Trades History
  __F = []    # Funds
  __V = 1     # File Version

  __DataPath = ""
  __StartDate = MyTime()

  # functions
  def __init__(self, Keys):
    self.__A = api(api_key=Keys.Key, api_secret=Keys.Secret, wait_for_nonce=True)

  def SetDataPath(self, DataPath):
    if DataPath[-1] != '/':
      self.__DataPath=DataPath+"/"
    else:
      self.__DataPath=DataPath

  def PrintElapsed(self, Str=""):
    print("_> ", end='')
    self.__StartDate.PrintDiff(end='') 
    print(" elapsed for %s " % Str)

  def GetStartDate(self):
    return self.__StartDate

  def Info(self):
    I=self.__A.getInfo()
    print("Info:\n  Balance:")
    #print(I)
    self.__F=I['return']['funds']
     
    for v in self.__F:
      if self.__F[v] > 0:
        print("    %s: %s" % (v, self.__F[v]))
    SrvTm = MyTime(I['return']['server_time'])
    print("  Server Time: "+SrvTm.Str())
    print("-----------------------------------------")

  def GetBalance(self, currency):
    if currency in self.__F:
      return float(self.__F[currency])
    else:
      return 0.0

  def CleanHist(self):
    self.__L = []

  def TransHist(self, BeginDay, EndDay):
    History=self.__A.TransHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="ASC", tsince=BeginDay, tend=EndDay)
    #print(History)

    if (History and History['success']):
      Ret=History['return']
      for v in Ret:
        TransTime=MyTime((Ret[v]['timestamp']))
        print(TransTime.Str(), end='')
        print(Ret[v])

  def PublicTrades(self, couple):
    T=self.__A.get_param3(couple, method='trades', param="limit=100")

    cnt=0
    for v in T[couple]:
      print ("%4d: " % cnt, end='')
      Time=MyTime(v['timestamp'])
      print(Time.Str(), end='')
      print(v)
      cnt+=1

  def _SortByTimestamp(self, item):
    return item[0]

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


  # obsolete
  def GetListFromCouple(self, couple):
    #D=MyTime()
    L=filter(lambda v : v[2] == couple, self.__L)
    #D.PrintDiff()
    return L

  # (ts, price, amount)
  def GetPriceList(self, couple):
    return list(map(lambda v : (v[0], v[2]['price'], v[2]['amount']), filter(lambda v : v[1] == couple, self.__L)))
#    return list(map(lambda v : (v[0], v[3]['price'], v[3]['amount']), filter(lambda v : v[2] == couple, self.__L)))
    

  # Tuple in MMList: [1490910279, {'min': 0.074, 'max': 0.07415, 'amount': 6.835143370000001}]
  def BuildMinMaxList2(self, PriceList, winsize):

    Debug=False

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
        print("[%2d] ts %f min: %f max: %f sum: %f cnt: %d" % (i+winsize, v[0], min, max, sum, cnt))
 
      MMList.append([v[0], {'min':min, 'max':max, 'amount':sum , 'cnt':cnt }])
  
    return MMList
     
  # Tuple in MMList: [1490910279, {'min': 0.074, 'max': 0.07415, 'amount': 6.835143370000001}]
  def BuildMinMaxList(self, couple, bucket_seconds):

    Debug=False

    L=self.GetPriceList(couple)

    #D=MyTime()

    start_ts=L[0][0]
    
    ts=start_ts
    if Debug:
      print("Starting List from %d" % start_ts)
    
    min=100000000000
    max=0
    sum=0
    cnt=0

    MMList = []

    if Debug:
      print("Dbg minmax:")
    for v in L:
      if Debug:
        print("  "+str(v))
             
      if v[0] > ts + bucket_seconds:
        if Debug:
          print("  -> ts=%d, min=%f, max=%f, amt=%f" %(ts, min, max, sum))
        MMList.append([ts, {'min':min, 'max':max, 'amount':sum , 'cnt':cnt }])
        ts = v[0]
        min=v[1]
        max=v[1]
        sum=v[2]
        cnt=1
      else:
        if Debug:
          print("  ..")
        if min > v[1]:
          min=v[1]
        if max < v[1]:
          max=v[1]
        sum += v[2]
        cnt += 1
    MMList.append([ts, {'min':min, 'max':max, 'amount':sum, 'cnt':cnt }])
 
    if Debug:
      print("MMList:")
      for v in MMList:
        print("  "+str(v))
   
    #D.PrintDiff()
    
    return MMList       


### Simulate Trading functions

  # T is of type MyTrade
  def SimulateTrading(self, T, couple):

    val=0.01

    Debug=True

    if Debug:
      T.PrintBalance()

    L=self.GetPriceList(couple)

    WinSize=50

    bankrupt_counter_sell=0
    bankrupt_counter_buy=0
    cnt_bid=0
    cnt_ask=0

    ts_prev=0
    for i in range(len(L)):
      v  = L[i]
      #v is last traded value
      ts = v[0]

      if i <= WinSize:
        ts_prev = ts
        continue

      print("{%d} overall filled orders Ask=%d Bid=%d. Current orderbook: %d" % (ts, T.LenOrderBookAsk(), T.LenOrderBookBid(), T.LenOrderBook()))

      T.FillOrders(v[1], ts=ts, age=WinSize)
#      T.FillOrders(v[1], ts=ts)

      LastL = L[i-WinSize-1:i]

      MMList = self.BuildMinMaxList2(LastL, WinSize)

      if ts == ts_prev:
        continue

      if v[1] < MMList[0][1]['min']:
        print("----------------------------------->Curval below min: %f < %f min" % (v[1], MMList[0][1]['min']))
        if T.PlaceOrderBid(v[1], val, couple, ts=ts) == 0.0:
          bankrupt_counter_sell += 1
        else:
          cnt_bid+=1

      if v[1] > MMList[0][1]['max']:
        print("----------------------------------->Curval above max: %f > %f min" % (v[1], MMList[0][1]['max']))
        if T.PlaceOrderAsk(v[1], val, couple, ts=ts) == 0.0:
          bankrupt_counter_buy += 1
        else:
          cnt_ask+=1

      #if Debug:
      #  print("MMList for %d" % i)
      #  for v in MMList:
      #    print("  "+str(v))

      ts_prev = ts

    T.SellToEqualizeStartBalance(L[-1][1], couple)
    #T.SellAll(L[-1][1], couple)
    print("\n-------------------------------------\nSimulation Summary:");
    print("  Bankrupt sell: %d buy: %d" % (bankrupt_counter_sell, bankrupt_counter_buy))
    print("  asked %d,  bid %d" % (cnt_ask, cnt_bid))
    T.PrintStartBalance()
    T.PrintBalance()


### Plot functions

  # obsolete
  def __GetPlotList(self, List, UseTime=False):
    if UseTime:
      return map(lambda v : (v[1], v[3]["price"]), List)
    else:
      return map(lambda v : (v[0], v[3]["price"]), List)

  # obsolete
  def __GetPlotListFromCouple(self, couple, UseTime=False):
    return list(self.__GetPlotList(self.GetListFromCouple(couple),UseTime))

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
  
  
  # Tuple in MMList: [1490910279, {'min': 0.074, 'max': 0.07415, 'amount': 6.835143370000001}]
  def GetMMPlot(self, couple, BucSec, Percentage=False):
    L=self.BuildMinMaxList2(self.GetPriceList(couple), BucSec)
    factor=1.0

    if Percentage:
      factor=100.0/((L[0][1]['min']+L[0][1]['max'])/2.0) #first entry is 100 %
       
    MinPlot=(list(map(lambda v:v[0],L)), list(map(lambda v:v[1]['min']*factor,L)))
    MaxPlot=(list(map(lambda v:v[0],L)), list(map(lambda v:v[1]['max']*factor,L)))

    return MinPlot, MaxPlot
 
### Crawler

  def RecPublicTrades(self, couple, limit=2000):
    T=self.__A.get_param3(couple, method='trades', param="limit=%d"%limit)

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


  def LoadList(self, version=None, week=0, year=0):
    if version == None:
      version = self.__V

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
    
    self.__L=sorted(self.__L, key=self._SortByTimestamp)
 
    return True

  def SaveList(self, version=None):
    #I=self.__A.getInfo()
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
                
        FileNameWk1="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, FirstEntry.StrWeek())
        FileNameWk2="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, LastEntry.StrWeek())
         
        L1 = list(filter(lambda v: MyTime(v[0]).Week() == wk1, self.__L))
        LN = list(filter(lambda v: MyTime(v[0]).Week() != wk1, self.__L))
   
        print("Saving data (%d entries) to %s" %(len(L1), FileNameWk1)) 
#        for v in L1:
#          print("Wk[%s] " % MyTime(v[0]).strWeek(), end='')
#          print(str(v))

        L1_FirstEntry=MyTime(L1[0][0])
        L1_LastEntry =MyTime(L1[-1][0])

        f=open(FileNameWk1, "w")
        f.write("#Num entries: %d \t from \t%s (w %d ts %d) \t to \t%s (w %d ts %d)\n" % (len(L1), \
                                                                                 L1_FirstEntry.Str(), L1_FirstEntry.Week(), L1_FirstEntry.Timestamp(),\
                                                                                 L1_LastEntry.Str(),  L1_LastEntry.Week(),  L1_LastEntry.Timestamp()))
        for v in L1:
          f.write(json.dumps(v)+"\n")
        f.close()
      else:
        LN = self.__L
        FileNameWk2="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, LastEntry.StrWeek())

      LN_FirstEntry=MyTime(LN[0][0])
      LN_LastEntry =MyTime(LN[-1][0])

      print("Saving data (%d entries) to %s" %(len(LN), FileNameWk2)) 
#      for v in LN:
#        print("Wk[%s] " % MyTime(v[0]).strWeek(), end='')
#        print(str(v))
      f=open(FileNameWk2, "w")
      f.write("#Num entries: %d \t from \t%s (w %d ts %d) \t to \t%s (w %d ts %d)\n" % (len(LN), \
                                                                                 LN_FirstEntry.Str(), LN_FirstEntry.Week(), LN_FirstEntry.Timestamp(),\
                                                                                 LN_LastEntry.Str(),  LN_LastEntry.Week(),  LN_LastEntry.Timestamp()))
      for v in LN:
        f.write(json.dumps(v)+"\n")
      f.close()


  def Crawler(self):
    self.LoadList()

    self.RecPublicTrades("dsh_btc")
    self.RecPublicTrades("dsh_eur")
    self.RecPublicTrades("dsh_usd")
    self.RecPublicTrades("btc_usd")
    self.RecPublicTrades("btc_eur")
    self.RecPublicTrades("eth_btc")
    self.RecPublicTrades("eth_eur")
    self.RecPublicTrades("eth_usd")
    
    self.SaveList()

  def SimulateTradingAndPlot(self, couple):
    
    #  T=MyTrade({ 'btc' : 0.2, 'dsh' : 0.0, 'eth' : 0.0 }) 
    T=MyTrade({ 'btc' : 1.0, 'dsh' : 1.0, 'eth' : 1.0 }) 
  
    self.SimulateTrading(T, couple)
  
    PLa=T.GetPlotHistAsk()
    Plb=T.GetPlotHistBid()
    return (PLa, Plb)

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
      L=self.BuildMinMaxList2(self.GetPriceList("dsh_btc"), 5)
      print("MMList")
      for v in L:
        print("  "+str(v))

      

  def InfoMode(self, week=0, year=0, version=None):
    if version == None:
      version = self.__V
    self.LoadList(version=version, week=week, year=year)

  def ParseCmdLineArgs(self, argv, modes):
    mode=""
    #week=0 # 0 is this week
    #year=0 # 0 is this year 
    #version=0

    if len(argv) > 1:
      for arg in argv:

        if arg in modes:
          mode = arg

        if "version" in arg:
          s = arg.split("=")
          MyRich.version=int(s[1])

        if "week" in arg:
          s = arg.split("=")
          MyRich.week=int(s[1])

        if "year" in arg:
          s = arg.split("=")
          MyRich.year=int(s[1])

        if "path" in arg:
          s = arg.split("=")
          self.SetDataPath(s[1])

        if arg == "help":
          ModeStr=""
          for m in modes:
            ModeStr = ModeStr+" ["+m+"]"
           
          print("Usage:")
          print("  %s [help] [path=/DATA_PATH]%s [version=0] [year=0] [week=0]" % (argv[0], ModeStr))
          mode="help"

    return mode
 
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

  def Test(self):

    #BeginDay="%.0f" % datetime.datetime(2017,3,15).timestamp()
    #EndDay  ="%.0f" % datetime.datetime(2017,3,17).timestamp()
    #R.TransHist(BeginDay, EndDay)

    #TradeHist=A.TradeHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="", tsince=BeginDay, tend=EndDay, tpair='btc_usd')
    #print(TradeHist)

    #R.PublicTrades("dsh_btc")

    #self.LoadList(week=14)

    #self.RecPublicTrades("dsh_btc", 10)
    #self.RecPublicTrades("dsh_eur", 2000)

    #self.PrintPublicTrades()

    #C=self.GetListFromCouple("dsh_eur")
    
    #L=self.BuildMinMaxList2(self.GetPriceList("dsh_btc"), 5)
    
    self.TestFillTrades()
    return
    
  #  T=MyTrade({ 'btc' : 0.2, 'dsh' : 0.0, 'eth' : 0.0 }) 
    T=MyTrade({ 'btc' : 1.0, 'dsh' : 1.0, 'eth' : 1.0 }) 
  
    T.PrintBalance()

    T.PlaceOrderAsk( 0.08,    0.24, "dsh_btc", ts=10)
    T.PlaceOrderAsk( 0.06,    0.24, "dsh_btc", ts=11)
    T.PlaceOrderAsk( 0.09,    0.24, "dsh_btc", ts=12)
    T.PlaceOrderAsk( 0.07,    0.24, "dsh_btc", ts=13)
    T.PlaceOrderAsk( 0.04,    0.24, "dsh_btc", ts=14)
    #T.PlaceOrderAsk( 0.03455, 0.5/0.03455,  "eth_btc", ts=15)

    T.PlaceOrderAsk( 0.09,    0.4, "dsh_btc", ts=12)
 
    #T.PlaceOrderBid( 0.06,    0.3, "dsh_btc", ts=12)
 
    T.FillOrders(0.07, ts=15, age=1)

    T.PrintHistAsk()
    T.PrintHistBid()
  
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
#    DataPath=""
#    week=0 # 0 is this week
#    year=0 # 0 is this year 
#    version=0

    if len(argv) > 1:
      modes = ["functest", "info", "crawler", "v0to1"]
      mode=R.ParseCmdLineArgs(argv, modes)

    if mode == "help":
      exit(0)

#      for arg in argv:
#        if arg == "functest":
#          mode = "functest"
#          DataPath="FuncTests/"
#        if arg == "info":
#          mode = "info"
#        if arg == "crawler":
#          mode = "crawler"
#        if arg == "v0to1":
#          mode = "v0to1"
#        if "version" in arg:
#          s = arg.split("=")
#          version=int(s[1])
#        if "week" in arg:
#          s = arg.split("=")
#          week=int(s[1])
#        if "year" in arg:
#          s = arg.split("=")
#          year=int(s[1])
#        if "path" in arg:
#          s = arg.split("=")
#          DataPath=s[1]+"/"
#        if arg == "help":
#          print("Usage:")
#          print("  %s [help] [path=/DATA_PATH] [info] [functest] [crawler] [v0to1] [version=0] [year=0] [week=0]" % argv[0])
#          exit(0)
   
    
    print("=============================================================================")
    print("%s started in mode %s\tTS: %d (%s)" % (argv[0], mode, R.GetStartDate().Timestamp(), R.GetStartDate().Str()))
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
    else:
      R.Test()
    
    print("-----------------------------------------------------------------------------")
    R.PrintElapsed("Overall") 
    print("=============================================================================")
    


if __name__ == "__main__":
    sys.exit(main())

