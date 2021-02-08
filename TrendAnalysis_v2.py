
# **** Version Control******
# v2.0 - Original One
# 27/04/2020 - Added NASDAQ & DowJones index
# 01/05/2020 - Added USDZAR & USDMXN
# 
# **********

from __future__ import absolute_import
from __future__ import print_function
import six.moves.configparser  # 1 
from array import array
from cProfile import label
from ctypes.wintypes import DOUBLE
import datetime
import six.moves.http_client
import json
from operator import concat
import operator
from string import index
import sys
import six.moves._thread
from threading import Timer, Thread, Event
from time import strftime
import time
import six.moves.urllib.request, six.moves.urllib.parse, six.moves.urllib.error

from matplotlib.legend import Legend
from matplotlib.pyplot import hlines, legend, title, text
from numpy.lib.function_base import average
from numpy.polynomial.polynomial import polyfit
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from pandas.io.pytables import HDFStore
from sklearn import datasets, linear_model
from sklearn.linear_model import  LinearRegression
from sklearn.metrics import mean_squared_error, r2_score , regression
from talib.abstract import numpy, LINEARREG
from pandas.tseries.offsets import BDay

#from com.clients.Mlearning.SVMTester import low
import matplotlib.pyplot as plt
import numpy as np
import oandapy as opy  # 2
import pandas as pd
import talib as tal
from sqlite3 import Timestamp
from numpy.lib.polynomial import polyval
from scipy.linalg._solve_toeplitz import float64
from calendar import weekday
from Cython.Shadow import NULL
from six.moves import range


#import seaborn as sns; sns.set()  # 18
config = six.moves.configparser.ConfigParser()  # 3
config.read('oanda.cfg')  # 4
All_Ins = ['EUR_USD','EUR_GBP','EUR_JPY','EUR_AUD','GBP_USD','GBP_JPY','GBP_AUD','AUD_USD','USD_JPY','AUD_JPY','AUD_NZD',
          'GBP_CAD','CAD_JPY','EUR_CAD','AUD_CAD','USD_CAD','BCO_USD','WTICO_USD','XAU_USD', 'XAG_USD', 'NZD_USD',
          'NZD_JPY', 'GBP_NZD', 'EUR_NZD','USD_ZAR','USD_MXN', 'GBP_CHF', 'EUR_CHF','USD_CHF','AUD_CHF','NZD_CAD',
          'SPX500_USD','NAS100_USD', 'US30_USD','USB10Y_USD','USB02Y_USD','USB05Y_USD','UK100_GBP',
          'UK10YB_GBP','DE30_EUR','DE10YB_EUR'
          ]
CCY_Tester = [ 'GBP_USD', 'SPX500_USD']
# No. of Candles setup
NCandles = 5 #No. of candles on either side
FIB_LEVELS = [.236,.382,.50,.618,.786]
Threshold = 0.0012 #Tolerance level
NoOfSameLevels = 1
levelDict = {}
tradeLogDict = {}
trendLogDict = {} # Structure is Curr:<TimeStamp>:<Trend>
currMatchingTrendDict = {} # Structure is Curr:Boolean
doneToday = {'W':False,'D':False,'H4':False}
oanda= opy.API(environment='practice',
                access_token='d37846642ec6da2de1bcd8d181d4b867-3ba1ff9c00bf0ee87d9cc7a18987212b')  # 5
data = {}
score = {}

# class MyThread(Thread):
#     def __init__(self, event):
#         Thread.__init__(self)
#         self.stopped = event
# 
#     def run(self):
#         while not self.stopped.wait(60):
#             print ("My pi pi thread")
#             data = oanda.get_history(instrument='EUR_USD',  # our instrument  vx 
#                          start='2016-04-21',  # start data
#                          #end='2017-04-04',  # end date
#                          granularity='D')  # minute bars  # 
#             df = pd.DataFrame(data['candles']).set_index('time')  # 8
#             df.index = pd.DatetimeIndex(df.index)
            #print df1D['closeAsk']

#stopFlag = Event()
#thread = MyThread(stopFlag)
#thread.start()
## MASTER LOOP OVER ALL G8 PAIRS


