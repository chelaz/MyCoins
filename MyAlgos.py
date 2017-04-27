### Trading Algos

import datetime

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

  def StrDayTime(self):
    """ returns string in format by example: 31.-23:59:00 """
    return self.__datetime.strftime('%d./%H:%M:%S')

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



class MyAlgoHelpers:

  # Tuple in MMList: [1490910279, {'min': 0.074, 'max': 0.07415, 'amount': 6.835143370000001}]
  def BuildMinMaxList2(PriceList, winsize, Debug=False):

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
 
  #items in MinMaxL: [ts, min, max]
  def GetMinMaxbyTS(MinMaxL, ts):
    TSL = list(filter(lambda v: v[0] == ts, MinMaxL))
    return TSL[0]

class MyAlgos:
  
  __T = None # MyTrade
   
  __MinMaxL = [] # item: [ts, min, max]
  __TimePerWinSize = []

  # Approach Algo:
  __Appr_Prev = {'mints':None, 'maxts':None} 


  def __init__(self):
    pass

  def SetTrading(self, T):
    self.__T = T

  def GetMinMaxList(self):
    return self.__MinMaxL

  def GetTimePerWinSize(self):
    return self.__TimePerWinSize


  # vc:    current price
  # LastL: last traded values list
  # C:     SimuConf
  def SimuInterBand(self, v, LastL, C):
    T = self.__T
    val = 0.01
    ts = v[0]

    L_LastWZ = LastL[-C.WinSize-1:]

    #print("Len of LastL: old %d new: %d\n" % (len(LastL[-C.WinSize-1:]), len(LastL)))
    MMList = MyAlgoHelpers.BuildMinMaxList2(L_LastWZ, C.WinSize)
#    MMList = self.BuildMinMaxList2(LastL, C.WinSize)
    min=MMList[0][1]['min']
    max=MMList[0][1]['max']
    sum=MMList[0][1]['amount']

    Test=False
    if Test:
      if v[1] > max:
        print("[%d] --------------------------===============> Error: %f > max= %f\n" \
              % (ts, v[1], max))
        __R.BuildMinMaxList2(L_LastWZ, C.WinSize, Debug=True)
        exit(0)

      if v[1] < min:
        print("[%d] --------------------------===============> Error: %f < min= %f\n" \
              % (ts, v[1], min))


    self.__MinMaxL.append([ts, min, max, sum])
    self.__TimePerWinSize.append([ts, ts-L_LastWZ[0][0]])

    maxmin = max-min

    #print("SimuInterBand: [%d] Cur: d%f %f < %f < %f D%f (WS %d)" % (ts,\
    #                       v[1]-min, min, v[1], max, max-v[1], \
    #                       C.WinSize))

    eps = maxmin*C.MinMaxEpsPerc

    if v[1] < min-eps:
#      price = min+maxmin*C.PlaceBidFact
      #price = min-eps
      price = 0.985*min
      #print("----------------------------------->Curval below min: %f < %f=min" % (v[1], min))
      print("Placing at : %f = %f + (%f-%f)*%f" % (price, min, max, min, C.PlaceBidFact))
      #if not C.OnlyAlternating or T.GetTypeOfLastFilled('InterBand') != 'bid':
      T.PlaceOrderAsk(price, # C.PlaceBidFact*v[1], \
                      val, C.couple, id='InterBand', ts=ts)

    if v[1] > max+eps:
#     price = max-maxmin*C.PlaceAskFact
      #price = max+eps
      price = 1.015*max
      #print("----------------------------------->Curval above max: %f > %f=max" % (v[1], max))
      #if not C.OnlyAlternating or T.GetTypeOfLastFilled('InterBand') != 'ask':
      T.PlaceOrderBid(price, #C.PlaceAskFact*v[1], \
                      val, C.couple, id='InterBand', ts=ts)


