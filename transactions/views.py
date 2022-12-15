from django.shortcuts import render,HttpResponse
from solana.rpc.api import Client
import blockcypher as bc
import pandas as pd
import requests
import json
from datetime import datetime,date,time

API_KEY="Z3RSFSNICB5H71ZV12HDZYQDDU83B86MDG"
solana_client = Client("https://api.mainnet-beta.solana.com")
address = {
    "btc_bep20":"1Foi5tMVqJfzT9tE4ofMAgUogZDHSemLki",
    "eth_bep20":"0x80AdB45e1cd8B955BB6aBE35aBaAD555f0b5A337",
    "btc_polygon":"0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6",
    "eth_polygon":"0x7ceb23fd6bc0add59e62ac25578270cff1b9f619",
    "TRON_BEP20":"TDeiYuUhxmzMtNiKwYooTBeKRoSCRWju7B",
    "TRON_Polygon":"0x88a7c5e152dcd89a86dd862cc20f641faa088807",
    'sol':"wp5YRzygMxuAEQBYpx7onCJrq8eUHp1oH7Wa29khpkM"
}

def home(request):
    curday=datetime.combine(date.today(), time())
    coin={"btc_bep20":[],"btc_polygon":[],"eth_bep20":[],"eth_polygon":[],"TRON_BEP20":[],"TRON_Polygon":[],'sol':[]}
    for i in coin:
        if i=="eth_bep20":
            url=f"""https://api.bscscan.com/api?module=account&action=tokentx&address={address[i]}&page=1&offset=5&startblock=0&endblock=999999999&sort=asc&apikey=Z3RSFSNICB5H71ZV12HDZYQDDU83B86MDG"""
            data=requests.get(url).content.decode("utf-8")
            data=json.loads(data)
            balance=[float(j['value'])/10**18 for j in data['result'] if curday<=datetime.fromtimestamp(int(j['timeStamp'])) ]
            coin[i]=balance
        if i=='btc_bep20':
            url=f"https://api.blockcypher.com/v1/btc/main/addrs/1PTUHs5ivGAN5aHTY7UQk5RcCE8a67mUT4"
            data=pd.read_json(url)
            # traday=datetime.fromisoformat(x['confirmed']+'+00:00').traday.strftime("%Y-%m-%d %H:%M:%S")
            coin[i]=[bc.from_base_unit(x['value'],'btc') for x in data['txrefs'] if curday<=datetime.strptime(x['confirmed'][:-1],"%Y-%m-%dT%H:%M:%S") ]
        if i=='TRON_BEP20':
            url=f"https://apilist.tronscan.org/api/transfer?sort=timestamp&count=True&limit=20&start=0&token=_&address={address[i]}"
            data=requests.get(url).content.decode("utf-8")
            data=json.loads(data)
            coin[i]=[float(x['amount'])/10**6 for x in data['data'] if curday<=datetime.fromtimestamp(int(x['timestamp'])/1000 ) ]
        if i=='sol':      
            txlist=solana_client.get_signatures_for_address(address[i])
            for tx in txlist['result']:                          
                signature=solana_client.get_transaction(tx['signature'])
                if curday<=datetime.fromtimestamp(int(tx['blockTime'])):
                    amount=signature['result']['meta']['preBalances'][0]-signature['result']['meta']['postBalances'][0]
                    coin[i].append(amount/10**9)

    return render(request,"index.html",context=coin)

"""
https://api.etherscan.io/api
   ?module=transaction
   &action=balance
   &txhash=0x15f8e5ea1079d9a0bb04a4c58ae5fe7654b5b2b4463375ff7ffb490aa0032f3a
   &apikey=YourApiKeyTok
   https://api.bscscan.com/api?module=account&action=balance&address=1Foi5tMVqJfzT9tE4ofMAgUogZDHSemLki&tag=latest&apikey=Z3RSFSNICB5H71ZV12HDZYQDDU83B86MDG
"""