# Procedure to draw Support & Resistance using the turning points
#Turning points are defined as: Close Prices/ Highs/Lows which have NCandles Up & NCandles down candles on both sides
#Now the Support & Resistance, could be constructed by joining 2 or more of these Turning points
#There has to be some buffer zone of about 10/20 pips to be defined to draw some Support/Resistance Zones 
#instead of exact levels
# The Algo we are using here is : First sort the turning points, then try to pair up sequentially as many possible

def drawLevels(Supportlevels,ResistanceLevels, curr):
    #print("Am getting there to draw levels Now..")
    #levelDict = {}
    if curr not in levelDict:
        levelDict[curr] = {}
    #Construct a Single series of levels but still we want to keep Support & Resistance separate
    OneSetOfLevels = [ Supportlevels,ResistanceLevels]
    OneFrame = pd.concat(OneSetOfLevels)    
    #orderedLevels = OneFrame.sort_index()
    orderedLevels = OneFrame.sort_values()
    
    for levels in range(1,len(orderedLevels)):
        for level2 in range(levels+1,len(orderedLevels)):
            if (orderedLevels[level2] > orderedLevels[levels] + (Threshold*100.0 if any(subccy in curr for subccy in ['JPY','BCO'])  else Threshold)):
                break;
        #levelAvg = average(orderedLevels[range(levels,level2)])
        if (level2 - levels) >=NoOfSameLevels:
            levelWeight = level2 - levels
            levelDict[curr].update({average(orderedLevels[levels:level2]):levelWeight}) 
            #print("Time Weightage of %s  " % (Alllevels[levels])) 
    #print ("THE LEVEL DICT for %s --> %s" %(curr,levelDict[curr]))
    #Draw the Fibs based on the LAST Support & resistance
    #drawFibs(ResistanceLevels[-1], Supportlevels[-1],orderedLevels)
    #drawFibs(max(levelDict[curr]), min(levelDict[curr]),orderedLevels)

#You only need the High & low to calculate the Fibs. Alllevels (ordered) is being passed as a param
#to facilitate calling the significantFibLevels function
def drawFibs( high,  low):
    print("Preparing to chalk out Fibs..")
    local_fib_levels = [(high - (high-low)*fib_level) for fib_level in FIB_LEVELS] 
    print(("FIB levels for High %s  Low %s --> %s" % (high,low, local_fib_levels)))
    #significantFibLevels(local_fib_levels, Alllevels)
    return local_fib_levels 
    
#This method iterates over the Fib levels found in drawFibs(..) method and compares the significance
#with the complete list of Support/Resistance levels found before
def significantFibLevels (fib_levels, S_R_levels):
    print ("Going to find significance of Fib levels")
    signi_fibs = [afib_level for afib_level in fib_levels if any(abs(afib_level - aLevel)<= Threshold/2
                  for aLevel in S_R_levels)]
    #for aFibLevel in sorted(fib_levels):
    #    for aLevel in S_R_levels if aFibLevel:
    print(("Significant Fib levels %s" % signi_fibs))        
                
def checkTrend(Supportlevels,ResistanceLevels, closePrice,closeTime,ema50, curr, time):
    #Simple Algo here, Higher high & higher lows for Uptrend, Lower highs & lower lows for downtrend
    #COULD BE CONSIDERED: Change of slope of Linear Regression (to complicate things !)
    #The last argument time is passed to detect the latest time, to detect the pattern in all 3 timeframes  
    
    if ((ResistanceLevels[-1] > ResistanceLevels[-2]) and (Supportlevels[-1] > Supportlevels[-2]) and closePrice > ema50):
        trendLogDict[curr].update({closeTime:"UPTREND"})
        #Checking with previous timeframe trend
        if currMatchingTrendDict[curr] != False  and currMatchingTrendDict[curr] == "UPTREND" and time == 1:
            currMatchingTrendDict[curr] = "UPTREND"
            print(("%s %s UPTREND" % curr,closeTime))
        else:     
            currMatchingTrendDict[curr] = False  
        #print("%s IS in UPTREND " % curr)
        #return 1
    else:
        if ((ResistanceLevels[-1] < ResistanceLevels[-2]) and (Supportlevels[-1] < Supportlevels[-2]) and closePrice < ema50):
            trendLogDict[curr].update({closeTime:"DOWNTREND"})
            #Checking with previous timeframe trend
            if currMatchingTrendDict[curr] != False  and currMatchingTrendDict[curr] == "DOWNTREND" and time == 1:
                currMatchingTrendDict[curr] = "DOWNTREND"
                print(("%s %s DOWNTREND" % curr,closeTime))
            else:     
                currMatchingTrendDict[curr] = False  
            #print("%s IS IN DOWNTREND " % curr)
            #return -1
        else:
            trendLogDict[curr].update({closeTime:"NO_TREND"})
            #print(" %s NO TREND  WAIT !!! " % curr)
            #return 0
    
                   

