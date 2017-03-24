#!/usr/bin/python3


#{'success': 1, 'return': {'funds': {'usd': 0, 'btc': 7e-05, 'ltc': 0, 'nmc': 0, 'rur': 0, 'eur': 0, 'nvc': 0, 'trc': 0, 'ppc': 0, 'ftc': 0, 'xpm': 0, 'cnh': 0, 'gbp': 0, 'dsh': 0.23952001, 'eth': 0.5988}, 'rights': {'info': 1, 'trade': 0, 'withdraw': 0}, 'transaction_count': 0, 'open_orders': 0, 'server_time': 1490357983}}
#{'type': 4, 'amount': 0.5988, 'currency': 'ETH', 'desc': 'Buy 0.6 ETH (-0.2%) from your order :order:1653889701: by price 0.03455 BTC', 'status': 2, 'timestamp': 1489664887}


#trades:api/2
#149: {'date': 1490392308, 'price': 964, 'amount': 0.00363446, 'tid': 95990860, 'price_currency': 'USD', 'item': 'BTC', 'trade_type': 'bid'}

#trades:api/3
#1999: {'type': 'ask', 'price': 963.253, 'amount': 0.3754092, 'tid': 95986030, 'timestamp': 1490389511}

import datetime

from btceapi import api
from Keys import Keys


class MyTime:
    __datetime = None

    def __init__(self, timestamp):
        self.__datetime = datetime.datetime.fromtimestamp(timestamp)

    def str(self):
        return self.__datetime.strftime('%Y-%m-%d %H:%M:%S')


class MyRich:
    __A = None

    def __init__(self, Keys):
        self.__A = api(api_key=Keys.Key, api_secret=Keys.Secret)
 
    def Info(self):
        I=self.__A.getInfo()
        print("Info:")
        print(I)
        Ret=I['return']['funds']
        for v in Ret:
            print("%s: %s" % (v, Ret[v]))
        print("------------------------")
        SrvTm = MyTime(I['return']['server_time'])
        print(SrvTm.str())

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
        T=self.__A.get_param3(couple, method='trades', param="limit=3000")

        cnt=0
        for v in T[couple]:
           print ("%4d: " % cnt, end='')
           Time=MyTime(v['timestamp'])
           print(Time.str(), end='')
           print(v)
           cnt+=1

BeginDay="%.0f" % datetime.datetime(2017,3,15).timestamp()
EndDay  ="%.0f" % datetime.datetime(2017,3,17).timestamp()

#print("Begin and End Day: %s - %s" % (BeginDay, EndDay))


R = MyRich(Keys)

R.Info()

R.TransHist(BeginDay, EndDay)

#TradeHist=A.TradeHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="", tsince=BeginDay, tend=EndDay, tpair='btc_usd')
#print(TradeHist)

R.PublicTrades("dsh_btc")

