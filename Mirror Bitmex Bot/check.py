print("Please wait ....\nThe script is running...")
import bitmex
import math
import json
import pandas as pd
import time as time
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings("ignore")

with open('mirror.json', 'r') as myfile:
    data=myfile.read()
obj = json.loads(data)


host_client = bitmex.bitmex(
    test = obj['HOST_ACCOUNT']['TEST_EXCHANGE'],
    api_key = (obj['HOST_ACCOUNT']['API_KEY']),
    api_secret = (obj['HOST_ACCOUNT']['SECRET'])
)

sub_client = []
name = []

for i in range(len(obj['SUB_ACCOUNTS'])):
    if obj['SUB_ACCOUNTS']['Account '+str(i+1)]['ENABLED'] == True:
        sub_client.append(
            bitmex.bitmex(
                test = obj['SUB_ACCOUNTS']['Account '+str(i+1)]['TEST_EXCHANGE'],
                api_key = obj['SUB_ACCOUNTS']['Account '+str(i+1)]['API_KEY'],
                api_secret = obj['SUB_ACCOUNTS']['Account '+str(i+1)]['SECRET']
            )
        )
        name.append(i+1)
        
def status(client):
    New = []
    orders = client.Order.Order_getOrders(reverse = True, count = 100).result()[0]
    for i in range(len(orders)):
        if orders[i]['ordStatus'] == 'New':
            New.append(orders[i])

    print("-------------------------------------------------------")
    print("\n\nOpen Orders:")
    for i in range(len(New)):
        print("\n\nOrder Id: "+New[i]['orderID']+
              "\nSymbol: "+New[i]['symbol']+
              "\nSide: "+New[i]['side']+
              "\nOrder Quantity: "+str(New[i]['orderQty']) +
              "\nPrice: "+str(New[i]['price']) +
              "\nStop Price: "+str(New[i]['stopPx']) +
              "\nOrder Status: "+str(New[i]['ordStatus']) )

    p = []
    positions = client.Position.Position_get().result()[0]
    for i in range(len(positions)):
        if positions[i]['currentQty'] != 0:
            p.append(positions[i])

    print("-------------------------------------------------------")
    print("\n\nOpen Positions:")
    for i in range(len(p)):
        print("\n\nSymbol: "+p[i]['symbol']+
              "\nCurrent Quantity: "+str(p[i]['currentQty'])+
              "\nAverage Cost Price: "+str(p[i]['avgCostPrice'])+
              "\nLiqidation Price: "+str(p[i]['liquidationPrice'])+
              "\nUnrealised Pnl: "+str(p[i]['unrealisedPnl'])
             )
        
print("\n\n################################ Host Account ################################")
status(host_client)

for i in range(len(sub_client)):
    print("\n\n################################ Account "+str(name[i])+" ################################")
    status(sub_client[i])

time.sleep(60*60)