## LINEAR REGRESSION PROCEDURE ....####
def checkTrendLines(KeyLevels):
    #Try to draw a linear regression with as much highs & lows as possible, with minm Residual error
    #(May BE NOT!!)Construct a Single series of levels but still we want to keep Support & Resistance separate
    #OneSetOfLevels = [ SupportLevels,ResistanceLevels]
    dfs = pd.DataFrame(data = KeyLevels, index = KeyLevels.index)
    #print dfs['lowBid']
    #dfs['index1'] = SupportLevels.index
    #dfs['levels'] = SupportLevels
    #Get last few Key levels , could be 5 to 10
    #lastFew = dfs.tail(10)
    #print("Last 6 Regression points--> %s" % pd.to_datetime(last6.index).astype(int))
    #pd.to_timedelta(last6).dt.total_seconds().astype(int)
    b,m = polyfit(pd.to_datetime(KeyLevels.index).astype(int), KeyLevels, 1)
    #print [b,m]
    y_fit = polyval([m,b],pd.to_datetime(KeyLevels.index).astype(int))
    return y_fit
   

## Output formatter indexed by ccy pair ## 
def outPutFormatter(trendLogDict, granularity):
    #Try to read the trendLogDict into a DataFrame and Output to excel
    print(("########## %s ###########" % granularity))
    trendFrame = pd.DataFrame.from_dict(trendLogDict, orient = 'index')
    print(trendFrame)
    
    
## Method to detect change in (Daily)Trend  and to highlight diff ##
#def detectChange(trendLogDict, granularity): 
    
        
    
 
def tradePoints(Supportlevels,ResistanceLevels, closePrice, curr):
    # Main routine to trigger a TRADE !!
    # Steps include: Establish if there's a Trend. ****If yes, and last Closing price within last Support & Resistance levels*** Prepare:
    # Wait for Price to pull back to one of the Fib levels, if its a significant Fib level, the better.
    # Look for a candle confirmation: Bullish/Bearing Engulfing Or a PinBar preferable 
    #That's it pretty much ! Trigger the Button!
    if(checkTrend(Supportlevels, ResistanceLevels, curr) == 1):
        print("AM IN UPTREND ----")
        #if(closePrice.between(ResistanceLevels[-1], Supportlevels[-1])):
        #Check Fib levels based on last Resistance & second last Support
        current_Fib_levels = drawFibs(ResistanceLevels[-1], Supportlevels[-2])
        if (any(abs(Supportlevels[-1] - aFibLevel)<= Threshold/2 for aFibLevel in current_Fib_levels)):
            print("LAST SUPPORT AT SYNC WITH A FIB LEVEL-- GOOD (*)")
            if(any(abs(Supportlevels[-1] - aKeyLevel)<= Threshold/2 for aKeyLevel in levelDict[curr] if aKeyLevel != Supportlevels[-1])):
                print("LAST SUPPORT COINCIDES WITH A PREV LEVEL-- EVEN BETTER (**). SET SL to that level")
                #populate the Trade Log object
                #if curr not in tradeLogDict:
                #   tradeLogDict[curr] = {}
                tradeLogDict[curr].update({closePrice: [Supportlevels[-1] - Threshold/2]})
            else:
                #Not a Key level, Put the SL conservatively i.e second last Support level
                tradeLogDict[curr].update({closePrice: [Supportlevels[-2] - Threshold/2]}) 
        else:
            print("TREND FOUND, BUT LAST SUPPORT DOESN'T COINCIDE WITH ANY LEVEL")
            
    elif ((checkTrend(Supportlevels, ResistanceLevels, curr) == -1) and closePrice < ResistanceLevels[-1] and closePrice < ema50):
            print("AM IN DOWN TREND ----")
            #if(closePrice.between(ResistanceLevels[-1], Supportlevels[-1])):
            #Check Fib levels based on last Resistance & second last Support
            if (any(abs(ResistanceLevels[-1] - aFibLevel)<= Threshold/2 for aFibLevel in current_Fib_levels)):
                print("LAST SUPPORT AT SYNC WITH A FIB LEVEL-- GOOD (*)")
                #if(checkPathClear(closePrice, curr)):
                if(any(abs(ResistanceLevels[-1] - aKeyLevel)<= Threshold/2 for aKeyLevel in levelDict[curr] if aKeyLevel != ResistanceLevels[-1])):
                    print("LAST SUPPORT COINCIDES WITH A PREV LEVEL-- EVEN BETTER (**). SET SL to that level")
                        # populate the Trade Log object
                        # if curr not in tradeLogDict: 
                        #   tradeLogDict[curr] = {}
                    tradeLogDict[curr].update({closePrice: [Supportlevels[-1] - Threshold/2]})
                else:
                    # Not a Key level, Put the SL conservatively i.e second last Support level
                    tradeLogDict[curr].update({closePrice: [Supportlevels[-2] - Threshold/2]})
                #else:
                    #print("PATH NOT CLEAR AHEAD FOR *SELL* TRADE AT %s " % closePrice)        
            else:
                print("DOWN TREND FOUND, BUT LAST SUPPORT DOESN'T COINCIDE WITH ANY LEVEL")       
    else:
        print("NO TREND... WAIT WAIT !!!")                 
                        
