#!/usr/bin/env python
# coding: utf-8

# In[110]:


import pandas as pd
import krython as kr 
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import math
import collections, functools, operator
import scipy.stats

#Read the data into dataframes
eurusd_prices = pd.read_csv('./eurusd-prices.csv')
eurusd_trades = pd.read_csv('./eurusd-trades.csv')
usdchf_prices = pd.read_csv('./usdchf-prices.csv')
EURUSD_PIP_Val = .0001


# In[111]:


# Task 1, part 1 : No hedging as it is in eurusd-trades


pnl_eurusd = []; position_eurusd = []; pnl_trade_counterparty = {}; pnl_trade = []
eff_quote_time = []; runningPnL = 0.00; runningPosition = 0; runningOfferPosition = 0; runningBidPosition = 0
vwapBid_num = 0.00; vwapOffer_num = 0.00; bidPrice = 0.00; offerPrice = 0.00; vwapBid = 0.00; vwapOffer = 0.00


for tradeCount in range(len(eurusd_trades)):
    #print (eurusd_trades.iloc[tradeCount]['time'])
    #Find the latest Bid/Offer quote prior to the trade
    realizedPnL = 0.00; unrealizedPnL = 0.00
    allQuotesUptoTrade = eurusd_prices.loc[eurusd_prices['time'] <= eurusd_trades.iloc[tradeCount]['time']]  
    quoteTime = max(allQuotesUptoTrade['time'])
    #To keep a track for efficiency (to be used for hedging later)
    quoteCount = len(allQuotesUptoTrade)
    eff_quote_time.append(quoteTime)
    tradeQuantity = eurusd_trades.iloc[tradeCount]['tradeQuantity']
    bidPrice = eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['bidPrice']
    offerPrice = eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['offerPrice']
    counterpartyID = eurusd_trades.iloc[tradeCount]['counterPartyId']
    # ASSUMPTION: In the data file , Side (Bid/Offer) is from Counterparty perspective, hence its the reverse for UBS PnL
    if eurusd_trades.iloc[tradeCount]['side'] == 'BID':
        #print ("BID:: %s %s" % (eurusd_trades.iloc[tradeCount]['tradeQuantity'],eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['bidPrice']))
        #bidPrice = eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['bidPrice']
        runningOfferPosition = int(runningOfferPosition) + tradeQuantity
        
        if runningPosition > 0:
            realizedPnL = (bidPrice - vwapBid)*tradeQuantity*EURUSD_PIP_Val
        else:
            realizedPnL = 0.0
        
        vwapOffer_num = float(vwapOffer_num) + bidPrice*tradeQuantity
        vwapOffer = round(float(vwapOffer_num/runningOfferPosition),5)
        
        runningPosition = int(runningPosition) - tradeQuantity
        #UnrealizedPnL on Net Quantity
         
        
        #runningPnL = float(runningPnL) +  tradeQuantity*bidPrice
    else:
        #offerPrice = eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['offerPrice']
        
        runningBidPosition = int(runningBidPosition) + tradeQuantity
        # Vwap = Sum(Quantity X Price)/Sum(Quantity): vwapBid_num keeps track of the numerator
        if runningPosition < 0:
            realizedPnL = (offerPrice - vwapOffer)*tradeQuantity*EURUSD_PIP_Val
        else:
            realizedPnL = 0.0    
        
        vwapBid_num = float(vwapBid_num) + offerPrice*tradeQuantity
        vwapBid = round(float(vwapBid_num/runningBidPosition),5)
        
        #runningPnL = float(runningPnL) +  (-1*tradeQuantity*offerPrice)
        runningPosition = int(runningPosition) + tradeQuantity
    # Keep track of Net Position
    
    
    #Calculate Unrealized PnL
    if runningPosition > 0:
        unrealizedPnL = (bidPrice - vwapBid)*runningPosition*EURUSD_PIP_Val
    else:
        unrealizedPnL = (offerPrice - vwapOffer)*runningPosition*EURUSD_PIP_Val
        

    runningPnL = round(float(runningPnL + realizedPnL + unrealizedPnL ),2)
    position_eurusd.append(runningPosition)
    pnl_eurusd.append(runningPnL)
    #print("TradeCount, Running VWAP Bid, Offer, BidQuantity, OfferQuantity, Net Quantity: %s,%s,%s,%s,%s,%s" % (tradeCount,vwapBid,vwapOffer,runningBidPosition,runningOfferPosition,runningPosition))
    print("RealizedPnl, UnrealizedPnL, totalPnL: %s,%s,%s" % (realizedPnL,unrealizedPnL,runningPnL))
    
    # Needed for Task 3 , part 1
    pnl_trade.append({counterpartyID: realizedPnL})
    
