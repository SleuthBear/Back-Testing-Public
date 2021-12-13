# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 09:57:28 2021

@author: alpha
"""
import math
import matplotlib.pyplot as plt

def is_peak(close, days, day):
    ''' Finds the peaks in the chart'''
    # Using a 1% margin for what is a peak
    margin= 0.01
    value = close[day]
    if day == 0 or day == len(days) - 1:
        return False
    elif close[day-1]*(1-margin) <= value >= close[day+1]*(1-margin):
        return True
    return False

def is_trough(close, days, day):
    '''Finds the troughs in the chart'''
    # Using a 1% margin for what is a trough
    margin = 0.01
    value = close[day]
    if day == 0 or day == len(days) - 1:
        return False
    elif close[day-1]*(1+margin) >= value <= close[day+1]*(1+margin):
        return True
    return False

def gradient(close1, close2, day1, day2):
    '''calculates the gradient between two points'''
    return (close2-close1)/(day2-day1)

def find_cross(close, days, close1, close2, day1, day2, bs):
    if bs == "b":
        buy_step = days.index(day2)+1
        buy_grad = gradient(close1, close2, day1, day2)
        while buy_step < len(days): # Find the current crossover
            if close[buy_step] >= close2 + (days[buy_step] - day2)*buy_grad:
                return days[buy_step] # buy line crosses here
            buy_step += 1
        return day2
    if bs == "s":
        sell_step = days.index(day2)+1
        sell_grad = gradient(close1, close2, day1, day2)
        while sell_step < len(days): # Find the current crossover
            if close[sell_step] >= close2 + (days[sell_step] - day2)*sell_grad:
                return days[sell_step] # buy line crosses here
            sell_step += 1
        return day2
     
def shift_right(d, c, days, close, margin, bs):
    new_d = d
    new_c = c
    if bs == 'b':
        i = len(days) - 1 - close[::-1].index(c) # Find the index of the point in days
        end = min(i+10, len(days))
        for day in range(i, end): # We examine the next 10 points
            if close[day] > (1-margin)*c: #within the margin
                new_d = days[day]
                new_c = close[day]
        return new_d, new_c  
    elif bs == 's':
        i = len(days) - 1 - close[::-1].index(c) # Find the index of the point in days
        end = min(i+10, len(days))
        for day in range(i, end): # We examine the next 10 points
            if close[day] < (1+margin)*c: #within the margin
                new_d = days[day]
                new_c = close[day]
        return new_d, new_c 
    
    

def trendline8(d, step, years, plot, margin):
    # We define our starting point, and then add every end of month value
    # from the end point to then stepping backwards
    start_step = max(0, step-365*years)
    close = []
    days = []
    at = step
    new_month = False
    while at > start_step:
        if d[at, 0][-2:] == "01": # We found the start of a new month |NEED BETTER SOLUTION|
            new_month = True
        at -= 1
        if new_month:
            value = d[at, 1]
            if not math.isnan(value):
                close.append(value)
                days.append(at)
                new_month = False
    if len(days) < 3:
        return 0
    # put the values in the correct order.
    days.reverse()
    close.reverse()
    
    # plot the monthly values
    if plot:
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.plot(days, close, color = "black")
        
    # Find the peaks in the monthly values
    peaks = []
    peak_days = []
    for i in range(len(days)):
        if is_peak(close, days, i):
            peaks.append(close[i]) # FIND BETTER METHOD  
            peak_days.append(days[i]) # FIND BETTER METHOD
    
    # Find the troughs in the monthly values
    troughs = []
    trough_days = []
    for i in range(len(days)):
        if is_trough(close, days, i):
            troughs.append(close[i]) # FIND BETTER METHOD  
            trough_days.append(days[i]) # FIND BETTER METHOD 
    
    # We cycle through maxes until we find a possible highest peak
    P1_c = max(peaks)
    while P1_c == peaks[-1]:
        if len(peaks) < 2:
            return 0 # We cant draw a buy line
        peaks.pop(-1)
        peak_days.pop(-1)
        P1_c = max(peaks)
    P1_i = len(peaks) - 1 - peaks[::-1].index(P1_c) #the index for the peak
    P1_d = peak_days[P1_i] # get the corresponding day
    # find the next highest peak to the right 
    # so we can start our iteration process
    P2_c =  max(peaks[P1_i+1:])
    P2_d = peak_days[P1_i + peaks[P1_i:].index(P2_c)]
    N1_d, N1_c = shift_right(P1_d, P1_c, days, close, margin, 'b') # flat bottom test
    if N1_c > P2_c and N1_d < P2_d:
        P1_d, P1_c = N1_d, N1_c
    # We cycle through maxes until we find a possible lowest trough
    T1_c = min(troughs)
    while T1_c == troughs[-1]:
        if len(troughs) < 2:
            return 0 # We cant draw a sell line
        troughs.pop(-1)
        trough_days.pop(-1)
        T1_c = min(troughs)
    T1_i = len(troughs) - 1 - troughs[::-1].index(T1_c) # The index of the trough
    T1_d = trough_days[T1_i] # get the corresponding day
    # find the next lowest trough to the right 
    # so we can start our iteration process
    T2_c =  min(troughs[T1_i+1:])
    T2_d = trough_days[T1_i + troughs[T1_i:].index(T2_c)]
    N1_d, N1_c = shift_right(T1_d, T1_c, days, close, margin, 's') # flat bottom test
    if N1_c < T2_c and N1_d < T2_d:
        T1_d, T1_c = N1_d, N1_c
    
    buy_done = False
    sell_done = False
    while not buy_done or not sell_done:
        old_T2_d = T2_d
        old_P2_d = P2_d
        buy_cross = find_cross(close, days, P1_c, P2_c, P1_d, P2_d, "b")
        buy_cross_value = close[days.index(buy_cross)]
        sell_cross = find_cross(close, days, T1_c, T2_c, T1_d, T2_d, "s")
        sell_cross_value = close[days.index(sell_cross)]
        if buy_cross < sell_cross and not buy_done: # Buy crosses before sell
            # We calculate the theoretical gradient we need to have
            old_P2_d = P2_d
            needed_grad = gradient(P1_c, sell_cross_value, P1_d, sell_cross)
            current_grad = gradient(P1_c, P2_c, P1_d, P2_d)
            P2_i = days.index(P2_d)
            for i in range(P2_i+1, len(days)):
                buy_grad = gradient(P1_c, close[i], P1_d, days[i])
                if needed_grad > buy_grad > current_grad:
                    P2_c = close[i]
                    P2_d = days[i]
                    current_grad = gradient(P1_c, P2_c, P1_d, P2_d)
                elif buy_grad >= needed_grad and buy_grad >= current_grad:
                    P2_c = close[i]
                    P2_d = days[i]
                    break
            if P2_d == old_P2_d: # Cant iterate buy lines any further
                buy_done = True 
            else:
                sell_done = False
            buy_cross = find_cross(close, days, P1_c, P2_c, P1_d, P2_d, "b")
            buy_cross_value = close[days.index(buy_cross)]
        if sell_cross <= buy_cross and not sell_done: # Buy crosses before sell     
            # We calculate the theoretical gradient we need to have
            old_T2_d = T2_d
            needed_grad = gradient(T1_c, buy_cross_value, T1_d, buy_cross)
            current_grad = gradient(T1_c, T2_c, T1_d, T2_d)
            T2_i = days.index(T2_d)
            for i in range(T2_i+1, len(days)):
                sell_grad = gradient(T1_c, close[i], T1_d, days[i])
                if needed_grad < sell_grad < current_grad:
                    T2_c = close[i]
                    T2_d = days[i]
                    current_grad = gradient(T1_c, T2_c, T1_d, T2_d)
                elif sell_grad <= needed_grad and sell_grad <= current_grad :
                    T2_c = close[i]
                    T2_d = days[i]
                    break
            if T2_d == old_T2_d: # Cant iterate sell lines any further
                sell_done = True
            else:
                buy_done = False
            sell_cross = find_cross(close, days, T1_c, T2_c, T1_d, T2_d, "b")
            sell_cross_value = close[days.index(buy_cross)]
        # Check if we can theoretically go further
        if P2_c == peaks[-1] or old_P2_d == P2_d:
            buy_done = True #We cant move the buy line any further
        if T2_c == peaks[-1] or old_T2_d == T2_d:
            sell_done = True #We cant move the buy line any further   
    
        buy_grad = gradient(P1_c, P2_c, P1_d, P2_d)
        sell_grad = gradient(T1_c, T2_c, T1_d, T2_d)
        buy = P2_c + (step-P2_d)*buy_grad
        sell = T2_c + (step-T2_d)*sell_grad
    if plot:
        ax.plot([P1_d, step], [P1_c, buy], color="green")
        ax.plot([T1_d, step], [T1_c, sell], color="red")    
        
    if buy > d[step, 1] > sell: # below buy above sell, do nothing
        if plot:
            plt.title("HOLD")
        return 0
    elif buy <= d[step, 1] and sell <= d[step, 1]: # above buy and sell, buy
        if plot:
            plt.title("BUY")
        return 1
    elif buy < d[step, 1] < sell: 
        if plot:
            plt.title("HOLD")
        return 0
    elif d[step, 1] < sell:
        if plot:
            plt.title("SELL")
        return -1           
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        