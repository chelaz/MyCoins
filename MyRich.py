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

  def __init__(self, timestamp):
    self.__datetime = datetime.datetime.fromtimestamp(timestamp)

  def str(self):
    return self.__datetime.strftime('%Y-%m-%d %H:%M:%S')

  def strDay(self):
    return self.__datetime.strftime('%Y-%m-%d')

  def strWeek(self):
    return self.__datetime.strftime('%Y-%W')


class MyRich:
  __A = None
  __L = []
  __V = 0 # File Version
  __DataPath = ""

  def __init__(self, Keys, DataPath=""):
    self.__A = api(api_key=Keys.Key, api_secret=Keys.Secret, wait_for_nonce=True)
    self.__DataPath=DataPath

  def Info(self):
    I=self.__A.getInfo()
    print("Info:\n  Balance:")
    #print(I)
    Ret=I['return']['funds']
    for v in Ret:
      if Ret[v] > 0:
        print("    %s: %s" % (v, Ret[v]))
    SrvTm = MyTime(I['return']['server_time'])
    print("  Server Time: "+SrvTm.str())
    print("-----------------------------------------")
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

  
  # Tuple: [1490601525, "2017-03-27 09:58:45", "dsh_eur", {"type": "ask", "price": 83.696, "amount": 0.17413282, "tid": 96247757, "timestamp": 1490601525}]
  def _BuildTuple(v, couple):
    return [v['timestamp'], MyTime(v['timestamp']).str(), couple, v]
#    return (v['timestamp'], MyTime(v['timestamp']).str(), couple, v)

  def GetTuple(self, timestamp, couple):
    for v in self.__L:
      if v[2] == couple:
        print("v[0]", end='')
        print(v[0])
        if v[0] == timestamp:
          return v[3]
    return None

<<<<<<< HEAD:my.py
  def RecPublicTrades(self, couple):
    T=self.__A.get_param3(couple, method='trades', param="limit=10")
=======
  def RecPublicTrades(self, couple, limit=2000):
    T=self.__A.get_param3(couple, method='trades', param="limit=%d"%limit)
>>>>>>> 8b54ca931f921872b733a55a8d3f64620f0f4e6d:MyRich.py

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

  def LoadList(self):
    I=self.__A.getInfo()
    #print(I)
    SrvTm = MyTime(I['return']['server_time'])
    FileName="%sTrades-V%02d-%s.dat" % (self.__DataPath, self.__V, SrvTm.strWeek())
    print("Loading data from "+FileName, end='', flush=True) 
    if not os.path.isfile(FileName):
      print(" ..does not exist. Aborted.")
      return

    with open(FileName, "r") as ins:
      for line in ins:
        self.__L.append(json.loads(line))

    print(" ..loaded %d entries" % len(self.__L))
 
  def SaveList(self):
    I=self.__A.getInfo()
    SrvTm = MyTime(I['return']['server_time'])
    FileName="%sTrades-V%02d-%s.dat" % (self.__DataPath, self.__V, SrvTm.strWeek())
    print("Saving data (%d entries) to %s" %(len(self.__L), FileName)) 

    f=open(FileName, "w")
    for v in self.__L:
      f.write(json.dumps(v))
      f.write("\n")
#      f.write(json.dumps(v, indent=2))
    f.close()


  def Crawler(self):
    R.LoadList()

    R.RecPublicTrades("dsh_btc")
    R.RecPublicTrades("dsh_eur")
    R.RecPublicTrades("dsh_usd")
    R.RecPublicTrades("btc_usd")
    R.RecPublicTrades("btc_eur")
    R.RecPublicTrades("eth_btc")
    R.RecPublicTrades("eth_eur")
    R.RecPublicTrades("eth_usd")
    
    R.SaveList()

###########################################################################

  def Test(self):

    #BeginDay="%.0f" % datetime.datetime(2017,3,15).timestamp()
    #EndDay  ="%.0f" % datetime.datetime(2017,3,17).timestamp()
    #R.TransHist(BeginDay, EndDay)

    #TradeHist=A.TradeHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="", tsince=BeginDay, tend=EndDay, tpair='btc_usd')
    #print(TradeHist)

    #R.PublicTrades("dsh_btc")

    R.LoadList()

    R.RecPublicTrades("dsh_btc", 20)
    R.RecPublicTrades("dsh_eur", 20)

<<<<<<< HEAD:my.py
R.RecPublicTrades("dsh_btc")
R.RecPublicTrades("dsh_eur")
#R.RecPublicTrades("dsh_usd")
#R.RecPublicTrades("btc_usd")
#R.RecPublicTrades("btc_eur")
R.RecPublicTrades("eth_btc")
R.RecPublicTrades("eth_eur")
#R.RecPublicTrades("eth_usd")
=======
    R.PrintPublicTrades()
>>>>>>> 8b54ca931f921872b733a55a8d3f64620f0f4e6d:MyRich.py

    R.SaveList()

  
###########################################################################

def main(argv=None):
    if argv is None:
        argv = sys.argv

    StartTime=datetime.datetime.now().timestamp()

    mode=""
    DataPath=""

    if len(argv) > 1:
      for arg in argv:
        if arg == "crawler":
          mode = "crawler"
        if "path" in arg:
          s = arg.split("=")
          DataPath=s[1]+"/"
        if arg == "help":
          print("Usage:")
          print("  %s [crawler] [path=/DATA_PATH] [help]" % argv[0])
          exit(0)
    
    R = MyRich(Keys, DataPath)
    
    R.Info()
    
    if mode == "crawler":
      R.Crawler()
    else:
      R.Test()
    
    
    EndTime=datetime.datetime.now().timestamp()
    
    print("%d seconds" % (EndTime-StartTime))
    print("=============================================================================")
    


if __name__ == "__main__":
    sys.exit(main())