#     if counterpartyID in pnl_trade_counterparty:
#         pnl_cpty = pnl_trade_counterparty.get(counterpartyID)
#         pnl_trade_counterparty.update(counterpartyID: float(pnl_cpty) + realizedPnL )
#     else:
#         pnl_trade_counterparty.update(counterpartyID:realizedPnL )
        
    
print ("Final Position & pnL: %s , %s"%(runningPosition,runningPnL))
#print ("Total Realized Pnl %s ": sum(pnl_trade_counterparty.values()))
# Now sum up the Trade PnL for each client : Task 3 Part 1
#pnl_client = dict(functools.reduce(operator.add, map(collections.Counter, pnl_trade))) 
result = {}
for d in pnl_trade: 
    for k in d.keys(): 
        result[k] = float(result.get(k, 0)) + float(d[k] )

print("PnL per client  : ", str(result)) 

#Adding 2 new columns in the trades dataframe to store the corresponding running Long/Short Position & PnL(in millions)
eurusd_trades['position'] = [p/100000 for p in position_eurusd]
eurusd_trades['pnl'] = [k/1000000 for k in pnl_eurusd]
# Plotting the whole series takes a bit of time, plotting PnL for first N trades instead
#plt.plot(eurusd_trades['time'].head(2000),eurusd_trades['pnl'].head(2000) , color = 'r')
#plt.plot(eurusd_trades['time'].head(2000),eurusd_trades['position'].head(2000) , color = 'b')
#plt.show()


# In[113]:


# Task1 Part 2
# Proposed Hedging model

STOP_LOSS = 0.0005 # 5 pips
EURUSD_PIP_Val = .0001
pnl_eurusd = []; position_eurusd = []; price_eurusd = []
eff_quote_time = []; runningPnL = 0.00; runningPosition = 0; runningOfferPosition = 0; runningBidPosition = 0
vwapBid_num = 0.00; vwapOffer_num = 0.00; bidPrice = 0.00; offerPrice = 0.00; vwapBid = 0.00; vwapOffer = 0.00
def checkPnL_Hedge(quoteTime, runningPosition,vwapBid,vwapOffer,stopLossInPips):
    #Find the next Bid/Offer immediately after the last trade, keep track of moving Bid/Offer quotes until the next trade
    #Close Position if price breaches Stop Loss
    #Hedging Strategy 1 (Market Order): Depending on the net Long/Short position,if Bid/Offer price moves over a certain threshold(in pips) compared to the net VWAP,Close position
    #Hedging Strategy 2 (Limit Order): For each Client trade, place an appr Stop-Loss
    #vwap = abs(round(float(runningPnL/runningPosition),5))
    realizedHedgePnL = 0.00
    
    nextBidPrice = float(eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['bidPrice'])
    nextOfferPrice = float(eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['offerPrice'])
    if (runningPosition > 0 & (nextBidPrice < vwapBid - stopLossInPips)):
        #Close Position
        realizedHedgePnL = runningPosition*(vwapBid - nextBidPrice)*EURUSD_PIP_Val
        print ("Position Closed by Hedging for Quantity: %s at VWAP:%s and BidPrice: %s , RealizedPnL: %s " % (runningPosition,vwapBid,nextBidPrice,realizedPnL))
        runningPosition = 0
    else:
        if (runningPosition < 0 & (nextOfferPrice > vwapOffer + stopLossInPips)):
            realizedHedgePnL = runningPosition*(vwapOffer - nextOfferPrice)*EURUSD_PIP_Val
            print ("Position Closed by Hedging for Quantity: %s at VWAP: %s and OfferPrice: %s, RealizedPnL: %s" % (runningPosition,vwapOffer,nextOfferPrice,realizedPnL))
            runningPosition = 0
    return (realizedHedgePnL,runningPosition)

