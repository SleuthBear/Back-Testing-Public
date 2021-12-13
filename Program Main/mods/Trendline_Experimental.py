# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 17:32:33 2021

@author: alpha
"""

import math
import matplotlib.pyplot as plt

###############################################################################   
def get_gradient(point1, point2):
    if point1[0] == point2[0]:
        print("WARNING", point1, point2)
    return (point2[1]-point1[1])/(point2[0]-point1[0])

def is_peak(close, days, day):
    value = close[day]
    if day == 0 or day == len(days) - 1:
        return False
    elif close[day-1] <= value >= close[day+1]:
        return True
    return False

def is_trough(close, days, day):
    value = close[day]
    if day == 0 or day == len(days) - 1:
        return False
    elif close[day-1] >= value <= close[day+1]:
        return True
    return False

def get_current(step, grad, left):
    return left[1] + (step-left[0])*grad

def shift_peaks(peaks, left_peak, margin):
    # Find peaks within the margin to the right
    rightmost_left = left_peak
    for peak in peaks[peaks.index(left_peak):]:
        if peak[1] > (1-margin)*left_peak[1]:
            rightmost_left = peak
    return rightmost_left

def shift_troughs(troughs, left_trough, margin):
    # Find troughs within the margin to the right
    rightmost_left = left_trough
    for trough in troughs[troughs.index(left_trough):]:
        if trough[1] < (1+margin)*left_trough[1]:
            rightmost_left = trough
    return rightmost_left
###############################################################################

def trendline(d, step, years, plot, margin):
    start_step = max(0, step-365*years)
    while math.isnan(d[start_step, 1]): # Step forward until we find a valid point
        start_step += 5 # jumps of 5 days because why not?
        if start_step > step: # If we get back to where we started no bueno
            return 0
    # USE MONTH JUMPS TO SPEED UP COMPUTATION
    #today = dt.datetime.strptime(d[step, 0], "%Y-%m-%d")
    close = []
    days = []
    at = start_step
    while at < step:
        #date = dt.datetime.strptime(d[at, 0], "%Y-%m-%d")
        if d[at, 0][-2:] == "01": # We found the start of a new month
            month_end = at - 1
            for i in range(15): # if we cant get a value in 15 days give up
                value = d[month_end, 1]
                if not math.isnan(value):
                    close.append(value)
                    days.append(month_end)
                    #days.append(dt.datetime.strptime(d[month_end, 0], "%Y-%m-%d"))
                    break
                month_end -= 1
        at += 1
    if len(days) < 3:
        return 0
    ###############################################################################   
    # 1-> get a list of all the peaks in the graph, as well as their height
    # 2-> get a list of all the troughs in the graph as well as their height
    # 3-> Find the heighest preak in the graph
    # 4-> If there is no lower peak to the right, repeat 3 with the peaks
    # to the left of this peak
    # 5-> Find the lowest trough in the graph
    # 6-> IF there is no higher trough to the right, repeat 5 with the troughs
    # to the left of this trough
    # 7-> Start stepping through days from whichever of the lowest trough or
    # highest peak is left-most.
    # 8-> If a peak it higher than our right peak (default 0) and less than
    # our left peak, we pick it as our right points
    # 9-> Iterate through future peaks to see if any are under the line from
    # the left peak to the right peak. If they are, and before the start of the
    # sell line then make it the new right peak.
    # 10-> repeat steps 8-9 with troughs.
    
    # Get the peaks and troughs
    peaks = []
    troughs = []
    for i in range(len(days)):
        if is_peak(close, days, i):
            peaks.append((days[i], close[i]))
        elif is_trough(close, days, i):
            troughs.append((days[i], close[i]))
    # Find the appropriate max and min peaks following steps 3-4 and 5-6
    if len(peaks) < 2 or len(troughs) < 2:
        return 0
    left_peak = max(peaks, key = lambda x: x[1])
    left_peak = shift_peaks(peaks, left_peak, margin)
    left_trough = min(troughs, key = lambda x: x[1])
    left_trough = shift_troughs(troughs, left_trough, margin)
    while left_peak == peaks[-1]:
        peaks.pop(-1)
        # If we have less than 2 troughs give up.
        if len(peaks) < 2:
            return 0
        
        left_peak = max(peaks, key = lambda x: x[1])
        left_peak = shift_peaks(peaks, left_peak, margin)
    while left_trough == troughs[-1]:
        troughs.pop(-1)
        # If we have less than 2 troughs give up.
        if len(troughs) < 2:
            return 0
        left_trough = min(troughs, key = lambda x: x[1])
        left_trough = shift_troughs(troughs, left_trough, margin)
    # Set the right peak deafult as the peak immediately to the right of 
    # the left peak
    right_peak = peaks[peaks.index(left_peak)+1]
    # step the right peak through
    for peak in peaks[peaks.index(right_peak):]:
        # current peak is greater than right peak, swap
        if peak[1] > right_peak[1]:
            right_peak = peak
        # If current peak is over the buy line & before the left trough, swap
        b_grad = get_gradient(left_peak, right_peak)
        if (left_peak[1] + (peak[0]-left_peak[0])*b_grad < peak[1] and 
              peak[0] < left_trough[0]):
            right_peak = peak
    # Set the right trough deafult as the peak immediately to the right of 
    # the left trough
    right_trough = troughs[troughs.index(left_trough)+1]
    for trough in troughs[troughs.index(right_trough):]:
        # current peak is greater than right peak, swap
        if trough[1] < right_trough[1]:
            right_trough = trough
        # If current trough is under the sell line & before the left peak, swap
        s_grad = get_gradient(left_trough, right_trough)
        if (left_trough[1]+(trough[0]-left_trough[0])*s_grad > trough[1] and 
             trough[0] < left_peak[0]):
            right_trough = trough
    # Find right peak and trough within the margin to the right 
    ############### THIS PART MAKES NO SENSE AND IS BAD #######################
    for peak in peaks[peaks.index(right_peak):]:
        if peak[1] > (1-margin)*right_peak[1]:
            right_peak = peak   
    for trough in troughs[troughs.index(right_trough):]:
        if trough[1] < (1+margin)*right_trough[1]:
            right_trough = trough 
    b_grad = get_gradient(left_peak, right_peak)   
    s_grad = get_gradient(left_trough, right_trough)
    buy = get_current(step, b_grad, left_peak)
    sell = get_current(step, s_grad, left_trough)
    if plot:
        print(left_peak, right_peak, (step, d[step, 1]))
        print(buy)
        print(left_trough, right_trough, (step, d[step, 1]))
        print(sell)
        
        plt.plot(days, close)
        plt.plot([left_peak[0], right_peak[0], step], [left_peak[1], right_peak[1], buy], color = "green")
        plt.plot([left_trough[0], right_trough[0], step], [left_trough[1], right_trough[1], sell], color = "red")
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
        
        
        
        
        
                                      
        
    