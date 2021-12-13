import pandas as pd
import os
from mods.QAVutilities import QAV, QAVStrategy
import cProfile
import pstats
import random
import datetime as dt
import math
from mods.trendlines import trendline3, trendline2, trendline4, trendline6, trendline7
from mods.trendlines_iterative import trendline8
import numpy as np
import scipy.stats
#from mods.trendlines import three_point_TL
# Taken from stackoverflow
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

PARTITION = "allcsv"
file_list = os.listdir(f"{os.getcwd()}\\{PARTITION}")

#df = pd.read_csv(f"{os.getcwd()}\\{PARTITION}\\KMD.AX.csv")
#stock = df.to_numpy()
#print(trendline8(stock, len(stock)-1, 5, True, 0.08))
#prof = cProfile.Profile()
#prof.run('trendline8(stock, len(stock)-1, 5, False, 0.08)')
#prof.dump_stats('trendline8_days.prof')
#stream = open('trendline8_days.txt', 'w')
#stats = pstats.Stats('trendline8_days.prof', stream=stream)
#stats.sort_stats('cumulative')
#stats.print_stats()

results = []
val = 0
count = 0
for i in range(100):
    print(i)
    stock_matrix = {}
    bootstrap = random.sample(file_list, 200)
    for file in bootstrap:
        df = pd.read_csv(f"{os.getcwd()}\\{PARTITION}\\{file}")
        stock_matrix[file[:-4]] = df.to_numpy()
    test = QAVStrategy(stock_matrix, 
                       starting_cash = 100000, 
                       qav_cutoff = 0.1, 
                       quality_cutoff = 0.5, 
                       threepointbuy = False, 
                       threepointsell = False, 
                       replace = False,
                       replace_gap = 182,
                       stoploss = 0,
                       qavdrop = False, 
                       tkiv1 = True, 
                       tkiv2 = True, 
                       pricebook = True, 
                       pricebook2 = True, 
                       cfshare = True, 
                       yieldpe = True, 
                       yieldbd = True,  
                       recordpe = True, 
                       upturn = False, 
                       equity = True,
                       pricetarget = True, 
                       epsgrowth = True, 
                       fciv2 = True, 
                       max_stocks = 20, 
                       random = False,
                       funnel = False)
    results.append(test.run(start_date = dt.date(2010, 3, 1), 
                 end_date = dt.date(2020, 1, 1)))
    
average = sum(results)/len(results)
SSE = 0
for result in results:
    SSE += (average-result)**2
standard_deviation = math.sqrt(SSE/len(results))

mean, lower, upper = mean_confidence_interval(results, 0.95)
print("-----------------------------\n")
print("Standard Deviation =", standard_deviation)
print("Mean =", mean)
print("95% confidence interval:", lower, "->", upper)