for tradeCount in range(len(eurusd_trades)):
    #print (eurusd_trades.iloc[tradeCount]['time'])
    #Find the latest Bid/Offer quote prior to the trade
    realizedPnL = 0.00; unrealizedPnL = 0.00; realizedHedgePnL = 0.00
    allQuotesUptoTrade = eurusd_prices.loc[eurusd_prices['time'] <= eurusd_trades.iloc[tradeCount]['time']]  
    quoteTime = max(allQuotesUptoTrade['time'])
    #To keep a track for efficiency (to be used for hedging later)
    quoteCount = len(allQuotesUptoTrade)
    eff_quote_time.append(quoteTime)
    tradeQuantity = eurusd_trades.iloc[tradeCount]['tradeQuantity']
    bidPrice = eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['bidPrice']
    offerPrice = eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['offerPrice']
    # ASSUMPTION: In the data file , Side (Bid/Offer) is from Counterparty perspective, hence its the reverse for UBS PnL
    if eurusd_trades.iloc[tradeCount]['side'] == 'BID':
        #print ("BID:: %s %s" % (eurusd_trades.iloc[tradeCount]['tradeQuantity'],eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['bidPrice']))
        #bidPrice = eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['bidPrice']
        runningOfferPosition = int(runningOfferPosition) + tradeQuantity
        
        if runningPosition > 0:
            realizedPnL = (bidPrice - vwapBid)*tradeQuantity*EURUSD_PIP_Val
        
        vwapOffer_num = float(vwapOffer_num) + bidPrice*tradeQuantity
        vwapOffer = round(float(vwapOffer_num/runningOfferPosition),5)
        
        runningPosition = int(runningPosition) - tradeQuantity
        price_eurusd.append(bidPrice)
        #UnrealizedPnL on Net Quantity
         
        
        #runningPnL = float(runningPnL) +  tradeQuantity*bidPrice
    else:
        #offerPrice = eurusd_prices.loc[eurusd_prices['time'] == quoteTime]['offerPrice']
        
        runningBidPosition = int(runningBidPosition) + tradeQuantity
        # Vwap = Sum(Quantity X Price)/Sum(Quantity): vwapBid_num keeps track of the numerator
        if runningPosition < 0:
            realizedPnL = (offerPrice - vwapOffer)*tradeQuantity*EURUSD_PIP_Val
        
        vwapBid_num = float(vwapBid_num) + offerPrice*tradeQuantity
        vwapBid = round(float(vwapBid_num/runningBidPosition),5)
        
        #runningPnL = float(runningPnL) +  (-1*tradeQuantity*offerPrice)
        runningPosition = int(runningPosition) + tradeQuantity
        price_eurusd.append(offerPrice)
    # Keep track of Net Position
    
    
    #Calculate Unrealized PnL
    if runningPosition > 0:
        unrealizedPnL = (bidPrice - vwapBid)*runningPosition*EURUSD_PIP_Val
    else:
        unrealizedPnL = (offerPrice - vwapOffer)*runningPosition*EURUSD_PIP_Val
        
    #Perform hedging until next trade
    for runningquoteCount in range(quoteCount,len(eurusd_prices)):
        nextQuoteTime = eurusd_prices.iloc[runningquoteCount + 1]['time']
        if tradeCount < len(eurusd_trades)-1:
            nextTradeTime = eurusd_trades.iloc[tradeCount + 1]['time']
            if nextQuoteTime < nextTradeTime and runningPosition != 0:
                (realizedHedgePnL, runningPosition) = checkPnL_Hedge(nextQuoteTime,runningPosition,vwapBid,vwapOffer,STOP_LOSS)
            else:
                break    
        else:
            break
        
    runningPnL = round(float(runningPnL + realizedPnL + unrealizedPnL + realizedHedgePnL),2)
    position_eurusd.append(runningPosition)
    pnl_eurusd.append(runningPnL)
    print("TradeCount, Running VWAP Bid, Offer, BidQuantity, OfferQuantity, Net Quantity: %s,%s,%s,%s,%s,%s" % (tradeCount,vwapBid,vwapOffer,runningBidPosition,runningOfferPosition,runningPosition))
    print("RealizedPnl, UnrealizedPnL, totalPnL: %s,%s,%s" % (realizedPnL,unrealizedPnL,runningPnL))
    #print (runningPnL)
