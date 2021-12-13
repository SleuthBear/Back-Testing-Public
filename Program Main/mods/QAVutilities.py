from mods.trendlines import trendline4
from mods.Trendline_Experimental import trendline
import datetime as dt
import math
from threading import Thread
import itertools
from time import sleep
import random
import csv

USE_PEAKS = False
MOE = 0.0

class QAV():
    
    '''
        Close=1	
        Volume=2
        EPS=3
        Shares=4	
        OpCf=5	
        Equity=6	
        NTA=7
        Price Target=8	
        Net Yield=9
        FEPS=10
        EPS growth=11	
        Operating Cash Flow Per Share=12	
        Price to Operating Cash Flow=13	
        NTA per Share=14	
        Book Value=15	
        Market Cap=16	
        PE=16
    '''
        
    def __init__(self, tkiv1 = True, tkiv2 = True, pricebook = True, 
                 pricebook2 = True, cfshare = True, yieldpe = True, 
                 yieldbd = True, recordpe = True, upturn = True, 
                 equity = True, threepointbuy = True, pricetarget = True, 
                 epsgrowth = True, fciv2 = True):

        self.use_tkiv1 = tkiv1
        self.use_tkiv2 = tkiv2
        self.use_pricebook = pricebook
        self.use_pricebook2 = pricebook2
        self.use_cfshare = cfshare
        self.use_yieldpe = yieldpe
        self.use_yieldbd = yieldbd
        self.use_recordpe = recordpe
        self.use_upturn = upturn
        self.use_equity = equity
        self.use_threepointbuy = threepointbuy
        self.use_pricetarget = pricetarget
        self.use_epsgrowth = epsgrowth
        self.use_fciv2 = fciv2
        self.BANK_DEBT = 3.0
    
    def record_low_PE(self, d, step):
        i = -10
        count = 1
        curr_EPS = d[step, 3]
        NEW_PE = d[step, 16]
        # Loop over all the data backwards until the 6 most recent PEs are 
        # found or until we find a PE smaller than our current  number
        while count < 6:
            #Step back 6 months
            try:
                if d[step+i, 3] and d[step+i, 3] != curr_EPS:
                    count += 1
                    curr_EPS = d[step+i, 3]
                    NEW_PE = ((d[step+i, 1])/(curr_EPS))
                # find if this PE < current PE
                if NEW_PE < d[step, 16] and NEW_PE > 0:
                    return 0
                # If there is an index error, we msut be at the end of the
                # dataset without finding a smaller PE, so we accept our PE
                # as the smallest
            except IndexError:
                return 1
            i -= 10
            
        # If we haven't found a smaller PE in the 6 most recent PEs
        # then we must have the smallest from the last 6.
        return 1

    def old_upturn(self, d, step):
        # We track recent periods by equity
        curr_equity = d[step, 6]
        i = 0
        while d[step+i, 6] == curr_equity or not d[step+i, 6]:
            i -= 1
        return trendline(d, step+i, 5, False, MOE) == 1
    
    def cons_incr_equity(self, d, step):
        i = -10
        count = 1
        curr_equity = d[step, 6]
        # Loop over all the data backwards until the 6 most recent PEs are 
        # found or until we find a PE smaller than our current  number
        while count < 6:
            #Step back 6 months
            try:
                if d[step+i, 6] > curr_equity:
                    return 0
                if d[step+i, 6] and d[step+i, 6] != curr_equity:
                    count += 1
                    curr_equity = d[step+i, 6]
            except IndexError:
                return 1
            i -= 1       
        return 1


    def calculate_QAV(self, d, step):
        score = 0
        num_items = 0


        # Price<=TKIV1?
        if self.use_tkiv1:
            TKIV1 = d[step, 3]/0.195
            if d[step, 1] <= TKIV1:
                score += 1
            num_items += 1
        
        # Price<= TKIV2?
        if self.use_tkiv2 and d[step, 11]:
            TKIV2 = d[step, 11]/0.061
            if d[step, 1] <= TKIV2:
                score += 1
            num_items += 1
            
        # Price<Book?
        if self.use_pricebook:
            if d[step, 1] < d[step, 15]:
                score += 1
            num_items += 1        

        # Price <= book+30%?
        if self.use_pricebook2:
            if d[step, 1] < d[step, 15]*1.3:
                score += 1
            num_items += 1

        
        # Record low of last 6 PEs?
        if self.use_recordpe:
            if self.record_low_PE(d, step):
                score += 1
            num_items += 1

        
        # Consistantly Increasing Equity?
        if self.use_equity:
            if self.cons_incr_equity(d, step):
                score += 1
            num_items += 1

        # Yield - PE > 1?
        if self.use_yieldpe:
            if d[step, 9]:
                if d[step, 9] - d[step, 16] > 1:
                    score += 1
                    num_items += 1

        # Yield > bank debt?
        if self.use_yieldbd:
            if d[step, 9]:
                if d[step, 9] > self.BANK_DEBT:
                    score += 1
            num_items += 1
        
        # Is FCIV>2*share price? (called FCIV but is actually TKIV2)
        if self.use_fciv2 and d[step, 11]:
            TKIV2 = d[step, 11]/0.061
            if TKIV2 > d[step, 1]*2:
                score += 1
            num_items += 1

        # CF/Share<=7 [ASK]
        if self.use_cfshare and d[step, 5]:
            if (d[step, 1]/(d[step, 5])) <= 7:
                score += 2  
            num_items += 1
            
        # Is price below 1 day price target? (instead of SDIV) [ASK]
        if self.use_pricetarget and d[step, 8]:
            if d[step, 1] < d[step, 8]:
                score += 1
            num_items += 1
        
        # 3-point-uptrend?
        # Because we won't buy unless it is a 3-point uptrend anyway, we can
        # simply assume this is true to avoid extra calculations
        if self.use_threepointbuy:
            score += 1
            num_items += 1
            
        # New 3-point upturn? CALCULATE ONLY IF IT COULD PUSH IT OVER 0.1
        if self.use_upturn and self.use_threepointbuy:
            if not self.old_upturn(d, step):
                score += 1
                #print("Recent Upturn PASSED")
            num_items += 1
                
        # Growth/PE > 1.5
        if (self.use_epsgrowth and d[step, 10] and d[step, 16] and 
            d[step, 3]):
            EPSgrowth = ((d[step, 10] - d[step, 3])
                         / d[step, 3])
            if (EPSgrowth*100)/d[step, 3] > 1.5:
                score += 1
                #print("Growth/PE > 1.5 PASSED")
            num_items += 1

        quality = score/num_items
        return quality, quality/d[step, 13]
    
    
        
        




