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


class MyTime:
  __datetime = None

  def __init__(self, timestamp=0):
    if timestamp == 0:
      self.__datetime=datetime.datetime.now()
    else:
      self.__datetime=datetime.datetime.fromtimestamp(timestamp)

  def str(self):
    return self.__datetime.strftime('%Y-%m-%d %H:%M:%S')

  def strDay(self):
    return self.__datetime.strftime('%Y-%m-%d')

  def strWeek(self):
    return self.__datetime.strftime('%Y-%W')

  def Week(self):
    return int(self.__datetime.strftime('%W'))

  def Year(self):
    return int(self.__datetime.strftime('%Y'))


  def PrintDiff(self, end='\n'):
    #diff=datetime.datetime.now().timestamp()-self.__datetime.timestamp()
    diff=datetime.datetime.now()-self.__datetime
#    print("... time diff "+str(diff))
    print(str(diff), end=end)



class MyRich:

  __A = None  # Instance of BTCeAPI
  __L = []    # Trades History
  __F = []    # Funds
  __V = 1     # File Version

  __StartDate = MyTime()
  __DataPath = ""

  def __init__(self, Keys, DataPath=""):
    self.__A = api(api_key=Keys.Key, api_secret=Keys.Secret, wait_for_nonce=True)
    self.__DataPath=DataPath

  def PrintEllapsed(self, Str=""):
    print("_> ", end='')
    self.__StartDate.PrintDiff(end='') 
    print(" elapsed for %s " % Str)

  def Info(self):
    I=self.__A.getInfo()
    print("Info:\n  Balance:")
    #print(I)
    self.__F=I['return']['funds']
     
    for v in self.__F:
      if self.__F[v] > 0:
        print("    %s: %s" % (v, self.__F[v]))
    SrvTm = MyTime(I['return']['server_time'])
    print("  Server Time: "+SrvTm.str())
    print("-----------------------------------------")

  def GetBalance(self, currency):
    if currency in self.__F:
      return float(self.__F[currency])
    else:
      return 0.0

  def TransHist(self, BeginDay, EndDay):
    History=self.__A.TransHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="ASC", tsince=BeginDay, tend=EndDay)
    #print(History)

    if (History and History['success']):
      Ret=History['return']
      for v in Ret:
        TransTime=MyTime((Ret[v]['timestamp']))
        print(TransTime.str(), end='')
        print(Ret[v])

  def PublicTrades(self, couple):
    T=self.__A.get_param3(couple, method='trades', param="limit=100")

    cnt=0
    for v in T[couple]:
      print ("%4d: " % cnt, end='')
      Time=MyTime(v['timestamp'])
      print(Time.str(), end='')
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


#  def GetTuple(self, timestamp, couple):
#    for v in self.__L:
#      if v[2] == couple:
#        print("v[0]", end='')
#        print(v[0])
#        if v[0] == timestamp:
#          return v[3]
#    return None


  # obsolete
  def GetListFromCouple(self, couple):
    #D=MyTime()
    L=filter(lambda v : v[2] == couple, self.__L)
    #D.PrintDiff()
    return L

  def GetPriceList(self, couple):
    return list(map(lambda v : (v[0], v[2]['price'], v[2]['amount']), filter(lambda v : v[1] == couple, self.__L)))
#    return list(map(lambda v : (v[0], v[3]['price'], v[3]['amount']), filter(lambda v : v[2] == couple, self.__L)))


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
    L=self.BuildMinMaxList(couple, BucSec)
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
    #I=self.__A.getInfo()
    #print(I)
    #SrvTm = MyTime(I['return']['server_time'])
    #SrvTm= MyTime(1490112676) # wk 12
    #SrvTm= MyTime(1490815277)  # wk 13

    if version == None:
      version = self.__V

    if week == 0:
      week = self.__StartDate.Week()
    if year == 0:
      year = self.__StartDate.Year()

    print("Ver: %d" % version)
    FileName="%sTrades-V%02d-%4d-%02d.dat" % (self.__DataPath, version, year, week)
    print("Loading data from "+FileName, end='', flush=True) 
    if not os.path.isfile(FileName):
      print(" ..does not exist. Aborted.")
      return False

    with open(FileName, "r") as ins:
      for line in ins:
        v=json.loads(line)
        if (len(v) == 4): # V0
          self.__L.append(MyRich._BuildTuple(v[3], v[2]))
        if (len(v) == 3): # V1
          #print(str(v))
          self.__L.append(MyRich._BuildTuple(v[2], v[1], timestamp=v[0]))

    FirstEntry=MyTime(self.__L[0][0])
    LastEntry =MyTime(self.__L[-1][0])
    print(" ..loaded %d entries from %s (w %d) to %s (w %d)" % (len(self.__L), FirstEntry.str(), FirstEntry.Week(), LastEntry.str(), LastEntry.Week()))
    return True

  def SaveList(self, version=None):
    #I=self.__A.getInfo()
    #SrvTm = MyTime(I['return']['server_time'])
  
    if version == None:
      version = self.__V

    if version == 0: 
      FileName="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, self.__StartDate.strWeek())
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
        
        FileNameWk1="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, FirstEntry.strWeek())
        FileNameWk2="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, LastEntry.strWeek())
         
        L1 = list(filter(lambda v: MyTime(v[0]).Week() == wk1, self.__L))
        LN = list(filter(lambda v: MyTime(v[0]).Week() != wk1, self.__L))
   
        print("Saving data (%d entries) to %s" %(len(L1), FileNameWk1)) 