print ("Final Position & pnL: %s , %s"%(runningPosition,runningPnL))
#Adding 2 new columns in the trades dataframe to store the corresponding running Long/Short Position & PnL(in millions)
eurusd_trades['position'] = [p/100000 for p in position_eurusd]
eurusd_trades['pnl'] = [k/1000000 for k in pnl_eurusd]
eurusd_trades['price'] = [float(p) for p in price_eurusd]
# Plotting the whole series takes a bit of time, plotting PnL for first N trades instead
#plt.plot(eurusd_trades['time'].head(2000),eurusd_trades['pnl'].head(2000) , color = 'r')
#plt.plot(eurusd_trades['time'].head(2000),eurusd_trades['position'].head(2000) , color = 'b')
#plt.show()


# # Testing the filtering of timestamps
# #eurusd_trades.columns
# eurusd_prices['time']
# max(eurusd_prices.loc[eurusd_prices['time'] < '01:34:00']['time'])
# eff_quote_time[-1]
# sum1 = 0.0
# for i in range(10):
#     sum1 = sum(eurusd_trades.iloc[i]['tradeQuantity']*eurusd_prices.loc[eurusd_prices['time'] == eff_quote_time[i]]['bidPrice'],sum1)
#     print (sum)

# In[4]:


# Testing the filtering of timestamps
#eurusd_trades.columns
import math
import matplotlib.pyplot as plt
eurusd_prices['time']
max(eurusd_prices.loc[eurusd_prices['time'] < '01:34:00']['time'])
eff_quote_time[-1]
sum1 = 0.0
sum2 = []
for i in range(10):
    sum1 = float(sum1) + eurusd_trades.iloc[i]['tradeQuantity']*eurusd_prices.loc[eurusd_prices['time'] == eff_quote_time[i]]['bidPrice']
    sum2.append(sum1)
print (sum2)
plt.plot(sum2)


# In[96]:


#print(eurusd_trades['time'])
eurusd_trades['pnl'] = [k*1000000 for k in pnl_eurusd]
#eurusd_trades['position'] = [k/100000 for k in position_eurusd]
#plt.plot(eurusd_trades['time'].head(5000),eurusd_trades['pnl'].head(5000), color ='r')
plt.plot(eurusd_prices['time'].head(4000),((eurusd_prices['bidPrice']+eurusd_prices['offerPrice'])/2).head(4000), color ='b')
plt.show()


# In[138]:



print ("Final Position & pnL: %s , %s"%(runningPosition,runningPnL))
#eurusd_trades['price'] = [float(p) for p in price_eurusd]
#eurusd_trades.head(50)
#eurusd_trades.plot(kind='kde',x='price',y='tradeQuantity')
#plt.hist(x=eurusd_trades['price'], y = eurusd_trades['tradeQuantity'],bins='auto',rwidth=0.0010)
eurusd_trades.plot(kind = 'bar' , x = 'price' , y = 'tradeQuantity' )


# In[147]:


eurusd_prices['midPrice'] = (eurusd_prices['bidPrice']+eurusd_prices['offerPrice'])/2
mp1 = eurusd_prices.plot(kind='line',x='time',y='midPrice')
px1 = eurusd_trades.plot(kind='line',x='time',y='pnl' , color = 'r')
ax1 = eurusd_trades.plot(kind='line',x='time',y='position' )
#eurusd_trades.loc[eurusd_trades['tradeQuantity'] == max(eurusd_trades['tradeQuantity'] & eurusd_trades['time'] < '05:00:00')]


# In[4]:


#Task 2: Alpha Trading Strategy

# Given the Bid/Offer quotes and the Trades data only, we have to play with Only 2 parameters in this context
# Our target is to predict the direction primarily of the immediate next quote or two, depending on the previous Quotes & the Trades

