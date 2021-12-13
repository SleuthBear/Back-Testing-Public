# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 13:12:13 2021

@author: alpha
"""

import os
import numpy as np
import pandas as pd
import eikon as ek
from datetime import datetime
# get access to eikon API through the app key
ek.set_app_key('1546eef126d74ad6a1c4f28ecf5900b6085bb788')
import time
import csv

start = "2006/01/01"
end = "2021/07/21"
def get_csv(ric):
    
    data = pd.DataFrame()
    # Get the needed dates
    date_index = pd.date_range(start, end, freq='D')
    data = pd.DataFrame(index=date_index)
    print("----------")
    print("close")
    done = 0
    while done <= 4:
        try:
            close = ek.get_timeseries(ric, 'CLOSE', start_date = start, end_date = end, interval='daily')
            done += 5
        except:
               done+=1
               if done > 4:
                   print("FAIL")
                   return
    print("volume")
    done = 0
    while done <= 4:
        try:
            volume = ek.get_timeseries(ric, 'VOLUME', start_date = start, end_date = end, interval='daily') 
            done += 5
        except:
            done+=1
            if done > 4:
                print("FAIL")
                return
    print("EPS")
    done = 0
    while done <= 4:
        try:
            EPS,e = ek.get_data(ric, [f"TR.F.EPSBasicExclExordItemsTot(SDate={start},EDate={end},Period=FS0,Frq=D).calcdate",f"TR.F.EPSBasicExclExordItemsTot(SDate={start},EDate={end},Period=FS0,Frq=D)"])  
            EPS.index = pd.to_datetime(EPS["Calc Date"])
            done += 5
        except:
            done+=1
            if done > 4:
                print("FAIL")
                return
    print("Future EPS")
    done = 0
    while done <= 4:
        try:
            FEPS,e = ek.get_data(ric, f"TR.EPSMean(SDate={start},EDate={end},Period=FY2,Frq=D)")  
            FEPS.index = pd.to_datetime(EPS["Calc Date"])
            done += 5
        except:
            done+=1
            if done > 4:
                print("FAIL")
                return
    #print("PE")
    #PE,e = ek.get_data(ric, ["TR.PE(SDate={start},EDate={end},Frq=D).calcdate", "TR.PE(SDate={start},EDate={end},Frq=D)"])
    #PE.index = pd.to_datetime(PE["Calc Date"])
    print("shares")
    done = 0
    while done <= 4:
        try:
            shares,e = ek.get_data(ric, f"TR.F.ComShrOutsTot(SDate={start},EDate={end},Period=FS0,Frq=D,Scale=6)")
            shares.index = pd.to_datetime(EPS["Calc Date"])
            done+=5
        except:
            done+=1
            if done > 4:
                print("FAIL")
                return
    print("opcf")
    done = 0
    while done <= 4:
        try:
            opcf,e = ek.get_data(ric,f"TR.F.NetCashFlowOp(SDate={start},EDate={end},,Period=FS0,Frq=D,Scale=6)")
            opcf.index = pd.to_datetime(EPS["Calc Date"])
            done+=5
        except:
            done+=1
            if done > 4:
                print("FAIL")
                return
    print("equity")
    done = 0
    while done <= 4:
        try:
            equity,e = ek.get_data(ric, f"TR.F.ComEqTot(SDate={start},EDate={end},Period=FS0,Frq=D,Scale=6)")
            equity.index = pd.to_datetime(EPS["Calc Date"])
            done+=5
        except:
            done+=1
            if done > 4:
                print("FAIL")
                return
    print("nta")
    done = 0
    while done <= 4:
        try:
            nta,e = ek.get_data(ric, f"TR.F.TotAssets(SDate={start},EDate={end},Period=FS0,Frq=D,Scale=6)")
                #nta,e = ek.get_data(ric, "TR.F.TotAssets(SDate=2011/06/30,EDate=2020/06/30,Period=FY0,Frq=D)")
            nta.index = pd.to_datetime(EPS["Calc Date"])
            done+=5
        except:
            done+=1
            if done > 4:
                print("FAIL")
                return
    print("price target")
    done = 0
    while done <= 4:
        try:
            price_target,e = ek.get_data(ric, f"TR.PriceTargetMean(SDate={start},EDate={end},Frq=D)")
            price_target.index = pd.to_datetime(EPS["Calc Date"])
            done+=5
        except:
            done+=1
            if done > 4:
                print("FAIL")
                return
    print("net yield")
    done = 0
    while done <= 4:
        try:
            net_yield,e = ek.get_data(ric, f"TR.F.DivYldComStockIssuePct(SDate={start},EDate={end},Period=FY0,Frq=D)")
            net_yield.index = pd.to_datetime(EPS["Calc Date"])
            done+=5
        except:
          done+=1
          if done > 4:
                print("FAIL")
                return
    #print("ROIC")
    #done = 0
    #while done <= 4:
    #    try:
    #        ROIC,e = ek.get_data(ric, f"TR.ROICActValue(SDate={start},EDate={end},Period=FY0,Frq=FY)")
    #        ROIC.index = pd.to_datetime(EPS["Calc Date"])
    #        done+=5
    #    except:
    #        done+=1
    #        if done > 4:
    #            print("FAIL")
    #            return
    
    
    data['Close'] = close['CLOSE']
    data['Volume'] = volume['VOLUME']
    data['EPS'] = EPS.iloc[:,2]
    data['Shares'] = shares.iloc[:,1]
    data['OpCf'] = opcf.iloc[:,1]
    data['Equity'] = equity.iloc[:,1]
    data['NTA'] = nta.iloc[:,1]
    data['Price Target'] = price_target.iloc[:,1]
    data['Net Yield'] = net_yield.iloc[:,1]
    data['FEPS'] = FEPS.iloc[:,1]
    data['Operating Cash Flow Per Share'] = data['OpCf']/data['Shares']
    data['Price to Operating Cash Flow'] = data['Close']/data['Operating Cash Flow Per Share']
    data['NTA per Share'] = data['NTA']/data['Shares']
    data['Book Value'] = data['Equity']/data['Shares']
    data['Market Cap'] = data['Close']*data['Shares']
    data.to_csv("temp.csv")
    data['PE'] = data['Close']/data['EPS']
    #data["ROIC"] = ROIC.iloc[:,1]
    

    print(ric)
    data.to_csv(f"C:/Users/alpha/OneDrive/Documents/GitHub/Stock-Analysis-Backtesting/Program Main/allcsv-july2021/{ric}.csv", index = True)
rics = open(f"C:/Users/alpha/OneDrive/Documents/GitHub/Stock-Analysis-Backtesting/Program Main/allstocks.txt", 'r')
reader = csv.reader(rics)

stock_list = []
for line in reader:
    print(line)
    stock_list.append(line[0] +".AX")
print(stock_list)

done = os.listdir("C:/Users/alpha/OneDrive/Documents/GitHub/Stock-Analysis-Backtesting/Program Main/allcsv-july2021")
 
for stock in stock_list:
    if stock + ".csv" in done:
        print("already done")
        continue
    else: 
        #try:
        get_csv(stock)
        #except:
            #continue
        