#        for v in L1:
#          print("Wk[%s] " % MyTime(v[0]).strWeek(), end='')
#          print(str(v))
        f=open(FileNameWk1, "w")
        for v in L1:
          f.write(json.dumps(v)+"\n")
        f.close()
      else:
        LN = self.__L
        FileNameWk2="%sTrades-V%02d-%s.dat" % (self.__DataPath, version, self.__StartDate.strWeek())

      print("Saving data (%d entries) to %s" %(len(LN), FileNameWk2)) 
#      for v in LN:
#        print("Wk[%s] " % MyTime(v[0]).strWeek(), end='')
#        print(str(v))
      f=open(FileNameWk2, "w")
      for v in LN:
        f.write(json.dumps(v)+"\n")
      f.close()


  def Crawler(self):
    self.LoadList()

    self.PublicTrades("dsh_btc")
    self.PublicTrades("dsh_eur")
    self.RecPublicTrades("dsh_usd")
    self.RecPublicTrades("btc_usd")
    self.RecPublicTrades("btc_eur")
    self.RecPublicTrades("eth_btc")
    self.RecPublicTrades("eth_eur")
    self.RecPublicTrades("eth_usd")
    
    self.SaveList()

  def ConvertData_v0to1(self, week=0, year=0):
    if self.LoadList(version=0, week=week, year=year):
      self.SaveList(version=1)

  def FuncTest(self):
    # load V0 with different weeks -> save to different files
    if self.LoadList(version=0, week=13, year=2017):
      self.SaveList(version=1)


###########################################################################

  def TestSaveV1(self):
    self.LoadList()
    #self.RecPublicTrades("dsh_btc", 10)
 
    for v in self.__L:
      print("Wk[%s] " % MyTime(v[0]).strWeek(), end='')
      print(str(v))

    self.SaveList(1)



  def Test(self):

    #BeginDay="%.0f" % datetime.datetime(2017,3,15).timestamp()
    #EndDay  ="%.0f" % datetime.datetime(2017,3,17).timestamp()
    #R.TransHist(BeginDay, EndDay)

    #TradeHist=A.TradeHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="", tsince=BeginDay, tend=EndDay, tpair='btc_usd')
    #print(TradeHist)

    #R.PublicTrades("dsh_btc")

    self.LoadList(version=0, week=13)

    #self.RecPublicTrades("dsh_btc", 10)
    #self.RecPublicTrades("dsh_eur", 2000)

    #self.PrintPublicTrades()

    #C=self.GetListFromCouple("dsh_eur")
    
    #L=self.BuildMinMaxList("dsh_usd", 100)
    
    #L=self.__GetPlotList(C) 
    #print("List from dsh_eur")
  
    L=self.GetPriceList("dsh_btc")
    #for v in L:
      #print("Wk[%s] " % MyTime(v[0]).strWeek(), end='')
      #print(str(v))


    #self.SaveList(1)

    #self.TestSaveV1()
      
###########################################################################

def main(argv=None):
    if argv is None:
        argv = sys.argv

    D=MyTime()

    StartTime=datetime.datetime.now().timestamp()

    mode=""
    DataPath=""
    week=0 # 0 is this week
    year=0 # 0 is this year 

    if len(argv) > 1:
      for arg in argv:
        if arg == "functest":
          mode = "functest"
          DataPath="FuncTests/"
        if arg == "crawler":
          mode = "crawler"
        if arg == "v0to1":
          mode = "v0to1"
        if "week" in arg:
          s = arg.split("=")
          week=int(s[1])
        if "year" in arg:
          s = arg.split("=")
          year=int(s[1])
        if "path" in arg:
          s = arg.split("=")
          DataPath=s[1]+"/"
        if arg == "help":
          print("Usage:")
          print("  %s [help] [path=/DATA_PATH] [functest] [crawler] [v0to1] [year=0] [week=0]" % argv[0])
          exit(0)
   
    R = MyRich(Keys, DataPath)
    
    #R.Info()
    if mode == "functest":
      R.FuncTest() 
    elif mode == "crawler":
      R.Crawler()
    elif mode == "v0to1":
      R.ConvertData_v0to1(week, year)
    else:
      R.Test()
    
    
    #EndTime=datetime.datetime.now().timestamp()
    
    #print("%d seconds" % (EndTime-StartTime))
    #print("Overall: ", end='')
    #D.PrintDiff()
    print("-----------------------------------------------------------------------------")
    R.PrintEllapsed("Overall") 
    print("=============================================================================")
    


if __name__ == "__main__":
    sys.exit(main())