pnl_eurusd = []; position_eurusd = []; 
eff_quote_time = []; runningPnL = 0.00; runningPosition = 0; 
vwapBid_num = 0.00; vwapOffer_num = 0.00; bidPrice = 0.00; offerPrice = 0.00; vwapBid = 0.00; vwapOffer = 0.00
nextQuote1_time = []; nextQuote2_time = []; bidOfferSpread = []; runingbidOfferQuantRatio = []; bidQuantity = [];
offerQuantity = []

initialTradeCount = 0
for quoteCount in range(len(eurusd_prices)-1):
    #print (eurusd_trades.iloc[tradeCount]['time'])
    #Find the latest Bid/Offer quote prior to the trade
    #realizedPnL = 0.00; unrealizedPnL = 0.00
    quoteTime = eurusd_prices.iloc[quoteCount]['time']
    nextQuoteTime = eurusd_prices.iloc[quoteCount+1]['time']
    bidPrice = eurusd_prices.iloc[quoteCount]['bidPrice']
    offerPrice = eurusd_prices.iloc[quoteCount]['offerPrice']
    bidOfferSpread.append(bidPrice - offerPrice)
    
    #Now find the Bid/Offer Ratio at that price level
    # The count is set to 1 to avoid division by zero
    runningOfferPosition = 1; runningBidPosition = 1
    print (" QuoteCount, Quotetime & NextQuoteTime  --> %s %s %s " % (quoteCount,quoteTime,nextQuoteTime))
    for tradeCount in range(initialTradeCount,len(eurusd_trades)):
        #print("INITIAL TRADECOUNT & tradeCount %s %s" % (initialTradeCount,tradeCount))
        tradeQuantity = eurusd_trades.iloc[tradeCount]['tradeQuantity']
        tradeTime = eurusd_trades.iloc[tradeCount]['time']
        #print("NEXT QUOTE time !! %s " % nextQuoteTime)
        if tradeTime > nextQuoteTime:
            #print("TRADE TIME > NEXT QUOTE !! %s " % nextQuoteTime)
            break
        else:
            if  tradeTime >= quoteTime:
                if eurusd_trades.iloc[tradeCount]['side'] == 'BID':
                    runningBidPosition = int(runningBidPosition) + tradeQuantity
                    #print("runningBidPosition BID:%s at time %s "% (runningBidPosition,tradeTime))
                else:
                    runningOfferPosition = int(runningOfferPosition) + tradeQuantity
                    #print("runningOfferPosition OFFER:%s at time %s "% (runningOfferPosition, tradeTime))
            

    # To optimise the Trade search, the counter starts from the last one
    initialTradeCount = tradeCount
    bidQuantity.append(runningBidPosition)
    offerQuantity.append(runningOfferPosition)
    runingbidOfferQuantRatio.append(runningBidPosition/runningOfferPosition)
    print ("time, bidPrice,OfferPrice,BidQuant,OfferQuant: %s,%s,%s,%s,%s "% (quoteTime,bidPrice,offerPrice,runningBidPosition,runningOfferPosition))

# To make it equal length as the prices series
bidQuantity.append(1);offerQuantity.append(1)
    
eurusd_prices['bidQuantity']  = bidQuantity   
eurusd_prices['offerQuantity']  = offerQuantity
eurusd_prices['bidOfferRatio']  = [round(float(b) / float(o),5) for b,o in zip(bidQuantity, offerQuantity)]
eurusd_prices['midPrice'] = (eurusd_prices['bidPrice']+eurusd_prices['offerPrice'])/2
eurusd_prices['bidAskSpread'] = (eurusd_prices['bidPrice']-eurusd_prices['offerPrice'])    
print(eurusd_prices.head(1000))
            


# In[35]:


# Task 2 : Trading Strategy: This is just a trial
# The main GLM model is in R. Couldn't do GLM here for lack of statsmodel package

from sklearn import linear_model
#eurusd_prices['netQuantity'] = eurusd_prices['bidQuantity'] - eurusd_prices['offerQuantity']
#eurusd_prices['bidAskSpread'] = (eurusd_prices['bidPrice']-eurusd_prices['offerPrice'])
#eurusd_prices.head(50)

