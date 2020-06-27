import bitmex
import math
import json
import pandas as pd
import time as time
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings("ignore")

print("Please wait ....\nThe bot is booting up...")

with open('mirror.json', 'r') as myfile:
    data=myfile.read()
obj = json.loads(data)


host_client = bitmex.bitmex(
    test = obj['HOST_ACCOUNT']['TEST_EXCHANGE'],
    api_key = (obj['HOST_ACCOUNT']['API_KEY']),
    api_secret = (obj['HOST_ACCOUNT']['SECRET'])
)

sub_client = []

for i in range(len(obj['SUB_ACCOUNTS'])):
    if obj['SUB_ACCOUNTS']['Account '+str(i+1)]['ENABLED'] == True:
        sub_client.append(
            bitmex.bitmex(
                test = obj['SUB_ACCOUNTS']['Account '+str(i+1)]['TEST_EXCHANGE'],
                api_key = obj['SUB_ACCOUNTS']['Account '+str(i+1)]['API_KEY'],
                api_secret = obj['SUB_ACCOUNTS']['Account '+str(i+1)]['SECRET']
            )
        )

ratios = []
for i in range(len(sub_client)):
    if obj['QUANTITY_SETTING']['USE_BALANCE_PROPORTION'] == True:
        r = (sub_client[i].User.User_getMargin().result()[0]['walletBalance']/host_client.User.User_getMargin().result()[0]['walletBalance'])
    else:
        r = 1
    ratios.append(r)
    
PrevOrderIDs = []
Canceled = []
PrevOrders = []
amendPreviousNew = []

while True:
    try:
        orders = host_client.Order.Order_getOrders(reverse = True, count = 50).result()[0]
        break
    except Exception as ex:
        print(ex)
        continue

for i in range(0, len(orders)):
    PrevOrderIDs.append(orders[i]['orderID'])
for i in range(0, len(orders)):
    if orders[i]['ordStatus'] == 'Canceled':
        Canceled.append(orders[i]['orderID'])
for i in range(0, len(orders)):
    PrevOrders.append(orders[i])
    