def testTradePoints(Supportlevels,ResistanceLevels, closePrice, curr):
    # Main routine to trigger a TRADE !!
    # Steps include: Establish if there's a Trend. ****If yes, and last Closing price within last Support & Resistance levels*** Prepare:
    # Wait for Price to pull back to one of the Fib levels, if its a significant Fib level, the better.
    # Look for a candle confirmation: Bullish/Bearing Engulfing Or a PinBar preferable 
    #That's it pretty much ! Trigger the Button!
    if(checkTrend(Supportlevels, ResistanceLevels, curr) == 1):
        print("AM IN UPTREND ----")
        #if(closePrice.between(ResistanceLevels[-1], Supportlevels[-1])):
        #Check Fib levels based on last Resistance & second last Support
        current_Fib_levels = drawFibs(ResistanceLevels[-1], Supportlevels[-2])
        if (any(abs(Supportlevels[-1] - aFibLevel)<= Threshold/2 for aFibLevel in current_Fib_levels)):
            print("LAST SUPPORT AT SYNC WITH A FIB LEVEL-- GOOD (*)")
            if(any(abs(Supportlevels[-1] - aKeyLevel)<= Threshold/2 for aKeyLevel in levelDict[curr] if aKeyLevel != Supportlevels[-1])):
                print("LAST SUPPORT COINCIDES WITH A PREV LEVEL-- EVEN BETTER (**). SET SL to that level")
                #populate the Trade Log object
                #if curr not in tradeLogDict:
                #   tradeLogDict[curr] = {}
                tradeLogDict[curr].update({closePrice: [Supportlevels[-1] - Threshold/2]})
            else:
                #Not a Key level, Put the SL conservatively i.e second last Support level
                tradeLogDict[curr].update({closePrice: [Supportlevels[-2] - Threshold/2]})
        else:
            print("TREND FOUND, BUT LAST SUPPORT DOESN'T COINCIDE WITH ANY LEVEL")                        
        