newRegeurusd_df = pd.DataFrame(data=eurusd_prices)
newRegeurusd_df.set_index('time')

# get the feature sets in a new df
X = pd.DataFrame(data=newRegeurusd_df[:-1], columns = ["bidOfferRatio","bidAskSpread","netQuantity"])
y = newRegeurusd_df['midPrice'][1:]
lm = linear_model.LinearRegression()
model = lm.fit(X,y)
print(model)
lm.score(X,y)

#newRegeurusd_df['midPrice'][2:]
#plt.scatter( x=newRegeurusd_df['bidOfferRatio'][:-1] , y = newRegeurusd_df['midPrice'][1:]  , s= 0.0001)
#plt.scatter(x, y, s=10)


# In[59]:


newRegeurusd_df.head(50)
newRegeurusd_df.to_csv('RegEurUsd.csv')
#newRegeurusd_df.plot(kind='bar',x='midPrice',y='netQuantity')


# In[96]:


import math
pd.to_datetime(eurusd_prices['time']).astype(int)
newRegeurusd_df.loc[(newRegeurusd_df['midPrice'] > 1.1145) & (newRegeurusd_df['midPrice'] < 1.1152)]
newRegeurusd_df['totalQuantity'] = round(newRegeurusd_df['bidQuantity'] + newRegeurusd_df['offerQuantity'],5)
newRegeurusd_df['logratio']  = [round(math.log(float(b) / float(o)),5) for b,o in zip(bidQuantity, offerQuantity)]
newRegeurusd_df['totalXnetQuantity'] =  round(newRegeurusd_df['netQuantity'] * newRegeurusd_df['totalQuantity'],5)
#newRegeurusd_df['nextMidPrice'][0:len(newRegeurusd_df)-1] = newRegeurusd_df['midPrice'][1:]
#[round(float(n) * float(t),5) for n,t in zip(netQuantity, totalQuantity)]
newRegeurusd_df['pricediff'] = newRegeurusd_df['midPrice'].diff()
# for k in range(len(newRegeurusd_df)-1):
#     newRegeurusd_df.iloc[k]['pricediff'] =  newRegeurusd_df.iloc[k+1]['pricediff']
#newRegeurusd_df['midPrice'] > 1.1145
#newRegeurusd_df.plot(kind='bar', x= 'midPrice', y = 'totalQuantity')
newRegeurusd_df[['time','midPrice','pricediff','netQuantity','totalQuantity','logratio','totalXnetQuantity']].sort_values(by=['netQuantity'],ascending=False).head(50)

#newRegeurusd_df.index


# In[120]:


# Task 3 Part 1 & 2: To show PnL per client
# print("PnL per client  : ", str(pnl_client))
result = {}
for d in pnl_trade: 
    for k in d.keys(): 
        result[k] = round(float(result.get(k, 0)) + float(d[k] ),2)
print (result)
print(sum(result.values()))
plt.bar(range(len(result)), list(result.values()), align='center')
plt.xticks(range(len(result)), list(result.keys()))
plt.show()


# In[138]:


# Task 3, Part 3 : Correlation
import scipy.stats
eurusd_prices['midPrice'] = (eurusd_prices['bidPrice']+eurusd_prices['offerPrice'])/2
usdchf_prices['midPrice'] = (usdchf_prices['bidPrice']+usdchf_prices['offerPrice'])/2

# In order to see the correlation, We need to construct a df with eurusd and usdchf quotes on the same time index first
df_eur = eurusd_prices.set_index('time')
df_chf = usdchf_prices.set_index('time')

merge_eurchf=pd.merge(df_eur,df_chf, how='inner', left_index=True, right_index=True)
#Now show the scatter plot & correlation coeff
plt.scatter(merge_eurchf['midPrice_x'], merge_eurchf['midPrice_y'])
print (merge_eurchf['midPrice_x'].corr(merge_eurchf['midPrice_y'])
,merge_eurchf['midPrice_x'].corr(merge_eurchf['midPrice_y'], method = 'spearman')
,merge_eurchf['midPrice_x'].corr(merge_eurchf['midPrice_y'],method = 'kendall'))


# In[ ]:




