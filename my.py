#!/usr/bin/python3


#{'success': 1, 'return': {'funds': {'usd': 0, 'btc': 7e-05, 'ltc': 0, 'nmc': 0, 'rur': 0, 'eur': 0, 'nvc': 0, 'trc': 0, 'ppc': 0, 'ftc': 0, 'xpm': 0, 'cnh': 0, 'gbp': 0, 'dsh': 0.23952001, 'eth': 0.5988}, 'rights': {'info': 1, 'trade': 0, 'withdraw': 0}, 'transaction_count': 0, 'open_orders': 0, 'server_time': 1490357983}}
#{'type': 4, 'amount': 0.5988, 'currency': 'ETH', 'desc': 'Buy 0.6 ETH (-0.2%) from your order :order:1653889701: by price 0.03455 BTC', 'status': 2, 'timestamp': 1489664887}

import datetime

from btceapi import api
from Keys import Keys


class MyTime:
    __datetime = None

    def __init__(self, timestamp):
        self.__datetime = datetime.datetime.fromtimestamp(timestamp)

    def str(self):
        return self.__datetime.strftime('%Y-%m-%d %H:%M:%S')


A=api(api_key=Keys.Key, api_secret=Keys.Secret)

Info=A.getInfo()

print("Info:")
print(Info)
print("------------------------")

SrvTm = MyTime(Info['return']['server_time'])
print(SrvTm.str())

BeginDay="%.0f" % datetime.datetime(2017,3,15).timestamp()
EndDay  ="%.0f" % datetime.datetime(2017,3,17).timestamp()

print("Begin and End Day: %s - %s" % (BeginDay, EndDay))

History=A.TransHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="ASC", tsince=BeginDay, tend=EndDay)

#print(History)

if (History['success']):
    Ret=History['return']
    for v in Ret:
        TransTime=MyTime((Ret[v]['timestamp']))
        print(TransTime.str(), end='')
        print(Ret[v])