class QAVStrategy():
    
    def __init__(self, stock_matrix, starting_cash = 100000, qav_cutoff = 0.1, quality_cutoff = 0.5, 
                 threepointsell = True, stoploss = 0, 
                 replace = False, replace_gap = 30,  qavdrop = False, tkiv1 = True, 
                 tkiv2 = True, pricebook = True, pricebook2 = True, 
                 cfshare = True, yieldpe = True, yieldbd = True, 
                 recordpe = True, upturn = True, equity = True, 
                 threepointbuy = True, pricetarget = True, epsgrowth = True, 
                 fciv2 = True, max_stocks = 20, random = False, funnel = False):
        
        self.QAV = QAV(tkiv1, tkiv2, pricebook, pricebook2, cfshare, yieldpe, 
                       yieldbd, recordpe, upturn, equity, threepointbuy,
                       pricetarget, epsgrowth, fciv2)
        
        self.stock_matrix = stock_matrix
        self.qav_cutoff = qav_cutoff
        self.quality_cutoff = quality_cutoff
        self.use_threepointbuy = threepointbuy
        self.use_threepointsell = threepointsell
        self.stoploss = stoploss
        self.use_replace = replace
        self.use_qavdrop = qavdrop
        self.use_funnel = funnel
        self.use_random = random
        self.account = {}
        
        self.days_since_replace = 0
        self.replace_gap = replace_gap
        self.buy_list = []
        
        self.cash = starting_cash
        
        self.max_stocks = max_stocks
        self.have_bought = 0
        self.full = 0
        self.portfolio = []
        
    def daily(self, step, day, writer):
        date = dt.datetime.strptime(day, "%Y-%m-%d").date()
        
        
            
            
        # Create the list of stocks that we can buy today
        slots_left = self.max_stocks - len(self.portfolio)
        if slots_left or (self.use_replace and self.days_since_replace >= 
                          self.replace_gap) or self.use_funnel:         
            for stock in self.stock_matrix.keys():
                quality = 0
                qav = 0
                data = self.stock_matrix[stock]
                if ((stock not in self.portfolio or self.use_funnel) and data[step, 16] > 0 
                    and data[step, 13]): # if funneling we can rebuy a stock we already own
                    quality, qav = self.QAV.calculate_QAV(data, step) 
                if quality > self.quality_cutoff and qav > self.qav_cutoff:
                    if self.use_threepointbuy and trendline(data, step, 5, False, MOE) == 1:
                        self.buy_list.append((stock, qav))
                    elif not self.use_threepointbuy:
                        self.buy_list.append((stock, qav))

            # Iterate through the market and add to the buy_list. This
            # is done using multithreading
            #self.thread_qav(step)
                
        # sort buy_list by QAV value
        self.buy_list.sort(key=lambda x: x[1], reverse=True)
        
        
        # Random
        if self.use_random and slots_left:
            random_stocks = random.sample(self.stock_matrix.keys(), slots_left)
            for stock in random_stocks:
                if stock not in self.portfolio and self.stock_matrix[stock][step, 1] > 0:
                    self.execute_buy(stock, 0, date, step, slots_left, writer)
                    slots_left -= 1
        
        # BUY 
        if not self.use_funnel: # We have seperate buy criteria with funnel
            to_buy = min(slots_left, len(self.buy_list))
            for i in range(to_buy):
                self.execute_buy(self.buy_list[i][0], self.buy_list[i][1], date, 
                                 step, slots_left, writer)
                slots_left -= 1
            buy_leftover = self.buy_list[to_buy:]
        
        # Update holdings
        self.update_holdings(step)
        
        # 3 POINT SELL
        # Sell once a month
        if self.use_threepointsell and date.day == 1:
            for stock in self.portfolio:
                data = self.stock_matrix[stock]
                # If we have a closing price for this day
                if not math.isnan(data[step, 1]):
                    if trendline(data, step, 5, False, MOE) == -1:
                        self.execute_sell(stock, date, step, writer)
                        slots_left += 1
        
        # REPLACE
        if ( self.use_replace and len(self.portfolio) == self.max_stocks #redundant condition
             and self.days_since_replace >= self.replace_gap and buy_leftover ):                                              
            qavs = []
            for stock in self.portfolio:
                qavs.append(self.QAV.calculate_QAV(self.stock_matrix[stock], 
                                                   step)[1])
                                                   
            # get the lowest qav score stock we have                                      
            stockqav = min(qavs)
            # get the highest qav score stock in the buy list
            best_buy = buy_leftover[0]
            buyqav = best_buy[1]
            #print(f"if {buyqav} > {stockqav}")
            if buyqav > stockqav:
                stock_to_sell = self.portfolio[qavs.index(stockqav)]
                self.execute_sell(stock_to_sell, date, step, writer)
                slots_left += 1
                self.execute_buy(best_buy[0], best_buy[1], 
                                 date, step, slots_left, writer)
                slots_left -= 1
                self.days_since_replace = 0
        else:
            # incriment the time since last replacement
            self.days_since_replace += 1
            
        
        # QAV DROP
        if self.use_qavdrop and date.day == 1:
            for stock in self.portfolio:
                data = self.stock_matrix[stock]
                if (data[step, 1] > 0 and 
                    self.QAV.calculate_QAV(data, step)[1] < self.qav_cutoff):
                    self.execute_sell(stock, date, step, writer)
                    slots_left += 1
                    
        # FUNNEL STRATEGY
        if self.use_funnel:
            if date.day == 1:
                self.have_bought = 0
            if not self.full: # Ininitially fill up our portfolio
                can_buy = min(len(self.buy_list), self.max_stocks-len(self.portfolio))
                for i in range(can_buy):
                    self.execute_buy(self.buy_list[i][0], self.buy_list[i][1], date, step, slots_left, writer)
                    slots_left -= 1
                if slots_left == 0:
                    self.full = 1

            elif date.month in [5,11] and not self.have_bought and self.buy_list:
                if len(self.portfolio) == 1:
                    stock_to_sell = self.portfolio[0]
                    self.execute_sell(stock_to_sell, date, step, writer)
                    self.full = 0 #start filling up the portfolio again
                else:
                    qavs = []
                    for stock in self.portfolio:
                        qavs.append(self.QAV.calculate_QAV(self.stock_matrix[stock], 
                                                           step)[1])                    
                    # get the lowest qav score stock we have and sell it                                    
                    stockqav = min(qavs)
                    stock_to_sell = self.portfolio[qavs.index(stockqav)]
                    self.execute_sell(stock_to_sell, date, step, writer)
                    slots_left = 1
                    self.execute_buy(self.buy_list[0][0], self.buy_list[0][1], date, step, slots_left, writer)
                    self.have_bought = 1
            
        # STOP LOSS
        if self.stoploss > 0:
            for stock in self.portfolio:
                data = self.stock_matrix[stock]
                if data[step, 1] > 0 and data[step, 1] < \
                                         self.stoploss*self.account[stock]["bought at"]:
                    self.execute_sell(stock, date, step, writer)
                    slots_left += 1 # probably redundant
        # Clear the buy list
        self.buy_list.clear()
        
        
        
        
        return
                        
    def update_holdings(self, step):
        #iterate throught the portfolio
        for stock in self.portfolio: 
            # set the price to the current value
            price = self.stock_matrix[stock][step, 1]
            if not math.isnan(price):
                self.account[stock]['price'] = price
            
    
    def execute_buy(self, stock, qav, date, step, slots_left, writer):
        if stock not in self.portfolio:
            self.portfolio.append(stock)
            price = self.stock_matrix[stock][step, 1]
            if slots_left == 1:
                to_spend = self.cash
            else:
                to_spend = (self.cash/slots_left)
            units = to_spend//price
            # subtract the money spent from our cash pile
            self.cash -= to_spend
            # Store account info as a nested dictionary
            self.account[stock] = {"price": price, "units": units, "qav": qav, 
                                   "bought": date, "sold": False, 
                                   "sold at": False, "bought at": price}
        elif stock in self.portfolio:
            if slots_left == 1:
                to_spend = self.cash
            else:
                to_spend = (self.cash/slots_left)
            price = self.stock_matrix[stock][step, 1]
            units = to_spend//price
            self.cash -= to_spend
            self.account[stock]["units"] += units
            self.account[stock]["bought"] = date
        #print(f"{date} - BOUGHT {stock}: {units} units at ${price} for \