###########################################

  # vc:    current price
  # LastL: last traded values list
  # C:     SimuConf
  def SimuApproachExtr(self, v, LastL, C):
    Placed=False
    T = self.__T
    val = 0.01
    ts = v[0]
    age = 50
   # age = 3600
    #age = 8000

    LastFilled = T.GetLastFilled() # ('ask'/'bid', ts, price, id)

    # Buy very first:
    if LastFilled == None:
      price = v[1] # *0.99
      T.PlaceOrderAsk(price, val, C.couple, id='first', ts=ts)
      return True
 
    Prv = self.__Appr_Prev 

    L_LastWZ = LastL[-C.WinSize-1:]

    MMList = MyAlgoHelpers.BuildMinMaxList2(L_LastWZ, C.WinSize)
    min=MMList[0][1]['min']
    max=MMList[0][1]['max']
    sum=MMList[0][1]['amount']
    self.__MinMaxL.append([ts, min, max, sum])
    self.__TimePerWinSize.append([ts, ts-L_LastWZ[0][0]])


    if Prv['mints'] == None:
      Prv['mints'] = ts
      Prv['min'] = min
      Prv['minprev'] = min
      Prv['mincnt'] = 1
      return   

    if Prv['maxts'] == None:
      Prv['maxts'] = ts
      Prv['max'] = max
      Prv['maxprev'] = max
      Prv['maxcnt'] = 1
      return
 
    if Prv['min'] == min:
      Prv['mincnt'] += 1
      #if Prv['mincnt'] > age and Prv['minprev'] > min:
      #if ts-Prv['mints'] > age and Prv['mincnt'] > age/3 and Prv['minprev'] > min:
      if ts-Prv['mints'] > age and Prv['minprev'] > min:
        print("[%s] Age %d cnt %d (ask appr)" % (MyTime(ts).StrDayTime(), ts-Prv['mints'], Prv['mincnt']))
        #price = v[1]*1.01
        price = v[1]
        T.PlaceOrderAsk(price, \
                        val, C.couple, id='ApproachExtr', ts=ts)
        Placed=True
        Prv['minprev'] = Prv['min']
        Prv['mincnt']  = 1
        Prv['mints'] = ts
        if C.OnlyAlternating:
          Prv['maxts'] = ts
               
    else:
      Prv['minprev'] = Prv['min']
      Prv['min']     = min
      Prv['mincnt']  = 1
      Prv['mints'] = ts
      if C.OnlyAlternating:
        Prv['maxts'] = ts
 
    Debug=False
    if Debug: 
      print("[%d] %s curmax %f " % (ts, str(Prv), max), end='')
    if Prv['max'] == max:
      if Debug: 
        print("==", end='')
      Prv['maxcnt'] += 1
 #     if Prv['maxcnt'] > age:
      #if ts-Prv['maxts'] > age and Prv['maxcnt'] > age/3 and Prv['maxprev'] < max:
      if ts-Prv['maxts'] > age and Prv['maxprev'] < max:
        print("[%s] Age %d cnt %d (bid appr)" % (MyTime(ts).StrDayTime(), ts-Prv['maxts'], Prv['maxcnt']))
        if Debug:
          print("prev < max", end='')
        #price = v[1]*0.99
        price = v[1]
        T.PlaceOrderBid(price, \
                        val, C.couple, id='ApproachExtr', ts=ts)
        Placed=True
        Prv['maxprev'] = Prv['max']
        Prv['maxcnt']  = 1
        if C.OnlyAlternating:
          Prv['mints'] = ts
        Prv['maxts'] = ts
 
    else:
      if Debug:
        print("prev != max", end='')
      Prv['maxprev'] = Prv['max']
      Prv['max']     = max
      Prv['maxcnt']  = 1
      if C.OnlyAlternating:
        Prv['mints'] = ts
      Prv['maxts'] = ts
    if Debug:
      print("\n")
    return Placed
      
###########################################


  # vc:    current price
  # LastL: last traded values list
  # C:     SimuConf
  def SimuIntraBand(self, v, LastL, C):
    Placed=False
    T = self.__T
    val = 0.01
    ts = v[0]
    p  = v[1]

    #print("SimuIntraBand: Cur: %f (WinSize: %d)" % (v[1], C.WinSize))

    MMList = self.BuildMinMaxList2(LastL, C.WinSize)

    min = MMList[0][1]['min']
    max = MMList[0][1]['max']
    
    if (max-min)*0.9+min < p and p < max:
      print("----------------------------------->Curval top: %f < %f=max" % (p, max))
      if T.GetTypeOfLastFilled('IntraBand') != 'bid':
        T.PlaceOrderBid(p, val, C.couple, id='IntraBand', ts=ts)
        Placed=True

    if (max-min)*0.1+min > p and p > min:
      print("----------------------------------->Curval bottom: %f > %f=min" % (p, min))
      if T.GetTypeOfLastFilled('IntraBand') != 'ask':
        T.PlaceOrderAsk(p, val, C.couple, id='IntraBand', ts=ts)
        Placed=True
    return Placed



  def AStopLoss(self, v, LastL, C):
    Placed=False
    val = 0.01
    ts = v[0]
    p  = v[1]
    T  = self.__T
 
    min = self.__MinMaxL[-1][1]
    max = self.__MinMaxL[-1][2]

    #print("mmlist: %s. min/max: %f/%f" % (str(self.__MinMaxL[-1]), min, max))


    LastFilled = T.GetLastFilled() # ('ask'/'bid', ts, price, id)
    MinMaxOfLastFilled = MyAlgoHelpers.GetMinMaxbyTS(self.__MinMaxL, LastFilled[1])

    # Buy very first:
    if LastFilled == None:
      price = p # *0.99
      T.PlaceOrderAsk(price, val, C.couple, id='StoppLoss', ts=ts)
      return True
  
    #print(str(LastFilled))

    if LastFilled[3] != 'ApproachExtr':
      return False

    if LastFilled[0] == 'ask':
      if p < MinMaxOfLastFilled[1]: # LastFilled[2]:
        price = MinMaxOfLastFilled[1] #min*0.99 #LastFilled[2] *0.99
        print("[%s] (bid sl)" % (MyTime(ts).StrDayTime()))
                 
        T.PlaceOrderBid(price, val, C.couple, id='StopLoss', ts=ts)
        Placed=True
    else:
      #print("lastfilled bid. p %f max %f" % (p, max))
      if p > MinMaxOfLastFilled[2]: # LastFilled[2]:
        price = MinMaxOfLastFilled[2] #max*1.01 #LastFilled[2] *1.01
        print("[%s] (ask sl)" % (MyTime(ts).StrDayTime()))
        res=T.PlaceOrderAsk(price, val, C.couple, id='StopLoss', ts=ts)
        #print("  [%d] (v=%f) placing %f %s" % (ts, p, price, str(res)))
        Placed=True
    return Placed