print("This bot is now running.")
while True:
    New = []
    Filled = []
    PartiallyFilled = []
    OrderIDs = []
    tempCanceled = []
    toCancel = []
    amender = []
    amendNew = []
    
    while True:
        try:
            orders = host_client.Order.Order_getOrders(reverse = True, count = 50).result()[0]
            break
        except Exception as ex:
            print(ex)
            continue
    
    for i in range(0, len(orders)):
        OrderIDs.append(orders[i]['orderID'])
        
        #FOR NEW ORDERS
        if orders[i]['orderID'] not in PrevOrderIDs:
            if orders[i]['ordStatus'] == 'New':
                New.append(orders[i])
            elif orders[i]['ordStatus'] == 'Filled':
                Filled.append(orders[i])
            elif orders[i]['ordStatus'] == 'PartiallyFilled':
                PartiallyFilled.append(orders[i])
                
        #FOR CANCELLED ORDERS
        if orders[i]['ordStatus'] == 'Canceled':
            tempCanceled.append(orders[i]['orderID'])
            if orders[i]['orderID'] not in Canceled:
                toCancel.append(orders[i]['orderID'])
                
        #FOR AMENDED ORDERS
        if orders[i]['ordStatus'] == 'New':
            amendNew.append(orders[i])
        
        
    if New != []:
        for j in range(len(sub_client)):
            post = []
            for i in range(0, len(New)):
                    post.append(
                        {
                            'clOrdID': New[i]['orderID'],
                            'symbol': New[i]['symbol'],
                            'side': New[i]['side'],
                            'simpleOrderQty': New[i]['simpleOrderQty'],
                            'orderQty': int(ratios[j]*New[i]['orderQty']),
                            'price' : New[i]['price'],
                            'displayQty': New[i]['displayQty'],
                            'stopPx': New[i]['stopPx'],
                            'pegOffsetValue': New[i]['pegOffsetValue'],
                            'pegPriceType': New[i]['pegPriceType'],
                            'ordType': New[i]['ordType'],
                            'timeInForce': New[i]['timeInForce'],
                            'execInst': New[i]['execInst'],
                            'contingencyType': New[i]['contingencyType'],
                            'text': "Submitted from Mirror Bot."
            
                        }
                    )
            times = 0
            while True:
                try:
                    response = sub_client[j].Order.Order_newBulk(orders=json.dumps(post)).result()
                    break
                    
                except Exception as ex:
                    times = times+1
                    if times > 10:
                        print("This error is on sub_client " + str(j+1))
                        print(ex)
                        break
                    else:
                        time.sleep(0.8)
                        continue
                
    
    if Filled != []:
        for j in range(len(sub_client)):
            post = []
            for i in range(0, len(Filled)):
                if Filled[i]['ordType'] == 'Market':
                    post.append(
                        {
                            'clOrdID': Filled[i]['orderID'],
                            'symbol': Filled[i]['symbol'],
                            'side': Filled[i]['side'],
                            'simpleOrderQty': Filled[i]['simpleOrderQty'],
                            'orderQty': int(ratios[j]*Filled[i]['orderQty']),
                            'ordType' : 'Market'
                        }
                    )

                else:
                    post.append(
                        {
                            'clOrdID': Filled[i]['orderID'],
                            'symbol': Filled[i]['symbol'],
                            'side': Filled[i]['side'],
                            'simpleOrderQty': Filled[i]['simpleOrderQty'],
                            'orderQty': int(ratios[j]*Filled[i]['orderQty']),
                            'price' : Filled[i]['price'],
                            'displayQty': Filled[i]['displayQty'],
                            'stopPx': Filled[i]['stopPx'],
                            'pegOffsetValue': Filled[i]['pegOffsetValue'],
                            'pegPriceType': Filled[i]['pegPriceType'],
                            'ordType': Filled[i]['ordType'],
                            'timeInForce': Filled[i]['timeInForce'],
                            'execInst': Filled[i]['execInst'],
                            'contingencyType': Filled[i]['contingencyType'],
                            'text': "Submitted from Mirror Bot."

                        }
                    )
            times = 0
            while True:
                try:
                    response = sub_client[j].Order.Order_newBulk(orders=json.dumps(post)).result()
                    break
                    
                except Exception as ex:
                    times = times+1
                    if times > 10:
                        print("This error is on sub_client " + str(j+1))
                        print(ex)
                        break
                    else:
                        time.sleep(0.8)
                        continue
    
    if PartiallyFilled != []:
        for j in range(len(sub_client)):
            post = []
            for i in range(0, len(PartiallyFilled)):
                    post.append(
                        {
                            'clOrdID': PartiallyFilled[i]['orderID'],
                            'symbol': PartiallyFilled[i]['symbol'],
                            'side': PartiallyFilled[i]['side'],
                            'simpleOrderQty': PartiallyFilled[i]['simpleOrderQty'],
                            'orderQty': int(ratios[j]*PartiallyFilled[i]['orderQty']),
                            'price' : PartiallyFilled[i]['price'],
                            'displayQty': PartiallyFilled[i]['displayQty'],
                            'stopPx': PartiallyFilled[i]['stopPx'],
                            'pegOffsetValue': PartiallyFilled[i]['pegOffsetValue'],
                            'pegPriceType': PartiallyFilled[i]['pegPriceType'],
                            'ordType': PartiallyFilled[i]['ordType'],
                            'timeInForce': PartiallyFilled[i]['timeInForce'],
                            'execInst': PartiallyFilled[i]['execInst'],
                            'contingencyType': PartiallyFilled[i]['contingencyType'],
                            'text': "Submitted from Mirror Bot."

                        }
                    )
            times = 0
            while True:
                try:
                    response = sub_client[j].Order.Order_newBulk(orders=json.dumps(post)).result()
                    break
                    
                except Exception as ex:
                    times = times+1
                    if times > 10:
                        print("This error is on sub_client " + str(j+1))
                        print(ex)
                        break
                    else:
                        time.sleep(0.8)
                        continue
        
    if toCancel != []:
        for i in range(0, len(sub_client)):
            times = 0
            while True:
                try:
                    response = sub_client[i].Order.Order_cancel(clOrdID = json.dumps(toCancel)).result()
                    break
                    
                except Exception as ex:
                    times = times+1
                    if times > 10:
                        print("This error is on sub_client " + str(i+1))
                        print(ex)
                        break
                    else:
                        time.sleep(0.8)
                        continue
            
        
        
    NewOrderId = []
    for i in range(len(amendNew)):
        NewOrderId.append(amendNew[i]['orderID'])
    
    PreviousOrderId = []
    for i in range(len(amendPreviousNew)):
        PreviousOrderId.append(amendPreviousNew[i]['orderID'])
    
    for k in range(len(sub_client)):
        amender = []
        for i in range(len(PreviousOrderId)):
            for j in range(len(NewOrderId)):
                if PreviousOrderId[i] == NewOrderId[j]:
                    if (
                        amendPreviousNew[i]['simpleOrderQty'] != amendNew[i]['simpleOrderQty']
                        or amendPreviousNew[i]['orderQty'] != amendNew[i]['orderQty']
                        or amendPreviousNew[i]['simpleLeavesQty'] != amendNew[i]['simpleLeavesQty']
                        or amendPreviousNew[i]['leavesQty'] != amendNew[i]['leavesQty']
                        or amendPreviousNew[i]['price'] != amendNew[i]['price']
                        or amendPreviousNew[i]['stopPx'] != amendNew[i]['stopPx']
                        or amendPreviousNew[i]['pegOffsetValue'] != amendNew[i]['pegOffsetValue']
                        or amendPreviousNew[i]['text'] != amendNew[i]['text']
                    ):
                        amender.append(
                            {
                                'origClOrdID': amendNew[i]['orderID'],
                                'simpleOrderQty': amendNew[i]['simpleOrderQty'],
                                'orderQty': int(ratios[k]*amendNew[i]['orderQty']),
                                'price' : amendNew[i]['price'],
                                'stopPx': amendNew[i]['stopPx'],
                                'pegOffsetValue': amendNew[i]['pegOffsetValue'],
                                'text': "Submitted from Mirror Bot."
        
                            }
                        )
        if amender != []:
            times = 0
            while True:
                try:
                    response = sub_client[k].Order.Order_amendBulk(orders=json.dumps(amender)).result()
                    break
                    
                except Exception as ex:
                    times = times+1
                    if times > 10:
                        print("This error is on sub_client "+str(k+1))
                        print(ex)
                        break
                    else:
                        time.sleep(0.8)
                        continue

    amendPreviousNew = amendNew
    Canceled = tempCanceled
    PrevOrderIDs = OrderIDs
    time.sleep(1)
