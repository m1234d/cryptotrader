from binance.client import Client
import msvcrt
import time
import sys
sys.path.append("C://Users/matth/")
import keyboard
from Prices import *
import pickle

from stockstats import StockDataFrame
client = Client("YyJcRnCwOo5h5YoLgSFBFZMGnlwehT0S845XKBD6KYr1IGTuz8pGNZbDR29hxWGR", "4vs7jUlSG4YI8hbcBKtQvF8fKXii6kcP0RcDPwJKFAxbIDLdfBlQvmrOd8xRvTJr")
from pandas import DataFrame
import pandas
import pandas as pd
import tkinter as tk
from binance.enums import *
from binance.websockets import BinanceSocketManager
globalData = dict()
mode = "Buying Mode Enabled"
def write_slogan():
    global testVar
    global mode
    global slogan
    global globalData
    if mode == "Buying Mode Enabled":
        mode = "Buying Mode Disabled"
        slogan.configure(text=mode)
        for t,i in globalData.items():
            i['traderData']['buyingEnabled'] = False
    else:
        mode = "Buying Mode Enabled"
        slogan.configure(text=mode)
        for t,i in globalData.items():
            i['traderData']['buyingEnabled'] = True



root = tk.Tk()
frame = tk.Frame(root)
frame.pack()
slogan = tk.Button(frame,
                   text=mode,
                   command=write_slogan)
slogan.pack(side=tk.LEFT)



def task():
   root.update()



def getAmount(sym, amt=.00028):
    return amountToLots(amt*(1/getPrice(sym)), sym)
    
def getPrice(sym):
    return float(client.get_symbol_ticker(symbol=sym)['price'])

def buy(traderData):

    traderData['buyPrice'] = float(client.get_ticker(symbol=traderData['tradingSymbol'])['askPrice'])
    traderData['buyAmount'] = traderData['amount'] * traderData['buyPrice']
    print("Buying", traderData['tradingSymbol'], ":", traderData['buyAmount'], "price:", traderData['buyPrice'])
    order = client.order_market_buy(
        symbol = traderData['tradingSymbol'],
        quantity = traderData['amount']
    )
    traderData['bought'] = True
    
def sell(traderData):
    sellAmount = traderData['amount'] * float(client.get_ticker(symbol=traderData['tradingSymbol'])['bidPrice'])
    print("Selling", traderData['tradingSymbol'], ":", sellAmount)
    print("Profit:", (sellAmount - traderData['buyAmount']))
    order = client.order_market_sell(
        symbol = traderData['tradingSymbol'],
        quantity = traderData['amount']
    )
    traderData['profit'] += (sellAmount - traderData['buyAmount'])
    traderData['bought'] = False

def buyTest(traderData):
    traderData['buyPrice'] = traderData['candles'][-1]['close']
    traderData['buyAmount'] = traderData['amount'] * traderData['candles'][-1]['close']
    print("Buying:", traderData['buyAmount'])
    traderData['bought'] = True
    
def sellTest(traderData):
    sellAmount = traderData['amount'] * traderData['candles'][-1]['close']
    print("Selling:", sellAmount)
    print("Profit:", (sellAmount - traderData['buyAmount']))
    print("Percent:", (sellAmount - traderData['buyAmount'])/traderData['buyAmount'] * 100)
    traderData['profit'] += (sellAmount - traderData['buyAmount'])
    traderData['bought'] = False
    
def generateChart(algo, traderData):
    try:
        chart = DataFrame.from_dict(traderData['candles'])
        stock = StockDataFrame.retype(chart)
        value = CCI(chart['close'], chart['high'], chart['low'], 4, 0.0109)[-1]

        if (time.clock() - traderData['startTime'] > traderData['time']):
            traderData['buyingEnabled'] = False
        if algo == "cci":
            print(traderData['tradingSymbol'], value, traderData['candles'][-1]['close'], traderData['candles'][-1]['date'])
            cci_value = value
            if cci_value < -100 and traderData['bought'] == False and traderData['updating'] == False:
                traderData['waiting'] = True
            if cci_value > -100 and traderData['bought'] == False and traderData['waiting'] and traderData['buyingEnabled']:
                buy(traderData)
                traderData['waiting'] = False
            elif cci_value > 100 and traderData['bought']:
                sell(traderData)
    
        if algo == "macd":
            macd_value = stock['macdh'][-1]
            print(macd_value)
            if macd_value > 0 and traderData['bought'] == False:
                buy(traderData)
            elif macd_value < 0 and traderData['bought']:
                sell(traderData)
    #get cci value for current time
    #if greater than 100 and not bought in yet, buy
    #if less than 100(NOT -100) and bought in, sell
    except:
        print("Unexpected error, trying again")
        time.sleep(.3)
        generateChart(algo, traderData)

def CCI(close, high, low, n, constant): 
    TP = close
    CCI = pd.Series((TP - TP.rolling(n).mean()) / (constant * TP.rolling(n).std()), name = 'CCI_' + str(n)) 
    return CCI
        
def generateBackChart(algo, traderData):

    chart = DataFrame.from_dict(traderData['candles'])
    stock = StockDataFrame.retype(chart)
    value = CCI(chart['close'], chart['high'], chart['low'], 4, 0.0109)[-1]
    if algo == "cci":
        print(value, traderData['candles'][-1]['close'], traderData['candles'][-1]['date'])
        cci_value = value
        if cci_value < -100 and traderData['bought'] == False:
            traderData['waiting'] = True
        elif cci_value > -100 and traderData['bought'] == False and traderData['waiting']:
            traderData['waiting'] = False
            buyTest(traderData)
        elif cci_value > 100 and traderData['bought']:
            sellTest(traderData)



    if algo == "macd":
        macd_value = stock['macdh'][-1]
        print(macd_value)
        if macd_value > 0 and traderData['bought'] == False:
            buyTest(traderData)
        elif macd_value < 0 and traderData['bought']:
            sellTest(traderData)
        
def backTest(algo, sym, am):
    traderData = dict()
    traderData['tradingSymbol'] = sym
    traderData['amount'] = am
    traderData['bought'] = False
    traderData['profit'] = 0
    traderData['buyAmount'] = 0
    traderData['algorithm'] = algo
    traderData['waiting'] = False
    traderData['waitingSell'] = False
    traderData['buyPrice'] = 1
    traderData['candles'] = []
    traderData['lastTime'] = 0 
    traderData['lastValue'] = 0
    
    candleSample = client.get_klines(symbol=traderData['tradingSymbol'], interval=KLINE_INTERVAL_30MINUTE, limit=5000)

    i = 0
    originalBuy = 0
    for data in candleSample:
        newData = dict()
        newData['open'] = float(data[1])
        newData['high'] = float(data[2])
        newData['low'] = float(data[3])
        newData['close'] = float(data[4])
        newData['volume'] = float(data[5])
        newData['date'] = pandas.to_datetime(data[0], unit='ms')
        traderData['candles'].append(newData)
        if (originalBuy == 0):
            originalBuy = traderData['amount'] * traderData['candles'][0]['close']
            traderData['originalBuy'] = originalBuy

        i = i + 1
        if i > 20:
            generateBackChart(traderData['algorithm'], traderData)
    print("Total Profit:", traderData['profit'])
    print("Percentage:", (traderData['profit']/originalBuy) * 100)
    print(originalBuy)
    print(traderData['amount'] * traderData['candles'][-1]['close'])
    print("Hodl Profit:", originalBuy*traderData['candles'][-1]['close'] - am)
    print("Percentage:", (originalBuy*traderData['candles'][-1]['close'] - am)/am * 100)
    return (traderData['profit']/originalBuy) * 100
    
def saveToFile():
    with open('data', 'wb') as fp:
        pickle.dump(globalData, fp)
    
saveButton = tk.Button(frame, text="Save", command=saveToFile)
saveButton.pack(side=tk.RIGHT)

def loadFromFile():
    global globalData
    with open ('data', 'rb') as fp:
        globalData = pickle.load(fp)

def rerunProcess():
    loadFromFile()
    for k,tick in globalData.items():
        tick['traderData']['startTime'] = time.clock()
        tick['traderData']['candles'] = []
        tick['traderData']['lastTime'] = 0 

        candleList = client.get_klines(symbol=tick['traderData']['tradingSymbol'], interval=KLINE_INTERVAL_30MINUTE, limit=50)
        
        i = 1
        for data in candleList:
            print(data)
            newData = dict()
            newData['open'] = float(data[1])
            newData['high'] = float(data[2])
            newData['low'] = float(data[3])
            newData['close'] = float(data[4])
            newData['volume'] = float(data[5])
            newData['date'] = pandas.to_datetime(data[0], unit='ms')
            tick['traderData']['candles'].append(newData)
            i = i + 1
        
        bm = BinanceSocketManager(client)
        conn_key = bm.start_kline_socket(tick['traderData']['tradingSymbol'], processer, interval=KLINE_INTERVAL_30MINUTE)
        bm.start()  
    
def process_message(msg, traderData):
    
    data = msg["k"]
    newData = dict()
    newData['open'] = float(data['o'])
    newData['close'] = float(data['c'])
    newData['high'] = float(data['h'])
    newData['low'] = float(data['l'])
    newData['volume'] = float(data['v'])
    newData['date'] = pandas.to_datetime(data['t'], unit='ms')
    
    if data['t'] == traderData['lastTime']:
        traderData['lastValue'] = newData
        traderData['candles'][-1] = newData
        traderData['updating'] = True
        generateChart(traderData['algorithm'], traderData)
        traderData['updated'] = True
    if data['t'] != traderData['lastTime']:
        if traderData['lastTime'] == 0:
            traderData['lastTime'] = data['t']
            return
        #traderData['lastValue'] = newData
        traderData['lastTime'] = data['t']
        traderData['candles'].append(newData)
        traderData['updating'] = False
        generateChart(traderData['algorithm'], traderData)
        traderData['updated'] = True

def processer(msg):
    globalData[msg['s']]['msg'] = msg
    globalData[msg['s']]['called'] = True   

def runTrader(algo, sym, am, t=432000000):
    traderData = dict()
    traderData['tradingSymbol'] = sym
    traderData['amount'] = am
    traderData['bought'] = False
    traderData['profit'] = 0
    traderData['buyAmount'] = 0
    traderData['algorithm'] = algo
    traderData['waiting'] = False
    traderData['updating'] = False
    traderData['buyPrice'] = 1
    traderData['candles'] = []
    traderData['lastTime'] = 0 
    traderData['lastValue'] = 0
    traderData['updated'] = False
    traderData['startTime'] = time.clock()
    traderData['time'] = t
    traderData['buyingEnabled'] = True
        
    candleList = client.get_klines(symbol=traderData['tradingSymbol'], interval=KLINE_INTERVAL_30MINUTE, limit=50)
    
    i = 1
    for data in candleList:
        print(data)
        newData = dict()
        newData['open'] = float(data[1])
        newData['high'] = float(data[2])
        newData['low'] = float(data[3])
        newData['close'] = float(data[4])
        newData['volume'] = float(data[5])
        newData['date'] = pandas.to_datetime(data[0], unit='ms')
        traderData['candles'].append(newData)
        i = i + 1
    
    generateChart(traderData['algorithm'], traderData)
    globalData[traderData['tradingSymbol']] = dict()
    globalData[traderData['tradingSymbol']]['called'] = False
    globalData[traderData['tradingSymbol']]['traderData'] = traderData
    bm = BinanceSocketManager(client)
    conn_key = bm.start_kline_socket(traderData['tradingSymbol'], processer, interval=KLINE_INTERVAL_30MINUTE)
    bm.start()  

# list = client.get_all_tickers()
# counter = 0
# for tick in list:
#     sym = tick['symbol']
#     if sym[-3:] == "BTC":
#         amount = getAmount(sym, .00003)
#         if(amount > 0):
#             counter += 1
#             runTrader("cci", sym, amount)
# print(counter)
#rerunProcess()


#backTest("cci", "ETHBTC", 100)

list = ["ADABTC", "BNBBTC", "XLMBTC", "LENDBTC", "OMGBTC", "NEBLBTC", "ICXBTC", "ETHBTC"]
# i = 0
# sum = 0
# for item in list:
#     sum += getAmount(item, 0.00028) * getPrice(item)
#     
# print(sum)

for item in list:
    runTrader("cci", item, getAmount(item)) #use when no positions open

#rerunProcess() #use when currently holding positions
    
  

while True:
    allUpdated = True
    buyingEnabled = True
    for key,trader in globalData.items():
        if trader['called'] == True:
            trader['called'] = False
            process_message(trader['msg'], trader['traderData'])
            
    for key,trader in globalData.items():
        if trader['traderData']['buyingEnabled'] == False:
            buyingEnabled = False
        if trader['traderData']['updated'] != True:
            allUpdated = False
            break
    if allUpdated == True:
        print("-------")
        profit = 0
        unProfit = 0
        for key,trader in globalData.items():
            trader['traderData']['updated'] = False
            profit += trader['traderData']['profit']
            if trader['traderData']['bought'] == True:
                print(trader['traderData']['tradingSymbol'], "position open")
                sellAmount = trader['traderData']['amount'] * trader['traderData']['candles'][-1]['close']
                unProfit += (sellAmount - trader['traderData']['buyAmount'])
        print("Realized Profit:", profit)
        print("Unrealized Profit:", unProfit)
        print("Current Potential Profit:", profit+unProfit)
        if buyingEnabled == False:
            print("Buying Disabled")
        print("SAVING")
        saveToFile()
        print("-------")
    task()

