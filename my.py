#!/usr/bin/python3

from btceapi import api
from Keys import Keys

A=api(api_key=Keys.Key, api_secret=Keys.Secret)

Info=A.getInfo()

print("Info:")
print(Info)
print("------------------------")
#{'success': 1, 'return': {'funds': {'usd': 0, 'btc': 7e-05, 'ltc': 0, 'nmc': 0, 'rur': 0, 'eur': 0, 'nvc': 0, 'trc': 0, 'ppc': 0, 'ftc': 0, 'xpm': 0, 'cnh': 0, 'gbp': 0, 'dsh': 0.23952001, 'eth': 0.5988}, 'rights': {'info': 1, 'trade': 0, 'withdraw': 0}, 'transaction_count': 0, 'open_orders': 0, 'server_time': 1490357983}}

servertime=Info['return']['server_time']

#History=A.TradeHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="ASC", tsince=servertime-1000000, tend=servertime, tpair="eth_btc")
History=A.TransHistory(tfrom="", tcount="", tfrom_id="", tend_id="", torder="ASC", tsince=servertime-1000000, tend=servertime)

if (History['success']):
    Ret=History['return']
    for v in Ret:
        print(Ret[v])