def calculateKeyLevels(lowPrices, highPrices):
    # Local_turning_points Support, using Close OR Low prices:
        local_turning_points_support = [localTPoints for localTPoints in range(NCandles, len(lowPrices) - NCandles) 
                                if (lowPrices[localTPoints] < min(lowPrices[list(range(localTPoints - NCandles, localTPoints))]) 
                                and (lowPrices[localTPoints] < min(lowPrices[list(range(localTPoints + 1, localTPoints + NCandles + 1))])))]
        # Local_turning_points Resistances, using Close or High prices:
        local_turning_points_resistance = [localTPoints for localTPoints in range(NCandles, len(highPrices) - NCandles) 
                                if (highPrices[localTPoints] > max(highPrices[list(range(localTPoints - NCandles, localTPoints))])
                                and (highPrices[localTPoints] > max(highPrices[list(range(localTPoints + 1, localTPoints + NCandles + 1))])))]
    
        return local_turning_points_support,local_turning_points_resistance


# Show upto 30Mins of granulation
# CHANGED the lowest granular from 1H to 30M on 2/2/21
for gran in ['W','D','H4' ,'H1']:
    #'W', 'W','D','D','H4', 'H4'
    levelDict = {}
    trendLogDict = {}
    for curr in All_Ins:
    #     data4H = oanda.get_history(instrument=curr,  # our instrument
    #                          start='2017-01-01',  # start data
    # #                         end='2017-04-21',  # end date
    #                          granularity='H4')  #
    #                          
        
        #Initialize the trendDict
        #print("Getting Data for %s"%curr)
        if curr not in trendLogDict:
            trendLogDict[curr] = {}
            
        if curr not in currMatchingTrendDict:
            currMatchingTrendDict[curr] = False
        
        regmodel = LinearRegression()
        n = 1
        # NOTE: All the previous timeperiods are 1 less, due to the format of Oanda Close data
        #Eg: <Start period> <Value> . Hence timedelta(2) is substracted instead of timedelta(1) 
            
        if gran == 'W':
            ND = 365*3 + 14 # Adding 14 to accomodate 2 extra weeks, since we are showing trends for last 3 weeks
        elif gran == 'D':
            ND = 600 + 2
        elif gran == 'H4':
            ND =  365/4 + 2/4
        else:
            ND = 365/25
             
        enddate = '2020-05-25 11:00:00'            
        data1D = oanda.get_history(instrument=curr,  # our instrument
                                 start=(datetime.datetime.now() - datetime.timedelta(ND)).strftime('%Y-%m-%d'),  # start data
                                 #end=enddate.strftime('%Y-%m-%d') ,  # end date
                                 #end = '2020-05-25',
                                 #end=enddate.strftime('%Y-%m-%d HH:mm:ss'),  # end date i.e current date
                                 granularity=gran) 
     
        # df4H = pd.DataFrame(data4H['candles']).set_index('time')  # 8
        # df4H.index = pd.DatetimeIndex(df4H.index)  # 9
        
        #print (data1D)
        df1D = pd.DataFrame(data1D['candles']).set_index('time')  # 8
        df1D.index = pd.DatetimeIndex(df1D.index)  # 9
        
        # df.info()
        # close = (df1D['closeBid']).__getitem__([index = (index % 2 =0)])
        openC = (df1D['openBid'])
        close = df1D['closeBid']
        # close1 = (df1D['closeAsk'])
        highPrices = df1D['highBid']
        lowPrices = df1D['lowBid']
        # A placeholder parameter, might be useful 
        volume = (df1D['volume'])
        
        #print df1D.tail()
        #print close,volume
        #print (curr,gran,close[-1], volume[-1])
        #print ("Last closing High & low price-> %f %f" % (highPrices[-1], lowPrices[-1]))
        ema8 = tal.EMA(np.array(close), 8)
        ema21 = tal.EMA(np.array(close), 21)
        ema50 = tal.EMA(np.array(close), 50)
        sma200 = tal.SMA(np.array(close), 200)
        rsi14 = tal.RSI(np.array(close), 14)
        
        #print ("200 SMA --> %s %s %s" % (curr,gran,sma200[-1]))
        
        # Lets get the Local Highs & Lows/Close prices
        # High/Low = In a NCandles candle setup, its higher/lower than the previous & next NCandles candles
        # An optimised way to check, would be to compare the current with the max/min of previous NCandles candles
        # NCandles could be 2, 4, 5... anything as per the strength of the turning point
        # It's envisaged , we might need to isolate the Support & Resistances, hence splitting into 2 categories
      
        
        # Local_turning_points using Close price, One set for for both Support & Resistance
        local_turning_points = [localTPoints for localTPoints in range(NCandles, len(close) - NCandles) if ((close[localTPoints] > 
                                max(close[list(range(localTPoints - NCandles, localTPoints - 1))])
                                and close[localTPoints] > max(close[list(range(localTPoints + 1, localTPoints + NCandles + 1))]))  or
                                (close[localTPoints] < min(close[list(range(localTPoints - NCandles, localTPoints))])
                                and close[localTPoints] < min(close[list(range(localTPoints + 1, localTPoints + NCandles + 1))])))]
        # Local_turning_points Support, using Close OR Low prices:
        #Check the trend for the most current and 2 previous timeframe 
         
        for i in [3,2,1]: # i=1 is the latest candle 
            if i ==1:
                local_turning_points_support,local_turning_points_resistance = calculateKeyLevels(lowPrices[2:], highPrices[2:])
                # Also Calculate key levels based on Close Price
                #local_turning_points_support,local_turning_points_resistance = calculateKeyLevels(close[2:], close[2:]) 
            elif i ==2: 
                local_turning_points_support,local_turning_points_resistance = calculateKeyLevels(lowPrices[1:-1], highPrices[1:-1])
            else:
                local_turning_points_support,local_turning_points_resistance = calculateKeyLevels(lowPrices[:-2], highPrices[:-2])        
    #         local_turning_points_support = [localTPoints for localTPoints in range(NCandles, len(lowPrices) - NCandles) 
    #                                 if (lowPrices[localTPoints] < min(lowPrices[range(localTPoints - NCandles, localTPoints)]) 
    #                                 and (lowPrices[localTPoints] < min(lowPrices[range(localTPoints + 1, localTPoints + NCandles + 1)])))]
    #         # Local_turning_points Resistances, using Close or High prices:
    #         local_turning_points_resistance = [localTPoints for localTPoints in range(NCandles, len(highPrices) - NCandles) 
    #                                 if (highPrices[localTPoints] > max(highPrices[range(localTPoints - NCandles, localTPoints)])
    #                                 and (highPrices[localTPoints] > max(highPrices[range(localTPoints + 1, localTPoints + NCandles + 1)])))]
    #                                 
            
            # print ("LOCAL TURNING POINTS %s -> %s" %(curr,local_turning_points))
            # print ("NO. of LOCAL TURNING POINTS Support & Resistance for %s -> %s %s" %(curr,len(local_turning_points_support), len(local_turning_points_resistance)))
            
            # hlines(close[local_turning_points],min(close.index),max(close.index), color = 'r')
            # plt.axhline(y=all(close[local_turning_points]), color='r', linestyle='-')
            
            # Draw the Support & Resistances using the local turning points arrays
            # A strong support and Resistance level, is determined by the Number of local_turning_points passing thru it
            # At least, 2 turning points are needed for this(In my view!), and the turning points are OK to lie within
            # a threshold (lets say 20 pips) of each other. 
            # For now,we shall aim to construct a single set of level (incl Support and resistance), as we think a validation by  
            # both Support and Resistance tends to be a stronger level. If needed, we can just draw the Support & resistance separately. 
            # OneSetOfLevels = [ lowPrices[local_turning_points_support] , highPrices[local_turning_points_resistance]]
            # OneFrame = pd.concat(OneSetOfLevels)
        #     print("LAST SUPPORT AND LAST RESISTANCE FOR %s --> %s-- %s %s ",(curr,lowPrices[local_turning_points_support][-1], highPrices[local_turning_points_resistance][-1],
        #                                                                       (lowPrices[local_turning_points_support],highPrices[local_turning_points_resistance] ) ))
        #     
            # CHECK IF IT'S TIME TO TRADE !
            # checkTrend(lowPrices[local_turning_points_support] , highPrices[local_turning_points_resistance], curr)
            #Draw levels based on Close
            #drawLevels(close[local_turning_points_support_close] , close[local_turning_points_resistance_close], curr)
            drawLevels(lowPrices[local_turning_points_support] , highPrices[local_turning_points_resistance], curr)
            checkTrend(lowPrices[local_turning_points_support] , highPrices[local_turning_points_resistance], 
                     close[-i], close.index[-i], ema50[-i], curr,i) # Passing i to detect the latest timeframe 
                       
            
            # drawLevels(close[local_turning_points])
            # ordered_ltp = sorted(set(lowPrices[local_turning_points_support],highPrices[local_turning_points_resistance])
            # print ordered_ltp
            # Merged_frame = (lowPrices[local_turning_points_support]).union(highPrices[local_turning_points_resistance])
            # plt.plot(close[local_turning_points].index, close[local_turning_points])
            # # Plot the Key levels in Support & Resistance ##
            if gran == 'D' and i == 1:
                ## PLOT based on Close Price :
                #plt.plot(close[local_turning_points_resistance].index, close[local_turning_points_resistance], 'go' , linestyle = '-')
                #plt.plot(close[local_turning_points_support].index, close[local_turning_points_support], 'ro', linestyle='-')
                
                #print highPrices[local_turning_points_resistance], lowPrices[local_turning_points_support], close[-1]
                plt.plot(highPrices[local_turning_points_resistance].index, highPrices[local_turning_points_resistance], 'go' , linestyle = '-')
                plt.plot(lowPrices[local_turning_points_support].index, lowPrices[local_turning_points_support], 'ro', linestyle='-')
                plt.plot(close.index, close)
                
                # If needed to show ALL Support and Resistance levels, Uncomment below 2 blocks
                 
#                 for sup in lowPrices[local_turning_points_support]:
#                     plt.axhline(y=sup, color='r', linestyle='-', label=sup)
#                     plt.annotate(s= sup,xy=(lowPrices[local_turning_points_support].index[-1],sup) )
#                 
#                 for sup in highPrices[local_turning_points_resistance]:
#                     plt.axhline(y=sup, color='g', linestyle='-', label=sup)
#                     plt.annotate(s= sup,xy=(highPrices[local_turning_points_resistance].index[-1],sup) )    
                
                #print ('Fitted Values from REGRESSION for %s -> %s' % (curr,y_fit))
                lastFewSupport = lowPrices[local_turning_points_support].tail(10)
                lastFewResistance = highPrices[local_turning_points_resistance].tail(10)
                
                # Call REGRESSION method , separately on Support & Resistance
                y_fitted_support = checkTrendLines(lastFewSupport)
                y_fitted_resistance = checkTrendLines(lastFewResistance)
                
                #y_fitted_support = checkTrendLines(lowPrices[local_turning_points_support] )
                #y_fitted_resistance = checkTrendLines(highPrices[local_turning_points_resistance])
                #Plot the Regression line with last few points
                #plt.plot(lastFewSupport.index, y_fitted_support, color='b', linestyle='-', )
                #plt.plot(lastFewResistance.index, y_fitted_resistance, color='y', linestyle='-', )
                #Plot the significant levels (Eg: Levels which have been validated at least twice)
                for level in levelDict[curr]:
                    if (levelDict[curr][level] > 2):
                        plt.axhline(y=level, color='r', linestyle='-', label=level)
                        plt.annotate(s= level,xy=(lastFewSupport.index[-1],level) )
    #         
    #         #xfit = np.linspace(0, 5, 50)
    #         #yfit = regmodel.predict(xfit[:, np.newaxis]) 
    #         #plt.plot(xfit,yfit)
    #         
    #         plt.title(curr + "  " + gran)
                plt.legend(curr)
                #plt.show()
                # plt.title(label = curr, loc = 'center')
                plt.savefig('C:\Users\Shuv\Documents\All Trading\Program Outputs\%s' % curr + "_" + gran)
                plt.close()
                
                
                
            # CHECK THE TRADING LOG NOW !!
            # print ("THE TRADING LOG for %s --> %s" %(curr,tradeLogDict[curr]))  
    outPutFormatter(trendLogDict, gran)
#print pd.DataFrame.from_dict(currMatchingTrendDict, orient = 'index')     
        
    
            
        
        