#${to_spend}")
        #writer.writerow((date, "B", stock, units, price, units*price))
    def execute_sell(self, stock, date, step, writer):
        self.portfolio.remove(stock)
        #self.account[stock]["price"] = False
        self.account[stock]["sold"] = date
        #sold_at = self.stock_matrix[stock][step, 1]
        sold_at = self.account[stock]["price"]
        self.account[stock]["sold at"] = sold_at
        units = self.account[stock]["units"]
        sold_for = sold_at*units
        self.cash += sold_for        
        #print(f"{date} - SOLD {stock}: {units} units at ${sold_at} for \
#${sold_for}")
        #writer.writerow((date, "S", stock, units, sold_at, -sold_for))
        
        
        
    def thread_qav(self, step):
        stocks1 = []
        stocks2 = []
        stocks3 = []
        stocks4 = []
        stocks5 = []
        stocks6 = []
        stocks7 = []
        stocks8 = []
        cycler = itertools.cycle([stocks1, stocks2, stocks3, stocks4,
                                  stocks5, stocks6, stocks7, stocks8])
        
        for stock in self.stock_matrix.keys():
            group = next(cycler)
            group.append(stock)
        t1 = Thread(target=self.populate_buy_list, args=((stocks1, step)))
        t2 = Thread(target=self.populate_buy_list, args=((stocks2, step)))
        t3 = Thread(target=self.populate_buy_list, args=((stocks3, step)))
        t4 = Thread(target=self.populate_buy_list, args=((stocks4, step)))
        t5 = Thread(target=self.populate_buy_list, args=((stocks5, step)))
        t6 = Thread(target=self.populate_buy_list, args=((stocks6, step)))
        t7 = Thread(target=self.populate_buy_list, args=((stocks7, step)))
        t8 = Thread(target=self.populate_buy_list, args=((stocks8, step)))
        t1.start()
        t2.start()
        t3.start()  
        t4.start()
        t5.start()
        t6.start()
        t7.start()
        t8.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()
        t6.join()
        t7.join()
        t8.join()

        
    def populate_buy_list(self, stocks, step):
        for stock in stocks:
            quality = 0
            qav = 0
            data = self.stock_matrix[stock]
            if (stock not in self.portfolio and data[step, 16] > 0 
                    and data[step, 13]):
                    quality, qav = self.QAV.calculate_QAV(data, step) 
            if quality > self.quality_cutoff and qav > self.qav_cutoff:
                    if self.use_threepointbuy and trendline(data, step, 5, False, MOE) == 1:
                        self.buy_list.append((stock, qav))
                    elif not self.use_threepointbuy:
                        self.buy_list.append((stock, qav))
        

        
    def run(self, start_date = dt.date(2010, 1, 1), 
                 end_date = dt.date(2020, 1, 1)):
        
        
        stock_one = list(self.stock_matrix.keys())[0]
        i = 0
        
        # Find the index of the first and last dates
        while True:
            try:
                date = self.stock_matrix[stock_one][i, 0]
                date = dt.datetime.strptime(date, "%Y-%m-%d").date()
            except IndexError:
                print(date)
                print("IndexError: The end date you have selected is outside \
                      the range of the data")
            if date == start_date:
                step = i
            if date >= end_date:
                end_step = i
                break
            i += 1
        
        print("Starting Cash = ", self.cash)
        f = open('csv_file.csv', 'w', newline = '')
        writer = csv.writer(f) # REMOVE
        # step through the data executing buys and sells
        while step <= end_step:
           self.daily(step, self.stock_matrix[stock_one][step, 0], writer)
           step += 1
        final_value = self.cash
        for stock in self.portfolio:
            #print(self.account[stock])
            final_value += self.account[stock]['price']*self.account[stock]['units']
            #writer.writerow((end_date, "S", stock, self.account[stock]['units'], self.account[stock]['price'],
            #                 -self.account[stock]['price']*self.account[stock]['units']))
        f.close()
        #print("portfolio", self.portfolio)
        print("Final Value = ", final_value)
        return final_value
            
        

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    