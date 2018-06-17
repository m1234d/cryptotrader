from binance.client import Client
import msvcrt
import time
import sys
import keyboard

from stockstats import StockDataFrame
client = Client("YyJcRnCwOo5h5YoLgSFBFZMGnlwehT0S845XKBD6KYr1IGTuz8pGNZbDR29hxWGR", "4vs7jUlSG4YI8hbcBKtQvF8fKXii6kcP0RcDPwJKFAxbIDLdfBlQvmrOd8xRvTJr")
from pandas import DataFrame
import pandas
from binance.enums import *
from binance.websockets import BinanceSocketManager
globalData = dict()

def amountToLots(amount, sym):
    if sym == "ETHBTC":
        amount = round(amount, 3)
    elif sym == "LTCBTC":
        amount = round(amount, 2)
    elif sym == "BNBBTC":
        amount = round(amount, 2)
    elif sym == "NEOBTC":
        amount = round(amount, 2)
    elif sym == "GASBTC":
        amount = round(amount, 2)
    elif sym == "BCCBTC":
        amount = round(amount, 3)
    elif sym == "MCOBTC":
        amount = round(amount, 2)
    elif sym == "QTUMBTC":
        amount = round(amount, 2)
    elif sym == "OMGBTC":
        amount = round(amount, 2)
    elif sym == "STRATBTC":
        amount = round(amount, 2)
    elif sym == "SALTBTC":
        amount = round(amount, 2)
    elif sym == "ETCBTC":
        amount = round(amount, 2)
    elif sym == "DASHBTC":
        amount = round(amount, 3)
    elif sym == "BTGBTC":
        amount = round(amount, 2)
    elif sym == "ARKBTC":
        amount = round(amount, 2)
    elif sym == "XMRBTC":
        amount = round(amount, 3)
    elif sym == "DLTBTC":
        amount = round(amount)
    elif sym == "AMBBTC":
        amount = round(amount)
    elif sym == "ZECBTC":
        amount = round(amount, 3)
    elif sym == "GVTBTC":
        amount = round(amount, 2)
    elif sym == "GXSBTC":
        amount = round(amount, 2)
    elif sym == "XZCBTC":
        amount = round(amount, 2)
    elif sym == "LSKBTC":
        amount = round(amount, 2)
    elif sym == "BCDBTC":
        amount = round(amount, 3)
    elif sym == "DGDBTC":
        amount = round(amount, 3)
    elif sym == "PPTBTC":
        amount = round(amount, 2)
    elif sym == "WAVESBTC":
        amount = round(amount, 2)
    elif sym == "ICXBTC":
        amount = round(amount, 2)
    elif sym == "NEBLBTC":
        amount = round(amount, 2)
    else:
        amount = round(amount)
    return amount

